#!/usr/bin/env python3
"""Fail closed on common privacy, provenance, rights, and release-integrity mistakes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import unicodedata
from datetime import datetime
from pathlib import Path
from urllib.parse import unquote

import build_index
import rights
from rights import REFERENCE_USE, RETAINED


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "release-manifest.json"
SCAN_DIRS = (
    ROOT / "LICENSES",
    ROOT / "index",
    ROOT / "context",
    ROOT / "corpus",
    ROOT / "catalog",
    ROOT / "config",
    ROOT / "docs",
    ROOT / "evals",
    ROOT / "examples",
)
SCAN_ROOT_FILES = (
    ROOT / "README.md",
    ROOT / "INDEX.md",
    ROOT / "CHANGELOG.md",
    ROOT / "LICENSE.md",
    ROOT / "AGENTS.md",
    ROOT / "CONTRIBUTING.md",
    ROOT / "LICENSE-CONTENT.md",
)
SENSITIVE_PATTERNS = {
    "email address": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    "mainland phone": re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)"),
    "macOS absolute path": re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    "Windows absolute path": re.compile(r"[A-Za-z]:\\\\Users\\\\"),
    "Google API key": re.compile(r"AIza[0-9A-Za-z_-]{30,}"),
    "GitHub token": re.compile(r"gh[pousr]_[0-9A-Za-z]{20,}"),
    "generic secret assignment": re.compile(
        r"(?i)(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*['\"][^'\"]{8,}"
    ),
}
FORBIDDEN_FIELDS = ('"user_email"', '"user_id"', '"community_id"')
URL_PATTERN = re.compile(r"https?://[^\s)\]>'\"]+", re.IGNORECASE)
BARE_DOMAIN_PATTERN = re.compile(
    r"(?<![@\w])(?:[A-Za-z0-9-]+\.)+(?:com|org|net|io|ai|co|cn)(?:/[^\s]*)?",
    re.IGNORECASE,
)
COMMENT_SENSITIVE_PATTERN = re.compile(
    r"(?:therapist|治疗师|心理咨询|抑郁|sponsor(?:ship)?|月收入|工资|薪资|报酬|"
    r"财务状况|PERM|EB-?1A|绿卡|被裁|裁员|未成年|\b17\s*岁|生病|离世|去世|"
    r"戒烟|伴侣|老婆|老公|男朋友|女朋友|私下|社群不赚钱|接管.{0,12}运营|"
    r"退款|refund|老学员|新学员|购买|优惠|折扣|报名|名额|课程|qualify|"
    r"付款|price|价格|预算|订单|客服|发票|上课|开课|lifetime|"
    r"\bcourse\b|\bmaven\b|\bcohort\b|self[- ]paced|"
    r"每月\s*\$?\s*\d+|\$\s*\d+.{0,12}(?:month|月)|"
    r"(?:跟|和|与).{0,12}(?:聊完|聊天|交流))",
    re.IGNORECASE,
)
PROVENANCE_FIELDS = (
    "author", "publisher", "original_author", "original_source_url", "original_published_at",
    "content_origin", "generation_method", "evidence_role", "yuzheng_stance_weight",
    "attribution_note", "source_family", "source_context", "language", "license",
    "source_video_id", "generated_at", "translation_publication_status", "original_language",
    "source_visibility", "text_access", "membership_platform", "membership_url",
    "membership_verified_at", "transcript_source_kind", "transcript_quality",
    "inclusion_authorization", "publication_date_provenance", "transcript_source_sha256", "archived_transcript_sha256",
)
REQUIRED_PROVENANCE = (
    "content_origin", "generation_method", "evidence_role", "yuzheng_stance_weight", "attribution_note",
)
AI_SYNTHESIS_ORIGINS = {"ai-synthesis", "ai-synthesis-of-mixed-sources"}


SOLO_REVIEW_AUTHORIZATION = "maintainer-request-2026-10-03-member-solo-speech"


def validate_member_video(row: dict, policy: dict, errors: list[str], solo_ids: frozenset[str] = frozenset()) -> None:
    approved = {item["video_id"]: item for item in policy.get("records", [])}.get(row.get("video_id"))
    label = str(row.get("id"))
    if not approved:
        errors.append(f"{label}: member video is not in the explicit snapshot policy")
        return
    expected = {
        "source_visibility": "members-only", "text_access": "public", "membership_platform": "youtube",
        "membership_url": policy.get("membership_url"), "membership_verified_at": policy.get("snapshot_at"),
        "inclusion_authorization": policy.get("authorization"), "published_at": approved["published_at"],
    }
    for key, value in expected.items():
        if row.get(key) != value:
            errors.append(f"{label}: invalid member provenance {key}")
    if not row.get("transcript_included") or not row.get("transcript_quality"):
        errors.append(f"{label}: authorized member video lacks transcript/quality provenance")
    if row.get("rights_scope") == "first-party":
        if not approved.get("prior_solo_transcript") or row.get("guest_names"):
            errors.append(f"{label}: member selection does not establish solo first-party ownership")
    elif row.get("rights_scope") != "publisher-authorized-transcript":
        errors.append(f"{label}: unexpected member transcript rights scope")
    if row.get("rights_scope") == "publisher-authorized-transcript":
        solo = row.get("video_id") in solo_ids
        expected = {
            "review_status": "maintainer-authorized", "license": REFERENCE_USE,
            "transcript_source_kind": approved["transcript_source_kind"], "transcript_source_sha256": approved["transcript_sha256"],
        }
        if solo:
            # Reviewed as Yuzheng speaking alone: his own speech, still member content.
            expected.update(speaker_classification="solo-yuzheng", content_origin="yuzheng-spoken-source",
                            yuzheng_stance_weight="direct-with-quotation-boundaries", evidence_role="primary-speech",
                            author="Yuzheng Sun", original_author="Yuzheng Sun")
            if approved.get("guest_names"):
                errors.append(f"{label}: a member video with named guests cannot be reviewed as solo speech")
        else:
            expected.update(speaker_classification="mixed-or-unresolved", content_origin="mixed-or-unresolved-speech",
                            yuzheng_stance_weight="not-evidence", evidence_role="speaker-attributed-speech")
            if row.get("author") == "Yuzheng Sun" or row.get("author") != row.get("original_author"):
                errors.append(f"{label}: member transcript cannot assign unresolved speakers to Yuzheng")
        for key, value in expected.items():
            if row.get(key) != value:
                kind = "solo" if solo else "mixed"
                errors.append(f"{label}: invalid {kind} member transcript attribution {key}")


COURSE_AUTHORIZATION = "maintainer-request-2026-10-03-zhenbenshi-course-text"
COURSE_URL = "https://www.superlinear.academy/c/work-wealth"


def validate_member_course(row: dict, policy: dict, errors: list[str]) -> None:
    """One 《真本事》 lesson text: exactly as authorized, first-party, reference use only, video access unchanged."""
    approved = {item["lesson_id"]: item for item in policy.get("records", [])}.get(row.get("lesson_id"))
    label = str(row.get("id"))
    if not approved:
        errors.append(f"{label}: course lesson is not in the explicit course text policy")
        return
    expected = {
        "id": f"circle-lesson-{approved['lesson_id']}", "title": approved["title"], "published_at": approved["published_at"],
        "url": f"{COURSE_URL}/sections/{approved['section_id']}/lessons/{approved['lesson_id']}",
        "source_type": "course-lesson", "rights_scope": "publisher-authorized-course-text",
        "license": REFERENCE_USE, "review_status": "maintainer-authorized",
        "author": "Yuzheng Sun", "original_author": "Yuzheng Sun", "publisher": "Yuzheng Sun",
        "content_origin": "yuzheng-published-text", "evidence_role": "published-source",
        "yuzheng_stance_weight": "direct-with-quotation-boundaries",
        "source_visibility": "members-only", "text_access": "public", "membership_platform": "superlinear",
        "membership_url": policy.get("membership_url"), "inclusion_authorization": policy.get("authorization"),
        "full_text_included": True,
    }
    for key, value in expected.items():
        if row.get(key) != value:
            errors.append(f"{label}: invalid course lesson provenance {key}")


CHINESE_EDITIONS_AUTHORIZATION = "maintainer-request-2026-10-04-chinese-editions"
CHINESE_EDITION_FIELDS = {
    "author": "AI", "publisher": "Yuzheng Sun", "rights_scope": "publisher-authorized-adaptation", "license": REFERENCE_USE,
    "review_status": "maintainer-authorized", "content_origin": "ai-translation", "generation_method": "ai-translation",
    "evidence_role": "translation", "yuzheng_stance_weight": "verify-original", "language": "zh", "original_language": "en",
    "source_visibility": "public", "text_access": "public", "inclusion_authorization": CHINESE_EDITIONS_AUTHORIZATION,
    "full_text_included": True, "third_party_exclusions": True,
}


def validate_chinese_editions(book_rows: list[dict], blog_rows: list[dict], policy: dict, errors: list[str]) -> None:
    """The Chinese book chapters and blog posts: exactly the pinned texts, AI rewrites that defer to the English originals."""
    if not (book_rows or blog_rows or policy):
        return
    if policy.get("authorization") != CHINESE_EDITIONS_AUTHORIZATION:
        errors.append("Chinese edition policy lacks explicit maintainer authorization")
        return
    book = policy.get("book") or {}
    blog = policy.get("blog") or {}
    groups = (
        (book_rows, {f"gdap-zh-{item['key']}": {**item, "published_at": book.get("published_at")} for item in book.get("entries", [])},
         "corpus/book-chapters", "book-chapter"),
        (blog_rows, {f"statsig-blog-{item['key']}-zh": item for item in blog.get("posts", [])}, "corpus/blog-posts", "blog-post"),
    )
    for rows, approved, folder, source_type in groups:
        if sorted(row.get("id") for row in rows) != sorted(approved):
            errors.append(f"{folder}: catalog differs from the reviewed Chinese edition policy")
        for row in rows:
            label = str(row.get("id"))
            item = approved.get(row.get("id"))
            if not item:
                continue
            expected = {**CHINESE_EDITION_FIELDS, "source_type": source_type, "url": item["url"],
                        "published_at": item["published_at"], "title": (row.get("title") if source_type == "book-chapter" else item["title"])}
            for key, value in expected.items():
                if row.get(key) != value:
                    errors.append(f"{label}: invalid Chinese edition provenance {key}")
            if "Yuzheng Sun" not in str(row.get("original_author", "")).split(", "):
                errors.append(f"{label}: a Chinese edition must name Yuzheng among the original authors")
            if source_type == "blog-post" and row.get("original_author") != ", ".join(item["authors"]):
                errors.append(f"{label}: blog post authors differ from the reviewed byline")
        actual = {str(path.relative_to(ROOT)) for path in (ROOT / folder).glob("*.md")}
        if actual != {row.get("corpus_path") for row in rows}:
            errors.append(f"{folder}: catalog/files mismatch")


VALUES_AUTHORIZATION = "maintainer-request-2026-10-04-values-conversations"
PUBLIC_CONVERSATION_FIELDS = {
    "rights_scope": "publisher-authorized-transcript", "license": REFERENCE_USE, "speaker_classification": "mixed-or-unresolved",
    "review_status": "maintainer-authorized", "content_origin": "mixed-or-unresolved-speech",
    "evidence_role": "speaker-attributed-speech", "yuzheng_stance_weight": "not-evidence", "source_visibility": "public",
    "text_access": "public", "inclusion_authorization": VALUES_AUTHORIZATION, "transcript_included": True,
}
EXCERPT_FIELDS = {
    "author": "Yuzheng Sun", "publisher": "Yuzheng Sun", "original_author": "Yuzheng Sun", "source_type": "video-excerpt",
    "rights_scope": "publisher-reviewed-speaker-excerpt", "speaker_classification": "yuzheng-turns-reviewed",
    "review_status": "maintainer-authorized", "third_party_exclusions": True, "content_origin": "yuzheng-spoken-source",
    "generation_method": "speaker-reviewed-excerpt", "evidence_role": "primary-speech",
    "yuzheng_stance_weight": "direct-with-quotation-boundaries", "language": "zh", "text_access": "public",
    "inclusion_authorization": VALUES_AUTHORIZATION, "full_text_included": True,
}
CUE_LINE = re.compile(r"^\[(\d{2}):(\d{2}):(\d{2})\]\([^)]+\)\s*(.*)$", re.M)
EXCERPT_LINK = re.compile(r"\[(\d{2}:\d{2}:\d{2})\]\(https://www\.youtube\.com/watch\?v=([A-Za-z0-9_-]{11})&t=(\d+)s\)")


def quote_key(text: str) -> str:
    """Words only: what a quotation must share with its transcript, whatever the punctuation and spacing."""
    return "".join(char for raw in text for char in unicodedata.normalize("NFKC", raw).lower()
                   if unicodedata.category(char)[0] not in "PZSC")


def validate_excerpt_quotes(path: Path, video_id: str, transcript: Path, errors: list[str]) -> int:
    """Every quotation in a reviewed excerpt file appears verbatim, in order, at its stated moment of the transcript."""
    label = str(path.relative_to(ROOT)) if path.resolve().is_relative_to(ROOT.resolve()) else path.name
    _, body = read_markdown(path)
    _, text = read_markdown(transcript)
    words, seconds, cue_starts = [], [], []
    for match in CUE_LINE.finditer(text):
        start = int(match[1]) * 3600 + int(match[2]) * 60 + int(match[3])
        key = quote_key(match[4])
        cue_starts.append((start, len(seconds)))
        words.append(key)
        seconds.extend([start] * len(key))
    words = "".join(words)
    count = 0
    for section in re.split(r"(?m)^## ", body)[1:]:
        heading = section.splitlines()[0]
        link = EXCERPT_LINK.search(section)
        quote = "".join(line[2:] for line in section.splitlines() if line.startswith("> "))
        if not link or not quote or link[2] != video_id or not heading.startswith(link[1]):
            errors.append(f"{label}: excerpt '{heading}' lacks its timestamp link or quotation")
            continue
        h, m, s = map(int, link[1].split(":"))
        if h * 3600 + m * 60 + s != int(link[3]):
            errors.append(f"{label}: excerpt '{heading}' has inconsistent timestamps")
        # Search from the stated moment: an opening teaser can repeat the same sentence earlier.
        position = next((offset for start, offset in cue_starts if start >= int(link[3])), len(words))
        first = None
        for segment in quote.split("……"):
            key = quote_key(segment)
            found = words.find(key, position) if len(key) >= 2 else -1
            if found < 0:
                errors.append(f"{label}: quotation at {link[1]} does not match the transcript verbatim")
                first = None
                break
            first = seconds[found] if first is None else first
            position = found + len(key)
        else:
            if first != int(link[3]):
                errors.append(f"{label}: quotation at {link[1]} starts at a different moment of the transcript")
        count += 1
    return count


def validate_values_conversations(video_rows: list[dict], excerpt_rows: list[dict], policy: dict,
                                  member_ids: set[str], errors: list[str]) -> set[str]:
    """The six public conversation transcripts and the reviewed excerpts of Yuzheng's own turns, exactly as pinned."""
    if not (excerpt_rows or policy):
        return set()
    if policy.get("authorization") != VALUES_AUTHORIZATION:
        errors.append("Values conversation policy lacks explicit maintainer authorization")
        return set()
    videos = {row.get("video_id"): row for row in video_rows}
    public = {item["video_id"]: item for item in policy.get("public_transcripts", [])}
    for identity, item in public.items():
        row = videos.get(identity, {})
        expected = {**PUBLIC_CONVERSATION_FIELDS, "title": item["title"], "published_at": item["published_at"],
                    "guest_names": item["guest_names"], "transcript_source_kind": item["transcript_source_kind"],
                    "transcript_source_sha256": item["transcript_sha256"]}
        for key, value in expected.items():
            if row.get(key) != value:
                errors.append(f"youtube-{identity}: invalid public conversation transcript {key}")
        if identity in member_ids or not row.get("guest_names"):
            errors.append(f"youtube-{identity}: a public conversation must be a non-member video with named guests")
    if {row.get("video_id") for row in video_rows if row.get("inclusion_authorization") == VALUES_AUTHORIZATION} != set(public):
        errors.append("Public conversation policy/catalog exact ID mismatch")
    conversations = {item["excerpt_path"]: item for item in policy.get("conversations", [])}
    if sorted(row.get("corpus_path") for row in excerpt_rows) != sorted(conversations):
        errors.append("Conversation excerpt policy/catalog exact mismatch")
    actual = {str(path.relative_to(ROOT)) for path in (ROOT / "corpus/conversation-excerpts").glob("*.md")}
    if actual != set(conversations):
        errors.append("conversation excerpt catalog/files mismatch")
    if not policy.get("removal") or set(policy.get("guests", {})) != {name for item in conversations.values() for name in item["guest_names"]}:
        errors.append("Values conversation policy lacks its removal route or a guest introduction")
    for item in conversations.values():
        transcript = ROOT / item["source_transcript"]
        text = transcript.read_text(encoding="utf-8") if transcript.is_file() else ""
        # Every conversation opens by naming its guests, whose words are theirs, and where his own words are.
        if "<!-- values-conversation:start -->" not in text or f"../conversation-excerpts/{Path(item['excerpt_path']).name}" not in text:
            errors.append(f"{item['source_transcript']}: conversation transcript lacks its opening note")
    for row in excerpt_rows:
        label = str(row.get("id"))
        item = conversations.get(row.get("corpus_path"))
        if not item:
            continue
        identity = row.get("video_id")
        video = videos.get(identity, {})
        member = identity in member_ids
        url = f"https://www.youtube.com/watch?v={identity}"
        expected = {**EXCERPT_FIELDS, "id": f"youtube-{identity}-yuzheng", "url": url, "source_family": url,
                    "license": REFERENCE_USE if member else "CC-BY-4.0", "source_visibility": "members-only" if member else "public",
                    "published_at": video.get("published_at"), "source_transcript": video.get("corpus_path"),
                    "transcript_source_kind": video.get("transcript_source_kind"), "transcript_quality": video.get("transcript_quality"),
                    "guest_names": item["guest_names"], "excerpt_count": item["excerpt_count"]}
        if member:
            expected.update({key: video.get(key) for key in ("membership_platform", "membership_url", "membership_verified_at")})
        for key, value in expected.items():
            if row.get(key) != value:
                errors.append(f"{label}: invalid conversation excerpt provenance {key}")
        if not video.get("transcript_included") or not (member or identity in public):
            errors.append(f"{label}: excerpt source is not an included member or reviewed public conversation")
            continue
        path = ROOT / str(row.get("corpus_path"))
        if not path.is_file():
            continue
        if sha256(path) != item["excerpt_sha256"]:
            errors.append(f"{label}: excerpt file differs from the reviewed snapshot")
        if validate_excerpt_quotes(path, identity, ROOT / video["corpus_path"], errors) != row.get("excerpt_count"):
            errors.append(f"{label}: excerpt count differs from its file")
    return set(public)


