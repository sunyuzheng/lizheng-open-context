"""Synthetic admission/staging boundaries; no corpus, provider, or model access."""
import copy
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("public_dialogue_proposal", SCRIPTS / "prepare_public_dialogues.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)
import search_dialogue_candidates as local_search

ID = "ABCDEFGHIJK"
OTHER = "LMNOPQRSTUV"


class PublicDialogueProposalTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.owner = self.base / "B"
        self.archive = self.base / "kedaibiao-channel"
        self.pack = self.owner / ".source-cache/synthetic-pack"
        self.pack.mkdir(parents=True)
        self.archive.mkdir()
        self.output = self.owner / ".source-cache/new-proposal"
        self.inventory_path = self.owner / ".source-cache/review/inventory.json"
        self.report_path = self.owner / ".source-cache/observations/consolidated-report.json"
        self.observation_path = self.owner / f".source-cache/observations/records/{ID}.json"
        self.original_source = self.put(self.archive / "archive/source/original.srt", b"synthetic guarded source\n")
        self.source_hash = tool.digest(self.original_source.read_bytes())
        self.member_path = self.put(self.owner / "config/member-video-policy.json", tool.encode({"records": []}))
        self.inventory = {"records": [{"video_id": ID, "title": "Synthetic local metadata", "guest_names_from_catalog": []}]}
        self.source = {"schema_version": 1, "id": f"youtube-{ID}", "video_id": ID,
            "data_layer": "raw", "source_type": "video-transcript", "published_at": "2020-01-02",
            "source_url": f"https://www.youtube.com/watch?v={ID}",
            "speaker_classification": "mixed-or-unresolved", "content_origin": "mixed-or-unresolved-speech",
            "evidence_role": "speaker-attributed-speech", "yuzheng_stance_weight": "not-evidence",
            "publication_performed": False, "approval_pending": True,
            "quality": {"status": "root-reviewed-ai-edits", "full_source_ai_processing_verified": True,
                "human_audio_review": False, "full_precision_certified": False,
                "full_original_source_read": False, "unresolved_count": 1,
                "source": str(self.original_source.relative_to(self.archive)), "source_sha256": self.source_hash,
                "output_sha256": "b" * 64, "receipt_sha256": "c" * 64},
            "units": [{"id": f"youtube-{ID}#cue-1", "start_seconds": 1.25, "end_seconds": 2.75,
                       "text": " Synthetic speech\nsecond fixture line ", "speaker_id": "unknown",
                       "speaker_name": "", "speaker_status": "unresolved"}]}
        self.raw_path = self.pack / f"raw/youtube-{ID}.json"
        self.manifest = {"purpose": "local-unapproved-dialogue-candidates", "publication_performed": False,
            "approval_pending": True, "archive_root": str(self.archive), "inventory": str(self.inventory_path),
            "candidate_count": 1, "prepared_count": 1, "held_count": 0, "cue_count": 1,
            "records": [{"video_id": ID, "status": "prepared", "path": f"raw/youtube-{ID}.json", "cue_count": 1}]}
        self.observation = {"video_id": ID, "status": "public_verified", "guard_failures": [],
            "metadata": {"id": ID, "channel_id": tool.CHANNEL, "availability": "public",
                         "is_live": False, "live_status": "not_live", "was_live": False, "age_limit": 0, "duration": 12},
            "public_author_metadata": {"title": "Synthetic public author title", "upload_date": "20200102"},
            "observed_finished_at": "2026-10-10T12:00:00+00:00"}
        self.row = {**copy.deepcopy(self.observation), "identity_verified": True,
                    "observation_finished_at": self.observation["observed_finished_at"],
                    "observation_path": str(self.observation_path),
                    "source_bindings": [{"video_id": ID, "source": str(self.original_source),
                                         "source_sha256": self.source_hash, "folder": "archive/source"}]}
        self.report = {"schema_version": 1, "status": "consolidated_hash_identity_audit_passed",
            "publication_performed": False, "approval_pending": True, "remote_writes": False,
            "expected_channel_id": tool.CHANNEL, "input_drift_count": 0,
            "requested_video_ids": [ID], "records": [self.row]}
        self.save_pack()
        self.save_observation()
        self.root_patch = patch.object(tool, "ROOT", self.owner)
        self.search_root_patch = patch.object(local_search, "ROOT", self.owner)
        self.root_patch.start(); self.search_root_patch.start()

    def tearDown(self):
        self.search_root_patch.stop(); self.root_patch.stop()
        self.temp.cleanup()

    @staticmethod
    def put(path, raw):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        return path

    @staticmethod
    def ref(path):
        raw = path.read_bytes()
        return {"sha256": tool.digest(raw), "bytes": len(raw)}

    def save_pack(self):
        self.put(self.inventory_path, tool.encode(self.inventory))
        self.put(self.raw_path, tool.encode(self.source))
        self.manifest["inventory_sha256"] = tool.digest(self.inventory_path.read_bytes())
        self.manifest["input_guards"] = {str(p): self.ref(p) for p in [self.inventory_path, self.original_source]}
        self.manifest["files"] = {f"raw/youtube-{ID}.json": self.ref(self.raw_path)}
        self.put(self.pack / "manifest.json", tool.encode(self.manifest))
        self.put(self.pack / "receipt.json", tool.encode({"status": "local-candidates-complete",
            "manifest_sha256": tool.digest((self.pack / "manifest.json").read_bytes()),
            "publication_performed": False, "approval_pending": True}))

    def save_observation(self):
        self.put(self.observation_path, tool.encode(self.observation))
        self.row["observation_sha256"] = tool.digest(self.observation_path.read_bytes())
        self.report["references"] = {str(self.observation_path): self.ref(self.observation_path)}
        self.save_report()

    def save_report(self):
        self.put(self.report_path, tool.encode(self.report))

    def prepare(self, exclusions=None):
        return tool.prepare(self.pack, [self.report_path], exclusions)

    def main(self, *extra):
        argv = ["prepare_public_dialogues.py", "--pack", str(self.pack), "--observations", str(self.report_path),
                "--output", str(self.output), *extra]
        with patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()):
            return tool.main()

    def test_unknown_raw_cues_preserved_and_no_quality_overclaim(self):
        files, plan = self.prepare()
        data = json.loads(files[f"corpus/dialogues/youtube-{ID}.json"])
        self.assertEqual(data["units"], self.source["units"])
        self.assertFalse(data["quality"]["full_original_source_read"])
        self.assertFalse(data["quality"]["human_audio_review"])
        self.assertFalse(data["quality"]["full_precision_certified"])
        self.assertFalse(data["quality"]["complete_speech_coverage_verified"])
        self.assertFalse(plan["publication_performed"])
        self.assertTrue(plan["approval_pending"])
        self.assertEqual(plan["proposed_dialogues"], 1)

    def test_protected_member_excluded_even_with_verified_public_observation(self):
        self.member_path.write_bytes(tool.encode({"records": [{"video_id": ID}]}))
        files, plan = self.prepare()
        self.assertEqual(plan["proposed_dialogues"], 0)
        self.assertEqual(plan["records"][0]["reason"], "protected-existing-member-snapshot")
        self.assertNotIn(f"corpus/dialogues/youtube-{ID}.json", files)

    def test_pending_and_unobserved_are_held_without_reading_missing_raw(self):
        self.observation.update(status="pending", metadata={}, public_author_metadata=None,
                                guard_failures=["anonymous_metadata_extraction_failed"])
        self.row.update(status="pending", metadata={}, public_author_metadata=None,
                        guard_failures=["anonymous_metadata_extraction_failed"], identity_verified=False)
        self.save_observation()
        self.manifest.update(prepared_count=0, held_count=1, cue_count=0)
        self.manifest["records"][0] = {"video_id": ID, "status": "held"}
        self.save_pack(); self.manifest["files"] = {}
        self.put(self.pack / "manifest.json", tool.encode(self.manifest))
        self.put(self.pack / "receipt.json", tool.encode({"status": "local-candidates-complete",
            "manifest_sha256": tool.digest((self.pack / "manifest.json").read_bytes()),
            "publication_performed": False, "approval_pending": True}))
        self.raw_path.unlink()
        files, plan = self.prepare()
        self.assertEqual(plan["proposed_dialogues"], 0)
        self.assertEqual(plan["records"][0]["reason"], "anonymous-visibility-not-verified")
        self.assertEqual(tool.prepare(self.pack, [])[1]["records"][0]["reason"], "not-anonymously-observed")

    def test_explicit_exclusion_is_exact_and_requires_nonempty_reason(self):
        self.assertEqual(self.prepare({ID: "synthetic root exclusion"})[1]["proposed_dialogues"], 0)
        for exclusions in [{OTHER: "synthetic"}, {ID: " "}, {ID: None}]:
            with self.subTest(exclusions=exclusions):
                with self.assertRaisesRegex(ValueError, "invalid_explicit_exclusions"):
                    self.prepare(exclusions)

    def test_report_safety_flags_reject(self):
        for field, value in [("publication_performed", True), ("approval_pending", False),
                             ("remote_writes", True), ("expected_channel_id", "other"), ("input_drift_count", 1)]:
            with self.subTest(field=field):
                previous = self.report[field]; self.report[field] = value; self.save_report()
                with self.assertRaisesRegex(ValueError, "observation_report_not_safe"):
                    self.prepare()
                self.report[field] = previous

    def test_exact_report_coverage_and_duplicate_observations(self):
        original = copy.deepcopy(self.report)
        for requested, records in [([ID, ID], [self.row]), ([OTHER], [self.row]), ([ID], [])]:
            self.report.update(requested_video_ids=requested, records=records); self.save_report()
            with self.assertRaisesRegex(ValueError, "observation_identity_coverage_mismatch"):
                self.prepare()
        self.report = original; self.row = self.report["records"][0]; self.save_report()
        with self.assertRaisesRegex(ValueError, "duplicate_observation_identity"):
            tool.prepare(self.pack, [self.report_path, self.report_path])

    def test_raw_observation_reference_and_row_hash_drift_reject(self):
        self.observation_path.write_bytes(self.observation_path.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "observation_reference_changed"):
            self.prepare()
        self.save_observation()
        self.row["observation_sha256"] = "0" * 64; self.save_report()
        with self.assertRaisesRegex(ValueError, "observation_record_changed"):
            self.prepare()

    def test_consolidated_fields_must_equal_raw_observation(self):
        for key, value in [("status", "pending"), ("metadata", {}),
                           ("public_author_metadata", {"title": "different synthetic metadata", "upload_date": "20200102"}),
                           ("guard_failures", ["synthetic drift"])]:
            with self.subTest(key=key):
                previous = self.row[key]; self.row[key] = value; self.save_report()
                with self.assertRaisesRegex(ValueError, "consolidated_observation_differs"):
                    self.prepare()
                self.row[key] = previous

    def test_public_identity_channel_live_availability_age_gates(self):
        for key, value in [("id", OTHER), ("channel_id", "other"), ("availability", "unlisted"),
                           ("is_live", True), ("live_status", "is_live"), ("age_limit", 18)]:
            with self.subTest(key=key):
                old = self.observation["metadata"][key]
                self.observation["metadata"][key] = value; self.row["metadata"][key] = value; self.save_observation()
                with self.assertRaisesRegex(ValueError, "public_observation_identity_unsafe"):
                    self.prepare()
                self.observation["metadata"][key] = old; self.row["metadata"][key] = old

    def test_author_title_and_date_required_without_inventing_values(self):
        for mutation in [{"title": " "}, {"upload_date": "20201340"}]:
            with self.subTest(field=next(iter(mutation))):
                old = copy.deepcopy(self.observation["public_author_metadata"])
                self.observation["public_author_metadata"].update(mutation)
                self.row["public_author_metadata"].update(mutation); self.save_observation()
                with self.assertRaises(ValueError):
                    self.prepare()
                self.observation["public_author_metadata"] = old; self.row["public_author_metadata"] = copy.deepcopy(old)

    def test_source_binding_id_or_hash_mismatch_reject(self):
        for mutation in [{"video_id": OTHER}, {"source_sha256": "0" * 64}]:
            with self.subTest(field=next(iter(mutation))):
                old = copy.deepcopy(self.row["source_bindings"])
                self.row["source_bindings"][0].update(mutation); self.save_report()
                with self.assertRaisesRegex(ValueError, "anonymous_source_binding_mismatch"):
                    self.prepare()
                self.row["source_bindings"] = old

    def test_quality_verified_flags_required(self):
        for key, value in [("status", "filename-only-claim"), ("full_source_ai_processing_verified", False),
                           ("human_audio_review", True), ("full_precision_certified", True)]:
            with self.subTest(key=key):
                previous = self.source["quality"][key]; self.source["quality"][key] = value; self.save_pack()
                with self.assertRaisesRegex(ValueError, "candidate_quality_not_verified"):
                    self.prepare()
                self.source["quality"][key] = previous

    def test_named_guessed_or_private_units_require_rejection(self):
        for mutation in [{"speaker_id": "yuzheng"}, {"speaker_name": "Synthetic guest"},
                         {"speaker_status": "model-guessed"}, {"source_visibility": "members-only"},
                         {"text_access": "private"}]:
            with self.subTest(fields=list(mutation)):
                original = copy.deepcopy(self.source["units"][0]); self.source["units"][0].update(mutation); self.save_pack()
                with self.assertRaises(ValueError):
                    self.prepare()
                self.source["units"][0] = original

    def test_quality_count_bool_and_hash_fields_require_strict_types(self):
        for key, value in [("full_original_source_read", "true"), ("unresolved_count", -1), ("unresolved_count", True),
                           ("source_sha256", "short"), ("output_sha256", "short"), ("receipt_sha256", "short")]:
            with self.subTest(key=key, value=value):
                original = self.source["quality"][key]; self.source["quality"][key] = value; self.save_pack()
                with self.assertRaises(ValueError):
                    self.prepare()
                self.source["quality"][key] = original

    def test_exact_unit_fields_and_complete_nonempty_raw_units_required(self):
        original = copy.deepcopy(self.source["units"])
        for units in [[], [{key: value for key, value in original[0].items() if key != "speaker_name"}],
                      [{**original[0], "summary": "synthetic derived field"}],
                      [{**original[0], "text": " "}]]:
            with self.subTest(fields=[sorted(unit) for unit in units]):
                self.source["units"] = units
                self.manifest["records"][0]["cue_count"] = len(units)
                self.manifest["cue_count"] = len(units)
                self.save_pack()
                with self.assertRaises(ValueError):
                    self.prepare()
        self.source["units"] = original

    def test_strict_finite_positive_unit_geometry_required(self):
        for mutation in [{"start_seconds": -1}, {"end_seconds": 1}, {"end_seconds": 1.25},
                         {"start_seconds": True}, {"start_seconds": "1.25"},
                         {"end_seconds": float("inf")}, {"end_seconds": float("nan")}]:
            with self.subTest(fields=list(mutation)):
                original = copy.deepcopy(self.source["units"][0])
                self.source["units"][0].update(mutation); self.save_pack()
                with self.assertRaises(ValueError):
                    self.prepare()
                self.source["units"][0] = original

    def test_duplicate_unit_id_rejected_with_correct_count(self):
        self.source["units"].append({**self.source["units"][0], "start_seconds": 4, "end_seconds": 5})
        self.manifest["records"][0]["cue_count"] = 2
        self.manifest["cue_count"] = 2
        self.save_pack()
        with self.assertRaises(ValueError):
            self.prepare()

    def test_source_binding_wrong_path_same_hash_requires_rejection(self):
        self.row["source_bindings"][0]["source"] = str(self.archive / "archive/unrelated/original.srt")
        self.save_report()
        with self.assertRaises(ValueError):
            self.prepare()

    def test_dry_run_does_not_write_or_overwrite(self):
        before = {str(p): p.read_bytes() for p in self.base.rglob("*") if p.is_file()}
        self.assertEqual(self.main(), 0)
        self.assertFalse(self.output.exists())
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.base.rglob("*") if p.is_file()})

    def test_local_apply_writes_only_new_cache_and_keeps_pending(self):
        self.assertEqual(self.main("--apply"), 0)
        self.assertFalse((self.owner / "corpus").exists())
        self.assertFalse((self.owner / "config/public-dialogue-policy.json").exists())
        receipt = json.loads((self.output / "receipt.json").read_bytes())
        self.assertFalse(receipt["publication_performed"])
        self.assertTrue(receipt["approval_pending"])
        before = {str(p): p.read_bytes() for p in self.output.rglob("*") if p.is_file()}
        self.assertEqual(self.main("--apply"), 2)
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.output.rglob("*") if p.is_file()})

    def test_public_output_path_or_symlink_parent_refused(self):
        self.output = self.owner / "corpus/proposal"
        self.assertEqual(self.main("--apply"), 2)
        self.assertFalse(self.output.exists())
        link = self.owner / ".source-cache/linked"
        link.symlink_to(self.archive, target_is_directory=True)
        self.output = link / "new-proposal"
        self.assertEqual(self.main("--apply"), 2)
        self.assertFalse((self.archive / "new-proposal").exists())

    def test_input_drift_between_prepare_and_local_apply_rejected(self):
        original_prepare = tool.prepare
        def change_after_prepare(*args, **kwargs):
            prepared = original_prepare(*args, **kwargs)
            self.original_source.write_bytes(b"synthetic concurrent drift\n")
            return prepared
        with patch.object(tool, "prepare", side_effect=change_after_prepare):
            self.assertEqual(self.main("--apply"), 2)
        self.assertFalse(self.output.exists())

    def test_input_drift_during_output_write_never_gets_complete_receipt(self):
        original_open = Path.open
        changed = False
        def open_then_change(path, mode="r", *args, **kwargs):
            nonlocal changed
            handle = original_open(path, mode, *args, **kwargs)
            if not changed and "x" in mode and path.is_relative_to(self.output):
                changed = True
                self.original_source.write_bytes(b"synthetic drift during staging write\n")
            return handle
        with patch.object(Path, "open", open_then_change):
            self.assertEqual(self.main("--apply"), 2)
        self.assertTrue(changed)
        self.assertFalse((self.output / "receipt.json").exists())


if __name__ == "__main__":
    unittest.main()
