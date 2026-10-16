#!/usr/bin/env python3
"""Derive every catalog field that repeats a fact owned elsewhere, so no copy is edited by hand.

Owners: catalog/guests.json holds people, groups and their members, programmes and who appeared where;
config/public-dialogue-policy.json holds which structured transcripts are public;
config/speaker-names.json holds the host's names. From them this module rewrites the copies in
catalog/videos.jsonl (guest names, programme titles, the structured transcript path), lists a
group's programmes on the pages of members who have their own, numbers each person's appearances
by date, and writes the shared name table catalog/guest-names.json that the
website and Context Infra read. `python3 scripts/validate_release.py --write-manifest` runs it;
validation fails while any copy is stale.
"""

from __future__ import annotations

import argparse
import json
import re
import unicodedata
from pathlib import Path
from validate_guest_catalog import appearance_catalog

ROOT = Path(__file__).resolve().parents[1]
GUESTS = "catalog/guests.json"
VIDEOS = "catalog/videos.jsonl"
NAMES = "catalog/guest-names.json"
SPEAKERS = "config/speaker-names.json"
DIALOGUE_POLICY = "config/public-dialogue-policy.json"
APPEARANCES = "catalog/guest-appearances.jsonl"

# A name's key: NFKC, casefold, then drop whitespace and these marks. Consumers normalize a
# question the same way before looking a key up; KEY_EXAMPLES let them test that they do.
KEY_DROP = frozenset(" \t\r\n　·・•&/、,.。()[]【】{}「」『』<>《》\"'“”‘’-–—_@#:;!?|")
KEY_RULE = "NFKC, casefold, then drop whitespace and the characters " + "".join(sorted(KEY_DROP - set(" \t\r\n　")))
KEY_EXAMPLES = [["Leo（Charisma）", "leocharisma"], ["Leo Charisma", "leocharisma"], ["charisma-Leo", "charismaleo"],
                ["硅谷徐老师（Howie Xu）", "硅谷徐老师howiexu"], ["Koji & Monica", "kojimonica"], ["王臻 & Nick", "王臻nick"]]
PARENTHETICAL = re.compile(r"^(?P<base>.+?)\s*[（(](?P<inner>[^（）()]+)[）)]\s*$")
MEMBER_SEPARATOR = re.compile(r"\s*[&＆/／、,，]\s*")
COMPANY_SEPARATOR = re.compile(r"\s*[·・|｜/／]\s*")
DIALOGUE_NOTE = ("Discovery metadata for this programme. Its public structured transcript is at dialogue_path; "
                 "quote each unit by its recorded speaker, and do not infer Yuzheng's views from this catalog row.")


