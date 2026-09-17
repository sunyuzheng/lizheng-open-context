# 立正 · Open Context

一个给人和 AI 都能读的公开知识底座：把立正在 Superlinear 社区与视频频道发表的内容、明确署名的英文社区资料、AI 翻译与综合，以及《真本事》框架参考，整理成可检索、可引用、可继续开发的开放仓库。

它不是一个替你模仿“立正口吻”的人格提示词，也不宣称能替本人回答。它更像一套有来源、有时间、有边界的公共材料：你可以用它做搜索、问答、视频推荐、研究索引，或开发自己的立正 Skill / Agent。

## 2026-09-17 更新 / Update

这次补入近期文章与视频，并把英文内容及作者归属纳入统一检索：

- **文章与视频**：新增 17 篇本人账号文章、刷新 3 篇已有文章，涵盖 AI Native 组织、fake work、视频播客流程与 Intake Skill 等主题；文章全文从 223 篇增至 240 篇。视频目录新增 8 条、移出 1 条已非公开内容，共 543 条；本人主讲字幕从 201 份增至 205 份。
- **英文资料**：补齐 50 篇已发布英文社区文章（49 个新正文文件，1 篇复用已有正文），另加入 77 份本人单讲视频的英文 AI 译稿。译稿保留原视频、时间码与 AI 生成日期，不冒充本人原本说出的英文。
- **明确归属**：英文社区文章中，11 篇源于立正、37 篇来自鸭哥、1 篇来自 Carl Guo、1 篇原作者尚待确认。发布账号与原作者分别记录；他人的观点、引语、提问与经历不因出现在立正的账号或视频里就变成立正的表达。AI 撰写的 synthesis 明确标记为二次整理，不能单独证明本人立场。
- **已有 Skill / Agent 请重建索引**：拉取更新后，在每个检索片段中保留作者、发布者、生成方式、来源语境和证据权重。同一原作的翻译／转载按 source_family 去重；搜索相关性分数不等于可信度。字段与使用方式见[来源模型](docs/source-model.md)。

**English:** This update adds recent posts and videos, 50 published English community articles, and 77 AI-translated transcripts of included solo presentations. Original authors, publishing accounts, quoted speakers, AI translations, and AI-written syntheses are identified separately. Community contributions are not Yuzheng's statements or biography; translations are not his original English wording; syntheses are secondary interpretations. Rebuild existing indexes and preserve attribution on every retrieval chunk. See the [source model](docs/source-model.md) and [release manifest](release-manifest.json).

## 从这里继续

这个仓库保存的是可以检索、引用和继续开发的公开版本；仓库更新、衍生 Skill、使用反馈和新的问题会继续在 Superlinear 社区里讨论。