def read_markdown(path: Path) -> tuple[dict, str]:
    text = path.read_text(encoding="utf-8")
    resolved = path.resolve()
    label = str(resolved.relative_to(ROOT.resolve())) if resolved.is_relative_to(ROOT.resolve()) else path.name
    match = re.match(r"\A---\n(.*?)\n---\n", text, re.S)
    if not match:
        raise ValueError(f"{label}: missing front matter")
    meta = {}
    for line in match[1].splitlines():
        if not line.strip():
            continue
        if ":" not in line:
            raise ValueError(f"{label}: invalid front matter")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip()
        if key in meta:
            raise ValueError(f"{label}: duplicate front matter key {key}")
        try:
            meta[key] = json.loads(value)
        except json.JSONDecodeError:
            meta[key] = value
    body = re.sub(r"<!-- provenance:start -->.*?<!-- provenance:end -->", "", text[match.end():], flags=re.S)
    return meta, body.lstrip()


def authorized_publisher_text(row: dict) -> bool:
    if row.get("rights_scope") != "first-party":
        return False
    if row.get("author") == "Yuzheng Sun":
        return True
    return (
        row.get("author") == "AI"
        and row.get("publisher") == "Yuzheng Sun"
        and row.get("content_origin") in AI_SYNTHESIS_ORIGINS
        and row.get("generation_method") == "ai-written"
        and row.get("evidence_role") == "secondary-synthesis"
        and row.get("yuzheng_stance_weight") == "secondary-only"
    )


