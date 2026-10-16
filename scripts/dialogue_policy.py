"""Exact public dialogue admission, separate from local candidate preparation."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

import search
from raw_turn_policy import reviewed_policy, validate_external_units, validate_units, voice_policy
from rights import REFERENCE_USE, RETAINED
from validate_guest_catalog import CATALOG_FIELDS, appearance_participants, programme_participants, safe_file, url, video_id

AUTHORIZATION = "maintainer-request-2026-10-10-dialogue-transcripts"
EXTERNAL_AUTHORIZATION = "maintainer-request-2026-10-15-guest-podcasts"
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


def validate_external_dialogue(root, row, participants, protected_ids=frozenset()):
    """An exact public external snapshot, without claiming the maintainer's YouTube channel."""
    identity = row.get("source_id")
    if (not isinstance(identity, str) or not re.fullmatch(r"dialogue-[a-z0-9][a-z0-9._-]*", identity)
            or "video_id" in row or row.get("corpus_path") != f"corpus/dialogues/{identity}.json"
            or not HASH.fullmatch(str(row.get("sha256", "")))):
        raise ValueError("invalid_external_dialogue_file_binding")
    path = safe_file(root, row["corpus_path"])
    if hashlib.sha256(path.read_bytes()).hexdigest() != row["sha256"]:
        raise ValueError("dialogue_snapshot_hash_mismatch")
    data = read_object(path)
    expected = {key: value for key, value in PROVENANCE.items()
                if key not in {"source_type", "publisher", "inclusion_authorization", "license", "rights_scope"}}
    if (type(data.get("schema_version")) is not int or data["schema_version"] != 1 or data.get("id") != identity
            or "video_id" in data or any(data.get(key) != value for key, value in expected.items())
            or data.get("source_type") not in {"video-transcript", "audio-transcript"}
            or data.get("inclusion_authorization") != EXTERNAL_AUTHORIZATION
            or not isinstance(data.get("publisher"), str) or not data["publisher"].strip()
            or (data.get("rights_scope"), data.get("license")) not in {
                ("publisher-authorized-transcript", REFERENCE_USE), ("third-party-reference", RETAINED)}
            or data.get("timestamp_mode") != "display-only"):
        raise ValueError("external_dialogue_provenance_or_identity_mismatch")
    url(row.get("source_url"))
    try:
        source_video_id = video_id(row["source_url"])
    except ValueError:
        source_video_id = None
    if source_video_id in protected_ids:
        raise ValueError("external_dialogue_cannot_bypass_youtube_policy")
    if (data.get("source_url") != row["source_url"] or data.get("source_family") != row["source_url"]
            or not isinstance(data.get("title"), str) or not data["title"].strip()
            or data.get("language") not in {"zh", "en", "mixed"}):
        raise ValueError("dialogue_source_metadata_missing")
    if CATALOG_FIELDS & data.keys():
        raise ValueError("dialogue_catalog_metadata_duplicated")
    datetime.fromisoformat(data["published_at"].replace("Z", "+00:00"))
    evidence = row.get("anonymous_evidence", {})
    if (evidence.get("source_url") != row["source_url"] or evidence.get("availability") != "public"
            or not HASH.fullmatch(str(evidence.get("receipt_sha256", "")))):
        raise ValueError("dialogue_public_identity_not_verified")
    datetime.fromisoformat(evidence["verified_at"].replace("Z", "+00:00"))
    if data.get("public_verified_at") != evidence["verified_at"]:
        raise ValueError("dialogue_public_snapshot_date_mismatch")
    validate_quality(data)
    previous = search.ROOT
    search.ROOT = root
    try:
        search.parse_raw_dialogue(path)
    finally:
        search.ROOT = previous
    validate_external_units(data, row.get("review_units", []), participants.get(identity, {}))
    if type(row.get("cue_count")) is not int or row["cue_count"] != len(data["units"]):
        raise ValueError("dialogue_cue_count_mismatch")
    return identity, row["corpus_path"], len(data["units"])


def validate_quality(data):
    quality = data.get("quality", {})
    if (quality.get("ai_text_processing_verified") is not True or quality.get("root_edit_review_verified") is not True
            or quality.get("human_audio_review") is not False or quality.get("full_precision_certified") is not False
            or quality.get("complete_speech_coverage_verified") is not False
            or type(quality.get("unresolved_count")) is not int or quality["unresolved_count"] < 0
            or any(not HASH.fullmatch(str(quality.get(key, ""))) for key in ("original_source_sha256", "root_output_sha256", "root_receipt_sha256"))):
        raise ValueError("dialogue_quality_overclaim_or_missing_proof")


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
        voices = voice_policy(root, policy, read_object)
        catalog_path = root / "catalog/guests.json"
        participants = programme_participants(read_object(catalog_path)) if catalog_path.exists() else {}
        external_participants = appearance_participants(root)
        protected_ids = member_ids | {row["video_id"] for row in rows if row.get("video_id")}
        identities = set()
        for row in rows:
            if "source_id" in row:
                identity, relative, cues = validate_external_dialogue(root, row, external_participants, protected_ids)
                if identity in identities:
                    raise ValueError("invalid_duplicate_or_protected_dialogue_id")
                identities.add(identity)
                admitted.add(relative)
                count += cues
                continue
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
                    or data.get("language") not in {"zh", "en", "mixed"}):
                raise ValueError("dialogue_source_metadata_missing")
            if CATALOG_FIELDS & data.keys():
                raise ValueError("dialogue_catalog_metadata_duplicated")
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
            validate_quality(data)
            validate_units(data, turns.get(identity), participants.get(data["id"], set()), voices.get(identity))
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
