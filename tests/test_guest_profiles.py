import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import guest_profiles as g


def entity(name, **extra):
    return {"entity_id": "guest:" + extra.pop("slug", name.lower().replace(" ", "-")), "display_name": name, "aliases": [name], **extra}


class StatedProfiles(unittest.TestCase):
    def test_reads_the_three_written_forms(self):
        marco, changxi, gene, mu = entity("Marco Casalaina"), entity("郑昌熙", slug="changxi-zheng"), entity("Gene Tabach"), entity("Mujtaba")
        cast = {e["entity_id"]: g.names(e) for e in (marco, changxi, gene, mu)}
        one = "聊了产品功课。\n\n嘉宾：Marco Casalaina，微软CoreAI产品副总裁、AI Futurist（VP Products of Core AI and AI Futurist, Microsoft） 主持：孙煜征博士（课代表立正），Superlinear Academy\n章节：\n00:00 开场"
        self.assertEqual(g.stated_profiles(one, cast), {"guest:marco-casalaina": "微软CoreAI产品副总裁、AI Futurist"})
        two = "嘉宾：郑昌熙（Changxi Zheng）\n哥伦比亚大学计算机科学教授、SceniX联合创始人；录制时在World Labs全职工作。\n社区伴读文章：https://example.org/a"
        self.assertEqual(g.stated_profiles(two, cast), {"guest:changxi-zheng": "哥伦比亚大学计算机科学教授、SceniX联合创始人"})
        three = ("这期我和Gene Tabach、Mujtaba Tirmizi聊了Ecosystem DS。\n\n嘉宾背景与近况（更新于2026年10月22日）：\n"
                 "Gene Tabach：曾负责Facebook的Ecosystem Data Science，后任Grow Therapy数据副总裁。目前已加入OpenAI。\n"
                 "Mujtaba Tirmizi：Meta数据科学负责人，访谈时负责Marketplace的DS团队。目前仍在Meta。\n\n嘉宾主页：\nGene：https://example.org/gene")
        self.assertEqual(g.stated_profiles(three, cast), {
            "guest:gene-tabach": "曾负责Facebook的Ecosystem Data Science，后任Grow Therapy数据副总裁",
            "guest:mujtaba": "Meta数据科学负责人，访谈时负责Marketplace的DS团队"})

    def test_infers_nothing_from_prose_or_from_the_generated_block(self):
        tiannan, lulu = entity("杨天楠", slug="yang-tiannan"), entity("Lulu（Multi-FIRE）", slug="lulu")
        cast = {e["entity_id"]: g.names(e) for e in (tiannan, lulu)}
        prose = "天楠是财经播客《听懂涨声》的主播，做过电台主持人和电视导演。\n天楠的解释是：摊主每做一个饼，都有顾客的真实反馈。"
        self.assertEqual(g.stated_profiles(prose, cast), {})
        # The block the channel generated from the catalog once gave this Lulu another Lulu's title.
        generated = "────\n嘉宾 / Guest：Lulu\n珠宝商 @ 水贝珠宝世家\n更多嘉宾访谈：https://www.lizheng.ai/guests"
        self.assertEqual(g.stated_profiles(generated, cast), {})
        # A line that could be either of two guests names nobody.
        both = {"guest:leo-a": ["Leo"], "guest:leo-b": ["Leo"]}
        self.assertEqual(g.stated_profiles("嘉宾：Leo，上海一家酒吧的首席调酒师", both), {})
        # The evidence report still shows the prose, for whoever writes the line.
        self.assertEqual(g.description_mentions(prose, g.names(tiannan))[0], "天楠是财经播客《听懂涨声》的主播，做过电台主持人和电视导演。")


class Fill(unittest.TestCase):
    def catalog(self, root, entities):
        (root / "catalog").mkdir(parents=True)
        (root / "corpus/dialogues").mkdir(parents=True)
        value = {"schema_version": 1, "entities": entities, "redirects": [],
                 "sources": [{"source_id": "youtube-aaaaaaaaaaa", "title": "对话A", "published_at": "2026-10-15T00:00:00Z",
                              "description": "嘉宾：Marco Casalaina，微软CoreAI产品副总裁、AI Futurist 主持：孙煜征"},
                             {"source_id": "youtube-bbbbbbbbbbb", "title": "杨天楠：假工作", "published_at": "2026-10-30T00:00:00Z",
                              "description": "天楠是财经播客《听懂涨声》的主播。"}],
                 "appearances": [{"entity_id": "guest:marco-casalaina", "source_id": "youtube-aaaaaaaaaaa"},
                                 {"entity_id": "guest:yang-tiannan", "source_id": "youtube-bbbbbbbbbbb"}]}
        (root / "catalog/guests.json").write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (root / "catalog/videos.jsonl").write_text("", encoding="utf-8")
        units = [{"id": "cue-1", "start_seconds": 2.0, "text": "大家好欢迎回到课代表立正", "speech_act": "introduction"},
                 {"id": "cue-2", "start_seconds": 4.0, "text": "今天我们请来了天楠", "speech_act": "introduction"}]
        (root / "corpus/dialogues/youtube-bbbbbbbbbbb.json").write_text(json.dumps({"units": units}, ensure_ascii=False), encoding="utf-8")

    def test_fills_only_what_is_stated_and_never_changes_a_line(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.catalog(root, [entity("Marco Casalaina"), entity("杨天楠", slug="yang-tiannan")])
            filled = g.fill(root)
            self.assertEqual([(f["display_name"], f["guest_title"]) for f in filled], [("Marco Casalaina", "微软CoreAI产品副总裁、AI Futurist")])
            self.assertEqual(g.fill(root), [])  # a second run changes nothing
            # The guest whose description only has prose stays without a line: reported with the evidence, not blocked.
            self.assertEqual(g.missing(root), ["杨天楠"])
            report = g.report(root)["guests_without_profile"]
            self.assertEqual([r["display_name"] for r in report], ["杨天楠"])
            self.assertEqual(report[0]["programmes"][0]["description_says"], ["天楠是财经播客《听懂涨声》的主播。"])
            self.assertEqual(report[0]["programmes"][0]["transcript_opening"]["units"], "youtube-bbbbbbbbbbb#cue-1..cue-2")
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.catalog(root, [entity("Marco Casalaina", guest_company="Microsoft"), entity("杨天楠", slug="yang-tiannan", guest_title="播客主播")])
            before = (root / "catalog/guests.json").read_text(encoding="utf-8")
            self.assertEqual(g.fill(root), [])
            self.assertEqual((root / "catalog/guests.json").read_text(encoding="utf-8"), before)


if __name__ == "__main__":
    unittest.main()