def validate_provenance(row: dict, label: str, errors: list[str], *, full_text: bool) -> None:
    for field in REQUIRED_PROVENANCE:
        if not row.get(field):
            errors.append(f"{label}: missing provenance field {field}")
    if full_text:
        for field in ("author", "publisher", "original_author", "source_family", "language", "license"):
            if not row.get(field):
                errors.append(f"{label}: missing provenance field {field}")
    is_synthesis = (
        (row.get("author") == "AI" and row.get("generation_method") != "ai-translation")
        or row.get("content_origin") in AI_SYNTHESIS_ORIGINS
        or row.get("generation_method") == "ai-written"
        or row.get("evidence_role") == "secondary-synthesis"
    )
    if is_synthesis and not (
        row.get("author") == "AI" and row.get("publisher") == "Yuzheng Sun"
        and row.get("content_origin") in AI_SYNTHESIS_ORIGINS
        and row.get("generation_method") == "ai-written"
        and row.get("evidence_role") == "secondary-synthesis"
        and row.get("yuzheng_stance_weight") == "secondary-only"
    ):
        errors.append(f"{label}: AI synthesis must retain AI authorship and secondary-only evidence")
    third_party = row.get("content_origin") == "third-party-community" or row.get("rights_scope") == "third-party-reference"
    if third_party:
        if row.get("yuzheng_stance_weight") != "not-evidence":
            errors.append(f"{label}: third-party content cannot establish Yuzheng's stance")
        if full_text and row.get("license") != RETAINED:
            errors.append(f"{label}: third-party content must retain original rights, not a repository CC license")
        if row.get("author") != row.get("original_author") or row.get("author") in {"AI", "Yuzheng Sun"}:
            errors.append(f"{label}: third-party author attribution is inconsistent")
    if row.get("content_origin") == "yuzheng-derivative":
        if row.get("original_author") != "Yuzheng Sun" or row.get("yuzheng_stance_weight") != "verify-original":
            errors.append(f"{label}: Yuzheng derivative must defer to its original source")
        if not row.get("original_source_url") or row.get("source_family") != row.get("original_source_url"):
            errors.append(f"{label}: derivative lacks its original source family")
    if not full_text or row.get("content_origin") == "metadata-only":
        if row.get("yuzheng_stance_weight") != "not-evidence" or row.get("evidence_role") != "discovery-only":
            errors.append(f"{label}: metadata-only source cannot establish a stance")
        if full_text:
            errors.append(f"{label}: metadata-only source has full text")


