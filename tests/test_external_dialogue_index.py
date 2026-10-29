"""Synthetic-only regression for participant labels across appearance editions."""
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import build_index


class ExternalDialogueIndexTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.root = Path(self.directory.name)
        for folder in ("config", "catalog", "corpus/dialogues"):
            (self.root / folder).mkdir(parents=True)
        self.ids = ("dialogue-synthetic-first", "dialogue-synthetic-second")
        self.records = []
        for i, identity in enumerate(self.ids):
            path = f"corpus/dialogues/{identity}.json"
            data = {"id": identity, "title": f"Synthetic edition {i}", "published_at": "2026-10-29",
                    "source_url": f"https://example.org/edition/{i}", "quality": {"unresolved_count": 0},
                    "license": build_index.REFERENCE_USE}
            (self.root / path).write_text(json.dumps(data), encoding="utf-8")
            self.records.append({"corpus_path": path})
        (self.root / "config/public-dialogue-policy.json").write_text(
            json.dumps({"records": self.records}), encoding="utf-8")
        self.appearance = {"id": "appearance-synthetic", "participants": [
            {"speaker_id": "yuzheng", "speaker_name": "Synthetic guest"},
            {"speaker_id": "host:synthetic", "speaker_name": "Synthetic host"}]}

    def tearDown(self):
        self.directory.cleanup()

    def write_appearances(self, rows):
        (self.root / "catalog/guest-appearances.jsonl").write_text(
            "\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")

    def assert_edition_participants(self, page):
        for i in range(2):
            line = next(line for line in page.splitlines() if f"Synthetic edition {i}" in line)
            self.assertIn("Synthetic guest；Synthetic host", line)
            self.assertNotIn("目录未列姓名", line)

    def test_top_level_and_all_source_versions_share_participant_labels(self):
        self.appearance.update(transcript_id=self.ids[0], transcript_path=self.records[0]["corpus_path"],
                               source_versions=[{"transcript_id": self.ids[1]}])
        self.write_appearances([self.appearance])
        self.assert_edition_participants(build_index.dialogue_page(self.root))

    def test_version_only_bindings_display_participants(self):
        self.appearance["source_versions"] = [{"transcript_id": identity} for identity in self.ids]
        self.write_appearances([self.appearance])
        self.assert_edition_participants(build_index.dialogue_page(self.root))

    def test_page_uses_canonical_conflict_check_for_version_bindings(self):
        self.appearance["source_versions"] = [{"transcript_id": self.ids[0]}]
        other = {**self.appearance, "id": "appearance-different"}
        self.write_appearances([self.appearance, other])
        with self.assertRaisesRegex(ValueError, "appearance_transcript_appearance_conflict"):
            build_index.dialogue_page(self.root)


if __name__ == "__main__":
    unittest.main()
