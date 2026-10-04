#!/usr/bin/env python3
"""Write the human index (INDEX.md and index/*.md) from the catalogs.

The pages are generated: change a catalog, the course map, or this script, then rerun
`python3 scripts/validate_release.py --write-manifest`. Validation fails on a stale page.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from urllib.parse import quote

from rights import LICENSE_TEXTS, REFERENCE_USE, RETAINED

ROOT = Path(__file__).resolve().parents[1]
GENERATED = "<!-- 由 scripts/build_index.py 根据 catalog/ 生成，请不要手改。Generated from catalog/; do not edit by hand. -->"
UNDATED = "日期未知"
LICENSE_NAMES = {
    "CC-BY-4.0": "CC BY 4.0",
    REFERENCE_USE: "立正参考使用许可",
    RETAINED: "原作者保留",
    "CC0-1.0": "CC0 1.0",
}


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def front_matter(path: Path) -> dict:
    match = re.match(r"\A---\n(.*?)\n---\n", path.read_text(encoding="utf-8"), re.S)
    meta = {}
    for line in match[1].splitlines() if match else []:
        key, _, value = line.partition(":")
        try:
            meta[key.strip()] = json.loads(value.strip())
        except json.JSONDecodeError:
            meta[key.strip()] = value.strip()
    return meta


def cell(text: object) -> str:
    """Plain text that stays inside one Markdown table cell or link label."""
    value = re.sub(r"\s+", " ", str(text or "")).strip().replace("\\", "\\\\")
    for char in "|[]*_`<>":
        value = value.replace(char, "\\" + char)
    return value


def relative(page: str, target: str) -> str:
    return "../" * page.count("/") + quote(target)


def link(page: str, label: str, target: str) -> str:
    """A link to a repository path (relative to the page) or to an absolute URL."""
    href = target if re.match(r"^https?://", target) else relative(page, target)
    return f"[{cell(label)}]({href})"


def license_link(page: str, license: str) -> str:
    return link(page, LICENSE_NAMES[license], LICENSE_TEXTS[license])


def github_anchor(heading: str) -> str:
    """GitHub's heading anchor: lowercase, punctuation removed, spaces to hyphens."""
    return re.sub(r"[^\w\- ]", "", heading.strip().lower()).replace(" ", "-")


def day(value: object) -> str:
    return str(value)[:10] if value else UNDATED


def newest_first(rows: list[dict], key: str = "published_at") -> list[dict]:
    ordered = sorted(rows, key=lambda row: str(row.get("title") or ""))
    return sorted(ordered, key=lambda row: str(row.get(key) or ""), reverse=True)


def by_year(rows: list[dict], key: str = "published_at") -> list[tuple[str, list[dict]]]:
    groups: dict[str, list[dict]] = {}
    for row in newest_first(rows, key):
        groups.setdefault(str(row.get(key))[:4] if row.get(key) else UNDATED, []).append(row)
    return sorted(groups.items(), key=lambda item: (item[0] == UNDATED, 0 if item[0] == UNDATED else -int(item[0])))


def table(header: list[str], rows: list[list[str]], numeric: set[int] = frozenset()) -> list[str]:
    align = ["---:" if index in numeric else "---" for index in range(len(header))]
    return ["| " + " | ".join(header) + " |", "| " + " | ".join(align) + " |", *("| " + " | ".join(row) + " |" for row in rows)]


def lesson_key(title: str) -> tuple[int, int]:
    label = title.partition("｜")[0]
    match = re.match(r"第(\d+)课", label)
    if not match:
        return (0, 0)
    return (int(match[1]), 2 if "下" in label else 1 if "上" in label else 0)


def framework_headings(path: Path) -> dict[str, tuple[str, str]]:
    """'框架二' -> (short label, anchor) from the framework reference's level-2 headings."""
    found = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = re.match(r"^## (框架[一二三四五六七八九十]+)：(.+)$", line)
        if match:
            short = re.sub(r"（.*?）", "", f"{match[1]}：{match[2]}").strip()
            found[match[1]] = (short, github_anchor(line[3:]))
    return found