def validate_catalog_bindings(catalogs: list[tuple[str, list[dict]]], errors: list[str]) -> None:
    bound_files: set[str] = set()
    metadata_cache: dict[str, dict] = {}
    for name, rows in catalogs:
        ids = [row.get("id") for row in rows]
        if len(ids) != len(set(ids)):
            errors.append(f"{name}: duplicate source IDs")
        for row in rows:
            label = f"{name}:{row.get('id')}"
            included = bool(row.get("full_text_included") or row.get("transcript_included"))
            validate_provenance(row, label, errors, full_text=included)
            relative = row.get("corpus_path")
            if bool(relative) != included:
                errors.append(f"{label}: full-text flag/corpus binding mismatch")
            if not relative:
                continue
            path = (ROOT / relative).resolve()
            try:
                path.relative_to((ROOT / "corpus").resolve())
            except ValueError:
                errors.append(f"{label}: corpus path escapes corpus directory")
                continue
            bound_files.add(str(path.relative_to(ROOT.resolve())))
            if not path.is_file():
                errors.append(f"{label}: bound corpus file is missing: {relative}")
                continue
            meta = metadata_cache.setdefault(relative, read_markdown(path)[0])
            for field in ("id", "title", "published_at", "rights_scope", *PROVENANCE_FIELDS):
                if field == "source_visibility" and row.get("source_type") not in {"video-transcript", "video-translation"}:
                    # A catalog's public discovery surface can link to an
                    # author-authorized body originally from a member space.
                    continue
                if row.get(field) != meta.get(field):
                    errors.append(f"{label}: catalog/file attribution mismatch for {field}")
            for field in ("speaker_classification", "review_status", "third_party_exclusions", "cue_alignment_status"):
                if field in row and row.get(field) != meta.get(field):
                    errors.append(f"{label}: catalog/file evidence mismatch for {field}")
            if row.get("url") != meta.get("source_url"):
                errors.append(f"{label}: catalog/file source URL mismatch")
    actual_files = {str(p.relative_to(ROOT)) for p in (ROOT / "corpus").rglob("*.md")}
    for unexpected in sorted(actual_files - bound_files):
        errors.append(f"{unexpected}: unexpected corpus file without a catalog binding")
    for relative, meta in metadata_cache.items():
        validate_provenance(meta, relative, errors, full_text=True)


def validate_english_sources(rows: list[dict], policy: dict, errors: list[str]) -> None:
    allowed = policy.get("included_post_ids", [])
    if len(allowed) != len(set(allowed)):
        errors.append("English source policy has duplicate IDs")
    expected_ids = {f"circle-{identity}" for identity in allowed}
    if {row.get("id") for row in rows} != expected_ids or len(rows) != len(expected_ids):
        errors.append("English source policy/catalog exact ID mismatch")
    if policy.get("space_id") != 2413136 or policy.get("source_visibility") != "public":
        errors.append("English source policy must identify the reviewed public English space")
    expected_files = set()
    for row in rows:
        label = str(row.get("id"))
        if row.get("language") != "en" or not str(row.get("url", "")).startswith("https://www.superlinear.academy/c/ai-resources-en/"):
            errors.append(f"{label}: unexpected English source language or URL")
        if not row.get("full_text_included") or not row.get("corpus_path"):
            errors.append(f"{label}: English source lacks its reviewed corpus binding")
            continue
        relative = str(row["corpus_path"])
        if relative.startswith("corpus/english-community/"):
            expected_files.add(relative)
        elif not relative.startswith("corpus/community-posts/") or not authorized_publisher_text(row):
            errors.append(f"{label}: invalid shared English corpus binding")
        path = ROOT / relative
        if path.is_file():
            meta, _ = read_markdown(path)
            if meta.get("source_visibility") != "public":
                errors.append(f"{label}: English corpus source is not public")
    actual_files = {str(p.relative_to(ROOT)) for p in (ROOT / "corpus/english-community").glob("*.md")}
    if expected_files != actual_files:
        errors.append("English source catalog/files mismatch")


