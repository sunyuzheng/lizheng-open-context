#!/usr/bin/env python3
"""Import the official course and membership pages as published originals; default dry-run.

Yuzheng decided on 2026-11-18 that the wording on his course pages counts as text he published (the words of
others on those pages do not). Questions about what the courses teach, cost and include had no original to answer
from: the AI-written context/superlinear-courses-map.md only guides reading, and older posts describe superseded
line-ups. These pages are the canonical owner of those facts.

config/course-pages-policy.json names each page, the sections taken and the parts left out (learner reviews and
stories, textbook excerpts by other authors, video players), and pins the extracted text by hash. A page is a living
document: re-import it after each release of the site, review the diff, then pin it again:

    python3 scripts/import_course_pages.py --fetch                  # check: fails if a live page no longer matches
    python3 scripts/import_course_pages.py --fetch --write-policy   # fetch, extract, pin after reviewing the text
    python3 scripts/import_course_pages.py --apply                  # write corpus/course-pages and the catalog

Fetched HTML stays in .source-cache/course-pages/ (not published).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

from enrich_provenance import write_markdown

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config/course-pages-policy.json"
CACHE = ROOT / ".source-cache/course-pages"
CATALOG = "catalog/course-pages.jsonl"
FOLDER = "corpus/course-pages"
AUTHORIZATION = "maintainer-request-2026-11-18-course-pages"
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
EMAIL_NOTE = "（邮箱地址见原页面）"
INVISIBLE = re.compile("[\u00ad\u200b\u200c\u200d\u2060\ufeff]")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
SKIP_TAGS = {"script", "style", "svg", "noscript", "template", "video", "audio", "picture", "img", "button", "iframe", "dialog"}
# Wrappers that keep a phrase together on narrow screens: their pieces are one run of text.
PHRASE_CLASSES = {"phrases", "phrase-lock", "halt", "arw-tie", "arw-tie-after", "arw-tie-before"}
# Placed between two separate labels the page sets side by side ("01" "AI Coding" "跨过动手的门槛").
SEPARATOR = "\x00"
CJK = "\u3000-\u303f\u4e00-\u9fff\uff00-\uffef"
BLOCK = {"summary", "p", "li", "dt", "dd", "blockquote", "figcaption", "tr", "h1", "h2", "h3", "h4", "h5", "h6", "div", "section",
         "article", "header", "footer", "aside", "ul", "ol", "dl", "table", "details", "small", "figure", "main", "nav"}


class Node:
    def __init__(self, tag: str, attrs: dict, parent: "Node | None"):
        self.tag, self.attrs, self.parent, self.children = tag, attrs, parent, []

    @property
    def classes(self) -> set[str]:
        return set(self.attrs.get("class", "").split())


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", {}, None)
        self.current = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, {k: v or "" for k, v in attrs}, self.current)
        self.current.children.append(node)
        if tag not in VOID:
            self.current = node

    def handle_startendtag(self, tag, attrs):
        self.current.children.append(Node(tag, {k: v or "" for k, v in attrs}, self.current))

    def handle_endtag(self, tag):
        node = self.current
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.current = node.parent

    def handle_data(self, data):
        self.current.children.append(data)


def matches(node: Node, selector: str) -> bool:
    """tag, .class, #id, tag.class / tag#id, or [attribute]."""
    if selector.startswith("[") and selector.endswith("]"):
        return selector[1:-1] in node.attrs
    match = re.fullmatch(r"([a-z0-9]*)(?:([.#])([A-Za-z0-9_-]+))?", selector)
    if not match:
        raise ValueError(f"unsupported selector {selector!r}")
    tag, kind, name = match.groups()
    if tag and node.tag != tag:
        return False
    if kind == ".":
        return name in node.classes
    if kind == "#":
        return node.attrs.get("id") == name
    return bool(tag)


def select(node: Node, selector: str) -> list[Node]:
    found = []
    for child in node.children:
        if isinstance(child, Node):
            if matches(child, selector):
                found.append(child)
            else:
                found.extend(select(child, selector))
    return found