def course_page(root: Path) -> str:
    page = "index/zhenbenshi-course.md"
    rows = read_jsonl(root / "catalog/course-lessons.jsonl")
    course = json.loads((root / "config/zhenbenshi-course-map.json").read_text(encoding="utf-8"))
    frameworks = framework_headings(root / "context/zhenbenshi-frameworks.md")
    reference = license_link(page, REFERENCE_USE)
    out = [
        GENERATED,
        "",
        "# 《真本事》课程文字稿",
        "",
        f"超线性学院会员课程《真本事：从会工作到会赚钱》共 {len(rows)} 节视频课。这里按课程顺序列出每节课下方的文字稿；课号与书中章节一一对应，第 11 课分上下两节。",
        "",
        f"- **怎么用**：文字可以阅读、搜索、放进不收费的 AI 问答工具，也可以短引用，按{reference}使用。课程视频和课件仍需[超线性学院会员]({course['course_url']})。",
        f"- **配套整理**：七套框架的整理版见{link(page, '《真本事》完整框架参考', 'context/zhenbenshi-frameworks.md')}，按问题找章节见{link(page, '《真本事》阅读地图', 'context/zhenbenshi-reading-map.md')}。这两份由 AI 整理，课文才是原文。",
        f"- **机器可读**：{link(page, 'catalog/course-lessons.jsonl', 'catalog/course-lessons.jsonl')}",
    ]
    known = {section["id"] for section in course["sections"]}
    stray = sorted({row["section_id"] for row in rows} - known)
    if stray:
        raise ValueError(f"course lessons in unnamed sections: {stray}")
    for section in course["sections"]:
        lessons = sorted((row for row in rows if row["section_id"] == section["id"]), key=lambda row: lesson_key(row["title"]))
        body = []
        for row in lessons:
            label, _, name = row["title"].partition("｜")
            number = lesson_key(row["title"])[0]
            related = []
            for key in course["frameworks"].get(str(row["lesson_id"]), []):
                if key not in frameworks:
                    raise ValueError(f"{row['lesson_id']}: {key} is not a heading in context/zhenbenshi-frameworks.md")
                short, anchor = frameworks[key]
                related.append(f"[{cell(short)}]({relative(page, 'context/zhenbenshi-frameworks.md')}#{anchor})")
            body.append([
                cell(label),
                link(page, name or row["title"], row["corpus_path"]),
                f"第 {number} 章" if number else "—",
                "<br>".join(related) or "—",
                f"[会员观看]({row['url']})",
            ])
        out += ["", f"## {section['name']}", "", *table(["课", "文字稿", "书中", "相关框架", "课程页面"], body)]
    return "\n".join(out) + "\n"


def community_page(root: Path) -> str:
    page = "index/community-posts.md"
    posts = read_jsonl(root / "catalog/community-posts.jsonl")
    comments = read_jsonl(root / "catalog/community-comments.jsonl")
    members = sum(row.get("source_visibility") == "members-only" for row in posts)
    out = [
        GENERATED,
        "",
        "# 社区帖子与评论",
        "",
        f"立正在超线性学院（Superlinear Academy）发布的 {len(posts)} 篇帖子和 {len(comments)} 条评论，按发布时间从新到旧排列。全文按{license_link(page, 'CC-BY-4.0')}开放，注明作者和出处即可转载、改编。",
        "",
        f"- **会员空间**：{members} 篇原帖发在需要会员的空间，作者已授权开放这些帖子的正文；同一页面上其他成员的内容不在这里。",
        f"- **机器可读**：{link(page, 'catalog/community-posts.jsonl', 'catalog/community-posts.jsonl')} · {link(page, 'catalog/community-comments.jsonl', 'catalog/community-comments.jsonl')}",
        "",
        "## 帖子",
    ]
    for year, rows in by_year(posts):
        body = []
        for row in rows:
            tags = [cell(row.get("space") or "")]
            if row.get("source_visibility") == "members-only":
                tags.append("会员空间")
            body.append([day(row.get("published_at")), link(page, row["title"], row["corpus_path"]), " · ".join(t for t in tags if t), f"[原帖]({row['url']})"])
        out += ["", f"### {year}（{len(rows)} 篇）", "", *table(["日期", "标题", "空间", "原帖"], body)]
    body = [
        [day(row.get("published_at")), link(page, row["title"], row["corpus_path"]), f"[原评论]({row['url']})"]
        for row in newest_first(comments)
    ]
    out += [
        "",
        f"## 评论（{len(comments)} 条）",
        "",
        "只收立正自己公开帖子下、原本就公开的本人评论；成员提及、联系方式和正文链接已移除。",
        "",
        *table(["日期", "评论", "原评论"], body),
    ]
    return "\n".join(out) + "\n"


