import copy
import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

TOOL = Path(__file__).absolute().parents[1] / "scripts/validate_guest_catalog.py"
spec = importlib.util.spec_from_file_location("guest_validator", TOOL)
v = importlib.util.module_from_spec(spec); spec.loader.exec_module(v)


def fixture():
    source = {"source_id": "youtube-abcdefghijk", "video_id": "abcdefghijk", "source_type": "youtube", "url": "https://www.youtube.com/watch?v=abcdefghijk", "title": "Synthetic programme", "thumbnail_url": "https://example.org/image.jpg"}
    entity = {"entity_id": "guest:alpha", "entity_type": "person", "display_name": "Synthetic Alpha", "aliases": ["Alpha"], "slug": "alpha", "alias_slugs": ["alpha", "old-alpha"], "primary_source_id": source["source_id"], "thumbnail_url": source["thumbnail_url"]}
    c = {"schema_version": 1, "entities": [entity], "sources": [source], "appearances": [{"entity_id": entity["entity_id"], "source_id": source["source_id"], "index": 0, "is_primary": True}], "redirects": []}
    a = {"schema_version": 1, "articles": [{"id": "article-a", "entity_id": "guest:alpha", "original_guest_slug": "old-alpha", "title": "Synthetic article", "summary": "Synthetic summary", "url": "https://example.org/article", "source_ids": [source["source_id"]]}]}
    return c, a


