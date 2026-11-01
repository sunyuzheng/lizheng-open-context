import copy
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import ingest_published_captions as ingest
from dialogue_policy import validate_quality


class PublishedCaptionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        (self.root / "catalog").mkdir()
        (self.root / "catalog/guests.json").write_text(json.dumps({"sources":[{"source_id":"youtube-ABCDEFGHIJK","title":"Synthetic interview"}],
            "appearances":[{"source_id":"youtube-ABCDEFGHIJK","entity_id":"guest:synthetic"}]}))
        self.info = dict(id="ABCDEFGHIJK", title="Synthetic interview", channel_id=ingest.CHANNEL,
                         availability="public", is_live=False, live_status="not_live", upload_date="20261101", duration=20)
        self.raw = b"WEBVTT\n\n00:00:01.000 --> 00:00:03.000\nSynthetic speech.\n"

    def tearDown(self): self.temp.cleanup()

    def test_exact_native_captions_do_not_claim_text_or_audio_review(self):
        data, row = ingest.prepare(self.info,self.raw,self.root)
        validate_quality(data)
        self.assertEqual(data["units"][0]["text"],"Synthetic speech.")
        self.assertFalse(data["quality"]["human_audio_review"])
        self.assertEqual(data["units"][0]["speaker_id"],"unknown")
        self.assertNotIn("ai_text_processing_verified",data["quality"])
        data["units"][0]["text"] += " changed"
        with self.assertRaisesRegex(ValueError,"provenance"): validate_quality(data)

    def test_anonymous_identity_programme_and_timebase_are_required(self):
        for field,value in [("availability","unlisted"),("channel_id","other"),("is_live",True),("title","Other interview"),("duration",0)]:
            with self.subTest(field=field), self.assertRaises(ValueError):
                ingest.prepare(self.info | {field:value},self.raw,self.root)

    def test_rolling_asr_drops_repeated_history_but_keeps_new_words(self):
        text = ('WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nOld words\nNew<00:00:01.500><c> words</c>\n\n'
                '00:00:02.000 --> 00:00:02.010\nNew words\n')
        rows = ingest.captions(text,10,automatic=True)
        self.assertEqual([r["text"] for r in rows],["New words"])
        data,_ = ingest.prepare(self.info,text.encode(),self.root,automatic=True,language="en")
        self.assertEqual(data["transcript_quality"],"platform-auto-captions-unverified")
        validate_quality(data)


if __name__ == "__main__": unittest.main()
