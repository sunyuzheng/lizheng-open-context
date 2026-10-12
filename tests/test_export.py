from __future__ import annotations

import hashlib
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
    def test_guest_import_uses_explicit_relations_not_name_similarity(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "guests.json"
            path.write_text(json.dumps({"schema_version": 1,
                "entities": [{"entity_id": "person:a", "display_name": "Jo"}, {"entity_id": "person:b", "display_name": "John"}],
                "sources": [{"source_id": "s1", "video_id": "video-a"}, {"source_id": "s2", "video_id": "video-b"}],
                "appearances": [{"source_id": "s1", "entity_id": "person:a"}, {"source_id": "s2", "entity_id": "person:b"}]}))
            self.assertEqual(MODULE.load_guests(path), ({"video-a", "video-b"}, {"video-a": ["Jo"], "video-b": ["John"]}))
            path.write_text("[]")
            with self.assertRaises(ValueError): MODULE.load_guests(path)

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

    def test_comment_rules_leave_substance_to_the_review(self):
        space = {"id": 1, "name": "论坛", "slug": "posts", "is_private": False}
        valid = {"author": MODULE.YUZHENG_NAME, "space_slug": "posts", "post_name": "怎么学AI"}
        body = "先挑一个每周都要做的任务，用AI做完它，再看哪一步最省时间。"
        self.assertTrue(MODULE.comment_candidate(valid, space, body))
        # Course and membership business is no longer a rule: the review decides it.
        self.assertTrue(MODULE.comment_candidate(valid, space, body + "课程里也讲过这个顺序。"))
        self.assertFalse(MODULE.comment_candidate(valid, space, "谢谢分享"))
        self.assertFalse(MODULE.comment_candidate(valid, space, body + "细节加我微信聊。"))
        self.assertFalse(MODULE.comment_candidate(valid, space, body + "你刚被裁，先休息一下。"))
        self.assertFalse(MODULE.comment_candidate(valid, space, "“" + body))
        self.assertFalse(MODULE.comment_candidate({**valid, "post_name": "招聘：寻找新同事"}, space, body))
        self.assertFalse(MODULE.comment_candidate({**valid, "space_slug": "say-hello"}, {**space, "slug": "say-hello"}, body))
        self.assertTrue(MODULE.comment_candidate(valid, {**space, "is_private": True}, body))
        self.assertFalse(MODULE.comment_candidate(valid, {**space, "is_hidden": True}, body))
        self.assertFalse(MODULE.comment_candidate(valid, {**space, "name": "删除和归档", "slug": "1a40ca"}, body))
        self.assertFalse(MODULE.comment_candidate(valid, {}, body))

    def test_export_publishes_only_reviewed_substance(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            cache = root / "cache"
            (cache / "bodies").mkdir(parents=True)
            (root / "config").mkdir()
            spaces = [{"id": 1, "name": "论坛", "slug": "posts", "is_private": False},
                      {"id": 2, "name": "Main Community", "slug": "main", "is_private": True,
                       "url": "https://www.superlinear.academy/c/main"}]
            (cache / "spaces.json").write_text(json.dumps({"records": spaces}))
            # Single-comment HTML is cached only for some comments; the others use the search text.
            (cache / "bodies" / "001.json").write_text(json.dumps({"records": [
                {"id": "99", "author": MODULE.YUZHENG_NAME, "body_html": "<p>别的评论</p>"}]}))
            def comment(cid, text):
                return {"id": str(cid), "author": MODULE.YUZHENG_NAME, "body": text, "created_at": "2026-01-02T03:04:05Z",
                        "url": f"https://www.superlinear.academy/c/posts/p#comment_wrapper_{cid}", "post_id": "9",
                        "post_name": "怎么学AI", "space_id": "1", "space_slug": "posts"}
            advice = "@Ann Lee 先挑一个每周都要做的任务，用AI做完它，再看哪一步最省时间。"
            thanks = "谢谢你的分享，写得很认真，期待你后面的更新和更多的项目进展！"
            view = "复利来自重复做同一件难事，而不是每次换一个新方向。"
            member_thread = {**comment(13, view), "space_id": "2", "space_slug": "main", "post_name": "我该不该辞职创业",
                             "url": "https://www.superlinear.academy/c/main/gai-bu-gai-ci-zhi#comment_wrapper_13"}
            (cache / "comments.json").write_text(json.dumps({"records": [comment(11, advice), comment(12, thanks), member_thread]}))
            texts = {f"circle-comment-{cid}": MODULE.sanitize_first_party_text(text, comment=True)
                     for cid, text in ((11, advice), (12, thanks), (13, view))}
            sha = {key: hashlib.sha256(text.encode("utf-8")).hexdigest() for key, text in texts.items()}
            review = root / "review.json"
            review.write_text(json.dumps({"decisions": {
                "circle-comment-11": {"category": "advice", "text_sha256": sha["circle-comment-11"]},
                "circle-comment-12": {"category": "social", "text_sha256": sha["circle-comment-12"]},
                "circle-comment-13": {"category": "view", "text_sha256": sha["circle-comment-13"]}}}))
            previous = MODULE.ROOT
            MODULE.ROOT = root
            try:
                stats = MODULE.export_community_comments(cache / "comments.json", cache / "bodies", cache / "spaces.json",
                                                         {}, "2026-08-30", review_path=review)
                self.assertEqual((stats["candidates"], stats["included"], stats["left_out_by_review"]), (3, 2, {"social": 1}))
                rows = {json.loads(line)["id"]: json.loads(line)
                        for line in (root / "catalog/community-comments.jsonl").read_text().splitlines()}
                row = rows["circle-comment-11"]
                self.assertEqual((row["title"], row["review_category"]), ("在《怎么学AI》下的回复", "advice"))
                published = (root / row["corpus_path"]).read_text()
                self.assertIn("[社区成员] 先挑一个每周都要做的任务", published)
                self.assertNotIn("Ann Lee", published)
                # Another member's post in a members-only space: no title, no post address, only the space.
                member = rows["circle-comment-13"]
                self.assertEqual((member["title"], member["source_visibility"], member["url"]),
                                 ("会员讨论区的回复（2026-01-02）", "members-only", "https://www.superlinear.academy/c/main#comment-13"))
                self.assertNotIn("parent_post_title", member)
                published = (root / member["corpus_path"]).read_text()
                self.assertNotIn("辞职", published)
                self.assertNotIn("gai-bu-gai", published)
                # A comment whose text changed since its review is not published on an old decision.
                review.write_text(json.dumps({"decisions": {
                    "circle-comment-11": {"category": "advice", "text_sha256": "0" * 64},
                    "circle-comment-12": {"category": "social", "text_sha256": sha["circle-comment-12"]},
                    "circle-comment-13": {"category": "view", "text_sha256": sha["circle-comment-13"]}}}))
                with self.assertRaises(SystemExit):
                    MODULE.export_community_comments(cache / "comments.json", cache / "bodies", cache / "spaces.json",
                                                     {}, "2026-08-30", review_path=review)
            finally:
                MODULE.ROOT = previous

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
