"""Exact-set public admission guards, using synthetic speech only."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import dialogue_policy as policy
import raw_turn_policy as turns

ID = "ABCDEFGHIJK"


class DialoguePolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.path = self.root / f"corpus/dialogues/youtube-{ID}.json"
        self.path.parent.mkdir(parents=True)
        (self.root / "config").mkdir()
        self.data = {**policy.PROVENANCE, "schema_version": 1, "id": f"youtube-{ID}", "video_id": ID,
            "title": "Synthetic dialogue", "published_at": "2020-01-02", "language": "zh",
            "attribution_note": "Speakers unresolved; not the publisher's stance.",
            "source_url": f"https://www.youtube.com/watch?v={ID}", "source_family": f"https://www.youtube.com/watch?v={ID}",
            "public_verified_at": "2026-10-10T12:00:00+00:00",
            "quality": {"ai_text_processing_verified": True, "root_edit_review_verified": True,
                "human_audio_review": False, "full_precision_certified": False, "complete_speech_coverage_verified": False,
                "unresolved_count": 1, "original_source_sha256": "a" * 64, "root_output_sha256": "b" * 64,
                "root_receipt_sha256": "c" * 64},
            "units": [{"id": "cue-1", "text": "Synthetic exact speech", "start_seconds": 1, "end_seconds": 3,
                       "speaker_id": "unknown", "speaker_name": "", "speaker_status": "unresolved"}]}
        self.row = {"video_id": ID, "corpus_path": self.path.relative_to(self.root).as_posix(), "cue_count": 1,
            "anonymous_evidence": {"video_id": ID, "channel_id": policy.CHANNEL, "availability": "public",
                "is_live": False, "is_upcoming": False, "receipt_sha256": "d" * 64,
                "verified_at": self.data["public_verified_at"]}}
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        self.path.write_text(json.dumps(self.data))
        self.row["sha256"] = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.config = {"schema_version": 1, "authorization": policy.AUTHORIZATION, "scope": "public-dialogues-only",
            "removal": "https://example.org/removal", "rights_notice": "Guests retain rights in their own speech; inclusion does not establish Yuzheng's endorsement.",
            "records": [self.row]}
        self.policy_path = self.root / "config/public-dialogue-policy.json"
        self.policy_path.write_text(json.dumps(self.config))

    def check(self, member_ids=None):
        errors = []
        stats = policy.validate_dialogues(self.root, member_ids or set(), errors)
        return stats, errors

    def test_complete_exact_unknown_source_is_admitted(self):
        stats, errors = self.check()
        self.assertEqual(errors, [])
        self.assertEqual(stats, {"structured_public_dialogues": 1, "structured_dialogue_cues": 1})

    def test_without_policy_never_admits_structured_sources(self):
        self.policy_path.unlink()
        self.assertIn("lack an exact", self.check()[1][0])

    def test_hash_drift_and_unbound_extra_source_rejected(self):
        self.path.write_text(self.path.read_text() + " ")
        self.assertIn("hash_mismatch", self.check()[1][0])
        self.save()
        (self.path.parent / "extra.json").write_text("{}")
        self.assertIn("exact_set_mismatch", self.check()[1][0])

    def test_unknown_never_becomes_a_named_or_endorsed_speaker(self):
        for mutation in [{"speaker_id": "yuzheng"}, {"speaker_name": "Guest"}, {"speaker_status": "guessed"}]:
            self.data["units"][0].update(speaker_id="unknown", speaker_name="", speaker_status="unresolved")
            self.data["units"][0].update(mutation); self.save()
            self.assertIn("separate_review_policy", self.check()[1][0])

    def test_private_member_wrong_channel_live_and_precision_overclaims_rejected(self):
        self.assertIn("protected", self.check({ID})[1][0])
        for field, bad in [("source_visibility", "members-only"), ("yuzheng_stance_weight", "direct")]:
            original = self.data[field]; self.data[field] = bad; self.save()
            self.assertTrue(self.check()[1]); self.data[field] = original
        for field, bad in [("channel_id", "other"), ("availability", "unlisted"), ("is_live", True)]:
            original = self.row["anonymous_evidence"][field]; self.row["anonymous_evidence"][field] = bad; self.save()
            self.assertTrue(self.check()[1]); self.row["anonymous_evidence"][field] = original
        self.data["quality"]["human_audio_review"] = True; self.save()
        self.assertIn("overclaim", self.check()[1][0])

    def test_source_identity_or_invalid_cue_rejected(self):
        self.data["video_id"] = "KJIHGFEDCBA"; self.save()
        self.assertIn("identity_mismatch", self.check()[1][0])
        self.data["video_id"] = ID; self.data["units"][0]["start_seconds"] = -1; self.save()
        self.assertTrue(self.check()[1])

    def test_participant_identity_is_metadata_and_requires_bounded_complete_fields(self):
        self.data.update(participant_entity_ids=["guest:synthetic"], participant_aliases=["Synthetic alias"],
                         participant_metadata_basis="Reviewed programme identity; no turn attribution")
        self.save()
        self.assertEqual(self.check()[1], [])
        self.assertEqual(self.data["units"][0]["speaker_id"], "unknown")
        for ids, aliases, basis in [([{}], [], "basis"), (["guest:a", "guest:a"], [], "basis"),
                                   (["guest:a"], ["/Users/private/source"], "basis"),
                                   (["guest:a"], ["alias"], "")]:
            with self.subTest(ids=ids):
                self.data.update(participant_entity_ids=ids, participant_aliases=aliases, participant_metadata_basis=basis)
                self.save(); self.assertIn("identity_metadata_invalid", self.check()[1][0])

    def save_reviewed_turn(self, speaker="yuzheng", act="question"):
        baseline = turns.digest(turns.unknown_units(self.data["units"]))
        unit = self.data["units"][0]
        unit.update(speaker_id=speaker, speaker_name="Synthetic speaker", speaker_status="reviewed-source-attribution", speech_act=act)
        self.save()
        self.turn_data = {"schema_version": 1, "method": turns.METHOD, "human_audio_review": False,
            "full_precision_certified": False, "records": [{"video_id": ID,
            "original_source_sha256": self.data["quality"]["original_source_sha256"],
            "unknown_units_sha256": baseline, "cue_count": 1, "review_basis": "Synthetic self-identification and adjacent source text",
            "units": [{"id": unit["id"], "content_sha256": turns.digest(turns.content(unit)),
                       **{key: unit[key] for key in ("speaker_id", "speaker_name", "speech_act")}}]}]}
        self.save_turn_policy()

    def save_turn_policy(self):
        path = self.root / "config/raw-turn-attribution-policy.json"
        path.write_text(json.dumps(self.turn_data))
        self.config["turn_attribution_policy"] = {"path": path.relative_to(self.root).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        self.policy_path.write_text(json.dumps(self.config))

    def test_exact_source_text_attribution_has_separate_binding_and_no_audio_claim(self):
        self.save_reviewed_turn()
        self.assertEqual(self.check()[1], [])
        previous = policy.search.ROOT
        policy.search.ROOT = self.root
        try:
            docs = policy.search.parse_raw_dialogue(self.path)
        finally:
            policy.search.ROOT = previous
        self.assertEqual(docs[0].speaker_id, "yuzheng")
        self.assertEqual(docs[0].speech_act, "question")
        self.assertEqual(docs[0].yuzheng_stance_weight, "not-evidence")

    def test_reviewed_turn_rejects_body_timing_identity_and_speech_act_changes(self):
        for field, value in [("text", "Invented words"), ("start_seconds", 2), ("speaker_id", "guest:other"),
                             ("speech_act", "statement"), ("speaker_status", "audio-anchor-reviewed")]:
            with self.subTest(field=field):
                self.data["units"][0].update(speaker_id="unknown", speaker_name="", speaker_status="unresolved")
                self.data["units"][0].pop("speech_act", None)
                self.save_reviewed_turn()
                self.data["units"][0][field] = value; self.path.write_text(json.dumps(self.data))
                self.row["sha256"] = hashlib.sha256(self.path.read_bytes()).hexdigest()
                self.policy_path.write_text(json.dumps(self.config))
                self.assertTrue(self.check()[1])

    def test_turn_policy_rejects_unbound_and_overclaimed_evidence(self):
        self.save_reviewed_turn()
        self.config.pop("turn_attribution_policy"); self.policy_path.write_text(json.dumps(self.config))
        self.assertIn("unbound_turn", self.check()[1][0])
        self.turn_data["human_audio_review"] = True; self.save_turn_policy()
        self.assertIn("turn_attribution_policy_invalid", self.check()[1][0])

    def test_turn_policy_refuses_boolean_schema_and_symlink_ancestor(self):
        self.save_reviewed_turn(); self.turn_data["schema_version"] = True; self.save_turn_policy()
        self.assertIn("turn_attribution_policy_invalid", self.check()[1][0])
        self.turn_data["schema_version"] = 1; self.save_turn_policy()
        original = self.root / "config"; target = self.root / "config-real"
        original.rename(target); original.symlink_to(target, target_is_directory=True)
        self.assertIn("binding_invalid", self.check()[1][0])

    def test_guest_attribution_requires_programme_entity_and_exact_unit_set(self):
        self.save_reviewed_turn(speaker="guest:synthetic", act="statement")
        self.assertIn("unit_invalid", self.check()[1][0])
        self.data.update(participant_entity_ids=["guest:synthetic"], participant_aliases=["synthetic"], participant_metadata_basis="programme only")
        self.path.write_text(json.dumps(self.data)); self.row["sha256"] = hashlib.sha256(self.path.read_bytes()).hexdigest()
        self.policy_path.write_text(json.dumps(self.config)); self.assertEqual(self.check()[1], [])
        self.turn_data["records"][0]["units"].append(dict(self.turn_data["records"][0]["units"][0]))
        self.save_turn_policy(); self.assertIn("unit_invalid", self.check()[1][0])


if __name__ == "__main__":
    unittest.main()
