#!/usr/bin/env python3
"""Build local, unapproved raw dialogue candidates from verified root copies.

This tool performs no attribution, model call, publication, or source replacement.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VIDEO_ID = re.compile(r"[A-Za-z0-9_-]{11}\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_bytes(value) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def safe(path: Path, owner: Path, area: Path | None = None, *, file=False) -> Path:
    """Reject lexical escapes and symlink components, including missing outputs."""
    owner = owner.absolute()
    path = path if path.is_absolute() else owner / path
    if ".." in path.parts or not path.is_relative_to(owner):
        raise ValueError("path_outside_owner")
    for component in (path, *path.parents):
        if component.is_symlink():
            raise ValueError("symlink_not_allowed")
    if area is not None and not path.is_relative_to(owner / area):
        raise ValueError("path_outside_allowed_area")
    if file and not path.is_file():
        raise ValueError("regular_file_required")
    return path


class Guards:
    def __init__(self):
        self.files: dict[str, dict] = {}

    def add(self, path: Path, owner: Path, expected: str | None = None,
            area: Path | None = None) -> bytes:
        path = safe(path, owner, area, file=True)
        raw = path.read_bytes()
        actual = digest(raw)
        if expected is not None and (not SHA256.fullmatch(expected) or actual != expected):
            raise ValueError("input_hash_mismatch")
        row = {"sha256": actual, "bytes": len(raw)}
        if str(path) in self.files and self.files[str(path)] != row:
            raise ValueError("input_changed_during_scan")
        self.files[str(path)] = row
        return raw

    def verify(self):
        for name, expected in self.files.items():
            path = Path(name)
            safe(path, path.anchor and Path(path.anchor), file=True)
            raw = path.read_bytes()
            if {"sha256": digest(raw), "bytes": len(raw)} != expected:
                raise ValueError("input_changed_during_scan")


def load_evidence(archive_root: Path, duplicate_ids: set[str]):
    """Call the existing complete rebuild/AI-chunk/amendment proof unchanged."""
    path = safe(archive_root / "tools/check/root_subtitle_review_evidence.py", archive_root, file=True)
    spec = importlib.util.spec_from_file_location("dialogue_candidate_root_evidence", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    records, rejected = module.verified_root_copies(archive_root)
    engine = module.finalizer()
    wrapper = sys.modules[engine.already_reviewed.__module__]
    aliases = wrapper.verified_aliases(archive_root, duplicate_ids) if duplicate_ids else {}
    return records, rejected, aliases, engine.source_cues


def root_inventory(root: Path) -> list[str]:
    area = safe(root / "logs/subtitle_text_review/root_reviews", root)
    # Includes immutable amendment receipts; never searches arbitrary ancestors.
    return sorted(str(safe(path, root)) for path in area.rglob("review.json")) if area.exists() else []


def unique(rows: list[dict], key: str) -> dict[str, dict]:
    result = {}
    for row in rows:
        identity = row.get(key)
        if not isinstance(identity, str) or not VIDEO_ID.fullmatch(identity) or identity in result:
            raise ValueError("invalid_or_duplicate_video_id")
        result[identity] = row
    return result


def authorization_records(data: dict, key: str) -> dict[str, dict]:
    rows = data.get(key)
    if not isinstance(rows, list):
        raise ValueError("authorization_snapshot_invalid")
    return unique(rows, "video_id")


def current_sources(rows: list[dict], aliases: dict, candidates: set[str]) -> dict[str, dict]:
    grouped = {}
    for row in rows:
        if row.get("video_id") in candidates:
            grouped.setdefault(row["video_id"], []).append(row)
    result = {}
    for identity, physical in grouped.items():
        if len(physical) > 1:
            alias = aliases.get(identity)
            if (not alias or {row.get("folder") for row in physical}
                    != {row["folder"] for row in alias["variants"]}):
                raise ValueError("quality_identity_conflict")
            result[identity] = {"selected_path": alias["selected_source"],
                                "selected_sha256": alias["selected_source_sha256"],
                                "physical_records": physical, "alias_evidence": alias}
        else:
            row = physical[0]
            if not row.get("selected_path") or row.get("status") in {"missing", "invalid"}:
                member = row.get("member_archive_audit")
                if isinstance(member, dict) and member.get("video_id") == identity and member.get("status") in {"machine_checks_passed", "warning"}:
                    row = member
            result[identity] = {**row, "physical_records": physical}
    return result


def bind_root(record: dict, root: Path, guards: Guards) -> dict:
    """Keep source, root leaf, parent chain, and exact AI receipt hash references."""
    for path_key, hash_key, area in (("source", "source_sha256", "archive"),
                                     ("output", "output_sha256", "logs/subtitle_text_review/root_reviews"),
                                     ("receipt", "receipt_sha256", "logs/subtitle_text_review/root_reviews")):
        guards.add(root / record[path_key], root, record[hash_key], Path(area))
    if record.get("base_receipt"):
        guards.add(root / record["base_receipt"], root, record["base_receipt_sha256"], Path("logs/subtitle_text_review/root_reviews"))
    for parent in record.get("amendment_parent_chain", []):
        for path_key, hash_key in (("review", "review_sha256"), ("output", "output_sha256")):
            guards.add(root / parent[path_key], root, parent[hash_key], Path("logs/subtitle_text_review/root_reviews"))
    # AI provenance is on the unchanged base receipt even for amended leaves.
    base = json.loads(guards.add(root / record.get("base_receipt", record["receipt"]), root,
                                  record.get("base_receipt_sha256", record["receipt_sha256"])))
    for path_key, hash_key in (("ai_receipt", "ai_receipt_sha256"), ("ai_output", "ai_output_sha256")):
        guards.add(root / base[path_key], root, base[hash_key], Path("logs/subtitle_text_review"))
    ai = json.loads(guards.add(root / base["ai_receipt"], root, base["ai_receipt_sha256"]))
    if (ai.get("status") != "text-reviewed" or ai.get("review") != "ai-text-review"
            or ai.get("full_source_text_reviewed") is not True or ai.get("timing_count_verified") is not True):
        raise ValueError("ai_receipt_status_unverified")
    for chunk in ai["chunks"]:
        chunk_output = safe(root / chunk["output"], root, Path("logs/subtitle_text_review/staging"), file=True)
        guards.add(chunk_output, root, chunk["output_sha256"])
        chunk_dir = root / "logs/subtitle_text_review/staging" / record["video_id"] / record["source_sha256"] / "chunks" / f"{chunk['description']['index']:04d}"
        guards.add(chunk_dir / "receipt.json", root)
        # Existing verifier proves the exact receipt equality and cue coverage.
        guards.add(chunk_output.with_name(f"{record['video_id']}.qwen.srt"), root, chunk["input_sha256"])
        guards.add(chunk_dir / f"{record['video_id']}.qwen.srt", root, chunk["input_sha256"])
        rejection = chunk["safety_rejections"]
        guards.add(root / rejection["path"], root, rejection["sha256"], Path("logs/subtitle_text_review/staging"))
    return {"ai_receipt": base["ai_receipt"], "ai_receipt_sha256": base["ai_receipt_sha256"],
            "ai_output": base["ai_output"], "ai_output_sha256": base["ai_output_sha256"],
            "ai_review_status": ai["status"], "ai_review": ai["review"],
            "ai_chunk_count": len(ai["chunks"]), "ai_timing_count_verified": True,
            "ai_safety_rejection_count": sum(chunk["safety_rejections"]["count"] for chunk in ai["chunks"]),
            "full_source_ai_processing_verified": base.get("full_source_ai_processing_verified") is True}


def author_metadata(record: dict, root: Path, guards: Guards) -> dict:
    """Fill catalog gaps only from the original ID-bound adjacent info file."""
    source = safe(root / record["source"], root, Path("archive"), file=True)
    folder = source.parent.parent if source.parent.name.endswith("_process") else source.parent
    matched = []
    for path in sorted(folder.glob("*.info.json")):
        data = json.loads(guards.add(path, root, area=Path("archive")))
        if data.get("id") == record["video_id"]:
            matched.append((path, data))
    if len(matched) != 1:
        raise ValueError("author_metadata_identity_missing_or_conflicting")
    path, data = matched[0]
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("author_metadata_title_missing")
    timestamp = data.get("timestamp")
    published = None
    if type(timestamp) in {int, float} and timestamp > 0:
        published = datetime.fromtimestamp(timestamp, timezone.utc).isoformat()
    elif isinstance(data.get("upload_date"), str) and re.fullmatch(r"\d{8}", data["upload_date"]):
        date = data["upload_date"]
        published = datetime.strptime(date, "%Y%m%d").date().isoformat()
    return {"title": title, "published_at": published,
            "metadata_source": str(path.relative_to(root)),
            "metadata_source_sha256": guards.files[str(path)]["sha256"]}


def build_candidates(archive_root: Path, inventory_path: Path, output: Path, *, apply=False,
                     owner: Path = ROOT) -> dict:
    owner = safe(owner.absolute(), owner.absolute())
    archive_root = safe(archive_root.absolute(), archive_root.absolute())
    output = safe(output, owner, Path(".source-cache"))
    if output == owner / ".source-cache" or output.exists():
        raise ValueError("output_must_be_new_exclusive_directory")
    guards = Guards()
    inventory = json.loads(guards.add(inventory_path, owner, area=Path(".source-cache")))
    if inventory.get("schema_version") != 1 or not isinstance(inventory.get("records"), list):
        raise ValueError("inventory_schema_invalid")
    candidates = unique(inventory["records"], "video_id")
    if inventory.get("summary", {}).get("candidate_union") != len(candidates):
        raise ValueError("inventory_count_mismatch")
    paths = {"catalog_videos": owner / "catalog/videos.jsonl", "podcast_series": archive_root / "podcast_series.json",
             "subtitle_quality": archive_root / "logs/subtitle_quality/subtitle_quality.json"}
    if set(inventory.get("inputs", {})) != set(paths):
        raise ValueError("inventory_input_mapping_invalid")
    inputs = {key: guards.add(path, owner if key == "catalog_videos" else archive_root, inventory["inputs"][key])
              for key, path in paths.items()}
    catalog = unique([json.loads(line) for line in inputs["catalog_videos"].splitlines() if line.strip()], "video_id")
    quality = json.loads(inputs["subtitle_quality"])
    series = json.loads(inputs["podcast_series"])
    if not isinstance(quality.get("records"), list):
        raise ValueError("quality_schema_invalid")
    policy_paths = {"member": owner / "config/member-video-policy.json", "public": owner / "config/values-conversations-policy.json"}
    policies = {key: json.loads(guards.add(path, owner)) for key, path in policy_paths.items()}
    member = authorization_records(policies["member"], "records")
    public = authorization_records(policies["public"], "public_transcripts")
    duplicate_ids = {identity for identity, count in Counter(row.get("video_id") for row in quality["records"]).items() if count > 1 and identity in candidates}
    before_roots = root_inventory(archive_root)
    roots, rejected, aliases, parse_cues = load_evidence(archive_root, duplicate_ids)
    if rejected:
        raise ValueError("root_evidence_rejected")
    for alias in aliases.values():
        guards.add(archive_root / alias["evidence_path"], archive_root, alias["evidence_sha256"], Path("logs/subtitle_quality"))
        for variant in alias["variants"]:
            for key in ("info", "media"):
                guards.add(archive_root / variant[f"{key}_path"], archive_root, variant[f"{key}_sha256"], Path("archive"))
    current = current_sources(quality["records"], aliases, set(candidates))
    seen, roots_by_pair = set(), {}
    for record in roots:
        pair = (record["video_id"], record["source_sha256"])
        if pair in seen:
            raise ValueError("root_identity_conflict")
        seen.add(pair)
        roots_by_pair[pair] = record
        bind_root(record, archive_root, guards)
    # Pin the actually loaded local proof implementation as well as this tool.
    guards.add(Path(__file__), ROOT)
    for module in tuple(sys.modules.values()):
        path = getattr(module, "__file__", None)
        if path and Path(path).suffix == ".py" and Path(path).absolute().is_relative_to(archive_root / "tools"):
            guards.add(Path(path).absolute(), archive_root, area=Path("tools"))
    documents, statuses = {}, []
    for identity, row in candidates.items():
        selected = current.get(identity, {})
        record = roots_by_pair.get((identity, selected.get("selected_sha256")))
        if not selected.get("selected_path"):
            statuses.append({"video_id": identity, "status": "held", "reason": "current_source_missing"})
            continue
        guards.add(archive_root / selected["selected_path"], archive_root, selected["selected_sha256"], Path("archive"))
        if not record:
            statuses.append({"video_id": identity, "status": "held", "reason": "current_root_copy_missing",
                             "source": selected["selected_path"], "source_sha256": selected["selected_sha256"]})
            continue
        if record["source"] != selected["selected_path"]:
            raise ValueError("root_selected_source_path_mismatch")
        if record.get("human_audio_review_verified") is not False or record.get("full_precision_certified") is not False:
            raise ValueError("root_quality_flags_unexpected")
        if type(record.get("unresolved_count")) is not int or record["unresolved_count"] < 0:
            raise ValueError("root_unresolved_count_invalid")
        provenance = bind_root(record, archive_root, guards)
        if not provenance["full_source_ai_processing_verified"]:
            raise ValueError("ai_processing_proof_missing")
        raw = guards.add(archive_root / record["output"], archive_root, record["output_sha256"])
        cues = parse_cues(raw, ".srt")
        if not cues:
            raise ValueError("empty_verified_root_copy")
        units = [{"id": f"youtube-{identity}#cue-{index}", "start_seconds": cue.start_ms / 1000,
                  "end_seconds": cue.end_ms / 1000, "text": cue.text, "speaker_id": "unknown",
                  "speaker_name": "", "speaker_status": "unresolved"} for index, cue in enumerate(cues, 1)]
        metadata = dict(catalog.get(identity, row))
        if metadata.get("title") is None or metadata.get("title") == "":
            metadata.update(author_metadata(record, archive_root, guards))
        if not isinstance(metadata.get("title", ""), str):
            raise ValueError("title_metadata_type_invalid")
        authorized = [{"snapshot": name, "policy_path": str(policy_paths[name].relative_to(owner)),
                       "policy_sha256": guards.files[str(policy_paths[name])]["sha256"],
                       "transcript_sha256": mapping[identity].get("transcript_sha256"),
                       "exact_root_output_matches_snapshot": mapping[identity].get("transcript_sha256") == record["output_sha256"]}
                      for name, mapping in (("member", member), ("public", public)) if identity in mapping]
        data = {"schema_version": 1, "data_layer": "raw", "id": f"youtube-{identity}", "video_id": identity,
                "title": metadata.get("title", ""), "source_url": f"https://www.youtube.com/watch?v={identity}",
                "published_at": metadata.get("published_at"), "source_date_in_podcast_series": series.get("episodes", {}).get(identity, {}).get("source_date"),
                "source_type": "video-transcript", "metadata_source": metadata.get("metadata_source"),
                "metadata_source_sha256": metadata.get("metadata_source_sha256"),
                "speaker_classification": "mixed-or-unresolved", "content_origin": "mixed-or-unresolved-speech",
                "evidence_role": "speaker-attributed-speech", "yuzheng_stance_weight": "not-evidence", "units": units,
                "quality": {**record, **provenance, "human_audio_review": False, "full_precision": False,
                            "complete_speech_coverage_verified": False},
                "visibility_snapshot": {"catalog": row.get("source_visibility_in_catalog"),
                    "archive": row.get("archive_privacy_snapshot"), "archive_snapshot_at": row.get("archive_privacy_snapshot_at"),
                    "quality_physical_records": [{key: item.get(key) for key in ("folder", "youtube_privacy", "content_class", "selected_path", "selected_sha256")}
                                                 for item in selected["physical_records"]]},
                "existing_exact_authorization_snapshots": authorized, "new_candidate_approval_required": True,
                "publication_performed": False, "approval_pending": True}
        name = f"raw/youtube-{identity}.json"
        documents[name] = json_bytes(data)
        statuses.append({"video_id": identity, "status": "prepared", "path": name, "cue_count": len(units),
                         "source_sha256": record["source_sha256"], "root_output_sha256": record["output_sha256"],
                         "existing_authorization_snapshots": [item["snapshot"] for item in authorized]})
    # Re-run the complete guard, not just a stale directory listing or mtime.
    end_roots, end_rejections, end_aliases, _ = load_evidence(archive_root, duplicate_ids)
    if (end_rejections or end_roots != roots or end_aliases != aliases
            or root_inventory(archive_root) != before_roots):
        raise ValueError("root_inventory_changed_during_scan")
    guards.verify()
    manifest = {"schema_version": 1, "purpose": "local-unapproved-dialogue-candidates", "data_layer": "raw",
                "generated_at": datetime.now(timezone.utc).isoformat(), "publication_performed": False, "approval_pending": True,
                "archive_root": str(archive_root), "inventory": str(inventory_path), "inventory_sha256": guards.files[str(inventory_path)]["sha256"],
                "input_guards": guards.files, "tool_sha256": digest(Path(__file__).read_bytes()),
                "authorization_snapshot_counts": {"member": len(member), "public": len(public)},
                "candidate_count": len(candidates), "prepared_count": len(documents),
                "held_count": sum(row["status"] == "held" for row in statuses),
                "cue_count": sum(row.get("cue_count", 0) for row in statuses), "root_evidence_rejections": {},
                "verified_aliases": aliases,
                "records": statuses, "files": {name: {"sha256": digest(data), "bytes": len(data)} for name, data in documents.items()}}
    if apply:
        safe(output, owner, Path(".source-cache"))
        output.parent.mkdir(parents=True, exist_ok=True)
        output.mkdir(exist_ok=False)
        (output / "raw").mkdir()
        for name, data in documents.items():
            with safe(output / name, owner, Path(".source-cache")).open("xb") as handle:
                handle.write(data)
        guards.verify()
        if root_inventory(archive_root) != before_roots:
            raise ValueError("root_inventory_changed_during_scan")
        with (output / "manifest.json").open("xb") as handle:
            handle.write(json_bytes(manifest))
        receipt = {"schema_version": 1, "status": "local-candidates-complete", "manifest_sha256": digest(json_bytes(manifest)),
                   "publication_performed": False, "approval_pending": True, "input_drift_count": 0,
                   "verified_at": datetime.now(timezone.utc).isoformat()}
        with (output / "receipt.json").open("xb") as handle:
            handle.write(json_bytes(receipt))
    return {"dry_run": not apply, "output": str(output), "candidate_count": manifest["candidate_count"],
            "prepared_count": manifest["prepared_count"], "held_count": manifest["held_count"], "cue_count": manifest["cue_count"]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive-root", type=Path, required=True)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="Write only a new local .source-cache directory.")
    args = parser.parse_args()
    try:
        print(json.dumps(build_candidates(args.archive_root, args.inventory.absolute(), args.output, apply=args.apply), ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, json.JSONDecodeError) as error:
        code = str(error) if type(error) is ValueError and re.fullmatch(r"[a-z_]+", str(error)) else "unsafe_or_invalid_inputs"
        print(json.dumps({"status": "rejected", "error": code}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
