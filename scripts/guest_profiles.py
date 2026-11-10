#!/usr/bin/env python3
"""List guests who have no profile line, with what their programmes say about who they are.

A guest's page opens with the profile line (guest_company, guest_title). A new guest enters
the catalog without one, so this report gathers the evidence to write it in the same release:
the programme titles, the sentences of the published description that name the guest, and the
opening of the transcript where guests are introduced. It reads committed files only and
guesses nothing: the line is written from this evidence by whoever prepares the release.

Where a published description states the guest's identity outright (嘉宾：姓名，身份), fill()
writes it as the profile line; validate_release.py --write-manifest calls it, so a new guest
gets a line without anyone remembering to add one. An existing line is never changed.

A missing profile line never blocks a release. Run after every interview ingestion.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SENTENCE = re.compile(r"[^。！？!?\n]+[。！？!?]?")
TIMED_LINE = re.compile(r"(?m)^\[(\d{2}):(\d{2}):(\d{2})\]\(https://www\.youtube\.com/watch\?v=[^)]+\)\s+(.+)$")
HAN_NAME = re.compile(r"[一-鿿]{2,4}\Z")
INTRODUCING = re.compile(r"欢迎|今天我们|今天请|请来|请到|采访|介绍|我叫|我是|welcome|introduce|my name", re.I)
OPENING_SECONDS = 600


def has_profile(entity: dict) -> bool:
    return bool((entity.get("guest_title") or "").strip() or (entity.get("guest_company") or "").strip())


def names(entity: dict) -> list[str]:
    """The ways a description or a transcript may name this guest, longest first."""
    found = set()
    for value in [entity["display_name"], entity.get("guest_en_name", ""), *entity.get("aliases", []),
                  *(m.get("name", "") for m in entity.get("members", []))]:
        for part in re.split(r"[（）()/&、]", value):
            part = part.strip()
            if len(part) < 2:
                continue
            found.add(part)
            if HAN_NAME.fullmatch(part) and len(part) >= 3:
                found.add(part[-2:])  # 杨天楠 is written 天楠 after the first mention
            elif " " in part and len(part.split()[0]) >= 3:
                found.add(part.split()[0])  # Marco Casalaina is Marco afterwards
    return sorted(found, key=len, reverse=True)


def description_mentions(description: str, guest_names: list[str]) -> list[str]:
    """Sentences of the published description that name the guest, each with the sentence after it
    when that one continues about them (他是……)."""
    sentences = [s.strip() for s in SENTENCE.findall(description) if s.strip()]
    out = []
    for index, sentence in enumerate(sentences):
        if not any(name in sentence for name in guest_names):
            continue
        following = sentences[index + 1] if index + 1 < len(sentences) else ""
        out.append(sentence + (following if re.match(r"(他|她|TA|He |She )", following) else ""))
    return list(dict.fromkeys(out))[:4]


def transcript_opening(root: Path, source_id: str, corpus_path: str | None, guest_names: list[str]) -> dict | None:
    """Where the programme introduces its guest: units tagged as introductions in the opening, or the
    opening lines that name the guest or sound like an introduction."""
    dialogue = root / f"corpus/dialogues/{source_id}.json"
    if dialogue.is_file():
        units = json.loads(dialogue.read_text(encoding="utf-8"))["units"]
        opening = [(i, u) for i, u in enumerate(units) if u["start_seconds"] <= OPENING_SECONDS]
        tagged = [(i, u) for i, u in opening if u.get("speech_act") == "introduction"]
        chosen = tagged or [(i, u) for i, u in opening if any(n in u["text"] for n in guest_names) or INTRODUCING.search(u["text"])]
        if not chosen:
            return None
        first = chosen[0][0]
        window = units[first:first + 20]
        return {"units": f"{source_id}#cue-{first + 1}..cue-{first + len(window)}", "start_seconds": int(window[0]["start_seconds"]),
                "text": " ".join(u["text"].strip() for u in window)}
    if corpus_path and (root / corpus_path).is_file():
        lines = []
        for m in TIMED_LINE.finditer((root / corpus_path).read_text(encoding="utf-8")):
            seconds = int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3))
            if seconds <= OPENING_SECONDS and (any(n in m.group(4) for n in guest_names) or INTRODUCING.search(m.group(4))):
                lines.append((seconds, m.group(4).strip()))
        if lines:
            return {"lines": f"{corpus_path}@{lines[0][0]}..@{lines[-1][0]}", "start_seconds": lines[0][0],
                    "text": " ".join(text for _, text in lines[:8])}
    return None


def report(root: Path = ROOT) -> dict:
    catalog = json.loads((root / "catalog/guests.json").read_text(encoding="utf-8"))
    videos = {}
    for line in (root / "catalog/videos.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row = json.loads(line)
            videos[row["id"]] = row
    sources = {s["source_id"]: s for s in catalog["sources"]}
    appearances: dict[str, list[str]] = {}
    for row in catalog["appearances"]:
        appearances.setdefault(row["entity_id"], []).append(row["source_id"])
    guests = []
    for entity in catalog["entities"]:
        if has_profile(entity):
            continue
        guest_names = names(entity)
        programmes = []
        for source_id in sorted(appearances.get(entity["entity_id"], []), key=lambda s: sources[s].get("published_at", ""), reverse=True):
            source = sources[source_id]
            item = {"source_id": source_id, "published_at": source.get("published_at", "")[:10], "title": source["title"]}
            mentions = description_mentions(source.get("description", ""), guest_names)
            if mentions:
                item["description_says"] = mentions
            opening = transcript_opening(root, source_id, (videos.get(source_id) or {}).get("corpus_path"), guest_names)
            if opening:
                item["transcript_opening"] = opening
            programmes.append(item)
        guests.append({"entity_id": entity["entity_id"], "display_name": entity["display_name"],
                       "has_introduction": bool(entity.get("introductions")), "programmes": programmes})
    return {
        "schema_version": 1,
        "method": "committed catalog, published descriptions and transcripts; evidence only, no profile is guessed",
        "what_to_do": "Write guest_title (and guest_company) in catalog/guests.json from this evidence, and quote an introduction "
                      "where the transcript says who the guest is (docs/source-model.md). When the evidence does not say who "
                      "the guest is, release without it: a missing profile line never blocks a release.",
        "guests_without_profile": guests,
    }


# 嘉宾：… as written for the programme. The block the channel once generated from this catalog
# (嘉宾 / Guest：… then 头衔 @ 公司) is not a source: it copies the catalog, and has named the wrong Lulu.
GUEST_LINE = re.compile(r"\s*嘉宾\s*[：:]\s*(.+)")
NAMED_LINE = re.compile(r"\s*([^：:，,。\n]{2,40})[：:]\s*(\S.*)")
ASCII_GLOSS = re.compile(r"（[\x20-\x7e]+）\s*$|\([\x20-\x7e]+\)\s*$")


def identity(text: str) -> str:
    """The identity a guest line states, or "" when the text is not one: the first clause, without the
    host's credit, an English gloss in brackets, links or chapter marks."""
    text = re.split(r"\s+主持\s*[：:]", text)[0].strip()
    text = re.split(r"[。；;]", text)[0].strip()
    text = ASCII_GLOSS.sub("", text).strip()
    if not 4 <= len(text) <= 80 or "http" in text or " @ " in text or re.match(r"\d{1,2}:\d{2}", text) or re.search(r"[：:]", text):
        return ""
    return text


