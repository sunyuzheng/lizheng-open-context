from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "export_public_corpus.py"
SPEC = importlib.util.spec_from_file_location("export_public_corpus", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(MODULE)


class ExportTests(unittest.TestCase):
    def test_manual_original_language_wins_over_auto_translation(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            valid = "1\n00:00:00,000 --> 00:00:01,000\nfixture\n\n"
            for name in ("sample.zh.srt", "sample.en.srt"):
                (folder / name).write_text(valid)
            (folder / "sample.info.json").write_text(json.dumps({"language": "zh-Hant", "subtitles": {"zh": [{}]}, "automatic_captions": {"en": [{"url": "https://example.com/?tlang=en"}]}}))
            self.assertEqual(MODULE.choose_transcript_path(folder, "human").name, "sample.zh.srt")

    def test_broken_final_does_not_hide_valid_corrected(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            (folder / "sample.final.srt").write_text("1\n00:00:03,000 --> 00:00:03,000\nfixture\n\n")
            (folder / "sample.corrected.srt").write_text("1\n00:00:03,000 --> 00:00:04,000\nfixture\n\n")
            self.assertEqual(MODULE.choose_transcript_path(folder, "corrected").name, "sample.corrected.srt")

    def test_raw_original_transcript_wins_over_translated_auto_captions(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)
            valid = "1\n00:00:00,000 --> 00:00:01,000\nfixture\n\n"
            for name in ("sample.qwen.srt", "sample.zh.srt"):
                (folder / name).write_text(valid)
            (folder / "sample.info.json").write_text(json.dumps({"language": "en", "subtitles": {}, "automatic_captions": {"zh": [{"url": "https://example.com/?tlang=zh"}]}}))
            self.assertEqual(MODULE.choose_transcript_path(folder, "timed_unknown").name, "sample.qwen.srt")

    def test_caption_validation_rejects_empty_backward_and_malformed_cues(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.srt"
            for value in ("1\n00:00:01,000 --> 00:00:02,000\n\n", "1\n00:99:00,000 --> 00:99:01,000\nfixture\n", "1\n00:00:02,000 --> 00:00:03,000\nfixture\n\n2\n00:00:01,000 --> 00:00:02,000\nsecond\n"):
                path.write_text(value)
                self.assertFalse(MODULE.transcript_structure_valid(path))
                self.assertIsNone(MODULE.choose_transcript_path(path.parent, None))

    def test_html_conversion_keeps_structure_and_drops_unlabelled_image(self):
        source = '<h2>标题</h2><p>一段<strong>重要</strong>文字。</p><img src="secret.jpg"><ul><li>甲</li></ul>'
        result = MODULE.html_to_markdown(source)
        self.assertIn("## 标题", result)
        self.assertIn("**重要**", result)
        self.assertIn("- 甲", result)
        self.assertNotIn("secret.jpg", result)

    def test_timed_transcript_parser(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.srt"
            path.write_text(
                "1\n00:00:03,000 --> 00:00:05,000\n你好 <b>世界</b>\n\n"
                "2\n00:00:08,000 --> 00:00:09,000\n下一句\n",
                encoding="utf-8",
            )
            self.assertEqual(MODULE.parse_timed_transcript(path), [(3, "你好 世界"), (8, "下一句")])

    def test_video_filter_is_fail_closed(self):
        valid = {
            "youtube_privacy": "public",
            "content_class": "normal_video",
            "podcast_policy": "ready_public_normal",
            "local_status": "ok",
        }
        self.assertTrue(MODULE.eligible_video(valid))
        for key, invalid in (
            ("youtube_privacy", "private"),
            ("content_class", "member_only"),
            ("podcast_policy", "not_public"),
            ("local_status", "invalid"),
        ):
            candidate = dict(valid)
            candidate[key] = invalid
            self.assertFalse(MODULE.eligible_video(candidate))

    def test_video_transcript_requires_positive_allowlist(self):
        unreviewed = MODULE.classify_video_rights("abcdefghijk", "单人口播", set(), {}, set())
        self.assertEqual(unreviewed["rights_scope"], "metadata-only")
        approved = MODULE.classify_video_rights(
            "abcdefghijk", "单人口播", set(), {}, {"abcdefghijk"}
        )
        self.assertEqual(approved["speaker_classification"], "solo-yuzheng")
        self.assertEqual(approved["review_status"], "approved")

    def test_positive_allowlist_conflict_fails_closed(self):
        with self.assertRaises(ValueError):
            MODULE.classify_video_rights(
                "abcdefghijk",
                "嘉宾访谈",
                set(),
                {},
                {"abcdefghijk"},
            )

    def test_comment_sanitizer_removes_member_and_contact_context(self):
        source = (
            "@某位成员 这是一个足够长的判断。@Sample Member 也不应留下半个姓名。"
            "联系 foo@example.com 或 13812345678。"
            "详情 https://example.com/private 以及 "
            "https://www.superlinear.academy/c/main/example#comment_wrapper_1"
        )
        result = MODULE.sanitize_first_party_text(source, comment=True)
        self.assertNotIn("某位成员", result)
        self.assertNotIn("Sample", result)
        self.assertNotIn("Member", result)
        self.assertNotIn("foo@example.com", result)
        self.assertNotIn("13812345678", result)
        self.assertNotIn("https://example.com/private", result)
        self.assertNotIn("https://www.superlinear.academy/", result)
        self.assertNotIn("Maven.com", MODULE.sanitize_first_party_text("见 Maven.com", comment=True))

    def test_comment_html_redacts_structured_member_mentions(self):
        source = (
            '<p><a class="mention" href="https://www.superlinear.academy/u/example">'
            "@Sample Member</a> 这是正文。</p>"
        )
        result = MODULE.html_to_markdown(source, redact_member_links=True)
        self.assertEqual(result, "[社区成员] 这是正文。")
        self.assertNotIn("Sample", result)

    def test_first_party_sanitizer_removes_local_paths(self):
        source = "本地文件在 /Users/example/private/project/notes.md 和 C:\\Users\\example\\secret.txt"
        result = MODULE.sanitize_first_party_text(source)
        self.assertNotIn("/Users/", result)
        self.assertNotIn("C:\\Users\\", result)

    def test_comment_selection_prefers_substantive_discussion(self):
        valid = {
            "author": MODULE.YUZHENG_NAME,
            "space_slug": "ai-resources",
            "body": "这是一个可以独立理解的评论。" * 12,
        }
        self.assertTrue(MODULE.comment_is_included(valid))
        self.assertFalse(MODULE.comment_is_included({**valid, "body": "谢谢分享"}))
        self.assertFalse(
            MODULE.comment_is_included({**valid, "body": "这是微信群里的私人讨论。" * 12})
        )
        self.assertFalse(
            MODULE.comment_is_included({**valid, "body": "这是通过 DM 继续沟通的内容。" * 12})
        )
        self.assertFalse(
            MODULE.comment_is_included({**valid, "post_name": "招聘：寻找新同事"})
        )
        self.assertFalse(MODULE.comment_is_included({**valid, "space_slug": "say-hello"}))

    def test_archived_and_test_spaces_are_not_current_content(self):
        self.assertEqual(
            MODULE.post_content_status({"name": "删除和归档", "slug": "1a40ca"}),
            "archived",
        )
        self.assertEqual(
            MODULE.post_content_status({"name": "test posts", "slug": "test-posts"}),
            "test",
        )


if __name__ == "__main__":
    unittest.main()
