#!/usr/bin/env python3
"""Build the public corpus from sanitized first-party Circle exports and local media.

The exporter deliberately needs explicit source paths. Circle inventory inputs must
contain only posts and comments authored by YZ｜立正 plus non-sensitive space metadata;
authoritative text comes from sanitized single-post and single-comment HTML caches so
search-indexed attachments cannot become corpus text. It never reads credentials, member
profiles, other people's comment bodies, messages, or raw media.
"""

from __future__ import annotations

import argparse
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
CIRCLE_MENTION = re.compile(
    r"@[A-Za-z0-9_\u3400-\u9fff｜|·.-]{1,40}"
    r"(?:[ \t]+[A-Z][A-Za-z0-9_.-]{1,39})?"
)
COMMENT_EXCLUDED_HINT = re.compile(
    r"(?:微信|wechat|私信|私聊|群聊|微信群|在群里|群内|群中|加群|短信|"
    r"电话|手机号|邮箱|住址|地址是|加我|联系我|\bDM\b|"
    r"(?:跟|和|与).{0,12}(?:聊完|聊天|交流))",
    re.IGNORECASE,
)
COMMENT_EXCLUDED_POST_HINT = re.compile(
    r"(?:自我介绍|新人报[到道]|新同学|say hello|招聘|招人|求职|内推|岗位|"
    r"hiring|job opening|活动|直播|新课|课程|退款|refund|福利|early access|会员|"
    r"\bcourse\b|\bmaven\b|\bcohort\b|self[- ]paced|作业提交|office hours?|答疑通知)",
    re.IGNORECASE,
)
COMMENT_SENSITIVE_REVIEW_HINT = re.compile(
    r"(?:therapist|治疗师|心理咨询|抑郁|sponsor(?:ship)?|月收入|工资|薪资|报酬|"
    r"财务状况|PERM|EB-?1A|绿卡|被裁|裁员|未成年|\b17\s*岁|生病|离世|去世|"
    r"戒烟|伴侣|老婆|老公|男朋友|女朋友|私下|社群不赚钱|接管.{0,12}运营|"
    r"退款|refund|老学员|新学员|购买|优惠|折扣|报名|名额|课程|qualify|"
    r"付款|price|价格|预算|订单|客服|发票|上课|开课|lifetime|"
    r"\bcourse\b|\bmaven\b|\bcohort\b|self[- ]paced|"
    r"每月\s*\$?\s*\d+|\$\s*\d+.{0,12}(?:month|月))",
    re.IGNORECASE,
)
COMMENT_INCLUDED_SPACES = {
    "main",
    "posts",
    "share-your-projects",
    "ai-resources",
    "notes",
    "tools",
    "news",
    "guji",
    "recording",
}
COMMENT_MIN_EFFECTIVE_CHARS = 80
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
        {path.resolve() for path in candidates if path.is_file() and path.stat().st_size > 20},
        key=str,
    )
    if not usable:
        return None

    def score(path: Path) -> tuple[int, str]:
        name = path.name.lower()
        if name.endswith(".corrected.srt") or name.endswith(".final.srt"):
            priority = 0
        elif status == "human" and any(
            marker in name for marker in (".zh-hans.", ".zh-hant.", ".zh.", ".en.")
        ):
            priority = 1
        elif ".qwen." in name:
            priority = 4
        elif name.endswith(".srt"):
            priority = 2
        elif name.endswith(".vtt"):
            priority = 3
        else:
            priority = 5
        return priority, str(path)

    return min(usable, key=score)


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


def comment_is_included(record: dict[str, Any]) -> bool:
    body = str(record.get("body") or "")
    return (
        record.get("author") == YUZHENG_NAME
        and record.get("space_slug") in COMMENT_INCLUDED_SPACES
        and len(comment_effective_text(body)) >= COMMENT_MIN_EFFECTIVE_CHARS
        and not COMMENT_EXCLUDED_HINT.search(body)
        and not COMMENT_EXCLUDED_POST_HINT.search(str(record.get("post_name") or ""))
        and not COMMENT_SENSITIVE_REVIEW_HINT.search(body)
        and not body.lstrip().startswith(("“", '"'))
        and not re.search(r"(?m)^\s*>", body)
    )


