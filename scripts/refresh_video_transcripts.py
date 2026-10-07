#!/usr/bin/env python3
"""Stage individually reviewed public solo transcripts without resetting any corpus."""
from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

from enrich_provenance import PROVENANCE_KEYS, default_provenance, read_markdown, write_markdown
from export_public_corpus import (choose_transcript_path, classify_video_rights,
                                 display_timestamp, eligible_video, load_guests,
                                 parse_timed_transcript, sanitize_first_party_text,
                                 video_publication_date)

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare(channel: Path, identities: list[str]) -> tuple[list[dict], list[tuple[Path, dict, str]]]:
    records = json.loads((channel / "logs/library_manifest/library_manifest.json").read_text())["records"]
    local = {row["video_id"]: row for row in records}
    rows = [json.loads(line) for line in (ROOT / "catalog/videos.jsonl").read_text().splitlines()]
    existing = {row["video_id"]: row for row in rows}
    allowlist = {line.strip() for line in (ROOT / "config/video-transcript-allowlist.txt").read_text().splitlines()
                 if line.strip() and not line.startswith("#")}
    overrides = json.loads((ROOT / "config/video-rights-overrides.json").read_text())
    guests, names = load_guests(channel / "guests.json")
    staged = []
    for identity in identities:
        source = local[identity]
        if not eligible_video(source):
            raise ValueError(f"{identity}: not an eligible currently public normal video")
        classification = classify_video_rights(identity, source["title"], guests, overrides, allowlist)
        if classification["rights_scope"] != "first-party":
            raise ValueError(f"{identity}: not an allowlisted solo transcript")
        folder = (channel / source["folder"]).resolve()
        folder.relative_to(channel.resolve())
        selected = choose_transcript_path(folder, source["transcript_status"])
        if selected is None:
            raise ValueError(f"{identity}: no structurally valid subtitle")
        receipt_path = channel / "logs/subtitle_backfill/text-review-receipts" / f"{identity}.json"
        receipt = json.loads(receipt_path.read_text())
        if (receipt.get("video_id") != identity or receipt.get("source_sha256") != sha256(selected)
                or receipt.get("text_review_status") != "text-reviewed"
                or receipt.get("speaker_classification") != "solo-yuzheng"):
            raise ValueError(f"{identity}: source does not match the reviewed text snapshot")
        cues = parse_timed_transcript(selected)
        url = f"https://www.youtube.com/watch?v={identity}"
        published_at = video_publication_date(source, folder)
        old = existing.get(identity)
        if old and old.get("inclusion_authorization"):
            raise ValueError(f"{identity}: separate snapshot policy must not be replaced")
        path = (ROOT / old["corpus_path"] if old and old.get("corpus_path")
                else ROOT / "corpus/videos" / f"{published_at[:10].replace('-', '')}-{identity}.md")
        meta = read_markdown(path)[0] if path.exists() else dict(
            id=f"youtube-{identity}", title=source["title"], author="Yuzheng Sun",
            source_type="video-transcript", source_url=url, published_at=published_at,
            rights_scope="first-party", speaker_classification="solo-yuzheng", review_status="approved",
            license="CC-BY-4.0", third_party_exclusions=True)
        quality = dict(transcript_status=source["transcript_status"], transcript_source_sha256=sha256(selected),
                       transcript_text_review_status="text-reviewed", transcript_audio_review_status=receipt["audio_review_status"],
                       transcript_structure_status="passed", transcript_precision_review_status="not-certified")
        meta.update(quality)
        meta["snapshot_at"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
        body = f"# {source['title']}\n\n> [观看原视频]({url}) · 字幕状态：`{source['transcript_status']}`。字幕文字已复核；未逐字听校，请以原视频为准。许可不覆盖发言中引用的第三方材料。\n\n"
        body += "\n".join(f"[{display_timestamp(second)}]({url}&t={second}s) {sanitize_first_party_text(text)}\n" for second, text in cues)
        meta.update(default_provenance(meta, body))
        row = dict(old) if old else dict(id=f"youtube-{identity}", video_id=identity, title=source["title"], url=url,
                                       published_at=published_at, rights_scope="first-party",
                                       speaker_classification="solo-yuzheng", review_status="approved",
                                       rights_reason="explicit reviewed solo transcript allowlist", guest_names=names.get(identity, []))
        row.update(quality, transcript_available=True, transcript_included=True,
                   cue_count=len(cues), corpus_path=str(path.relative_to(ROOT)))
        row.update({key: meta[key] for key in PROVENANCE_KEYS if key in meta})
        if old:
            rows[rows.index(old)] = row
        else:
            rows.append(row)
        staged.append((path, meta, body))
    return rows, staged


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel-root", required=True, type=Path)
    parser.add_argument("--video-id", required=True, action="append")
    parser.add_argument("--apply", action="store_true", help="Write local release draft only")
    args = parser.parse_args()
    rows, staged = prepare(args.channel_root.resolve(), args.video_id)
    if args.apply:
        for path, meta, body in staged:
            write_markdown(path, meta, body)
        (ROOT / "catalog/videos.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows))
    print(json.dumps({"mode": "local-apply" if args.apply else "plan-only", "videos": args.video_id,
                      "corpus_paths": [str(path.relative_to(ROOT)) for path, _, _ in staged],
                      "publication": "none"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
