#!/usr/bin/env python3
"""Import the Chinese editions Yuzheng authorized on 2026-10-04; default dry-run.

Both are AI rewrites, in his Chinese voice, of English works he wrote or co-wrote:

* Growth Data Analytics Playbook (Mengying Li, Joe Kumar and Yuzheng Sun; Statsig Press, 2025). The Chinese
  edition is published free at lizheng.ai; its source is the site's content/books/growth-data-analytics-playbook-zh/.
* His posts on the Statsig blog, two of them co-written. Source: a folder of adapted Markdown with manifest.json.

config/chinese-editions-policy.json pins every included text by hash. After reviewing new source text, refresh it
with --write-policy, then import with --apply. Figures are not copied: each becomes its caption, with a pointer to
where the picture can be seen.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from enrich_provenance import write_markdown
from rights import LICENSE_TEXTS, REFERENCE_USE

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config/chinese-editions-policy.json"
AUTHORIZATION = "maintainer-request-2026-10-04-chinese-editions"
SNAPSHOT = "2026-10-04"
BOOK_CATALOG = "catalog/book-chapters.jsonl"
BLOG_CATALOG = "catalog/blog-posts.jsonl"
BOOK_FOLDER = "corpus/book-chapters"
BLOG_FOLDER = "corpus/blog-posts"
BOOK_TITLE = "Growth Data Analytics Playbook"
BOOK_SITE = "https://www.lizheng.ai/book/growth-data-analytics-playbook"
BOOK_ORIGINAL_URL = "https://www.amazon.com/Growth-Data-Analytics-Playbook-Product-Market/dp/1544549822"
BOOK_PUBLISHED = "2025-11-18"
BOOK_AUTHORS = "Mengying Li, Joe Kumar, Yuzheng Sun"
LICENSE_URL = f"https://github.com/sunyuzheng/lizheng-open-context/blob/main/{LICENSE_TEXTS[REFERENCE_USE]}"
FIGURE = re.compile(r"^!\[([^\]]*)\]\([^)]+\)\s*$", re.M)

SHARED = dict(
    author="AI", publisher="Yuzheng Sun", snapshot_at=SNAPSHOT, generated_at=SNAPSHOT, content_status="current",
    rights_scope="publisher-authorized-adaptation", license=REFERENCE_USE, review_status="maintainer-authorized",
    content_origin="ai-translation", generation_method="ai-translation", evidence_role="translation",
    yuzheng_stance_weight="verify-original", language="zh", original_language="en",
    source_visibility="public", text_access="public", third_party_exclusions=True,
    inclusion_authorization=AUTHORIZATION,
)


def sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def strip_title(markdown: str) -> tuple[str, str]:
    """The H1 and the text after it."""
    lines = markdown.rstrip("\n").split("\n")
    if not lines or not lines[0].startswith("# "):
        raise ValueError("source text must start with an H1")
    return lines[0][2:].strip(), "\n".join(lines[1:]).strip() + "\n"


def figures_as_captions(markdown: str, where: str) -> str:
    """Each figure becomes its caption; the picture itself stays at `where`."""
    return FIGURE.sub(lambda match: f"> {match[1]}（图见{where}）", markdown)


# ---------- sources ----------

def book_sources(book_dir: Path) -> list[dict]:
    book = json.loads((book_dir / "book.json").read_text(encoding="utf-8"))
    entries = [{"key": "about", "file": book["front"], "label": "", "title": "关于这本书", "url": BOOK_SITE,
                "original": "Introduction"}]
    for chapter in book["chapters"]:
        key = "conclusion" if chapter["slug"] == "conclusion" else f"ch{int(chapter['slug']):02d}"
        entries.append({"key": key, "file": chapter["file"], "label": chapter["label"], "title": chapter["title"],
                        "url": f"{BOOK_SITE}/{chapter['slug']}", "original": chapter["original"]})
    for entry in entries:
        entry["text"] = (book_dir / "chapters" / entry["file"]).read_text(encoding="utf-8")
    return entries


def byline(author: dict) -> str:
    return re.sub(r",\s*PhD$", "", author["name"]).strip()


def blog_sources(blog_dir: Path) -> list[dict]:
    manifest = json.loads((blog_dir / "manifest.json").read_text(encoding="utf-8"))
    entries = []
    for article in manifest["articles"]:
        entries.append({
            "key": article["slug"], "file": article["file"], "url": article["url"],
            "title": article["title_zh"], "original": article["title_en"], "published_at": article["published_date"],
            "authors": [byline(author) for author in article["authors"]],
            "co_authors": [byline(author) for author in article["authors"] if not author.get("is_yuzheng")],
            "text": (blog_dir / article["file"]).read_text(encoding="utf-8"),
        })
    return entries


def build_policy(book_dir: Path, blog_dir: Path) -> dict:
    return {
        "authorization": AUTHORIZATION,
        "snapshot_at": SNAPSHOT,
        "note": "Yuzheng asked to rewrite his book and his Statsig blog posts in his Chinese voice and include them; he holds the right to publish the book (Statsig Press) and states he holds the rights to the blog posts. Text only: figures are reduced to captions.",
        "book": {
            "title": BOOK_TITLE, "authors": BOOK_AUTHORS.split(", "), "publisher": "Statsig Press",
            "published_at": BOOK_PUBLISHED, "isbn": "9781544549828", "edition_url": BOOK_SITE,
            "entries": [{"key": entry["key"], "title": entry["title"], "url": entry["url"],
                         "text_sha256": sha256(entry["text"])} for entry in book_sources(book_dir)],
        },
        "blog": {
            "site": "https://www.statsig.com/blog",
            "posts": [{"key": entry["key"], "title": entry["title"], "url": entry["url"],
                       "published_at": entry["published_at"], "authors": entry["authors"],
                       "text_sha256": sha256(entry["text"])} for entry in blog_sources(blog_dir)],
        },
    }


def load_policy(path: Path = POLICY) -> dict:
    policy = json.loads(path.read_text(encoding="utf-8"))
    if policy.get("authorization") != AUTHORIZATION:
        raise ValueError("Chinese edition policy lacks the explicit inclusion authorization")
    return policy


def checked(entries: list[dict], approved: list[dict], kind: str) -> list[dict]:
    by_key = {entry["key"]: entry for entry in entries}
    if sorted(by_key) != sorted(item["key"] for item in approved):
        raise ValueError(f"{kind}: source entries differ from the reviewed policy")
    for item in approved:
        if sha256(by_key[item["key"]]["text"]) != item["text_sha256"]:
            raise ValueError(f"{kind} {item['key']}: text differs from the reviewed policy; review and --write-policy")
    return [by_key[item["key"]] for item in approved]


# ---------- documents ----------

def book_document(entry: dict) -> tuple[str, dict, str]:
    heading, body = strip_title(entry["text"])
    title = f"《{BOOK_TITLE}》中文版 · {heading}"
    meta = dict(
        id=f"gdap-zh-{entry['key']}", title=title, original_title=entry["original"], **SHARED,
        original_author=BOOK_AUTHORS, source_type="book-chapter", source_url=entry["url"],
        original_source_url=BOOK_ORIGINAL_URL, source_family=entry["url"], published_at=BOOK_PUBLISHED,
        original_published_at=BOOK_PUBLISHED, translation_publication_status="published-free-at-lizheng-ai",
        source_context="One chapter of the free Chinese edition of a co-authored book (Statsig Press, 2025), rewritten by AI in Yuzheng's Chinese voice and published by him at lizheng.ai. The date is the English original's.",
        attribution_note=("《Growth Data Analytics Playbook》中文版：原书由Mengying Li、Joe Kumar和孙煜征合著，Statsig Press 2025年出版；"
                          "中文版由AI按立正的中文表达习惯改写，立正授权在lizheng.ai免费发布，不是他亲笔的中文。书里的「我们」指三位作者，"
                          "不能整段当作立正一个人的立场；只有第十章Marketplace的故事是他本人的经历。核对具体说法请回到英文原书。"),
    )
    notice = (f"> **中文版** · 《{BOOK_TITLE}》中文版的一部分。原书由Mengying Li、Joe Kumar和孙煜征合著（Statsig Press，2025）；"
              f"中文版由AI按立正的中文习惯改写，立正授权在[lizheng.ai]({BOOK_SITE})免费发布。按[立正参考使用许可]({LICENSE_URL})使用；"
              f"图和完整排版见[在线版]({entry['url']})。")
    text = f"# {title}\n\n{notice}\n\n{figures_as_captions(body, '在线版')}"
    return f"{BOOK_FOLDER}/{BOOK_PUBLISHED.replace('-', '')}-gdap-zh-{entry['key']}.md", meta, text


def blog_document(entry: dict) -> tuple[str, dict, str]:
    heading, body = strip_title(entry["text"])
    if heading != entry["title"]:
        raise ValueError(f"{entry['key']}: H1 differs from the manifest title")
    co = entry["co_authors"]
    authors = ", ".join(entry["authors"])
    shared_view = (f"本文由{'、'.join(co)}和立正合著，文中的观点属于两位作者，不能整篇当作立正一个人的立场。" if co else "")
    meta = dict(
        id=f"statsig-blog-{entry['key']}-zh", title=entry["title"], original_title=entry["original"], **SHARED,
        original_author=authors, source_type="blog-post", source_url=entry["url"], original_source_url=entry["url"],
        source_family=entry["url"], published_at=entry["published_at"], original_published_at=entry["published_at"],
        translation_publication_status="repository-reading-aid-not-platform-publication",
        source_context="Chinese adaptation of a post Yuzheng published on the Statsig blog, rewritten by AI in his Chinese voice; the date is the English original's. Figures are reduced to captions.",
        attribution_note=("立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。"
                          + shared_view + "文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。"),
    )
    if co:
        meta["co_authors"] = co
    notice = (f"> **中文版** · 立正在Statsig博客发表的文章「{entry['original']}」的中文版，AI按他的中文习惯改写。"
              f"按[立正参考使用许可]({LICENSE_URL})使用；图见[英文原文]({entry['url']})。")
    text = f"# {entry['title']}\n\n{notice}\n\n{figures_as_captions(body, '英文原文')}"
    return f"{BLOG_FOLDER}/{entry['published_at'].replace('-', '')}-{entry['key']}-zh.md", meta, text


def prepare(book_dir: Path, blog_dir: Path, policy: dict, root: Path = ROOT):
    book = checked(book_sources(book_dir), policy["book"]["entries"], "book")
    blog = checked(blog_sources(blog_dir), policy["blog"]["posts"], "blog")
    outputs = {}
    for catalog, documents in ((BOOK_CATALOG, [book_document(entry) for entry in book]),
                               (BLOG_CATALOG, [blog_document(entry) for entry in blog])):
        rows = []
        for relative, meta, text in documents:
            row = {key: value for key, value in meta.items() if key != "source_url"}
            rows.append({**row, "url": meta["source_url"], "corpus_path": relative, "full_text_included": True})
        outputs[catalog] = (documents, rows)
    return outputs


def apply_prepared(root: Path, outputs: dict) -> None:
    for catalog, (documents, rows) in outputs.items():
        folder = root / (BOOK_FOLDER if catalog == BOOK_CATALOG else BLOG_FOLDER)
        folder.mkdir(parents=True, exist_ok=True)
        keep = {Path(relative).name for relative, _, _ in documents}
        for stale in folder.glob("*.md"):
            if stale.name not in keep:
                stale.unlink()
        for relative, meta, text in documents:
            write_markdown(root / relative, meta, text)
        (root / catalog).write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--book", type=Path, required=True, help="the site's content/books/growth-data-analytics-playbook-zh")
    parser.add_argument("--blog", type=Path, required=True, help="folder of adapted Statsig blog posts with manifest.json")
    parser.add_argument("--write-policy", action="store_true", help="pin the current source texts after reviewing them")
    parser.add_argument("--apply", action="store_true", help="write the local corpus and catalogs; never pushes")
    args = parser.parse_args()
    if args.write_policy:
        POLICY.write_text(json.dumps(build_policy(args.book, args.blog), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    outputs = prepare(args.book, args.blog, load_policy())
    if args.apply:
        apply_prepared(ROOT, outputs)
    print(json.dumps({"mode": "local-apply" if args.apply else "dry-run",
                      **{catalog: len(rows) for catalog, (_, rows) in outputs.items()}}, ensure_ascii=False))


if __name__ == "__main__":
    main()