def validate_translations(rows: list[dict], videos: list[dict], allowlist: set[str], errors: list[str]) -> None:
    video_by_id = {row.get("video_id"): row for row in videos}
    source_ids = [row.get("source_video_id") for row in rows]
    if len(source_ids) != len(set(source_ids)):
        errors.append("English translations contain duplicate source videos")
    for row in rows:
        label = str(row.get("id"))
        identity = row.get("source_video_id")
        video = video_by_id.get(identity, {})
        if identity not in allowlist or not video.get("transcript_included"):
            errors.append(f"{label}: translation source is not an included allowlisted solo video")
        url = f"https://www.youtube.com/watch?v={identity}"
        if row.get("id") != f"youtube-{identity}-en-ai" or any(row.get(k) != url for k in ("url", "source_family", "original_source_url")):
            errors.append(f"{label}: translation source identity/family mismatch")
        expected = {
            "author": "AI", "publisher": "Yuzheng Sun", "original_author": "Yuzheng Sun",
            "source_type": "video-translation", "content_origin": "ai-translation",
            "generation_method": "ai-translation", "evidence_role": "translation",
            "yuzheng_stance_weight": "verify-original", "language": "en",
            "rights_scope": "first-party-derivative", "license": "CC-BY-4.0",
            "translation_publication_status": "repository-reading-aid-not-platform-publication",
            "third_party_exclusions": True,
        }
        for key, value in expected.items():
            if row.get(key) != value:
                errors.append(f"{label}: translation attribution mismatch for {key}")
        generated_at = row.get("generated_at")
        try:
            if not isinstance(generated_at, str):
                raise ValueError("missing generation date")
            datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        except ValueError:
            errors.append(f"{label}: missing or invalid translation generation date")
        if not row.get("published_at") or row.get("published_at") != video.get("published_at"):
            errors.append(f"{label}: translation must preserve original video publication date")
        if not row.get("full_text_included") or not str(row.get("corpus_path", "")).startswith("corpus/english-translations/"):
            errors.append(f"{label}: translation lacks its corpus binding")
    expected_files = {row.get("corpus_path") for row in rows}
    actual_files = {str(p.relative_to(ROOT)) for p in (ROOT / "corpus/english-translations").glob("*.md")}
    if expected_files != actual_files:
        errors.append("English translation catalog/files mismatch")


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.relative_to(ROOT)}:{number}: invalid JSON: {exc}") from exc
    return rows


def read_json_object_without_duplicate_keys(path: Path) -> dict:
    def pairs_hook(pairs: list[tuple[str, object]]) -> dict:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"{path.relative_to(ROOT)}: duplicate key {key}")
            result[key] = value
        return result

    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=pairs_hook)


