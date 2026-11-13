#!/usr/bin/env python3
"""Stage explicitly supplied public Shorts captions locally; no fetching or model calls.

The input manifest binds local info, caption and listing receipts by SHA256. --write
adds raw snapshots and their exact admission rows only; catalogs remain separately
reviewed. No source file is overwritten and the default makes no filesystem writes.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
from datetime import datetime
from pathlib import Path

from dialogue_policy import (CHANNEL, HASH, PROVENANCE, SHORTS_AUTHORIZATION, VIDEO_ID,
                             read_object, validate_public_short, validate_quality)
from raw_turn_policy import digest, unknown_units

ROOT = Path(__file__).resolve().parents[1]
METHODS = {"publisher-captions", "platform-auto-captions", "local-caption-copy"}
TIMING = re.compile(r"(?:(\d{2,}):)?([0-5]\d):([0-5]\d)[,.](\d{3})\s+-->\s+"
                    r"(?:(\d{2,}):)?([0-5]\d):([0-5]\d)[,.](\d{3})(?:\s+\S+:\S+)*\Z")


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True, allow_nan=False) + "\n").encode()


def verified_at(value):
    if not isinstance(value, str) or datetime.fromisoformat(value.replace("Z", "+00:00")).tzinfo is None:
        raise ValueError("verified_timestamp_required")
    return value


def captions(raw: bytes, duration: float):
    """Preserve every timed cue, including repeated/overlapping rolling-caption rows.

