from __future__ import annotations

import contextlib
import dataclasses
import importlib.util
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / filename)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


SEARCH = load_module("provenance_search", "search.py")
VALIDATOR = load_module("provenance_validator", "validate_release.py")


def source_meta(**updates) -> dict:
    result = {
        "id": "circle-1", "title": "Quantum context", "author": "Guest Author",
        "publisher": "Superlinear Academy", "original_author": "Guest Author",
        "source_type": "english-community", "source_url": "https://www.superlinear.academy/c/ai-resources-en/example",
        "published_at": "2026-04-01", "source_visibility": "public",
        "content_origin": "third-party-community", "generation_method": "not-established",
        "evidence_role": "community-reference", "yuzheng_stance_weight": "not-evidence",
        "attribution_note": "The speaker's experiences are not Yuzheng's biography.",
        "source_family": "https://example.org/original", "original_source_url": "https://example.org/original",
        "source_context": "Published community reference", "language": "en",
        "rights_scope": "third-party-reference", "license": "LicenseRef-Original-Rights-Retained",
    }
    result.update(updates)
    return result


def write_source(root: Path, relative: str, meta: dict, body: str = "# Quantum context\n\nText") -> Path:
    path = root / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    front = "---\n" + "\n".join(f"{key}: {json.dumps(value, ensure_ascii=False)}" for key, value in meta.items()) + "\n---\n\n"
    path.write_text(front + body, encoding="utf-8")
    return path


def catalog_row(meta: dict, relative: str) -> dict:
    row = dict(meta, url=meta["source_url"], corpus_path=relative, full_text_included=True)
    row.pop("source_url")
    return row


