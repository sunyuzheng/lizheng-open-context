import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import import_member_course as course
import validate_release as validator
from enrich_provenance import read_markdown

HTML = "<p><strong>合成的第一章</strong></p><p>" + "合成的课程文字，用来测试导入。" * 60 + "</p>"
LESSON = dict(id=1, name="第01课｜合成课程", section_id=10, space_id=course.SPACE_ID, status="published",
              created_at="2025-03-01T00:00:00.000Z", body_html=HTML)


def policy(**changes):
    record = dict(lesson_id=1, section_id=10, title="第01课｜合成课程", published_at="2025-03-01T00:00:00.000Z",
                  text_sha256=hashlib.sha256(HTML.encode("utf-8")).hexdigest())
    record.update(changes)
    return dict(snapshot_at="2026-10-04", authorization=course.AUTHORIZATION, membership_url=course.COURSE_URL,
                course=dict(space_id=course.SPACE_ID, url=course.COURSE_URL), records=[record])


class MemberCourseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = (Path(self.temp.name) / "repo").resolve()
        (self.root / "catalog").mkdir(parents=True)
        self.export = Path(self.temp.name) / "export.json"
        self.export.write_text(json.dumps({"records": [LESSON]}, ensure_ascii=False))

    def test_imports_the_authorized_text_with_its_access_and_rights(self):
        writes, rows = course.prepare(self.export, policy(), self.root)
        course.apply_prepared(self.root, writes, rows)
        meta, body = read_markdown(self.root / rows[0]["corpus_path"])
        self.assertEqual(meta["source_type"], "course-lesson")
        self.assertEqual(meta["source_url"], f"{course.COURSE_URL}/sections/10/lessons/1")
        self.assertEqual((meta["source_visibility"], meta["text_access"], meta["membership_platform"]), ("members-only", "public", "superlinear"))
        self.assertEqual((meta["rights_scope"], meta["license"]), ("publisher-authorized-course-text", "LicenseRef-Original-Rights-Retained"))
        self.assertIn("**会员课程**", body)
        self.assertIn("合成的课程文字", body)
        errors = []
        validator.validate_member_course(rows[0], policy(), errors)
        self.assertEqual(errors, [])

    def test_refuses_text_or_titles_that_differ_from_the_authorization(self):
        with self.assertRaisesRegex(ValueError, "differs from the authorized snapshot"):
            course.prepare(self.export, policy(text_sha256="0" * 64), self.root)
        with self.assertRaisesRegex(ValueError, "differs from the reviewed policy"):
            course.prepare(self.export, policy(title="另一个标题"), self.root)

    def test_validation_rejects_an_open_license_or_a_lesson_outside_the_policy(self):
        writes, rows = course.prepare(self.export, policy(), self.root)
        errors = []
        validator.validate_member_course({**rows[0], "license": "CC-BY-4.0"}, policy(), errors)
        self.assertTrue(any("license" in error for error in errors))
        errors = []
        validator.validate_member_course({**rows[0], "lesson_id": 2}, policy(), errors)
        self.assertTrue(any("not in the explicit course text policy" in error for error in errors))

    def test_the_policy_names_exactly_the_23_lessons(self):
        live = course.load_policy()
        self.assertEqual(len(live["records"]), 23)
        self.assertTrue(all(row["title"] for row in live["records"]))


if __name__ == "__main__":
    unittest.main()
