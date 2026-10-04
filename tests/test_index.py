import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import build_index


def catalog(name):
    return [json.loads(line) for line in (ROOT / f"catalog/{name}.jsonl").read_text().splitlines() if line.strip()]


class IndexTests(unittest.TestCase):
    def test_committed_pages_are_current(self):
        errors = []
        build_index.validate(errors)
        self.assertEqual(errors, [])

    def test_course_page_lists_every_lesson_once_in_course_order(self):
        page = build_index.course_page(ROOT)
        for row in catalog("course-lessons"):
            self.assertEqual(page.count(f"]({build_index.relative('index/x.md', row['corpus_path'])})"), 1, row["title"])
        order = [line.split("|")[1].strip() for line in page.splitlines() if line.startswith(("| 第", "| 宣导片"))]
        self.assertEqual(len(order), 23)
        self.assertEqual((order[0], order[1], order[-1]), ("宣导片", "第01课", "第21课"))
        self.assertEqual(order.index("第11课（上）") + 1, order.index("第11课（下）"))

    def test_course_map_names_real_lessons_and_framework_headings(self):
        course = json.loads((ROOT / "config/zhenbenshi-course-map.json").read_text())
        policy = json.loads((ROOT / "config/member-course-policy.json").read_text())
        lessons = {str(row["lesson_id"]) for row in policy["records"]}
        sections = {row["section_id"] for row in policy["records"]}
        headings = build_index.framework_headings(ROOT / "context/zhenbenshi-frameworks.md")
        self.assertEqual(len(headings), 7)
        self.assertEqual({section["id"] for section in course["sections"]}, sections)
        for lesson, frameworks in course["frameworks"].items():
            self.assertIn(lesson, lessons)
            for key in frameworks:
                self.assertIn(key, headings)

    def test_every_catalog_item_is_listed(self):
        pages = build_index.pages(ROOT)
        for name, page in (
            ("videos", "index/videos.md"), ("community-posts", "index/community-posts.md"),
            ("community-comments", "index/community-posts.md"), ("english-community", "index/english.md"),
            ("english-translations", "index/english.md"), ("knowledge-bank", "index/knowledge-bank.md"),
        ):
            for row in catalog(name):
                self.assertIn(f"({row['url']})", pages[page], f"{name}:{row['id']}")

    def test_every_full_text_file_is_linked_from_an_index_page(self):
        text = "\n".join(build_index.pages(ROOT).values())
        for path in sorted((ROOT / "corpus").rglob("*.md")):
            target = str(path.relative_to(ROOT))
            self.assertIn(build_index.relative("index/x.md", target), text, target)

    def test_table_cells_escape_markdown(self):
        self.assertEqual(build_index.cell("a|b [c] *d* <e>\n f"), "a\\|b \\[c\\] \\*d\\* \\<e\\> f")

    def test_anchors_follow_github(self):
        self.assertEqual(build_index.github_anchor("框架六：抓住10%的核心价值"), "框架六抓住10的核心价值")
        self.assertEqual(build_index.github_anchor("AI 整理与《真本事》框架"), "ai-整理与真本事框架")
        self.assertEqual(build_index.github_anchor("评论（10 条）"), "评论10-条")


if __name__ == "__main__":
    unittest.main()
