import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import import_chinese_editions as editions
import rights
import search
import validate_release as validator
from enrich_provenance import read_markdown

CHAPTER = "# 第1章　合成的一章\n\n> 对应原书Chapter 1: A synthetic chapter\n\n正文第一段。\n\n![图1-1　合成的图注](images/fig-01-01.png)\n\n后面的正文。\n"
POST = ("# 合成的博客文章\n\n- 原文标题：A synthetic post\n- 原文链接：https://www.statsig.com/blog/synthetic\n\n"
        "正文。\n\n![合成的图](images/synthetic/01.png)\n")


class ChineseEditionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        self.book = base / "book"
        (self.book / "chapters").mkdir(parents=True)
        (self.book / "chapters/00-about.md").write_text("# 关于这本书\n\n介绍。\n", encoding="utf-8")
        (self.book / "chapters/01.md").write_text(CHAPTER, encoding="utf-8")
        (self.book / "book.json").write_text(json.dumps({"front": "00-about.md", "chapters": [
            {"slug": "1", "file": "01.md", "label": "第1章", "title": "合成的一章", "original": "Chapter 1: A synthetic chapter"}]}), encoding="utf-8")
        self.blog = base / "blog"
        self.blog.mkdir()
        (self.blog / "20250101-synthetic.md").write_text(POST, encoding="utf-8")
        (self.blog / "manifest.json").write_text(json.dumps({"articles": [{
            "slug": "synthetic", "file": "20250101-synthetic.md", "url": "https://www.statsig.com/blog/synthetic",
            "title_zh": "合成的博客文章", "title_en": "A synthetic post", "published_date": "2025-01-01",
            "authors": [{"name": "Someone Else", "is_yuzheng": False}, {"name": "Yuzheng Sun, PhD", "is_yuzheng": True}]}]}), encoding="utf-8")
        self.root = base / "repo"
        (self.root / "catalog").mkdir(parents=True)

    def prepared(self, policy=None):
        return editions.prepare(self.book, self.blog, policy or editions.build_policy(self.book, self.blog), self.root)

    def test_imports_ai_rewrites_that_defer_to_the_english_originals(self):
        outputs = self.prepared()
        editions.apply_prepared(self.root, outputs)
        book_rows = outputs[editions.BOOK_CATALOG][1]
        self.assertEqual([row["id"] for row in book_rows], ["gdap-zh-about", "gdap-zh-ch01"])
        meta, body = read_markdown(self.root / book_rows[1]["corpus_path"])
        self.assertEqual((meta["author"], meta["publisher"], meta["original_author"]), ("AI", "Yuzheng Sun", editions.BOOK_AUTHORS))
        self.assertEqual((meta["content_origin"], meta["evidence_role"], meta["yuzheng_stance_weight"]), ("ai-translation", "translation", "verify-original"))
        self.assertEqual((meta["license"], meta["source_url"]), (rights.REFERENCE_USE, f"{editions.BOOK_SITE}/1"))
        self.assertIn("> 图1-1　合成的图注（图见在线版）", body)
        self.assertNotIn("![", body)
        self.assertIn("**中文版**", body)

    def test_a_co_written_post_keeps_both_authors_and_does_not_speak_for_yuzheng_alone(self):
        rows = self.prepared()[editions.BLOG_CATALOG][1]
        self.assertEqual(rows[0]["original_author"], "Someone Else, Yuzheng Sun")
        self.assertEqual(rows[0]["co_authors"], ["Someone Else"])
        self.assertIn("不能整篇当作立正一个人的立场", rows[0]["attribution_note"])
        self.assertEqual(rows[0]["url"], "https://www.statsig.com/blog/synthetic")

    def test_refuses_text_that_changed_after_review(self):
        policy = editions.build_policy(self.book, self.blog)
        (self.book / "chapters/01.md").write_text(CHAPTER + "新加的一句。\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "differs from the reviewed policy"):
            self.prepared(policy)

    def test_validation_holds_the_rewrites_to_reference_use_and_translation_weight(self):
        policy = editions.build_policy(self.book, self.blog)
        outputs = self.prepared(policy)
        book_rows, blog_rows = outputs[editions.BOOK_CATALOG][1], outputs[editions.BLOG_CATALOG][1]
        for field, value in (("license", "CC-BY-4.0"), ("yuzheng_stance_weight", "direct-with-quotation-boundaries"), ("author", "Yuzheng Sun")):
            errors = []
            validator.validate_chinese_editions([{**book_rows[0], field: value}, *book_rows[1:]], blog_rows, policy, errors)
            self.assertTrue(any(field in error for error in errors), field)

    def test_the_rights_map_names_the_original_publishers(self):
        outputs = self.prepared()
        editions.apply_prepared(self.root, outputs)
        book = outputs[editions.BOOK_CATALOG][1][0]["corpus_path"]
        blog = outputs[editions.BLOG_CATALOG][1][0]["corpus_path"]
        self.assertEqual(rights.file_rights(book, self.root), (rights.REFERENCE_USE, rights.BOOK_EDITION))
        self.assertEqual(rights.file_rights(blog, self.root), (rights.REFERENCE_USE, rights.BLOG_EDITIONS))

    def test_the_real_release_pins_every_text_and_search_can_filter_them(self):
        policy = json.loads((ROOT / "config/chinese-editions-policy.json").read_text(encoding="utf-8"))
        self.assertEqual(policy["authorization"], editions.AUTHORIZATION)
        documents = search.load_documents()
        self.assertTrue(any(search.type_matches(doc, "book") for doc in documents))
        self.assertTrue(any(search.type_matches(doc, "blog") for doc in documents))
        self.assertFalse(any(search.license_matches(doc, "open") for doc in documents if doc.source_type in {"book-chapter", "blog-post"}))


if __name__ == "__main__":
    unittest.main()
