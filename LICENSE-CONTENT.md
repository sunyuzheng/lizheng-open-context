# 版权细则

**Rights details** · [English](#english)

[`LICENSE.md`](LICENSE.md) 是一页纸的总览；这里说明每一类具体包括什么，以及为什么这样分。各类资料的数量见 [`INDEX.md`](INDEX.md)。

## 1. 立正的文字 · CC BY 4.0

文件的 `license` 字段为 `CC-BY-4.0`，许可全文见 [`LICENSES/CC-BY-4.0.txt`](LICENSES/CC-BY-4.0.txt)。包括：

- **立正在超线性学院发表的帖子和评论**（`rights_scope: first-party`）。原帖在会员空间的，作者已明确授权开放自己的正文；文件保留原始可见性。评论只覆盖立正本人写的那段文字，不覆盖所在帖子、其他成员的回复和成员身份。
- **本人主讲视频的字幕**（`first-party`），必须在 `config/video-transcript-allowlist.txt` 里逐条列出。其中 3 份来自会员视频，此前已按本许可发布，保持不变。
- **源于立正的英文文章**（`first-party`），保留发布账号和翻译方式。
- **本人视频的英文 AI 译稿**（`first-party-derivative`）：AI 翻译，立正是原讲者；译稿不是立正的英文原话。
- **AI 整理**（`context/` 和 `examples/`）：作者标为 AI，发布者是立正。其中《真本事》框架参考和阅读地图来自作者自有的课程与书籍框架，由立正按本许可发布，不是出版社的版本。

署名时尽量写明：原作者或原讲者（立正 / Yuzheng Sun），实际撰写者或译者（例如 AI），标题，原始链接或本仓库，以及是否改动过。

作者身份和授权是两回事。AI 整理写作者 AI、发布者立正；这不表示 AI 是法律上的权利人，也不表示立正亲笔写过或逐句认可其中每句话。

## 2. 会员内容的文字 · 立正参考使用许可 1.0

文件的 `license` 字段为 `LicenseRef-Lizheng-Reference-Use-1.0`，许可全文见 [`LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md`](LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md)。包括：

- **《真本事》课程文字稿**（`publisher-authorized-course-text`）：2026-10-03 作者授权的 23 份，精确清单和每课文字的哈希见 [`config/member-course-policy.json`](config/member-course-policy.json)。课程视频、课件、作业和评论不在本仓库。
- **频道会员视频的字幕**（`publisher-authorized-transcript`）：2026-10-02 发布者授权的 215 份，清单见 [`config/member-video-policy.json`](config/member-video-policy.json)。原视频仍需频道会员观看。其中 45 份经人工核对只有立正一人讲述（清单见 [`config/member-solo-review.json`](config/member-solo-review.json)），可以当作他本人的表达；其余是对话，字幕没有逐段区分说话人：嘉宾和提问者的话归他们本人，本许可只在立正有权授权的范围内生效，整份字幕不能当作立正的立场。

这样分的原因：这些文字来自付费课程和会员视频。开放文字，是为了让人能搜索、查证、用 AI 问答和短引用；不开放的是整篇转载、收费使用、训练模型，以及做成能代替原课程或原视频的内容。

## 3. 他人的作品 · 原作者保留

文件的 `license` 字段为 `LicenseRef-Original-Rights-Retained`，说明见 [`LICENSES/LicenseRef-Original-Rights-Retained.md`](LICENSES/LicenseRef-Original-Rights-Retained.md)。这是一个标记，不是许可：

- **其他作者的英文文章**（`third-party-reference`）：维护者从超线性学院公开的英文空间选定收录，清单见 [`config/english-source-policy.json`](config/english-source-policy.json)。文件保留原作者、发布账号、原文链接和翻译或转载标记；原作者待确认的按未知处理。它们不属于立正的 CC BY 授权，也不代表立正的观点。

无论文件用哪种许可，下面这些都不在本仓库的任何许可之内：

- 嘉宾、提问者和其他说话人的话，除非另有书面记录；
- 第三方引文、链接页面、图片、嵌入内容、论文、书籍、商标和姓名；
- 《真本事：从会工作到会赚钱》图书的出版社版式、插图、扫描件和第三方授权素材；
- 超线性学院、合作者、社区成员、客户或其他权利人的内容，除非文件明确说明；
- 肖像、隐私、背书、商标和防止混淆等权利。

## 4. 目录数据 · CC0 1.0

`catalog/`、`config/`、`index/`、`INDEX.md` 和 `release-manifest.json`：在维护者有权的范围内放弃全部权利，见 [`LICENSES/CC0-1.0.txt`](LICENSES/CC0-1.0.txt)。这不影响来源平台的权利，也不保证事实准确。目录里出现的他人文章标题、作者和链接，只作为事实信息列出，原文仍归原作者。

## 5. 程序和说明文档 · MIT

`scripts/`、`tests/`、`evals/`、`docs/`，以及 `README.md`、`AGENTS.md`、`CONTRIBUTING.md`、`COMMUNITY-PROJECTS.md`、`CHANGELOG.md` 等说明文件，见 [`LICENSES/MIT.txt`](LICENSES/MIT.txt)。

## 机器怎么读

- 每个内容文件开头的 `license` 字段是 SPDX 标识符。
- [`REUSE.toml`](REUSE.toml) 按 [REUSE 3.3 规范](https://reuse.software/spec-3.3/) 列出全部文件的许可和权利人，由 `scripts/rights.py` 生成，可以用 `reuse lint` 检查。
- [`release-manifest.json`](release-manifest.json) 记录每个文件的哈希和许可，以及每种许可覆盖的文件数。
- 做收费产品时，`python3 scripts/search.py "你的问题" --license open` 只检索可以自由再利用的资料（CC BY 4.0 和目录数据）。

## 不冒充、不背书

许可允许你使用材料，不允许你声称立正、超线性学院、嘉宾或任何雇主认可你的作品。第三方做的 Agent 和 Skill 请清楚标明是独立开发的。

文件里的说法与本文不一致时，按更窄的那一种理解，并开 issue 说明。

---

## English

[`LICENSE.md`](LICENSE.md) is the one-page overview. This page explains what each kind contains and why. [`INDEX.md`](INDEX.md) has the counts.

**1. Yuzheng Sun's writing · CC BY 4.0.** His Superlinear Academy posts and comments (`first-party`; for posts from member spaces the author explicitly authorized opening his own text, and a comment license covers only his own words), transcripts of videos where he speaks alone (each listed in `config/video-transcript-allowlist.txt`; three come from member videos and keep their earlier CC BY license), English articles that originate with him, AI English translations of his videos (`first-party-derivative`; not his original English words), and the AI syntheses in `context/` and `examples/`, including the author-owned *真本事* framework reference and reading map (not the publisher's edition). Attribute the original author or speaker, the actual writer or translator (such as AI), the title, the source link, and any changes. Naming AI as a writer does not claim that AI holds legal rights, or that Yuzheng wrote or endorsed every sentence.

**2. Text from members-only content · Lizheng Reference Use License 1.0.** The 23 *真本事* lesson texts authorized on 2026-10-03 (`publisher-authorized-course-text`; list and hashes in `config/member-course-policy.json`; course videos, slides, assignments, and comments are not included) and the 215 member video transcripts authorized on 2026-10-02 (`publisher-authorized-transcript`; list in `config/member-video-policy.json`; the videos stay members-only). 45 of them were reviewed as Yuzheng speaking alone (`config/member-solo-review.json`) and count as his own speech. In the conversations, speakers are not separated turn by turn: guests and questioners keep the rights in their own words, the license applies only to the extent of Yuzheng Sun's rights, and a whole transcript cannot stand for his views. The text is open for search, verification, AI question answering, and short quotation, but not for republishing in full, charging for it, training models, or replacing the original course or videos.

**3. Other people's work · original rights retained.** English articles by other authors (`third-party-reference`), selected from Superlinear Academy's public English space and listed in `config/english-source-policy.json`, keep their original author, publishing account, source link, and translation or repost notice; they are not covered by Yuzheng's CC BY grant and do not represent his views. No license in this repository covers guests' and other speakers' words, third-party quotations, linked pages, images, embeds, papers, books, trademarks, or names; the publisher's layout, illustrations, scans, or third-party material of the *真本事* book; content owned by Superlinear Academy, co-authors, community members, customers, or other rights holders unless a file says so; or rights of publicity, privacy, endorsement, trademark, or passing off.

**4. Catalog data · CC0 1.0.** `catalog/`, `config/`, `index/`, `INDEX.md`, and `release-manifest.json`, to the extent the maintainer holds rights. Source-platform rights and factual accuracy are unaffected; titles, authors, and links of other people's articles are listed as facts.

**5. Code and documentation · MIT.** `scripts/`, `tests/`, `evals/`, `docs/`, and README, AGENTS, CONTRIBUTING, COMMUNITY-PROJECTS, CHANGELOG, and similar files.

**Machine-readable.** Each content file's `license` field is an SPDX identifier; [`REUSE.toml`](REUSE.toml) maps every file under the REUSE 3.3 specification (generated by `scripts/rights.py`, checkable with `reuse lint`); [`release-manifest.json`](release-manifest.json) records each file's hash and license. For paid products, `python3 scripts/search.py "query" --license open` searches only freely reusable material.

**No impersonation or endorsement.** The licenses let you use the material; they do not let you claim that Yuzheng Sun, Superlinear Academy, a guest, or an employer endorses your work. Label third-party agents and skills as independently developed. If a file-level statement differs from this page, follow the narrower one and open an issue.
