import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
SPEC = importlib.util.spec_from_file_location("derive_catalogs", ROOT / "scripts/derive_catalogs.py")
derive = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(derive)


def entity(entity_id, display, aliases, entity_type="person", company=""):
    return {"entity_id": entity_id, "entity_type": entity_type, "display_name": display, "aliases": aliases,
            "guest_company": company}


CATALOG = {
    "schema_version": 1,
    "entities": [
        entity("guest:leo-a", "Leo（Charisma）", ["Leo", "Leo（Charisma）"]),
        entity("guest:leo-b", "Leo（The Union）", ["Leo", "Leo（The Union）"], company="Bar · Cafe"),
        entity("guest:pair", "王臻 & Nick", ["王臻 & Nick"], entity_type="group"),
        entity("guest:show", "Roast（Austin、Jesse）", ["Roast（Austin、Jesse）"], entity_type="group"),
        entity("guest:howie", "硅谷徐老师（Howie Xu）", ["硅谷徐老师（Howie Xu）", "Howie Xu"]),
    ],
    "sources": [
        {"source_id": "youtube-AAAAAAAAAAA", "video_id": "AAAAAAAAAAA", "title": "Current title A", "published_at": "2024-01-01T00:00:00Z"},
        {"source_id": "youtube-BBBBBBBBBBB", "video_id": "BBBBBBBBBBB", "title": "Current title B", "published_at": "2020-01-01T00:00:00Z"},
    ],
    "appearances": [
        {"entity_id": "guest:leo-a", "source_id": "youtube-AAAAAAAAAAA", "index": 7, "is_primary": True},
        {"entity_id": "guest:leo-a", "source_id": "youtube-BBBBBBBBBBB", "index": 0, "is_primary": False},
        {"entity_id": "guest:pair", "source_id": "youtube-AAAAAAAAAAA", "index": 3, "is_primary": True},
    ],
    "redirects": [],
}


class DerivedVideoTests(unittest.TestCase):
    def rows(self):
        return [
            {"id": "youtube-AAAAAAAAAAA", "video_id": "AAAAAAAAAAA", "title": "Old title A", "guest_names": ["Old name"],
             "transcript_included": False, "attribution_note": "Discovery metadata only."},
            {"id": "youtube-BBBBBBBBBBB", "video_id": "BBBBBBBBBBB", "title": "Title in the bound file",
             "guest_names": [], "transcript_included": True, "dialogue_path": "corpus/dialogues/youtube-BBBBBBBBBBB.json"},
            {"id": "youtube-CCCCCCCCCCC", "video_id": "CCCCCCCCCCC", "title": "Solo", "guest_names": ["Stale"],
             "transcript_included": False},
        ]

    def test_guest_names_titles_and_dialogue_paths_follow_their_owners(self):
        a, b, c = derive.derived_videos(self.rows(), CATALOG, {"AAAAAAAAAAA"})
        self.assertEqual(a["guest_names"], ["Leo（Charisma）", "王臻 & Nick"])
        self.assertEqual(a["title"], "Current title A")
        self.assertEqual(a["dialogue_path"], "corpus/dialogues/youtube-AAAAAAAAAAA.json")
        self.assertEqual(a["attribution_note"], derive.DIALOGUE_NOTE)
        # A full-text row keeps the title of its bound file; validation compares it with the catalog.
        self.assertEqual(b["title"], "Title in the bound file")
        self.assertNotIn("dialogue_path", b)
        self.assertEqual(b["guest_names"], ["Leo（Charisma）"])
        self.assertEqual(c["guest_names"], [])

    def test_appearances_are_numbered_from_the_earliest_programme(self):
        ordered = derive.ordered_appearances(CATALOG)["appearances"]
        by_pair = {(row["entity_id"], row["source_id"]): row["index"] for row in ordered}
        self.assertEqual(by_pair[("guest:leo-a", "youtube-BBBBBBBBBBB")], 0)
        self.assertEqual(by_pair[("guest:leo-a", "youtube-AAAAAAAAAAA")], 1)
        self.assertEqual(by_pair[("guest:pair", "youtube-AAAAAAAAAAA")], 0)


class NameTableTests(unittest.TestCase):
    def table(self):
        speakers = {"schema_version": 1, "speakers": [{"speaker_id": "yuzheng", "role": "host", "names": ["立正", "Yuzheng Sun"]}]}
        return derive.name_table(CATALOG, speakers)

    def test_key_rule_matches_its_examples(self):
        for text, key in derive.KEY_EXAMPLES:
            self.assertEqual(derive.name_key(text), key, text)

    def test_names_cover_base_names_members_and_labels(self):
        names = {row["key"]: row for row in self.table()["names"]}
        self.assertEqual(names["leo"]["entity_ids"], ["guest:leo-a", "guest:leo-b"])
        self.assertEqual(names["硅谷徐老师"]["entity_ids"], ["guest:howie"])
        self.assertIn("base", names["硅谷徐老师"]["kinds"])
        for member in ("王臻", "nick", "austin", "jesse"):
            self.assertIn("member", names[member]["kinds"], member)
        self.assertEqual(names["charisma"]["entity_ids"], ["guest:leo-a"])
        # A parenthetical that is already an alias is a name, not a qualifier.
        self.assertNotIn("guest:howie", self.table()["qualifiers"])

    def test_qualifiers_and_speakers(self):
        table = self.table()
        self.assertEqual([row["key"] for row in table["qualifiers"]["guest:leo-a"]], ["charisma"])
        self.assertEqual([row["key"] for row in table["qualifiers"]["guest:leo-b"]], ["theunion", "bar", "cafe"])
        self.assertEqual(table["speakers"][0]["speaker_id"], "yuzheng")
        self.assertEqual([row["key"] for row in table["speakers"][0]["names"]], ["立正", "yuzhengsun"])
        # Company names tell namesakes apart but never become names that find a person.
        self.assertNotIn("bar", {row["key"] for row in table["names"]})
        self.assertEqual(table["key_drop"], "".join(sorted(derive.KEY_DROP - set(" \t\r\n\u3000"))))

    def test_a_label_shared_with_an_organization_finds_everyone_there(self):
        catalog = {**CATALOG, "entities": [*CATALOG["entities"],
                   entity("guest:lulu", "Lulu（Multi-FIRE）", ["Lulu"]), entity("guest:leon", "Leon", ["Leon"], company="Meta · Multi-FIRE")]}
        speakers = {"schema_version": 1, "speakers": [{"speaker_id": "yuzheng", "role": "host", "names": ["立正"]}]}
        names = {row["key"]: row for row in derive.name_table(catalog, speakers)["names"]}
        self.assertEqual(names["multifire"]["entity_ids"], ["guest:leon", "guest:lulu"])


class RepositoryTests(unittest.TestCase):
    def test_committed_derived_files_are_current(self):
        errors = []
        derive.validate(errors, ROOT)
        self.assertEqual(errors, [])

    def test_write_is_idempotent(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for relative in (derive.GUESTS, derive.VIDEOS, derive.SPEAKERS, derive.DIALOGUE_POLICY):
                (root / relative).parent.mkdir(parents=True, exist_ok=True)
                (root / relative).write_bytes((ROOT / relative).read_bytes())
            (root / derive.NAMES).write_text("{}", encoding="utf-8")
            self.assertEqual(derive.write(root), [derive.NAMES])
            self.assertEqual(derive.write(root), [])
            self.assertEqual(json.loads((root / derive.NAMES).read_text())["schema_version"], 1)


if __name__ == "__main__":
    unittest.main()