def stated_profiles(description: str, participants: dict[str, list[str]]) -> dict[str, str]:
    """Profile lines the published description states outright, by entity id. Three written forms are
    read and nothing is inferred from prose:

        嘉宾：姓名，身份                      the identity runs to 主持： or the end of the line
        嘉宾：姓名（English）                 with the identity on the next line
        姓名：身份                            on the lines under a 嘉宾背景 heading

    participants maps each guest of the programme to the names it may be written by. A line counts
    only when it names exactly one of them.
    """
    def who(name_text: str) -> str | None:
        found = [entity for entity, known in participants.items() if any(name_text.startswith(n) for n in known if len(n) >= 2)]
        return found[0] if len(found) == 1 else None

    lines = [line.strip() for line in description.splitlines()]
    out: dict[str, str] = {}
    in_background = False
    for index, line in enumerate(lines):
        if not line:
            continue
        if "嘉宾背景" in line:
            in_background = True
            continue
        guest_line = GUEST_LINE.fullmatch(line)
        if guest_line:
            rest = guest_line.group(1).strip()
            name_text, _, stated = rest.partition("，")
            entity = who(ASCII_GLOSS.sub("", name_text).strip() or name_text)
            if not entity:
                continue
            following = next((x for x in lines[index + 1:] if x), "")
            value = identity(stated) or identity(following)
            if value:
                out.setdefault(entity, value)
            continue
        if in_background:
            named = NAMED_LINE.fullmatch(line)
            entity = who(named.group(1).strip()) if named else None
            if entity and identity(named.group(2)):
                out.setdefault(entity, identity(named.group(2)))
            elif not named:
                in_background = False
    return out


def fill(root: Path = ROOT) -> list[dict]:
    """Give each guest without a profile line the identity a published description of theirs states,
    newest programme first. Writes catalog/guests.json only when something was filled; returns what."""
    path = root / "catalog/guests.json"
    catalog = json.loads(path.read_text(encoding="utf-8"))
    sources = {s["source_id"]: s for s in catalog["sources"]}
    entities = {e["entity_id"]: e for e in catalog["entities"]}
    cast: dict[str, list[str]] = {}
    for row in catalog["appearances"]:
        cast.setdefault(row["source_id"], []).append(row["entity_id"])
    filled = []
    for source in sorted(catalog["sources"], key=lambda s: s.get("published_at", ""), reverse=True):
        description = source.get("description")
        if not description:
            continue
        participants = {eid: names(entities[eid]) for eid in cast.get(source["source_id"], [])}
        for entity_id, value in stated_profiles(description, participants).items():
            entity = entities[entity_id]
            if has_profile(entity):
                continue
            entity["guest_title"] = value
            filled.append({"entity_id": entity_id, "display_name": entity["display_name"], "guest_title": value, "source_id": source["source_id"]})
    if filled:
        path.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return filled


def missing(root: Path = ROOT) -> list[str]:
    """Display names of the guests without a profile line, for the release summary."""
    catalog = json.loads((root / "catalog/guests.json").read_text(encoding="utf-8"))
    return [e["display_name"] for e in catalog["entities"] if not has_profile(e)]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--fill", action="store_true", help="first write the profile lines that published descriptions state outright")
    args = parser.parse_args()
    result = report()
    if args.fill:
        result = {"filled": fill(), **report()}
    value = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    if args.output:
        args.output.write_text(value, encoding="utf-8")
    else:
        print(value)


if __name__ == "__main__":
    main()
