"""Applying voice labels: who gets named, what stays unresolved, and what is never touched."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import raw_turn_policy as turns
import voice_attribution as voice


def unit(i, **fields):
    return {"id": f"cue-{i}", "text": f"line {i}", "start_seconds": i, "end_seconds": i + 1,
            "speaker_id": "unknown", "speaker_name": "", "speaker_status": "unresolved", **fields}


class ApplyTests(unittest.TestCase):
    def test_labels_need_a_classified_speech_act_and_a_named_voice(self):
        units = [unit(0), unit(1), unit(2), unit(3)]
        labels = [("yuzheng", 0.3), ("other:0", 0.2), ("other:1", 0.2), ("yuzheng", 0.3)]
        acts = {"0": "statement", "1": "question", "2": "statement"}
        guest = {"voice": "other:0", "entity_id": "guest:alpha", "name": "Alpha"}
        out = voice.attributed_units(units, labels, acts, guest)
        self.assertEqual([(u["speaker_id"], u.get("speech_act")) for u in out],
                         [("yuzheng", "statement"), ("guest:alpha", "question"), ("unknown", None), ("unknown", None)])
        self.assertTrue(all(u["speaker_status"] == turns.VOICE for u in out[:2]))
        self.assertEqual(out[2]["speaker_status"], "unresolved")  # a second voice is never named
        self.assertEqual(out[3]["speaker_status"], "unresolved")  # no speech act, no label

    def test_reviewed_units_and_the_text_are_never_changed(self):
        reviewed = unit(0, speaker_id="guest:alpha", speaker_name="Alpha", speaker_status=turns.REVIEWED, speech_act="statement")
        out = voice.attributed_units([reviewed, unit(1)], [("yuzheng", 0.4), ("yuzheng", 0.4)], {"0": "question", "1": "statement"}, None)
        self.assertEqual(out[0], reviewed)
        self.assertEqual(turns.digest(turns.unknown_units(out)), turns.digest(turns.unknown_units([reviewed, unit(1)])))

    def test_a_guest_is_named_only_for_one_listed_person_and_one_other_voice(self):
        entities = {"guest:alpha": {"entity_type": "person", "display_name": "Alpha"},
                    "guest:pair": {"entity_type": "group", "display_name": "Alpha & Beta"}}
        one = {"voices": {"yuzheng": 300.0, "other:0": 900.0}}
        self.assertEqual(voice.single_guest(one, ["guest:alpha"], entities),
                         {"voice": "other:0", "entity_id": "guest:alpha", "name": "Alpha"})
        self.assertIsNone(voice.single_guest(one, ["guest:pair"], entities))
        self.assertIsNone(voice.single_guest(one, ["guest:alpha", "guest:pair"], entities))
        self.assertIsNone(voice.single_guest({"voices": {"yuzheng": 1.0, "other:0": 9.0, "other:1": 9.0}}, ["guest:alpha"], entities))
        self.assertIsNone(voice.single_guest(one, [], entities))


if __name__ == "__main__":
    unittest.main()