def read_allowlist(path: Path) -> set[str]:
    values = [
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    if len(values) != len(set(values)):
        raise ValueError(f"{path.relative_to(ROOT)}: duplicate video IDs")
    return set(values)


def release_paths() -> list[str]:
    """Every published path, including the manifest that describes the others."""
    return [str(path.relative_to(ROOT)) for path in public_files()] + ["release-manifest.json"]


def public_files() -> list[Path]:
    files = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        if relative == Path("release-manifest.json"):
            continue
        # .github holds this repository's own automation (it tells ask-lizheng a release is out); it is
        # not release content, and the Ask's sync refuses hidden paths in the manifest.
        if any(part in {".git", ".github", ".source-cache", "__pycache__"} for part in relative.parts):
            continue
        files.append(path)
    return sorted(files, key=lambda path: str(path.relative_to(ROOT)))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_sensitive_data(errors: list[str]) -> None:
    scan_files = [path for path in SCAN_ROOT_FILES if path.is_file()]
    for directory in SCAN_DIRS:
        if directory.exists():
            scan_files.extend(path for path in directory.rglob("*") if path.is_file())
    for path in scan_files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for label, pattern in SENSITIVE_PATTERNS.items():
            scan = text
            if label == "mainland phone":
                # Locked transcript/file hashes can contain phone-shaped runs.
                # Ignore only named 64-hex checksum values, never prose numbers.
                scan = re.sub(r'(?m)(["\w]*sha256[" ]*:\s*)"[a-f0-9]{64}"', r'\1"[checksum]"', text)
            if pattern.search(scan):
                errors.append(f"{path.relative_to(ROOT)}: possible {label}")
        if path.suffix == ".jsonl":
            for field in FORBIDDEN_FIELDS:
                if field in text:
                    errors.append(f"{path.relative_to(ROOT)}: forbidden private field {field}")


def validate_internal_links(errors: list[str]) -> None:
    link_pattern = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
    for path in public_files():
        if path.suffix.lower() != ".md":
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for raw_target in link_pattern.findall(text):
            target = raw_target.strip().split("#", 1)[0]
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
                continue
            decoded = unquote(target)
            resolved = (path.parent / decoded).resolve()
            try:
                resolved.relative_to(ROOT.resolve())
            except ValueError:
                errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {raw_target}")
                continue
            if not resolved.exists():
                errors.append(f"{path.relative_to(ROOT)}: broken internal link: {raw_target}")


def validate_rights(errors: list[str]) -> dict[str, int]:
    kb_catalog_path = ROOT / "catalog" / "knowledge-bank.jsonl"
    community_posts_catalog_path = ROOT / "catalog" / "community-posts.jsonl"
    community_comments_catalog_path = ROOT / "catalog" / "community-comments.jsonl"
    video_catalog_path = ROOT / "catalog" / "videos.jsonl"
    english_catalog_path = ROOT / "catalog" / "english-community.jsonl"
    translation_catalog_path = ROOT / "catalog" / "english-translations.jsonl"
    english_policy_path = ROOT / "config" / "english-source-policy.json"
    if not english_catalog_path.is_file() or not english_policy_path.is_file():
        errors.append("English source catalog or reviewed policy is missing")
        english_rows, english_policy = [], {}
    else:
        english_rows = read_jsonl(english_catalog_path)
        english_policy = read_json_object_without_duplicate_keys(english_policy_path)
    if not translation_catalog_path.is_file():
        errors.append("catalog/english-translations.jsonl is missing")
        translation_rows = []
    else:
        translation_rows = read_jsonl(translation_catalog_path)
    if not kb_catalog_path.is_file():
        errors.append("catalog/knowledge-bank.jsonl is missing")
        kb_rows = []
    else:
        kb_rows = read_jsonl(kb_catalog_path)
    if not community_posts_catalog_path.is_file():
        errors.append("catalog/community-posts.jsonl is missing")
        community_post_rows = []
    else:
        community_post_rows = read_jsonl(community_posts_catalog_path)
    if not community_comments_catalog_path.is_file():
        errors.append("catalog/community-comments.jsonl is missing")
        community_comment_rows = []
    else:
        community_comment_rows = read_jsonl(community_comments_catalog_path)
    if not video_catalog_path.is_file():
        errors.append("catalog/videos.jsonl is missing")
        video_rows = []
    else:
        video_rows = read_jsonl(video_catalog_path)

    comment_policy_path = ROOT / "config" / "community-comment-policy.json"
    if not comment_policy_path.is_file():
        errors.append("config/community-comment-policy.json is missing")
        comment_policy = {}
    else:
        comment_policy = read_json_object_without_duplicate_keys(comment_policy_path)

    allowlist_path = ROOT / "config" / "video-transcript-allowlist.txt"
    overrides_path = ROOT / "config" / "video-rights-overrides.json"
    if not allowlist_path.is_file() or not overrides_path.is_file():
        errors.append("video rights config is missing")
        transcript_allowlist: set[str] = set()
        rights_overrides: dict = {}
    else:
        transcript_allowlist = read_allowlist(allowlist_path)
        rights_overrides = read_json_object_without_duplicate_keys(overrides_path)

    course_catalog_path = ROOT / "catalog" / "course-lessons.jsonl"
    course_rows = read_jsonl(course_catalog_path) if course_catalog_path.is_file() else []
    course_policy_path = ROOT / "config" / "member-course-policy.json"
    course_policy = read_json_object_without_duplicate_keys(course_policy_path) if course_policy_path.is_file() else {}
    course_ids = [row["lesson_id"] for row in course_policy.get("records", [])]
    if course_rows or course_ids:
        if course_policy.get("authorization") != COURSE_AUTHORIZATION or (course_policy.get("course") or {}).get("url") != COURSE_URL:
            errors.append("Course text policy lacks explicit maintainer authorization")
        if len(course_ids) != 23 or len(course_ids) != len(set(course_ids)):
            errors.append("Course text policy differs from the exact authorized 23 lessons")
        if sorted(row.get("lesson_id") for row in course_rows) != sorted(course_ids):
            errors.append("Course text policy/catalog exact lesson mismatch")
        for row in course_rows:
            validate_member_course(row, course_policy, errors)
        expected_course_files = {row.get("corpus_path") for row in course_rows}
        actual_course_files = {str(path.relative_to(ROOT)) for path in (ROOT / "corpus" / "course-lessons").glob("*.md")}
        if expected_course_files != actual_course_files:
            errors.append("course lesson catalog/files mismatch")

    book_rows = read_jsonl(ROOT / "catalog" / "book-chapters.jsonl") if (ROOT / "catalog" / "book-chapters.jsonl").is_file() else []
    blog_rows = read_jsonl(ROOT / "catalog" / "blog-posts.jsonl") if (ROOT / "catalog" / "blog-posts.jsonl").is_file() else []
    editions_policy_path = ROOT / "config" / "chinese-editions-policy.json"
    editions_policy = read_json_object_without_duplicate_keys(editions_policy_path) if editions_policy_path.is_file() else {}
    validate_chinese_editions(book_rows, blog_rows, editions_policy, errors)

    member_path = ROOT / "config/member-video-policy.json"
    member_policy = read_json_object_without_duplicate_keys(member_path) if member_path.is_file() else {}
    member_list = [row["video_id"] for row in member_policy.get("records", [])]
    member_ids = set(member_list)
    if len(member_list) != len(member_ids):
        errors.append("Member video policy contains duplicate IDs")
    if member_ids and member_policy.get("authorization") != "maintainer-request-2026-10-02-member-transcripts":
        errors.append("Member video policy lacks explicit maintainer authorization")
    if member_ids and (len(member_ids) != 218 or member_policy.get("membership_url") != "https://www.youtube.com/channel/UC_5lJHgnMP_lb_VpIiXV0hQ/join"):
        errors.append("Member video policy differs from the exact authorized channel snapshot")
    if {row.get("video_id") for row in video_rows if row.get("inclusion_authorization") and row.get("inclusion_authorization") == member_policy.get("authorization")} != member_ids:
        errors.append("Member video policy/catalog exact ID mismatch")
    solo_path = ROOT / "config/member-solo-review.json"
    solo_review = read_json_object_without_duplicate_keys(solo_path) if solo_path.is_file() else {}
    solo_ids = frozenset(solo_review.get("solo_video_ids", []))
    if solo_review and solo_review.get("authorization") != SOLO_REVIEW_AUTHORIZATION:
        errors.append("Solo member speech review lacks the explicit maintainer request")
    prior_solo = {row["video_id"] for row in member_policy.get("records", []) if row.get("prior_solo_transcript")}
    if not solo_ids <= member_ids - prior_solo:
        errors.append("Solo member speech review names videos outside the mixed member snapshot")

    values_path = ROOT / "config/values-conversations-policy.json"
    values_policy = read_json_object_without_duplicate_keys(values_path) if values_path.is_file() else {}
    excerpt_catalog_path = ROOT / "catalog" / "conversation-excerpts.jsonl"
    excerpt_rows = read_jsonl(excerpt_catalog_path) if excerpt_catalog_path.is_file() else []
    public_conversations = validate_values_conversations(video_rows, excerpt_rows, values_policy, member_ids, errors)

    for row in kb_rows:
        if row.get("full_text_included") and not authorized_publisher_text(row):
            errors.append(f"{row.get('id')}: non-first-party Knowledge Bank full text")
        if not str(row.get("url", "")).startswith("https://www.superlinear.academy/"):
            errors.append(f"{row.get('id')}: unexpected Knowledge Bank source URL")

    for label, rows, id_prefix in (
        ("community post", community_post_rows, "circle-"),
        ("community comment", community_comment_rows, "circle-comment-"),
    ):
        ids = [row.get("id") for row in rows]
        if len(ids) != len(set(ids)):
            errors.append(f"duplicate IDs in {label} catalog")
        for row in rows:
            if not str(row.get("id", "")).startswith(id_prefix):
                errors.append(f"{row.get('id')}: unexpected {label} ID")
            if not authorized_publisher_text(row):
                errors.append(f"{row.get('id')}: non-first-party {label} content")
            if not row.get("full_text_included") or not row.get("corpus_path"):
                errors.append(f"{row.get('id')}: missing {label} full text")
            if not str(row.get("url", "")).startswith("https://www.superlinear.academy/"):
                errors.append(f"{row.get('id')}: unexpected {label} source URL")

    expected_community_post_files = {row.get("corpus_path") for row in community_post_rows}
    actual_community_post_files = {
        str(path.relative_to(ROOT)) for path in (ROOT / "corpus" / "community-posts").glob("*.md")
    }
    if expected_community_post_files != actual_community_post_files:
        errors.append("community post catalog/files mismatch")
    expected_community_comment_files = {row.get("corpus_path") for row in community_comment_rows}
    actual_community_comment_files = {
        str(path.relative_to(ROOT)) for path in (ROOT / "corpus" / "community-comments").glob("*.md")
    }
    if expected_community_comment_files != actual_community_comment_files:
        errors.append("community comment catalog/files mismatch")
    if comment_policy.get("comments_included") != len(community_comment_rows):
        errors.append("community comment policy/catalog count mismatch")
    if int(comment_policy.get("source_comments_reviewed") or 0) < len(community_comment_rows):
        errors.append("community comment policy reviewed count is invalid")

    community_post_ids = {row.get("id") for row in community_post_rows}
    for row in community_comment_rows:
        if row.get("parent_post_id") not in community_post_ids:
            errors.append(f"{row.get('id')}: comment parent is not an included Yuzheng post")
        if row.get("source_visibility") != "public":
            errors.append(f"{row.get('id')}: comment source is not public")
        if not row.get("parent_post_title"):
            errors.append(f"{row.get('id')}: comment is missing first-party parent title")
        corpus_path = ROOT / str(row.get("corpus_path") or "")
        if not corpus_path.is_file():
            continue
        meta, body = read_markdown(corpus_path)
        urls = URL_PATTERN.findall(body)
        source_url = str(row.get("url") or "")
        if len(urls) != 1 or any(url != source_url for url in urls) or meta.get("source_url") != source_url:
            errors.append(f"{row.get('id')}: comment contains a non-canonical or extra URL")
        without_urls = URL_PATTERN.sub("", body)
        if BARE_DOMAIN_PATTERN.search(without_urls):
            errors.append(f"{row.get('id')}: comment contains a bare domain")
        # Inspect the original comment after its title and canonical source note.
        body = body.split("\n\n", 2)[-1]
        if COMMENT_SENSITIVE_PATTERN.search(body):
            errors.append(f"{row.get('id')}: comment contains sensitive-context hint")
        if body.lstrip().startswith(("“", '"')):
            errors.append(f"{row.get('id')}: comment begins with a possible third-party quotation")
        if re.search(r"(?m)^\s*>", body):
            errors.append(f"{row.get('id')}: comment contains a possible third-party block quotation")
        if "@" in body:
            errors.append(f"{row.get('id')}: comment contains an unredacted mention")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for value, label in (
        (len(community_post_rows), "篇"),
        (len(community_comment_rows), "条"),
    ):
        if f"{value} {label}" not in readme:
            errors.append(f"README.md does not state current {value} {label} corpus count")

    for row in video_rows:
        is_member = row.get("video_id") in member_ids
        # One of the six public conversations the publisher opened on 2026-10-04 (checked above).
        is_conversation = row.get("video_id") in public_conversations
        if is_member:
            validate_member_video(row, member_policy, errors, solo_ids)
        if row.get("transcript_included") and not (is_member or is_conversation) and row.get("rights_scope") != "first-party":
            errors.append(f"{row.get('id')}: mixed-speaker transcript included")
        if row.get("transcript_included") and not is_conversation and (not is_member or row.get("rights_scope") == "first-party") and (
            row.get("speaker_classification") != "solo-yuzheng"
            or row.get("review_status") != "approved"
        ):
            errors.append(f"{row.get('id')}: transcript lacks positive speaker-rights approval")
        if row.get("transcript_included") and not (is_member or is_conversation) and row.get("guest_names"):
            errors.append(f"{row.get('id')}: known guest transcript included")
        if not str(row.get("url", "")).startswith("https://www.youtube.com/watch?v="):
            errors.append(f"{row.get('id')}: unexpected video source URL")

    included_video_ids = {
        row.get("video_id") for row in video_rows if row.get("transcript_included")
    }
    expected_video_ids = transcript_allowlist | member_ids | public_conversations
    if included_video_ids != expected_video_ids:
        missing = sorted(expected_video_ids - included_video_ids)
        unexpected = sorted(included_video_ids - expected_video_ids)
        errors.append(
            "video transcript catalog/allowlist mismatch"
            + (f"; missing={','.join(missing)}" if missing else "")
            + (f"; unexpected={','.join(unexpected)}" if unexpected else "")
        )
    conflicts = sorted(transcript_allowlist & set(rights_overrides))
    if conflicts:
        errors.append("video allowlist conflicts with manual exclusions: " + ", ".join(conflicts))

    for directory in (ROOT / "context", ROOT / "examples"):
        for path in directory.glob("*.md"):
            meta, _ = read_markdown(path)
            label = str(path.relative_to(ROOT))
            validate_provenance(meta, label, errors, full_text=True)
            if meta.get("author") != "AI" or meta.get("content_origin") not in AI_SYNTHESIS_ORIGINS:
                errors.append(f"{label}: repository synthesis must identify AI authorship")
            if meta.get("license") != "CC-BY-4.0":
                errors.append(f"{label}: missing content license")
    for directory in (
        ROOT / "corpus" / "community-posts",
        ROOT / "corpus" / "community-comments",
        ROOT / "corpus" / "videos",
    ):
        for pattern in directory.glob("*.md") if directory.exists() else []:
            meta, _ = read_markdown(pattern)
            identity = str(meta.get("id", "")).removeprefix("youtube-")
            member_reference = (meta.get("rights_scope") == "publisher-authorized-transcript" and (
                (meta.get("inclusion_authorization") == member_policy.get("authorization") and identity in member_ids)
                or (meta.get("inclusion_authorization") == VALUES_AUTHORIZATION and identity in public_conversations)))
            if not member_reference and (not authorized_publisher_text(meta) or meta.get("license") != "CC-BY-4.0"):
                errors.append(f"{pattern.relative_to(ROOT)}: missing first-party attribution/license")
            if meta.get("third_party_exclusions") is not True:
                errors.append(f"{pattern.relative_to(ROOT)}: missing third-party rights notice")

    validate_english_sources(english_rows, english_policy, errors)
    validate_translations(translation_rows, video_rows, transcript_allowlist, errors)
    validate_catalog_bindings([
        ("knowledge-bank", kb_rows), ("community-posts", community_post_rows),
        ("community-comments", community_comment_rows), ("videos", video_rows),
        ("english-community", english_rows), ("english-translations", translation_rows),
        ("course-lessons", course_rows), ("book-chapters", book_rows), ("blog-posts", blog_rows),
        ("conversation-excerpts", excerpt_rows),
    ], errors)

    return {
        "community_posts_catalog": len(community_post_rows),
        "community_posts_full_text": sum(
            bool(row.get("full_text_included")) for row in community_post_rows
        ),
        "community_comments_included": len(community_comment_rows),
        "member_course_lessons": len(course_rows),
        "book_chapters_zh": len(book_rows),
        "public_conversation_transcripts": len(public_conversations),
        "conversation_excerpt_files": len(excerpt_rows),
        "conversation_excerpts": sum(int(row.get("excerpt_count") or 0) for row in excerpt_rows),
        "blog_posts_zh": len(blog_rows),
        "community_comments_reviewed": int(
            comment_policy.get("source_comments_reviewed") or 0
        ),
        "knowledge_bank_catalog": len(kb_rows),
        "knowledge_bank_full_text": sum(bool(row.get("full_text_included")) for row in kb_rows),
        "video_catalog": len(video_rows),
        "video_transcripts": sum(bool(row.get("transcript_included")) for row in video_rows),
        "video_metadata_only": sum(not bool(row.get("transcript_included")) for row in video_rows),
        "member_video_transcripts": len(member_ids),
        "member_video_solo_reviewed": len(solo_ids),
        "known_guest_videos": sum(bool(row.get("guest_names")) for row in video_rows),
        "english_community_catalog": len(english_rows),
        "english_community_full_text_files": len(list((ROOT / "corpus/english-community").glob("*.md"))),
        "english_community_original_yuzheng": sum(row.get("original_author") == "Yuzheng Sun" for row in english_rows),
        "english_community_third_party_or_unresolved": sum(row.get("original_author") != "Yuzheng Sun" for row in english_rows),
        "english_video_translations": len(translation_rows),
    }


def build_manifest(stats: dict[str, int], license_map: dict[str, tuple[str, str]]) -> dict:
    snapshot_path = ROOT / "config" / "release-snapshot.json"
    snapshot = json.loads(snapshot_path.read_text()) if snapshot_path.is_file() else {
        "snapshot_at": "2026-09-17",
        "source_snapshots": {
            "community_posts": "2026-09-17", "knowledge_bank": "2026-09-17",
            "english_community": "2026-09-17", "community_comments": "2026-08-30",
            "video_inventory": "2026-09-15", "video_speaker_rights_review": "2026-09-17",
            "english_translation_library": "2026-04-19", "provenance_review": "2026-09-17",
        },
    }
    for value in [snapshot["snapshot_at"], *snapshot["source_snapshots"].values()]:
        datetime.strptime(value, "%Y-%m-%d")
    files = [str(path.relative_to(ROOT)) for path in public_files()]
    license_counts: dict[str, int] = {}
    for license, _ in license_map.values():
        license_counts[license] = license_counts.get(license, 0) + 1
    return {
        "schema_version": 3,
        "snapshot_at": snapshot["snapshot_at"],
        "repository": "sunyuzheng/lizheng-open-context",
        "intended_visibility": "public",
        "source_snapshots": snapshot["source_snapshots"],
        "filters": {
            "community_posts_full_text": "current Circle-search posts authored by YZ｜立正 plus one first-party Knowledge Bank item preserved from the earlier public snapshot; archived and hidden test spaces excluded; contact data redacted",
            "community_comments_full_text": "first-party comments on included Yuzheng-authored posts, from discussion spaces with at least 80 effective characters; member mentions, contact data, sensitive/private context, third-party leading quotations, and all inline links removed",
            "knowledge_bank_full_text": "first-party Knowledge Bank posts point to the unified community-post corpus; other authors remain metadata-only",
            "videos": "youtube public + normal_video + ready_public_normal + local_status ok",
            "video_full_text": "explicit V1 solo-Yuzheng allowlist, plus the exact maintainer-authorized member-video-policy snapshot and the six public conversations in config/values-conversations-policy.json; mixed/unresolved speech is under the Lizheng Reference Use License, guests keep the rights in their own words, and it cannot independently establish Yuzheng's stance",
            "conversation_excerpts": "Yuzheng's own turns in the twelve conversations that shaped his values (问道, 赵智沉, 王路, Leon), reviewed speaker by speaker on 2026-10-04; every quotation must match its included transcript verbatim at the stated moment; headings and context lines are AI-written; excerpts from member videos are under the Lizheng Reference Use License, from public videos CC BY 4.0",
            "member_videos": "open transcript text, members-only original videos; exact IDs and transcript hashes in config/member-video-policy.json; YouTube membership is distinct from Ask's Superlinear Founding quota",
            "book": "author-owned complete framework reference and chapter map; no publisher-formatted assets",
            "course_lessons": "the exact 23 maintainer-authorized 《真本事》 lesson texts in config/member-course-policy.json, under the Lizheng Reference Use License; course videos, slides, assignments, and comments stay members-only and are not included",
            "english_community": "exact reviewed public post allowlist; original author, publisher, AI translation and repost roles remain separate; third-party rights retained",
            "chinese_editions": "the exact texts in config/chinese-editions-policy.json: the free Chinese edition of Growth Data Analytics Playbook and Yuzheng's Statsig blog posts, AI rewrites in his Chinese voice under the Lizheng Reference Use License; they defer to the English originals, co-authors keep their share, and figures are reduced to captions",
            "english_video_translations": "canonical AI translations of currently allowlisted solo-Yuzheng public videos only; generation date is not a public publication date; source-family deduplication",
            "attribution": "AI synthesis is secondary-only; third-party and metadata-only sources cannot establish Yuzheng's stance; search relevance is separate from stance authority",
            "rights": "one license per file, recorded below and in REUSE.toml; the plain-language overview is LICENSE.md",
        },
        "counts": stats,
        "licenses": {
            license: {"text": rights.LICENSE_TEXTS.get(license), "files": count}
            for license, count in sorted(license_counts.items())
        },
        "files": [
            {
                "path": relative,
                "bytes": (ROOT / relative).stat().st_size,
                "sha256": sha256(ROOT / relative),
                "license": license_map.get(relative, (None,))[0],
            }
            for relative in files
        ],
    }


def validate_manifest(expected: dict, errors: list[str]) -> None:
    if not MANIFEST.is_file():
        errors.append("release-manifest.json is missing; run with --write-manifest")
        return
    actual = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if actual != expected:
        errors.append("release-manifest.json is stale; rerun with --write-manifest")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true",
                        help="regenerate INDEX.md, index/, REUSE.toml, and release-manifest.json")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    errors: list[str] = []
    if args.write_manifest:
        # Generated pages come first: the rights map and the manifest cover them too.
        try:
            build_index.write()
        except (KeyError, ValueError) as exc:
            errors.append(f"index pages: {exc}")
        rights.write(release_paths())
    validate_sensitive_data(errors)
    validate_internal_links(errors)
    try:
        build_index.validate(errors)
    except (KeyError, ValueError) as exc:
        errors.append(f"index pages: {exc}")
    license_map = rights.validate(release_paths(), errors)
    try:
        stats = validate_rights(errors)
    except ValueError as exc:
        errors.append(str(exc))
        stats = {}
    expected = build_manifest(stats, license_map)
    if args.write_manifest and not errors:
        MANIFEST.write_text(json.dumps(expected, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    else:
        validate_manifest(expected, errors)
    if errors:
        print("Release validation failed:")
        for error in errors:
            print(f"- {error}")
        raise SystemExit(1)
    print(json.dumps({"status": "ok", "counts": stats, "files": len(expected["files"])}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