class CatalogTests(unittest.TestCase):
    def test_valid_shared_programme_multiple_people(self):
        c, a = fixture(); e = copy.deepcopy(c["entities"][0]); e.update(entity_id="guest:beta", slug="beta", alias_slugs=["beta"], display_name="Beta")
        c["entities"].append(e); c["appearances"].append({**c["appearances"][0], "entity_id": "guest:beta"})
        self.assertEqual(v.validate_catalog(c, a)["appearances"], 2)

    def test_duplicate_entity_or_pair(self):
        for field in ("entities", "appearances", "sources"):
            c, a = fixture(); c[field].append(copy.deepcopy(c[field][0]))
            with self.assertRaises(ValueError): v.validate_catalog(c, a)

    def test_incomplete_relation(self):
        c, a = fixture(); c["appearances"] = []
        with self.assertRaisesRegex(ValueError, "coverage"): v.validate_catalog(c, a)

    def test_wrong_url_id(self):
        c, a = fixture(); c["sources"][0]["url"] = "https://www.youtube.com/watch?v=lmnopqrstuv"
        with self.assertRaisesRegex(ValueError, "url_id"): v.validate_catalog(c, a)

    def test_unknown_entity_article_resource(self):
        c, a = fixture(); a["articles"][0]["entity_id"] = "guest:missing"
        with self.assertRaisesRegex(ValueError, "entity"): v.validate_catalog(c, a)
        c, a = fixture(); c["entities"][0]["community_resources"] = [{"kind": "unknown", "title": "Fixture", "summary": "Fixture", "url": "https://example.org/a"}]
        with self.assertRaisesRegex(ValueError, "resource"): v.validate_catalog(c, a)

    def test_unique_primary(self):
        c, a = fixture()
        self.assertEqual(v.validate_catalog(c, a)["entities"], 1)
        c["appearances"][0]["is_primary"] = False
        with self.assertRaisesRegex(ValueError, "primary"): v.validate_catalog(c, a)

    def test_declared_circle_and_relative_image(self):
        c, a = fixture(); s = c["sources"][0]; old = s["source_id"]; s.update(source_id="https://community.example.org/c/sessions/fixture", url="https://community.example.org/c/sessions/fixture", source_type="circle", video_id=None, thumbnail_url="/guest-media/image.png")
        c["entities"][0]["primary_source_id"] = s["source_id"]; c["appearances"][0]["source_id"] = s["source_id"]; a["articles"][0]["source_ids"] = [s["source_id"]]
        self.assertEqual(v.validate_catalog(c, a)["sources"], 1)
        s["thumbnail_url"] = "/guest-media/../secret.png"
        with self.assertRaises(ValueError): v.validate_catalog(c, a)

    def test_legacy_http_social_preserved_only_link_field(self):
        c, a = fixture(); c["entities"][0]["xiaohongshu_url"] = "http://example.org/public-link"
        v.validate_catalog(c, a); c["sources"][0]["url"] = "http://www.youtube.com/watch?v=abcdefghijk"
        with self.assertRaises(ValueError): v.validate_catalog(c, a)

    def test_unknown_or_private_payload_fields_rejected(self):
        for key in ("source_profiles", "units", "identity_basis"):
            c, a = fixture(); c["entities"][0][key] = []
            with self.assertRaisesRegex(ValueError, "fields"): v.validate_catalog(c, a)

    def test_raw_speakers_bound_to_catalog_without_duplicate_names(self):
        c, _ = fixture(); raw = {"id": "youtube-abcdefghijk", "video_id": "abcdefghijk", "source_url": c["sources"][0]["url"], "units": [{"speaker_id": "unknown", "text": "Synthetic speech"}]}
        before = copy.deepcopy(raw); self.assertEqual(v.verify_raw_metadata(c, [raw]), 1); self.assertEqual(raw, before)
        raw["units"][0]["speaker_id"] = "guest:alpha"
        self.assertEqual(v.verify_raw_metadata(c, [raw]), 1)
        raw["units"][0]["speaker_id"] = "guest:unrelated"
        with self.assertRaisesRegex(ValueError, "speaker_programme"): v.verify_raw_metadata(c, [raw])
        raw["units"][0]["speaker_id"] = "unknown"
        for key in v.CATALOG_FIELDS:
            raw[key] = "Duplicated metadata"
            with self.assertRaisesRegex(ValueError, "duplicated"): v.verify_raw_metadata(c, [raw])
            raw.pop(key)

    def test_raw_hash_drift_paths_and_symlink(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve(); (root / "catalog").mkdir(); (root / "config").mkdir(); (root / "corpus").mkdir()
            c, a = fixture()
            for p, x in [("catalog/guests.json", c), ("catalog/guest-articles.json", a)]: (root / p).write_text(json.dumps(x))
            raw = b'{}'; (root / "corpus/raw.json").write_bytes(raw); sha = hashlib.sha256(raw).hexdigest()
            (root / "config/public-dialogue-policy.json").write_text(json.dumps({"records": [{"corpus_path": "corpus/raw.json", "sha256": sha}]}))
            (root / "release-manifest.json").write_text(json.dumps({"files": [{"path": "corpus/raw.json", "bytes": 2, "sha256": sha}]}))
            (root / "corpus/raw.json").write_bytes(b'[]')
            with self.assertRaisesRegex(ValueError, "hash"): v.validate_guest_catalog(root)
            with self.assertRaises(ValueError): v.safe_file(root, "../escape")
            (root / "linked").symlink_to(root / "corpus", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "symlink"): v.safe_file(root, "linked/raw.json")

    def test_duplicate_json_key_and_false_boolean_schema(self):
        with self.assertRaisesRegex(ValueError, "duplicate"): v.strict_json('{"a":1,"a":2}')
        c, a = fixture(); c["schema_version"] = True
        with self.assertRaises(ValueError): v.validate_catalog(c, a)

    def test_manifest_generation_checks_new_policy_then_verifies_release(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td).resolve()
            for name in ("catalog", "config", "corpus"):
                (root / name).mkdir()
            c, a = fixture()
            raw = json.dumps({"id": "youtube-abcdefghijk", "video_id": "abcdefghijk", "source_url": c["sources"][0]["url"], "units": [{"speaker_id": "unknown"}]}).encode()
            for p, x in [("catalog/guests.json", c), ("catalog/guest-articles.json", a)]:
                (root / p).write_text(json.dumps(x))
            (root / "corpus/raw.json").write_bytes(raw)
            binding = {"corpus_path": "corpus/raw.json", "video_id": "abcdefghijk", "sha256": hashlib.sha256(raw).hexdigest()}
            (root / "config/public-dialogue-policy.json").write_text(json.dumps({"records": [binding]}))
            (root / "release-manifest.json").write_text(json.dumps({"files": [{"path": "corpus/raw.json", "bytes": 1, "sha256": "old"}]}))
            self.assertEqual(v.validate_guest_catalog(root, verify_manifest=False)["public_raw_records"], 1)
            with self.assertRaisesRegex(ValueError, "hash"):
                v.validate_guest_catalog(root)
            (root / "corpus/raw.json").write_bytes(raw + b' ')
            with self.assertRaisesRegex(ValueError, "hash"):
                v.validate_guest_catalog(root, verify_manifest=False)


if __name__ == "__main__": unittest.main()
