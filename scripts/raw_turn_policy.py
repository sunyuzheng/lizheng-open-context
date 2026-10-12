"""Unit attribution for public dialogues, each method under its own bound policy.

Source-text attribution (config/raw-turn-attribution-policy.json) records units a reviewer
attributed from the words themselves. Voice attribution (config/audio-speaker-policy.json)
records units whose speaker a voice match established: each programme's record binds the
labelled units by hash to the exact transcript they were made from, so editing the text or a
label without redoing the match fails validation.
"""
from __future__ import annotations

import hashlib
import json
import re

ACTS = frozenset({"statement", "question", "introduction", "acknowledgement", "joke", "reported-other"})
METHOD = "source-text-and-self-identification"
REVIEWED = "reviewed-source-attribution"
VOICE = "audio-voice-match"
VOICE_METHOD = "voice-profile-anchored-diarization"
VOICE_POLICY = "config/audio-speaker-policy.json"
VOICE_FIELDS = {"schema_version", "method", "human_audio_review", "full_precision_certified", "model", "profile",
                "thresholds", "speech_acts", "evaluation", "records"}
VOICE_RECORD = {"video_id", "unknown_units_sha256", "labels_sha256", "audio_sha256", "counts", "maintainer_check"}


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def content(unit):
    return {key: unit[key] for key in ("id", "text", "start_seconds", "end_seconds")}


def unknown_units(units):
    return [{**{key: value for key, value in unit.items() if key != "speech_act"},
             "speaker_id": "unknown", "speaker_name": "", "speaker_status": "unresolved"} for unit in units]


def reviewed_policy(root, public_policy, read_object):
    binding = public_policy.get("turn_attribution_policy")
    path = root / "config/raw-turn-attribution-policy.json"
    if binding is None:
        if path.exists():
            raise ValueError("unbound_turn_attribution_policy")
        return {}
    if (not isinstance(binding, dict) or set(binding) != {"path", "sha256"}
            or binding["path"] != "config/raw-turn-attribution-policy.json"
            or any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != binding["sha256"]):
        raise ValueError("turn_attribution_policy_binding_invalid")
    data = read_object(path)
    if (set(data) != {"schema_version", "method", "human_audio_review", "full_precision_certified", "records"}
            or type(data["schema_version"]) is not int or data["schema_version"] != 1 or data["method"] != METHOD
            or data["human_audio_review"] is not False or data["full_precision_certified"] is not False
            or not isinstance(data["records"], list)):
        raise ValueError("turn_attribution_policy_invalid")
    rows = {}
    for row in data["records"]:
        if (not isinstance(row, dict) or set(row) != {"video_id", "original_source_sha256", "unknown_units_sha256", "cue_count", "units", "review_basis"}
                or row["video_id"] in rows or not re.fullmatch(r"[A-Za-z0-9_-]{11}", row["video_id"])
                or any(not re.fullmatch(r"[0-9a-f]{64}", row[key]) for key in ("original_source_sha256", "unknown_units_sha256"))
                or type(row["cue_count"]) is not int or row["cue_count"] < 1
                or not isinstance(row["review_basis"], str) or not row["review_basis"].strip()
                or not isinstance(row["units"], list) or not row["units"]):
            raise ValueError("turn_attribution_record_invalid")
        rows[row["video_id"]] = row
    admitted = {row["video_id"] for row in public_policy["records"]}
    if not set(rows) <= admitted:
        raise ValueError("turn_attribution_source_not_admitted")
    return rows


def voice_labels(units):
    """What a voice record binds: every voice-attributed unit's speaker and speech act."""
    return [{key: u[key] for key in ("id", "speaker_id", "speaker_name", "speech_act")} for u in units if u.get("speaker_status") == VOICE]


def voice_policy(root, public_policy, read_object):
    binding = public_policy.get("audio_attribution_policy")
    path = root / VOICE_POLICY
    if binding is None:
        if path.exists():
            raise ValueError("unbound_audio_attribution_policy")
        return {}
    if (not isinstance(binding, dict) or set(binding) != {"path", "sha256"} or binding["path"] != VOICE_POLICY
            or any(p.is_symlink() for p in (path, *path.parents)) or not path.is_file()
            or hashlib.sha256(path.read_bytes()).hexdigest() != binding["sha256"]):
        raise ValueError("audio_attribution_policy_binding_invalid")
    data = read_object(path)
    if (set(data) != VOICE_FIELDS or type(data["schema_version"]) is not int or data["schema_version"] != 1
            or data["method"] != VOICE_METHOD or data["human_audio_review"] is not False
            or data["full_precision_certified"] is not False
            or not all(isinstance(data[key], dict) and data[key] for key in ("model", "profile", "thresholds", "speech_acts", "evaluation"))
            or not isinstance(data["records"], list)):
        raise ValueError("audio_attribution_policy_invalid")
    rows = {}
    for row in data["records"]:
        if (not isinstance(row, dict) or set(row) != VOICE_RECORD or row["video_id"] in rows
                or not isinstance(row["video_id"], str) or not re.fullmatch(r"[A-Za-z0-9_-]{11}", row["video_id"])
                or any(not isinstance(row[key], str) or not re.fullmatch(r"[0-9a-f]{64}", row[key])
                       for key in ("unknown_units_sha256", "labels_sha256", "audio_sha256"))
                or not isinstance(row["counts"], dict) or set(row["counts"]) != {"yuzheng", "guest", "unresolved"}
                or any(type(v) is not int or v < 0 for v in row["counts"].values())
                or not (row["maintainer_check"] is None or (isinstance(row["maintainer_check"], dict)
                        and set(row["maintainer_check"]) == {"date", "answer"}
                        and all(isinstance(v, str) and v.strip() for v in row["maintainer_check"].values())))):
            raise ValueError("audio_attribution_record_invalid")
        rows[row["video_id"]] = row
    admitted = {row["video_id"] for row in public_policy["records"]}
    if not set(rows) <= admitted:
        raise ValueError("audio_attribution_source_not_admitted")
    return rows


