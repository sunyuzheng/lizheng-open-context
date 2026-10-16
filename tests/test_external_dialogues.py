"""External admissions retain exact source versions and separately reviewed speech."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import dialogue_policy as policy
import raw_turn_policy as turns
import search
import validate_guest_catalog as guests

SOURCE = "dialogue-circle-12345"
URL = "https://example.org/recording/published-replay"


class ExternalDialogueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.path = self.root / f"corpus/dialogues/{SOURCE}.json"
        self.path.parent.mkdir(parents=True)
        (self.root / "config").mkdir()
        self.data = {**policy.PROVENANCE, "schema_version": 1, "id": SOURCE,
            "title": "Synthetic external conversation", "published_at": "2026-09-25", "language": "zh",
            "source_url": URL, "source_family": URL, "publisher": "Original source publisher",
            "inclusion_authorization": policy.EXTERNAL_AUTHORIZATION, "timestamp_mode": "display-only",
            "public_verified_at": "2026-10-15T12:00:00+00:00",
            "quality": {"ai_text_processing_verified": True, "root_edit_review_verified": True,
                "human_audio_review": False, "full_precision_certified": False,
                "complete_speech_coverage_verified": False, "unresolved_count": 1,
                "original_source_sha256": "a" * 64, "root_output_sha256": "b" * 64,
                "root_receipt_sha256": "c" * 64},
            "units": [{"id": "cue-1", "text": "Synthetic exact speech", "start_seconds": 61.5,
                       "end_seconds": 64, "speaker_id": "unknown", "speaker_name": "", "speaker_status": "unresolved"}]}
        self.row = {"source_id": SOURCE, "source_url": URL, "corpus_path": self.path.relative_to(self.root).as_posix(),
            "cue_count": 1, "review_units": [], "anonymous_evidence": {"source_url": URL,
                "availability": "public", "receipt_sha256": "d" * 64, "verified_at": self.data["public_verified_at"]}}
        self.config = {"schema_version": 1, "authorization": policy.AUTHORIZATION, "scope": "public-dialogues-only",
            "removal": "https://example.org/removal",
            "rights_notice": "Guests retain rights in their own speech; inclusion does not establish Yuzheng's endorsement.",
            "records": [self.row]}
        self.save()

    def tearDown(self):
        self.temp.cleanup()

    def save(self):
        self.path.write_text(json.dumps(self.data), encoding="utf-8")
        self.row["sha256"] = hashlib.sha256(self.path.read_bytes()).hexdigest()
        (self.root / "config/public-dialogue-policy.json").write_text(json.dumps(self.config), encoding="utf-8")

    def check(self):
        errors = []
        stats = policy.validate_dialogues(self.root, set(), errors)
        return stats, errors

    def documents(self):
        previous = search.ROOT
        search.ROOT = self.root
        try:
            return search.parse_raw_dialogue(self.path)
        finally:
            search.ROOT = previous

    def appearance(self):
        row = {"id": "appearance-synthetic", "title": "Synthetic show title", "show": "Synthetic show",
               "url": "https://example.org/official-audio", "published_at": "2026-09-25",
               "transcript_id": SOURCE, "transcript_path": self.row["corpus_path"],
               "participants": [{"speaker_id": "yuzheng", "speaker_name": "立正", "role": "guest"},
                                {"speaker_id": "host:synthetic", "speaker_name": "Synthetic host", "role": "host"}]}
        folder = self.root / "catalog"
        folder.mkdir(exist_ok=True)
        (folder / "guest-appearances.jsonl").write_text(json.dumps(row) + "\n", encoding="utf-8")
        return row

    def reviewed(self):
        self.appearance()
        unit = self.data["units"][0]
        unit.update(speaker_id="host:synthetic", speaker_name="Synthetic host",
                    speaker_status=turns.REVIEWED, speech_act="question")
        self.row["review_units"] = [{"id": unit["id"], "content_sha256": turns.digest(turns.content(unit)),
            **{key: unit[key] for key in ("speaker_id", "speaker_name", "speech_act")}}]
        self.save()

    def test_unknown_external_source_needs_no_fake_youtube_identity(self):
        self.assertEqual(self.check(), ({"structured_public_dialogues": 1, "structured_dialogue_cues": 1}, []))
        self.assertNotIn("video_id", self.data)
        doc = self.documents()[0]
        self.assertEqual((doc.source_url, doc.source_type, doc.speaker_status), (URL, "video-transcript", "unresolved"))
        self.assertTrue(doc.text.startswith("[00:01:01] "))
        self.assertNotIn("&t=", doc.source_url)
        self.assertNotIn("youtube", doc.source_url)
        self.data["source_type"] = "audio-transcript"; self.save()
        self.assertEqual(self.check()[1], [])
        self.assertEqual(self.documents()[0].source_type, "audio-transcript")

    def test_hash_exact_set_and_source_public_evidence_remain_bound(self):
        self.path.write_text(self.path.read_text() + " ")
        self.assertIn("hash_mismatch", self.check()[1][0])
        self.save()
        extra = self.path.parent / "unbound.json"; extra.write_text("{}")
        self.assertIn("exact_set_mismatch", self.check()[1][0]); extra.unlink()
        self.row["anonymous_evidence"]["source_url"] = "https://example.org/different-version"
        self.save(); self.assertIn("not_verified", self.check()[1][0])
        self.row["anonymous_evidence"]["source_url"] = URL
        self.row["anonymous_evidence"]["availability"] = "members-only"
        self.save(); self.assertIn("not_verified", self.check()[1][0])

    def test_review_units_bind_content_timing_label_and_act_after_snapshot_rebinding(self):
        self.reviewed()
        self.assertEqual(self.check()[1], [])
        original = copy.deepcopy(self.data)
        for field, value in [("text", "Changed source speech"), ("start_seconds", 62),
                             ("speech_act", "statement"), ("speaker_id", "yuzheng"),
                             ("speaker_name", "Different host")]:
            with self.subTest(field=field):
                self.data = copy.deepcopy(original)
                self.data["units"][0][field] = value
                self.save()
                self.assertTrue(self.check()[1])
        self.data = original
        self.row["review_units"][0]["id"] = "wrong-cue"
        self.save(); self.assertIn("exact_units_mismatch", self.check()[1][0])

    def test_named_speech_requires_exact_review_and_appearance_identity(self):
        self.reviewed()
        self.row["review_units"] = []
        self.save(); self.assertIn("exact_units_mismatch", self.check()[1][0])
        self.reviewed()
        (self.root / "catalog/guest-appearances.jsonl").unlink()
        self.assertIn("speaker_not_in_appearance", self.check()[1][0])
        self.appearance()
        people = guests.appearance_participants(self.root)
        self.assertEqual(guests.verify_raw_metadata({"appearances": []}, [self.data], people), 1)
        self.data["units"][0]["speaker_id"] = "guest:wrong-ashley"
        with self.assertRaisesRegex(ValueError, "speaker_programme_mismatch"):
            guests.verify_raw_metadata({"appearances": []}, [self.data], people)

    def test_external_provenance_does_not_relax_existing_rights_or_quality(self):
        original = copy.deepcopy(self.data)
        for key, value in [("video_id", "ABCDEFGHIJK"), ("inclusion_authorization", policy.AUTHORIZATION),
                           ("license", "CC0-1.0"), ("rights_scope", "first-party"),
                           ("source_visibility", "members-only"), ("timestamp_mode", "youtube")]:
            self.data = copy.deepcopy(original); self.data[key] = value
            self.save(); self.assertTrue(self.check()[1], key)
        self.data = original
        self.data["quality"]["full_precision_certified"] = True
        self.save(); self.assertIn("overclaim", self.check()[1][0])

    def test_external_retained_reference_pair_is_exact(self):
        for scope, license, valid in [
                ("third-party-reference", policy.RETAINED, True),
                ("publisher-authorized-transcript", policy.REFERENCE_USE, True),
                ("third-party-reference", policy.REFERENCE_USE, False),
                ("publisher-authorized-transcript", policy.RETAINED, False)]:
            with self.subTest(scope=scope, license=license):
                self.data.update(rights_scope=scope, license=license)
                self.save()
                self.assertEqual(not self.check()[1], valid)

    def test_guest_validator_accepts_bound_external_file_without_creating_interviewee(self):
        self.reviewed()
        catalog = {"schema_version": 1, "entities": [], "sources": [], "appearances": [], "redirects": []}
        (self.root / "catalog/guests.json").write_text(json.dumps(catalog))
        (self.root / "catalog/guest-articles.json").write_text(json.dumps({"schema_version": 1, "articles": []}))
        (self.root / "release-manifest.json").write_text(json.dumps({"files": [{
            "path": self.row["corpus_path"], "sha256": self.row["sha256"], "bytes": self.path.stat().st_size}]}))
        stats = guests.validate_guest_catalog(self.root)
        self.assertEqual((stats["public_raw_records"], stats["entities"], stats["sources"]), (1, 0, 0))
        self.assertEqual(self.check()[1], [])

    def test_optional_appearance_catalog_is_metadata_never_raw_speech(self):
        self.path.unlink()
        previous = search.ROOT
        search.ROOT = self.root
        try:
            self.assertEqual(search.load_documents(), [])
            self.appearance()
            doc, = search.load_documents()
            self.assertEqual((doc.source_type, doc.data_layer, doc.speaker_status),
                             ("guest-appearance-catalog", "structured", "not-speech"))
            self.assertEqual(doc.yuzheng_stance_weight, "not-evidence")
            self.assertIn("Synthetic host", doc.text)
            self.assertTrue(search.type_matches(doc, "video"))
        finally:
            search.ROOT = previous

    def test_external_participants_join_raw_and_catalog_without_assigning_speech(self):
        row = self.appearance()
        row["participants"][1].update(aliases=["Synthetic Host Q"], qualifiers=["Synthetic Seattle radio"])
        (self.root / "catalog/guest-appearances.jsonl").write_text(json.dumps(row) + "\n")
        before = self.path.read_bytes()
        previous = search.ROOT
        search.ROOT = self.root
        try:
            raw = search.parse_raw_dialogue(self.path)[0]
            ownership = (raw.speaker_id, raw.speaker_status, raw.author, raw.yuzheng_stance_weight)
            search.apply_guest_catalog([raw])
            self.assertEqual((raw.speaker_id, raw.speaker_status, raw.author, raw.yuzheng_stance_weight), ownership)
            docs = search.load_documents()
            self.assertEqual(len(docs), 2)
            for doc in docs:
                self.assertEqual(doc.participant_entity_ids, "yuzheng；host:synthetic")
                self.assertEqual(doc.participant_names, "立正；Synthetic host")
                self.assertIn("Synthetic Host Q", doc.participant_aliases)
                self.assertIn("Synthetic Seattle radio", doc.participant_aliases)
                self.assertTrue(doc.participant_metadata_basis.startswith("catalog/guest-appearances.jsonl"))
            self.assertEqual(raw.timestamp_mode, "display-only")
            self.assertEqual(self.path.read_bytes(), before)
        finally:
            search.ROOT = previous

    def test_external_alias_fields_are_validated_even_for_catalog_only_rows(self):
        row = self.appearance()
        row.pop("transcript_id"); row.pop("transcript_path")
        row["participants"][1]["aliases"] = "not-an-array"
        (self.root / "catalog/guest-appearances.jsonl").write_text(json.dumps(row) + "\n")
        self.assertIn("participant_names_invalid", self.check()[1][0])

    def test_split_versions_join_every_source_without_assigning_speech_or_copying_documents(self):
        row = self.appearance()
        second_id = "dialogue-synthetic-second-half"
        second_path = self.path.with_name(second_id + ".json")
        second = copy.deepcopy(self.data)
        second.update(id=second_id, source_url="https://example.org/recording/second-half",
                      source_family="https://example.org/recording/second-half")
        second_path.write_text(json.dumps(second))
        row["source_versions"] = [{"transcript_id": SOURCE}, {"transcript_id": second_id},
                                  {"transcript_id": SOURCE, "transcript_path": self.row["corpus_path"]}]
        (self.root / "catalog/guest-appearances.jsonl").write_text(json.dumps(row) + "\n")
        self.assertEqual(set(guests.appearance_participants(self.root)), {SOURCE, second_id})
        previous = search.ROOT
        search.ROOT = self.root
        try:
            before = {path: path.read_bytes() for path in (self.path, second_path)}
            docs = search.load_documents()
            raw = [doc for doc in docs if doc.data_layer == "raw"]
            self.assertEqual(len(docs), 3)  # two existing raw files + one metadata record
            self.assertEqual({doc.source_family for doc in docs}, {row['id']})
            self.assertEqual({doc.source_id for doc in raw}, {SOURCE, second_id})
            self.assertEqual(len({doc.id for doc in docs}), len(docs))
            for doc in raw:
                self.assertEqual(doc.participant_entity_ids, "yuzheng；host:synthetic")
                self.assertEqual((doc.speaker_id, doc.speaker_name, doc.speaker_status), ("unknown", "", "unresolved"))
                self.assertEqual(doc.yuzheng_stance_weight, "not-evidence")
                self.assertEqual(doc.timestamp_mode, "display-only")
                self.assertNotIn("&t=", doc.source_url)
            self.assertEqual({path: path.read_bytes() for path in before}, before)
        finally:
            search.ROOT = previous

    def test_version_only_bindings_keep_reviewed_external_participants(self):
        self.reviewed()
        row = self.appearance()
        row.pop("transcript_id"); row.pop("transcript_path")
        row["source_versions"] = [{"transcript_id": SOURCE}]
        (self.root / "catalog/guest-appearances.jsonl").write_text(json.dumps(row) + "\n")
        self.assertEqual(self.check()[1], [])
        self.assertEqual(guests.appearance_participants(self.root)[SOURCE]["host:synthetic"], "Synthetic host")

    def test_transcript_binding_rejects_bad_ids_paths_and_cross_appearance_conflicts(self):
        row = self.appearance()
        invalid = [
            {"source_versions": {}}, {"source_versions": ["not-an-object"]},
            {"source_versions": [{"transcript_path": self.row["corpus_path"]}]},
            {"source_versions": [{"transcript_id": "dialogue-../escape"}]},
            {"source_versions": [{"transcript_id": "youtube-too-short"}]},
            {"source_versions": [{"transcript_id": SOURCE, "transcript_path": "/" + self.row["corpus_path"]}]},
            {"source_versions": [{"transcript_id": SOURCE, "transcript_path": f"corpus/dialogues/../{SOURCE}.json"}]},
            {"source_versions": [{"transcript_id": SOURCE, "transcript_path": None}]},
            {"transcript_path": f"corpus/dialogues/dialogue-other.json"},
            {"transcript_path": None},
        ]
        for change in invalid:
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    search.appearance_transcript_bindings([{**row, **change}])
        another = {**row, "id": "appearance-other"}
        with self.assertRaisesRegex(ValueError, "appearance_conflict"):
            search.appearance_transcript_bindings([row, another])
        another.pop("transcript_id"); another.pop("transcript_path")
        another["source_versions"] = [{"transcript_id": SOURCE}]
        with self.assertRaisesRegex(ValueError, "appearance_conflict"):
            search.appearance_transcript_bindings([row, another])
        row.pop("transcript_path")
        with self.assertRaisesRegex(ValueError, "transcript_identity_invalid"):
            search.appearance_transcript_bindings([row])

    def test_reused_youtube_version_keeps_canonical_guest_identity_and_single_transcript(self):
        youtube_id = "youtube-ABCDEFGHIJK"
        youtube_path = self.path.with_name(youtube_id + ".json")
        self.data.update(id=youtube_id, video_id="ABCDEFGHIJK",
                         source_url="https://www.youtube.com/watch?v=ABCDEFGHIJK",
                         source_family="https://www.youtube.com/watch?v=ABCDEFGHIJK")
        youtube_path.write_text(json.dumps(self.data)); self.path.unlink()
        row = self.appearance()
        row.pop("transcript_id"); row.pop("transcript_path")
        row["source_versions"] = [{"transcript_id": youtube_id}, {"transcript_id": youtube_id}]
        (self.root / "catalog/guest-appearances.jsonl").write_text(json.dumps(row) + "\n")
        own = {"entities": [{"entity_id": "guest:canonical", "display_name": "Canonical guest", "aliases": ["Own alias"]}],
               "sources": [{"source_id": youtube_id, "url": self.data["source_url"], "title": "Canonical source"}],
               "appearances": [{"source_id": youtube_id, "entity_id": "guest:canonical"}]}
        (self.root / "catalog/guests.json").write_text(json.dumps(own))
        self.assertEqual(set(guests.appearance_participants(self.root)), {youtube_id})
        previous = search.ROOT
        search.ROOT = self.root
        try:
            docs = search.load_documents()
            self.assertEqual(len(docs), 2)
            raw, = [doc for doc in docs if doc.data_layer == "raw"]
            self.assertEqual(raw.participant_entity_ids, "guest:canonical")
            self.assertEqual(raw.participant_names, "Canonical guest")
            self.assertEqual(raw.participant_aliases, "Own alias")
            self.assertEqual({doc.source_family for doc in docs}, {row['id']})
            self.assertEqual((raw.speaker_id, raw.speaker_name), ("unknown", ""))
            self.assertNotIn("&t=", raw.source_url)  # retained display-only mode
            metadata, = [doc for doc in docs if doc.source_type == "guest-appearance-catalog"]
            self.assertEqual(metadata.participant_entity_ids, "yuzheng；host:synthetic")
            self.assertEqual(len(own["entities"]), 1)
        finally:
            search.ROOT = previous

    def test_markdown_youtube_and_external_editions_share_family_not_version_provenance(self):
        youtube_id='youtube-ABCDEFGHIJK';youtube_url='https://www.youtube.com/watch?v=ABCDEFGHIJK'
        markdown=self.root/'corpus/videos/synthetic.md';markdown.parent.mkdir()
        meta={'id':youtube_id,'title':'Synthetic family probe','source_type':'video-transcript',
              'source_url':youtube_url,'source_family':youtube_url,'published_at':'2026-09-25',
              'data_layer':'raw','speaker_id':'unknown','speaker_status':'unresolved',
              'license':'LicenseRef-Lizheng-Reference-Use-1.0','rights_scope':'first-party',
              'source_visibility':'members-only','text_access':'public','timestamp_mode':'youtube'}
        markdown.write_text('---\n'+'\n'.join(f'{key}: {json.dumps(value)}' for key,value in meta.items())
                            +'\n---\n\n[00:02:03]('+youtube_url+'&t=123s) Synthetic family probe exact speech.')
        self.data['units'][0]['text']='Synthetic family probe exact speech.';self.save()
        row=self.appearance();row['source_versions']=[{'transcript_id':youtube_id},{'transcript_id':SOURCE}]
        catalog=self.root/'catalog/guest-appearances.jsonl';catalog.write_text(json.dumps(row)+'\n')
        previous=search.ROOT;search.ROOT=self.root
        try:
            originals={d.id:vars(d).copy() for d in [*search.parse_markdown(markdown),*search.parse_raw_dialogue(self.path)]}
            before={path:path.read_bytes() for path in (markdown,self.path,catalog)}
            docs=search.load_documents();raw=[doc for doc in docs if doc.data_layer=='raw']
            self.assertEqual({doc.source_id for doc in raw},{youtube_id,SOURCE})
            self.assertEqual({doc.source_family for doc in docs},{row['id']})
            mutable={'source_family','participant_entity_ids','participant_names','participant_aliases','participant_metadata_basis'}
            for doc in raw:
                self.assertEqual({k:v for k,v in vars(doc).items() if k not in mutable},
                                 {k:v for k,v in originals[doc.id].items() if k not in mutable})
            yt=next(doc for doc in raw if doc.source_id==youtube_id)
            self.assertEqual(yt.source_url,youtube_url+'&t=123s')
            self.assertEqual((yt.license,yt.source_visibility,yt.text_access),
                             (meta['license'],'members-only','public'))
            results=search.search_documents(raw,'Synthetic family probe',top=10)
            self.assertEqual(len(results),1)
            self.assertEqual(results[0]['source_family'],row['id'])
            search.apply_guest_catalog(docs)
            self.assertEqual({doc.source_family for doc in docs},{row['id']})
            self.assertEqual({path:path.read_bytes() for path in before},before)
        finally:search.ROOT=previous

    def test_distinct_appearances_never_merge_by_shared_url_or_text(self):
        row=self.appearance();other_id='dialogue-synthetic-other'
        other=copy.deepcopy(self.data);other['id']=other_id
        other_path=self.path.with_name(other_id+'.json');other_path.write_text(json.dumps(other))
        other_row={**row,'id':'appearance-other','transcript_id':other_id,
                   'transcript_path':f'corpus/dialogues/{other_id}.json'}
        catalog=self.root/'catalog/guest-appearances.jsonl'
        catalog.write_text(json.dumps(row)+'\n'+json.dumps(other_row)+'\n')
        previous=search.ROOT;search.ROOT=self.root
        try:
            docs=search.load_documents();raw=[doc for doc in docs if doc.data_layer=='raw']
            self.assertEqual({doc.source_family for doc in raw},{row['id'],other_row['id']})
            self.assertEqual(len(search.search_documents(raw,'Synthetic exact speech',top=10)),2)
            other_row.update(transcript_id=SOURCE,transcript_path=self.row['corpus_path'])
            catalog.write_text(json.dumps(row)+'\n'+json.dumps(other_row)+'\n')
            with self.assertRaisesRegex(ValueError,'appearance_conflict'):search.load_documents()
        finally:search.ROOT=previous

    def test_actual_youtube_sources_keep_timing_but_other_hosts_never_gain_it(self):
        self.data.pop("timestamp_mode")
        self.data["source_url"] = "https://www.youtube.com/watch?v=ABCDEFGHIJK"
        self.save(); self.assertEqual(self.documents()[0].source_url, "https://www.youtube.com/watch?v=ABCDEFGHIJK&t=61s")
        self.data["source_url"] = "https://www.youtube.com.example.org/watch?v=ABCDEFGHIJK"
        self.save(); self.assertEqual(self.documents()[0].source_url, self.data["source_url"])

    def test_external_record_cannot_relabel_a_protected_youtube_source(self):
        source = "https://www.youtube.com/watch?v=ABCDEFGHIJK"
        self.data.update(source_url=source, source_family=source)
        self.row["source_url"] = source
        self.row["anonymous_evidence"]["source_url"] = source
        self.save()
        errors = []
        policy.validate_dialogues(self.root, {"ABCDEFGHIJK"}, errors)
        self.assertIn("cannot_bypass_youtube_policy", errors[0])


if __name__ == "__main__":
    unittest.main()