def name_key(text: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFKC", text).casefold() if char not in KEY_DROP)


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def json_text(value) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def jsonl_text(rows: list[dict]) -> str:
    return "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows)


def participants(catalog: dict) -> dict[str, list[str]]:
    """Each programme's people, by source ID, in the catalog's order."""
    relation: dict[str, list[str]] = {}
    for row in catalog["appearances"]:
        people = relation.setdefault(row["source_id"], [])
        if row["entity_id"] not in people:
            people.append(row["entity_id"])
    return relation


def member_appearances(catalog: dict) -> dict:
    """A member who has their own page also appears in every programme of their group."""
    have = {(row["entity_id"], row["source_id"]) for row in catalog["appearances"]}
    primary = {entity["entity_id"]: entity["primary_source_id"] for entity in catalog["entities"]}
    extra = []
    for group in catalog["entities"]:
        for member in group.get("members", []):
            member_id = member.get("entity_id")
            if not member_id:
                continue
            for row in catalog["appearances"]:
                if row["entity_id"] == group["entity_id"] and (member_id, row["source_id"]) not in have:
                    have.add((member_id, row["source_id"]))
                    extra.append({"entity_id": member_id, "source_id": row["source_id"], "index": 0,
                                  "is_primary": primary.get(member_id) == row["source_id"]})
    return {**catalog, "appearances": [*catalog["appearances"], *extra]}


def name_parts(text: str) -> list[str]:
    """The separate names a group's display name or alias lists (Koji & Monica, The Tech Roast Show（Austin、Jesse、Nikita）)."""
    match = PARENTHETICAL.match(text)
    base = match["base"].strip() if match else text
    parts = []
    for piece in ([base, match["inner"]] if match else [base]):
        split = [part.strip() for part in MEMBER_SEPARATOR.split(piece) if part.strip()]
        if len(split) > 1:
            parts.extend(split)
    return parts


def membership_errors(catalog: dict) -> list[str]:
    """A group's declared members and the names its display name and aliases list must agree."""
    entities = {entity["entity_id"]: entity for entity in catalog["entities"]}
    errors = []
    for group in catalog["entities"]:
        if group["entity_type"] != "group":
            continue
        members = group.get("members", [])
        known = set()
        for member in members:
            keys = {name_key(member["name"])} | ({name_key(member["en_name"])} if member.get("en_name") else set())
            if member.get("entity_id") in entities:
                person = entities[member["entity_id"]]
                keys |= {name_key(text) for text in [person["display_name"], *person["aliases"]]}
            known |= keys
        listed = {name_key(part) for text in [group["display_name"], *group["aliases"]] for part in name_parts(text)}
        missing = sorted(listed - known)
        if missing:
            errors.append(f"{group['entity_id']} lists names that are not declared members: {', '.join(missing)}")
        for member in members:
            keys = {name_key(member["name"])} | ({name_key(member["en_name"])} if member.get("en_name") else set())
            if not keys & listed and not member.get("entity_id"):
                errors.append(f"{group['entity_id']} member {member['name']} is not named by the group")
    return errors


def ordered_appearances(catalog: dict) -> dict:
    """Number each person's appearances 0, 1, 2… from their earliest programme."""
    dates = {source["source_id"]: source.get("published_at") or "" for source in catalog["sources"]}
    by_entity: dict[str, list[dict]] = {}
    for row in catalog["appearances"]:
        by_entity.setdefault(row["entity_id"], []).append(row)
    order = {}
    for entity_id, rows in by_entity.items():
        for position, row in enumerate(sorted(rows, key=lambda row: (dates[row["source_id"]], row["source_id"]))):
            order[(entity_id, row["source_id"])] = position
    appearances = [{**row, "index": order[(row["entity_id"], row["source_id"])]} for row in catalog["appearances"]]
    return {**catalog, "appearances": appearances}


def derived_videos(rows: list[dict], catalog: dict, dialogue_ids: set[str]) -> list[dict]:
    names = {entity["entity_id"]: entity["display_name"] for entity in catalog["entities"]}
    sources = {source["source_id"]: source for source in catalog["sources"]}
    people = participants(catalog)
    result = []
    for row in rows:
        row = dict(row)
        source_id = "youtube-" + row["video_id"]
        row["guest_names"] = sorted({names[entity_id] for entity_id in people.get(source_id, [])})
        source = sources.get(source_id)
        # The catalog keeps the programme's current title; a full-text row keeps the title its
        # bound file carries, and validation reports any difference for review.
        if source and not row.get("transcript_included"):
            row["title"] = source["title"]
        if row["video_id"] in dialogue_ids:
            row["dialogue_path"] = f"corpus/dialogues/youtube-{row['video_id']}.json"
            if not row.get("transcript_included"):
                row["attribution_note"] = DIALOGUE_NOTE
        else:
            row.pop("dialogue_path", None)
        result.append(row)
    return result


def entity_names(entity: dict) -> tuple[list[tuple[str, str]], list[str]]:
    """(name, kind) pairs that find this entity, and the qualifiers that tell it apart."""
    texts = [entity["display_name"], *entity["aliases"]]
    alias_keys = {name_key(text) for text in texts}
    found: list[tuple[str, str]] = []
    qualifiers: list[str] = []
    for text in texts:
        found.append((text, "display" if text == entity["display_name"] else "alias"))
    for text in texts:
        match = PARENTHETICAL.match(text)
        base = match["base"].strip() if match else text
        if match:
            found.append((base, "base"))
            inner = [part for part in MEMBER_SEPARATOR.split(match["inner"]) if part.strip()]
            if entity["entity_type"] == "group" and len(inner) > 1:
                pass  # the members, declared explicitly below
            elif name_key(match["inner"]) not in alias_keys:
                # A nickname, channel or programme label: it tells namesakes apart, and
                # people also search by it (宝二爷, Charisma, 品酒课).
                found.append((match["inner"].strip(), "qualifier"))
                qualifiers.append(match["inner"].strip())
    for member in entity.get("members", []):
        # A member with their own page is found through it; the others find the group.
        if not member.get("entity_id"):
            found.extend((name, "member") for name in (member["name"], member.get("en_name")) if name)
    for part in COMPANY_SEPARATOR.split(entity.get("guest_company") or ""):
        if part.strip():
            qualifiers.append(part.strip())
    return found, qualifiers


def name_table(catalog: dict, speakers: dict, appearances: list[dict] | None = None) -> dict:
    entries: dict[str, dict] = {}
    qualifiers: dict[str, list[dict]] = {}
    company_keys: dict[str, set[str]] = {}
    for entity in catalog["entities"]:
        for part in COMPANY_SEPARATOR.split(entity.get("guest_company") or ""):
            if name_key(part):
                company_keys.setdefault(name_key(part), set()).add(entity["entity_id"])
    for entity in catalog["entities"]:
        found, extra = entity_names(entity)
        for text, kind in found:
            key = name_key(text)
            if not key:
                continue
            entry = entries.setdefault(key, {"name": text.strip(), "key": key, "entity_ids": [], "kinds": []})
            if entity["entity_id"] not in entry["entity_ids"]:
                entry["entity_ids"].append(entity["entity_id"])
            if kind not in entry["kinds"]:
                entry["kinds"].append(kind)
        rows, seen = [], set()
        for text in extra:
            key = name_key(text)
            if key and key not in seen:
                seen.add(key)
                rows.append({"name": text, "key": key})
        if rows:
            qualifiers[entity["entity_id"]] = rows
    for appearance in appearances or []:
        for person in appearance["participants"]:
            identity = person["speaker_id"]
            if identity == "yuzheng":
                continue  # his names remain owned by config/speaker-names.json
            for text in [person["speaker_name"], *person.get("aliases", [])]:
                key = name_key(text)
                entry = entries.setdefault(key, {"name": text.strip(), "key": key, "entity_ids": [], "kinds": []})
                if identity not in entry["entity_ids"]:
                    entry["entity_ids"].append(identity)
                if "appearance-participant" not in entry["kinds"]:
                    entry["kinds"].append("appearance-participant")
            rows = qualifiers.setdefault(identity, [])
            for text in person.get("qualifiers", []):
                key = name_key(text)
                if key and not any(row["key"] == key for row in rows):
                    rows.append({"name": text, "key": key})
            if not rows:
                qualifiers.pop(identity, None)
    for entry in entries.values():
        # A label shared with other people's organization (Multi-FIRE) finds all of them.
        if "qualifier" in entry["kinds"]:
            for entity_id in company_keys.get(entry["key"], ()):
                if entity_id not in entry["entity_ids"]:
                    entry["entity_ids"].append(entity_id)
        entry["entity_ids"].sort()
    return {
        "schema_version": 1,
        "generated_from": [GUESTS, SPEAKERS] + ([APPEARANCES] if appearances is not None else []),
        "key_rule": KEY_RULE,
        "key_drop": "".join(sorted(KEY_DROP - set(" \t\r\n\u3000"))),
        "key_examples": KEY_EXAMPLES,
        "speakers": [{"speaker_id": row["speaker_id"], "role": row["role"],
                      "names": [{"name": name, "key": name_key(name)} for name in row["names"]]}
                     for row in speakers["speakers"]],
        "names": [entries[key] for key in sorted(entries)],
        "qualifiers": {entity_id: qualifiers[entity_id] for entity_id in sorted(qualifiers)},
    }


def outputs(root: Path = ROOT) -> dict[str, str]:
    """Every derived file's expected text, from the owning files as they are now."""
    catalog = ordered_appearances(member_appearances(read_json(root / GUESTS)))
    errors = membership_errors(catalog)
    if errors:
        raise ValueError("; ".join(errors))
    speakers = read_json(root / SPEAKERS)
    if speakers.get("schema_version") != 1 or not speakers.get("speakers"):
        raise ValueError("config/speaker-names.json is invalid")
    policy_path = root / DIALOGUE_POLICY
    dialogue_ids = {row["video_id"] for row in read_json(policy_path)["records"] if row.get("video_id")} if policy_path.is_file() else set()
    rows = [json.loads(line) for line in (root / VIDEOS).read_text(encoding="utf-8").splitlines() if line.strip()]
    return {
        GUESTS: json_text(catalog),
        VIDEOS: jsonl_text(derived_videos(rows, catalog, dialogue_ids)),
        NAMES: json_text(name_table(catalog, speakers, appearance_catalog(root) if (root / APPEARANCES).is_file() else None)),
    }


def write(root: Path = ROOT) -> list[str]:
    changed = []
    for relative, text in outputs(root).items():
        path = root / relative
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            path.write_text(text, encoding="utf-8")
            changed.append(relative)
    return changed


def validate(errors: list[str], root: Path = ROOT) -> None:
    try:
        expected = outputs(root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f"derived catalogs: {exc}")
        return
    for relative, text in expected.items():
        path = root / relative
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            errors.append(f"{relative} has stale derived fields; rerun python3 scripts/validate_release.py --write-manifest")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="only report stale derived files")
    args = parser.parse_args()
    if args.check:
        errors: list[str] = []
        validate(errors)
        print("\n".join(errors) or "derived catalogs are current")
        raise SystemExit(1 if errors else 0)
    print(json.dumps({"changed": write()}, ensure_ascii=False))


if __name__ == "__main__":
    main()
