import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import export_public_corpus as exporter
import import_member_transcripts as members
import search
import validate_release as validator
from enrich_provenance import default_provenance, read_markdown

ID = "abcdefghijk"
URL = f"https://www.youtube.com/watch?v={ID}"


class MemberTranscriptTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = (Path(self.temp.name) / "repo").resolve()
        self.archive = Path(self.temp.name) / "archive"
        (self.root / "catalog").mkdir(parents=True)
        (self.root / "catalog/videos.jsonl").write_text("")
        folder = self.archive / ID
        folder.mkdir(parents=True)
        srt = "1\n00:00:02,000 --> 00:00:04,000\n合成资料，对话人的经验。\n\n2\n00:00:08,000 --> 00:00:10,000\n合成资料，回到这个时间点。\n"
        (folder / "transcript.srt").write_text(srt)
        checksum = members.digest(folder / "transcript.srt")
        self.source = dict(video_id=ID, title="合成会员对话", source_url=URL,
                           membership_verified=True, membership_verified_at="2026-10-02", visibility="Members",
                           published_at=None, studio_display_date="2026-09-24", transcript_sha256=checksum,
                           transcript_source_kind="local_qwen_uncorrected")
        self.policy = dict(snapshot_at="2026-10-02", authorization="maintainer-request-2026-10-02-member-transcripts",
                           membership_url="https://www.youtube.com/channel/UC_5lJHgnMP_lb_VpIiXV0hQ/join",
                           records=[dict(video_id=ID, title=self.source["title"], published_at="2026-09-24",
                                         transcript_sha256=checksum, transcript_source_kind="local_qwen_uncorrected", guest_names=["合成嘉宾"])])
        self.write_source()

    def write_source(self):
        (self.archive / ID / "source.json").write_text(json.dumps(self.source))

    def import_local(self):
        counts, writes, rows = members.prepare(self.archive, self.policy, self.root)
        members.apply_prepared(self.root, writes, rows)
        return counts, writes, rows

    def test_import_preserves_member_access_timestamps_guest_attribution_and_quality(self):
        counts, writes, rows = self.import_local()
        self.assertEqual(counts["new_transcripts"], 1)
        row = rows[0]
        self.assertEqual(row["text_access"], "public")
        self.assertEqual(row["source_visibility"], "members-only")
        self.assertEqual(row["transcript_quality"], "uncorrected-asr")
        self.assertEqual(row["published_at"], "2026-09-24")
        self.assertNotEqual(row["author"], "Yuzheng Sun")
        self.assertEqual(row["yuzheng_stance_weight"], "not-evidence")
        self.assertEqual(row["license"], "LicenseRef-Lizheng-Reference-Use-1.0")
        body = writes[0][0].read_text()
        self.assertIn("按[立正参考使用许可](https://github.com/sunyuzheng/lizheng-open-context/blob/main/LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md)使用", body)
        self.assertIn(URL + "&t=8s", body)
        self.assertNotIn(str(self.archive), body)
        with patch.object(search, "ROOT", self.root):
            chunk = search.parse_markdown(writes[0][0])[0]
            result = search.search_documents([chunk], "合成资料")[0]
            self.assertEqual(result["source_visibility"], "members-only")
            self.assertEqual(result["membership_platform"], "youtube")
            self.assertEqual(result["transcript_quality"], "uncorrected-asr")
            self.assertEqual(result["speaker_classification"], "mixed-or-unresolved")

    def test_hash_or_identity_changes_fail_before_writes(self):
        path = self.archive / ID / "transcript.srt"
        path.write_text(path.read_text() + "\nChanged input")
        with self.assertRaisesRegex(ValueError, "differs from authorized snapshot"):
            members.prepare(self.archive, self.policy, self.root)
        self.assertEqual((self.root / "catalog/videos.jsonl").read_text(), "")
        self.assertFalse((self.root / "corpus").exists())

    def test_access_requires_verified_current_snapshot(self):
        self.source["membership_verified"] = False
        self.write_source()
        with self.assertRaisesRegex(ValueError, "membership provenance"):
            members.prepare(self.archive, self.policy, self.root)

    def test_reimport_is_idempotent_and_preserves_existing_body(self):
        _, writes, _ = self.import_local()
        before = writes[0][0].read_bytes()
        catalog = (self.root / "catalog/videos.jsonl").read_bytes()
        counts, _, rows = self.import_local()
        self.assertEqual(counts["new_transcripts"], 0)
        self.assertEqual(len(rows), 1)
        self.assertEqual(writes[0][0].read_bytes(), before)
        self.assertEqual((self.root / "catalog/videos.jsonl").read_bytes(), catalog)

    def test_enrichment_never_upgrades_mixed_speech_to_yuzheng(self):
        _, writes, _ = self.import_local()
        meta, body = read_markdown(writes[0][0])
        result = default_provenance(meta, body)
        self.assertEqual(result["original_author"], meta["original_author"])
        self.assertEqual(result["yuzheng_stance_weight"], "not-evidence")
        self.assertEqual(result["license"], "LicenseRef-Lizheng-Reference-Use-1.0")

    def test_validator_rejects_a_member_source_upgraded_to_direct_authority(self):
        _, _, rows = self.import_local()
        errors = []
        validator.validate_member_video(rows[0], self.policy, errors)
        self.assertEqual(errors, [])
        for mutation in ({"license": "CC-BY-4.0"}, {"license": "LicenseRef-Original-Rights-Retained"}, {"yuzheng_stance_weight": "direct-with-quotation-boundaries"}, {"text_access": "members-only"}):
            errors = []
            validator.validate_member_video(dict(rows[0], **mutation), self.policy, errors)
            self.assertTrue(errors)

    def test_public_export_preserves_independent_member_snapshot(self):
        _, writes, _ = self.import_local()
        before = writes[0][0].read_bytes()
        channel = Path(self.temp.name) / "channel"
        (channel / "logs/library_manifest").mkdir(parents=True)
        (channel / "logs/library_manifest/library_manifest.json").write_text('{"records": []}')
        (channel / "guests.json").write_text("[]")
        with patch.object(exporter, "ROOT", self.root):
            exporter.export_videos(channel, "2026-10-03", {}, set())
        self.assertEqual(writes[0][0].read_bytes(), before)
        rows = [json.loads(line) for line in (self.root / "catalog/videos.jsonl").read_text().splitlines()]
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["membership_verified_at"], "2026-10-02")


if __name__ == "__main__":
    unittest.main()
