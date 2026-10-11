"""Synthetic, offline published-source raw/derived boundary guards."""
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location(
    "synthetic_published_section_search",
    Path(__file__).parents[1] / "scripts/search.py",
)
search = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = search
SPEC.loader.exec_module(search)


class PublishedSectionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "pack"
        self.root.mkdir()
        self.previous_root = search.ROOT
        search.ROOT = self.root
        self.path = self.root / "corpus/community-posts/synthetic.md"
        self.path.parent.mkdir(parents=True)
        self.policy = self.root / "config/source-section-layers.json"
        self.policy.parent.mkdir()
        self.prefix = "Raw synthetic prefix.\n\n## Original section\n\nOriginal synthetic line.\n\n"
        self.derived = "## Classified section\n\nSynthetic editorial paragraph.\n"
        self.body = self.prefix + self.derived
        self.write_source()
        self.row = {
            "path": "corpus/community-posts/synthetic.md",
            "source_id": "synthetic-source",
            "source_sha256": self.source_hash(),
            "layer": "derived",
            "start_marker": "## Classified section",
            "writer": "AI",
            "content_origin": "ai-synthesis",
            "generation_method": "source-declared-ai-written",
            "classification_basis": "Synthetic explicit source declaration",
        }
        self.write_policy()

    def tearDown(self):
        search.ROOT = self.previous_root
        self.temp.cleanup()

    def write_source(self, source_id="synthetic-source", body=None):
        header = (
            f'---\nid: "{source_id}"\nsource_type: "community-post"\n'
            'author: "Synthetic publishing account"\npublisher: "Synthetic publisher"\n'
            'content_origin: "first-party-source"\nevidence_role: "primary-text"\n'
            'yuzheng_stance_weight: "primary"\n---\n'
        )
        self.path.write_text(header + (self.body if body is None else body), encoding="utf-8")

    def source_hash(self):
        return hashlib.sha256(self.path.read_bytes()).hexdigest()

    def write_policy(self, rows=None, **changes):
        self.row.update(changes)
        data = {"schema_version": 1, "records": [self.row] if rows is None else rows}
        self.policy.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")

    def parts(self, **meta_changes):
        meta = {"id": "synthetic-source", "source_snapshot_sha256": self.source_hash()}
        meta.update(meta_changes)
        return search.published_source_parts(self.path, meta, self.body)

    def test_explicit_boundary_preserves_entire_raw_prefix_and_derived_suffix(self):
        raw, derived = self.parts()
        self.assertEqual(raw, ("raw", self.prefix, {"data_layer": "raw"}))
        self.assertEqual(derived[0], "derived")
        self.assertEqual(derived[1], self.derived)
        self.assertEqual(raw[1] + derived[1], self.body)
        self.assertEqual(derived[2]["author"], "AI")
        self.assertEqual(derived[2]["speaker_status"], "not-speech")
        self.assertEqual(derived[2]["yuzheng_stance_weight"], "secondary-only")

    def test_document_chunks_keep_raw_author_and_derived_classification(self):
        docs = search.parse_markdown(self.path)
        raw = [doc for doc in docs if doc.data_layer == "raw"]
        derived = [doc for doc in docs if doc.data_layer == "derived"]
        self.assertTrue(raw and derived)
        self.assertTrue(all(doc.author == "Synthetic publishing account" for doc in raw))
        self.assertTrue(all(doc.author == "AI" and doc.speaker_status == "not-speech" for doc in derived))
        self.assertTrue(all(doc.content_origin == "ai-synthesis" for doc in derived))
        self.assertNotIn("Synthetic editorial paragraph", "\n".join(doc.text for doc in raw))
        self.assertNotIn("Raw synthetic prefix", "\n".join(doc.text for doc in derived))
        self.assertTrue(all(doc.source_snapshot_sha256 == self.source_hash() for doc in docs))

    def test_exact_archive_notice_is_not_raw_source_evidence(self):
        notice = ('> 原文：[Synthetic title](https://example.test/source) · 发布于 2026-01-01 · '
                  '原始空间公开可见。本文保留发表时语境；其中第三方引文、发言、链接与商标不随正文重新授权。')
        self.write_source(body=notice + '\n\n' + self.derived)
        raw = self.path.read_text().replace('source_type: "community-post"\n',
            'source_type: "community-post"\ntitle: "Synthetic title"\nsource_url: "https://example.test/source"\n'
            'published_at: "2026-01-01T00:00:00Z"\nsource_visibility: "public"\n')
        self.path.write_text(raw)
        self.write_policy(source_sha256=self.source_hash())
        before = self.path.read_bytes()
        docs = search.parse_markdown(self.path)
        self.assertEqual(len(docs), 1)
        self.assertEqual(docs[0].data_layer, 'derived')
        self.assertNotIn('原文：', docs[0].text)
        self.assertEqual(self.path.read_bytes(), before)

    def test_original_reference_line_is_preserved_without_exact_archive_notice(self):
        self.write_source(body='> 原文：a real original reference.\n\n' + self.derived)
        self.write_policy(source_sha256=self.source_hash())
        docs = search.parse_markdown(self.path)
        self.assertIn('a real original reference.', docs[0].text)
        self.assertEqual(docs[0].data_layer, 'raw')

    def test_unconfirmed_editorial_writer_is_not_inferred_to_be_ai(self):
        self.write_policy(writer="整理者（未确认）", content_origin="published-editorial-adaptation",
                          generation_method="source-declared-editorial-adaptation")
        derived = [doc for doc in search.parse_markdown(self.path) if doc.data_layer == "derived"]
        self.assertTrue(derived)
        self.assertTrue(all(doc.author == "整理者（未确认）" for doc in derived))
        self.assertTrue(all(doc.content_origin != "ai-synthesis" for doc in derived))

    def test_unknown_writer_cannot_borrow_ai_origin_triplet(self):
        self.write_policy(writer="Unconfirmed writer")
        with self.assertRaisesRegex(ValueError, "writer classification"):
            search.published_section_records(self.root)

    def test_whole_body_is_explicitly_derived_without_losing_source_text(self):
        self.row.pop("start_marker")
        self.write_policy(whole_body=True)
        parts = self.parts()
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0][0:2], ("derived", self.body))
        self.assertTrue(all(doc.data_layer == "derived" for doc in search.parse_markdown(self.path)))

    def test_source_byte_drift_is_rejected(self):
        self.path.write_bytes(self.path.read_bytes() + b"\n")
        with self.assertRaisesRegex(ValueError, "hash or identity changed"):
            search.validate_published_sections(self.root)

    def test_source_identity_drift_is_rejected_even_when_hash_is_repinned(self):
        self.write_source(source_id="another-source")
        self.write_policy(source_sha256=self.source_hash())
        with self.assertRaisesRegex(ValueError, "hash or identity changed"):
            search.validate_published_sections(self.root)

    def test_malformed_hash_or_missing_identity_is_rejected(self):
        for changes in ({"source_sha256": "0" * 63}, {"source_sha256": "G" * 64},
                        {"source_id": ""}, {"source_id": None}):
            with self.subTest(changes=changes):
                row = dict(self.row, **changes)
                self.write_policy(rows=[row])
                with self.assertRaisesRegex(ValueError, "identity is missing"):
                    search.published_section_records(self.root)

    def test_missing_classified_source_fails_closed_and_restores_root(self):
        self.path.unlink()
        previous = search.ROOT
        with self.assertRaisesRegex(ValueError, "source is missing"):
            search.validate_published_sections(self.root)
        self.assertIs(search.ROOT, previous)

    def test_duplicate_record_path_is_rejected(self):
        self.write_policy(rows=[self.row, dict(self.row)])
        with self.assertRaisesRegex(ValueError, "Duplicate or unsafe"):
            search.published_section_records(self.root)

    def test_path_traversal_hidden_paths_and_wrong_source_family_are_rejected(self):
        for relative in ("../outside.md", "corpus/community-posts/../outside.md",
                         "corpus/community-posts/.hidden.md", "corpus/videos/source.md",
                         "/corpus/community-posts/source.md", "corpus/community-posts/nested/source.md"):
            with self.subTest(relative=relative):
                self.write_policy(rows=[dict(self.row, path=relative)])
                with self.assertRaises(ValueError):
                    search.published_section_records(self.root)

    def test_policy_file_symlink_is_rejected(self):
        target = self.root / "policy-copy.json"
        self.policy.rename(target)
        self.policy.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            search.published_section_records(self.root)

    def test_policy_parent_symlink_is_rejected(self):
        external = Path(self.temp.name) / "external-config"
        self.policy.parent.rename(external)
        (self.root / "config").symlink_to(external, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            search.published_section_records(self.root)

    def test_source_file_symlink_is_rejected(self):
        target = self.root / "source-copy.md"
        self.path.rename(target)
        self.path.symlink_to(target)
        with self.assertRaisesRegex(ValueError, "symlink"):
            search.validate_published_sections(self.root)

    def test_source_parent_symlink_is_rejected(self):
        target = self.root / "posts-copy"
        self.path.parent.rename(target)
        (self.root / "corpus/community-posts").symlink_to(target, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            search.validate_published_sections(self.root)

    def test_missing_repeated_or_nonheading_boundary_is_rejected(self):
        for body in (self.prefix, self.body + self.derived, self.body.replace("## Classified section", "inline ## Classified section")):
            with self.subTest(body_length=len(body)):
                self.body = body
                self.write_source()
                self.write_policy(source_sha256=self.source_hash())
                with self.assertRaisesRegex(ValueError, "boundary changed"):
                    search.validate_published_sections(self.root)

    def test_marker_text_in_paragraph_does_not_create_an_extra_boundary(self):
        self.body = self.prefix + "Inline ## Classified section is not a boundary.\n\n" + self.derived
        self.write_source()
        self.write_policy(source_sha256=self.source_hash())
        raw, derived = self.parts()
        self.assertIn("Inline ## Classified section", raw[1])
        self.assertEqual(derived[1], self.derived)

    def test_ambiguous_marker_and_whole_body_settings_are_rejected(self):
        self.write_policy(whole_body=True)
        with self.assertRaisesRegex(ValueError, "boundary is not explicit"):
            search.published_section_records(self.root)

    def test_empty_explicit_whole_body_is_rejected(self):
        self.body = " \n\t\n"
        self.write_source()
        self.row.pop("start_marker")
        self.write_policy(whole_body=True, source_sha256=self.source_hash())
        with self.assertRaisesRegex(ValueError, "body is empty"):
            search.validate_published_sections(self.root)

    def test_missing_classification_basis_is_rejected(self):
        self.write_policy(classification_basis=" \n ")
        with self.assertRaisesRegex(ValueError, "lacks its source basis"):
            search.published_section_records(self.root)

    def test_unclassified_source_stays_raw_even_with_editorial_keywords(self):
        self.write_policy(rows=[])
        self.assertIsNone(self.parts())
        self.assertTrue(all(doc.data_layer == "raw" and doc.author != "AI"
                            for doc in search.parse_markdown(self.path)))

    def test_validation_is_read_only_and_restores_module_root(self):
        before = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        previous = search.ROOT
        search.validate_published_sections(self.root)
        after = {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)
        self.assertIs(search.ROOT, previous)

    def bounded_source(self, *, mixed_writer=False):
        marker = "Editorial [section] + (synthetic)"
        end = "Original publisher afterword"
        self.derived = marker + "\n\nSynthetic derived line.\n\n"
        self.suffix = end + "\n\nOriginal synthetic afterword.\n"
        self.body = self.prefix + self.derived + self.suffix
        self.write_source()
        changes = dict(start_marker=marker, end_marker=end, source_sha256=self.source_hash())
        if mixed_writer:
            changes.update(writer="AI与原发布者（逐段归属未核）",
                           content_origin="ai-synthesis-of-mixed-sources",
                           generation_method="source-declared-ai-with-editorial-notes")
        self.write_policy(**changes)
        return marker, end

    def test_literal_nonheading_start_marker_is_supported_without_end_marker(self):
        marker, _ = self.bounded_source()
        self.row.pop("end_marker")
        self.write_policy()
        raw, derived = self.parts()
        self.assertEqual(raw[1], self.prefix)
        self.assertEqual(derived[1], self.derived + self.suffix)
        self.assertTrue(derived[1].startswith(marker + "\n"))
        self.assertEqual(raw[1] + derived[1], self.body)

    def test_bounded_parts_cover_prefix_derived_and_suffix_exactly(self):
        self.bounded_source()
        raw, derived, tail = self.parts()
        self.assertEqual([part[0] for part in (raw, derived, tail)], ["raw", "derived", "raw-suffix"])
        self.assertEqual([part[1] for part in (raw, derived, tail)], [self.prefix, self.derived, self.suffix])
        self.assertEqual(tail[2], {"data_layer": "raw"})
        self.assertEqual("".join(part[1] for part in (raw, derived, tail)).encode(), self.body.encode())

    def test_original_afterword_retains_raw_author_instead_of_ai(self):
        self.bounded_source(mixed_writer=True)
        docs = search.parse_markdown(self.path)
        afterword = [doc for doc in docs if "#raw-suffix-chunk-" in doc.id]
        self.assertTrue(afterword)
        self.assertTrue(all(doc.data_layer == "raw" for doc in afterword))
        self.assertTrue(all(doc.author == "Synthetic publishing account" for doc in afterword))
        self.assertTrue(all(doc.evidence_role == "primary-text" for doc in afterword))
        self.assertTrue(all(doc.content_origin == "first-party-source" for doc in afterword))
        self.assertIn("Original synthetic afterword", "\n".join(doc.text for doc in afterword))

    def test_raw_prefix_and_suffix_chunk_identifiers_do_not_collide(self):
        self.bounded_source()
        docs = search.parse_markdown(self.path)
        ids = [doc.id for doc in docs]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(any("#raw-chunk-" in value for value in ids))
        self.assertTrue(any("#raw-suffix-chunk-" in value for value in ids))
        self.assertTrue(any("#derived-chunk-" in value for value in ids))
        self.assertEqual({doc.source_id for doc in docs}, {"synthetic-source"})

    def test_missing_end_marker_is_rejected(self):
        _, end = self.bounded_source()
        self.body = self.body.replace(end, "Another afterword", 1)
        self.write_source()
        self.write_policy(source_sha256=self.source_hash())
        with self.assertRaisesRegex(ValueError, "end boundary changed"):
            search.validate_published_sections(self.root)

    def test_duplicate_end_marker_is_rejected(self):
        _, end = self.bounded_source()
        self.body += "\n" + end + "\n"
        self.write_source()
        self.write_policy(source_sha256=self.source_hash())
        with self.assertRaisesRegex(ValueError, "end boundary changed"):
            search.validate_published_sections(self.root)

    def test_end_marker_before_start_is_rejected(self):
        _, end = self.bounded_source()
        self.body = end + "\n\n" + self.prefix + self.derived
        self.write_source()
        self.write_policy(source_sha256=self.source_hash())
        with self.assertRaisesRegex(ValueError, "end boundary changed"):
            search.validate_published_sections(self.root)

    def test_end_marker_equal_to_start_is_rejected(self):
        marker, _ = self.bounded_source()
        self.write_policy(end_marker=marker)
        with self.assertRaisesRegex(ValueError, "end boundary changed"):
            search.validate_published_sections(self.root)

    def test_end_marker_in_a_paragraph_is_not_an_exact_boundary(self):
        _, end = self.bounded_source()
        self.body = self.body.replace(end, "Inline " + end, 1)
        self.write_source()
        self.write_policy(source_sha256=self.source_hash())
        with self.assertRaisesRegex(ValueError, "end boundary changed"):
            search.validate_published_sections(self.root)

    def test_nonheading_start_marker_is_unique_and_full_line_only(self):
        marker, _ = self.bounded_source()
        original = self.body
        for body in (original + "\n" + marker + "\n", original.replace(marker, "Inline " + marker, 1)):
            with self.subTest(body_length=len(body)):
                self.body = body
                self.write_source()
                self.write_policy(source_sha256=self.source_hash())
                with self.assertRaisesRegex(ValueError, "boundary changed"):
                    search.validate_published_sections(self.root)

    def test_invalid_single_line_markers_and_whole_body_end_are_rejected(self):
        self.bounded_source()
        original = dict(self.row)
        for changes in ({"start_marker": "first\nsecond"}, {"end_marker": "first\nsecond"},
                        {"start_marker": " "}, {"end_marker": " "}, {"end_marker": 1},
                        {"start_marker": None, "whole_body": True}):
            with self.subTest(changes=changes):
                self.write_policy(rows=[dict(original, **changes)])
                with self.assertRaisesRegex(ValueError, "boundary is not explicit"):
                    search.published_section_records(self.root)

    def test_mixed_writer_is_secondary_only_and_never_own_stance(self):
        self.bounded_source(mixed_writer=True)
        derived = [doc for doc in search.parse_markdown(self.path) if doc.data_layer == "derived"]
        self.assertTrue(derived)
        self.assertTrue(all(doc.author == "AI与原发布者（逐段归属未核）" for doc in derived))
        self.assertTrue(all(doc.content_origin == "ai-synthesis-of-mixed-sources" for doc in derived))
        self.assertTrue(all(doc.generation_method == "source-declared-ai-with-editorial-notes" for doc in derived))
        self.assertTrue(all(doc.evidence_role == "secondary-synthesis" and doc.yuzheng_stance_weight == "secondary-only"
                            for doc in derived))
        self.assertTrue(all(doc.speaker_id == "" and doc.speaker_name == "" and doc.speaker_status == "not-speech"
                            for doc in derived))

    def test_mixed_writer_cannot_borrow_other_classification_triplets(self):
        self.bounded_source(mixed_writer=True)
        original = dict(self.row)
        for changes in ({"content_origin": "ai-synthesis"}, {"generation_method": "source-declared-ai-written"},
                        {"writer": "AI"}):
            with self.subTest(changes=changes):
                self.write_policy(rows=[dict(original, **changes)])
                with self.assertRaisesRegex(ValueError, "writer classification"):
                    search.published_section_records(self.root)


if __name__ == "__main__":
    unittest.main()