def validate_voice_units(data, row, participant_ids):
    units = data["units"]
    labelled = [u for u in units if u.get("speaker_status") == VOICE]
    if row is None:
        if labelled:
            raise ValueError("audio_attribution_requires_policy_record")
        return
    if digest(unknown_units(units)) != row["unknown_units_sha256"]:
        raise ValueError("audio_attribution_source_units_changed")
    for unit in labelled:
        if (unit.get("speech_act") not in ACTS or not isinstance(unit.get("speaker_name"), str) or not unit["speaker_name"].strip()
                or (unit.get("speaker_id") != "yuzheng" and unit.get("speaker_id") not in participant_ids)):
            raise ValueError("audio_attribution_unit_invalid")
    if digest(voice_labels(units)) != row["labels_sha256"]:
        raise ValueError("audio_attribution_labels_changed")
    counts = {"yuzheng": sum(u["speaker_id"] == "yuzheng" for u in labelled),
              "guest": sum(u["speaker_id"] != "yuzheng" for u in labelled),
              "unresolved": sum(u["speaker_id"] == "unknown" for u in units)}
    if counts != row["counts"]:
        raise ValueError("audio_attribution_counts_mismatch")


def validate_units(data, row, participant_ids, voice_row=None):
    units = data["units"]
    if any(u.get("speaker_id") == "unknown" and "speech_act" in u for u in units):
        raise ValueError("turn_attribution_unknown_speaker_changed")
    if any(u.get("speaker_id") != "unknown" and u.get("speaker_status") not in {REVIEWED, VOICE} for u in units):
        raise ValueError("dialogue_named_speaker_requires_separate_review_policy")
    validate_voice_units(data, voice_row, participant_ids)
    annotations = {u["id"]: u for u in units if u.get("speaker_status") == REVIEWED}
    if row is None:
        if annotations or any(u.get("speaker_id") == "unknown" and (u.get("speaker_name", "") != "" or u.get("speaker_status") != "unresolved") for u in units):
            raise ValueError("dialogue_named_speaker_requires_separate_review_policy")
        return
    if (data["quality"]["original_source_sha256"] != row["original_source_sha256"]
            or len(units) != row["cue_count"] or digest(unknown_units(units)) != row["unknown_units_sha256"]):
        raise ValueError("turn_attribution_source_units_changed")
    if any(u.get("speaker_id") == "unknown" and (u.get("speaker_name", "") != "" or u.get("speaker_status") != "unresolved") for u in units):
        raise ValueError("turn_attribution_unknown_speaker_changed")
    expected = {}
    for annotation in row["units"]:
        if (not isinstance(annotation, dict) or set(annotation) != {"id", "content_sha256", "speaker_id", "speaker_name", "speech_act"}
                or annotation["id"] in expected or annotation["speech_act"] not in ACTS
                or not isinstance(annotation["speaker_id"], str)
                or not re.fullmatch(r"(?:yuzheng|guest:[a-z0-9_.:-]+)", annotation["speaker_id"])
                or not isinstance(annotation["speaker_name"], str) or not annotation["speaker_name"].strip()
                or len(annotation["speaker_name"]) > 100 or any(ord(c) < 32 for c in annotation["speaker_name"])
                or (annotation["speaker_id"] != "yuzheng" and annotation["speaker_id"] not in participant_ids)
                or not re.fullmatch(r"[0-9a-f]{64}", annotation["content_sha256"])):
            raise ValueError("turn_attribution_unit_invalid")
        expected[annotation["id"]] = annotation
    if set(expected) != set(annotations):
        raise ValueError("turn_attribution_exact_units_mismatch")
    for identity, annotation in expected.items():
        unit = annotations[identity]
        if (digest(content(unit)) != annotation["content_sha256"]
                or any(unit.get(key) != annotation[key] for key in ("speaker_id", "speaker_name", "speech_act"))
                or unit.get("speaker_status") != "reviewed-source-attribution"):
            raise ValueError("turn_attribution_unit_changed")