def render(node: Node, drop: list[str], sections: tuple[str, ...] = ("h2",)) -> str:
    """Readable Markdown of a page part: headings, paragraphs, list items and table rows, in page order.

    The headings named in sections (tags, or "summary" for a question in a list of questions) are written as ##:
    the parser starts a retrievable chunk at each ##, so a question and its answer stay one unit titled by the
    question. Other headings are written one level lower than they would be."""
    out: list[str] = []

    def inline(n: Node) -> str:
        parts, previous = [], None
        for child in n.children:
            if isinstance(child, str):
                parts.append(child)
                previous = None if child.strip() else previous
            elif child.tag == "br":
                parts.append("\n")
                previous = None
            elif child.tag != "wbr" and not skipped(child):
                text = inline(child)
                if not text.strip():
                    continue
                if previous is not None and not (previous.classes | child.classes) & PHRASE_CLASSES:
                    parts.append(SEPARATOR)
                parts.append(text)
                previous = child
        return "".join(parts)

    def skipped(n: Node) -> bool:
        return (n.tag in SKIP_TAGS or n.attrs.get("aria-hidden") == "true" or "hidden" in n.attrs
                or any(matches(n, selector) for selector in drop))

    def clean(text: str) -> str:
        text = INVISIBLE.sub("", text)
        # Layout whitespace between Chinese characters is not a word space.
        text = re.sub(f"(?<=[{CJK}])[ \\t]+(?=[{CJK}])", "", text)
        text = re.sub(f"[ \\t]*{SEPARATOR}+[ \\t]*", SEPARATOR, text)
        text = re.sub(f"{SEPARATOR}(?=[，。、；：！？）」》])|(?<=[（「《]){SEPARATOR}", "", text)
        text = text.replace(SEPARATOR, " · ")
        lines = [re.sub(r"[ \t\r\f\v]+", " ", line).strip(" ·") for line in text.split("\n")]
        return "\n".join(line for line in lines if line)

    # Column names of the ARIA tables being read (role="table" built from divs, like a before/after table): each cell
    # after the first is written under its column's name ("以前：…", "学完：…"), since the bare text of a row cannot
    # say which column a sentence stood in. The header row itself is not written.
    table_headers: list[list[str]] = []

    def walk(n: Node) -> None:
        if skipped(n):
            return
        role = n.attrs.get("role")
        if role == "table":
            table_headers.append([])
            walk_node(n)
            table_headers.pop()
            return
        if role == "row" and table_headers:
            cells = [c for c in n.children if isinstance(c, Node) and c.attrs.get("role") in {"cell", "columnheader", "rowheader"} and not skipped(c)]
            if cells and all(c.attrs.get("role") == "columnheader" for c in cells):
                table_headers[-1] = [clean(inline(c)).replace("\n", " ") for c in cells]
                return
            for index, cell in enumerate(cells):
                label = table_headers[-1][index] if index < len(table_headers[-1]) else ""
                if index == 0 or not label or re.fullmatch(r"h[1-6]", cell.tag):
                    walk(cell)
                    continue
                text = clean(inline(cell)).replace("\n", " ")
                if text:
                    out.append(f"{label}：{text}")
            return
        walk_node(n)

    def walk_node(n: Node) -> None:
        if n.tag == "summary":
            # A question in a list of questions and answers.
            text = clean(inline(n)).replace("\n", " ")
            if text:
                out.append(("## " if "summary" in sections else "#### ") + text)
            return
        if re.fullmatch(r"h[1-6]", n.tag):
            text = clean(inline(n)).replace("\n", " ")
            if text:
                out.append(("## " if n.tag in sections else "#" * max(3, int(n.tag[1]) + 1) + " ") + text)
            return
        if n.tag == "tr":
            cells = [clean(inline(c)).replace("\n", " ") for c in n.children if isinstance(c, Node) and c.tag in {"td", "th"}]
            if any(cells):
                out.append("| " + " | ".join(cells) + " |")
            return
        if n.tag in {"p", "li", "dt", "dd", "blockquote", "figcaption"} or (
                n.tag in BLOCK and not any(isinstance(c, Node) and (c.tag in BLOCK or c.tag in {"tr", "td", "th"}) for c in n.children)):
            text = clean(inline(n))
            if text:
                out.append(("- " if n.tag == "li" else "") + text.replace("\n", " " if n.tag != "p" else "\n"))
            return
        # A mixed block: loose text between its block children is its own paragraph.
        loose: list[str] = []
        for child in n.children:
            if isinstance(child, str) or (isinstance(child, Node) and child.tag not in BLOCK and child.tag not in {"tr", "td", "th", "tbody", "thead"} and not re.fullmatch(r"h[1-6]", child.tag)):
                loose.append(child if isinstance(child, str) else ("" if skipped(child) else inline(child)))
                continue
            if clean("".join(loose)):
                out.append(clean("".join(loose)))
            loose = []
            walk(child)
        if clean("".join(loose)):
            out.append(clean("".join(loose)))

    walk(node)
    # A heading must not stand alone at the end, and a line never repeats the one before it.
    result: list[str] = []
    for line in out:
        if result and result[-1] == line:
            continue
        result.append(line)
    while result and result[-1].startswith("#"):
        result.pop()
    return "\n\n".join(result).strip() + "\n"


