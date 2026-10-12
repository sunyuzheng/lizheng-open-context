#!/usr/bin/env python3
"""Build the public corpus from sanitized first-party Circle exports and local media.

The exporter deliberately needs explicit source paths. Circle inventory inputs must
contain only posts and comments authored by YZ｜立正 plus non-sensitive space metadata;
post text comes from sanitized single-post HTML caches so search-indexed attachments cannot
become corpus text. Comment text comes from the single-comment HTML when it is cached and
otherwise from the search export's comment text. It never reads credentials, member profiles,
other people's comment bodies, messages, or raw media.
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
YUZHENG_NAME = "YZ｜立正"
EMAIL = re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE)
MAINLAND_PHONE = re.compile(r"(?<!\d)1[3-9]\d{9}(?!\d)")
MACOS_ABSOLUTE_PATH = re.compile(r"/Users/[A-Za-z0-9._-]+/[^\s<>()\[\]{}\"']+")
WINDOWS_ABSOLUTE_PATH = re.compile(
    r"[A-Za-z]:\\Users\\[^\\\s]+\\[^\s<>()\[\]{}\"']+",
    re.IGNORECASE,
)
INLINE_URL = re.compile(r"https?://\S+", re.IGNORECASE)
MARKDOWN_LINK = re.compile(r"\[([^\]]*)\]\(https?://[^)]+\)", re.IGNORECASE)
BARE_DOMAIN = re.compile(
    r"(?<![@\w])(?:[A-Za-z0-9-]+\.)+(?:com|org|net|io|ai|co|cn)(?:/[^\s]*)?",
    re.IGNORECASE,
)
# A display name: one word, then an optional capitalized surname or initial ("Allen Z"), then any
# tags members add after a bar ("Moses | INTP").
CIRCLE_MENTION = re.compile(
    r"@[A-Za-z0-9_\u3400-\u9fff｜|·.-]{1,40}"
    r"(?:[ \t]+[A-Z][A-Za-z0-9_.-]{0,39})?"
    r"(?:[ \t]*[｜|][ \t]*[A-Za-z0-9_\u3400-\u9fff.-]{1,20})*"
)
COMMENT_EXCLUDED_HINT = re.compile(
    r"(?:微信|wechat|私信|私聊|群聊|微信群|在群里|群内|群中|加群|短信|"
    r"电话|手机号|邮箱|住址|地址是|加我|联系我|\bDM\b|"
    r"(?:跟|和|与).{0,12}(?:聊完|聊天|交流))",
    re.IGNORECASE,
)
# Comments: what Yuzheng wrote under any post in a public space, when it says something on its
# own. The rules below remove what is never published: contact details and private channels,
# introduction and hiring threads, and other people's private circumstances. A model then sorts
# the rest into substance and small talk (scripts/review_community_comments.py); its decisions
# are pinned to the exact published text in config/community-comment-review.json.
COMMENT_EXCLUDED_POST_HINT = re.compile(
    r"(?:自我介绍|新人报[到道]|新同学|say hello|招聘|招人|求职|内推|岗位|hiring|job opening)",
    re.IGNORECASE,
)
COMMENT_SENSITIVE_REVIEW_HINT = re.compile(
    r"(?:therapist|治疗师|心理咨询|抑郁|sponsor(?:ship)?|月收入|工资|薪资|报酬|"
    r"财务状况|PERM|EB-?1A|绿卡|被裁|裁员|未成年|\b17\s*岁|生病|离世|去世|"
    r"戒烟|康复|伴侣|老婆|老公|男朋友|女朋友|私下|社群不赚钱|接管.{0,12}运营)",
    re.IGNORECASE,
)
# Member introductions and event logistics.
COMMENT_EXCLUDED_SPACES = {"say-hello", "events"}
COMMENT_MIN_EFFECTIVE_CHARS = 20
COMMENT_REVIEW_PATH = ROOT / "config" / "community-comment-review.json"
COMMENT_REVIEW_INCLUDE = {
    "view": "他自己的判断或看法",
    "advice": "给提问者或读者的具体建议",
    "explanation": "解释原因、机制、概念或取舍",
    "experience": "他本人的经历、做法或观察",
    "information": "有用的事实或资源，不是事务通知",
}
COMMENT_REVIEW_EXCLUDE = {
    "social": "欢迎、感谢、夸奖、祝贺，没有说出看法或理由",
    "admin": "搬帖、排期、链接指路，以及课程、会员、报名、付款、退款等事务",
    "chat": "玩笑、闲聊，或只是提问",
    "context": "不看原帖和其他成员的话就读不懂",
    "private": "谈到某位成员的健康、家庭、感情、收入数字、移民身份、被裁或与人冲突等敏感私事",
}
MIXED_SPEAKER_HINT = re.compile(
    r"(?:访谈|专访|采访|圆桌|对谈|对话|聊天|闲扯|实况|播客|podcast|interview|"
    r"和.{1,18}聊|与.{1,18}聊|课代表.{0,8}×|鸭哥演示|冯老师品酒课|master sommelier)",
    re.IGNORECASE,
)
TIMECODE = re.compile(
    r"(?P<h>\d{1,2}):(?P<m>\d{2}):(?P<s>\d{2})[,.](?P<ms>\d{3})"
)


def yaml_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def front_matter(fields: dict[str, Any]) -> str:
    lines = ["---"]
    for key, value in fields.items():
        if value is None:
            continue
        if isinstance(value, bool):
            rendered = "true" if value else "false"
        elif isinstance(value, (int, float)):
            rendered = str(value)
        elif isinstance(value, list):
            rendered = json.dumps(value, ensure_ascii=False)
        else:
            rendered = yaml_string(str(value))
        lines.append(f"{key}: {rendered}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def reset_generated_dir(path: Path) -> None:
    resolved = path.resolve()
    resolved.relative_to(ROOT.resolve())
    if resolved.exists():
        shutil.rmtree(resolved)
    resolved.mkdir(parents=True, exist_ok=True)


class MarkdownHTMLParser(HTMLParser):
    """Small, dependency-free converter for Circle's published article HTML."""

    def __init__(self, *, redact_member_links: bool = False) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.links: list[str | None] = []
        self.list_stack: list[str] = []
        self.ordered_index: list[int] = []
        self.in_pre = False
        self.blockquote_depth = 0
        self.list_item_depth = 0
        self.redact_member_links = redact_member_links
        self.redacted_link_depth = 0

    def emit(self, value: str) -> None:
        self.parts.append(value)

    def newline(self, count: int = 1) -> None:
        current = "".join(self.parts)
        trailing = len(current) - len(current.rstrip("\n"))
        if trailing < count:
            self.emit("\n" * (count - trailing))

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_dict = {k: v or "" for k, v in attrs}
        if tag == "p":
            if self.list_item_depth:
                return
            if self.blockquote_depth:
                self.newline(1)
                self.emit("> ")
            else:
                self.newline(2)
        elif tag in {"div", "section"}:
            self.newline(2)
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.newline(2)
            self.emit("#" * int(tag[1]) + " ")
        elif tag == "br":
            self.newline(1)
        elif tag == "hr":
            self.newline(2)
            self.emit("---")
            self.newline(2)
        elif tag == "blockquote":
            self.newline(2)
            self.blockquote_depth += 1
        elif tag in {"strong", "b"}:
            self.emit("**")
        elif tag in {"em", "i"}:
            self.emit("*")
        elif tag == "code" and not self.in_pre:
            self.emit("`")
        elif tag == "pre":
            self.newline(2)
            self.emit("```\n")
            self.in_pre = True
        elif tag == "a":
            href = attrs_dict.get("href", "")
            classes = set(attrs_dict.get("class", "").split())
            is_member_link = "mention" in classes or "/u/" in href
            if self.redact_member_links and is_member_link:
                self.emit("[社区成员]")
                self.links.append(None)
                self.redacted_link_depth += 1
            else:
                self.emit("[")
                self.links.append(href)
        elif tag in {"ul", "ol"}:
            self.list_stack.append(tag)
            if tag == "ol":
                self.ordered_index.append(0)
            self.newline(1)
        elif tag == "li":
            self.newline(1)
            self.list_item_depth += 1
            indent = "  " * max(0, len(self.list_stack) - 1)
            if self.list_stack and self.list_stack[-1] == "ol":
                self.ordered_index[-1] += 1
                marker = f"{self.ordered_index[-1]}. "
            else:
                marker = "- "
            self.emit(indent + marker)
        elif tag == "img":
            alt = attrs_dict.get("alt", "").strip()
            if alt:
                self.emit(f"[图片：{alt}]")

    def handle_endtag(self, tag: str) -> None:
        if tag == "p":
            if not self.list_item_depth:
                self.newline(1 if self.blockquote_depth else 2)
        elif tag in {"div", "section"} or tag.startswith("h"):
            self.newline(2)
        elif tag == "blockquote":
            self.blockquote_depth = max(0, self.blockquote_depth - 1)
            self.newline(2)
        elif tag == "li":
            self.list_item_depth = max(0, self.list_item_depth - 1)
        elif tag in {"strong", "b"}:
            self.emit("**")
        elif tag in {"em", "i"}:
            self.emit("*")
        elif tag == "code" and not self.in_pre:
            self.emit("`")
        elif tag == "pre":
            self.emit("\n```")
            self.newline(2)
            self.in_pre = False
        elif tag == "a":
            href = self.links.pop() if self.links else ""
            if href is None:
                self.redacted_link_depth = max(0, self.redacted_link_depth - 1)
            else:
                self.emit(f"]({href})" if href else "]")
        elif tag in {"ul", "ol"}:
            if self.list_stack:
                ended = self.list_stack.pop()
                if ended == "ol" and self.ordered_index:
                    self.ordered_index.pop()
            self.newline(2)

    def handle_data(self, data: str) -> None:
        if self.redacted_link_depth:
            return
        if self.in_pre:
            self.emit(data)
            return
        cleaned = re.sub(r"[ \t\r\f\v]+", " ", data)
        self.emit(cleaned)

    def markdown(self) -> str:
        text = "".join(self.parts)
        text = re.sub(r"\n[ \t]+\n", "\n\n", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r" +\n", "\n", text)
        return text.strip()


