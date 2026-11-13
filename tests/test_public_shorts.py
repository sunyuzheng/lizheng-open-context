"""Shorts admission is a caption snapshot, never inferred solo/interview speech."""
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import dialogue_policy as policy
import ingest_public_shorts as ingest
import raw_turn_policy as turns
import search

ID = "ABCDEFGHIJK"
DATE = "2026-11-12T12:00:00Z"


class PublicShortTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        (self.root / "config").mkdir()
        self.config = {"schema_version": 1, "authorization": policy.AUTHORIZATION, "scope": "public-dialogues-only",
                       "removal": "https://example.org/removal",
                       "rights_notice": "Guests retain rights in their own speech; inclusion does not establish Yuzheng's endorsement.",
                       "records": []}
        (self.root / "config/public-dialogue-policy.json").write_bytes(ingest.encode(self.config))
        self.info = {"id": ID, "title": "Synthetic public short", "channel_id": policy.CHANNEL,
                     "availability": "public", "is_live": False, "live_status": "not_live",
                     "upload_date": "20261112", "duration": 20,
                     "subtitles": {"zh": [{"ext": "vtt"}]}, "automatic_captions": {"en": [{"ext": "vtt"}]}}
        self.caption = b"1\n00:00:01,125 --> 00:00:03,250\nSynthetic one.\nSecond line.\n\n2\n00:00:03,200 --> 00:00:04,500\nSynthetic one.\n"
        self.listing = {"schema_version": 1, "channel_id": policy.CHANNEL,
                        "source_url": f"https://www.youtube.com/channel/{policy.CHANNEL}/shorts",
                        "verified_at": DATE, "video_ids": [ID]}

    def tearDown(self):
        self.temp.cleanup()

    def prepare(self, *, info=None, listing=None, caption=None, **kwargs):
        raw = self.caption if caption is None else caption
        return ingest.prepare(self.info if info is None else info, raw,
                              self.listing if listing is None else listing,
                              info_sha256="a" * 64, caption_sha256=hashlib.sha256(raw).hexdigest(),
                              listing_sha256="b" * 64, method=kwargs.pop("method", "publisher-captions"),
                              origin=kwargs.pop("origin", "platform"), **kwargs)

    def save(self, data, row):
        target = self.root / row["corpus_path"]
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(ingest.encode(data))
        row["sha256"] = hashlib.sha256(target.read_bytes()).hexdigest()
        self.config["records"] = [row]
        (self.root / "config/public-dialogue-policy.json").write_bytes(ingest.encode(self.config))

    def validate(self):
        errors = []
        stats = policy.validate_dialogues(self.root, set(), errors)
        return stats, errors

    def test_short_needs_no_guest_or_interview_and_keeps_exact_cues_unknown(self):
        data, row = self.prepare()
        self.assertEqual(row["programme_type"], "short")
        self.assertEqual(data["inclusion_authorization"], policy.SHORTS_AUTHORIZATION)
        self.assertEqual(data["units"][0]["text"], "Synthetic one.\nSecond line.")
        self.assertEqual((data["units"][0]["start_seconds"], data["units"][0]["end_seconds"]), (1.125, 3.25))
        self.assertEqual(len(data["units"]), 2)  # Repeated words and cross-cue overlap remain.
        self.assertFalse(data["quality"]["human_audio_review"])
        self.assertNotIn("ai_text_processing_verified", data["quality"])
        self.save(data, row)
        self.assertEqual(self.validate(), ({"structured_public_dialogues": 1, "structured_dialogue_cues": 2}, []))
        previous = search.ROOT
        search.ROOT = self.root
        try:
            docs = search.parse_raw_dialogue(self.root / row["corpus_path"])
        finally:
            search.ROOT = previous
        self.assertTrue(docs)
        self.assertTrue(all(d.speaker_id == "unknown" and d.yuzheng_stance_weight == "not-evidence" for d in docs))
        self.assertTrue(all(d.source_url.startswith(f"https://www.youtube.com/watch?v={ID}") for d in docs))

    def test_private_unlisted_live_upcoming_other_owner_and_bad_duration_rejected(self):
        for key, value in [("availability", "private"), ("availability", "unlisted"),
                           ("is_live", True), ("live_status", "is_upcoming"), ("channel_id", "other"),
                           ("duration", 0), ("duration", True), ("duration", float("inf"))]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                self.prepare(info=self.info | {key: value})

    def test_listing_presence_owner_and_column_are_bound(self):
        for patch in [{"video_ids": []}, {"channel_id": "other"}, {"source_url": "https://www.youtube.com/feed/subscriptions"},
                      {"verified_at": "2026-11-12"}, {"video_ids": [ID, ID]}]:
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.prepare(listing=self.listing | patch)

    def test_platform_auto_captions_keep_unverified_quality_and_rolling_rows(self):
        raw = b"WEBVTT\n\n00:00:01.000 --> 00:00:02.000\nOld words\nNew<00:00:01.500><c> words</c>\n\n00:00:02.000 --> 00:00:02.010\nNew words\n"
        data, row = self.prepare(caption=raw, method="platform-auto-captions", language="en")
        self.assertEqual([u["text"] for u in data["units"]], ["Old words\nNew words", "New words"])
        self.assertEqual(data["transcript_quality"], "platform-auto-captions-unverified")
        self.save(data, row)
        self.assertEqual(self.validate()[1], [])

    def test_local_script_is_not_evidence_of_published_captions(self):
        with self.assertRaisesRegex(ValueError, "track_required"):
            self.prepare(info=self.info | {"subtitles": {}})
        with self.assertRaisesRegex(ValueError, "receipt_required"):
            self.prepare(origin="uploaded-local")
        upload = {"video_id": ID, "caption_sha256": hashlib.sha256(self.caption).hexdigest(),
                  "status": "uploaded", "platform": "youtube", "verified_at": DATE, "receipt_sha256": "c" * 64}
        data, row = self.prepare(origin="uploaded-local", upload=upload, info=self.info | {"subtitles": {}})
        self.save(data, row)
        self.assertEqual(self.validate()[1], [])
        for patch in [{"caption_sha256": "d" * 64}, {"video_id": "XXXXXXXXXXX"}, {"status": "prepared"}]:
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.prepare(origin="uploaded-local", upload=upload | patch)

    def local_source(self):
        return {"video_id": ID, "caption_sha256": hashlib.sha256(self.caption).hexdigest(),
                "association_basis": "Video-ID archive and public title, description and duration association reviewed",
                "source_kind": "archive-local-corrected", "reviewed_at": DATE,
                "public_metadata_sha256": "a" * 64, "receipt_sha256": "c" * 64}

    def test_local_archive_copy_is_not_platform_uploaded_or_new_ai_review(self):
        data, row = self.prepare(method="local-caption-copy", origin="local-archive", source=self.local_source(),
                                 info=self.info | {"subtitles": {}, "automatic_captions": {}})
        self.save(data, row)
        self.assertEqual(self.validate()[1], [])
        self.assertEqual(data["transcript_quality"], "source-unverified")
        self.assertEqual(data["generation_method"], "local-caption-copy")
        self.assertFalse(data["quality"]["new_text_rewrite"])
        self.assertFalse(data["quality"]["ai_text_processing_verified"])
        self.assertFalse(data["quality"]["human_audio_review"])
        self.assertNotIn("root_edit_review_verified", data["quality"])
        self.assertNotIn("upload_binding", row)
        self.assertEqual(data["units"][0]["text"], "Synthetic one.\nSecond line.")
        self.assertTrue(all(u["speaker_id"] == "unknown" for u in data["units"]))
        for field in ["new_text_rewrite", "ai_text_processing_verified", "human_audio_review"]:
            changed = json.loads(json.dumps(data)); changed["quality"][field] = True
            with self.subTest(field=field), self.assertRaises(ValueError):
                policy.validate_quality(changed)

    def test_local_copy_receipt_requires_exact_video_caption_info_and_review(self):
        with self.assertRaisesRegex(ValueError, "receipt_required"):
            self.prepare(method="local-caption-copy", origin="local-archive")
        for patch in [{"video_id": "XXXXXXXXXXX"}, {"caption_sha256": "d" * 64},
                      {"public_metadata_sha256": "d" * 64}, {"association_basis": ""},
                      {"association_basis": "/Users/synthetic/private"}, {"reviewed_at": "20261112"}]:
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                self.prepare(method="local-caption-copy", origin="local-archive", source=self.local_source() | patch)
        for method, origin in [("publisher-captions", "local-archive"), ("local-caption-copy", "platform"),
                               ("local-caption-copy", "uploaded-local")]:
            with self.subTest(method=method, origin=origin), self.assertRaises(ValueError):
                self.prepare(method=method, origin=origin, source=self.local_source())
        data, row = self.prepare(method="local-caption-copy", origin="local-archive", source=self.local_source())
        row["source_binding"]["receipt_sha256"] = "e" * 64
        self.save(data, row)
        self.assertIn("local_source_binding_invalid", self.validate()[1][0])

    def test_caption_or_time_change_rejected_even_after_raw_file_rebinding(self):
        for field, value in [("text", "Changed synthetic words"), ("start_seconds", 1.2), ("end_seconds", 3.3)]:
            data, row = self.prepare()
            data["units"][0][field] = value
            self.save(data, row)
            self.assertIn("publisher_caption_provenance_invalid", self.validate()[1][0])

    def test_quality_source_and_listing_hashes_are_separately_bound(self):
        for mutate in [lambda d, r: d["quality"].update(caption_sha256="c" * 64),
                       lambda d, r: r["shorts_evidence"].update(present=False),
                       lambda d, r: r["shorts_evidence"].update(receipt_sha256="c" * 64),
                       lambda d, r: r.update(programme_type="interview"),
                       lambda d, r: d.update(inclusion_authorization=policy.SHORTS_AUTHORIZATION + "-extra")]:
            data, row = self.prepare(); mutate(data, row); self.save(data, row)
            self.assertTrue(self.validate()[1])

    def test_parent_family_only_with_exact_binding_and_never_invented(self):
        parent = {"video_id": ID, "parent_url": "https://www.youtube.com/watch?v=XXXXXXXXXXX",
                  "verified_at": DATE, "receipt_sha256": "d" * 64}
        data, row = self.prepare(parent=parent)
        self.save(data, row); self.assertEqual(self.validate()[1], [])
        self.assertEqual(data["source_family"], parent["parent_url"])
        data, row = self.prepare(); data["source_family"] = parent["parent_url"]
        self.save(data, row); self.assertIn("parent_binding_invalid", self.validate()[1][0])

    def test_named_yuzheng_still_requires_existing_exact_text_attribution_policy(self):
        data, row = self.prepare()
        unit = data["units"][0]
        unit.update(speaker_id="yuzheng", speaker_name="立正", speaker_status=turns.REVIEWED, speech_act="statement")
        self.save(data, row)
        self.assertIn("requires_separate_review_policy", self.validate()[1][0])
        review = {"schema_version": 1, "method": turns.METHOD, "human_audio_review": False,
                  "full_precision_certified": False, "records": [{"video_id": ID,
                  "original_source_sha256": data["quality"]["original_source_sha256"],
                  "unknown_units_sha256": turns.digest(turns.unknown_units(data["units"])), "cue_count": 2,
                  "review_basis": "Synthetic unit-only source text check",
                  "units": [{"id": unit["id"], "content_sha256": turns.digest(turns.content(unit)),
                             **{k: unit[k] for k in ("speaker_id", "speaker_name", "speech_act")}}]}]}
        path = self.root / "config/raw-turn-attribution-policy.json"; path.write_bytes(ingest.encode(review))
        self.config["turn_attribution_policy"] = {"path": "config/raw-turn-attribution-policy.json",
                                                  "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}
        self.save(data, row); self.assertEqual(self.validate()[1], [])

    def manifest(self):
        for name, raw in [("info.json", ingest.encode(self.info)), ("listing.json", ingest.encode(self.listing)), ("captions.srt", self.caption)]:
            (self.root / name).write_bytes(raw)
        def binding(name):
            return {"path": name, "sha256": hashlib.sha256((self.root / name).read_bytes()).hexdigest()}
        data = {"schema_version": 1, "authorization": policy.SHORTS_AUTHORIZATION,
                "records": [{"info": binding("info.json"), "captions": {**binding("captions.srt"),
                "method": "publisher-captions", "origin": "platform"}, "shorts_receipt": binding("listing.json")}]}
        path = self.root / "manifest.json"; path.write_bytes(ingest.encode(data)); return path, data

    def test_default_dry_run_does_not_write_and_write_is_explicit_non_overwriting(self):
        path, _ = self.manifest(); before = (self.root / "config/public-dialogue-policy.json").read_bytes()
        result = ingest.run(path, root=self.root)
        self.assertEqual(result["mode"], "dry-run")
        self.assertFalse((self.root / "corpus").exists())
        self.assertEqual((self.root / "config/public-dialogue-policy.json").read_bytes(), before)
        ingest.run(path, root=self.root, write=True)
        self.assertEqual(self.validate()[1], [])
        with self.assertRaisesRegex(ValueError, "existing_source"):
            ingest.run(path, root=self.root, write=True)

    def test_manifest_hash_tampering_and_personal_manuscript_extension_rejected(self):
        path, manifest = self.manifest()
        (self.root / "captions.srt").write_bytes(self.caption + b" ")
        with self.assertRaisesRegex(ValueError, "hash_mismatch"):
            ingest.run(path, root=self.root)
        path, manifest = self.manifest()
        (self.root / "script.md").write_bytes(self.caption)
        manifest["records"][0]["captions"]["path"] = "script.md"; path.write_bytes(ingest.encode(manifest))
        with self.assertRaisesRegex(ValueError, "srt_or_vtt"):
            ingest.run(path, root=self.root)

    def test_existing_markdown_transcript_is_not_silently_replaced_by_raw_short(self):
        path, _ = self.manifest()
        (self.root / "catalog").mkdir()
        (self.root / "catalog/videos.jsonl").write_text(json.dumps({"video_id": ID, "transcript_included": True}) + "\n")
        with self.assertRaisesRegex(ValueError, "existing_source"):
            ingest.run(path, root=self.root, write=True)
        self.assertFalse((self.root / "corpus").exists())

    def test_local_copy_manifest_binds_actual_receipt_and_stays_dry_run(self):
        path, manifest = self.manifest()
        source = self.local_source(); source.pop("receipt_sha256")
        source["public_metadata_sha256"] = manifest["records"][0]["info"]["sha256"]
        source_path = self.root / "source-binding.json"; source_path.write_bytes(ingest.encode(source))
        manifest["records"][0]["captions"].update(method="local-caption-copy", origin="local-archive")
        manifest["records"][0]["source_binding"] = {"path": source_path.name,
                                                      "sha256": hashlib.sha256(source_path.read_bytes()).hexdigest()}
        path.write_bytes(ingest.encode(manifest))
        prepared, _ = ingest.prepare_manifest(path, self.root)
        self.assertEqual(prepared[0][1]["source_binding"]["receipt_sha256"], manifest["records"][0]["source_binding"]["sha256"])
        self.assertFalse((self.root / "corpus").exists())
        source_path.write_bytes(source_path.read_bytes() + b" ")
        with self.assertRaisesRegex(ValueError, "hash_mismatch"):
            ingest.run(path, root=self.root, write=True)
        self.assertFalse((self.root / "corpus").exists())

    def test_invalid_caption_blocks_and_out_of_range_times_fail_closed(self):
        for raw in [b"Personal manuscript only", self.caption.replace(b"00:00:03,250", b"00:00:00,000"),
                    self.caption.replace(b"00:00:04,500", b"00:01:04,500")]:
            with self.subTest(raw=raw[:8]), self.assertRaises(ValueError):
                self.prepare(caption=raw)


if __name__ == "__main__":
    unittest.main()
