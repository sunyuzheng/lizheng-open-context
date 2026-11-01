#!/usr/bin/env python3
"""Reconcile programme identity, public transcript versions and speaker coverage.

Channel listings are discovery candidates, never proof that a video is public.
This report reads committed source facts; it neither guesses guests from titles
nor downloads private/member sources. Run after every interview ingestion.
"""
from __future__ import annotations
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def reconcile(root=ROOT, listing=None):
    catalog = json.loads((root / "catalog/guests.json").read_text())
    videos = {r["id"]: r for r in map(json.loads, (root / "catalog/videos.jsonl").read_text().splitlines())}
    policy = json.loads((root / "config/public-dialogue-policy.json").read_text())
    dialogues = {r.get("source_id") or "youtube-" + r["video_id"]: r for r in policy["records"]}
    people = {}
    for r in catalog["appearances"]:
        people.setdefault(r["source_id"], []).append(r["entity_id"])
    rows = []
    for s in catalog["sources"]:
        sid = s["source_id"]
        row = {"source_id": sid, "url": s["url"], "title": s["title"], "participants": people.get(sid, [])}
        if sid in dialogues:
            record = dialogues[sid]
            data = json.loads((root / record["corpus_path"]).read_text())
            counts = Counter(u.get("speaker_id", "unknown") for u in data["units"])
            row.update(text="structured-dialogue", text_path=record["corpus_path"], source_sha256=record["sha256"],
                       speaker_units=dict(counts), speaker_state="partially-attributed" if counts.get("unknown") and len(counts) > 1
                       else "unresolved" if counts.get("unknown") else "attributed")
        elif videos.get(sid, {}).get("transcript_included"):
            row.update(text="legacy-transcript", text_path=videos[sid].get("corpus_path"), speaker_state="see-source-provenance")
        else:
            row.update(text="missing", speaker_state="no-text")
        if s.get("source_type") == "youtube" and sid not in videos:
            row["catalogue_gap"] = "missing-video-row"
        rows.append(row)
    result = {"schema_version": 1, "method": "catalogue participation and exact admitted source snapshots; no title classification",
              "summary": dict(Counter(r["text"] for r in rows)), "programmes": rows}
    if listing:
        known = set(videos) | set(dialogues)
        result["unclassified_listing_candidates"] = [r["video_id"] for r in listing["videos"] if "youtube-" + r["video_id"] not in known]
        result["listing_notice"] = "These IDs require anonymous per-video visibility and interview classification checks; a channel listing can contain member videos."
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--listing", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = reconcile(listing=json.loads(args.listing.read_text()) if args.listing else None)
    value = json.dumps(report, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(value)
    else:
        print(value)


if __name__ == "__main__":
    main()
