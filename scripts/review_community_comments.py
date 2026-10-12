#!/usr/bin/env python3
"""Sort Yuzheng's public comments into substance and small talk, and pin each decision.

scripts/export_public_corpus.py publishes a comment only when config/community-comment-review.json
holds a decision for its exact published text, in one of the include categories. This script asks a
model about every candidate without such a decision (a new comment, or one whose text changed), then
checks each one it would include a second time against a stricter reading, and writes the file;
decisions already made are kept. Needs AI_BUILDER_TOKEN.

  AI_BUILDER_TOKEN=... python3 scripts/review_community_comments.py
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import export_public_corpus as corpus  # noqa: E402

MODEL = "gpt-5"
URL = "https://space.ai-builders.com/backend/v1/chat/completions"
BATCH = 12
CATEGORIES = {**corpus.COMMENT_REVIEW_INCLUDE, **corpus.COMMENT_REVIEW_EXCLUDE}
PROMPT = (
    "你在整理立正（课代表立正，社区名 YZ｜立正）在超线性学院社区公开空间里写的评论，决定哪些收进他的公开资料库。"
    "资料库给人和 AI 读，用来了解他怎么想、怎么建议。每条输入有编号、帖子标题、帖子是不是他自己发的、评论正文；"
    "成员名字已换成[社区成员]，链接已换成[链接见原评论]。\n\n给每条评论选一个类别。\n收：\n"
    + "".join(f"- {key}：{text}\n" for key, text in corpus.COMMENT_REVIEW_INCLUDE.items())
    + "不收：\n"
    + "".join(f"- {key}：{text}\n" for key, text in corpus.COMMENT_REVIEW_EXCLUDE.items())
    + "\n规则：\n"
    "1. 尽量多收。只要评论里有一句结合帖子标题就能读懂的看法、建议、解释、经历或有用信息，即使夹着寒暄，也选对应的“收”类别。\n"
    "2. 帖子是成员公开发的提问或项目，他就此给的建议和看法照样收；只有谈到成员敏感私事的才选 private，即使里面有建议。\n"
    "3. 只是告诉对方去看某个视频、帖子或链接，没有说出内容的，选 admin。\n"
    '4. 只输出 JSON：{"decisions": {"编号": "类别"}}，每个编号都要有，类别只能是上面列出的英文词。'
)
# The first pass is told to include generously; this pass catches business and private matters it let in.
VERIFY_PROMPT = (
    "你在复核立正（YZ｜立正）社区评论的收录。下面的评论初判可以收进他的公开资料库。资料库给人和 AI 读，"
    "每条评论会单独出现，读者只看得到帖子标题和这条评论。逐条复核。\n"
    "keep：读者能从中知道立正的一个看法、建议、解释、经历或有用信息。\n改判：\n"
    "- admin：主要在办事务。买不买、何时买、优惠券、价格套餐、退款、哪门课包含什么、报名或权限、去哪个平台看、"
    "报 bug、改链接、搬帖、对某个帖子格式排版的修改意见、正在谈的合作或采购等内部业务。\n"
    "- private：谈到某位成员或他家人的私事，或者是和某位成员的争执、投诉、点名。\n"
    "- chat：闲聊、玩笑、个人打卡记录，或只是提问。\n"
    "- social：只是夸奖、感谢，没有说出具体看法。\n"
    "- context：离开原帖读不懂。\n"
    "拿不准、但确实有一句能单独读懂的看法时，选 keep。\n"
    '只输出 JSON：{"decisions": {"编号": "keep|admin|private|chat|social|context"}}，每个编号都要有。'
)


def candidates(cache: Path) -> list[dict]:
    records = json.loads((cache / "circle-author-comments.json").read_text(encoding="utf-8"))["records"]
    authoritative = {int(r["id"]): r for r in corpus.load_cache_directory(
        cache / "circle-author-comment-bodies", "authoritative Circle comment bodies")}
    spaces = {int(s["id"]): s for s in json.loads((cache / "circle-spaces.json").read_text(encoding="utf-8"))["records"]}
    posts = json.loads((cache / "circle-author-posts.json").read_text(encoding="utf-8"))["records"]
    own_titles = {int(p["id"]): str(p["title"]) for p in posts if p.get("author") == corpus.YUZHENG_NAME}
    return list(corpus.comment_candidates(records, authoritative, spaces, own_titles))


async def judge(client, token: str, prompt: str, allowed: set[str], batch: list[dict],
                semaphore: asyncio.Semaphore) -> dict[str, str]:
    items = [{"编号": item["id"], "帖子标题": item["parent_title"], "他自己的帖子": item["own_parent"],
              "评论": item["text"]} for item in batch]
    payload = {"model": MODEL, "reasoning_effort": "low", "response_format": {"type": "json_object"},
               "messages": [{"role": "system", "content": prompt},
                            {"role": "user", "content": json.dumps(items, ensure_ascii=False)}]}
    wanted = {item["id"] for item in batch}
    for attempt in range(5):
        async with semaphore:
            try:
                response = await client.post(URL, json=payload, headers={"Authorization": "Bearer " + token}, timeout=180)
                response.raise_for_status()
                got = json.loads(response.json()["choices"][0]["message"]["content"]).get("decisions") or {}
                if set(got) >= wanted and all(got[key] in allowed for key in wanted):
                    return {key: got[key] for key in wanted}
            except Exception:  # retried below; the run fails if a batch never succeeds
                pass
        await asyncio.sleep(2 * 2 ** attempt)
    raise SystemExit(f"Review failed for {sorted(wanted)[0]} and {len(wanted) - 1} others")


async def review(unjudged: list[dict], unchecked: list[dict], token: str) -> tuple[dict[str, str], set[str]]:
    """Categories for the unjudged comments, then a second look at every inclusion not yet checked."""
    import httpx

    semaphore = asyncio.Semaphore(4)
    async with httpx.AsyncClient() as client:
        async def run(prompt: str, allowed: set[str], items: list[dict]) -> dict[str, str]:
            batches = [items[i:i + BATCH] for i in range(0, len(items), BATCH)]
            results = await asyncio.gather(*(judge(client, token, prompt, allowed, batch, semaphore) for batch in batches))
            return {key: value for result in results for key, value in result.items()}

        first = await run(PROMPT, set(CATEGORIES), unjudged)
        included = unchecked + [item for item in unjudged if first[item["id"]] in corpus.COMMENT_REVIEW_INCLUDE]
        second = await run(VERIFY_PROMPT, {"keep", *corpus.COMMENT_REVIEW_EXCLUDE}, included)
    return {**first, **{key: value for key, value in second.items() if value != "keep"}}, set(second)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cache-dir", type=Path, default=ROOT / ".source-cache", help="Directory holding the sanitized Circle caches")
    args = parser.parse_args(argv)
    found = candidates(args.cache_dir.expanduser().resolve())
    path = corpus.COMMENT_REVIEW_PATH
    data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"schema_version": 1, "runs": [], "decisions": {}}
    decisions = data["decisions"]
    unjudged = [item for item in found if (decisions.get(item["id"]) or {}).get("text_sha256") != item["text_sha256"]]
    unchecked = [item for item in found if item not in unjudged and decisions[item["id"]]["category"]
                 in corpus.COMMENT_REVIEW_INCLUDE and not decisions[item["id"]].get("checked")]
    pending = unjudged + unchecked
    checked: set[str] = set()
    if pending:
        token = os.environ.get("AI_BUILDER_TOKEN", "")
        if not token:
            print("Set AI_BUILDER_TOKEN to review the new comments.", file=sys.stderr)
            return 1
        changed, checked = asyncio.run(review(unjudged, unchecked, token))
        for item in pending:
            key = item["id"]
            decisions[key] = {"category": changed.get(key, (decisions.get(key) or {}).get("category")),
                              "text_sha256": item["text_sha256"], **({"checked": True} if key in checked else {})}
        data["runs"].append({"reviewed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "model": MODEL,
                             "prompt_sha256": hashlib.sha256(PROMPT.encode("utf-8")).hexdigest(),
                             "check_prompt_sha256": hashlib.sha256(VERIFY_PROMPT.encode("utf-8")).hexdigest(),
                             "judged": len(unjudged), "checked": len(checked)})
    # Only comments the rules still admit keep a decision.
    current = {item["id"] for item in found}
    data["decisions"] = dict(sorted((key, value) for key, value in decisions.items() if key in current))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for item in found:
        category = decisions[item["id"]]["category"]
        counts[category] = counts.get(category, 0) + 1
    print(json.dumps({"candidates": len(found), "judged_now": len(unjudged), "checked_now": len(checked),
                      "categories": dict(sorted(counts.items())),
                      "included": sum(n for c, n in counts.items() if c in corpus.COMMENT_REVIEW_INCLUDE)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
