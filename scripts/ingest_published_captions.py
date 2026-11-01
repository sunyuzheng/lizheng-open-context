#!/usr/bin/env python3
"""Prepare exact publisher captions from an anonymously verified public interview.

Default is a local dry run. --write updates this checkout, never pushes or publishes.
Programme identity/participants must already have been reviewed into guests.json.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

from dialogue_policy import CHANNEL, INTERVIEW_AUTHORIZATION, PROVENANCE
from raw_turn_policy import digest, unknown_units

ROOT = Path(__file__).resolve().parents[1]


def timestamp(value):
    h, m, s = value.replace(",", ".").split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def captions(raw, duration, *, automatic=False):
    rows = []
    for block in re.split(r"\n\s*\n", raw.replace("\r\n", "\n")):
        lines = block.splitlines()
        match = next((re.match(r"(\d{2}:\d{2}:\d{2}[.,]\d+) --> (\d{2}:\d{2}:\d{2}[.,]\d+)", s) for s in lines if " --> " in s), None)
        if not match:
            continue
        a, b = map(timestamp, match.groups())
        line = lines.index(match.string)
        content = lines[line + 1:]
        if automatic:
            # YouTube rolling captions repeat the previous row in a 10ms cue.
            # Keep only new word-timed rows, preserving their words and order.
            content = [s for s in content if re.search(r"<\d{2}:\d{2}:\d{2}", s)]
            if not content:
                continue
        text = html.unescape(re.sub(r"<[^>]*>", "", " ".join(content))).strip()
        if not text or not 0 <= a <= b <= duration + 3 or (rows and a < rows[-1]["start_seconds"]):
            raise ValueError("invalid_caption_text_or_timebase")
        rows.append(dict(id=f"cue-{len(rows) + 1}", start_seconds=a, end_seconds=b, text=text,
                         speaker_id="unknown", speaker_name="", speaker_status="unresolved"))
    if not rows:
        raise ValueError("empty_captions")
    return rows


def prepare(info, caption_raw, root=ROOT, *, automatic=False, language="zh"):
    vid = info.get("id", "")
    if (not re.fullmatch(r"[A-Za-z0-9_-]{11}", vid) or info.get("channel_id") != CHANNEL
            or info.get("availability") != "public" or info.get("is_live") is not False
            or info.get("live_status") != "not_live" or info.get("age_limit", 0) != 0
            or type(info.get("duration")) not in (int, float) or not math.isfinite(info["duration"]) or info["duration"] <= 0):
        raise ValueError("not_verified_public_channel_video")
    sid = f"youtube-{vid}"
    catalog = json.loads((root / "catalog/guests.json").read_text())
    source = next((s for s in catalog["sources"] if s["source_id"] == sid), None)
    people = [r["entity_id"] for r in catalog["appearances"] if r["source_id"] == sid]
    if not source or not people or source["title"] != info["title"]:
        raise ValueError("reviewed_programme_identity_required")
    units = captions(caption_raw.decode("utf-8"), info["duration"], automatic=automatic)
    method = "platform-auto-captions" if automatic else "publisher-captions"
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    url = f"https://www.youtube.com/watch?v={vid}"
    data = {**PROVENANCE, "schema_version": 1, "id": sid, "video_id": vid,
            "title": info["title"], "source_url": url, "source_family": url,
            "source_duration_seconds": info["duration"], "inclusion_authorization": INTERVIEW_AUTHORIZATION,
            "published_at": datetime.strptime(info["upload_date"], "%Y%m%d").date().isoformat(),
            "public_verified_at": now, "language": language, "units": units,
            "generation_method": method, "transcript_source_kind": method.replace("captions", "timed-captions"),
            "transcript_quality": method + "-unverified",
            "quality": {"method": method, "caption_sha256": hashlib.sha256(caption_raw).hexdigest(),
                        "unresolved_count": len(units),
                        "caption_units_sha256": digest(unknown_units(units)), "human_audio_review": False,
                        "full_precision_certified": False, "complete_speech_coverage_verified": False}}
    raw = encode(data)
    row = {"video_id": vid, "programme_type": "interview", "corpus_path": f"corpus/dialogues/{sid}.json",
           "sha256": hashlib.sha256(raw).hexdigest(), "cue_count": len(units),
           "anonymous_evidence": {"video_id": vid, "channel_id": CHANNEL, "availability": "public",
              "is_live": False, "is_upcoming": False, "verified_at": now,
              "receipt_sha256": digest({k: info.get(k) for k in ("id", "channel_id", "title", "availability", "duration", "upload_date", "live_status")})}}
    return data, row


def encode(data):
    return (json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--info", type=Path, required=True)
    parser.add_argument("--captions", type=Path, required=True)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--automatic", action="store_true")
    parser.add_argument("--language", choices=("zh", "en", "mixed"), default="zh")
    args = parser.parse_args()
    data, row = prepare(json.loads(args.info.read_text()), args.captions.read_bytes(), automatic=args.automatic, language=args.language)
    path = ROOT / row["corpus_path"]
    policy_path = ROOT / "config/public-dialogue-policy.json"
    policy = json.loads(policy_path.read_text())
    if path.exists() or any(r.get("video_id") == data["video_id"] for r in policy["records"]):
        raise ValueError("existing_source_requires_separate_review")
    if args.write:
        path.write_bytes(encode(data))
        policy["records"].append(row)
        policy_path.write_bytes(encode(policy))
    print(json.dumps({"write": args.write, "path": row["corpus_path"], "cues": len(data["units"]), "sha256": row["sha256"]}))


if __name__ == "__main__":
    main()
