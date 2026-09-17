#!/usr/bin/env python3
"""Apply attribution and import an explicitly selected published English snapshot.

Run after export_public_corpus.py. Requires sanitized source caches; never reads
local unpublished English translations or assumes that a publisher is an author.
"""
from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

from export_public_corpus import front_matter, html_to_markdown, sanitize_first_party_text

ROOT = Path(__file__).resolve().parents[1]
FM = re.compile(r"\A---\n(.*?)\n---\n", re.S)
PROVENANCE_KEYS = (
    "author", "publisher", "original_author", "original_source_url", "original_published_at",
    "content_origin", "generation_method", "evidence_role", "yuzheng_stance_weight",
    "attribution_note", "language", "source_family", "source_context", "license",
)
NOTICE_START = "<!-- provenance:start -->"
NOTICE_END = "<!-- provenance:end -->"


def read_markdown(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    match = FM.match(raw)
    if not match:
        raise ValueError(f"Missing front matter: {path.name}")
    meta = {}
    for line in match[1].splitlines():
        key, value = line.split(":", 1)
        try:
            meta[key] = json.loads(value.strip())
        except json.JSONDecodeError:
            meta[key] = value.strip()
    return meta, raw[match.end():]


def write_markdown(path: Path, meta: dict, body: str) -> None:
    body = re.sub(re.escape(NOTICE_START) + r".*?" + re.escape(NOTICE_END), "", body, flags=re.S).lstrip()
    note = meta["attribution_note"]
    notice = f"{NOTICE_START}\n> Attribution / 归属：{note}\n{NOTICE_END}\n\n"
    path.write_text(front_matter(meta) + "\n" + notice + body, encoding="utf-8")


def default_provenance(meta: dict, body: str, *, synthesis: bool = False) -> dict:
    source_type = meta.get("source_type")
    source_url = meta.get("source_url", "")
    language = "en" if meta.get("community_space_slug") == "ai-resources-en" else "zh"
    if synthesis:
        return dict(author="AI", publisher="Yuzheng Sun", original_author="See cited sources",
                    content_origin="ai-synthesis", generation_method="ai-written",
                    evidence_role="secondary-synthesis", yuzheng_stance_weight="secondary-only",
                    attribution_note="本文件由 AI 撰写／综合，整理对象是立正及所引来源；不是立正亲笔、逐字原话或逐句认可的证明。请回到原文核实，不能用综合层覆盖直接来源。",
                    source_family=meta.get("id"), language=language,
                    source_context="AI-authored repository synthesis of public sources; not a new statement by Yuzheng.")
    if source_type == "video-transcript":
        return dict(publisher="Yuzheng Sun", original_author="Yuzheng Sun",
                    content_origin="yuzheng-spoken-source", generation_method="transcription",
                    evidence_role="primary-speech", yuzheng_stance_weight="direct-with-quotation-boundaries",
                    attribution_note="立正主讲内容的转录；只将他本人明确表达的判断归给他。朗读、转述的社区文章、提问、案例与引文仍归原作者；同一人说出口不等于同一人创作。未标明引文作者时保持未知，以原视频与时间码为准。",
                    source_family=source_url, language=language,
                    source_context="Public presentation; quoted or discussed community material is contextual third-party evidence.")
    return dict(author="Yuzheng Sun", publisher="Yuzheng Sun", original_author="Yuzheng Sun",
                content_origin="yuzheng-published-text", generation_method="not-established",
                evidence_role="published-source", yuzheng_stance_weight="direct-with-quotation-boundaries",
                attribution_note="发布于立正账号；发布归属不证明文字全部由本人亲笔撰写。引用、访谈嘉宾、社区提问与案例归相应作者／说话人；其中的他人主张不能直接算作立正立场。",
                source_family=source_url, language=language,
                source_context="Dated published post or reply; preserve the distinction between publisher, narrator, and quoted contributor.")


def english_provenance(record: dict) -> dict:
    raw = record["body_html"]
    opening = html.unescape(re.sub(r"<[^>]+>", "", raw[:2200]))
    author_match = re.match(r"\s*Author:\s*(.*?)\s*\|", opening)
    aliases = {"立正": "Yuzheng Sun", "课代表立正": "Yuzheng Sun", "YZ｜立正": "Yuzheng Sun", "鸭哥": "Yan Wang 鸭哥"}
    publisher = record["author"]
    original_author = aliases.get(author_match[1], author_match[1]) if author_match else aliases.get(publisher, publisher)
    if original_author == "Superlinear Academy":
        original_author = "Unresolved original author"
    original_match = re.search(r'<a[^>]+href="([^"]+)"[^>]*>See original</a>', raw[:2200])
    original_url = html.unescape(original_match[1]) if original_match else record["url"]
    published_match = re.search(r"Published (\d{4}-\d{2}-\d{2})", opening[:500])
    translated = "Translated by Superlinear Bot" in opening[:500]
    reposted = "Reposted by Superlinear Bot" in opening[:500]
    generation = "ai-translation" if translated else "bot-repost-writing-process-unverified" if reposted else "not-established"
    first_party = original_author == "Yuzheng Sun"
    note = f"Original author: {original_author}. Published by: {publisher}. "
    note += "AI translation by Superlinear Bot; verify wording against the original. " if translated else "Bot repost; this alone does not establish who translated or wrote the English. " if reposted else "English writing/translation process is not established by the source. "
    note += "This is a derivative of Yuzheng's source, not independent corroboration or proof of his exact English wording." if first_party and (translated or reposted) else "Attribute only the author's own statements to Yuzheng; quotations retain their original speakers." if first_party else "Community reference: these ideas and first-person experiences are NOT Yuzheng's statements or biography. Inclusion does not imply his endorsement."
    return dict(author=original_author, original_author=original_author, publisher=publisher,
                original_source_url=original_url, original_published_at=published_match[1] if published_match else None,
                language="en", content_origin="yuzheng-derivative" if first_party and (translated or reposted) else "yuzheng-published-text" if first_party else "third-party-community",
                generation_method=generation, evidence_role="translation-or-repost" if translated or reposted else "published-source" if first_party else "community-reference",
                yuzheng_stance_weight="verify-original" if first_party and (translated or reposted) else "direct-with-quotation-boundaries" if first_party else "not-evidence",
                source_family=original_url, source_context="Published English Knowledge Bank: original author, reposting account and generation process are separate roles.",
                attribution_note=note, rights_scope="first-party" if first_party else "third-party-reference",
                license="CC-BY-4.0" if first_party else "LicenseRef-Original-Rights-Retained")


def annotate_existing(overrides: dict) -> dict[str, dict]:
    by_id = {}
    for directory in ("context", "examples", "corpus/community-posts", "corpus/community-comments", "corpus/videos"):
        for path in sorted((ROOT / directory).glob("*.md")):
            meta, body = read_markdown(path)
            if directory in {"context", "examples"} and not meta.get("source_url"):
                meta["source_url"] = "https://github.com/sunyuzheng/lizheng-open-context/blob/main/" + str(path.relative_to(ROOT))
            meta.update(default_provenance(meta, body, synthesis=directory in {"context", "examples"}))
            meta.update(overrides.get(meta["id"], {}))
            write_markdown(path, meta, body)
            by_id[meta["id"]] = meta
    return by_id


def import_english(cache: Path, by_id: dict[str, dict]) -> list[dict]:
    data = json.loads(cache.read_text(encoding="utf-8"))
    records = data["records"]
    if len({r["id"] for r in records}) != len(records):
        raise ValueError("Duplicate English source IDs")
    policy = json.loads((ROOT / "config/english-source-policy.json").read_text())
    if {r["id"] for r in records} != set(policy["included_post_ids"]):
        raise ValueError("English input differs from reviewed published source allowlist")
    directory = ROOT / "corpus/english-community"
    directory.mkdir(exist_ok=True)
    rows = []
    for record in records:
        if record["space_id"] != policy["space_id"] or "/c/ai-resources-en/" not in record["url"]:
            raise ValueError("Unexpected English source space")
        identity = f"circle-{record['id']}"
        provenance = english_provenance(record)
        meta = dict(id=identity, title=record["title"], source_type="english-community",
                    source_url=record["url"], published_at=record["published_at"], updated_at=record.get("updated_at"),
                    snapshot_at=data["snapshot_at"], source_visibility="public", content_status="current",
                    third_party_exclusions=True, **provenance)
        if identity in by_id:
            paths = [p for p in (ROOT / "corpus/community-posts").glob("*.md") if read_markdown(p)[0]["id"] == identity]
            path = paths[0]
            old, body = read_markdown(path)
            old.update(provenance)
            write_markdown(path, old, body)
            by_id[identity] = old
        else:
            path = directory / f"{record['published_at'][:10].replace('-', '')}-{record['id']}.md"
            # Strip profile links without deleting the explicit author credit.
            raw = re.sub(r'<a\b[^>]*href="[^"]*/u/[^"]*"[^>]*>(.*?)</a>', r'\1', record["body_html"], flags=re.S)
            raw = re.sub(r'<a\b[^>]*class="file"[^>]*>.*?</a>', '', raw, flags=re.S)
            body = sanitize_first_party_text(html_to_markdown(raw, redact_member_links=True))
            write_markdown(path, meta, f"# {record['title'].strip()}\n\n" + body + "\n")
            by_id[identity] = meta
        rows.append(dict(id=identity, title=record["title"], url=record["url"],
                         published_at=record["published_at"], snapshot_at=data["snapshot_at"],
                         source_type="english-community", full_text_included=True,
                         corpus_path=str(path.relative_to(ROOT)), **provenance))
    (ROOT / "catalog/english-community.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows))
    return rows


def sync_catalogs(by_id: dict[str, dict], overrides: dict | None = None) -> None:
    for path in (ROOT / "catalog").glob("*.jsonl"):
        rows = [json.loads(line) for line in path.read_text().splitlines()]
        for row in rows:
            meta = by_id.get(row["id"])
            if meta:
                row.update({k: meta[k] for k in PROVENANCE_KEYS if k in meta})
            elif "content_origin" not in row:
                row.update(content_origin="metadata-only", evidence_role="discovery-only", yuzheng_stance_weight="not-evidence",
                           generation_method="metadata-extraction", attribution_note="Discovery metadata only; do not infer Yuzheng's views or quote an unavailable transcript.")
            if not meta and overrides:
                row.update(overrides.get(row["id"], {}))
            if not meta:
                row.setdefault("author", "Not established from metadata")
                row.setdefault("original_author", row["author"])
                row.setdefault("publisher", "Yuzheng Sun" if row.get("video_id") else "Source publishing account not recorded")
                row.setdefault("source_family", row.get("url", row["id"]))
                row.setdefault("source_context", "Public discovery catalog; authorship and speaking roles must be checked at the original source.")
        path.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--english-cache", type=Path, required=True)
    args = parser.parse_args()
    overrides = json.loads((ROOT / "config/attribution-overrides.json").read_text())
    by_id = annotate_existing(overrides)
    english = import_english(args.english_cache, by_id)
    sync_catalogs(by_id, overrides)
    print(json.dumps({"english_sources": len(english), "english_first_party": sum(r["original_author"] == "Yuzheng Sun" for r in english), "english_third_party_or_unresolved": sum(r["original_author"] != "Yuzheng Sun" for r in english), "annotated_sources": len(by_id)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