def video_kind(row: dict) -> str:
    if not row.get("transcript_included"):
        return "只有目录"
    if row.get("speaker_classification") != "solo-yuzheng":
        return "会员 · 对话" if row.get("source_visibility") == "members-only" else "公开 · 对话"
    return "会员 · 本人主讲" if row.get("source_visibility") == "members-only" else "本人主讲"


def transcript_groups(videos: list[dict]) -> dict[str, int]:
    """Transcript counts by who speaks and which license applies."""
    groups = {"open-solo": 0, "open-solo-member": 0, "member-solo": 0, "member-mixed": 0, "public-mixed": 0, "listed": 0}
    for row in videos:
        kind = video_kind(row)
        if kind == "只有目录":
            groups["listed"] += 1
        elif kind == "会员 · 对话":
            groups["member-mixed"] += 1
        elif kind == "公开 · 对话":
            groups["public-mixed"] += 1
        elif row.get("license") == "CC-BY-4.0":
            groups["open-solo"] += 1
            groups["open-solo-member"] += kind == "会员 · 本人主讲"
        else:
            groups["member-solo"] += 1
    return groups


def video_page(root: Path) -> str:
    page = "index/videos.md"
    videos = read_jsonl(root / "catalog/videos.jsonl")
    groups = transcript_groups(videos)
    open_label = f"本人主讲（含 {groups['open-solo-member']} 条早先收录的会员视频）" if groups["open-solo-member"] else "本人主讲"
    out = [
        GENERATED,
        "",
        "# 视频目录",
        "",
        f"立正 YouTube 频道「课代表立正」的 {len(videos)} 条视频，按发布时间从新到旧排列。其中 {len(videos) - groups['listed']} 条有字幕全文：",
        "",
        *table(["类型", "数量", "字幕的许可"], [
            [open_label, str(groups["open-solo"]), license_link(page, "CC-BY-4.0")],
            ["会员 · 本人主讲", str(groups["member-solo"]), license_link(page, REFERENCE_USE)],
            ["会员 · 对话", str(groups["member-mixed"]), f"{license_link(page, REFERENCE_USE)}；嘉宾的话归嘉宾本人"],
            ["公开 · 对话", str(groups["public-mixed"]), f"{license_link(page, REFERENCE_USE)}；嘉宾的话归嘉宾本人"],
            ["只有目录", str(groups["listed"]), "没有字幕全文；标题、日期和链接按" + license_link(page, "CC0-1.0") + "开放"],
        ], numeric={1}),
        "",
        "会员视频需要频道会员才能观看，字幕文字已获授权开放。「会员 · 本人主讲」经人工核对只有立正一人讲述；「会员 · 对话」和「公开 · 对话」里嘉宾、主持人和提问者的话归他们本人。「公开 · 对话」是立正 2026-10-04 指定收录的、塑造他价值观的几场公开对话，这些对话里他本人的话另见" + link(page, "塑造价值观的对话", "index/values-conversations.md") + "。「只有目录」多是嘉宾访谈、多人对话或尚未复核说话人的视频。",
        "",
        f"机器可读：{link(page, 'catalog/videos.jsonl', 'catalog/videos.jsonl')}",
    ]
    for year, rows in by_year(videos):
        body = [
            [day(row.get("published_at")), f"[{cell(row['title'])}]({row['url']})",
             link(page, "全文", row["corpus_path"]) if row.get("transcript_included") else "—", video_kind(row)]
            for row in rows
        ]
        out += ["", f"## {year}（{len(rows)} 条）", "", *table(["日期", "视频", "字幕", "类型"], body)]
    return "\n".join(out) + "\n"


