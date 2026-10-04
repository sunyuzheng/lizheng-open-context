#!/usr/bin/env python3
"""Import the conversations that shaped Yuzheng's values; default dry-run.

The author asked on 2026-10-04 to turn his conversations with 格桑泽仁 (问道), 赵智沉, 王路 and Leon
into Open Context source material. Four of these conversations are member videos whose transcripts
are already open; this script adds the six public ones (王路 and Leon) exactly as reviewed in
config/values-conversations-policy.json, and lists the reviewed excerpts of Yuzheng's own turns in
catalog/conversation-excerpts.jsonl.

  --archive DIR     the channel subtitle archive the public transcripts come from
  --apply           write the transcripts, the video catalog rows and the excerpt catalog
  --write-policy    re-pin the transcript and excerpt hashes after a reviewed edit
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from enrich_provenance import read_markdown, write_markdown
from export_public_corpus import display_timestamp, parse_timed_transcript, sanitize_first_party_text
from rights import LICENSE_TEXTS, REFERENCE_USE

ROOT = Path(__file__).resolve().parents[1]
POLICY = "config/values-conversations-policy.json"
EXCERPTS = "corpus/conversation-excerpts"
EXCERPT_CATALOG = "catalog/conversation-excerpts.jsonl"
AUTHORIZATION = "maintainer-request-2026-10-04-values-conversations"
QUALITY = {"youtube_human_subtitle": "human-caption", "local_timed_unknown": "source-unverified"}
LICENSE_URL = f"https://github.com/sunyuzheng/lizheng-open-context/blob/main/{LICENSE_TEXTS[REFERENCE_USE]}"
TRANSCRIPT_NOTE = ("频道发布者 2026-10-04 授权收录的公开对话字幕；说话人没有逐段标注。嘉宾、提问者和引文分别归相应说话人，"
                   "嘉宾的话不能当作立正的立场；立正本人可确认的发言另行摘录在 corpus/conversation-excerpts/。"
                   "收录不改变嘉宾对自己言论的权利。以原视频核实说话人和准确措辞。")
TRANSCRIPT_CONTEXT = ("Public channel conversation; the publisher authorized open transcript inclusion on 2026-10-04 for the "
                      "conversations that shaped his values. Speaking turns are not diarized; Yuzheng's own turns are reviewed separately.")
EXCERPT_FIELDS = (
    "id", "title", "published_at", "rights_scope", "license", "author", "publisher", "original_author",
    "content_origin", "generation_method", "evidence_role", "yuzheng_stance_weight", "attribution_note",
    "source_family", "source_context", "language", "source_visibility", "text_access", "membership_platform",
    "membership_url", "membership_verified_at", "transcript_source_kind", "transcript_quality",
    "inclusion_authorization", "speaker_classification", "review_status", "third_party_exclusions",
    "source_type", "video_id", "source_transcript", "guest_names", "excerpt_count",
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_policy(root: Path = ROOT) -> dict:
    policy = json.loads((root / POLICY).read_text(encoding="utf-8"))
    if policy.get("authorization") != AUTHORIZATION:
        raise ValueError("Values conversation policy lacks the explicit maintainer request")
    ids = [item["video_id"] for item in policy["public_transcripts"]]
    if len(ids) != len(set(ids)) or any(not re.fullmatch(r"[A-Za-z0-9_-]{11}", identity) for identity in ids):
        raise ValueError("Invalid or duplicate public conversation IDs")
    return policy


def find_subtitle(archive: Path, identity: str, kind: str) -> Path:
    """The archived subtitle for one video: the human Chinese track, or the only timed track."""
    folders = [path for path in archive.glob(f"*/*_{identity}") if path.is_dir()]
    if len(folders) != 1:
        raise ValueError(f"{identity}: expected one archive folder, found {len(folders)}")
    if kind == "youtube_human_subtitle":
        candidates = list(folders[0].glob("*.zh.srt"))
    else:
        candidates = [path for path in folders[0].glob("*.srt") if path.name.count(".") == 1]
    if len(candidates) != 1:
        raise ValueError(f"{identity}: expected one {kind} subtitle, found {len(candidates)}")
    return candidates[0]


def transcript_text(path: Path, url: str) -> str:
    cues = parse_timed_transcript(path)
    if not cues:
        raise ValueError(f"{path.name}: empty timed transcript")
    # ASS hard-space escapes (\h) are layout, not words.
    clean = lambda value: re.sub(r"\s+", " ", value.replace("\\h", " ")).strip()
    return "\n\n".join(f"[{display_timestamp(seconds)}]({url}&t={seconds}s) {sanitize_first_party_text(clean(value))}"
                       for seconds, value in cues)


def prepare_public(archive: Path, policy: dict, root: Path = ROOT) -> tuple[list[tuple[Path, dict, str]], list[dict]]:
    archive = archive.expanduser().resolve()
    rows = [json.loads(line) for line in (root / "catalog/videos.jsonl").read_text(encoding="utf-8").splitlines()]
    by_id = {row["video_id"]: row for row in rows}
    writes = []
    for approved in policy["public_transcripts"]:
        identity, kind = approved["video_id"], approved["transcript_source_kind"]
        old = by_id.get(identity)
        if not old:
            raise ValueError(f"{identity}: not in the video catalog")
        if old.get("title") != approved["title"] or old.get("published_at") != approved["published_at"]:
            raise ValueError(f"{identity}: catalog metadata differs from the reviewed policy")
        subtitle = find_subtitle(archive, identity, kind)
        if digest(subtitle) != approved["transcript_sha256"]:
            raise ValueError(f"{identity}: subtitle differs from the reviewed snapshot")
        url = f"https://www.youtube.com/watch?v={identity}"
        author = "Yuzheng Sun; " + "; ".join(approved["guest_names"])
        meta = dict(id=f"youtube-{identity}", title=approved["title"], author=author, publisher="Yuzheng Sun",
                    original_author=author, source_type="video-transcript", source_url=url,
                    published_at=approved["published_at"], snapshot_at=policy["reviewed_at"], content_status="current",
                    rights_scope="publisher-authorized-transcript", license=REFERENCE_USE,
                    speaker_classification="mixed-or-unresolved", review_status="maintainer-authorized",
                    third_party_exclusions=True, transcript_status=kind,
                    content_origin="mixed-or-unresolved-speech", generation_method="transcription",
                    evidence_role="speaker-attributed-speech", yuzheng_stance_weight="not-evidence",
                    source_family=url, language="zh", source_context=TRANSCRIPT_CONTEXT, attribution_note=TRANSCRIPT_NOTE,
                    source_visibility="public", text_access="public", transcript_source_kind=kind,
                    transcript_quality=QUALITY[kind], transcript_source_sha256=approved["transcript_sha256"],
                    inclusion_authorization=AUTHORIZATION, publication_date_provenance="youtube-published-at")
        target = root / "corpus/videos" / f"{approved['published_at'][:10].replace('-', '')}-{identity}.md"
        body = (f"# {approved['title']}\n\n> **公开视频** · [观看完整视频]({url}) · 字幕文字经频道发布者授权收录，按[立正参考使用许可]({LICENSE_URL})使用；"
                f"嘉宾的话归嘉宾本人。字幕来源：`{kind}`；校对状态：`{QUALITY[kind]}`。以原视频核实说话人和准确措辞。\n\n"
                f"{transcript_text(subtitle, url)}\n")
        writes.append((target, meta, body))
        row = {**old, **{k: v for k, v in meta.items() if k not in {"source_url", "source_type", "snapshot_at", "content_status"}},
               "url": url, "corpus_path": str(target.relative_to(root)), "transcript_available": True,
               "transcript_included": True, "guest_names": approved["guest_names"], "rights_reason": AUTHORIZATION}
        row["cue_count"] = len(parse_timed_transcript(subtitle))
        by_id[identity] = row
    ordered = sorted(by_id.values(), key=lambda row: (str(row.get("published_at") or ""), row["video_id"]))
    return writes, ordered


def excerpt_rows(root: Path = ROOT) -> list[dict]:
    rows = []
    for path in sorted((root / EXCERPTS).glob("*.md")):
        meta, _ = read_markdown(path)
        row = {key: meta[key] for key in EXCERPT_FIELDS if key in meta}
        row.update(url=meta["source_url"], full_text_included=True, corpus_path=str(path.relative_to(root)))
        rows.append(row)
    return sorted(rows, key=lambda row: (str(row.get("published_at")), row["id"]))


def write_policy(root: Path, archive: Path | None) -> dict:
    policy = load_policy(root)
    if archive:
        for item in policy["public_transcripts"]:
            item["transcript_sha256"] = digest(find_subtitle(archive.expanduser().resolve(), item["video_id"], item["transcript_source_kind"]))
    conversations = []
    for row in excerpt_rows(root):
        path = root / row["corpus_path"]
        conversations.append(dict(video_id=row["video_id"], title=row["title"], guest_names=row["guest_names"],
                                  source_visibility=row["source_visibility"], source_transcript=row["source_transcript"],
                                  excerpt_path=row["corpus_path"], excerpt_count=row["excerpt_count"], excerpt_sha256=digest(path)))
    policy["conversations"] = conversations
    (root / POLICY).write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return policy


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--archive", type=Path)
    parser.add_argument("--apply", action="store_true", help="write local files only; never push or deploy")
    parser.add_argument("--write-policy", action="store_true")
    args = parser.parse_args()
    if args.write_policy:
        policy = write_policy(ROOT, args.archive)
        print(json.dumps({"mode": "policy", "public_transcripts": len(policy["public_transcripts"]),
                          "conversations": len(policy["conversations"])}, ensure_ascii=False))
        return
    policy = load_policy()
    writes, rows = prepare_public(args.archive, policy) if args.archive else ([], [])
    excerpts = excerpt_rows()
    if args.apply:
        for target, meta, body in writes:
            write_markdown(target, meta, body)
        if rows:
            (ROOT / "catalog/videos.jsonl").write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        (ROOT / EXCERPT_CATALOG).write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in excerpts), encoding="utf-8")
    print(json.dumps({"mode": "local-apply" if args.apply else "dry-run", "public_transcripts": len(writes),
                      "excerpt_files": len(excerpts), "excerpts": sum(row.get("excerpt_count", 0) for row in excerpts)},
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