**[查看仓库更新与衍生 Skill 讨论 →](https://www.superlinear.academy/c/tools/lizheng-context?utm_source=github&utm_medium=referral&utm_campaign=lizheng_open_context)**

这条讨论发生在免费的 Superlinear Academy。20,000+ 位成员已经在社区分享 700+ 个公开项目；如果你有一个正在做的问题、原型或失败复盘，可以[免费加入并继续讨论](https://www.superlinear.academy/community?utm_source=github&utm_medium=referral&utm_campaign=lizheng_open_context)。

继续看公开内容：[YouTube](https://www.youtube.com/@kedaibiao) · [Bilibili](https://space.bilibili.com/491306902)

## 这里有什么

| 层 | 内容 | 开放方式 |
|---|---|---|
| `context/` | 当前核心主张、公开简介、Public Axioms V1、《真本事》完整框架与阅读地图 | AI 撰写的整理与综合；底层原作归立正，不能当作本人亲笔或原话 |
| `corpus/community-posts/` | 立正在 Superlinear 各正常空间发布的 240 篇第一方帖子 | 全文、原帖链接、日期、空间与原始可见性，CC BY 4.0 |
| `corpus/community-comments/` | 从 2,519 条本人评论中筛出的 10 条独立、有检索价值的公开补充 | 只纳入本人公开帖子下的公开评论；保留原评论链接，移除成员提及名称、联系方式、正文链接与敏感语境 |
| `catalog/community-posts.jsonl` / `community-comments.jsonl` | 上述帖子与纳入评论的机器可读目录 | 可用于 RAG、索引和增量同步 |
| `catalog/knowledge-bank.jsonl` | Knowledge Bank 的 171 篇公开文章目录 | 所有作者只列公开元数据；立正的 37 篇全文指向统一社区语料 |
| `catalog/videos.jsonl` | 立正 YouTube 频道的 543 条公开常规视频目录 | 标题、日期、链接、字幕状态、权利范围 |
| `corpus/videos/` | 通过 V1 正向说话人/权利 allowlist 的 205 份本人主讲字幕 | 带 YouTube 时间码；嘉宾、多人及未确认内容不复制全文 |
| `corpus/english-community/` / `catalog/english-community.jsonl` | 50 篇已发布英文文章：11 篇源于立正、37 篇鸭哥、1 篇 Carl Guo、1 篇原作者待确认 | 49 个新增正文文件，另 1 篇指向已有正文；保留原作者、发布账号、原文链接与 Bot 翻译／转载标记 |
| `corpus/english-translations/` | 77 份本人单讲视频的英文 AI 译稿 | 独立标注 AI 生成、原视频发布日期与译稿生成日期；属于阅读辅助，不冒充英文原话 |
| `docs/` | 数据边界、回答协议、建 agent 指南 | 可直接作为开发规范 |
| `scripts/` | 导出、搜索与发布前检查 | MIT |

准确数量和每个文件的哈希见 [`release-manifest.json`](release-manifest.json)。

## 30 秒开始

无需向量数据库，先用仓库自带的本地搜索：

```bash
python3 scripts/search.py "如何找到适合写在简历里的项目" --top 8
python3 scripts/search.py "fake work" --type knowledge-bank
python3 scripts/search.py "如何建立信念" --type community
python3 scripts/search.py "项目复盘" --type comment
python3 scripts/search.py "做出代表作" --type video
python3 scripts/search.py "context infrastructure" --type english --json
```

搜索结果会给出标题、日期、原始链接、命中片段，以及原作者、发布账号、生成方式和立场证据权重；视频结果尽可能给到可点击的时间码。相关性分数不代表事实置信度，同一原作的翻译／转载不重复算独立证据。

想先看这套材料如何真正回答社区提出的问题，可以读[“如何找到适合写在简历里的项目，并复盘它”示例](examples/resume-projects.md)。示例明确标出了直接来源与仓库综合，避免把新生成的方法冒充成原话。

如果要接入 LLM，建议先读：

1. [`docs/answering-contract.md`](docs/answering-contract.md)：回答时怎样区分原文、综合判断和推断；
2. [`docs/build-your-own-agent.md`](docs/build-your-own-agent.md)：最小可用的检索与推荐流程；
3. [`docs/source-model.md`](docs/source-model.md)：来源优先级、时间与字段；
4. [`AGENTS.md`](AGENTS.md)：可直接交给 coding agent 的行为说明。

## 已有参考实现

[`sunyuzheng/zhenbenshi-advisor`](https://github.com/sunyuzheng/zhenbenshi-advisor) 是一个已经公开、聚焦《真本事》职业与价值框架的轻量 skill。它适合直接参考“怎样把一本书做成建议流程”；本仓库不复制或替代它，而是提供更广的公共来源层，让开发者可以同时使用《真本事》、Knowledge Bank、YouTube 与当前 thesis，并保留出处和时间语义。

## 社区已经开始二创

社区成员 UB 已经基于这个仓库做出了 [`Superlinear Advisor / 超线性小助手`](https://github.com/wyuebei-cloud/superlinear-advisor)：一个用于 Hermes Agent 的来源可追溯问答 Skill。它不模仿“立正口吻”，而是区分直接来源、综合与推断，并把答案带回原文和视频时间码。开发过程和反馈可以在[社区讨论](https://www.superlinear.academy/c/tools/lizheng-context#comment_wrapper_113225533)里继续看。

这不是唯一或“官方指定”的实现。它证明的是：同一套开放 context 可以支持不同工具、交互方式和问题选择。更多衍生实现见 [`COMMUNITY-PROJECTS.md`](COMMUNITY-PROJECTS.md)。

## 这套材料主张什么

当前最核心的一句话是：

> **MAKE WHAT LASTS.**<br>
> **做点真东西。**

它和《真本事》之间的桥是：

> **学点真本事，做点真东西。**

`做出你的代表作` 是更长程的愿望：把逐渐挣来的理解与手艺，做成自己愿意长期负责、世界也愿意继续选择的作品。它不是一套成功保证，也不是要求每件工作都必须成为资产。

完整版本见 [`context/core-thesis.md`](context/core-thesis.md)。

## 为什么不直接发布一个“立正 Skill”

一个固定 skill 很快会把新的判断冻结成旧规则，也容易把“像他说话”误当成“理解他说过什么”。公开底座让不同的人可以做不同产品，同时保留三个更重要的能力：

- 回到原始出处，而不是只继承二手总结；
- 看见观点何时发表，以及后来是否变化；
- 明确区分本人原话、跨材料综合和开发者自己的推断。

仓库仍提供一套最小回答协议，但不垄断最终交互形式。

## Superlinear 帖子与评论怎样进入仓库

帖子层保留上次发布的作者正文，并用 2026-09-17 的单帖可见正文补入 17 篇新帖、刷新 3 篇已有文章，共 240 篇；继续排除归档与测试空间。正常空间即使需要会员权限，作者也已明确授权开放自己的正文；每个文件保留原始可见性和来源日期，不能因进入仓库就自动视为当前立场。历史评论仍使用 2026-08-30 的已审核快照。

搜索接口只负责发现帖子；正文重新从每个帖子页面的可见 HTML 取得。Circle 的搜索索引有时会把附件中可检索的文字拼到 `body`，如果直接导出，可能把访谈附件或其他隐藏索引误当成文章正文。仓库明确不采用那部分内容。

评论层不追求“全量越多越好”。2,519 条本人评论先收窄到我自己已纳入仓库的公开帖子之下，并只考虑原本就公开可见的评论；之后再限定知识与项目讨论空间，并要求去掉成员提及名称、链接后至少仍有 80 个有效字符。欢迎语、活动与招聘、自我介绍、第三方长引文、会员语境、归档/测试空间，以及带私聊、健康、收入、移民、未成年人、内部运营、课程购买资格、折扣或退款等敏感个人和商业语境的内容不进入仓库。最终纳入 10 条；正文中的成员提及名称、联系方式和所有链接都会移除，只保留该条评论自己的原始链接。具体规则见 [`config/community-comment-policy.json`](config/community-comment-policy.json)。仓库不复制评论周围的其他成员内容。

## 明确不在这里的内容

- 微信、短信、邮件、私信、私人聊天与未公开会议；
- 本次英文来源清单以外的其他成员正文，以及成员评论、个人资料、邮箱、用户 ID 与参与数据；
- 未通过公开评论规则的短回复、欢迎语、运营回复与可能带有私密语境的本人评论；
- 学员、客户、合作方的非公开信息；
- 合同、财务、定价策略、内部运营、路线图和商业机密；
- 未发布选题、草稿、未授权课程课件、会员视频与私有媒体；
- 凭证、token、Cookie、环境变量、日志和本地绝对路径；
- 《真本事》出版社版式、插图、扫描件，以及不是由立正拥有权利的第三方素材；
- 付费课程的原始视频与逐字转录（框架内容已经以作者自有版本完整开放）；
- 已知嘉宾访谈的完整逐字稿。

视频字幕采用正向 allowlist：新视频不会因为“暂时没发现嘉宾”就自动获得全文许可，必须先明确加入 `config/video-transcript-allowlist.txt`；任何与嘉宾索引或人工排除表冲突的 ID 会让导出直接失败。

公开可见不等于可以无条件再授权。英文社区资料是本次明确收录的例外：他人原作保留原权利，不纳入立正的 CC BY 授权；归属不明的文章按未知处理。完整边界见 [`docs/privacy-and-rights.md`](docs/privacy-and-rights.md) 与 [`LICENSE-CONTENT.md`](LICENSE-CONTENT.md)。

## 更新与纠错

这个仓库是版本化快照，不是假装永远最新的“数字分身”。每次发布会记录来源日期、筛选规则、数量和哈希。发现错字、归属错误、断链或隐私问题，请开 issue；涉及移除请求时，请只描述目标文件和原因，不要在 issue 里再次粘贴敏感内容。

## 用完之后，带一个结果回来

如果这个仓库帮你做出了一个答案、搜索工具、立正 Skill / Agent 或其他作品，欢迎同时把它带回 GitHub 和社区：

1. 开源一个可检查的版本，说明它使用了哪些来源、怎样区分引用与推断；
2. 提交 pull request，把它加入 [`COMMUNITY-PROJECTS.md`](COMMUNITY-PROJECTS.md)；
3. 在 [Share Your Projects](https://www.superlinear.academy/c/share-your-projects?utm_source=github&utm_medium=referral&utm_campaign=lizheng_open_context) 发布可运行版本、失败原因或复盘，并把帖子链接带回[仓库更新讨论](https://www.superlinear.academy/c/tools/lizheng-context?utm_source=github&utm_medium=referral&utm_campaign=lizheng_open_context)。

通过基本的链接、来源与权利检查后，项目会出现在这个上游仓库的社区实现列表里，给后来的 GitHub 访客多一个发现你的入口。社区也能围绕真实结果继续讨论，而不只停在“我也在用 AI”。

## License

- 程序与开发文档：MIT，见 [`LICENSE`](LICENSE)。
- 标注为 CC BY 4.0 的作者授权内容与派生整理：保留实际作者和 AI 生成标记，见 [`LICENSE-CONTENT.md`](LICENSE-CONTENT.md)。
- 公开元数据：CC0 1.0。
- 第三方引文、链接、姓名、商标和嘉宾内容不因进入本仓库而被重新授权。
