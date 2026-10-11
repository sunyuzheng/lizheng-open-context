"""Synthetic attribution and raw/derived boundary regressions."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

spec = importlib.util.spec_from_file_location("dialogue_layer_search", Path(__file__).parents[1] / "scripts/search.py")
search = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = search
spec.loader.exec_module(search)


class DialogueLayerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.old = search.ROOT
        search.ROOT = self.root

    def tearDown(self):
        search.ROOT = self.old
        self.temp.cleanup()

    def markdown(self, text):
        path = self.root / "source.md"
        path.write_text(text)
        return path

    def test_reviewed_quote_does_not_inherit_ai_heading_or_background(self):
        path = self.markdown('''---
id: "episode-own"
source_type: "video-excerpt"
speaker_classification: "yuzheng-turns-reviewed"
content_origin: "yuzheng-spoken-source"
evidence_role: "primary-speech"
---
# Editorial introduction

## 00:00:20 AI-heading-token

[00:00:20](https://www.youtube.com/watch?v=ABCDEFGHIJK&t=20s) · 背景：AI-background-token

> exact first line
> exact second line
''')
        raw, derived = search.parse_markdown(path)
        self.assertEqual(raw.data_layer, "raw")
        self.assertEqual(raw.speaker_id, "yuzheng")
        self.assertIn("exact first line\nexact second line", raw.text)
        for marker in ["AI-heading-token", "AI-background-token", "Editorial introduction"]:
            self.assertNotIn(marker, raw.text)
        self.assertEqual(derived.data_layer, "derived")
        self.assertEqual(derived.author, "AI")
        self.assertEqual(derived.content_origin, "ai-synthesis")
        self.assertEqual(derived.speaker_id, "")
        self.assertIn("AI-heading-token", derived.text)
        self.assertNotIn("exact first line", derived.text)
        self.assertEqual(raw.fragment_id, derived.fragment_id)

    def test_transcript_intro_is_not_raw_speech(self):
        path = self.markdown('''---
id: "episode"
source_type: "video-transcript"
speaker_classification: "mixed-or-unresolved"
---
# AI introduction

> Editorial introduction

[00:00:01](https://www.youtube.com/watch?v=ABCDEFGHIJK&t=1s) speech one

[00:00:02](https://www.youtube.com/watch?v=ABCDEFGHIJK&t=2s) speech two
''')
        docs = search.parse_markdown(path)
        self.assertEqual(len(docs), 1)
        self.assertNotIn("introduction", docs[0].text)
        self.assertEqual(docs[0].speaker_id, "unknown")
        self.assertIn("speech one", docs[0].text)
        self.assertIn("speech two", docs[0].text)

    def structured(self, **overrides):
        data = dict(schema_version=1, data_layer="raw", id="youtube-ABCDEFGHIJK", title="Conversation",
                    source_url="https://www.youtube.com/watch?v=ABCDEFGHIJK", content_origin="mixed-or-unresolved-speech",
                    evidence_role="speaker-attributed-speech", units=[
                        dict(id="1", start_seconds=1.25, end_seconds=2.5, text="first speech", speaker_id="yuzheng", speaker_name="立正", speaker_status="reviewed-source-attribution"),
                        dict(id="2", start_seconds=2.5, end_seconds=4.5, text="other speech", speaker_id="guest", speaker_name="Guest", speaker_status="audio-anchor-reviewed"),
                        dict(id="3", start_seconds=4.5, end_seconds=6.5, text="unresolved speech", speaker_id="unknown", speaker_status="unresolved")])
        data.update(overrides)
        path = self.root / "raw.json"
        path.write_text(json.dumps(data))
        return path, data

    def test_chunks_never_merge_speakers_or_upgrade_unknown(self):
        path, _ = self.structured()
        docs = search.parse_raw_dialogue(path)
        self.assertEqual([doc.speaker_id for doc in docs], ["yuzheng", "guest", "unknown"])
        self.assertEqual([doc.text.split(") ", 1)[1] for doc in docs], ["first speech", "other speech", "unresolved speech"])
        self.assertEqual(docs[0].content_origin, "yuzheng-spoken-source")
        for doc in docs[1:]:
            self.assertEqual(doc.yuzheng_stance_weight, "not-evidence")
        self.assertTrue(all(doc.data_layer == "raw" for doc in docs))

    def test_no_derived_data_required_for_loading_or_search(self):
        path, _ = self.structured()
        documents = search.parse_raw_dialogue(path)
        results = search.search_documents(documents, "other speech")
        self.assertTrue(results)
        self.assertEqual(results[0]["data_layer"], "raw")
        self.assertEqual(results[0]["speaker_id"], "guest")

    def test_unreviewed_named_speaker_is_refused(self):
        path, data = self.structured()
        data["units"][1]["speaker_status"] = "model-guessed"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "Named raw speaker"):
            search.parse_raw_dialogue(path)

    def test_invalid_times_empty_speech_duplicate_cues_are_refused(self):
        for mutation in [dict(start_seconds=-1), dict(end_seconds=.1), dict(start_seconds=True), dict(text=""), dict(id="2")]:
            with self.subTest(mutation=mutation):
                path, data = self.structured()
                data["units"][0].update(mutation)
                path.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    search.parse_raw_dialogue(path)

    def test_ai_context_is_derived(self):
        path = self.markdown('---\nid: "context-1"\nsource_type: "context"\n---\nAI editorial content')
        self.assertEqual(search.parse_markdown(path)[0].data_layer, "derived")

    def test_marker_only_window_is_retained_in_raw_but_not_retrieved_as_speech(self):
        path, data = self.structured()
        data["units"][0].update(text="< No Speech >", speaker_id="unknown", speaker_name="", speaker_status="unresolved")
        path.write_text(json.dumps(data)); before = path.read_bytes()
        docs = search.parse_raw_dialogue(path)
        self.assertEqual(len(docs), 2)
        self.assertTrue(all("No Speech" not in doc.text for doc in docs))
        self.assertEqual(path.read_bytes(), before)
        self.assertEqual(len(json.loads(path.read_bytes())["units"]), 3)

    def test_structured_current_version_replaces_legacy_body_and_catalog(self):
        path, data = self.structured()
        folder = self.root / "corpus/dialogues"; folder.mkdir(parents=True)
        path.rename(folder / "youtube-ABCDEFGHIJK.json")
        legacy = self.root / "corpus/videos/legacy.md"; legacy.parent.mkdir(parents=True)
        legacy.write_text('---\nid: "youtube-ABCDEFGHIJK"\nsource_type: "video-transcript"\n---\nlegacy-only-body')
        catalog = self.root / "catalog/videos.jsonl"; catalog.parent.mkdir()
        catalog.write_text(json.dumps({"id": "youtube-ABCDEFGHIJK", "title": "Old catalog title"}) + '\n')
        docs = search.load_documents()
        self.assertEqual(len(docs), 3)
        self.assertTrue(all(doc.path.startswith("corpus/dialogues/") for doc in docs))
        self.assertNotIn("legacy-only-body", " ".join(doc.text for doc in docs))

    def test_distinct_participants_keep_one_common_source_family(self):
        path, _ = self.structured()
        results = search.search_documents(search.parse_raw_dialogue(path), "speech", 8)
        self.assertEqual({row["speaker_id"] for row in results}, {"yuzheng", "guest", "unknown"})
        self.assertEqual(len({row["source_family"] for row in results}), 1)

    def test_participant_metadata_is_searchable_without_assigning_unknown_speech(self):
        path, data = self.structured()
        data["participant_names"] = "目录中的合成人名"
        path.write_text(json.dumps(data, ensure_ascii=False))
        results = search.search_documents(search.parse_raw_dialogue(path), "目录中的合成人名", 8)
        self.assertEqual(len(results), 3)
        unknown = next(row for row in results if row["speaker_id"] == "unknown")
        self.assertEqual(unknown["speaker_name"], "")
        self.assertEqual(unknown["author"], "说话人待核")

    def test_unknown_dialogue_keeps_distinct_windows_with_one_evidence_family(self):
        path, data = self.structured()
        data["units"] = [dict(id=f"cue-{i}", start_seconds=i * 10, end_seconds=i * 10 + 5,
                              text=f"window {i} probe " + "x" * 2590,
                              speaker_id="unknown", speaker_status="unresolved") for i in range(1, 6)]
        path.write_text(json.dumps(data))
        docs = search.parse_raw_dialogue(path)
        results = search.search_documents(docs, "probe", 8)
        self.assertEqual(len(results), 3)
        self.assertEqual(len({r["fragment_id"] for r in results}), 3)
        self.assertEqual(len({r["source_family"] for r in results}), 1)
        self.assertTrue(all(r["speaker_id"] == "unknown" and r["yuzheng_stance_weight"] == "not-evidence" for r in results))

    def test_unknown_windows_refuse_duplicate_overlap_and_unmapped_edition(self):
        from dataclasses import replace
        path, _ = self.structured()
        doc = search.parse_raw_dialogue(path)[-1]
        doc.fragment_id = "episode#cue-10-cue-20"
        for other in [replace(doc), replace(doc, text="other probe", fragment_id="episode#cue-15-cue-25"),
                      replace(doc, text="other probe", fragment_id="episode#cue-30-cue-40", source_snapshot_sha256="different")]:
            self.assertTrue(search.raw_windows_overlap(doc, other))
        self.assertFalse(search.raw_windows_overlap(doc, replace(doc, text="other probe", fragment_id="episode#cue-30-cue-40")))
        doc.fragment_id = "episode#episode#cue-10-episode#cue-20"
        self.assertFalse(search.raw_windows_overlap(doc, replace(doc, text="other probe", fragment_id="episode#episode#cue-30-episode#cue-40")))
        self.assertTrue(search.raw_windows_overlap(doc, replace(doc, text="other probe", fragment_id="episode#episode#cue-15-episode#cue-25")))

    def test_identity_alias_discovery_does_not_change_turn_or_stance(self):
        path, data = self.structured()
        data.update(participant_names="Source name", participant_aliases=["合成别名"],
                    participant_entity_ids=["guest:synthetic"], participant_metadata_basis="programme metadata only")
        path.write_text(json.dumps(data, ensure_ascii=False))
        results = search.search_documents(search.parse_raw_dialogue(path), "合成别名", 8)
        self.assertEqual(len(results), 3)
        unknown = next(row for row in results if row["speaker_id"] == "unknown")
        self.assertEqual(unknown["participant_entity_ids"], "guest:synthetic")
        self.assertEqual(unknown["speaker_name"], "")
        self.assertEqual(unknown["yuzheng_stance_weight"], "not-evidence")

    def test_excerpt_without_quote_fails_closed(self):
        path = self.markdown('---\nsource_type: "video-excerpt"\n---\n## 00:00:01 heading\n\n[00:00:01](https://www.youtube.com/watch?v=ABCDEFGHIJK&t=1s) no quotation')
        with self.assertRaises(ValueError):
            search.parse_markdown(path)


if __name__ == "__main__":
    unittest.main()