def english_page(root: Path) -> str:
    page = "index/english.md"
    articles = read_jsonl(root / "catalog/english-community.jsonl")
    translations = read_jsonl(root / "catalog/english-translations.jsonl")
    own = sum(row.get("original_author") == "Yuzheng Sun" for row in articles)
    out = [
        GENERATED,
        "",
        "# 英文资料",
        "",
        "## 英文社区文章",
        "",
        f"超线性学院公开英文空间里选定收录的 {len(articles)} 篇文章。{own} 篇源于立正，按{license_link(page, 'CC-BY-4.0')}开放；"
        f"其余 {len(articles) - own} 篇是其他作者的文章，{license_link(page, RETAINED)}，不能当作立正的观点。",
        "",
        f"机器可读：{link(page, 'catalog/english-community.jsonl', 'catalog/english-community.jsonl')}",
        "",
        *table(["日期", "标题", "原作者", "许可", "原文"], [
            [day(row.get("published_at")), link(page, row["title"], row["corpus_path"]), cell(row.get("original_author")),
             LICENSE_NAMES[row["license"]], f"[原文]({row['url']})"]
            for row in newest_first(articles)
        ]),
        "",
        "## 英文 AI 译稿",
        "",
        f"立正本人主讲视频的 {len(translations)} 份英文 AI 译稿，按{license_link(page, 'CC-BY-4.0')}开放。它们是阅读辅助，不是立正的英文原话；引用前请回到原视频核实。",
        "",
        f"机器可读：{link(page, 'catalog/english-translations.jsonl', 'catalog/english-translations.jsonl')}",
        "",
        *table(["原视频日期", "标题", "原视频"], [
            [day(row.get("published_at")), link(page, row["title"], row["corpus_path"]), f"[YouTube]({row['url']})"]
            for row in newest_first(translations)
        ]),
    ]
    return "\n".join(out) + "\n"


def knowledge_bank_page(root: Path) -> str:
    page = "index/knowledge-bank.md"
    rows = read_jsonl(root / "catalog/knowledge-bank.jsonl")
    full = sum(bool(row.get("full_text_included")) for row in rows)
    out = [
        GENERATED,
        "",
        "# Knowledge Bank 目录",
        "",
        f"超线性学院 Knowledge Bank 的 {len(rows)} 篇公开文章。立正本人的 {full} 篇有全文，链接到社区帖子全文；其他作者的文章这里只列标题、作者、日期和链接，全文请到原站阅读，权利归原作者。",
        "",
        f"机器可读：{link(page, 'catalog/knowledge-bank.jsonl', 'catalog/knowledge-bank.jsonl')}",
    ]
    for year, group in by_year(rows):
        body = [
            [day(row.get("published_at")), f"[{cell(row['title'])}]({row['url']})", cell(row.get("author")),
             link(page, "全文", row["corpus_path"]) if row.get("full_text_included") else "—"]
            for row in group
        ]
        out += ["", f"## {year}（{len(group)} 篇）", "", *table(["日期", "标题", "作者", "全文"], body)]
    return "\n".join(out) + "\n"


BOOK_SITE = "https://www.lizheng.ai/book/growth-data-analytics-playbook"


def book_order(row: dict) -> tuple[int, int]:
    key = str(row["id"]).removeprefix("gdap-zh-")
    return (0, 0) if key == "about" else (2, 0) if key == "conclusion" else (1, int(key.removeprefix("ch")))


def book_page(root: Path) -> str:
    page = "index/growth-data-analytics-playbook-zh.md"
    rows = sorted(read_jsonl(root / "catalog/book-chapters.jsonl"), key=book_order)
    reference = license_link(page, REFERENCE_USE)
    body = [[cell(row["title"].partition(" · ")[2]), f"[在线阅读]({row['url']})", link(page, "全文", row["corpus_path"])] for row in rows]
    out = [
        GENERATED,
        "",
        "# 《Growth Data Analytics Playbook》中文版",
        "",
        "原书由Mengying Li、Joe Kumar和孙煜征合著，Statsig Press 2025年出版。中文版由AI按立正的中文表达习惯整本改写，保留全部框架、案例和练习，立正授权在lizheng.ai免费发布；每章可以在线读，也可以下载EPUB和PDF。",
        "",
        f"- **怎么用**：按{reference}使用。书里的「我们」指三位作者，不能整段当作立正一个人的立场；具体说法请回到英文原书核对。",
        f"- **图**：这里只收文字，图只保留图注；图和完整排版见[在线版]({BOOK_SITE})。",
        f"- **机器可读**：{link(page, 'catalog/book-chapters.jsonl', 'catalog/book-chapters.jsonl')}",
        "",
        *table(["章节", "在线阅读", "全文"], body),
    ]
    return "\n".join(out) + "\n"


