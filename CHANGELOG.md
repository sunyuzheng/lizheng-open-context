# 更新记录

**Changelog** · 每次发布的准确数量、来源快照日期与文件哈希见 [`release-manifest.json`](release-manifest.json)。

## 2026-10-03 《真本事》课程文字稿、社区新帖、统一版权、完整目录

**课程文字稿。** 作者授权把超线性学院会员课程《真本事》23 节视频课下方的文字稿补入，供检索与问答：宣导片和第 01–21 课（第 11 课分上下），约 15 万字，在 [`corpus/course-lessons/`](corpus/course-lessons/)，按课程顺序的目录见 [`index/zhenbenshi-course.md`](index/zhenbenshi-course.md)。课程视频与课件仍只对会员开放；开放的是文字，不是课程本身。精确范围和每课文字的哈希见 [`config/member-course-policy.json`](config/member-course-policy.json)，维护流程见[课程文字稿说明](docs/member-course.md)。

**社区新帖。** 补入 3 篇新帖：[《建议每个人都用Opus 5.5做一下个人主页》](corpus/community-posts/20261001-personal-homepage-with-opus-5-5-36993423.md)、[《问问立正：直接问我讲过的内容，Founding Member不限次》](corpus/community-posts/20261002-ask-lizheng-37030030.md)、[《AI替你做出来以后，你还会什么？｜哥大客座课程回放》](corpus/community-posts/20261003-columbia-ai-learning-and-judgment-20261002-37077565.md)（立正讲「假学习的终结」，鸭哥讲求职与晋升；鸭哥的部分和同学提问归他们本人）。另外重新读取了 21 篇 9 月 30 日之后改动过的帖子：多数只是更新时间变了；4 篇正文或位置有变化，其中两篇活动回放从「论坛」移到「活动回放」，链接随之更新。帖子共 252 篇，Knowledge Bank 目录 169 篇不变，英文空间没有新文章。

**判断卡接上新内容。** [判断卡](context/decision-cards.json)是问答时按问题加载的推理导航：讲清一个判断在什么条件下成立、不能推出什么，并指向该读的原文。新增 8 张《真本事》判断卡，分别是职业选择（道天地将法）、个人价值公式、少数高价值工作、三种思维、财务自由与投资、手艺与坚持、赚钱这门手艺、沟通，每张都以课文为原文依据。旧卡接上两篇新帖：「交付结果与能力增长」接上哥大讲座，「先明确内容要放大什么」接上个人主页。现在共 16 张。会员视频字幕暂时只进检索，没有写进判断卡。

**统一版权。** 资料分五类，各用各的许可，总览见 [`LICENSE.md`](LICENSE.md)，细则见 [`LICENSE-CONTENT.md`](LICENSE-CONTENT.md)：

- 立正的文字：CC BY 4.0（不变）；
- 会员内容的文字：《真本事》课程文字稿和 215 份会员视频对话字幕，从「原权利保留、没写明能做什么」改为按新的[立正参考使用许可 1.0](LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md)开放：可以阅读、搜索、放进不收费的 AI 问答工具、短引用；不能整篇转载、收费使用或训练模型；嘉宾的话仍归嘉宾；
- 他人的作品：原作者保留（不变）；
- 目录数据：CC0 1.0（不变）；
- 程序和说明文档：MIT（不变）。原来的 `LICENSE` 是 MIT 全文，GitHub 因此把整个仓库显示为 MIT；现在 MIT 全文移到 [`LICENSES/MIT.txt`](LICENSES/MIT.txt)，`LICENSE.md` 是五类资料的总览。

新增 [`REUSE.toml`](REUSE.toml)（REUSE 3.3 规范），每个文件都标明许可和权利人；`release-manifest.json` 也记录每个文件的许可。发布检查会在许可标记、许可全文或 `REUSE.toml` 不一致时失败。

**完整目录。** 新增 [`INDEX.md`](INDEX.md) 和 `index/` 下五个目录页：《真本事》按课程顺序（对应书中章节和框架），帖子、视频、英文资料与 Knowledge Bank 按年份。目录由 `scripts/build_index.py` 从 `catalog/` 生成，过期时发布检查会失败。