def html_to_markdown(value: str, *, redact_member_links: bool = False) -> str:
    parser = MarkdownHTMLParser(redact_member_links=redact_member_links)
    parser.feed(value)
    parser.close()
    return parser.markdown()


def sanitize_first_party_text(value: str, *, comment: bool = False) -> str:
    """Remove contact data; comments also drop member handles and external deep links."""
    value = EMAIL.sub("[邮箱已省略；请查看原帖]", value)
    value = MAINLAND_PHONE.sub("[手机号已省略；请查看原帖]", value)
    value = MACOS_ABSOLUTE_PATH.sub("[本地路径已省略]", value)
    value = WINDOWS_ABSOLUTE_PATH.sub("[本地路径已省略]", value)
    if comment:
        value = CIRCLE_MENTION.sub("[社区成员]", value)
        value = re.sub(r"\[社区成员\]\([^)]+\)", "[社区成员]", value)
        value = MARKDOWN_LINK.sub(
            lambda match: f"{match.group(1).strip()} [链接见原评论]".strip(), value
        )
        value = INLINE_URL.sub("[链接见原评论]", value)
        value = BARE_DOMAIN.sub("[链接见原评论]", value)
    value = re.sub(r"[ \t]+\n", "\n", value)
    value = re.sub(r"\n{3,}", "\n\n", value)
    return value.strip()


def comment_effective_text(value: str) -> str:
    value = EMAIL.sub("", value)
    value = MAINLAND_PHONE.sub("", value)
    value = CIRCLE_MENTION.sub("", value)
    value = INLINE_URL.sub("", value)
    return re.sub(r"\s+", "", value)


def source_visibility(space: dict[str, Any]) -> str:
    if space.get("is_hidden_from_non_members") or space.get("is_hidden"):
        return "hidden"
    if space.get("is_private"):
        return "members-only"
    return "public"


