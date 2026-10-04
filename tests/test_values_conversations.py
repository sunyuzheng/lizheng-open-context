import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import import_values_conversations as conversations
import rights
import search
import validate_release as validator
from enrich_provenance import read_markdown

POLICY = json.loads((ROOT / conversations.POLICY).read_text(encoding="utf-8"))
EXCERPTS = [json.loads(line) for line in (ROOT / conversations.EXCERPT_CATALOG).read_text(encoding="utf-8").splitlines()]
VIDEOS = {row["video_id"]: row for row in map(json.loads, (ROOT / "catalog/videos.jsonl").read_text(encoding="utf-8").splitlines())}
NEW_CARDS = {"science-limits-open-mind", "oneness-and-fairness", "self-and-constructed-me", "define-your-own-meaning",
             "method-over-answers", "prove-less-understand-first", "subdue-the-mind-real-needs", "parenting-time-not-control"}


class ExcerptFidelityTests(unittest.TestCase):
    def check(self, path: Path, row: dict) -> list[str]:
        errors = []
        count = validator.validate_excerpt_quotes(path, row["video_id"], ROOT / row["source_transcript"], errors)
        return errors, count

    def test_every_released_quotation_matches_its_transcript_at_the_stated_moment(self):
        self.assertEqual(len(EXCERPTS), 12)
        for row in EXCERPTS:
            errors, count = self.check(ROOT / row["corpus_path"], row)
            self.assertEqual(errors, [], row["id"])
            self.assertEqual(count, row["excerpt_count"])
        self.assertEqual(sum(row["excerpt_count"] for row in EXCERPTS), 132)

    def edited(self, row: dict, old: str, new: str) -> Path:
        text = (ROOT / row["corpus_path"]).read_text(encoding="utf-8")
        self.assertIn(old, text)
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / Path(row["corpus_path"]).name
        path.write_text(text.replace(old, new, 1), encoding="utf-8")
        return path

    def test_a_changed_word_fails(self):
        row = next(row for row in EXCERPTS if row["video_id"] == "G1sQ5Yei2ug")
        errors, _ = self.check(self.edited(row, "科学能解释的东西很少", "科学能解释的东西很多"), row)
        self.assertTrue(any("does not match the transcript verbatim" in error for error in errors))

    def test_a_quotation_moved_to_another_moment_fails(self):
        row = next(row for row in EXCERPTS if row["video_id"] == "G1sQ5Yei2ug")
        path = self.edited(row, "## 00:08:53 只能赚认知内的钱\n\n[00:08:53](https://www.youtube.com/watch?v=G1sQ5Yei2ug&t=533s)",
                           "## 00:07:47 只能赚认知内的钱\n\n[00:07:47](https://www.youtube.com/watch?v=G1sQ5Yei2ug&t=467s)")
        errors, _ = self.check(path, row)
        self.assertTrue(any("different moment" in error for error in errors))

    def test_a_teaser_that_repeats_a_sentence_does_not_count_as_the_quotation(self):
        # The opening teaser of this video repeats the excerpted sentence much earlier.
        row = next(row for row in EXCERPTS if row["video_id"] == "u4DpfGx-9i0")
        errors, count = self.check(ROOT / row["corpus_path"], row)
        self.assertEqual((errors, count), ([], 3))

    def test_matching_ignores_punctuation_and_spacing_but_not_words(self):
        self.assertEqual(validator.quote_key("我觉得，科学 能解释的？"), validator.quote_key("我觉得科学能解释的"))
        self.assertNotEqual(validator.quote_key("能解释"), validator.quote_key("不能解释"))


class PolicyAndProvenanceTests(unittest.TestCase):
    def test_policy_pins_the_six_public_transcripts_and_the_twelve_excerpt_files(self):
        self.assertEqual(POLICY["authorization"], validator.VALUES_AUTHORIZATION)
        public = {item["video_id"] for item in POLICY["public_transcripts"]}
        self.assertEqual(public, {"VSX1wxueZPU", "CTcMvIZFQcw", "9LKJ8JdLtfI", "dlv97OHFnGY", "AqQ6HQXFueE", "u4DpfGx-9i0"})
        for identity in public:
            row = VIDEOS[identity]
            self.assertEqual((row["license"], row["speaker_classification"], row["yuzheng_stance_weight"]),
                             (rights.REFERENCE_USE, "mixed-or-unresolved", "not-evidence"))
            self.assertEqual((row["source_visibility"], row["evidence_role"]), ("public", "speaker-attributed-speech"))
            self.assertTrue(row["guest_names"])
        for item in POLICY["conversations"]:
            self.assertEqual(hashlib.sha256((ROOT / item["excerpt_path"]).read_bytes()).hexdigest(), item["excerpt_sha256"])

    def test_excerpts_are_his_own_speech_and_follow_their_source_license(self):
        for row in EXCERPTS:
            video = VIDEOS[row["video_id"]]
            self.assertEqual((row["author"], row["evidence_role"], row["source_type"]), ("Yuzheng Sun", "primary-speech", "video-excerpt"))
            member = video["source_visibility"] == "members-only"
            self.assertEqual(row["license"], rights.REFERENCE_USE if member else "CC-BY-4.0")
            self.assertEqual(row["source_transcript"], video["corpus_path"])
            meta, body = read_markdown(ROOT / row["corpus_path"])
            self.assertIn("不是立正的话", meta["attribution_note"])
            self.assertEqual(body.count("\n## "), row["excerpt_count"])

    def test_charisma_leo_is_a_different_guest_and_stays_metadata_only(self):
        for identity in ("bcWYOkDa66k", "PHIhRTl2HHs", "FBodpxppwfc", "UsMKU7qcywY"):
            self.assertFalse(VIDEOS[identity].get("transcript_included"))

    def test_search_reads_the_excerpts_as_their_own_type(self):
        documents = [doc for doc in search.load_documents() if doc.source_type == "video-excerpt"]
        self.assertEqual(len({doc.source_id for doc in documents}), 12)
        self.assertTrue(all(search.type_matches(doc, "excerpt") and search.type_matches(doc, "video") for doc in documents))
        self.assertTrue(all("youtube.com/watch?v=" in doc.source_url and "&t=" in doc.source_url for doc in documents if doc.section))