**搜索。** `scripts/search.py` 新增 `--type course`，以及 `--license open`（只检索可以自由再利用的资料，适合收费产品）。

**更正。** 《真本事》文字稿的授权日期是 2026-10-03，之前误记为 10-04。

**English:** Adds the lesson texts of the members-only *真本事* course (23 lessons) for retrieval and Q&A; the course videos and slides stay members-only. Adds 3 new community posts (including the companion post for the Columbia guest lecture "The End of Fake Learning") and re-reads 21 posts edited since 2026-09-30, for 252 posts in total. Adds 8 reasoning cards grounded in the course lesson texts and links two new posts into existing cards, for 16 cards. The repository's rights are now one scheme of five kinds: Yuzheng Sun's writing (CC BY 4.0), text from members-only content (the new Lizheng Reference Use License 1.0: read, search, use in free AI tools, quote briefly; no full republication, paid use, or model training), other people's work (original rights retained), catalog data (CC0), and code and documentation (MIT). `LICENSE.md` replaces the MIT-only `LICENSE`, `REUSE.toml` maps every file, and `INDEX.md` plus `index/` index all material. Corrects the course authorization date to 2026-10-03.

## 2026-10-02 会员字幕补充

维护者授权把218份频道会员视频字幕用于开放检索与问答：新增215份，已有3份保留原文并补上会员标记。视频目录现为760条，字幕全文421份。原视频仍需YouTube频道会员观看；开放的是这一批字幕文字，不是会员视频文件，也不改变问问立正的Superlinear Founding额度。

每份资料保留原视频与时间码、会员状态核验日期、字幕来源和校对状态。嘉宾与说话人边界未确认的对话保留原权利与归属，不能用整篇证明立正本人的立场。精确范围和输入哈希见[`config/member-video-policy.json`](config/member-video-policy.json)，维护流程见[会员字幕说明](docs/member-transcripts.md)。

## 2026-09-30 更新 / Update

这次更新把近期提问、AI 学习、技术判断、职业价值与创作的材料补进同一个可回源的底座：

- **249 篇本人发布正文**：补入 9 篇，重新读取 32 篇已有正文。近期新增包括《假学习的终结》《为什么别人的好建议，到你这里就用不上？》《AI 接过工作之后，人生的问题才刚刚开始》、Jev 技术判断，以及周洁、Ashley 和切问 02 的对话伴读。
- **551 条视频目录、206 份主讲字幕**：刷新匿名公开视频清单，补入 9 条视频、移除 1 条已不在公开清单的目录；新增 Jev 主讲视频的作者发布中文字幕，保留具体时间链接。嘉宾／未复核视频继续只提供发现元数据。
- **当前知识库目录**：Knowledge Bank 有 169 篇公开文章元数据，36 篇本人正文；已迁往 Tools 或活动回放的文章仍可通过统一帖子库找到。原有 10 条审核评论、50 篇英文社区资料和 77 份英文 AI 译稿继续保留各自的历史快照。
- **Context 组织**：新增 [8 组判断卡](context/decision-cards.json)，关联原文、适用条件、不能推出的结论与材料间张力，可供产品按问题加载。它们是 AI 整理的推理导航，不能独立充当作者立场的证据。
- **问题导航**：新增[近期阅读地图](context/recent-reading-map.md)，从“真的学会了吗”“建议为何用不上”“新技术值不值得追”“自媒体要放大什么”等问题，找到相关原文。它是 AI 编写的检索导航，不是本人确认的新理论。

文章、视频与衍生整理仍分别记录来源、时间和归属。旧材料没有因本次增量更新而被重新标成最新观点。5 条新视频的具体发布日期尚未取得可靠元数据，目录如实留空；不借它们推断当前立场。准确数量、来源快照日期与文件哈希见 [release manifest](release-manifest.json)。

**English:** This update adds 9 published first-party posts, re-reads 32 existing posts, refreshes the public video discovery catalog, and adds the author-published Chinese captions for the solo Jev presentation. Publication dates, speakers, community contributors, AI translations and syntheses retain separate provenance. The new reading map is AI-authored navigation, not independent evidence of Yuzheng's views. Rebuild downstream indexes after updating.
