"""Synthetic local converter boundaries; no corpus access or model calls."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("dialogue_candidates", Path(__file__).parents[1] / "scripts/build_dialogue_candidates.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

ID = "ABCDEFGHIJK"
SRT = b"1\n00:00:01,234 --> 00:00:02,500\n literal first line \nsecond line\n\n2\n00:00:03,000 --> 00:00:04,001\n< No Speech >\n\n"


class DialogueCandidateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.owner, self.archive = self.base / "B", self.base / "A"
        self.owner.mkdir(); self.archive.mkdir()
        self.output = self.owner / ".source-cache/new-candidates"
        self.inventory = self.owner / ".source-cache/review/inventory.json"
        self.source = self.put(self.archive, "archive/source/original.srt", SRT)
        self.source_hash = tool.digest(SRT)
        area = f"logs/subtitle_text_review/root_reviews/{ID}/{self.source_hash}"
        self.root_output = self.put(self.archive, f"{area}/transcript.text-reviewed.srt", SRT)
        ai_output = self.put(self.archive, f"logs/subtitle_text_review/results/{ID}/original.ai-reviewed.srt", SRT)
        chunk_dir = f"logs/subtitle_text_review/staging/{ID}/{self.source_hash}/chunks/0001"
        attempt = chunk_dir + "/attempts/synthetic"
        chunk_output = self.put(self.archive, attempt + f"/{ID}.corrected.srt", SRT)
        self.put(self.archive, attempt + f"/{ID}.qwen.srt", SRT)
        self.put(self.archive, chunk_dir + f"/{ID}.qwen.srt", SRT)
        rejection = self.put(self.archive, attempt + "/safety-rejections.json", tool.json_bytes({"rejection_count": 0}))
        self.chunk = {"output": str(chunk_output.relative_to(self.archive)), "output_sha256": tool.digest(SRT),
                      "input_sha256": tool.digest(SRT), "description": {"index": 1},
                      "safety_rejections": {"path": str(rejection.relative_to(self.archive)), "sha256": tool.digest(rejection.read_bytes()), "count": 0}}
        self.put(self.archive, chunk_dir + "/receipt.json", tool.json_bytes(self.chunk))
        ai = self.put(self.archive, f"logs/subtitle_text_review/receipts/{ID}/{self.source_hash}.json", tool.json_bytes({"chunks": [self.chunk],
                      "status": "text-reviewed", "review": "ai-text-review", "full_source_text_reviewed": True, "timing_count_verified": True}))
        receipt = self.put(self.archive, area + "/review.json", tool.json_bytes({
            "ai_receipt": str(ai.relative_to(self.archive)), "ai_receipt_sha256": tool.digest(ai.read_bytes()),
            "ai_output": str(ai_output.relative_to(self.archive)), "ai_output_sha256": tool.digest(SRT),
            "full_source_ai_processing_verified": True}))
        self.record = {"video_id": ID, "source": str(self.source.relative_to(self.archive)), "source_sha256": self.source_hash,
                       "output": str(self.root_output.relative_to(self.archive)), "output_sha256": tool.digest(SRT),
                       "receipt": str(receipt.relative_to(self.archive)), "receipt_sha256": tool.digest(receipt.read_bytes()),
                       "unresolved_count": 2, "full_original_source_read": False,
                       "human_audio_review_verified": False, "full_precision_certified": False}
        self.quality_row = {"video_id": ID, "folder": "archive/source", "status": "warning",
                            "selected_path": self.record["source"], "selected_sha256": self.source_hash,
                            "youtube_privacy": "unknown", "content_class": "unknown"}
        self.put(self.owner, "catalog/videos.jsonl", (json.dumps({"video_id": ID, "title": "Synthetic author metadata", "published_at": "2020-01-02"}) + "\n").encode())
        self.put(self.archive, "podcast_series.json", tool.json_bytes({"episodes": {}}))
        self.put(self.archive, "logs/subtitle_quality/subtitle_quality.json", tool.json_bytes({"records": [self.quality_row]}))
        self.put(self.owner, "config/member-video-policy.json", tool.json_bytes({"records": [{"video_id": ID, "transcript_sha256": "a" * 64}]}))
        self.put(self.owner, "config/values-conversations-policy.json", tool.json_bytes({"public_transcripts": []}))
        self.inventory_data = {"schema_version": 1, "inputs": self.input_hashes(), "summary": {"candidate_union": 1},
                               "records": [{"video_id": ID, "title": "Synthetic metadata", "source_visibility_in_catalog": None,
                                            "archive_privacy_snapshot": ["unknown"]}]}
        self.save_inventory()

    def tearDown(self):
        self.temp.cleanup()

    def put(self, owner, name, data):
        path = owner / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def input_hashes(self):
        return {"catalog_videos": tool.digest((self.owner / "catalog/videos.jsonl").read_bytes()),
                "podcast_series": tool.digest((self.archive / "podcast_series.json").read_bytes()),
                "subtitle_quality": tool.digest((self.archive / "logs/subtitle_quality/subtitle_quality.json").read_bytes())}

    def save_inventory(self):
        self.put(self.owner, str(self.inventory.relative_to(self.owner)), tool.json_bytes(self.inventory_data))

    def parse(self, raw, suffix):
        # Synthetic fixture parser asserts byte-exact transfer to the real parser interface.
        self.assertEqual(raw, SRT); self.assertEqual(suffix, ".srt")
        return [SimpleNamespace(start_ms=1234, end_ms=2500, text=" literal first line \nsecond line"),
                SimpleNamespace(start_ms=3000, end_ms=4001, text="< No Speech >")]

    def run_build(self, *, apply=False, records=None, rejected=None, aliases=None):
        evidence = ([self.record] if records is None else records, rejected or {}, aliases or {}, self.parse)
        with patch.object(tool, "load_evidence", return_value=evidence):
            return tool.build_candidates(self.archive, self.inventory, self.output, apply=apply, owner=self.owner)

    def test_dry_run_creates_no_files_or_directory(self):
        before = {str(p): p.read_bytes() for p in self.base.rglob("*") if p.is_file()}
        summary = self.run_build()
        self.assertTrue(summary["dry_run"])
        self.assertFalse(self.output.exists())
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.base.rglob("*") if p.is_file()})

    def test_exact_cue_text_time_unknown_speaker_and_unapproved_snapshot(self):
        self.run_build(apply=True)
        doc = json.loads((self.output / f"raw/youtube-{ID}.json").read_bytes())
        self.assertEqual([u["text"] for u in doc["units"]], [" literal first line \nsecond line", "< No Speech >"])
        self.assertEqual([(u["start_seconds"], u["end_seconds"]) for u in doc["units"]], [(1.234, 2.5), (3, 4.001)])
        self.assertTrue(all(u["speaker_id"] == "unknown" and u["speaker_name"] == "" and u["speaker_status"] == "unresolved" for u in doc["units"]))
        self.assertEqual(doc["quality"]["unresolved_count"], 2)
        self.assertFalse(doc["quality"]["full_original_source_read"])
        self.assertFalse(doc["quality"]["human_audio_review"])
        self.assertFalse(doc["quality"]["full_precision"])
        self.assertTrue(doc["approval_pending"]); self.assertFalse(doc["publication_performed"])
        self.assertFalse(doc["existing_exact_authorization_snapshots"][0]["exact_root_output_matches_snapshot"])
        manifest = json.loads((self.output / "manifest.json").read_bytes())
        self.assertEqual(manifest["candidate_count"], manifest["prepared_count"] + manifest["held_count"])
        for name, expected in manifest["files"].items():
            self.assertEqual(tool.digest((self.output / name).read_bytes()), expected["sha256"])
        receipt = json.loads((self.output / "receipt.json").read_bytes())
        self.assertEqual(receipt["manifest_sha256"], tool.digest((self.output / "manifest.json").read_bytes()))

    def test_inventory_hash_drift_rejected_before_proof_scan(self):
        (self.owner / "catalog/videos.jsonl").write_bytes(b"changed")
        with patch.object(tool, "load_evidence") as proof, self.assertRaisesRegex(ValueError, "input_hash_mismatch"):
            tool.build_candidates(self.archive, self.inventory, self.output, owner=self.owner)
        proof.assert_not_called()

    def test_missing_catalog_title_uses_exact_id_bound_author_metadata(self):
        self.put(self.owner, "catalog/videos.jsonl", b"")
        self.inventory_data["records"][0]["title"] = None
        self.inventory_data["inputs"] = self.input_hashes(); self.save_inventory()
        info = self.put(self.archive, "archive/source/original.info.json", tool.json_bytes({
            "id": ID, "title": "Exact original author title", "upload_date": "20200102"}))
        self.run_build(apply=True)
        doc = json.loads((self.output / f"raw/youtube-{ID}.json").read_bytes())
        self.assertEqual(doc["title"], "Exact original author title")
        self.assertEqual(doc["published_at"], "2020-01-02")
        self.assertEqual(doc["metadata_source_sha256"], tool.digest(info.read_bytes()))

    def test_title_fallback_refuses_other_video_metadata(self):
        self.put(self.owner, "catalog/videos.jsonl", b"")
        self.inventory_data["records"][0]["title"] = None
        self.inventory_data["inputs"] = self.input_hashes(); self.save_inventory()
        self.put(self.archive, "archive/source/original.info.json", tool.json_bytes({"id": "KJIHGFEDCBA", "title": "Other video"}))
        with self.assertRaisesRegex(ValueError, "author_metadata_identity_missing_or_conflicting"):
            self.run_build()

    def test_source_hash_drift_rejected(self):
        self.source.write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "input_hash_mismatch"):
            self.run_build()

    def test_chunk_output_hash_drift_rejected(self):
        (self.archive / self.chunk["output"]).write_bytes(b"changed")
        with self.assertRaisesRegex(ValueError, "input_hash_mismatch"):
            self.run_build()

    def test_output_escape_rejected(self):
        self.output = self.owner / "corpus/dialogues"
        with self.assertRaisesRegex(ValueError, "path_outside_allowed_area"):
            self.run_build()

    def test_dotdot_escape_rejected(self):
        self.output = self.owner / ".source-cache/../corpus/dialogues"
        with self.assertRaisesRegex(ValueError, "path_outside_owner"):
            self.run_build()

    def test_output_parent_symlink_rejected(self):
        (self.owner / ".source-cache/link").symlink_to(self.base, target_is_directory=True)
        self.output = self.owner / ".source-cache/link/result"
        with self.assertRaisesRegex(ValueError, "symlink_not_allowed"):
            self.run_build()

    def test_source_symlink_rejected(self):
        data = self.source.read_bytes(); self.source.unlink()
        other = self.put(self.base, "elsewhere.srt", data)
        self.source.symlink_to(other)
        with self.assertRaisesRegex(ValueError, "symlink_not_allowed"):
            self.run_build()

    def test_duplicate_candidate_identity_rejected(self):
        self.inventory_data["records"] *= 2; self.inventory_data["summary"]["candidate_union"] = 2
        self.save_inventory()
        with self.assertRaisesRegex(ValueError, "invalid_or_duplicate_video_id"):
            self.run_build()

    def test_duplicate_root_pair_and_quality_identity_conflict_rejected(self):
        with self.assertRaisesRegex(ValueError, "root_identity_conflict"):
            self.run_build(records=[self.record, self.record])
        self.put(self.archive, "logs/subtitle_quality/subtitle_quality.json", tool.json_bytes({"records": [self.quality_row, self.quality_row]}))
        self.inventory_data["inputs"] = self.input_hashes(); self.save_inventory()
        with self.assertRaisesRegex(ValueError, "quality_identity_conflict"):
            self.run_build()

    def test_missing_source_is_explicit_held_without_raw_output(self):
        self.put(self.archive, "logs/subtitle_quality/subtitle_quality.json", tool.json_bytes({"records": []}))
        self.inventory_data["inputs"] = self.input_hashes(); self.save_inventory()
        result = self.run_build(apply=True, records=[])
        self.assertEqual((result["prepared_count"], result["held_count"]), (0, 1))
        manifest = json.loads((self.output / "manifest.json").read_bytes())
        self.assertEqual(manifest["records"][0]["reason"], "current_source_missing")
        self.assertEqual(list((self.output / "raw").iterdir()), [])

    def test_old_source_root_cannot_cover_current_source(self):
        current = self.put(self.archive, "archive/source/current.srt", b"synthetic new source bytes")
        row = dict(self.quality_row, selected_path=str(current.relative_to(self.archive)), selected_sha256=tool.digest(current.read_bytes()))
        self.put(self.archive, "logs/subtitle_quality/subtitle_quality.json", tool.json_bytes({"records": [row]}))
        self.inventory_data["inputs"] = self.input_hashes(); self.save_inventory()
        result = self.run_build()
        self.assertEqual((result["prepared_count"], result["held_count"]), (0, 1))

    def test_proof_rejection_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "root_evidence_rejected"):
            self.run_build(rejected={"amendment_branch_ambiguous": 1})

    def test_existing_output_never_overwritten(self):
        self.run_build(apply=True)
        receipt = (self.output / "receipt.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "output_must_be_new_exclusive_directory"):
            self.run_build(apply=True)
        self.assertEqual((self.output / "receipt.json").read_bytes(), receipt)

    def test_guard_checks_scan_time_drift_before_any_apply_write(self):
        calls = 0
        def evidence(*args):
            nonlocal calls
            calls += 1
            if calls == 2:
                (self.owner / "catalog/videos.jsonl").write_bytes(b"changed")
            return [self.record], {}, {}, self.parse
        with patch.object(tool, "load_evidence", side_effect=evidence), self.assertRaisesRegex(ValueError, "input_changed_during_scan"):
            tool.build_candidates(self.archive, self.inventory, self.output, apply=True, owner=self.owner)
        self.assertFalse(self.output.exists())

    def test_root_inventory_growth_rejected(self):
        calls = 0
        def evidence(*args):
            nonlocal calls
            calls += 1
            if calls == 2:
                self.put(self.archive, "logs/subtitle_text_review/root_reviews/KJIHGFEDCBA/" + "b" * 64 + "/review.json", b"{}")
            return [self.record], {}, {}, self.parse
        with patch.object(tool, "load_evidence", side_effect=evidence), self.assertRaisesRegex(ValueError, "root_inventory_changed_during_scan"):
            tool.build_candidates(self.archive, self.inventory, self.output, owner=self.owner)

    def test_unresolved_count_must_exist_not_default_zero(self):
        row = dict(self.record); del row["unresolved_count"]
        with self.assertRaisesRegex(ValueError, "root_unresolved_count_invalid"):
            self.run_build(records=[row])

    def test_source_path_cannot_be_replaced_by_same_hash_other_path(self):
        same = self.put(self.archive, "archive/source/same-bytes.srt", SRT)
        row = dict(self.quality_row, selected_path=str(same.relative_to(self.archive)))
        self.put(self.archive, "logs/subtitle_quality/subtitle_quality.json", tool.json_bytes({"records": [row]}))
        self.inventory_data["inputs"] = self.input_hashes(); self.save_inventory()
        with self.assertRaisesRegex(ValueError, "root_selected_source_path_mismatch"):
            self.run_build()

    def test_verified_alias_keeps_both_physical_records(self):
        alternate = dict(self.quality_row, folder="archive/alternate")
        self.put(self.archive, "logs/subtitle_quality/subtitle_quality.json", tool.json_bytes({"records": [self.quality_row, alternate]}))
        self.inventory_data["inputs"] = self.input_hashes(); self.save_inventory()
        variants = []
        for folder in ("archive/source", "archive/alternate"):
            info = self.put(self.archive, folder + "/identity.info.json", tool.json_bytes({"id": ID}))
            media = self.put(self.archive, folder + "/media.m4a", b"synthetic media bytes")
            variants.append({"folder": folder, "info_path": str(info.relative_to(self.archive)), "info_sha256": tool.digest(info.read_bytes()),
                             "media_path": str(media.relative_to(self.archive)), "media_sha256": tool.digest(media.read_bytes())})
        evidence = self.put(self.archive, "logs/subtitle_quality/verified_aliases.json", tool.json_bytes({"synthetic": True}))
        alias = {ID: {"variants": variants, "evidence_path": str(evidence.relative_to(self.archive)), "evidence_sha256": tool.digest(evidence.read_bytes()),
                       "selected_source": self.record["source"], "selected_source_sha256": self.source_hash}}
        self.run_build(apply=True, aliases=alias)
        data = json.loads((self.output / f"raw/youtube-{ID}.json").read_bytes())
        self.assertEqual(len(data["visibility_snapshot"]["quality_physical_records"]), 2)

    def test_alias_wrong_folder_scope_rejected(self):
        self.put(self.archive, "logs/subtitle_quality/subtitle_quality.json", tool.json_bytes({"records": [self.quality_row, self.quality_row]}))
        self.inventory_data["inputs"] = self.input_hashes(); self.save_inventory()
        evidence = self.put(self.archive, "logs/subtitle_quality/verified_aliases.json", b"{}")
        info = self.put(self.archive, "archive/unrelated/identity.info.json", b"{}")
        media = self.put(self.archive, "archive/unrelated/media.m4a", b"fixture")
        alias = {ID: {"variants": [{"folder": "archive/unrelated", "info_path": str(info.relative_to(self.archive)),
                                    "info_sha256": tool.digest(info.read_bytes()), "media_path": str(media.relative_to(self.archive)),
                                    "media_sha256": tool.digest(media.read_bytes())}],
                       "evidence_path": str(evidence.relative_to(self.archive)), "evidence_sha256": tool.digest(evidence.read_bytes()),
                       "selected_source": self.record["source"], "selected_source_sha256": self.source_hash}}
        with self.assertRaisesRegex(ValueError, "quality_identity_conflict"):
            self.run_build(aliases=alias)


if __name__ == "__main__":
    unittest.main()
