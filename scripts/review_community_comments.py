#!/usr/bin/env python3
"""Sort Yuzheng's community comments into substance and small talk, and pin each decision.

scripts/export_public_corpus.py publishes a comment only when config/community-comment-review.json
holds a decision for its exact published text, in one of the include categories. This script asks a
model about every candidate without such a decision (a new comment, or one whose text changed), then
checks each one it would include a second time against a stricter reading, screens every inclusion
from a members-only space for anything about the member it answers, and writes the file; decisions
already made are kept. Needs AI_BUILDER_TOKEN when there is anything to review. With
--export it then regenerates only the comment corpus, its catalog and policy, leaving the rest of
the release alone.

  AI_BUILDER_TOKEN=... python3 scripts/review_community_comments.py --export
  python3 scripts/validate_release.py --write-manifest
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
    "你在整理立正（课代表立正，社区名 YZ｜立正）在超线性学院社区写的评论，决定哪些收进他的公开资料库。"
    "资料库给人和 AI 读，用来了解他怎么想、怎么建议。每条输入有编号、帖子标题、帖子是不是他自己发的、"
    "帖子标题会不会公开、评论正文；成员名字已换成[社区成员]，链接已换成[链接见原评论]。\n\n给每条评论选一个类别。\n收：\n"
    + "".join(f"- {key}：{text}\n" for key, text in corpus.COMMENT_REVIEW_INCLUDE.items())
    + "不收：\n"
    + "".join(f"- {key}：{text}\n" for key, text in corpus.COMMENT_REVIEW_EXCLUDE.items())
    + "\n规则：\n"
    "1. 尽量多收。只要评论里有一句结合帖子标题就能读懂的看法、建议、解释、经历或有用信息，即使夹着寒暄，也选对应的“收”类别。\n"
    "2. 帖子是成员公开发的提问或项目，他就此给的建议和看法照样收；只有谈到成员敏感私事的才选 private，即使里面有建议。\n"
    "3. 只是告诉对方去看某个视频、帖子或链接，没有说出内容的，选 admin。\n"
    "4. 帖子标题不公开的，是会员空间里别的成员的帖子：读者看不到标题，不看标题读不懂的选 context；"
    "只要谈到发帖成员本人的处境、经历、工作、项目或问题，就选 private，只谈普遍道理的照常收。\n"
    '5. 只输出 JSON：{"decisions": {"编号": "类别"}}，每个编号都要有，类别只能是上面列出的英文词。'
)
# The first pass is told to include generously; this pass catches business and private matters it let in.
VERIFY_PROMPT = (
    "你在复核立正（YZ｜立正）社区评论的收录。下面的评论初判可以收进他的公开资料库。资料库给人和 AI 读，"
    "每条评论会单独出现，读者只看得到帖子标题和这条评论；标了帖子标题不公开的，读者连标题也看不到。逐条复核。\n"
    "keep：读者能从中知道立正的一个看法、建议、解释、经历或有用信息。\n改判：\n"
    "- admin：主要在办事务。买不买、何时买、优惠券、价格套餐、退款、哪门课包含什么、报名或权限、去哪个平台看、"
    "报 bug、改链接、搬帖、对某个帖子格式排版的修改意见、正在谈的合作或采购等内部业务。\n"
    "- private：谈到某位成员或他家人的私事，或者是和某位成员的争执、投诉、点名；"
    "帖子标题不公开的，谈到发帖成员本人的处境、经历、工作、项目或问题也算。\n"
    "- chat：闲聊、玩笑、个人打卡记录，或只是提问。\n"
    "- social：只是夸奖、感谢，没有说出具体看法。\n"
    "- context：离开原帖读不懂。\n"
    "拿不准、但确实有一句能单独读懂的看法时，选 keep。\n"
    '只输出 JSON：{"decisions": {"编号": "keep|admin|private|chat|social|context"}}，每个编号都要有。'
)
# Members posted in a members-only space expecting only members to read it, so a reply there is
# published only when nothing in it tells a reader about the member it answers.
PRIVACY_PROMPT = (
    "下面是立正在会员空间里写的回复。会员发帖时只预期会员能看到；这些回复会公开，但不显示所在的帖子。"
    "帖子标题只是让你判断，不会公开。逐条判断。\n"
    "private：回复提到或暗示了它所回应的成员本人的情况，比如情绪、心理、健康、家庭、感情、经历、工作或职业变动、收入、"
    "住在哪里或搬去哪里、在哪家公司和公司内部的做法、项目的内容、个人计划或决心、正在面对的问题，"
    "哪怕只有半句、哪怕是夸奖或鼓励；或者写出了别人的名字、私下的对话。"
    "例如“回家以后可以多给家里人做做饭”“我认识几个朋友也是今年从温哥华回西雅图”“放下光环去过普通生活真的难”"
    "“我看了这个项目，如果让我来做……”“在某公司的人才体系里……”都选 private。\n"
    "keep：只谈普遍的道理和方法，或者立正自己的看法和经历，读者从中看不出那位成员本人的任何情况。\n"
    "拿不准时选 private。\n"
    '只输出 JSON：{"decisions": {"编号": "keep|private"}}，每个编号都要有。'
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
              "帖子标题公开": item["title_shown"], "评论": item["text"]} for item in batch]
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


async def review(unjudged: list[dict], unchecked: list[dict], unscreened: list[dict], current: dict[str, str],
                 token: str) -> tuple[dict[str, str], set[str], set[str]]:
    """Categories for the unjudged comments, a second look at every inclusion not yet checked, then the
    privacy screen for members-only inclusions. `current` holds the categories already decided."""
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
        decided = {**current, **first, **{key: value for key, value in second.items() if value != "keep"}}
        waiting = {item["id"] for item in unscreened}
        members = unscreened + [item for item in included if item["visibility"] == "members-only"
                                and item["id"] not in waiting and decided[item["id"]] in corpus.COMMENT_REVIEW_INCLUDE]
        members = [item for item in members if decided[item["id"]] in corpus.COMMENT_REVIEW_INCLUDE]
        third = await run(PRIVACY_PROMPT, {"keep", "private"}, members)
    changed = {key: value for key, value in decided.items() if key in {i["id"] for i in unjudged + unchecked + members}}
    changed.update({key: "private" for key, value in third.items() if value == "private"})
    return changed, set(second), set(third)


def export(cache: Path) -> dict:
    """Write the reviewed comments with their provenance; posts come from the committed post catalog."""
    import enrich_provenance as provenance

    posts = [json.loads(line) for line in (ROOT / "catalog/community-posts.jsonl").read_text(encoding="utf-8").splitlines()]
    author_posts = {int(row["id"].removeprefix("circle-")): {"title": row["title"]} for row in posts}
    comments = cache / "circle-author-comments.json"
    stats = corpus.export_community_comments(comments, cache / "circle-author-comment-bodies", cache / "circle-spaces.json",
                                             author_posts, json.loads(comments.read_text(encoding="utf-8"))["snapshot_at"])
    overrides = json.loads((ROOT / "config/attribution-overrides.json").read_text(encoding="utf-8"))
    by_id = {}
    for path in sorted((ROOT / "corpus/community-comments").glob("*.md")):
        meta, body = provenance.read_markdown(path)
        meta.update(provenance.default_provenance(meta, body))
        meta.update(overrides.get(meta["id"], {}))
        provenance.write_markdown(path, meta, body)
        by_id[meta["id"]] = meta
    catalog = ROOT / "catalog/community-comments.jsonl"
    rows = [json.loads(line) for line in catalog.read_text(encoding="utf-8").splitlines()]
    for row in rows:
        row.update({key: by_id[row["id"]][key] for key in provenance.PROVENANCE_KEYS if key in by_id[row["id"]]})
    catalog.write_text("".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    return stats


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cache-dir", type=Path, default=ROOT / ".source-cache", help="Directory holding the sanitized Circle caches")
    parser.add_argument("--export", action="store_true", help="Then regenerate the comment corpus, catalog and policy")
    args = parser.parse_args(argv)
    cache = args.cache_dir.expanduser().resolve()
    found = candidates(cache)
    path = corpus.COMMENT_REVIEW_PATH
    data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"schema_version": 1, "runs": [], "decisions": {}}
    decisions = data["decisions"]
    unjudged = [item for item in found if (decisions.get(item["id"]) or {}).get("text_sha256") != item["text_sha256"]]
    settled = [item for item in found if item not in unjudged]
    included = [item for item in settled if decisions[item["id"]]["category"] in corpus.COMMENT_REVIEW_INCLUDE]
    unchecked = [item for item in included if not decisions[item["id"]].get("checked")]
    unscreened = [item for item in included if item["visibility"] == "members-only" and not decisions[item["id"]].get("screened")]
    pending = unjudged + [item for item in included if item in unchecked or item in unscreened]
    checked: set[str] = set()
    screened: set[str] = set()
    if pending:
        token = os.environ.get("AI_BUILDER_TOKEN", "")
        if not token:
            print("Set AI_BUILDER_TOKEN to review the new comments.", file=sys.stderr)
            return 1
        current = {item["id"]: decisions[item["id"]]["category"] for item in settled}
        changed, checked, screened = asyncio.run(review(unjudged, unchecked, unscreened, current, token))
        for item in pending:
            key = item["id"]
            previous = decisions.get(key) if item not in unjudged else {}
            decisions[key] = {"category": changed.get(key, (previous or {}).get("category")), "text_sha256": item["text_sha256"]}
            if key in checked or (previous or {}).get("checked"):
                decisions[key]["checked"] = True
            if key in screened or (previous or {}).get("screened"):
                decisions[key]["screened"] = True
        data["runs"].append({"reviewed_at": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "model": MODEL,
                             "prompt_sha256": hashlib.sha256(PROMPT.encode("utf-8")).hexdigest(),
                             "check_prompt_sha256": hashlib.sha256(VERIFY_PROMPT.encode("utf-8")).hexdigest(),
                             "privacy_prompt_sha256": hashlib.sha256(PRIVACY_PROMPT.encode("utf-8")).hexdigest(),
                             "judged": len(unjudged), "checked": len(checked), "screened": len(screened)})
    # Only comments the rules still admit keep a decision.
    current = {item["id"] for item in found}
    data["decisions"] = dict(sorted((key, value) for key, value in decisions.items() if key in current))
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for item in found:
        category = decisions[item["id"]]["category"]
        counts[category] = counts.get(category, 0) + 1
    print(json.dumps({"candidates": len(found), "judged_now": len(unjudged), "checked_now": len(checked), "screened_now": len(screened),
                      "categories": dict(sorted(counts.items())),
                      "included": sum(n for c, n in counts.items() if c in corpus.COMMENT_REVIEW_INCLUDE)}, ensure_ascii=False))
    if args.export:
        print(json.dumps(export(cache), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
