import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from enrich_provenance import default_provenance, english_provenance
from export_public_corpus import video_publication_date
from import_english_translations import source_has_video_id


class ImportSourceTests(unittest.TestCase):
    def test_publishing_in_recording_space_does_not_prove_ai_authorship(self):
        meta = {"author": "AI", "source_type": "community-post", "community_space_slug": "recording", "source_url": "https://example.org/post"}
        actual = default_provenance(meta, "A short directory announcement")
        self.assertEqual(actual["author"], "Yuzheng Sun")
        self.assertEqual(actual["generation_method"], "not-established")

    def test_brand_account_does_not_become_original_author(self):
        record = {"body_html": "<p>A community article</p>", "author": "Superlinear Academy", "url": "https://example.org/post"}
        actual = english_provenance(record)
        self.assertEqual(actual["original_author"], "Unresolved original author")
        self.assertEqual(actual["yuzheng_stance_weight"], "not-evidence")

    def test_explicit_translation_notice_keeps_three_roles(self):
        record = {"body_html": '<p>Author: 立正 | Published 2026-04-01 | <a href="https://example.org/original">See original</a> | Translated by Superlinear Bot</p>', "author": "Superlinear Academy", "url": "https://example.org/english"}
        actual = english_provenance(record)
        self.assertEqual(actual["publisher"], "Superlinear Academy")
        self.assertEqual(actual["original_author"], "Yuzheng Sun")
        self.assertEqual(actual["generation_method"], "ai-translation")
        self.assertEqual(actual["source_family"], "https://example.org/original")

    def test_video_identity_must_be_full_path_component_suffix(self):
        identity = "abcdefghijk"
        self.assertTrue(source_has_video_id(Path("archive/title_abcdefghijk/source.zh.srt"), identity))
        self.assertTrue(source_has_video_id(Path("export/title_abcdefghijk.zh.srt"), identity))
        self.assertFalse(source_has_video_id(Path("archive/title_abcdefghijk_extra/source.srt"), identity))
        self.assertFalse(source_has_video_id(Path("archive/prefixabcdefghijksuffix/source.srt"), identity))

    def test_publication_fallback_uses_matching_platform_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            folder = Path(temporary)
            (folder / "wrong.info.json").write_text(json.dumps({"id": "other", "timestamp": 1}))
            (folder / "right.info.json").write_text(json.dumps({"id": "video", "timestamp": 1789656000}))
            self.assertEqual(video_publication_date({"video_id": "video"}, folder), "2026-09-17T14:40:00Z")
            self.assertEqual(video_publication_date({"video_id": "unknown", "upload_date": "20260915"}, folder), "2026-09-15")


if __name__ == "__main__":
    unittest.main()