def export_community_comments(
    comments_cache_path: Path,
    authoritative_bodies_dir: Path,
    spaces_cache_path: Path,
    author_posts: dict[int, dict[str, Any]],
    snapshot_at: str,
) -> dict[str, int]:
    records = json.loads(comments_cache_path.read_text(encoding="utf-8"))["records"]
    authoritative_records = load_cache_directory(
        authoritative_bodies_dir, "authoritative Circle comment bodies"
    )
    authoritative_by_id = {int(record["id"]): record for record in authoritative_records}
    spaces = {
        int(space["id"]): space
        for space in json.loads(spaces_cache_path.read_text(encoding="utf-8"))["records"]
    }
    corpus_dir = ROOT / "corpus" / "community-comments"
    catalog_path = ROOT / "catalog" / "community-comments.jsonl"
    reset_generated_dir(corpus_dir)
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_rows: list[dict[str, Any]] = []
    excluded_private_hint = 0
    excluded_non_author_parent = 0
    excluded_non_public_source = 0
    excluded_low_signal_or_space = 0

    for record in sorted(
        records, key=lambda item: (item.get("created_at") or "", int(item["id"]))
    ):
        if record.get("author") != YUZHENG_NAME:
            raise ValueError(f"circle-comment-{record.get('id')}: unexpected author")
        comment_id = int(record["id"])
        post_id = int(record.get("post_id") or 0)
        if post_id not in author_posts:
            excluded_non_author_parent += 1
            continue
        space = spaces.get(int(record.get("space_id") or 0), {})
        if source_visibility(space) != "public":
            excluded_non_public_source += 1
            continue
        authoritative = authoritative_by_id.get(comment_id)
        if not authoritative:
            raise ValueError(f"circle-comment-{comment_id}: missing authoritative comment body")
        if authoritative.get("author") != YUZHENG_NAME:
            raise ValueError(f"circle-comment-{comment_id}: unexpected authoritative author")
        record = dict(record)
        record["body"] = html_to_markdown(
            authoritative.get("body_html") or "", redact_member_links=True
        )
        if COMMENT_EXCLUDED_HINT.search(str(record.get("body") or "")):
            excluded_private_hint += 1
            continue
        if not comment_is_included(record):
            excluded_low_signal_or_space += 1
            continue
        own_parent = author_posts.get(post_id)
        visibility = source_visibility(space)
        body = sanitize_first_party_text(str(record.get("body") or ""), comment=True)
        title = f"对《{own_parent['title']}》的补充" if own_parent else "社区讨论补充"
        date = (record.get("created_at") or "undated")[:10]
        target = corpus_dir / f"{date.replace('-', '')}-{comment_id}.md"
        fields = {
            "id": f"circle-comment-{comment_id}",
            "title": title,
            "author": "Yuzheng Sun",
            "source_type": "community-comment",
            "source_url": record["url"],
            "published_at": record.get("created_at"),
            "snapshot_at": snapshot_at,
            "community_space_slug": record.get("space_slug"),
            "source_visibility": visibility,
            "parent_post_id": f"circle-{post_id}",
            "parent_post_title": own_parent.get("title") if own_parent else None,
            "selection_rule": "substantive-comment-v1",
            "rights_scope": "first-party",
            "license": "CC-BY-4.0",
            "third_party_exclusions": True,
            "privacy_redactions": True,
        }
        access_note = "原始讨论公开可见" if visibility == "public" else "原始讨论可能需要社区权限"
        source_note = (
            f"\n> [查看原评论及上下文]({record['url']}) · "
            f"发布于 {date} · {access_note}。"
            "仓库只保留立正本人在自己帖子下的评论，并已移除成员提及名称、联系方式和正文链接；"
            "周围成员内容不在本仓库许可范围内。\n\n"
        )
        target.write_text(front_matter(fields) + source_note + body + "\n", encoding="utf-8")
        corpus_path = str(target.relative_to(ROOT))
        catalog_rows.append(
            {
                "id": f"circle-comment-{comment_id}",
                "title": title,
                "author": "Yuzheng Sun",
                "url": record["url"],
                "published_at": record.get("created_at"),
                "space_slug": record.get("space_slug"),
                "source_visibility": visibility,
                "parent_post_id": f"circle-{post_id}",
                "parent_post_title": own_parent.get("title") if own_parent else None,
                "rights_scope": "first-party",
                "full_text_included": True,
                "corpus_path": corpus_path,
            }
        )

    with catalog_path.open("w", encoding="utf-8") as handle:
        for row in catalog_rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")
    stats = {
        "reviewed": len(records),
        "included": len(catalog_rows),
        "excluded_private_hint": excluded_private_hint,
        "excluded_non_author_parent": excluded_non_author_parent,
        "excluded_non_public_source": excluded_non_public_source,
        "excluded_low_signal_or_space": excluded_low_signal_or_space,
    }
    policy = {
        "schema_version": 1,
        "snapshot_at": snapshot_at,
        "source_author": YUZHENG_NAME,
        "source_comments_reviewed": len(records),
        "comments_included": len(catalog_rows),
        "included_space_slugs": sorted(COMMENT_INCLUDED_SPACES),
        "minimum_effective_characters": COMMENT_MIN_EFFECTIVE_CHARS,
        "parent_scope": "public-source comments on included Yuzheng-authored posts only",
        "excluded_private_context_hints": [
            "微信 / WeChat",
            "私信、私聊、群聊、短信或 DM",
            "电话、手机号、邮箱或住址",
            "加我、加群或联系我",
        ],
        "excluded_parent_post_hints": [
            "自我介绍与新人报道",
            "招聘、求职与内推",
            "活动、直播、课程、作业与答疑通知",
        ],
        "sensitive_context_review_hints": [
            "health, bereavement, minor status, immigration or layoff context",
            "personal income, compensation or financial context",
            "partner or private-conversation context",
            "internal community operations or sponsorship context",
            "course purchase, eligibility, discount, refund or support operations",
        ],
        "privacy_redactions": [
            "Circle member mention names",
            "email addresses",
            "mainland mobile numbers",
            "all inline links and bare domains (the canonical Circle comment link is retained)",
        ],
        "rationale": (
            "Comments are included only when they carry enough standalone substance for retrieval. "
            "Only public-source replies on included Yuzheng-authored posts are eligible by default. Short reactions, "
            "welcomes, administrative replies, member-introduction threads, jobs, events, leading "
            "third-party quotations, sensitive-personal context, archived/test spaces, and "
            "private-context hints stay out of the public corpus."
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
    guest_ids: set[str] = set()
    names: dict[str, list[str]] = {}
    for guest in json.loads(path.read_text(encoding="utf-8")):
        guest_name = guest.get("guest_name") or guest.get("guest_en_name") or "嘉宾"
        for video_id in guest.get("all_video_ids") or []:
            guest_ids.add(video_id)
            names.setdefault(video_id, []).append(guest_name)
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
    guest_path = channel_root / "guests.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    guest_ids, guest_names = load_guests(guest_path)
    records = [record for record in manifest["records"] if eligible_video(record)]
    eligible_ids = {record["video_id"] for record in records}
    stale_allowlist_ids = sorted(transcript_allowlist - eligible_ids)
    if stale_allowlist_ids:
        raise ValueError(
            "Transcript allowlist contains videos outside the eligible public snapshot: "
            + ", ".join(stale_allowlist_ids)
        )
    corpus_dir = ROOT / "corpus" / "videos"
    catalog_path = ROOT / "catalog" / "videos.jsonl"
    reset_generated_dir(corpus_dir)
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_rows: list[dict[str, Any]] = []
    transcript_available = 0
    transcript_included = 0
    mixed_speaker_count = 0
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
