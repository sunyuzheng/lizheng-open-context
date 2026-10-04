#!/usr/bin/env python3
"""Import the exact maintainer-authorized member transcript snapshot; default dry-run."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

from export_public_corpus import display_timestamp, front_matter, parse_timed_transcript, sanitize_first_party_text
from enrich_provenance import read_markdown, write_markdown
from rights import LICENSE_TEXTS, REFERENCE_USE

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config/member-video-policy.json"
LICENSE_URL = f"https://github.com/sunyuzheng/lizheng-open-context/blob/main/{LICENSE_TEXTS[REFERENCE_USE]}"
MEMBER_FIELDS = (
    "source_visibility", "text_access", "membership_platform", "membership_url",
    "membership_verified_at", "transcript_source_kind", "transcript_quality",
    "transcript_source_sha256", "inclusion_authorization", "publication_date_provenance",
)
QUALITY = {
    "youtube_studio_export": "studio-caption", "youtube_human_subtitle": "human-caption",
    "local_corrected": "corrected", "local_corrected_timing_normalized": "corrected",
    "local_qwen_uncorrected": "uncorrected-asr", "local_timed_unknown": "source-unverified",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize_date(value: str | None) -> str | None:
    if not value:
        return None
    if re.fullmatch(r"\d{8}", value):
        return datetime.strptime(value, "%Y%m%d").date().isoformat()
    datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


def load_policy(path: Path = POLICY) -> dict:
    policy = json.loads(path.read_text())
    if policy.get("authorization") != "maintainer-request-2026-10-02-member-transcripts":
        raise ValueError("Member transcript policy lacks the explicit inclusion authorization")
    ids = [row["video_id"] for row in policy["records"]]
    if len(ids) != 218 or policy.get("membership_url") != "https://www.youtube.com/channel/UC_5lJHgnMP_lb_VpIiXV0hQ/join":
        raise ValueError("Expected the exact 218-video channel membership snapshot")
    if len(ids) != len(set(ids)) or any(not re.fullmatch(r"[A-Za-z0-9_-]{11}", identity) for identity in ids):
        raise ValueError("Invalid or duplicate authorized member video IDs")
    return policy


def prepare(archive: Path, policy: dict, root: Path = ROOT) -> tuple[dict, list[tuple[Path, dict, str]], list[dict]]:
    root = root.resolve()
    archive = archive.expanduser().resolve()
    catalog = root / "catalog/videos.jsonl"
    rows = [json.loads(line) for line in catalog.read_text().splitlines()]
    by_id = {row["video_id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("Existing video catalog has duplicate identities")
    writes = []
    counts = {"authorized_member_videos": len(policy["records"]), "new_transcripts": 0, "existing_transcripts_marked": 0, "new_catalog_entries": 0}
    for approved in policy["records"]:
        identity = approved["video_id"]
        folder = archive / identity
        folder.resolve().relative_to(archive)
        source = json.loads((folder / "source.json").read_text())
        path = folder / "transcript.srt"
        url = f"https://www.youtube.com/watch?v={identity}"
        if source.get("video_id") != identity or source.get("source_url") != url:
            raise ValueError(f"{identity}: archive identity/source URL mismatch")
        if source.get("visibility") != "Members" or source.get("membership_verified") is not True:
            raise ValueError(f"{identity}: missing verified membership provenance")
        if source.get("membership_verified_at") != policy["snapshot_at"]:
            raise ValueError(f"{identity}: membership snapshot changed; review a new policy")
        if digest(path) != approved["transcript_sha256"] or source.get("transcript_sha256") != approved["transcript_sha256"]:
            raise ValueError(f"{identity}: transcript differs from authorized snapshot")
        kind = source["transcript_source_kind"]
        if kind not in QUALITY:
            raise ValueError(f"{identity}: unknown transcript provenance")
        date = normalize_date(source.get("published_at") or source.get("studio_display_date"))
        if date != approved["published_at"] or source["title"] != approved["title"] or kind != approved["transcript_source_kind"]:
            raise ValueError(f"{identity}: source metadata differs from reviewed policy")
        access = dict(source_visibility="members-only", text_access="public", membership_platform="youtube",
                      membership_url=policy["membership_url"], membership_verified_at=policy["snapshot_at"],
                      transcript_source_kind=kind, transcript_quality=QUALITY[kind],
                      transcript_source_sha256=approved["transcript_sha256"], inclusion_authorization=policy["authorization"],
                      publication_date_provenance="studio-display-date" if not source.get("published_at") else "archive-source-date")
        old = by_id.get(identity, {})
        if not old:
            counts["new_catalog_entries"] += 1
        # Preserve a previously approved solo transcript and its source text.
        existing = bool(old.get("transcript_included"))
        solo = existing and old.get("rights_scope") == "first-party" and old.get("speaker_classification") == "solo-yuzheng"
        if solo and not approved.get("prior_solo_transcript"):
            raise ValueError(f"{identity}: no prior solo transcript approval in the member policy")
        if existing:
            target = (root / old["corpus_path"]).resolve()
            target.relative_to(root.resolve())
            meta, body = read_markdown(target)
            # Existing text may use a different source from the newly archived SRT.
            if solo:
                access["transcript_source_kind"] = old.get("transcript_source_kind", "previously-included-transcript")
                access["transcript_quality"] = old.get("transcript_quality", "human-caption" if meta.get("transcript_status") == "human" else "source-unverified")
                access.pop("transcript_source_sha256", None)
                if old.get("transcript_source_sha256"):
                    access["transcript_source_sha256"] = old["transcript_source_sha256"]
                access["archived_transcript_sha256"] = approved["transcript_sha256"]
            meta.update(access)
            counts["existing_transcripts_marked"] += 1
        else:
            target = root / "corpus/videos" / f"{(date or 'undated')[:10].replace('-', '')}-{identity}.md"
            speakers = approved.get("guest_names", [])
            author = "Yuzheng Sun; " + ("; ".join(speakers) if speakers else "other or unresolved speakers")
            meta = dict(id=f"youtube-{identity}", title=source["title"], author=author, publisher="Yuzheng Sun",
                        original_author=author, source_type="video-transcript", source_url=url,
                        published_at=date, snapshot_at=policy["snapshot_at"], content_status="current",
                        rights_scope="publisher-authorized-transcript", license=REFERENCE_USE,
                        speaker_classification="mixed-or-unresolved", review_status="maintainer-authorized",
                        third_party_exclusions=True, transcript_status=kind,
                        content_origin="mixed-or-unresolved-speech", generation_method="transcription",
                        evidence_role="speaker-attributed-speech", yuzheng_stance_weight="not-evidence",
                        source_family=url, language="en" if "英文" in (source.get("caption_text_language_note") or "") else (source.get("source_language") or "und"),
                        source_context="Channel member video; publisher authorized open transcript inclusion. Speaking turns are not diarized; identify each speaker at the original timestamp.",
                        attribution_note="频道发布者授权开放的会员视频字幕；多人或说话人边界未逐段确认。嘉宾、提问者、引文和本人观点分别归相应说话人；无法确认说话人时保持未知，不把整份字幕归成立正立场。收录不改变第三方原有权利，也不开放原视频的会员访问权限。",
                        **access)
            cues = parse_timed_transcript(path)
            if not cues:
                raise ValueError(f"{identity}: empty timed transcript")
            text = "\n\n".join(f"[{display_timestamp(seconds)}]({url}&t={seconds}s) {sanitize_first_party_text(value)}" for seconds, value in cues)
            body = f"# {source['title']}\n\n> **会员视频** · [观看会员完整视频]({url}) · 字幕文字已获授权开放，按[立正参考使用许可]({LICENSE_URL})使用；原视频观看需频道会员。字幕来源：`{kind}`；校对状态：`{QUALITY[kind]}`。以原视频核实说话人和准确措辞。\n\n{text}\n"
            counts["new_transcripts"] += 1
        # Strip only the old generated access notice when re-running.
        body = re.sub(r"<!-- member-access:start -->.*?<!-- member-access:end -->\s*", "", body, flags=re.S)
        if solo:
            body = f"<!-- member-access:start -->\n> **会员视频** · 字幕文字已获授权开放；[观看会员完整视频]({url})需频道会员。\n<!-- member-access:end -->\n\n" + body
            meta["source_context"] = "Channel member video with an already approved solo-Yuzheng transcript; third-party quotations retain their speakers."
        row = {**old, **meta, "video_id": identity, "url": url, "corpus_path": str(target.relative_to(root)),
               "transcript_available": True, "transcript_included": True,
               "guest_names": old.get("guest_names") or approved.get("guest_names", []),
               "rights_reason": policy["authorization"]}
        row.pop("source_url", None)
        by_id[identity] = row
        writes.append((target, meta, body))
    return counts, writes, sorted(by_id.values(), key=lambda row: (str(row.get("published_at") or ""), row["video_id"]))


def apply_prepared(root: Path, writes: list, rows: list) -> None:
    for target, meta, body in writes:
        target.parent.mkdir(parents=True, exist_ok=True)
        write_markdown(target, meta, body)
    (root / "catalog/videos.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="Write local corpus only; never push or deploy")
    args = parser.parse_args()
    counts, writes, rows = prepare(args.archive, load_policy())
    if args.apply:
        apply_prepared(ROOT, writes, rows)
    print(json.dumps({"mode": "local-apply" if args.apply else "dry-run", **counts}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