def blog_page(root: Path) -> str:
    page = "index/statsig-blog.md"
    rows = read_jsonl(root / "catalog/blog-posts.jsonl")
    reference = license_link(page, REFERENCE_USE)
    shared = sum(bool(row.get("co_authors")) for row in rows)
    body = [[day(row.get("published_at")), cell(row["title"]), f"[{cell(row['original_title'])}]({row['url']})",
             cell(row.get("original_author")), link(page, "全文", row["corpus_path"])] for row in newest_first(rows)]
    out = [
        GENERATED,
        "",
        "# Statsig博客文章中文版",
        "",
        f"立正在Statsig官方博客发表的 {len(rows)} 篇英文文章（其中 {shared} 篇合著），由AI按他的中文表达习惯完整改写：论证、例子、数字和结论都保留，没有加原文没有的事实或经历。",
        "",
        f"- **怎么用**：按{reference}使用。合著文章的观点属于两位作者；文中引用的他人观点归原作者。具体说法请回到英文原文核对。",
        "- **图**：这里只收文字，图只保留图注；图在英文原文里。",
        f"- **机器可读**：{link(page, 'catalog/blog-posts.jsonl', 'catalog/blog-posts.jsonl')}",
        "",
        *table(["日期", "中文标题", "英文原文", "作者", "全文"], body),
    ]
    return "\n".join(out) + "\n"


def conversations_page(root: Path) -> str:
    page = "index/values-conversations.md"
    rows = sorted(read_jsonl(root / "catalog/conversation-excerpts.jsonl"), key=lambda row: str(row.get("published_at")))
    videos = {row["video_id"]: row for row in read_jsonl(root / "catalog/videos.jsonl")}
    reference, cc_by = license_link(page, REFERENCE_USE), license_link(page, "CC-BY-4.0")
    body = []
    for row in rows:
        video = videos[row["video_id"]]
        access = "会员视频" if row.get("source_visibility") == "members-only" else "公开视频"
        title = re.sub(r"^立正本人的话 · ", "", row["title"])
        body.append([day(row.get("published_at")), f"[{cell(title)}]({row['url']})", cell("、".join(row.get("guest_names") or [])),
                     access, link(page, "全文", video["corpus_path"]), link(page, f"{row['excerpt_count']} 段", row["corpus_path"])])
    out = [
        GENERATED,
        "",
        "# 塑造价值观的对话",
        "",
        f"立正说，问道（格桑泽仁）和跟王路、赵智沉、Leon 的对话，是他价值观塑造的重要组成部分。这里按时间列出这 {len(rows)} 场对话，"
        f"每场都有字幕全文，以及逐段核对说话人后摘出的立正本人的话（共 {sum(int(row.get('excerpt_count') or 0) for row in rows)} 段）。",
        "",
        f"- **立正本人的话**：只收能从上下文确认是他说的段落，引文与字幕逐字一致，发布前逐段核对。会员视频里的摘录按{reference}使用，公开视频里的按{cc_by}。每段的小标题和「背景」由 AI 写成。",
        f"- **字幕全文**：嘉宾、主持人和提问者的话归他们本人，不能当作立正的立场；按{reference}使用。",
        f"- **来龙去脉**：每场对话里他带进去了什么、接住了什么、后来写进了哪些帖子和课，见{link(page, '塑造价值观的对话：阅读地图', 'context/values-conversations-map.md')}（AI 整理）。",
        f"- **机器可读**：{link(page, 'catalog/conversation-excerpts.jsonl', 'catalog/conversation-excerpts.jsonl')}",
        "",
        *table(["日期", "对话", "嘉宾", "原视频", "字幕", "立正本人的话"], body),
    ]
    return "\n".join(out) + "\n"


