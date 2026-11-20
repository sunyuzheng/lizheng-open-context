import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import import_course_pages as pages
import validate_release as validator

HTML = """<html><body><main>
<section class="wrap hero"><h2><span class="phrase-lock">三门课，</span><span class="phrase-lock">到底学什么？</span></h2>
<p class="path-name"><span>01</span><strong>AI Coding</strong><em>跨过动手的门槛</em></p>
<p><span class="phrases">一个<wbr/>晚上<wbr/>上手。</span></p>
<blockquote class="review-quote"><p>学员的评价，不收。</p><cite>某位学员</cite></blockquote>
<p class="hero-next" data-next-masterclass><strong>下一场大师课</strong><span>11月6日</span></p>
<svg aria-hidden="true"><text>图标</text></svg>
</section>
<section id="faq"><details><summary><strong>怎样退款？</strong><span aria-hidden="true">+</span></summary>
<div class="faq-answer"><p>请联系 someone@example.com 。</p></div></details>
<dialog class="reimbursement-dialog"><p>申请模板，不收。</p></dialog></section>
</main></body></html>"""
PAGE = {"key": "synthetic", "sections": ["section.hero", "#faq"],
        "drop": [".review-quote", "[data-next-masterclass]", "blockquote", "cite"],
        "must_contain": ["AI Coding"], "must_not_contain": ["学员的评价"]}


class CoursePageExtractionTests(unittest.TestCase):
    def test_keeps_the_pages_own_words_and_leaves_out_others(self):
        text = pages.extract(HTML, PAGE)
        self.assertIn("## 三门课，到底学什么？", text)
        self.assertIn("01 · AI Coding · 跨过动手的门槛", text)
        self.assertIn("一个晚上上手。", text)
        self.assertIn("#### 怎样退款？", text)
        self.assertIn("请联系 （邮箱地址见原页面） 。", text)
        for absent in ("学员的评价", "某位学员", "下一场", "图标", "申请模板", "@"):
            self.assertNotIn(absent, text)

    def test_a_before_after_table_names_its_columns(self):
        html = """<html><body><section class="cd"><div class="change" role="table">
<div class="change-head" role="row"><span role="columnheader">练什么</span><span role="columnheader">以前</span><span role="columnheader">学完</span></div>
<div class="change-row" role="row"><h4 role="cell"><span>验收结果</span><span class="change-title">练习：报销单</span></h4>
<p class="change-before" role="cell"><span class="phrases">看到完成就交差。</span></p><p class="change-after" role="cell">核对总数。</p></div>
<div class="change-row" role="row"><h4 role="cell"><span>进阶</span></h4><p class="change-before" role="cell"></p><p class="change-after" role="cell">分得开数据。</p></div>
</div></section></body></html>"""
        text = pages.extract(html, {"key": "table", "sections": ["section.cd"], "chunk_at": ["h4"]})
        self.assertIn("## 验收结果 · 练习：报销单\n\n以前：看到完成就交差。\n\n学完：核对总数。", text)
        self.assertIn("## 进阶\n\n学完：分得开数据。", text)
        self.assertNotIn("练什么", text)

    def test_lines_of_one_sentence_join_without_a_separator(self):
        html = """<html><body><section class="road"><p class="stop-can"><span class="stop-line"><span class="phrase-lock">一步一步，</span><span class="phrase-lock">构建系统：</span></span><span class="stop-line"><span class="phrase-lock">有聪明的内核。</span></span></p>
<p class="fits"><b>天天写代码</b><span><span class="stop-line">决定水平的是架构。</span><span class="stop-line">你当管理者。</span></span></p></section></body></html>"""
        text = pages.extract(html, {"key": "lines", "sections": ["section.road"]})
        self.assertIn("一步一步，构建系统：有聪明的内核。", text)
        self.assertIn("天天写代码 · 决定水平的是架构。你当管理者。", text)

    def test_a_changed_page_fails_instead_of_guessing(self):
        with self.assertRaisesRegex(ValueError, "matches 0 parts"):
            pages.extract(HTML, {**PAGE, "sections": ["#pricing"]})
        with self.assertRaisesRegex(ValueError, "still contains"):
            pages.extract(HTML, {**PAGE, "drop": [], "must_not_contain": ["学员的评价"]})


class CoursePagePolicyTests(unittest.TestCase):
    def test_release_files_match_the_pinned_extracts(self):
        policy = json.loads((ROOT / "config/course-pages-policy.json").read_text(encoding="utf-8"))
        rows = validator.read_jsonl(ROOT / "catalog/course-pages.jsonl")
        errors = []
        validator.validate_course_pages(rows, policy, errors)
        self.assertEqual(errors, [])
        self.assertEqual(len(rows), len(policy["pages"]))
        for row in rows:
            self.assertEqual(row["content_origin"], "yuzheng-published-text")
            self.assertEqual(row["evidence_role"], "published-source")

    def test_an_edited_page_text_is_rejected(self):
        policy = json.loads((ROOT / "config/course-pages-policy.json").read_text(encoding="utf-8"))
        rows = validator.read_jsonl(ROOT / "catalog/course-pages.jsonl")
        tampered = json.loads(json.dumps(policy))
        tampered["pages"][0]["text_sha256"] = "0" * 64
        errors = []
        validator.validate_course_pages(rows, tampered, errors)
        self.assertTrue(any("differs from the pinned extract" in error for error in errors), errors)
        errors = []
        validator.validate_course_pages(rows, {**policy, "authorization": "someone-else"}, errors)
        self.assertEqual(errors, ["Course page policy lacks explicit maintainer authorization"])


if __name__ == "__main__":
    unittest.main()
