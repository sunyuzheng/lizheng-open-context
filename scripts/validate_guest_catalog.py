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
    allowed = required | PROFILE_STRINGS | PROFILE_URLS | {"community_resources"}
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
    return counts


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root", type=Path, default=Path(__file__).absolute().parents[1])
    args = p.parse_args()
    print(json.dumps(validate_guest_catalog(args.root), sort_keys=True))