class SearchProvenanceTests(unittest.TestCase):
    def test_every_chunk_and_output_keeps_author_and_evidence_boundary(self):
        meta = source_meta()
        body = "<!-- provenance:start -->\n> uniqueattributiontoken\n<!-- provenance:end -->\n\n"
        body += "## First\n\nQuantum one.\n\n## Second\n\nQuantum two.\n\n## Third\n\nQuantum three."
        with tempfile.TemporaryDirectory() as directory, patch.object(SEARCH, "ROOT", Path(directory)):
            path = write_source(Path(directory), "corpus/english-community/one.md", meta, body)
            chunks = SEARCH.parse_markdown(path)
            self.assertEqual(len(chunks), 3)
            for chunk in chunks:
                for key in SEARCH.PROVENANCE_FIELDS:
                    if key in meta:
                        self.assertEqual(getattr(chunk, key), meta[key])
                self.assertNotIn("uniqueattributiontoken", chunk.text)
            results = SEARCH.search_documents(chunks, "Quantum")
            self.assertEqual(len(results), 1)
            result = json.loads(json.dumps(results))[0]
            for key in SEARCH.PROVENANCE_FIELDS:
                self.assertIn(key, result)
                if key in meta:
                    self.assertEqual(result[key], meta[key])
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                SEARCH.print_results(results)
            for key in SEARCH.PROVENANCE_FIELDS:
                self.assertIn(f"{key}:", output.getvalue())
            self.assertIn("not-evidence", output.getvalue())

    def test_original_translation_and_repost_are_one_evidence_family(self):
        base = SEARCH.Document(id="one", source_id="one", title="Quantum", section="", source_type="community-post", source_url="", published_at="2026-01-01", text="Quantum", path="one.md", source_family="https://example.org/original")
        translated = dataclasses.replace(base, id="two", source_id="two", source_type="video-translation", author="AI", language="en", yuzheng_stance_weight="verify-original")
        unrelated = dataclasses.replace(base, id="three", source_id="three", source_family="https://example.org/independent")
        results = SEARCH.search_documents([base, translated, unrelated], "Quantum", 8)
        self.assertEqual(len(results), 2)
        self.assertEqual(len({row["source_family"] for row in results}), 2)

    def test_relevance_score_does_not_turn_stance_into_ranking_weight(self):
        base = SEARCH.Document(id="one", source_id="one", title="Quantum", section="", source_type="community-post", source_url="", published_at="", text="Quantum", path="one.md", yuzheng_stance_weight="direct-with-quotation-boundaries")
        secondary = dataclasses.replace(base, source_type="context", author="AI", yuzheng_stance_weight="secondary-only")
        third_party = dataclasses.replace(base, source_type="english-community", author="Guest", yuzheng_stance_weight="not-evidence")
        scores = [SEARCH.score(doc, "Quantum", ["quantum"], {"quantum": 3}, 3, 7) for doc in (base, secondary, third_party)]
        self.assertEqual(scores[0], scores[1])
        self.assertEqual(scores[0], scores[2])

    def test_english_loader_indexes_translation_and_shared_first_party(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(SEARCH, "ROOT", Path(directory)):
            root = Path(directory)
            write_source(root, "corpus/english-translations/one.md", source_meta(id="translation", source_type="video-translation"))
            write_source(root, "corpus/community-posts/two.md", source_meta(id="shared", source_type="community-post"))
            documents = SEARCH.load_documents()
            self.assertEqual(len(documents), 2)
            self.assertTrue(all(SEARCH.type_matches(doc, "english") for doc in documents))
            self.assertTrue(SEARCH.type_matches(next(doc for doc in documents if doc.source_id == "translation"), "video"))

    def test_snapshot_date_is_not_invented_as_publication_date(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(SEARCH, "ROOT", Path(directory)):
            meta = source_meta(published_at=None, snapshot_at="2026-09-17")
            path = write_source(Path(directory), "context/draft.md", meta)
            result = SEARCH.search_documents(SEARCH.parse_markdown(path), "Quantum")[0]
            self.assertEqual(result["published_at"], "")
            self.assertEqual(result["snapshot_at"], "2026-09-17")


class ProvenanceValidationTests(unittest.TestCase):
    def test_ai_synthesis_cannot_be_promoted_to_direct_authority(self):
        meta = source_meta(author="AI", publisher="Yuzheng Sun", original_author="Cited sources", content_origin="ai-synthesis", generation_method="ai-written", evidence_role="secondary-synthesis", yuzheng_stance_weight="secondary-only", rights_scope="first-party", license="CC-BY-4.0")
        errors = []
        VALIDATOR.validate_provenance(meta, "sample", errors, full_text=True)
        self.assertEqual(errors, [])
        self.assertTrue(VALIDATOR.authorized_publisher_text(meta))
        for change in ({"author": "Yuzheng Sun"}, {"yuzheng_stance_weight": "direct-with-quotation-boundaries"}, {"evidence_role": "primary-speech"}):
            errors = []
            VALIDATOR.validate_provenance(dict(meta, **change), "sample", errors, full_text=True)
            self.assertTrue(any("AI synthesis" in error for error in errors))
        self.assertFalse(VALIDATOR.authorized_publisher_text(dict(meta, author="Someone Else")))

    def test_third_party_and_metadata_cannot_inherit_yuzheng_license_or_stance(self):
        errors = []
        VALIDATOR.validate_provenance(source_meta(license="CC-BY-4.0", yuzheng_stance_weight="direct-with-quotation-boundaries"), "guest", errors, full_text=True)
        self.assertTrue(any("original rights" in error for error in errors))
        self.assertTrue(any("stance" in error for error in errors))
        errors = []
        VALIDATOR.validate_provenance(source_meta(content_origin="metadata-only", rights_scope="metadata-only", evidence_role="primary-speech"), "metadata", errors, full_text=False)
        self.assertTrue(any("metadata-only source cannot" in error for error in errors))

    def test_catalog_detects_attribution_loss_mismatch_missing_and_orphan_files(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(VALIDATOR, "ROOT", Path(directory)):
            root = Path(directory)
            relative = "corpus/english-community/one.md"
            meta = source_meta()
            path = write_source(root, relative, meta)
            row = catalog_row(meta, relative)
            errors = []
            VALIDATOR.validate_catalog_bindings([("english", [row])], errors)
            self.assertEqual(errors, [])
            broken = dict(row)
            del broken["attribution_note"]
            broken["author"] = "Yuzheng Sun"
            errors = []
            VALIDATOR.validate_catalog_bindings([("english", [broken])], errors)
            self.assertTrue(any("missing provenance field attribution_note" in error for error in errors))
            self.assertTrue(any("catalog/file attribution mismatch for author" in error for error in errors))
            path.unlink()
            write_source(root, "corpus/english-community/orphan.md", source_meta(id="orphan"))
            errors = []
            VALIDATOR.validate_catalog_bindings([("english", [row])], errors)
            self.assertTrue(any("bound corpus file is missing" in error for error in errors))
            self.assertTrue(any("unexpected corpus file" in error for error in errors))

    def test_english_policy_requires_exact_ids_and_public_file_binding(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(VALIDATOR, "ROOT", Path(directory)):
            root = Path(directory)
            meta = source_meta()
            relative = "corpus/english-community/one.md"
            write_source(root, relative, meta)
            row = catalog_row(meta, relative)
            policy = {"included_post_ids": [1], "space_id": 2413136, "source_visibility": "public"}
            errors = []
            VALIDATOR.validate_english_sources([row], policy, errors)
            self.assertEqual(errors, [])
            errors = []
            VALIDATOR.validate_english_sources([row], dict(policy, included_post_ids=[1, 2]), errors)
            self.assertTrue(any("exact ID mismatch" in error for error in errors))
            write_source(root, relative, dict(meta, source_visibility="members-only"))
            errors = []
            VALIDATOR.validate_english_sources([row], policy, errors)
            self.assertTrue(any("not public" in error for error in errors))

    def test_ai_translation_requires_current_solo_source_and_generation_date(self):
        with tempfile.TemporaryDirectory() as directory, patch.object(VALIDATOR, "ROOT", Path(directory)):
            root = Path(directory)
            identity = "abcdefghijk"
            url = f"https://www.youtube.com/watch?v={identity}"
            meta = source_meta(id=f"youtube-{identity}-en-ai", author="AI", publisher="Yuzheng Sun", original_author="Yuzheng Sun", source_type="video-translation", source_video_id=identity, source_url=url, original_source_url=url, source_family=url, content_origin="ai-translation", generation_method="ai-translation", evidence_role="translation", yuzheng_stance_weight="verify-original", rights_scope="first-party-derivative", license="CC-BY-4.0", third_party_exclusions=True, generated_at="2026-04-19T12:00:00Z", translation_publication_status="repository-reading-aid-not-platform-publication")
            relative = "corpus/english-translations/one.md"
            write_source(root, relative, meta)
            row = catalog_row(meta, relative)
            videos = [{"video_id": identity, "transcript_included": True, "published_at": meta["published_at"]}]
            errors = []
            VALIDATOR.validate_provenance(row, "translation", errors, full_text=True)
            VALIDATOR.validate_translations([row], videos, {identity}, errors)
            self.assertEqual(errors, [])
            errors = []
            VALIDATOR.validate_translations([dict(row, generated_at=None)], videos, set(), errors)
            self.assertTrue(any("not an included allowlisted solo video" in error for error in errors))
            self.assertTrue(any("generation date" in error for error in errors))
            errors = []
            VALIDATOR.validate_translations([dict(row, published_at="2026-04-19")], videos, {identity}, errors)
            self.assertTrue(any("original video publication date" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