def load_cache_directory(path: Path, label: str) -> list[dict[str, Any]]:
    if not path.is_dir():
        raise SystemExit(f"Missing sanitized {label} cache directory: {path}")
    records: list[dict[str, Any]] = []
    for source in sorted(path.glob("*.json")):
        payload = json.loads(source.read_text(encoding="utf-8"))
        records.extend(payload.get("records") or [])
    if not records:
        raise SystemExit(f"Sanitized {label} cache directory is empty: {path}")
    ids = [int(record["id"]) for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError(f"Duplicate IDs in sanitized {label} cache")
    return records


def choose_transcript_path(folder: Path, status: str | None) -> Path | None:
    candidates: list[Path] = []
    candidates.extend(folder.glob("*.srt"))
    candidates.extend(folder.glob("*.vtt"))
    for process_dir in sorted(folder.glob("*_process")):
        if process_dir.is_dir():
            candidates.extend(process_dir.glob("*.srt"))
            candidates.extend(process_dir.glob("*.vtt"))
    usable = sorted(
        {path.resolve() for path in candidates if path.is_file() and path.stat().st_size > 20
         and transcript_structure_valid(path)},
        key=str,
    )
    if not usable:
        return None

    infos = sorted(folder.glob("*.info.json"))
    info = json.loads(infos[0].read_text(encoding="utf-8")) if len(infos) == 1 else {}
    manual = info.get("subtitles") or {}
    automatic = info.get("automatic_captions") or {}
    original_language = str(info.get("language") or "").split("-", 1)[0].lower()

    def score(path: Path) -> tuple[int, int, int, str]:
        name = path.name.lower().replace(".normalized.srt", ".srt")
        language = next((key for key in sorted(set(manual) | set(automatic), key=len, reverse=True)
                         if name.endswith(f".{key.lower()}{path.suffix.lower()}")), None)
        family = str(language or "").split("-", 1)[0].lower()
        language_rank = 0 if family and family == original_language else 1 if language is None else 2
        if name.endswith((".corrected.srt", ".final.srt")):
            priority = 0  # A filename is a claim, not proof of editorial accuracy.
        elif language in manual and manual[language]:
            priority = 1
        elif name.endswith(".qwen.srt"):
            priority = 3
        elif language in automatic:
            entries = automatic[language]
            translated = any("tlang=" in str(row.get("url", "")) for row in entries if isinstance(row, dict))
            priority = 5 if translated else 4
        else:
            priority = 2
        return priority, language_rank, 0 if path.suffix == ".srt" else 1, str(path)

    return min(usable, key=score)


def transcript_structure_valid(path: Path) -> bool:
    """Reject broken timing/empty cues before choosing among available tracks."""
    try:
        raw = path.read_text(encoding="utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
        blocks = [block for block in re.split(r"\n[ \t]*\n+", raw.strip()) if block.strip()]
        if path.suffix == ".vtt":
            if not blocks or not blocks.pop(0).startswith("WEBVTT"):
                return False
        previous = -1.0
        count = 0
        for block in blocks:
            lines = block.splitlines()
            if path.suffix == ".vtt" and re.match(r"^(?:NOTE(?:[ \t]|$)|STYLE$|REGION$)", lines[0]):
                continue
            index = 1 if "-->" not in lines[0] else 0
            if path.suffix == ".srt" and (index != 1 or not lines[0].isdigit()):
                return False
            if len(lines) <= index + 1:
                return False
            timing = re.fullmatch(r"(?:(\d+):)?([0-5]\d):([0-5]\d)[,.](\d{3})\s+-->\s+"
                                  r"(?:(\d+):)?([0-5]\d):([0-5]\d)[,.](\d{3})(?:\s+[A-Za-z]+:\S+)*", lines[index])
            if not timing:
                return False
            values = timing.groups()
            start, end = [(int(values[i] or 0) * 3600 + int(values[i+1]) * 60
                           + int(values[i+2]) + int(values[i+3]) / 1000) for i in (0, 4)]
            # Angle-bracket annotations such as '< No Speech >' are source text,
            # not HTML tags. Do not turn them into apparently empty captions.
            text = html.unescape(re.sub(r"</?[A-Za-z][^>]*>|<\d{1,2}:\d{2}(?::\d{2})?\.\d{3}>", "", "\n".join(lines[index+1:]))).strip()
            if not text or end <= start or start < previous:
                return False
            previous = start
            count += 1
        return bool(count)
    except (OSError, UnicodeError, ValueError):
        return False


def timestamp_seconds(value: str) -> int:
    match = TIMECODE.search(value)
    if not match:
        return 0
    return int(match["h"]) * 3600 + int(match["m"]) * 60 + int(match["s"])


def display_timestamp(seconds: int) -> str:
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def parse_timed_transcript(path: Path) -> list[tuple[int, str]]:
    raw = path.read_text(encoding="utf-8-sig", errors="replace")
    blocks = re.split(r"\n\s*\n", raw.replace("\r\n", "\n").replace("\r", "\n"))
    cues: list[tuple[int, str]] = []
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        timing_index = next((i for i, line in enumerate(lines) if "-->" in line), None)
        if timing_index is None:
            continue
        start = timestamp_seconds(lines[timing_index].split("-->", 1)[0])
        text_lines = lines[timing_index + 1 :]
        text_value = " ".join(text_lines)
        text_value = re.sub(r"<[^>]+>", "", text_value)
        text_value = html.unescape(text_value)
        text_value = re.sub(r"\s+", " ", text_value).strip()
        if not text_value:
            continue
        if cues and text_value == cues[-1][1]:
            continue
        cues.append((start, text_value))
    return cues


def article_filename(record: dict[str, Any]) -> str:
    date = (record.get("published_at") or "undated")[:10].replace("-", "")
    slug = re.sub(r"[^a-zA-Z0-9_-]+", "-", record.get("slug") or str(record["id"]))
    return f"{date}-{slug}-{record['id']}.md"


def post_content_status(space: dict[str, Any]) -> str:
    name = str(space.get("name") or "")
    slug = str(space.get("slug") or "")
    if name == "删除和归档" or slug == "1a40ca":
        return "archived"
    if "test" in name.lower() or slug.startswith("test"):
        return "test"
    return "current"


def export_community_posts(
    author_cache_path: Path,
    authoritative_bodies_dir: Path,
    spaces_cache_path: Path,
    knowledge_cache_path: Path,
    snapshot_at: str,
) -> tuple[dict[str, int], dict[int, str], dict[int, dict[str, Any]]]:
    author_records = json.loads(author_cache_path.read_text(encoding="utf-8"))["records"]
    authoritative_records = load_cache_directory(
        authoritative_bodies_dir, "authoritative Circle post bodies"
    )
    authoritative_by_id = {int(record["id"]): record for record in authoritative_records}
    spaces = {
        int(space["id"]): space
        for space in json.loads(spaces_cache_path.read_text(encoding="utf-8"))["records"]
    }
    knowledge_records = json.loads(knowledge_cache_path.read_text(encoding="utf-8"))["records"]
    knowledge_by_id = {
        int(record["id"]): record
        for record in knowledge_records
        if record.get("is_yuzheng") and record.get("author") == YUZHENG_NAME
    }
    space_by_slug = {space.get("slug"): space for space in spaces.values()}
    merged: dict[int, dict[str, Any]] = {}
    for raw in author_records:
        if raw.get("author") != YUZHENG_NAME:
            continue
        record = dict(raw)
        record["id"] = int(record["id"])
        authoritative = authoritative_by_id.get(record["id"])
        if not authoritative:
            raise ValueError(f"circle-{record['id']}: missing authoritative post body")
        if authoritative.get("author") != YUZHENG_NAME:
            raise ValueError(f"circle-{record['id']}: unexpected authoritative post author")
        for key in (
            "title",
            "slug",
            "url",
            "published_at",
            "updated_at",
            "status",
            "space_id",
            "space_name",
            "space_slug",
        ):
            if authoritative.get(key) is not None:
                record[key] = authoritative[key]
        record["body_markdown"] = html_to_markdown(
            authoritative.get("body_html") or "", redact_member_links=True
        )
        merged[record["id"]] = record

    unexpected_authoritative = sorted(set(authoritative_by_id) - set(merged))
    if unexpected_authoritative:
        raise ValueError(
            "Authoritative post cache contains unexpected IDs: "
            + ", ".join(str(value) for value in unexpected_authoritative)
        )

    # Preserve first-party Knowledge Bank articles that existed in the earlier public
    # snapshot but no longer appear in Circle's current cross-space search.
    knowledge_space = space_by_slug.get("ai-resources", {})
    for record_id, knowledge in knowledge_by_id.items():
        if record_id in merged:
            continue
        merged[record_id] = {
            "id": record_id,
            "title": knowledge["title"],
            "slug": knowledge.get("slug") or str(record_id),
            "url": knowledge["url"],
            "published_at": knowledge.get("published_at"),
            "updated_at": knowledge.get("updated_at"),
            "status": "published",
            "body_markdown": html_to_markdown(
                knowledge.get("body_html") or "", redact_member_links=True
            ),
            "author": YUZHENG_NAME,
            "space_id": knowledge_space.get("id"),
            "space_name": knowledge_space.get("name") or "Knowledge Bank",
            "space_slug": knowledge_space.get("slug") or "ai-resources",
            "legacy_public_snapshot": True,
        }

    corpus_dir = ROOT / "corpus" / "community-posts"
    catalog_path = ROOT / "catalog" / "community-posts.jsonl"
    reset_generated_dir(corpus_dir)
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_rows: list[dict[str, Any]] = []
    paths: dict[int, str] = {}
    public_records: dict[int, dict[str, Any]] = {}
    visibility_counts: dict[str, int] = {"public": 0, "members-only": 0, "hidden": 0}
    status_counts: dict[str, int] = {"current": 0, "archived": 0, "test": 0}

    for record in sorted(
        merged.values(), key=lambda item: (item.get("published_at") or "", int(item["id"]))
    ):
        space = spaces.get(int(record.get("space_id") or 0), {})
        if not space and record.get("space_slug"):
            space = space_by_slug.get(record.get("space_slug"), {})
        visibility = source_visibility(space)
        content_status = post_content_status(space)
        status_counts[content_status] = status_counts.get(content_status, 0) + 1
        if content_status in {"archived", "test"}:
            continue
        visibility_counts[visibility] = visibility_counts.get(visibility, 0) + 1
        body = record.get("body_markdown") or record.get("body") or ""
        body = sanitize_first_party_text(str(body))
        if not body:
            raise ValueError(f"circle-{record['id']}: first-party post has no body")
        filename = article_filename(record)
        target = corpus_dir / filename
        source_type = "knowledge-bank" if record.get("space_slug") == "ai-resources" else "community-post"
        fields = {
            "id": f"circle-{record['id']}",
            "title": record["title"],
            "author": "Yuzheng Sun",
            "source_type": source_type,
            "source_url": record["url"],
            "published_at": record.get("published_at"),
            "updated_at": record.get("updated_at"),
            "snapshot_at": snapshot_at,
            "community_space": record.get("space_name"),
            "community_space_slug": record.get("space_slug"),
            "source_visibility": visibility,
            "content_status": content_status,
            "rights_scope": "first-party",
            "license": "CC-BY-4.0",
            "third_party_exclusions": True,
            "contact_data_redacted": True,
        }
        access_note = "原始空间公开可见"
        if visibility == "members-only":
            access_note = "原始空间可能需要社区会员权限"
        elif visibility == "hidden":
            access_note = "原始空间当前不公开；正文由作者明确授权开放"
        source_note = (
            f"\n> 原文：[{record['title']}]({record['url']}) · "
            f"发布于 {(record.get('published_at') or '日期未知')[:10]} · {access_note}。"
            "本文保留发表时语境；其中第三方引文、发言、链接与商标不随正文重新授权。\n\n"
        )
        target.write_text(front_matter(fields) + source_note + body + "\n", encoding="utf-8")
        corpus_path = str(target.relative_to(ROOT))
        paths[int(record["id"])] = corpus_path
        public_records[int(record["id"])] = record
        catalog_rows.append(
            {
                "id": f"circle-{record['id']}",
                "title": record["title"],
                "author": "Yuzheng Sun",
                "url": record["url"],
                "published_at": record.get("published_at"),
                "updated_at": record.get("updated_at"),
                "space": record.get("space_name"),
                "space_slug": record.get("space_slug"),
                "source_type": source_type,
                "source_visibility": visibility,
                "content_status": content_status,
                "rights_scope": "first-party",
                "full_text_included": True,
                "corpus_path": corpus_path,
            }
        )

    with catalog_path.open("w", encoding="utf-8") as handle:
        for row in catalog_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    stats = {
        "reviewed": len(merged),
        "catalog": len(catalog_rows),
        "full_text": len(catalog_rows),
        "public_source": visibility_counts.get("public", 0),
        "members_only_source": visibility_counts.get("members-only", 0),
        "hidden_source": visibility_counts.get("hidden", 0),
        "archived_excluded": status_counts.get("archived", 0),
        "test_excluded": status_counts.get("test", 0),
    }
    return stats, paths, public_records


def comment_candidate(record: dict[str, Any], space: dict[str, Any], raw: str) -> bool:
    """Rules only: whether the substance review may consider this comment at all."""
    title = str(record.get("post_name") or "")
    return (
        record.get("author") == YUZHENG_NAME
        and bool(space)
        and source_visibility(space) == "public"
        and post_content_status(space) == "current"
        and record.get("space_slug") not in COMMENT_EXCLUDED_SPACES
        and len(comment_effective_text(raw)) >= COMMENT_MIN_EFFECTIVE_CHARS
        and not COMMENT_EXCLUDED_HINT.search(raw)
        and not COMMENT_EXCLUDED_POST_HINT.search(title)
        and not COMMENT_SENSITIVE_REVIEW_HINT.search(raw)
        and not COMMENT_SENSITIVE_REVIEW_HINT.search(title)
        and not raw.lstrip().startswith(("“", '"'))
        and not re.search(r"(?m)^\s*>", raw)
    )


def comment_candidates(
    records: list[dict[str, Any]],
    authoritative_by_id: dict[int, dict[str, Any]],
    spaces: dict[int, dict[str, Any]],
    own_titles: dict[int, str],
) -> Iterable[dict[str, Any]]:
    """Comments that pass the rules, each with the exact text the corpus would publish.

    The text comes from the single-comment HTML when it is cached (comments under Yuzheng's own
    posts), otherwise from the search export, whose text matches the HTML except where a member
    later changed the display name a mention shows; mentions are redacted either way.
    """
    for record in sorted(records, key=lambda item: (item.get("created_at") or "", int(item["id"]))):
        if record.get("author") != YUZHENG_NAME:
            raise ValueError(f"circle-comment-{record.get('id')}: unexpected author")
        comment_id = int(record["id"])
        authoritative = authoritative_by_id.get(comment_id)
        if authoritative and authoritative.get("author") != YUZHENG_NAME:
            raise ValueError(f"circle-comment-{comment_id}: unexpected authoritative author")
        if authoritative:
            raw = html_to_markdown(authoritative.get("body_html") or "", redact_member_links=True)
        else:
            raw = str(record.get("body") or "")
        space = spaces.get(int(record.get("space_id") or 0), {})
        if not comment_candidate(record, space, raw):
            continue
        post_id = int(record.get("post_id") or 0)
        own = post_id in own_titles
        parent_title = own_titles[post_id] if own else sanitize_first_party_text(str(record.get("post_name") or ""))
        if not parent_title.strip():
            continue
        text = sanitize_first_party_text(raw, comment=True)
        yield {
            "id": f"circle-comment-{comment_id}",
            "comment_id": comment_id,
            "post_id": post_id,
            "record": record,
            "space": space,
            "text": text,
            "text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "parent_title": parent_title.strip(),
            "own_parent": own,
            "body_source": "circle-comment-html" if authoritative else "circle-search-text",
        }


def load_comment_review(path: Path = COMMENT_REVIEW_PATH) -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8")).get("decisions") or {}


def export_community_comments(
    comments_cache_path: Path,
    authoritative_bodies_dir: Path,
    spaces_cache_path: Path,
    author_posts: dict[int, dict[str, Any]],
    snapshot_at: str,
    review_path: Path = COMMENT_REVIEW_PATH,
) -> dict[str, Any]:
    records = json.loads(comments_cache_path.read_text(encoding="utf-8"))["records"]
    authoritative_records = load_cache_directory(
        authoritative_bodies_dir, "authoritative Circle comment bodies"
    )
    authoritative_by_id = {int(record["id"]): record for record in authoritative_records}
    spaces = {
        int(space["id"]): space
        for space in json.loads(spaces_cache_path.read_text(encoding="utf-8"))["records"]
    }
    own_titles = {int(post_id): str(post["title"]) for post_id, post in author_posts.items()}
    candidates = list(comment_candidates(records, authoritative_by_id, spaces, own_titles))
    decisions = load_comment_review(review_path)
    unreviewed = [item["id"] for item in candidates
                  if (decisions.get(item["id"]) or {}).get("text_sha256") != item["text_sha256"]]
    if unreviewed:
        raise SystemExit(f"{len(unreviewed)} comments have no review of their current text "
                         f"(first: {unreviewed[0]}); run scripts/review_community_comments.py")
    corpus_dir = ROOT / "corpus" / "community-comments"
    catalog_path = ROOT / "catalog" / "community-comments.jsonl"
    reset_generated_dir(corpus_dir)
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_rows: list[dict[str, Any]] = []
    left_out: dict[str, int] = {}

    for item in candidates:
        category = decisions[item["id"]]["category"]
        if category not in COMMENT_REVIEW_INCLUDE:
            left_out[category] = left_out.get(category, 0) + 1
            continue
        record = item["record"]
        title = (f"对《{item['parent_title']}》的补充" if item["own_parent"]
                 else f"在《{item['parent_title']}》下的回复")
        date = (record.get("created_at") or "undated")[:10]
        target = corpus_dir / f"{date.replace('-', '')}-{item['comment_id']}.md"
        fields = {
            "id": item["id"],
            "title": title,
            "author": "Yuzheng Sun",
            "source_type": "community-comment",
            "source_url": record["url"],
            "published_at": record.get("created_at"),
            "snapshot_at": snapshot_at,
            "community_space_slug": record.get("space_slug"),
            "source_visibility": "public",
            "parent_post_id": f"circle-{item['post_id']}",
            "parent_post_title": item["parent_title"],
            "selection_rule": "reviewed-comment-v2",
            "review_category": category,
            "body_source": item["body_source"],
            "rights_scope": "first-party",
            "license": "CC-BY-4.0",
            "third_party_exclusions": True,
            "privacy_redactions": True,
        }
        source_note = (
            f"\n> [查看原评论及上下文]({record['url']}) · 发布于 {date} · 原始讨论公开可见。"
            "仓库只收立正本人的回复，已移除成员提及名称、联系方式和正文链接；"
            "原帖和其他成员的话不在本仓库许可范围内。\n\n"
        )
        target.write_text(front_matter(fields) + source_note + item["text"] + "\n", encoding="utf-8")
        catalog_rows.append(
            {
                "id": item["id"],
                "title": title,
                "author": "Yuzheng Sun",
                "url": record["url"],
                "published_at": record.get("created_at"),
                "space_slug": record.get("space_slug"),
                "source_visibility": "public",
                "parent_post_id": f"circle-{item['post_id']}",
                "parent_post_title": item["parent_title"],
                "review_category": category,
                "rights_scope": "first-party",
                "full_text_included": True,
                "corpus_path": str(target.relative_to(ROOT)),
            }
        )

    with catalog_path.open("w", encoding="utf-8") as handle:
        for row in catalog_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    stats = {
        "reviewed": len(records),
        "candidates": len(candidates),
        "included": len(catalog_rows),
        "left_out_by_review": dict(sorted(left_out.items())),
    }
    policy = {
        "schema_version": 2,
        "snapshot_at": snapshot_at,
        "source_author": YUZHENG_NAME,
        "source_comments_reviewed": len(records),
        "comment_candidates": len(candidates),
        "comments_included": len(catalog_rows),
        "scope": "comments under any post in a public, current space, except member introductions and events",
        "excluded_space_slugs": sorted(COMMENT_EXCLUDED_SPACES),
        "minimum_effective_characters": COMMENT_MIN_EFFECTIVE_CHARS,
        "excluded_private_context_hints": [
            "微信 / WeChat",
            "私信、私聊、群聊、短信或 DM",
            "电话、手机号、邮箱或住址",
            "加我、加群或联系我",
        ],
        "excluded_parent_post_hints": [
            "自我介绍与新人报道",
            "招聘、求职与内推",
        ],
        "excluded_sensitive_context": [
            "health, bereavement, minor status, immigration or layoff context",
            "personal income, compensation or financial context",
            "partner or private-conversation context",
            "internal community operations or sponsorship context",
        ],
        "review": {
            "file": "config/community-comment-review.json",
            "include": COMMENT_REVIEW_INCLUDE,
            "exclude": COMMENT_REVIEW_EXCLUDE,
            "left_out": dict(sorted(left_out.items())),
        },
        "privacy_redactions": [
            "Circle member mention names",
            "email addresses",
            "mainland mobile numbers",
            "all inline links and bare domains (the canonical Circle comment link is retained)",
        ],
        "rationale": (
            "Every comment Yuzheng wrote under a post in a public space is considered. Rules first remove "
            "contact details and private channels, introduction and hiring threads, other people's private "
            "circumstances, leading third-party quotations and comments under the minimum length; a pinned "
            "review then keeps each comment that states a view, advice, an explanation, his own experience "
            "or useful information, and leaves out small talk, administration, chat, replies that cannot be "
            "read without the thread, and anything about a member's private situation. Comments in "
            "members-only spaces are not included."
        ),
    }
    policy_path = ROOT / "config" / "community-comment-policy.json"
    policy_path.write_text(
        json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return stats


def export_knowledge_bank(
    cache_path: Path, community_paths: dict[int, str]
) -> dict[str, int]:
    payload = json.loads(cache_path.read_text(encoding="utf-8"))
    records = payload["records"]
    catalog_path = ROOT / "catalog" / "knowledge-bank.jsonl"
    legacy_corpus_dir = ROOT / "corpus" / "knowledge-bank"
    reset_generated_dir(legacy_corpus_dir)
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_rows: list[dict[str, Any]] = []
    full_text_count = 0
    for record in sorted(records, key=lambda item: item.get("published_at") or ""):
        is_yuzheng = bool(record.get("is_yuzheng")) and record.get("author") == YUZHENG_NAME
        corpus_path = community_paths.get(int(record["id"])) if is_yuzheng else None
        if corpus_path:
            full_text_count += 1
        catalog_rows.append(
            {
                "id": f"circle-{record['id']}",
                "title": record["title"],
                "author": "Yuzheng Sun" if is_yuzheng else record.get("author"),
                "url": record["url"],
                "published_at": record.get("published_at"),
                "updated_at": record.get("updated_at"),
                "rights_scope": "first-party" if is_yuzheng else "metadata-only",
                "full_text_included": bool(corpus_path),
                "corpus_path": corpus_path,
            }
        )
    with catalog_path.open("w", encoding="utf-8") as handle:
        for row in catalog_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return {"catalog": len(catalog_rows), "full_text": full_text_count}


def load_guests(path: Path) -> tuple[set[str], dict[str, list[str]]]:
    """Read explicit source relationships from the owning public directory."""
    catalog = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(catalog, dict) or catalog.get("schema_version") != 1:
        raise ValueError("Expected the shared guest catalog")
    entities = {e["entity_id"]: e for e in catalog["entities"]}
    sources = {s["source_id"]: s for s in catalog["sources"]}
    guest_ids: set[str] = set()
    names: dict[str, list[str]] = {}
    for row in catalog["appearances"]:
        video_id = sources[row["source_id"]]["video_id"]
        if video_id:
            guest_ids.add(video_id)
            names.setdefault(video_id, []).append(entities[row["entity_id"]]["display_name"])
    return guest_ids, names


def load_id_allowlist(path: Path) -> set[str]:
    """Load an explicit, reviewed set of video IDs; new videos default to metadata-only."""
    ids: list[str] = []
    for number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        value = raw.strip()
        if not value or value.startswith("#"):
            continue
        if not re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
            raise ValueError(f"{path.name}:{number}: invalid YouTube video ID {value!r}")
        ids.append(value)
    if len(ids) != len(set(ids)):
        raise ValueError(f"{path.name}: duplicate video IDs")
    return set(ids)


def classify_video_rights(
    video_id: str,
    title: str,
    guest_ids: set[str],
    rights_overrides: dict[str, str],
    transcript_allowlist: set[str],
) -> dict[str, str | list[str]]:
    exclusion_reasons: list[str] = []
    if video_id in guest_ids:
        exclusion_reasons.append("known-guest-index")
    if MIXED_SPEAKER_HINT.search(title):
        exclusion_reasons.append("mixed-speaker-title")
    if video_id in rights_overrides:
        exclusion_reasons.append(f"manual-review: {rights_overrides[video_id]}")

    if video_id in transcript_allowlist and exclusion_reasons:
        raise ValueError(
            f"{video_id}: transcript allowlist conflicts with mixed-speaker evidence: "
            + "; ".join(exclusion_reasons)
        )
    if exclusion_reasons:
        return {
            "rights_scope": "mixed-speakers",
            "speaker_classification": "mixed-speakers",
            "review_status": "excluded",
            "rights_reasons": exclusion_reasons,
        }
    if video_id in transcript_allowlist:
        return {
            "rights_scope": "first-party",
            "speaker_classification": "solo-yuzheng",
            "review_status": "approved",
            "rights_reasons": ["explicit-v1-transcript-allowlist"],
        }
    return {
        "rights_scope": "metadata-only",
        "speaker_classification": "unreviewed",
        "review_status": "unreviewed",
        "rights_reasons": ["not-in-transcript-allowlist"],
    }


def eligible_video(record: dict[str, Any]) -> bool:
    return (
        record.get("youtube_privacy") == "public"
        and record.get("content_class") == "normal_video"
        and record.get("podcast_policy") == "ready_public_normal"
        and record.get("local_status") == "ok"
    )


def video_publication_date(record: dict[str, Any], folder: Path) -> str | None:
    """Prefer the canonical publication date, then public platform metadata."""
    if record.get("youtube_published_at"):
        return str(record["youtube_published_at"])
    for path in sorted(folder.glob("*.info.json")):
        info = json.loads(path.read_text(encoding="utf-8"))
        if info.get("id") != record["video_id"]:
            continue
        timestamp = info.get("release_timestamp") or info.get("timestamp")
        if timestamp:
            return datetime.fromtimestamp(timestamp, timezone.utc).isoformat().replace("+00:00", "Z")
        date = info.get("upload_date")
        if date and re.fullmatch(r"\d{8}", str(date)):
            return datetime.strptime(str(date), "%Y%m%d").date().isoformat()
    date = str(record.get("upload_date") or "")
    if re.fullmatch(r"\d{8}", date):
        return datetime.strptime(date, "%Y%m%d").date().isoformat()
    return date or None


def export_videos(
    channel_root: Path,
    snapshot_at: str,
    rights_overrides: dict[str, str],
    transcript_allowlist: set[str],
) -> dict[str, int]:
    manifest_path = channel_root / "logs" / "library_manifest" / "library_manifest.json"
    guest_path = ROOT / "catalog" / "guests.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    guest_ids, guest_names = load_guests(guest_path)
    records = [record for record in manifest["records"] if eligible_video(record)]
    # Canonical transcript policies retain their exact snapshots across media refreshes.
    existing_catalog = ROOT / "catalog/videos.jsonl"
    policy_path = ROOT / "config" / "public-dialogue-policy.json"
    policy = json.loads(policy_path.read_text()) if policy_path.is_file() else {}
    dialogue_ids = {r["video_id"] for r in policy.get("records", [])}
    retained_rows = []
    retained_files = []
    if existing_catalog.is_file():
        for line in existing_catalog.read_text().splitlines():
            row = json.loads(line)
            if (row.get("inclusion_authorization") == "maintainer-request-2026-10-02-member-transcripts"
                    or (row.get("video_id") in dialogue_ids and row.get("transcript_included"))
                    or row.get("inclusion_authorization") == "maintainer-request-2026-10-04-values-conversations"):
                path = (ROOT / row["corpus_path"]).resolve()
                path.relative_to(ROOT.resolve())
                retained_rows.append(row)
                retained_files.append((path, path.read_bytes()))
    retained_ids = {row["video_id"] for row in retained_rows}
    records = [record for record in records if record["video_id"] not in retained_ids]
    eligible_ids = {record["video_id"] for record in records}
    stale_allowlist_ids = sorted(transcript_allowlist - eligible_ids - retained_ids)
    if stale_allowlist_ids:
        raise ValueError(
            "Transcript allowlist contains videos outside the eligible public snapshot: "
            + ", ".join(stale_allowlist_ids)
        )
    corpus_dir = ROOT / "corpus" / "videos"
    catalog_path = ROOT / "catalog" / "videos.jsonl"
    reset_generated_dir(corpus_dir)
    for path, contents in retained_files:
        path.write_bytes(contents)
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_rows: list[dict[str, Any]] = list(retained_rows)
    transcript_available = sum(bool(row.get("transcript_available")) for row in retained_rows)
    transcript_included = sum(bool(row.get("transcript_included")) for row in retained_rows)
    mixed_speaker_count = sum(row.get("speaker_classification") == "mixed-or-unresolved" for row in retained_rows)
    unreviewed_count = 0

    for record in sorted(records, key=lambda item: item.get("youtube_published_at") or ""):
        video_id = record["video_id"]
        title = record["title"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        folder = (channel_root / record["folder"]).resolve()
        folder.relative_to(channel_root.resolve())
        published_at = video_publication_date(record, folder)
        transcript_path = choose_transcript_path(folder, record.get("transcript_status"))
        has_transcript = transcript_path is not None
        if has_transcript:
            transcript_available += 1
        classification = classify_video_rights(
            video_id, title, guest_ids, rights_overrides, transcript_allowlist
        )
        rights_scope = str(classification["rights_scope"])
        rights_reasons = list(classification["rights_reasons"])
        if rights_scope == "mixed-speakers":
            mixed_speaker_count += 1
        elif rights_scope == "metadata-only":
            unreviewed_count += 1
        corpus_path: str | None = None
        cue_count = 0
        if has_transcript and rights_scope == "first-party":
            cues = parse_timed_transcript(transcript_path)
            cue_count = len(cues)
            if cues:
                date = (published_at or "undated")[:10]
                safe_date = date.replace("-", "")
                target = corpus_dir / f"{safe_date}-{video_id}.md"
                fields = {
                    "id": f"youtube-{video_id}",
                    "title": title,
                    "author": "Yuzheng Sun",
                    "source_type": "video-transcript",
                    "source_url": url,
                    "published_at": published_at,
                    "snapshot_at": snapshot_at,
                    "rights_scope": "first-party",
                    "speaker_classification": classification["speaker_classification"],
                    "review_status": classification["review_status"],
                    "license": "CC-BY-4.0",
                    "third_party_exclusions": True,
                    "transcript_status": record.get("transcript_status"),
                }
                lines = [front_matter(fields), f"# {title}\n"]
                lines.append(
                    f"> [观看原视频]({url}) · 字幕状态：`{record.get('transcript_status')}`。"
                    "字幕可能有转写错误，请以原视频为准。许可不覆盖发言中引用的第三方材料。\n"
                )
                for seconds, cue in cues:
                    time_url = f"{url}&t={seconds}s"
                    lines.append(f"[{display_timestamp(seconds)}]({time_url}) {cue}\n")
                target.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
                corpus_path = str(target.relative_to(ROOT))
                transcript_included += 1
        catalog_rows.append(
            {
                "id": f"youtube-{video_id}",
                "video_id": video_id,
                "title": title,
                "url": url,
                "published_at": published_at,
                "transcript_status": record.get("transcript_status"),
                "transcript_available": has_transcript,
                "transcript_included": bool(corpus_path),
                "cue_count": cue_count,
                "rights_scope": rights_scope,
                "speaker_classification": classification["speaker_classification"],
                "review_status": classification["review_status"],
                "rights_reason": "; ".join(rights_reasons),
                "guest_names": sorted(set(guest_names.get(video_id, []))),
                "corpus_path": corpus_path,
            }
        )
    with catalog_path.open("w", encoding="utf-8") as handle:
        for row in catalog_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    return {
        "catalog": len(catalog_rows),
        "transcript_available": transcript_available,
        "transcript_included": transcript_included,
        "mixed_speaker_metadata_only": mixed_speaker_count,
        "unreviewed_metadata_only": unreviewed_count,
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--channel-root",
        type=Path,
        required=True,
        help="Path to the local kedaibiao-channel repository",
    )
    parser.add_argument(
        "--knowledge-cache",
        type=Path,
        default=ROOT / ".source-cache" / "knowledge-bank.json",
        help="Sanitized Knowledge Bank catalog export",
    )
    parser.add_argument(
        "--community-posts-cache",
        type=Path,
        default=ROOT / ".source-cache" / "circle-author-posts.json",
        help="Sanitized Circle search export containing only YZ｜立正 posts",
    )
    parser.add_argument(
        "--community-post-bodies-dir",
        type=Path,
        default=ROOT / ".source-cache" / "circle-author-post-bodies",
        help="Sanitized get_post exports containing authoritative visible post HTML",
    )
    parser.add_argument(
        "--community-comments-cache",
        type=Path,
        default=ROOT / ".source-cache" / "circle-author-comments.json",
        help="Sanitized Circle search export containing only YZ｜立正 comments",
    )
    parser.add_argument(
        "--community-comment-bodies-dir",
        type=Path,
        default=ROOT / ".source-cache" / "circle-author-comment-bodies",
        help="Sanitized get_comment exports for eligible comments on Yuzheng-authored posts",
    )
    parser.add_argument(
        "--community-spaces-cache",
        type=Path,
        default=ROOT / ".source-cache" / "circle-spaces.json",
        help="Sanitized Circle space names, slugs, and visibility flags",
    )
    parser.add_argument("--snapshot-at", default="2026-08-30")
    parser.add_argument(
        "--rights-overrides",
        type=Path,
        default=ROOT / "config" / "video-rights-overrides.json",
        help="Reviewed video IDs that must remain metadata-only",
    )
    parser.add_argument(
        "--transcript-allowlist",
        type=Path,
        default=ROOT / "config" / "video-transcript-allowlist.txt",
        help="Explicitly reviewed solo-Yuzheng video IDs allowed to export full transcripts",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    channel_root = args.channel_root.expanduser().resolve()
    cache_path = args.knowledge_cache.expanduser().resolve()
    community_posts_path = args.community_posts_cache.expanduser().resolve()
    community_post_bodies_dir = args.community_post_bodies_dir.expanduser().resolve()
    community_comments_path = args.community_comments_cache.expanduser().resolve()
    community_comment_bodies_dir = args.community_comment_bodies_dir.expanduser().resolve()
    community_spaces_path = args.community_spaces_cache.expanduser().resolve()
    rights_path = args.rights_overrides.expanduser().resolve()
    allowlist_path = args.transcript_allowlist.expanduser().resolve()
    if not cache_path.is_file():
        raise SystemExit(f"Missing sanitized Knowledge Bank cache: {cache_path}")
    for label, path in (
        ("community posts", community_posts_path),
        ("community comments", community_comments_path),
        ("community spaces", community_spaces_path),
    ):
        if not path.is_file():
            raise SystemExit(f"Missing sanitized {label} cache: {path}")
    if not (channel_root / "logs" / "library_manifest" / "library_manifest.json").is_file():
        raise SystemExit(f"Not a kedaibiao-channel source root: {channel_root}")
    if not rights_path.is_file():
        raise SystemExit(f"Missing video rights override file: {rights_path}")
    if not allowlist_path.is_file():
        raise SystemExit(f"Missing transcript allowlist file: {allowlist_path}")
    rights_overrides = json.loads(rights_path.read_text(encoding="utf-8"))
    transcript_allowlist = load_id_allowlist(allowlist_path)
    community_posts, community_paths, author_posts = export_community_posts(
        community_posts_path,
        community_post_bodies_dir,
        community_spaces_path,
        cache_path,
        args.snapshot_at,
    )
    community_comments = export_community_comments(
        community_comments_path,
        community_comment_bodies_dir,
        community_spaces_path,
        author_posts,
        args.snapshot_at,
    )
    knowledge = export_knowledge_bank(cache_path, community_paths)
    videos = export_videos(
        channel_root, args.snapshot_at, rights_overrides, transcript_allowlist
    )
    print(
        json.dumps(
            {
                "community_posts": community_posts,
                "community_comments": community_comments,
                "knowledge_bank": knowledge,
                "videos": videos,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
