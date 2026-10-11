#!/usr/bin/env python3
"""Prepare an exact LOCAL public-dialogue proposal; never publish or overwrite it."""
from __future__ import annotations

import argparse
import json
import math
import re
from datetime import datetime, timezone
from pathlib import Path

from build_dialogue_candidates import ROOT, digest, safe
from dialogue_policy import AUTHORIZATION, CHANNEL, HASH, PROVENANCE, read_object
from search_dialogue_candidates import verify_pack


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode()


def checked(path, guards, *, expected=None):
    path = safe(Path(path).absolute(), ROOT, Path(".source-cache"), file=True)
    raw = path.read_bytes()
    actual = {"sha256": digest(raw), "bytes": len(raw)}
    if expected is not None and actual != expected:
        raise ValueError("observation_reference_changed")
    guards[str(path)] = actual
    return read_object(path)


def observations(reports, inventory_ids, guards):
    result = {}
    for path in reports:
        report = checked(path, guards)
        if (report.get("publication_performed") is not False or report.get("approval_pending") is not True
                or report.get("expected_channel_id") != CHANNEL or report.get("input_drift_count") != 0
                or report.get("remote_writes") not in (0, False)):
            raise ValueError("observation_report_not_safe")
        requested = report["requested_video_ids"]
        rows = report["records"]
        if (len(set(requested)) != len(requested) or len(rows) != len(requested)
                or {row["video_id"] for row in rows} != set(requested) or not set(requested) <= inventory_ids):
            raise ValueError("observation_identity_coverage_mismatch")
        for name, reference in report["references"].items():
            target = safe(Path(name).absolute(), ROOT, Path(".source-cache"), file=True)
            raw = target.read_bytes()
            if reference != {"sha256": digest(raw), "bytes": len(raw)}:
                raise ValueError("observation_reference_changed")
            guards[str(target)] = reference
        for row in rows:
            identity = row["video_id"]
            if identity in result:
                raise ValueError("duplicate_observation_identity")
            actual = checked(row["observation_path"], guards)
            if guards[row["observation_path"]]["sha256"] != row["observation_sha256"]:
                raise ValueError("observation_record_changed")
            for key in ("video_id", "status", "metadata", "public_author_metadata", "guard_failures"):
                left, right = actual.get(key), row.get(key)
                if key == "metadata" and row.get("status") == "pending":
                    left, right = left or {}, right or {}
                if left != right:
                    raise ValueError("consolidated_observation_differs")
            if row["status"] == "public_verified":
                meta = row["metadata"]
                if (row.get("identity_verified") is not True or row.get("guard_failures")
                        or meta.get("id") != identity or meta.get("channel_id") != CHANNEL
                        or meta.get("availability") != "public" or meta.get("is_live") is not False
                        or meta.get("live_status") != "not_live" or meta.get("age_limit") != 0):
                    raise ValueError("public_observation_identity_unsafe")
                author = row["public_author_metadata"]
                if not isinstance(author.get("title"), str) or not author["title"].strip():
                    raise ValueError("public_author_title_missing")
                datetime.strptime(author["upload_date"], "%Y%m%d")
                datetime.fromisoformat(row["observation_finished_at"].replace("Z", "+00:00"))
            elif row["status"] != "pending":
                raise ValueError("unsupported_observation_status")
            result[identity] = row
    return result


