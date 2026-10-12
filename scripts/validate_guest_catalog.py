#!/usr/bin/env python3
"""Validate public guest metadata and programme references; never assign turns."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ENTITY = re.compile(r"guest:[a-z0-9][a-z0-9-]*\Z")
VIDEO = re.compile(r"[A-Za-z0-9_-]{11}\Z")
SLUG = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
TYPES = {"person", "group", "virtual-character", "anonymous-label", "unresolved"}
PROFILE_STRINGS = {"guest_en_name", "guest_title", "guest_company", "guest_bio", "guest_bio_en", "interview_date"}
PROFILE_URLS = {"xiaohongshu_url", "linkedin_url", "youtube_playlist_url"}
MEMBER_FIELDS = frozenset({"name", "en_name", "entity_id"})
INTRO_FIELDS = frozenset({"source_id", "text", "quote", "locator", "start_seconds"})
UNIT_LOCATOR = re.compile(r"youtube-[A-Za-z0-9_-]{11}#cue-\d+\Z")
LINE_LOCATOR = re.compile(r"(corpus/videos/[^@\s]+\.md)@(\d+)\Z")
TIMED_LINE = re.compile(r"(?m)^\[(\d{2}):(\d{2}):(\d{2})\]\(https://www\.youtube\.com/watch\?v=[^)]+\)\s+(.+)$")
CATALOG_FIELDS = frozenset({"participant_entity_ids", "participant_names", "participant_aliases", "participant_metadata_basis", "attribution_note"})


def require(value, code):
    if not value:
        raise ValueError(code)


def strict_json(raw):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, "duplicate_json_key")
            result[key] = value
        return result
    return json.loads(raw, object_pairs_hook=pairs)


def safe_file(root, relative):
    require(isinstance(relative, str) and relative and not Path(relative).is_absolute(), "path_invalid")
    require(all(part not in {"..", ".", ""} for part in Path(relative).parts), "path_invalid")
    path = root / relative
    for parent in [path, *path.parents]:
        require(not parent.is_symlink(), "symlink_forbidden")
    require(path.is_file() and path.resolve().is_relative_to(root.resolve()), "file_required")
    return path


def url(value, image=False, social=False):
    require(isinstance(value, str) and bool(value), "url_type_invalid")
    if image and value.startswith("/"):
        require(not value.startswith("//") and ".." not in value.split("/") and "\\" not in value and not any(c in value for c in "?#"), "image_path_invalid")
        return
    p = urlsplit(value)
    require(p.scheme in ({"http", "https"} if social else {"https"}) and bool(p.hostname) and not p.username and not p.password and not p.fragment,
            "url_invalid")
    require(not any(c.isspace() for c in value) and "\\" not in value and p.port in {None, 443}, "url_invalid")


def video_id(value):
    url(value)
    p = urlsplit(value)
    if p.hostname == "youtu.be":
        candidate = p.path.strip("/")
    elif p.hostname in {"youtube.com", "www.youtube.com", "m.youtube.com"} and p.path == "/watch":
        ids = parse_qs(p.query).get("v", [])
        require(len(ids) == 1, "youtube_id_invalid")
        candidate = ids[0]
    else:
        raise ValueError("youtube_url_invalid")
    require(VIDEO.fullmatch(candidate), "youtube_id_invalid")
    return candidate


def strings(values, code):
    require(isinstance(values, list) and all(isinstance(v, str) and v for v in values) and len(set(values)) == len(values), code)


def finite_count(value, code):
    require(type(value) in {int, float} and math.isfinite(value) and value >= 0, code)


def validate_catalog(catalog, articles):
    require(type(catalog.get("schema_version")) is int and catalog["schema_version"] == 1, "catalog_schema_invalid")
    require(set(catalog) == {"schema_version", "entities", "sources", "appearances", "redirects"}, "catalog_fields_invalid")
    for name in ("entities", "sources", "appearances", "redirects"):
        require(isinstance(catalog[name], list), "catalog_array_invalid")
    entities, sources, slugs, pairs = {}, {}, {}, set()
    required = {"entity_id", "entity_type", "display_name", "aliases", "slug", "alias_slugs", "primary_source_id", "thumbnail_url"}
    allowed = required | PROFILE_STRINGS | PROFILE_URLS | {"community_resources", "members", "introductions"}
    for e in catalog["entities"]:
        require(isinstance(e, dict) and required <= set(e) <= allowed, "entity_fields_invalid")
        eid = e["entity_id"]
        require(isinstance(eid, str) and ENTITY.fullmatch(eid) and eid not in entities, "entity_id_invalid_or_duplicate")
        require(e["entity_type"] in TYPES and isinstance(e["display_name"], str) and e["display_name"], "entity_identity_invalid")
        strings(e["aliases"], "aliases_invalid"); strings(e["alias_slugs"], "alias_slugs_invalid")
        require(SLUG.fullmatch(e["slug"]) and e["slug"] in e["alias_slugs"], "slug_invalid")
        for slug in e["alias_slugs"]:
            require(SLUG.fullmatch(slug) and slug not in slugs, "slug_duplicate_or_invalid")
            slugs[slug] = eid
        for key in PROFILE_STRINGS & e.keys():
            require(isinstance(e[key], str), "profile_string_invalid")
        for key in PROFILE_URLS & e.keys():
            url(e[key], social=True)
        url(e["thumbnail_url"], image=True)
        resources = e.get("community_resources", [])
        require(isinstance(resources, list), "resources_invalid")
        for r in resources:
            require(isinstance(r, dict) and {"kind", "title", "url", "summary"} <= set(r) <= {"kind", "title", "url", "summary", "author"}, "resource_fields_invalid")
            require(r["kind"] in {"guest_post", "student_resource", "event"} and all(isinstance(v, str) for v in r.values()), "resource_type_invalid")
            url(r["url"])
        entities[eid] = e
    for e in entities.values():
        # A group names its members; a member who has their own page links to it by entity_id.
        if e["entity_type"] != "group":
            require("members" not in e, "members_only_for_groups")
            continue
        require(isinstance(e.get("members"), list), "group_members_required")
        names = set()
        for m in e["members"]:
            require(isinstance(m, dict) and "name" in m and set(m) <= MEMBER_FIELDS
                    and all(isinstance(v, str) and v.strip() == v and v for v in m.values()), "member_fields_invalid")
            require(m["name"] not in names, "member_duplicate")
            names.add(m["name"])
            if "entity_id" in m:
                target = entities.get(m["entity_id"])
                require(target is not None and target["entity_type"] == "person", "member_entity_invalid")
    for s in catalog["sources"]:
        required = {"source_id", "video_id", "source_type", "url", "title", "thumbnail_url"}
        require(isinstance(s, dict) and required <= set(s) <= required | {"published_at", "view_count", "metadata_verified_at"}, "source_fields_invalid")
        sid = s["source_id"]
        require(isinstance(sid, str) and sid not in sources and isinstance(s["title"], str) and bool(s["title"]), "source_id_duplicate_or_invalid")
        url(s["url"]); url(s["thumbnail_url"], image=True)
        if s["source_type"] == "youtube":
            require(isinstance(s["video_id"], str) and VIDEO.fullmatch(s["video_id"]) and sid == "youtube-" + s["video_id"] and video_id(s["url"]) == s["video_id"], "source_url_id_mismatch")
        else:
            require(s["source_type"] == "circle" and s["video_id"] is None and sid == s["url"], "circle_source_invalid")
        if "published_at" in s:
            require(isinstance(s["published_at"], str) and bool(s["published_at"]), "published_at_invalid")
        if "metadata_verified_at" in s:
            require(isinstance(s["metadata_verified_at"], str) and bool(s["metadata_verified_at"]), "metadata_verified_at_invalid")
        if "view_count" in s:
            finite_count(s["view_count"], "source_views_invalid")
        sources[sid] = s
    primaries, covered = set(), set()
    for r in catalog["appearances"]:
        require(isinstance(r, dict) and set(r) == {"entity_id", "source_id", "index", "is_primary"}, "appearance_fields_invalid")
        pair = (r["entity_id"], r["source_id"])
        require(pair[0] in entities and pair[1] in sources and pair not in pairs, "appearance_reference_or_duplicate")
        require(type(r["index"]) is int and r["index"] >= 0 and type(r["is_primary"]) is bool, "appearance_geometry_invalid")
        require(r["is_primary"] == (entities[pair[0]]["primary_source_id"] == pair[1]), "primary_reference_invalid")
        if r["is_primary"]:
            require(pair[0] not in primaries, "primary_duplicate")
            primaries.add(pair[0])
        pairs.add(pair); covered.add(pair[1])
    require(primaries == set(entities) and covered == set(sources), "catalog_coverage_incomplete")
    for e in entities.values():
        # Each introduction quotes, word for word, where a programme of theirs says who they are.
        seen_sources = set()
        for intro in e.get("introductions", []):
            require(isinstance(intro, dict) and set(intro) == INTRO_FIELDS, "introduction_fields_invalid")
            require(isinstance(intro["text"], str) and 0 < len(intro["text"].strip()) <= 60 and isinstance(intro["quote"], str) and intro["quote"].strip(),
                    "introduction_text_invalid")
            require((e["entity_id"], intro["source_id"]) in pairs and intro["source_id"] not in seen_sources, "introduction_source_invalid")
            require(isinstance(intro["locator"], list) and intro["locator"] and len(intro["locator"]) <= 20
                    and all(isinstance(x, str) and (UNIT_LOCATOR.fullmatch(x) or LINE_LOCATOR.fullmatch(x)) for x in intro["locator"]),
                    "introduction_locator_invalid")
            require(type(intro["start_seconds"]) is int and intro["start_seconds"] >= 0, "introduction_time_invalid")
            seen_sources.add(intro["source_id"])
        for m in e.get("members", []):
            if "entity_id" in m:
                require(all((m["entity_id"], sid) in pairs for gid, sid in pairs if gid == e["entity_id"]), "member_appearance_missing")
    redirects = set()
    for r in catalog["redirects"]:
        require(set(r) == {"from_entity_id", "canonical_entity_id"} and ENTITY.fullmatch(r["from_entity_id"]) and r["canonical_entity_id"] in entities and r["from_entity_id"] not in entities and r["from_entity_id"] not in redirects, "redirect_invalid")
        redirects.add(r["from_entity_id"])
    require(type(articles.get("schema_version")) is int and articles["schema_version"] == 1 and set(articles) == {"schema_version", "articles"} and isinstance(articles["articles"], list), "articles_schema_invalid")
    article_ids, article_urls = set(), set()
    for a in articles["articles"]:
        required = {"id", "entity_id", "original_guest_slug", "title", "summary", "url", "source_ids"}
        require(isinstance(a, dict) and required <= set(a) <= required | {"takeaways", "source_urls", "read_time_minutes"}, "article_fields_invalid")
        require(isinstance(a["id"], str) and a["id"] and a["id"] not in article_ids and a["url"] not in article_urls, "article_duplicate")
        require(a["entity_id"] in entities and slugs.get(a["original_guest_slug"]) == a["entity_id"], "article_entity_invalid")
        require(isinstance(a["title"], str) and isinstance(a["summary"], str), "article_text_type_invalid")
        url(a["url"]); strings(a["source_ids"], "article_sources_invalid")
        require(all((a["entity_id"], sid) in pairs for sid in a["source_ids"]), "article_source_reference_invalid")
        for field in ("takeaways", "source_urls"):
            if field in a:
                strings(a[field], "article_list_invalid")
        for u in a.get("source_urls", []):
            url(u)
            require(u in {sources[sid]["url"] for sid in a["source_ids"]}, "article_source_url_mismatch")
        if "read_time_minutes" in a:
            finite_count(a["read_time_minutes"], "article_read_time_invalid")
        article_ids.add(a["id"]); article_urls.add(a["url"])
    return {"entities": len(entities), "sources": len(sources), "appearances": len(pairs), "slug_routes": len(slugs), "articles": len(article_ids), "redirects": len(redirects)}


def programme_participants(catalog):
    relation = {}
    for r in catalog["appearances"]:
        relation.setdefault(r["source_id"], set()).add(r["entity_id"])
    return relation


def verify_raw_metadata(catalog, raw_records):
    """Bind source identities and reviewed speakers to the shared catalog."""
    relation = programme_participants(catalog)
    seen = set()
    for raw in raw_records:
        vid = raw.get("video_id")
        require(isinstance(vid, str) and VIDEO.fullmatch(vid) and vid not in seen and raw.get("id") == "youtube-" + vid and video_id(raw.get("source_url")) == vid, "raw_identity_invalid")
        seen.add(vid)
        expected = relation.get("youtube-" + vid, set())
        require(not (CATALOG_FIELDS & raw.keys()), "raw_catalog_metadata_duplicated")
        for unit in raw.get("units", []):
            speaker = unit.get("speaker_id", "unknown")
            require(speaker in {"unknown", "yuzheng"} or speaker in expected, "raw_speaker_programme_mismatch")
    return len(seen)


def validate_guest_catalog(root, verify_raw=True, verify_manifest=True):
    root = Path(root).absolute()
    catalog = strict_json(safe_file(root, "catalog/guests.json").read_bytes())
    articles = strict_json(safe_file(root, "catalog/guest-articles.json").read_bytes())
    counts = validate_catalog(catalog, articles)
    if verify_raw:
        entries = {}
        if verify_manifest:
            manifest = strict_json(safe_file(root, "release-manifest.json").read_bytes())
            entries = {r["path"]: r for r in manifest["files"]}
            require(len(entries) == len(manifest["files"]), "manifest_duplicate")
        policy = strict_json(safe_file(root, "config/public-dialogue-policy.json").read_bytes())
        records = []
        for r in policy["records"]:
            path = safe_file(root, r["corpus_path"]); data = path.read_bytes()
            digest = hashlib.sha256(data).hexdigest()
            require(digest == r["sha256"], "raw_hash_mismatch")
            if verify_manifest:
                require(digest == entries[r["corpus_path"]]["sha256"] and len(data) == entries[r["corpus_path"]]["bytes"], "raw_hash_mismatch")
            raw = strict_json(data)
            require(raw.get("video_id") == r.get("video_id"), "raw_policy_identity_mismatch")
            records.append(raw)
        counts["public_raw_records"] = verify_raw_metadata(catalog, records)
        counts["introductions"] = verify_introductions(root, catalog)
    return counts


def verify_introductions(root, catalog):
    """Every quoted introduction is exactly the transcript lines its locator names, from that programme."""
    transcripts = {}
    videos = {}

    def transcript_path(video):
        # Read only when a quote comes from a full-text video transcript.
        if not videos:
            for line in safe_file(root, "catalog/videos.jsonl").read_text(encoding="utf-8").splitlines():
                if line.strip():
                    row = json.loads(line)
                    videos[row["video_id"]] = row.get("corpus_path")
        return videos.get(video)
    sources = {s["source_id"]: s for s in catalog["sources"]}
    count = 0
    for e in catalog["entities"]:
        for intro in e.get("introductions", []):
            first = intro["locator"][0]
            if UNIT_LOCATOR.fullmatch(first):
                require(all(UNIT_LOCATOR.fullmatch(x) and x.startswith(intro["source_id"] + "#") for x in intro["locator"]), "introduction_locator_source_mismatch")
                if intro["source_id"] not in transcripts:
                    units = strict_json(safe_file(root, f"corpus/dialogues/{intro['source_id']}.json").read_bytes())["units"]
                    transcripts[intro["source_id"]] = {u["id"]: (index, u) for index, u in enumerate(units)}
                table = transcripts[intro["source_id"]]
                require(all(x in table for x in intro["locator"]), "introduction_unit_missing")
                indexes = [table[x][0] for x in intro["locator"]]
                require(indexes == list(range(indexes[0], indexes[0] + len(indexes))), "introduction_units_not_consecutive")
                texts = [table[x][1]["text"] for x in intro["locator"]]
                start = int(table[first][1]["start_seconds"])
            else:
                path = LINE_LOCATOR.fullmatch(first).group(1)
                video = sources[intro["source_id"]].get("video_id")
                require(transcript_path(video) == path and all(LINE_LOCATOR.fullmatch(x) and x.startswith(path + "@") for x in intro["locator"]),
                        "introduction_locator_source_mismatch")
                if path not in transcripts:
                    lines = {}
                    for m in TIMED_LINE.finditer(safe_file(root, path).read_text(encoding="utf-8")):
                        lines.setdefault(int(m.group(1)) * 3600 + int(m.group(2)) * 60 + int(m.group(3)), m.group(4))
                    transcripts[path] = lines
                table = transcripts[path]
                seconds = [int(LINE_LOCATOR.fullmatch(x).group(2)) for x in intro["locator"]]
                require(all(t in table for t in seconds) and seconds == sorted(seconds), "introduction_line_missing")
                texts = [table[t] for t in seconds]
                start = seconds[0]
            require(" ".join(t.strip() for t in texts) == intro["quote"], "introduction_quote_not_verbatim")
            require(start == intro["start_seconds"], "introduction_time_mismatch")
            count += 1
    return count


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).absolute().parents[1])
    args = p.parse_args()
    print(json.dumps(validate_guest_catalog(args.root), sort_keys=True))