def hub_page(root: Path) -> str:
    page = "INDEX.md"
    count = lambda name: len(read_jsonl(root / f"catalog/{name}.jsonl"))
    videos = read_jsonl(root / "catalog/videos.jsonl")
    groups = transcript_groups(videos)
    english = read_jsonl(root / "catalog/english-community.jsonl")
    own_english = sum(row.get("original_author") == "Yuzheng Sun" for row in english)
    other_english = sum(row.get("original_author") != "Yuzheng Sun" for row in english)
    kb = read_jsonl(root / "catalog/knowledge-bank.jsonl")
    excerpts = read_jsonl(root / "catalog/conversation-excerpts.jsonl")
    context_files = sorted((root / "context").glob("*"))
    cc_by, reference, retained, cc0 = (license_link(page, key) for key in ("CC-BY-4.0", REFERENCE_USE, RETAINED, "CC0-1.0"))
    comments = count("community-comments")
    # Same heading text as community_page writes for its comment section.
    comments_anchor = github_anchor(f"评论（{comments} 条）")
    full_text = [
        ["《真本事》课程文字稿", f"{count('course-lessons')} 份", link(page, "按课程顺序", "index/zhenbenshi-course.md"), link(page, "corpus/course-lessons/", "corpus/course-lessons/"), reference],
        ["《Growth Data Analytics Playbook》中文版", f"{count('book-chapters')} 份", link(page, "按章节", "index/growth-data-analytics-playbook-zh.md"), link(page, "corpus/book-chapters/", "corpus/book-chapters/"), reference],
        ["Statsig博客文章中文版", f"{count('blog-posts')} 篇", link(page, "按日期", "index/statsig-blog.md"), link(page, "corpus/blog-posts/", "corpus/blog-posts/"), reference],
        ["社区帖子", f"{count('community-posts')} 篇", link(page, "按年份", "index/community-posts.md"), link(page, "corpus/community-posts/", "corpus/community-posts/"), cc_by],
        ["社区评论", f"{comments} 条", f"[在帖子目录末尾](index/community-posts.md#{comments_anchor})", link(page, "corpus/community-comments/", "corpus/community-comments/"), cc_by],
        ["视频字幕：本人主讲", f"{groups['open-solo']} 份", link(page, "视频目录", "index/videos.md"), link(page, "corpus/videos/", "corpus/videos/"), cc_by],
        ["视频字幕：会员视频 · 本人主讲", f"{groups['member-solo']} 份", link(page, "视频目录", "index/videos.md"), link(page, "corpus/videos/", "corpus/videos/"), reference],
        ["视频字幕：会员视频 · 对话", f"{groups['member-mixed']} 份", link(page, "视频目录", "index/videos.md"), link(page, "corpus/videos/", "corpus/videos/"), f"{reference}；嘉宾的话归嘉宾"],
        ["视频字幕：公开视频 · 对话", f"{groups['public-mixed']} 份", link(page, "视频目录", "index/videos.md"), link(page, "corpus/videos/", "corpus/videos/"), f"{reference}；嘉宾的话归嘉宾"],
        ["对话里立正本人的话", f"{sum(int(row.get('excerpt_count') or 0) for row in excerpts)} 段", link(page, "塑造价值观的对话", "index/values-conversations.md"), link(page, "corpus/conversation-excerpts/", "corpus/conversation-excerpts/"), f"会员视频里的：{reference}；公开视频里的：{cc_by}"],
        ["英文文章：源于立正", f"{own_english} 篇", link(page, "英文资料", "index/english.md"), link(page, "corpus/english-community/", "corpus/english-community/"), cc_by],
        ["英文文章：其他作者", f"{other_english} 篇", link(page, "英文资料", "index/english.md"), link(page, "corpus/english-community/", "corpus/english-community/"), retained],
        ["英文 AI 译稿", f"{count('english-translations')} 份", link(page, "英文资料", "index/english.md"), link(page, "corpus/english-translations/", "corpus/english-translations/"), cc_by],
        ["AI 整理与《真本事》框架", f"{len(context_files)} 份", f"[见下文](#{github_anchor('AI 整理与《真本事》框架')})", link(page, "context/", "context/"), cc_by],
    ]
    listed = [
        ["视频目录", f"{len(videos)} 条", link(page, "视频目录", "index/videos.md"), link(page, "catalog/videos.jsonl", "catalog/videos.jsonl"), f"{groups['listed']} 条只有目录、没有字幕"],
        ["Knowledge Bank", f"{len(kb)} 篇", link(page, "Knowledge Bank 目录", "index/knowledge-bank.md"), link(page, "catalog/knowledge-bank.jsonl", "catalog/knowledge-bank.jsonl"), f"立正的 {sum(bool(r.get('full_text_included')) for r in kb)} 篇有全文，其他作者只列标题和链接"],
    ]
    contexts = []
    for path in context_files:
        title = front_matter(path).get("title") if path.suffix == ".md" else "判断卡：按问题加载的推理导航"
        contexts.append(f"- {link(page, title or path.name, f'context/{path.name}')}")
    out = [
        GENERATED,
        "",
        "# 目录",
        "",
        "这里列出仓库里的全部资料：有多少、放在哪、能怎么用。想按内容找，用 `python3 scripts/search.py \"你的问题\"`，或者去[问问立正](https://ask.lizheng.ai)直接提问。版权的完整说明见 [LICENSE.md](LICENSE.md)。",
        "",
        "## 有全文的资料",
        "",
        *table(["资料", "数量", "目录页", "文件夹", "可以怎么用"], full_text, numeric={1}),
        "",
        f"许可的意思：{cc_by}注明作者和出处即可转载、改编、商用；{reference}可以阅读、搜索、放进不收费的 AI 问答工具和短引用，不能整篇转载、收费使用或训练模型；{retained}只供阅读和检索参考。",
        "",
        "## 只有目录的资料",
        "",
        *table(["资料", "数量", "目录页", "机器可读", "说明"], listed, numeric={1}),
        "",
        f"目录数据（`catalog/`、`config/`、`index/` 和本页）按{cc0}开放。",
        "",
        "## AI 整理与《真本事》框架",
        "",
        "这些文件由 AI 根据上面的原文整理，适合快速理解和按问题找原文；它们不是立正的原话，回答时要回到原文核实。",
        "",
        *contexts,
        f"- 示例回答：{link(page, '如何找到适合写在简历里的项目，并复盘它', 'examples/resume-projects.md')}",
        "",
        "## 给开发者",
        "",
        f"- {link(page, '回答协议', 'docs/answering-contract.md')}：怎样区分原文、综合和推断",
        f"- {link(page, '自己做一个 Agent', 'docs/build-your-own-agent.md')}：最小可用的检索与推荐流程",
        f"- {link(page, '来源模型', 'docs/source-model.md')}：字段、来源优先级与时间",
        f"- {link(page, '隐私与权利', 'docs/privacy-and-rights.md')}：什么进仓库、什么不进",
        f"- {link(page, 'release-manifest.json', 'release-manifest.json')}：每个文件的哈希与许可；{link(page, 'REUSE.toml', 'REUSE.toml')}：机器可读的许可对照",
        "",
        "## English",
        "",
        "This page indexes everything in the repository: how much there is, where it lives, and how you may use it. "
        "Yuzheng Sun's posts, comments, solo video transcripts, English originals, AI translations, and AI syntheses are CC BY 4.0. "
        "Yuzheng's own turns excerpted from the conversations that shaped his values follow their source: CC BY 4.0 from public videos, the Lizheng Reference Use License from member videos. "
        "The *Zhenbenshi* course texts, member video transcripts, the transcripts of six public conversations with guests, and the Chinese editions of *Growth Data Analytics Playbook* and Yuzheng's Statsig blog posts (AI rewrites in his Chinese voice) are under the Lizheng Reference Use License: read, search, use in free AI tools, and quote briefly, "
        "but do not republish them in full, charge for them, or train models on them. Articles by other authors keep their original rights. "
        "Catalogs and index pages are CC0; code and documentation are MIT. See [LICENSE.md](LICENSE.md).",
    ]
    return "\n".join(out) + "\n"