def extract(html: str, page: dict) -> str:
    tree = Tree()
    tree.feed(html)
    parts = []
    for selector in page["sections"]:
        nodes = select(tree.root, selector)
        if len(nodes) != 1:
            raise ValueError(f"{page['key']}: {selector} matches {len(nodes)} parts; the page changed, review the policy")
        parts.append(render(nodes[0], page.get("drop", []), tuple(page.get("chunk_at", ["h2"]))))
    text = "\n".join(parts)
    text = EMAIL.sub(EMAIL_NOTE, text)
    for phrase in page.get("must_contain", []):
        if phrase not in text:
            raise ValueError(f"{page['key']}: extracted text lacks {phrase!r}; review the policy")
    for phrase in page.get("must_not_contain", []):
        if phrase in text:
            raise ValueError(f"{page['key']}: extracted text still contains {phrase!r}, which the policy leaves out")
    return text


def sha256(data: str | bytes) -> str:
    return hashlib.sha256(data.encode("utf-8") if isinstance(data, str) else data).hexdigest()


def load_policy(path: Path = POLICY) -> dict:
    policy = json.loads(path.read_text(encoding="utf-8"))
    if policy.get("authorization") != AUTHORIZATION:
        raise ValueError("course page policy lacks the maintainer's authorization")
    return policy


def fetch(page: dict) -> Path:
    CACHE.mkdir(parents=True, exist_ok=True)
    request = urllib.request.Request(page["fetch_url"], headers={"User-Agent": "lizheng-open-context course-page import"})
    raw = urllib.request.urlopen(request, timeout=30).read()
    target = CACHE / f"{page['key']}.html"
    target.write_bytes(raw)
    return target


def document(page: dict, policy: dict, text: str) -> tuple[str, dict, str]:
    snapshot = page["snapshot_at"]
    path = f"{FOLDER}/{page['key']}.md"
    meta = {
        "id": f"course-page-{page['key']}", "title": page["title"], "author": "Yuzheng Sun",
        "publisher": "Yuzheng Sun", "original_author": "Yuzheng Sun",
        "snapshot_at": snapshot, "published_at": snapshot, "content_status": "current",
        "rights_scope": "first-party", "license": "CC-BY-4.0", "review_status": "maintainer-authorized",
        "content_origin": "yuzheng-published-text", "generation_method": "not-established",
        "evidence_role": "published-source", "yuzheng_stance_weight": "direct-with-quotation-boundaries",
        "language": "zh", "source_visibility": "public", "text_access": "public", "third_party_exclusions": True,
        "contact_data_redacted": True, "inclusion_authorization": AUTHORIZATION,
        "source_type": "course-page", "source_url": page["source_url"], "source_family": page["source_url"],
        "source_context": policy["source_context"], "attribution_note": policy["attribution_note"],
    }
    heading = f"# {page['title']}\n\n> 原页面：[{page['source_url']}]({page['source_url']}) · 本份文字取自 {snapshot} 的页面。\n\n"
    return path, meta, heading + text


def catalog_row(path: str, meta: dict, text_sha: str) -> dict:
    row = {key: value for key, value in meta.items() if key not in {"source_url"}}
    row.update(url=meta["source_url"], corpus_path=path, full_text_included=True, text_sha256=text_sha)
    return dict(sorted(row.items()))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--fetch", action="store_true", help="download the live pages into .source-cache first")
    parser.add_argument("--write-policy", action="store_true", help="pin the extracted texts (after reviewing them)")
    parser.add_argument("--apply", action="store_true", help="write corpus/course-pages and the catalog; never pushes")
    args = parser.parse_args()
    policy = load_policy()
    today = datetime.now(ZoneInfo("America/Los_Angeles")).date().isoformat()
    outputs = {}
    for page in policy["pages"]:
        cached = fetch(page) if args.fetch else CACHE / f"{page['key']}.html"
        html = cached.read_text(encoding="utf-8")
        text = extract(html, page)
        if args.write_policy:
            page.update(snapshot_at=today if args.fetch else page["snapshot_at"], html_sha256=sha256(html), text_sha256=sha256(text))
        elif page.get("text_sha256") != sha256(text):
            raise SystemExit(f"{page['key']}: the live page no longer matches the pinned text; review the change, then --fetch --write-policy and --apply")
        path, meta, body = document(page, policy, text)
        outputs[path] = (meta, body, page["text_sha256"])
        print(f"{page['key']}: {len(text)} characters from {page['fetch_url']}")
    if args.write_policy:
        POLICY.write_text(json.dumps(policy, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print("pinned", POLICY.relative_to(ROOT))
    if args.apply:
        folder = ROOT / FOLDER
        folder.mkdir(parents=True, exist_ok=True)
        for stale in folder.glob("*.md"):
            if str(stale.relative_to(ROOT)) not in outputs:
                stale.unlink()
        rows = []
        for path, (meta, body, text_sha) in outputs.items():
            write_markdown(ROOT / path, meta, body)
            rows.append(catalog_row(path, meta, text_sha))
        (ROOT / CATALOG).write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
        print("wrote", len(rows), "pages and", CATALOG)


if __name__ == "__main__":
    main()