Only subtitle markup/entities are decoded; words, line breaks, starts and ends are
retained. This does not correct ASR, merge repeats, assign speakers or certify audio.
"""
    text = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    blocks = [s for s in re.split(r"\n[ \t]*\n+", text.strip()) if s.strip()]
    vtt = bool(blocks and blocks[0].startswith("WEBVTT"))
    if vtt:
        blocks.pop(0)
    rows = []
    for block in blocks:
        lines = block.splitlines()
        if vtt and re.match(r"^(?:NOTE(?:[ \t]|$)|STYLE$|REGION$)", lines[0]):
            continue
        i = 0 if "-->" in lines[0] else 1
        if len(lines) <= i + 1 or (not vtt and (i != 1 or not lines[0].isdigit())):
            raise ValueError("invalid_caption_cue")
        match = TIMING.fullmatch(lines[i])
        if not match:
            raise ValueError("invalid_caption_timing")
        values = match.groups()
        start, end = [int(values[j] or 0) * 3600 + int(values[j+1]) * 60
                      + int(values[j+2]) + int(values[j+3]) / 1000 for j in (0, 4)]
        words = "\n".join(lines[i+1:])
        words = re.sub(r"</?(?:c|v|b|i|u|lang|ruby|rt)(?:[ .][^>]*)?>", "", words)
        words = html.unescape(re.sub(r"<\d{2}:\d{2}(?::\d{2})?\.\d{3}>", "", words))
        if (not words.strip() or not 0 <= start < end <= duration + 3
                or (rows and start < rows[-1]["start_seconds"])):
            raise ValueError("invalid_caption_text_or_timebase")
        rows.append({"id": f"cue-{len(rows)+1}", "text": words, "start_seconds": start, "end_seconds": end,
                     "speaker_id": "unknown", "speaker_name": "", "speaker_status": "unresolved"})
    if not rows:
        raise ValueError("empty_captions")
    return rows


def bound_file(base: Path, binding, *, captions_file=False):
    if (not isinstance(binding, dict) or not isinstance(binding.get("path"), str)
            or not HASH.fullmatch(str(binding.get("sha256", "")))):
        raise ValueError("invalid_local_file_binding")
    path = (base / binding["path"]).resolve()
    if captions_file and path.suffix.lower() not in {".srt", ".vtt"}:
        raise ValueError("caption_file_must_be_srt_or_vtt")
    if not path.is_file() or path.stat().st_size > 10_000_000:
        raise ValueError("missing_or_oversize_input")
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != binding["sha256"]:
        raise ValueError("input_hash_mismatch")
    return raw


def prepare(info, caption_raw, listing, *, info_sha256, caption_sha256, listing_sha256,
            method, origin, language="zh", upload=None, parent=None, source=None):
    identity = info.get("id")
    if (not isinstance(identity, str) or not VIDEO_ID.fullmatch(identity)
            or info.get("channel_id") != CHANNEL or info.get("availability") != "public"
            or info.get("is_live") is not False or info.get("live_status") != "not_live"
            or info.get("age_limit", 0) != 0 or type(info.get("duration")) not in (int, float)
            or not math.isfinite(info["duration"]) or info["duration"] <= 0
            or not isinstance(info.get("title"), str) or not info["title"].strip()):
        raise ValueError("not_verified_public_channel_short")
    ids = listing.get("video_ids")
    if (type(listing.get("schema_version")) is not int or listing["schema_version"] != 1 or listing.get("channel_id") != CHANNEL
            or listing.get("source_url") != f"https://www.youtube.com/channel/{CHANNEL}/shorts"
            or not isinstance(ids, list) or any(not isinstance(i, str) or not VIDEO_ID.fullmatch(i) for i in ids)
            or len(ids) != len(set(ids)) or identity not in ids):
        raise ValueError("not_in_verified_public_shorts_listing")
    date = verified_at(listing.get("verified_at"))
    if ((method, origin) not in {("publisher-captions", "platform"), ("publisher-captions", "uploaded-local"),
                               ("platform-auto-captions", "platform"), ("local-caption-copy", "local-archive")}
            or language not in {"zh", "en", "mixed"}
            or any(not HASH.fullmatch(str(s)) for s in [info_sha256, caption_sha256, listing_sha256])
            or hashlib.sha256(caption_raw).hexdigest() != caption_sha256):
        raise ValueError("invalid_caption_binding")
    if origin == "local-archive":
        if (not isinstance(source, dict) or source.get("video_id") != identity
                or source.get("caption_sha256") != caption_sha256
                or source.get("public_metadata_sha256") != info_sha256 or upload is not None):
            raise ValueError("local_caption_source_receipt_required")
        verified_at(source.get("reviewed_at"))
    elif source is not None:
        raise ValueError("unexpected_local_source_binding")
    if origin == "uploaded-local":
        if (method != "publisher-captions" or not isinstance(upload, dict)
                or upload.get("video_id") != identity or upload.get("caption_sha256") != caption_sha256
                or upload.get("status") != "uploaded" or upload.get("platform") != "youtube"):
            raise ValueError("uploaded_caption_receipt_required")
        verified_at(upload.get("verified_at"))
    elif upload is not None:
        raise ValueError("unexpected_upload_binding")
    elif origin == "platform" and (not isinstance(info.get("subtitles" if method == "publisher-captions" else "automatic_captions"), dict) or not any(
            info["subtitles" if method == "publisher-captions" else "automatic_captions"].values())):
        raise ValueError("published_platform_caption_track_required")
    url = f"https://www.youtube.com/watch?v={identity}"
    family = url
    if parent is not None:
        if (not isinstance(parent, dict) or parent.get("video_id") != identity
                or not re.fullmatch(r"https://www\.youtube\.com/watch\?v=[A-Za-z0-9_-]{11}", str(parent.get("parent_url", "")))):
            raise ValueError("invalid_parent_binding")
        verified_at(parent.get("verified_at"))
        family = parent["parent_url"]
    units = captions(caption_raw, info["duration"])
    published = datetime.strptime(info["upload_date"], "%Y%m%d").date().isoformat()
    data = {**PROVENANCE, "schema_version": 1, "id": f"youtube-{identity}", "video_id": identity,
            "title": info["title"], "source_url": url, "source_family": family,
            "source_duration_seconds": info["duration"], "timestamp_mode": "youtube",
            "published_at": published, "public_verified_at": date, "language": language,
            "inclusion_authorization": SHORTS_AUTHORIZATION, "generation_method": method,
            "transcript_source_kind": method.replace("captions", "timed-captions"),
            "transcript_quality": "source-unverified" if method == "local-caption-copy" else method + "-unverified", "units": units,
            "source_context": "Exact public Shorts caption snapshot; unverified wording and unresolved speakers. Repeated caption rows and overlaps remain in source order.",
            "quality": {"method": method, "caption_origin": origin, "caption_sha256": caption_sha256,
                        "original_source_sha256": caption_sha256, "caption_units_sha256": digest(unknown_units(units)),
                        "shorts_receipt_sha256": listing_sha256, "unresolved_count": len(units),
                        "human_audio_review": False, "full_precision_certified": False,
                        "complete_speech_coverage_verified": False}}
    row = {"video_id": identity, "programme_type": "short", "corpus_path": f"corpus/dialogues/youtube-{identity}.json",
           "sha256": hashlib.sha256(encode(data)).hexdigest(), "cue_count": len(units),
           "anonymous_evidence": {"video_id": identity, "channel_id": CHANNEL, "availability": "public",
                                  "is_live": False, "is_upcoming": False, "verified_at": date, "receipt_sha256": info_sha256},
           "shorts_evidence": {"video_id": identity, "channel_id": CHANNEL,
                               "source_url": listing["source_url"], "verified_at": date,
                               "receipt_sha256": listing_sha256, "present": True},
           "caption_evidence": {"video_id": identity, "method": method, "origin": origin,
                                "caption_sha256": caption_sha256, "info_sha256": info_sha256}}
    if upload is not None:
        row["upload_binding"] = {k: upload[k] for k in ("video_id", "caption_sha256", "status", "platform", "verified_at", "receipt_sha256")}
    if parent is not None:
        row["parent_binding"] = {k: parent[k] for k in ("video_id", "parent_url", "verified_at", "receipt_sha256")}
    if source is not None:
        row["source_binding"] = {k: source[k] for k in ("video_id", "caption_sha256", "association_basis", "source_kind",
                                                       "reviewed_at", "public_metadata_sha256", "receipt_sha256")}
        data["quality"].update(new_text_rewrite=False, ai_text_processing_verified=False, source_association_reviewed=True,
                               source_binding_receipt_sha256=source["receipt_sha256"], local_source_kind=source["source_kind"])
        data["source_context"] = ("Unmodified local archive caption copy associated with this public Shorts video by an exact review receipt. "
                                  "Not a platform caption or upload claim; no new text rewrite or full audio review. Speakers remain unresolved unless separately attributed.")
        row["sha256"] = hashlib.sha256(encode(data)).hexdigest()
    validate_public_short(data, row)
    validate_quality(data)
    return data, row


def prepare_manifest(path: Path, root=ROOT):
    manifest = read_object(path)
    if (manifest.get("schema_version") != 1 or manifest.get("authorization") != SHORTS_AUTHORIZATION
            or not isinstance(manifest.get("records"), list) or not manifest["records"]):
        raise ValueError("invalid_public_shorts_manifest")
    prepared = []
    ids = set()
    for item in manifest["records"]:
        base = path.resolve().parent
        info_raw = bound_file(base, item["info"])
        caption_raw = bound_file(base, item["captions"], captions_file=True)
        listing_raw = bound_file(base, item["shorts_receipt"])
        optional = {}
        for key, argument in [("upload_binding", "upload"), ("parent_binding", "parent"), ("source_binding", "source")]:
            if key in item:
                b = bound_file(base, item[key]); optional[argument] = {
                    **json.loads(b), "receipt_sha256": item[key]["sha256"]}
        data, row = prepare(json.loads(info_raw), caption_raw, json.loads(listing_raw),
                            info_sha256=item["info"]["sha256"], caption_sha256=item["captions"]["sha256"],
                            listing_sha256=item["shorts_receipt"]["sha256"], method=item["captions"]["method"],
                            origin=item["captions"]["origin"], language=item.get("language", "zh"), **optional)
        if data["video_id"] in ids:
            raise ValueError("duplicate_manifest_video")
        ids.add(data["video_id"]); prepared.append((data, row))
    policy_path = root / "config/public-dialogue-policy.json"
    policy = read_object(policy_path)
    existing = {r.get("video_id") for r in policy["records"] if r.get("video_id")}
    catalog_path = root / "catalog/videos.jsonl"
    if catalog_path.is_file():
        existing.update(r.get("video_id") for r in
                        (json.loads(line) for line in catalog_path.read_text().splitlines() if line.strip())
                        if r.get("transcript_included") is True)
    for data, row in prepared:
        if data["video_id"] in existing or (root / row["corpus_path"]).exists():
            raise ValueError("existing_source_requires_separate_review")
    return prepared, policy


def run(path: Path, *, write=False, root=ROOT):
    prepared, policy = prepare_manifest(path, root)
    if write:
        for data, row in prepared:
            target = root / row["corpus_path"]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(encode(data))
        policy["records"].extend(row for _, row in prepared)
        (root / "config/public-dialogue-policy.json").write_bytes(encode(policy))
    return {"mode": "local-write" if write else "dry-run", "publication": "none", "videos": len(prepared),
            "cues": sum(row["cue_count"] for _, row in prepared),
            "sources": [{"video_id": data["video_id"], "path": row["corpus_path"], "sha256": row["sha256"]} for data, row in prepared]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--write", action="store_true", help="Write local raw snapshots and exact admission rows only")
    args = parser.parse_args()
    print(json.dumps(run(args.manifest, write=args.write), ensure_ascii=False))


if __name__ == "__main__":
    main()
