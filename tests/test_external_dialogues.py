"""External admissions retain exact source versions and separately reviewed speech."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import dialogue_policy as policy
import raw_turn_policy as turns
import search
import validate_guest_catalog as guests

SOURCE = "dialogue-circle-12345"
URL = "https://example.org/recording/published-replay"


class ExternalDialogueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.path = self.root / f"corpus/dialogues/{SOURCE}.json"
        self.path.parent.mkdir(parents=True)
        (self.root / "config").mkdir()
        self.data = {**policy.PROVENANCE, "schema_version": 1, "id": SOURCE,
            "title": "Synthetic external conversation", "published_at": "2026-09-25", "language": "zh",
            "source_url": URL, "source_family": URL, "publisher": "Original source publisher",
            "inclusion_authorization": policy.EXTERNAL_AUTHORIZATION, "timestamp_mode": "display-only",
            "public_verified_at": "2026-10-15T12:00:00+00:00",
            "quality": {"ai_text_processing_verified": True, "root_edit_review_verified": True,
                "human_audio_review": False, "full_precision_certified": False,
                "complete_speech_coverage_verified": False, "unresolved_count": 1,
                "original_source_sha256": "a" * 64, "root_output_sha256": "b" * 64,
                "root_receipt_sha256": "c" * 64},
            "units": [{"id": "cue-1", "text": "Synthetic exact speech", "start_seconds": 61.5,
                       "end_seconds": 64, "speaker_id": "unknown", "speaker_name": "", "speaker_status": "unresolved"}]}
        self.row = {"source_id": SOURCE, "source_url": URL, "corpus_path": self.path.relative_to(self.root).as_posix(),
            "cue_count": 1, "review_units": [], "anonymous_evidence": {"source_url": URL,
                "availability": "public", "receipt_sha256": "d" * 64, "verified_at": self.data["public_verified_at"]}}
        self.config = {"schema_version": 1, "authorization": policy.AUTHORIZATION, "scope": "public-dialogues-only",
            "removal": "https://example.org/removal",
            "rights_notice": "Guests retain rights in their own speech; inclusion does not establish Yuzheng's endorsement.",
            "records": [self.row]}
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        self.path.write_text(json.dumps(self.data), encoding="utf-8")
        self.row["sha256"] = hashlib.sha256(self.path.read_bytes()).hexdigest()
        (self.root / "config/public-dialogue-policy.json").write_text(json.dumps(self.config), encoding="utf-8")

    def check(self):
        errors = []
        stats = policy.validate_dialogues(self.root, set(), errors)
        return stats, errors

    def documents(self):
        previous = search.ROOT
        search.ROOT = self.root
        try:
            return search.parse_raw_dialogue(self.path)
        finally:
            search.ROOT = previous

    def appearance(self):
        row = {"id": "appearance-synthetic", "title": "Synthetic show title", "show": "Synthetic show",
               "url": "https://example.org/official-audio", "published_at": "2026-09-25",
               "transcript_id": SOURCE, "transcript_path": self.row["corpus_path"],
               "participants": [{"speaker_id": "yuzheng", "speaker_name": "立正", "role": "guest"},
                                {"speaker_id": "host:synthetic", "speaker_name": "Synthetic host", "role": "host"}]}
        folder = self.root / "catalog"
        folder.mkdir(exist_ok=True)
        (folder / "guest-appearances.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
        return row

    def reviewed(self):
        self.appearance()
        unit = self.data["units"][0]
        unit.update(speaker_id="host:synthetic", speaker_name="Synthetic host",
                    speaker_status=turns.REVIEWED, speech_act="question")
        self.row["review_units"] = [{"id": unit["id"], "content_sha256": turns.digest(turns.content(unit)),
            **{key: unit[key] for key in ("speaker_id", "speaker_name", "speech_act")}}]
        self.save()

    def test_unknown_external_source_needs_no_fake_youtube_identity(self):
        self.assertEqual(self.check(), ({"structured_public_dialogues": 1, "structured_dialogue_cues": 1}, []))
        self.assertNotIn("video_id", self.data)
        doc = self.documents()[0]
        self.assertEqual((doc.source_url, doc.source_type, doc.speaker_status), (URL, "video-transcript", "unresolved"))
        self.assertTrue(doc.text.startswith("[00:01:01] "))
        self.assertNotIn("&t=", doc.source_url)
        self.assertNotIn("youtube", doc.source_url)
        self.data["source_type"] = "audio-transcript"; self.save()
        self.assertEqual(self.check()[1], [])
        self.assertEqual(self.documents()[0].source_type, "audio-transcript")

    def test_hash_exact_set_and_source_public_evidence_remain_bound(self):
        self.path.write_text(self.path.read_text() + " ")
        self.assertIn("hash_mismatch", self.check()[1][0])
        self.save()
        extra = self.path.parent / "unbound.json"; extra.write_text("{}")
        self.assertIn("exact_set_mismatch", self.check()[1][0]); extra.unlink()
        self.row["anonymous_evidence"]["source_url"] = "https://example.org/different-version"
        self.save(); self.assertIn("not_verified", self.check()[1][0])
        self.row["anonymous_evidence"]["source_url"] = URL
        self.row["anonymous_evidence"]["availability"] = "members-only"
        self.save(); self.assertIn("not_verified", self.check()[1][0])

    def test_review_units_bind_content_timing_label_and_act_after_snapshot_rebinding(self):
        self.reviewed()
        self.assertEqual(self.check()[1], [])
        original = copy.deepcopy(self.data)
        for field, value in [("text", "Changed source speech"), ("start_seconds", 62),
                             ("speech_act", "statement"), ("speaker_id", "yuzheng"),
                             ("speaker_name", "Different host")]:
            with self.subTest(field=field):
                self.data = copy.deepcopy(original)
                self.data["units"][0][field] = value
                self.save()
                self.assertTrue(self.check()[1])
        self.data = original
        self.row["review_units"][0]["id"] = "wrong-cue"
        self.save(); self.assertIn("exact_units_mismatch", self.check()[1][0])

    def test_named_speech_requires_exact_review_and_appearance_identity(self):
        self.reviewed()
        self.row["review_units"] = []
        self.save(); self.assertIn("exact_units_mismatch", self.check()[1][0])
        self.reviewed()
        (self.root / "catalog/guest-appearances.jsonl").unlink()
        self.assertIn("speaker_not_in_appearance", self.check()[1][0])
        self.appearance()
        people = guests.appearance_participants(self.root)
        self.assertEqual(guests.verify_raw_metadata({"appearances": []}, [self.data], people), 1)
        self.data["units"][0]["speaker_id"] = "guest:wrong-ashley"
        with self.assertRaisesRegex(ValueError, "speaker_programme_mismatch"):
            guests.verify_raw_metadata({"appearances": []}, [self.data], people)

    def test_external_provenance_does_not_relax_existing_rights_or_quality(self):
        original = copy.deepcopy(self.data)
        for key, value in [("video_id", "ABCDEFGHIJK"), ("inclusion_authorization", policy.AUTHORIZATION),
                           ("license", "CC0-1.0"), ("rights_scope", "first-party"),
                           ("source_visibility", "members-only"), ("timestamp_mode", "youtube")]:
            self.data = copy.deepcopy(original); self.data[key] = value
            self.save(); self.assertTrue(self.check()[1], key)
        self.data = original
        self.data["quality"]["full_precision_certified"] = True
        self.save(); self.assertIn("overclaim", self.check()[1][0])

    def test_external_retained_reference_pair_is_exact(self):
        for scope, license, valid in [
                ("third-party-reference", policy.RETAINED, True),
                ("publisher-authorized-transcript", policy.REFERENCE_USE, True),
                ("third-party-reference", policy.REFERENCE_USE, False),
                ("publisher-authorized-transcript", policy.RETAINED, False)]:
            with self.subTest(scope=scope, license=license):
                self.data.update(rights_scope=scope, license=license)
                self.save()
                self.assertEqual(not self.check()[1], valid)

    def test_guest_validator_accepts_bound_external_file_without_creating_interviewee(self):
        self.reviewed()
        catalog = {"schema_version": 1, "entities": [], "sources": [], "appearances": [], "redirects": []}
        (self.root / "catalog/guests.json").write_text(json.dumps(catalog))
        (self.root / "catalog/guest-articles.json").write_text(json.dumps({"schema_version": 1, "articles": []}))
        (self.root / "release-manifest.json").write_text(json.dumps({"files": [{
            "path": self.row["corpus_path"], "sha256": self.row["sha256"], "bytes": self.path.stat().st_size}]}))
        stats = guests.validate_guest_catalog(self.root)
        self.assertEqual((stats["public_raw_records"], stats["entities"], stats["sources"]), (1, 0, 0))
        self.assertEqual(self.check()[1], [])

    def test_optional_appearance_catalog_is_metadata_never_raw_speech(self):
        self.path.unlink()
        previous = search.ROOT
        search.ROOT = self.root
        try:
            self.assertEqual(search.load_documents(), [])
            self.appearance()
            doc, = search.load_documents()
            self.assertEqual((doc.source_type, doc.data_layer, doc.speaker_status),
                             ("guest-appearance-catalog", "structured", "not-speech"))
            self.assertEqual(doc.yuzheng_stance_weight, "not-evidence")
            self.assertIn("Synthetic host", doc.text)
            self.assertTrue(search.type_matches(doc, "video"))
        finally:
            search.ROOT = previous

    def test_external_participants_join_raw_and_catalog_without_assigning_speech(self):
        row = self.appearance()
        row["participants"][1].update(aliases=["Synthetic Host Q"], qualifiers=["Synthetic Seattle radio"])
        (self.root / "catalog/guest-appearances.jsonl").write_text(json.dumps(row) + "\n")
        before = self.path.read_bytes()
        previous = search.ROOT
        search.ROOT = self.root
        try:
            raw = search.parse_raw_dialogue(self.path)[0]
            ownership = (raw.speaker_id, raw.speaker_status, raw.author, raw.yuzheng_stance_weight)
            search.apply_guest_catalog([raw])
            self.assertEqual((raw.speaker_id, raw.speaker_status, raw.author, raw.yuzheng_stance_weight), ownership)
            docs = search.load_documents()
            self.assertEqual(len(docs), 2)
            for doc in docs:
                self.assertEqual(doc.participant_entity_ids, "yuzheng；host:synthetic")
                self.assertEqual(doc.participant_names, "立正；Synthetic host")
                self.assertIn("Synthetic Host Q", doc.participant_aliases)
                self.assertIn("Synthetic Seattle radio", doc.participant_aliases)
                self.assertTrue(doc.participant_metadata_basis.startswith("catalog/guest-appearances.jsonl"))
            self.assertEqual(raw.timestamp_mode, "display-only")
            self.assertEqual(self.path.read_bytes(), before)
        finally:
            search.ROOT = previous

    def test_external_alias_fields_are_validated_even_for_catalog_only_rows(self):
        row = self.appearance()
        row.pop("transcript_id"); row.pop("transcript_path")
        row["participants"][1]["aliases"] = "not-an-array"
        (self.root / "catalog/guest-appearances.jsonl").write_text(json.dumps(row) + "\n")
        self.assertIn("participant_names_invalid", self.check()[1][0])

    def test_actual_youtube_sources_keep_timing_but_other_hosts_never_gain_it(self):
        self.data.pop("timestamp_mode")
        self.data["source_url"] = "https://www.youtube.com/watch?v=ABCDEFGHIJK"
        self.save(); self.assertEqual(self.documents()[0].source_url, "https://www.youtube.com/watch?v=ABCDEFGHIJK&t=61s")
        self.data["source_url"] = "https://www.youtube.com.example.org/watch?v=ABCDEFGHIJK"
        self.save(); self.assertEqual(self.documents()[0].source_url, self.data["source_url"])

    def test_external_record_cannot_relabel_a_protected_youtube_source(self):
        source = "https://www.youtube.com/watch?v=ABCDEFGHIJK"
        self.data.update(source_url=source, source_family=source)
        self.row["source_url"] = source
        self.row["anonymous_evidence"]["source_url"] = source
        self.save()
        errors = []
        policy.validate_dialogues(self.root, {"ABCDEFGHIJK"}, errors)
        self.assertIn("cannot_bypass_youtube_policy", errors[0])


if __name__ == "__main__":
    unittest.main()
