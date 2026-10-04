#!/usr/bin/env python3
"""Import the exact maintainer-authorized 《真本事》 course lesson texts; default dry-run."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path

from export_public_corpus import html_to_markdown, sanitize_first_party_text
from enrich_provenance import write_markdown

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config/member-course-policy.json"
AUTHORIZATION = "maintainer-request-2026-10-04-zhenbenshi-course-text"
SPACE_ID = 1858870
COURSE_URL = "https://www.superlinear.academy/c/work-wealth"
CATALOG = "catalog/course-lessons.jsonl"


def lesson_url(section_id: int, lesson_id: int) -> str:
    return f"{COURSE_URL}/sections/{section_id}/lessons/{lesson_id}"


def load_policy(path: Path = POLICY) -> dict:
    policy = json.loads(path.read_text())
    if policy.get("authorization") != AUTHORIZATION:
        raise ValueError("Course text policy lacks the explicit inclusion authorization")
    course = policy.get("course") or {}
    if course.get("space_id") != SPACE_ID or course.get("url") != COURSE_URL or policy.get("membership_url") != COURSE_URL:
        raise ValueError("Expected the 《真本事》 course space")
    ids = [row["lesson_id"] for row in policy["records"]]
    if len(ids) != 23 or len(ids) != len(set(ids)):
        raise ValueError("Expected the exact 23 authorized lesson texts")
    return policy


def prepare(export: Path, policy: dict, root: Path = ROOT) -> tuple[list[tuple[Path, dict, str]], list[dict]]:
    """Checks every lesson against the reviewed policy and returns the files and catalog rows to write."""
    records = {row["id"]: row for row in json.loads(export.expanduser().read_text())["records"]}
    writes, rows = [], []
    for approved in policy["records"]:
        identity = approved["lesson_id"]
        lesson = records.get(identity)
        if not lesson:
            raise ValueError(f"{identity}: authorized lesson missing from the export")
        body_html = lesson.get("body_html") or ""
        if lesson.get("space_id") != SPACE_ID or lesson.get("status") != "published":
            raise ValueError(f"{identity}: not a published lesson of the course")
        if hashlib.sha256(body_html.encode("utf-8")).hexdigest() != approved["text_sha256"]:
            raise ValueError(f"{identity}: lesson text differs from the authorized snapshot")
        if lesson.get("name") != approved["title"] or lesson.get("section_id") != approved["section_id"] or lesson.get("created_at") != approved["published_at"]:
            raise ValueError(f"{identity}: lesson metadata differs from the reviewed policy")
        url = lesson_url(approved["section_id"], identity)
        text = sanitize_first_party_text(html_to_markdown(body_html, redact_member_links=True))
        if len(text) < 500:
            raise ValueError(f"{identity}: lesson text is unexpectedly short")
        meta = dict(
            id=f"circle-lesson-{identity}", title=approved["title"], author="Yuzheng Sun", publisher="Yuzheng Sun",
            original_author="Yuzheng Sun", source_type="course-lesson", source_url=url,
            published_at=approved["published_at"], snapshot_at=policy["snapshot_at"], content_status="current",
            rights_scope="publisher-authorized-course-text", license="LicenseRef-Original-Rights-Retained",
            review_status="maintainer-authorized", content_origin="yuzheng-published-text",
            generation_method="not-established", evidence_role="published-source",
            yuzheng_stance_weight="direct-with-quotation-boundaries", source_family=url, language="zh",
            source_context="Members-only lesson text from the 《真本事》 course on Superlinear Academy; the author authorized open retrieval of this text. Course videos and slides remain members-only.",
            attribution_note="立正《真本事》会员课程的文字稿，由作者发布在超线性学院课程空间；作者授权开放文字供检索与问答，课程视频与课件仍只对会员开放。引用、案例与他人观点归原作者，不能直接算作立正立场。",
            source_visibility="members-only", text_access="public", membership_platform="superlinear",
            membership_url=policy["membership_url"], inclusion_authorization=policy["authorization"],
        )
        body = (f"# {approved['title']}\n\n> **会员课程** · 《真本事》课程的文字稿，作者授权开放检索与问答；"
                f"[课程页面]({url})与课程视频需超线性学院会员。\n\n{text}\n")
        target = root / "corpus/course-lessons" / f"{approved['published_at'][:10].replace('-', '')}-{identity}.md"
        writes.append((target, meta, body))
        row = {key: value for key, value in meta.items() if key != "source_url"}
        rows.append({**row, "url": url, "corpus_path": str(target.relative_to(root)), "full_text_included": True,
                     "course": "真本事", "lesson_id": identity, "section_id": approved["section_id"]})
    rows.sort(key=lambda row: (row["published_at"], row["lesson_id"]))
    return writes, rows


def apply_prepared(root: Path, writes: list, rows: list) -> None:
    folder = root / "corpus/course-lessons"
    folder.mkdir(parents=True, exist_ok=True)
    keep = {target.name for target, _, _ in writes}
    for stale in folder.glob("*.md"):
        if stale.name not in keep:
            stale.unlink()
    for target, meta, body in writes:
        write_markdown(target, meta, body)
    (root / CATALOG).write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--export", type=Path, required=True, help="Circle course_lessons export for space 1858870")
    parser.add_argument("--apply", action="store_true", help="Write local corpus only; never push or deploy")
    args = parser.parse_args()
    writes, rows = prepare(args.export, load_policy())
    if args.apply:
        apply_prepared(ROOT, writes, rows)
    chars = sum(len(body) for _, _, body in writes)
    print(json.dumps({"mode": "local-apply" if args.apply else "dry-run", "lessons": len(writes), "characters": chars}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
