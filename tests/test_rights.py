import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import rights
import validate_release as validator


class RightsTests(unittest.TestCase):
    def test_every_published_file_has_one_license_and_reuse_toml_is_current(self):
        errors = []
        mapping = rights.validate(validator.release_paths(), errors)
        self.assertEqual(errors, [])
        self.assertEqual(mapping["corpus/course-lessons/20250301-1883192.md"][0], rights.REFERENCE_USE)
        self.assertEqual(mapping["scripts/search.py"][0], "MIT")
        self.assertEqual(mapping["catalog/videos.jsonl"][0], "CC0-1.0")
        self.assertEqual(mapping["context/decision-cards.json"][0], "CC-BY-4.0")
        self.assertNotIn("LICENSE.md", mapping)

    def test_each_kind_of_material_keeps_its_license(self):
        by_folder = {}
        for path, (license, _) in rights.rights_map(validator.release_paths()).items():
            if path.startswith("corpus/"):
                by_folder.setdefault(path.split("/")[1], set()).add(license)
        self.assertEqual(by_folder["course-lessons"], {rights.REFERENCE_USE})
        self.assertEqual(by_folder["community-posts"], {"CC-BY-4.0"})
        self.assertEqual(by_folder["videos"], {"CC-BY-4.0", rights.REFERENCE_USE})
        self.assertEqual(by_folder["english-community"], {"CC-BY-4.0", rights.RETAINED})

    def test_guest_speech_is_never_assigned_to_yuzheng_alone(self):
        for path, (license, holder) in rights.rights_map(validator.release_paths()).items():
            if path.startswith("corpus/videos/") and license == rights.REFERENCE_USE:
                self.assertEqual(holder, rights.SPEAKERS)

    def test_manifest_records_each_file_license(self):
        manifest = json.loads((ROOT / "release-manifest.json").read_text())
        licenses = {row["path"]: row["license"] for row in manifest["files"]}
        self.assertIsNone(licenses["LICENSE.md"])
        self.assertEqual(licenses["corpus/course-lessons/20250301-1883192.md"], rights.REFERENCE_USE)
        self.assertEqual(sum(info["files"] for info in manifest["licenses"].values()),
                         sum(value is not None for value in licenses.values()) + 1)  # + the manifest itself

    def test_reuse_groups_uniform_folders_and_lists_mixed_ones(self):
        mapping = {
            "a/x.md": ("CC-BY-4.0", "Y"), "a/y.md": ("CC-BY-4.0", "Y"),
            "b/c/1.md": ("CC-BY-4.0", "Y"), "b/c/2.md": ("MIT", "M"),
            "b/d/1.md": ("MIT", "M"), "README.md": ("MIT", "M"),
        }
        groups = rights.annotation_groups(mapping)
        self.assertEqual(sorted(groups[("CC-BY-4.0", "Y")]), ["a/**", "b/c/1.md"])
        self.assertEqual(sorted(groups[("MIT", "M")]), ["README.md", "b/c/2.md", "b/d/**"])

    def test_validation_flags_unknown_licenses_missing_texts_and_stale_reuse(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "corpus/x").mkdir(parents=True)
            (root / "corpus/x/a.md").write_text('---\nlicense: "CC-BY-NC-4.0"\n---\n\nbody\n')
            (root / "scripts").mkdir()
            (root / "scripts/a.py").write_text("")
            (root / "LICENSES").mkdir()
            (root / "LICENSES/Unused.txt").write_text("x")
            errors = []
            rights.validate(["corpus/x/a.md", "scripts/a.py"], errors, root)
            joined = "\n".join(errors)
            self.assertIn("corpus/x/a.md: content must declare", joined)
            self.assertIn("LICENSES/MIT.txt: license text is missing", joined)
            self.assertIn("LICENSES/Unused.txt: license text is not used", joined)
            self.assertIn("REUSE.toml is stale", joined)


if __name__ == "__main__":
    unittest.main()