class OpeningNoteTests(unittest.TestCase):
    def test_every_conversation_transcript_names_its_guests_and_points_to_his_words(self):
        for item in POLICY["conversations"]:
            _, body = read_markdown(ROOT / item["source_transcript"])
            note = body.split(conversations.NOTE_START, 1)[1].split(conversations.NOTE_END, 1)[0]
            for name in item["guest_names"]:
                self.assertIn(POLICY["guests"][name]["display"], note)
            self.assertIn("不代表立正的观点", note)
            self.assertIn(Path(item["excerpt_path"]).name, note)
            # The note sits after the title and access notice, before the first timestamp.
            self.assertLess(body.index(conversations.NOTE_START), body.index("](https://www.youtube.com/watch?v=" + item["video_id"] + "&t="))

    def test_the_note_is_replaced_not_repeated_when_rerun(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        root = Path(folder.name)
        item = next(item for item in POLICY["conversations"] if item["video_id"] == "VSX1wxueZPU")
        target = root / item["source_transcript"]
        target.parent.mkdir(parents=True)
        target.write_text((ROOT / item["source_transcript"]).read_text(encoding="utf-8"), encoding="utf-8")
        policy = {**POLICY, "conversations": [item]}
        conversations.annotate(root, policy)
        conversations.annotate(root, policy)
        self.assertEqual(target.read_text(encoding="utf-8").count(conversations.NOTE_START), 1)
        self.assertEqual(target.read_text(encoding="utf-8"), (ROOT / item["source_transcript"]).read_text(encoding="utf-8"))


class ReasoningCardTests(unittest.TestCase):
    def test_new_value_cards_rest_on_his_own_words_not_on_whole_conversations(self):
        cards = {card["id"]: card for card in json.loads((ROOT / "context/decision-cards.json").read_text(encoding="utf-8"))["cards"]}
        self.assertLessEqual(NEW_CARDS, set(cards))
        for card_id in NEW_CARDS:
            for source in cards[card_id]["sources"]:
                meta, _ = read_markdown(ROOT / source["path"])
                self.assertNotEqual(meta["yuzheng_stance_weight"], "not-evidence", (card_id, source["path"]))
                self.assertNotIn(meta.get("content_origin"), {"ai-synthesis", "ai-translation"})


class ImportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        base = Path(self.temp.name)
        folder = base / "archive" / "有人工字幕" / "20210101_对话_AAAAAAAAAAA"
        folder.mkdir(parents=True)
        self.subtitle = folder / "对话.zh.srt"
        self.subtitle.write_text("1\n00:00:01,000 --> 00:00:03,000\n我们可以walk\\haway\n\n2\n00:00:04,000 --> 00:00:06,000\n嘉宾说的话\n", encoding="utf-8")
        self.root = base / "repo"
        (self.root / "catalog").mkdir(parents=True)
        (self.root / "corpus/videos").mkdir(parents=True)
        row = {"video_id": "AAAAAAAAAAA", "id": "youtube-AAAAAAAAAAA", "title": "一场合成的对话", "published_at": "2021-01-01T00:00:00Z",
               "url": "https://www.youtube.com/watch?v=AAAAAAAAAAA", "transcript_included": False}
        (self.root / "catalog/videos.jsonl").write_text(json.dumps(row, ensure_ascii=False) + "\n", encoding="utf-8")
        self.policy = {"reviewed_at": "2026-10-04", "public_transcripts": [{
            "video_id": "AAAAAAAAAAA", "title": "一场合成的对话", "published_at": "2021-01-01T00:00:00Z", "guest_names": ["嘉宾"],
            "transcript_source_kind": "youtube_human_subtitle", "transcript_sha256": hashlib.sha256(self.subtitle.read_bytes()).hexdigest()}]}

    def test_imports_a_pinned_public_conversation_as_mixed_speech(self):
        writes, rows = conversations.prepare_public(Path(self.temp.name) / "archive", self.policy, self.root)
        target, meta, body = writes[0]
        self.assertEqual(target.name, "20210101-AAAAAAAAAAA.md")
        self.assertEqual((meta["author"], meta["speaker_classification"], meta["yuzheng_stance_weight"]),
                         ("Yuzheng Sun; 嘉宾", "mixed-or-unresolved", "not-evidence"))
        self.assertEqual((meta["license"], meta["source_visibility"]), (rights.REFERENCE_USE, "public"))
        self.assertIn("我们可以walk away", body)
        self.assertTrue(rows[0]["transcript_included"])

    def test_refuses_a_subtitle_that_differs_from_the_reviewed_snapshot(self):
        self.policy["public_transcripts"][0]["transcript_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            conversations.prepare_public(Path(self.temp.name) / "archive", self.policy, self.root)


if __name__ == "__main__":
    unittest.main()