PAGES = {
    "INDEX.md": hub_page,
    "index/zhenbenshi-course.md": course_page,
    "index/values-conversations.md": conversations_page,
    "index/growth-data-analytics-playbook-zh.md": book_page,
    "index/statsig-blog.md": blog_page,
    "index/community-posts.md": community_page,
    "index/videos.md": video_page,
    "index/english.md": english_page,
    "index/knowledge-bank.md": knowledge_bank_page,
}


def pages(root: Path = ROOT) -> dict[str, str]:
    return {name: build(root) for name, build in PAGES.items()}


def write(root: Path = ROOT) -> dict[str, str]:
    built = pages(root)
    folder = root / "index"
    folder.mkdir(exist_ok=True)
    for stale in folder.glob("*.md"):
        if f"index/{stale.name}" not in built:
            stale.unlink()
    for name, text in built.items():
        (root / name).write_text(text, encoding="utf-8")
    return built


def validate(errors: list[str], root: Path = ROOT) -> None:
    built = pages(root)
    for name, text in built.items():
        path = root / name
        if not path.is_file() or path.read_text(encoding="utf-8") != text:
            errors.append(f"{name} is stale; rerun python3 scripts/validate_release.py --write-manifest")
    for path in (root / "index").glob("*") if (root / "index").is_dir() else []:
        if f"index/{path.name}" not in built:
            errors.append(f"index/{path.name}: not a generated index page")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="only report stale pages")
    args = parser.parse_args()
    if args.check:
        errors: list[str] = []
        validate(errors)
        print("\n".join(errors) or "index pages are current")
        raise SystemExit(1 if errors else 0)
    print(json.dumps({name: len(text.splitlines()) for name, text in write().items()}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
