#!/usr/bin/env python3
"""Import AI translations only when their source is an included solo video.

These are repository reading aids, not evidence that Yuzheng spoke English or
published an English version. Original and translated sources share one family.
"""
from __future__ import annotations
import argparse
import json
import re
from pathlib import Path

from enrich_provenance import read_markdown, write_markdown
from export_public_corpus import parse_timed_transcript, display_timestamp

ROOT = Path(__file__).resolve().parents[1]
TIMING = re.compile(r"\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[,.]\d{3}")


def source_has_video_id(path: Path, identity: str) -> bool:
    pattern = re.compile(r"(?:^|_)" + re.escape(identity) + r"(?:$|\.)")
    return any(pattern.search(part) for part in path.parts)


def import_translations(manifest: Path, channel_root: Path, library_root: Path) -> dict:
    videos = {r["video_id"]: r for r in (json.loads(line) for line in (ROOT / "catalog/videos.jsonl").read_text().splitlines()) if r["transcript_included"]}
    rows = []
    seen = set()
    directory = ROOT / "corpus/english-translations"
    directory.mkdir(exist_ok=True)
    for record in json.loads(manifest.read_text()):
        if record.get("state") != "canonical_clean":
            continue
        matches = [identity for identity in videos if source_has_video_id(Path(record["source_srt"]), identity)]
        if len(matches) != 1:
            continue
        identity = matches[0]
        if identity in seen:
            raise ValueError(f"Duplicate canonical translation: {identity}")
        source = Path(record["source_srt"]).resolve()
        source.relative_to(channel_root.resolve())
        info_ids = {json.loads(p.read_text()).get("id") for p in source.parent.glob("*.info.json")}
        if info_ids and identity not in info_ids:
            raise ValueError(f"Source platform metadata ID differs: {identity}")
        translated = Path(record["translated_srt"]).resolve()
        translated.relative_to(library_root.resolve())
        readable = Path(record["readable_path"]).resolve()
        readable.relative_to(library_root.resolve())
        source_times = TIMING.findall(source.read_text(encoding="utf-8-sig"))
        translated_times = TIMING.findall(translated.read_text(encoding="utf-8-sig"))
        if not source_times or source_times != translated_times:
            raise ValueError(f"Translation timing differs from source: {identity}")
        source_meta, _ = read_markdown(readable)
        generated_at = source_meta.get("generated_at")
        if not generated_at:
            raise ValueError(f"Unknown translation generation date: {identity}")
        video = videos[identity]
        url = video["url"]
        meta = dict(id=f"youtube-{identity}-en-ai", title=record["title"],
                    author="AI", original_author="Yuzheng Sun", publisher="Yuzheng Sun",
                    source_type="video-translation", source_video_id=identity,
                    source_url=url, original_source_url=url, source_family=url,
                    published_at=video["published_at"], generated_at=generated_at,
                    snapshot_at="2026-09-17", translation_publication_status="repository-reading-aid-not-platform-publication",
                    language="en", original_language="zh", content_origin="ai-translation",
                    generation_method="ai-translation", generation_model=record.get("model") or source_meta.get("model"),
                    evidence_role="translation", yuzheng_stance_weight="verify-original",
                    rights_scope="first-party-derivative", license="CC-BY-4.0", third_party_exclusions=True,
                    content_status="current", cue_alignment_status="verified-against-source-srt",
                    source_context="AI-generated English reading aid for an already published, included solo presentation. Publication date belongs to the original video, not to this English translation.",
                    attribution_note="AI-translated English, NOT Yuzheng's original English wording. Original speaker: Yuzheng Sun. Quoted community authors, audience questions and other people's experiences remain theirs, even if read aloud by Yuzheng. Verify speaker/quotation boundaries and exact claims against the original timestamped source. This translation and its Chinese source are one source family, not independent corroboration.")
        cues = parse_timed_transcript(translated)
        # The shared renderer collapses adjacent repeated subtitle text. Raw SRT
        # cue boundaries were compared above before that presentation cleanup.
        if not cues:
            raise ValueError(f"Empty translated transcript: {identity}")
        path = directory / f"{video['published_at'][:10].replace('-', '')}-{identity}-en.md"
        body = f"# {record['title']}\n\n" + "\n".join(f"[{display_timestamp(seconds)}]({url}&t={seconds}s) {text}\n" for seconds, text in cues)
        write_markdown(path, meta, body)
        rows.append({**meta, "url": url, "full_text_included": True, "corpus_path": str(path.relative_to(ROOT)), "cue_count": len(cues)})
        seen.add(identity)
    expected = {r["corpus_path"] for r in rows}
    actual = {str(p.relative_to(ROOT)) for p in directory.glob("*.md")}
    if actual != expected:
        raise ValueError("Unexpected stale translation files; review removals explicitly")
    (ROOT / "catalog/english-translations.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows))
    return {"english_ai_translations": len(rows), "aligned_cues": sum(r["cue_count"] for r in rows)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--channel-root", type=Path, required=True)
    parser.add_argument("--library-root", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(import_translations(args.manifest, args.channel_root, args.library_root)))


if __name__ == "__main__":
    main()
