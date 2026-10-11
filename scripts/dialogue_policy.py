"""Exact public dialogue admission, separate from local candidate preparation."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

import search
from raw_turn_policy import reviewed_policy, validate_units
from rights import REFERENCE_USE

AUTHORIZATION = "maintainer-request-2026-10-10-dialogue-transcripts"
CHANNEL = "UC_5lJHgnMP_lb_VpIiXV0hQ"
HASH = re.compile(r"[0-9a-f]{64}\Z")
VIDEO_ID = re.compile(r"[A-Za-z0-9_-]{11}\Z")
PROVENANCE = {
    "data_layer": "raw", "source_type": "video-transcript",
    "speaker_classification": "mixed-or-unresolved", "content_origin": "mixed-or-unresolved-speech",
    "generation_method": "transcription-with-ai-text-review", "evidence_role": "speaker-attributed-speech",
    "yuzheng_stance_weight": "not-evidence", "rights_scope": "publisher-authorized-transcript",
    "license": REFERENCE_USE, "source_visibility": "public", "text_access": "public",
    "publisher": "Yuzheng Sun", "author": "说话人待核", "original_author": "说话人待核",
    "inclusion_authorization": AUTHORIZATION,
    "transcript_quality": "ai-text-reviewed", "transcript_source_kind": "faithful-text-review-copy",
}


def read_object(path: Path):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_json_key")
            result[key] = value
        return result
    value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs)
    if not isinstance(value, dict):
        raise ValueError("expected_json_object")
    return value


def validate_dialogues(root: Path, member_ids: set[str], errors: list[str]) -> dict:
    policy_path = root / "config/public-dialogue-policy.json"
    folder = root / "corpus/dialogues"
    actual = {path.relative_to(root).as_posix() for path in folder.glob("*.json")} if folder.exists() else set()
    if not policy_path.exists():
        if actual:
            errors.append("Structured dialogue files lack an exact public admission policy")
        return {"structured_public_dialogues": 0, "structured_dialogue_cues": 0}
    admitted, count = set(), 0
    try:
        policy = read_object(policy_path)
        if (policy.get("schema_version") != 1 or policy.get("authorization") != AUTHORIZATION
                or policy.get("scope") != "public-dialogues-only" or not policy.get("removal")
                or policy.get("rights_notice") != "Guests retain rights in their own speech; inclusion does not establish Yuzheng's endorsement."):
            raise ValueError("invalid_public_dialogue_policy")
        rows = policy.get("records")
        if not isinstance(rows, list):
            raise ValueError("invalid_public_dialogue_records")
        turns = reviewed_policy(root, policy, read_object)
        identities = set()
        for row in rows:
            identity = row.get("video_id")
            if not isinstance(identity, str) or not VIDEO_ID.fullmatch(identity) or identity in identities or identity in member_ids:
                raise ValueError("invalid_duplicate_or_protected_dialogue_id")
            identities.add(identity)
            relative = f"corpus/dialogues/youtube-{identity}.json"
            if row.get("corpus_path") != relative or not HASH.fullmatch(str(row.get("sha256", ""))):
                raise ValueError("invalid_dialogue_file_binding")
            admitted.add(relative)
            path = root / relative
            if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()) or not path.is_file():
                raise ValueError("unsafe_dialogue_source_path")
            raw = path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != row["sha256"]:
                raise ValueError("dialogue_snapshot_hash_mismatch")
            data = read_object(path)
            if data.get("id") != f"youtube-{identity}" or data.get("video_id") != identity or data.get("schema_version") != 1:
                raise ValueError("dialogue_identity_mismatch")
            if any(data.get(key) != value for key, value in PROVENANCE.items()):
                raise ValueError("dialogue_provenance_or_access_mismatch")
            if (data.get("source_url") != f"https://www.youtube.com/watch?v={identity}"
                    or data.get("source_family") != data["source_url"]
                    or not isinstance(data.get("title"), str) or not data["title"].strip()
                    or not data.get("attribution_note") or data.get("language") not in {"zh", "en", "mixed"}
                    or not isinstance(data.get("participant_names", ""), str)):
                raise ValueError("dialogue_source_metadata_missing")
            identity_fields = {"participant_entity_ids", "participant_aliases", "participant_metadata_basis"}
            if identity_fields & data.keys():
                ids, aliases, basis = (data.get(key) for key in (
                    "participant_entity_ids", "participant_aliases", "participant_metadata_basis"))
                if (not isinstance(ids, list) or len(ids) > 64
                        or any(not isinstance(eid, str) or not re.fullmatch(r"[a-z][a-z0-9_.:-]{0,127}", eid) for eid in ids)
                        or len(ids) != len(set(ids))
                        or not isinstance(aliases, list) or len(aliases) > 128
                        or any(not isinstance(alias, str) or not alias.strip() or len(alias) > 100
                               or any(ord(c) < 32 for c in alias) or "/Users/" in alias for alias in aliases)
                        or not isinstance(basis, str) or not basis.strip() or len(basis) > 1000):
                    raise ValueError("dialogue_participant_identity_metadata_invalid")
            datetime.fromisoformat(data["published_at"].replace("Z", "+00:00"))
            evidence = row.get("anonymous_evidence", {})
            if (evidence.get("video_id") != identity or evidence.get("channel_id") != CHANNEL
                    or evidence.get("availability") != "public" or evidence.get("is_live") is not False
                    or evidence.get("is_upcoming") is not False
                    or not HASH.fullmatch(str(evidence.get("receipt_sha256", "")))):
                raise ValueError("dialogue_public_identity_not_verified")
            datetime.fromisoformat(evidence["verified_at"].replace("Z", "+00:00"))
            if data.get("public_verified_at") != evidence["verified_at"]:
                raise ValueError("dialogue_public_snapshot_date_mismatch")
            quality = data.get("quality", {})
            if (quality.get("ai_text_processing_verified") is not True or quality.get("root_edit_review_verified") is not True
                    or quality.get("human_audio_review") is not False or quality.get("full_precision_certified") is not False
                    or quality.get("complete_speech_coverage_verified") is not False
                    or type(quality.get("unresolved_count")) is not int or quality["unresolved_count"] < 0
                    or any(not HASH.fullmatch(str(quality.get(key, ""))) for key in ("original_source_sha256", "root_output_sha256", "root_receipt_sha256"))):
                raise ValueError("dialogue_quality_overclaim_or_missing_proof")
            validate_units(data, turns.get(identity))
            previous = search.ROOT
            search.ROOT = root
            try:
                search.parse_raw_dialogue(path)
            finally:
                search.ROOT = previous
            if row.get("cue_count") != len(data["units"]):
                raise ValueError("dialogue_cue_count_mismatch")
            count += len(data["units"])
        if admitted != actual:
            raise ValueError("dialogue_policy_files_exact_set_mismatch")
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as error:
        code = str(error) if type(error) is ValueError and re.fullmatch(r"[a-z_]+", str(error)) else "invalid_public_dialogue_inputs"
        errors.append(f"Public dialogue admission rejected: {code}")
    return {"structured_public_dialogues": len(admitted), "structured_dialogue_cues": count}
