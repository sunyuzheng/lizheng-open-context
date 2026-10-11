"""Synthetic local-pack verification only; no corpus or provider access."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location("local_dialogue_search", SCRIPTS / "search_dialogue_candidates.py")
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)

ID = "ABCDEFGHIJK"
HELD = "LMNOPQRSTUV"


class LocalDialogueSearchTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.base = Path(self.temp.name).resolve()
        self.owner = self.base / "B"
        self.archive = self.base / "kedaibiao-channel"
        self.pack = self.owner / ".source-cache/synthetic-pack"
        self.pack.mkdir(parents=True)
        self.archive.mkdir()
        self.source = self.archive / "archive/source.srt"
        self.source.parent.mkdir()
        self.source.write_bytes(b"synthetic input guard\n")
        self.relative = f"raw/youtube-{ID}.json"
        self.raw_path = self.pack / self.relative
        self.raw_path.parent.mkdir()
        self.raw_data = {"id": f"youtube-{ID}", "video_id": ID,
                         "units": [{"id": "synthetic-unit", "start_seconds": 1.0,
                                    "end_seconds": 2.0, "text": "synthetic fixture"}]}
        self.raw_path.write_bytes(self.encode(self.raw_data))
        self.manifest = {
            "purpose": "local-unapproved-dialogue-candidates",
            "publication_performed": False, "approval_pending": True,
            "archive_root": str(self.archive), "candidate_count": 2,
            "prepared_count": 1, "held_count": 1, "cue_count": 1,
            "records": [{"video_id": ID, "status": "prepared", "path": self.relative, "cue_count": 1},
                        {"video_id": HELD, "status": "held"}],
            "files": {self.relative: self.ref(self.raw_path)},
            "input_guards": {str(self.source): self.ref(self.source)},
        }
        self.receipt = {"status": "local-candidates-complete", "publication_performed": False,
                        "approval_pending": True}
        self.save_manifest()
        self.root_patch = patch.object(tool, "ROOT", self.owner)
        self.root_patch.start()

    def tearDown(self):
        self.root_patch.stop()
        self.temp.cleanup()

    @staticmethod
    def encode(data):
        return (json.dumps(data, sort_keys=True) + "\n").encode()

    def ref(self, path):
        raw = path.read_bytes()
        return {"sha256": tool.digest(raw), "bytes": len(raw)}

    def save_receipt(self):
        (self.pack / "receipt.json").write_bytes(self.encode(self.receipt))

    def save_manifest(self):
        raw = self.encode(self.manifest)
        (self.pack / "manifest.json").write_bytes(raw)
        self.receipt["manifest_sha256"] = tool.digest(raw)
        self.save_receipt()

    def rebind_raw(self):
        self.raw_path.write_bytes(self.encode(self.raw_data))
        self.manifest["files"][self.relative] = self.ref(self.raw_path)
        self.save_manifest()

    def test_valid_pack_and_held_coverage_read_only(self):
        before = {str(p): p.read_bytes() for p in self.base.rglob("*") if p.is_file()}
        with patch.object(tool, "load_candidates", side_effect=AssertionError("verification must not search")):
            self.assertEqual(tool.verify_pack(self.pack), self.manifest)
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.base.rglob("*") if p.is_file()})

    def test_receipt_manifest_hash_tamper_rejected(self):
        self.receipt["manifest_sha256"] = "0" * 64
        self.save_receipt()
        with self.assertRaisesRegex(ValueError, "local_pack_receipt_invalid"):
            tool.verify_pack(self.pack)

    def test_receipt_status_or_publication_boundary_tamper_rejected(self):
        for field, value in [("status", "partial"), ("publication_performed", True), ("approval_pending", False)]:
            with self.subTest(field=field):
                previous = self.receipt[field]
                self.receipt[field] = value
                self.save_receipt()
                with self.assertRaisesRegex(ValueError, "local_pack_receipt_invalid"):
                    tool.verify_pack(self.pack)
                self.receipt[field] = previous
        self.save_receipt()

    def test_raw_file_tamper_rejected(self):
        self.raw_path.write_bytes(self.raw_path.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "local_pack_file_changed"):
            tool.verify_pack(self.pack)

    def test_input_guard_tamper_rejected(self):
        self.source.write_bytes(b"changed synthetic input\n")
        with self.assertRaisesRegex(ValueError, "local_pack_input_changed"):
            tool.verify_pack(self.pack)

    def test_pack_path_traversal_and_outside_cache_rejected(self):
        for path in [self.owner / ".source-cache/../elsewhere", self.owner / "public-pack", self.base / "outside-pack"]:
            with self.subTest(path=path.name):
                with self.assertRaisesRegex(ValueError, "path_outside"):
                    tool.verify_pack(path)

    def test_manifest_record_path_traversal_rejected_before_file_read(self):
        self.manifest["records"][0]["path"] = "raw/../../outside.json"
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "local_pack_path_invalid"):
            tool.verify_pack(self.pack)

    def test_symlink_pack_rejected(self):
        linked = self.owner / ".source-cache/linked-pack"
        linked.symlink_to(self.pack, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink_not_allowed"):
            tool.verify_pack(linked)

    def test_symlink_manifest_or_raw_file_rejected(self):
        for path in [self.pack / "manifest.json", self.raw_path]:
            with self.subTest(path=path.name):
                original = path.read_bytes()
                target = self.base / (path.name + ".synthetic-target")
                target.write_bytes(original)
                path.unlink()
                path.symlink_to(target)
                with self.assertRaisesRegex(ValueError, "symlink_not_allowed"):
                    tool.verify_pack(self.pack)
                path.unlink()
                path.write_bytes(original)

    def test_symlink_input_guard_rejected(self):
        target = self.archive / "archive/other.srt"
        target.write_bytes(self.source.read_bytes())
        self.source.unlink()
        self.source.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink_not_allowed"):
            tool.verify_pack(self.pack)

    def test_input_path_outside_both_owners_rejected(self):
        outside = self.base / "outside.txt"
        outside.write_bytes(b"synthetic")
        self.manifest["input_guards"] = {str(outside): self.ref(outside)}
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "path_outside_owner"):
            tool.verify_pack(self.pack)

    def test_duplicate_or_malformed_identity_rejected(self):
        for identity in [ID, "invalid"]:
            with self.subTest(identity=identity):
                self.manifest["records"][1]["video_id"] = identity
                self.save_manifest()
                with self.assertRaisesRegex(ValueError, "local_pack_identity_invalid"):
                    tool.verify_pack(self.pack)

    def test_raw_video_or_document_identity_mismatch_rejected(self):
        for field, value in [("video_id", HELD), ("id", "youtube-" + HELD)]:
            with self.subTest(field=field):
                previous = self.raw_data[field]
                self.raw_data[field] = value
                self.rebind_raw()
                with self.assertRaisesRegex(ValueError, "local_pack_source_identity_invalid"):
                    tool.verify_pack(self.pack)
                self.raw_data[field] = previous

    def test_unit_count_mismatch_rejected(self):
        self.raw_data["units"] = []
        self.rebind_raw()
        with self.assertRaisesRegex(ValueError, "local_pack_cue_count_invalid"):
            tool.verify_pack(self.pack)

    def test_missing_or_extra_manifest_file_rejected(self):
        self.manifest["files"] = {}
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "local_pack_path_invalid"):
            tool.verify_pack(self.pack)
        self.manifest["files"] = {self.relative: self.ref(self.raw_path), "raw/unlisted.json": {"sha256": "0" * 64, "bytes": 0}}
        self.save_manifest()
        with self.assertRaisesRegex(ValueError, "local_pack_coverage_invalid"):
            tool.verify_pack(self.pack)

    def test_all_coverage_counters_match_actual_records(self):
        for field in ["candidate_count", "prepared_count", "held_count", "cue_count"]:
            with self.subTest(field=field):
                previous = self.manifest[field]
                self.manifest[field] += 1
                self.save_manifest()
                with self.assertRaisesRegex(ValueError, "local_pack_coverage_invalid"):
                    tool.verify_pack(self.pack)
                self.manifest[field] = previous


if __name__ == "__main__":
    unittest.main()