def prepare(pack, reports, exclusions=None):
    pack = Path(pack).absolute()
    manifest = verify_pack(pack)
    guards = dict(manifest["input_guards"])
    guards[str(Path(__file__).resolve())] = {"sha256": digest(Path(__file__).read_bytes()), "bytes": Path(__file__).stat().st_size}
    for name in ("manifest.json", "receipt.json"):
        checked(pack / name, guards)
    inventory = checked(manifest["inventory"], guards)
    if guards[manifest["inventory"]]["sha256"] != manifest["inventory_sha256"]:
        raise ValueError("inventory_changed")
    candidates = {row["video_id"]: row for row in inventory["records"]}
    observed = observations(reports, set(candidates), guards)
    member_path = ROOT / "config/member-video-policy.json"
    member_raw = member_path.read_bytes()
    guards[str(member_path)] = {"sha256": digest(member_raw), "bytes": len(member_raw)}
    protected = {row["video_id"] for row in json.loads(member_raw)["records"]}
    exclusions = exclusions or {}
    if not set(exclusions) <= set(candidates) or any(not isinstance(reason, str) or not reason.strip() for reason in exclusions.values()):
        raise ValueError("invalid_explicit_exclusions")
    files, policy_rows, decisions = {}, [], []
    cue_count = 0
    for identity, candidate in sorted(candidates.items()):
        observation = observed.get(identity)
        reason = ("protected-existing-member-snapshot" if identity in protected else exclusions.get(identity)
                  or ("anonymous-visibility-not-verified" if observation and observation["status"] == "pending"
                      else "not-anonymously-observed" if observation is None else ""))
        if reason:
            decisions.append({"video_id": identity, "title": candidate.get("title"), "status": "local-only", "reason": reason})
            continue
        source_path = pack / f"raw/youtube-{identity}.json"
        source = checked(source_path, guards)
        quality = source["quality"]
        if (quality.get("status") not in {"root-reviewed-ai-edits", "root-reviewed-amendment"} or quality.get("full_source_ai_processing_verified") is not True
                or quality.get("human_audio_review") is not False or quality.get("full_precision_certified") is not False
                or type(quality.get("full_original_source_read")) is not bool
                or type(quality.get("unresolved_count")) is not int or quality["unresolved_count"] < 0
                or any(not HASH.fullmatch(str(quality.get(key, ""))) for key in ("source_sha256", "output_sha256", "receipt_sha256"))):
            raise ValueError("candidate_quality_not_verified")
        if not source.get("units") or any(unit.get("speaker_id") != "unknown" or unit.get("speaker_name", "") != ""
                                         or unit.get("speaker_status") != "unresolved" for unit in source["units"]):
            raise ValueError("candidate_named_speaker_needs_separate_review")
        seen = set()
        fields = {"id", "start_seconds", "end_seconds", "text", "speaker_id", "speaker_name", "speaker_status"}
        for unit in source["units"]:
            if (set(unit) != fields or not isinstance(unit["id"], str) or not unit["id"] or unit["id"] in seen
                    or not isinstance(unit["text"], str) or not unit["text"].strip()
                    or any(type(unit[key]) not in (int, float) or not math.isfinite(unit[key]) for key in ("start_seconds", "end_seconds"))
                    or not 0 <= unit["start_seconds"] < unit["end_seconds"]):
                raise ValueError("candidate_raw_unit_invalid")
            seen.add(unit["id"])
        source_path = safe(Path(manifest["archive_root"]) / quality["source"], Path(manifest["archive_root"]), file=True)
        if not any(binding["video_id"] == identity and binding["source_sha256"] == quality["source_sha256"]
                   and binding["source"] == str(source_path)
                   for binding in observation["source_bindings"]):
            raise ValueError("anonymous_source_binding_mismatch")
        author = observation["public_author_metadata"]
        duration = observation["metadata"].get("duration")
        if type(duration) not in (int, float) or not math.isfinite(duration) or duration <= 0:
            raise ValueError("public_media_duration_not_verified")
        if max(unit["end_seconds"] for unit in source["units"]) > duration + 3:
            decisions.append({"video_id": identity, "title": candidate.get("title"), "status": "local-only",
                              "reason": "subtitle-timing-exceeds-current-public-video; source version needs review"})
            continue
        date = datetime.strptime(author["upload_date"], "%Y%m%d").date().isoformat()
        url = f"https://www.youtube.com/watch?v={identity}"
        data = {**PROVENANCE, "schema_version": 1, "id": f"youtube-{identity}", "video_id": identity,
            "title": author["title"], "published_at": date, "original_published_at": source["published_at"],
            "language": "mixed", "source_url": url, "source_family": url,
            "transcript_quality": "ai-text-reviewed", "transcript_source_kind": "faithful-text-review-copy",
            "participant_names": "；".join(candidate.get("guest_names_from_catalog") or []),
            "participant_metadata_basis": "existing-author-catalog; names do not assign individual turns",
            "public_verified_at": observation["observation_finished_at"],
            "attribution_note": "本节目含多人或归属未决的发言。参与者名单仅供查找，不能据此指定任何一句的说话人；嘉宾发言不证明立正赞同。字幕经 AI 文字校对及实际改动复核，尚未逐句听校；待核片段须回到原视频。",
            "quality": {"ai_text_processing_verified": True, "root_edit_review_verified": True,
                "full_original_source_read": quality["full_original_source_read"], "human_audio_review": False,
                "full_precision_certified": False, "complete_speech_coverage_verified": False,
                "unresolved_count": quality["unresolved_count"], "original_source_sha256": quality["source_sha256"],
                "root_output_sha256": quality["output_sha256"], "root_receipt_sha256": quality["receipt_sha256"]},
            "units": source["units"]}
        relative = f"corpus/dialogues/youtube-{identity}.json"
        raw = encode(data)
        files[relative] = raw
        policy_rows.append({"video_id": identity, "corpus_path": relative, "sha256": digest(raw), "cue_count": len(data["units"]),
            "anonymous_evidence": {"video_id": identity, "channel_id": CHANNEL, "availability": "public",
                "is_live": False, "is_upcoming": False, "verified_at": data["public_verified_at"],
                "receipt_sha256": observation["observation_sha256"]}})
        cue_count += len(data["units"])
        decisions.append({"video_id": identity, "title": data["title"], "status": "proposed-public-raw",
                          "path": relative, "cue_count": len(data["units"]), "speakers": "unresolved"})
    policy = {"schema_version": 1, "authorization": AUTHORIZATION, "scope": "public-dialogues-only",
        "authorization_scope": "Maintainer requested dialogue retrieval on 2026-10-10. Publication approval is recorded separately for the exact reviewed release; guests retain their own rights.",
        "removal": "https://lizheng.ai/contact", "rights_notice": "Guests retain rights in their own speech; inclusion does not establish Yuzheng's endorsement.",
        "records": policy_rows}
    files["config/public-dialogue-policy.json"] = encode(policy)
    plan = {"schema_version": 1, "purpose": "exact-local-public-dialogue-proposal", "generated_at": datetime.now(timezone.utc).isoformat(),
        "publication_performed": False, "approval_pending": True,
        "destinations": ["sunyuzheng/lizheng-open-context main", "https://ask.lizheng.ai"], "audience": "public repository readers and Ask Lizheng users",
        "candidate_count": len(candidates), "observed_count": len(observed), "proposed_dialogues": len(policy_rows), "proposed_cues": cue_count,
        "speaker_attribution": "New structured dialogue units remain unresolved; existing reviewed own quotations stay separate.",
        "records": decisions, "input_guards": guards,
        "files": {name: {"sha256": digest(raw), "bytes": len(raw)} for name, raw in files.items()}}
    return files, plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pack", type=Path, required=True)
    parser.add_argument("--observations", type=Path, action="append", required=True)
    parser.add_argument("--exclusions", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    try:
        exclusions = read_object(args.exclusions) if args.exclusions else None
        files, plan = prepare(args.pack, args.observations, exclusions)
        if args.exclusions:
            checked(args.exclusions, plan["input_guards"])
        output = safe(args.output.absolute(), ROOT, Path(".source-cache"))
        if output.exists():
            raise ValueError("proposal_output_already_exists")
        if args.apply:
            # Recheck every pinned input immediately before the reversible local write.
            for name, expected in plan["input_guards"].items():
                raw = Path(name).read_bytes()
                if expected != {"sha256": digest(raw), "bytes": len(raw)}:
                    raise ValueError("proposal_input_changed")
            output.mkdir()
            for relative, raw in files.items():
                target = output / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("xb") as handle:
                    handle.write(raw)
            for name, expected in plan["input_guards"].items():
                path = Path(name)
                if any(item.is_symlink() for item in (path, *path.parents)) or not path.is_file():
                    raise ValueError("proposal_input_changed")
                raw = path.read_bytes()
                if expected != {"sha256": digest(raw), "bytes": len(raw)}:
                    raise ValueError("proposal_input_changed")
            for relative, expected in plan["files"].items():
                target = safe(output / relative, ROOT, Path(".source-cache"), file=True)
                raw = target.read_bytes()
                if expected != {"sha256": digest(raw), "bytes": len(raw)}:
                    raise ValueError("proposal_output_changed")
            raw_plan = encode(plan)
            (output / "plan.json").write_bytes(raw_plan)
            (output / "receipt.json").write_bytes(encode({"status": "local-public-proposal-complete", "publication_performed": False,
                "approval_pending": True, "plan_sha256": digest(raw_plan), "tool_sha256": digest(Path(__file__).read_bytes())}))
        print(json.dumps({key: plan[key] for key in ("candidate_count", "observed_count", "proposed_dialogues", "proposed_cues", "publication_performed", "approval_pending")} | {"mode": "local-apply" if args.apply else "dry-run"}))
        return 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        print(json.dumps({"status": "rejected", "reason": "public-proposal-input-verification-failed"}))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
