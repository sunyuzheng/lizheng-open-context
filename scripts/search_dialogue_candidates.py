#!/usr/bin/env python3
"""Read-only local dialogue search; never imports candidates into public context."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import search
from build_dialogue_candidates import ROOT, digest, safe


def verify_pack(pack: Path, *, verify_inputs=True) -> dict:
    pack = safe(pack.absolute(), ROOT, Path(".source-cache"))
    manifest_path = safe(pack / "manifest.json", ROOT, Path(".source-cache"), file=True)
    receipt_path = safe(pack / "receipt.json", ROOT, Path(".source-cache"), file=True)
    raw = manifest_path.read_bytes()
    manifest = json.loads(raw)
    receipt = json.loads(receipt_path.read_bytes())
    if (receipt.get("status") != "local-candidates-complete" or receipt.get("manifest_sha256") != digest(raw)
            or receipt.get("publication_performed") is not False or manifest.get("publication_performed") is not False
            or receipt.get("approval_pending") is not True or manifest.get("approval_pending") is not True
            or manifest.get("purpose") != "local-unapproved-dialogue-candidates"):
        raise ValueError("local_pack_receipt_invalid")
    files = manifest.get("files")
    records = manifest.get("records")
    if not isinstance(files, dict) or not isinstance(records, list):
        raise ValueError("local_pack_manifest_invalid")
    identities, paths, cues = set(), set(), 0
    for row in records:
        identity = row.get("video_id")
        if not isinstance(identity, str) or not re.fullmatch(r"[A-Za-z0-9_-]{11}", identity) or identity in identities:
            raise ValueError("local_pack_identity_invalid")
        identities.add(identity)
        if row.get("status") == "held":
            continue
        relative = f"raw/youtube-{identity}.json"
        if row.get("status") != "prepared" or row.get("path") != relative or relative not in files:
            raise ValueError("local_pack_path_invalid")
        path = safe(pack / relative, ROOT, Path(".source-cache"), file=True)
        body = path.read_bytes()
        if files[relative] != {"sha256": digest(body), "bytes": len(body)}:
            raise ValueError("local_pack_file_changed")
        data = json.loads(body)
        if data.get("video_id") != identity or data.get("id") != f"youtube-{identity}":
            raise ValueError("local_pack_source_identity_invalid")
        if len(data.get("units", [])) != row.get("cue_count"):
            raise ValueError("local_pack_cue_count_invalid")
        paths.add(relative)
        cues += row["cue_count"]
    if (set(files) != paths or manifest.get("candidate_count") != len(identities)
            or manifest.get("prepared_count") != len(paths)
            or manifest.get("held_count") != len(identities) - len(paths)
            or manifest.get("cue_count") != cues):
        raise ValueError("local_pack_coverage_invalid")
    if verify_inputs:
        archive = Path(manifest["archive_root"])
        if not archive.is_absolute() or archive.name != "kedaibiao-channel":
            raise ValueError("local_pack_archive_owner_invalid")
        for name, expected in manifest["input_guards"].items():
            path = Path(name)
            owner = ROOT if path.is_relative_to(ROOT) else archive
            safe(path, owner, file=True)
            raw = path.read_bytes()
            if expected != {"sha256": digest(raw), "bytes": len(raw)}:
                raise ValueError("local_pack_input_changed")
    return manifest


def load_candidates(pack: Path, manifest: dict):
    documents = []
    previous = search.ROOT
    search.ROOT = pack.absolute()
    try:
        for relative in sorted(manifest["files"]):
            documents.extend(search.parse_raw_dialogue(pack / relative))
    finally:
        search.ROOT = previous
    return documents


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("query", nargs="?")
    parser.add_argument("--top", type=int, default=8)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    try:
        manifest = verify_pack(args.pack)
        if args.verify_only:
            print(json.dumps({"status": "local-pack-verified", "candidate_count": manifest["candidate_count"],
                              "prepared_count": manifest["prepared_count"], "held_count": manifest["held_count"],
                              "cue_count": manifest["cue_count"], "publication_performed": False,
                              "speaker_attribution": "unresolved; candidate export does not infer identities"}, ensure_ascii=False))
        elif args.query:
            print(json.dumps({"scope": "local-unapproved-candidates", "publication_performed": False,
                "quality_notice": "AI text correction and review do not certify audio accuracy or speaker identity.",
                "results": search.search_documents(load_candidates(args.pack, manifest), args.query, args.top)}, ensure_ascii=False, indent=2))
        else:
            parser.error("query or --verify-only is required")
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        print(json.dumps({"status": "rejected", "reason": "local-pack-verification-failed"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
