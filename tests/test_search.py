from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "search.py"
SPEC = importlib.util.spec_from_file_location("search", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class SearchTests(unittest.TestCase):
    def test_long_context_is_split_on_sections(self):
        body = "简介\n\n## 第一节\n\n内容甲\n\n## 第二节\n\n内容乙"
        chunks = MODULE.chunk_markdown(body, "context")
        self.assertEqual([section for section, _ in chunks], ["", "第一节", "第二节"])

    def test_context_filter_includes_book_framework(self):
        doc = MODULE.Document(
            id="book#chunk-1",
            source_id="book",
            title="书",
            section="框架",
            source_type="book-framework",
            source_url="",
            published_at="",
            text="内容",
            path="context/book.md",
        )
        self.assertTrue(MODULE.type_matches(doc, "context"))

    def test_community_filter_includes_posts_comments_and_knowledge_bank(self):
        for source_type in ("community-post", "community-comment", "knowledge-bank"):
            doc = MODULE.Document(
                id=source_type,
                source_id=source_type,
                title="标题",
                section="",
                source_type=source_type,
                source_url="",
                published_at="",
                text="内容",
                path="sample.md",
            )
            self.assertTrue(MODULE.type_matches(doc, "community"))

    def test_comment_filter_is_narrow(self):
        comment = MODULE.Document(
            id="comment",
            source_id="comment",
            title="评论",
            section="",
            source_type="community-comment",
            source_url="",
            published_at="",
            text="内容",
            path="sample.md",
        )
        self.assertTrue(MODULE.type_matches(comment, "comment"))
        self.assertFalse(MODULE.type_matches(comment, "knowledge-bank"))

    def test_open_license_filter_keeps_only_freely_reusable_material(self):
        def doc(source_type, license):
            return MODULE.Document(id=source_type, source_id=source_type, title="标题", section="", source_type=source_type,
                                   source_url="", published_at="", text="内容", path="sample.md", license=license)
        self.assertTrue(MODULE.license_matches(doc("community-post", "CC-BY-4.0"), "open"))
        self.assertTrue(MODULE.license_matches(doc("video-catalog", ""), "open"))
        self.assertFalse(MODULE.license_matches(doc("course-lesson", "LicenseRef-Lizheng-Reference-Use-1.0"), "open"))
        self.assertFalse(MODULE.license_matches(doc("english-community", "LicenseRef-Original-Rights-Retained"), "open"))
        self.assertTrue(MODULE.license_matches(doc("course-lesson", "LicenseRef-Lizheng-Reference-Use-1.0"), "all"))
        self.assertTrue(MODULE.type_matches(doc("course-lesson", ""), "course"))

if __name__ == "__main__":
    unittest.main()
