# 立正 · Open Context

一个给人和 AI 都能读的公开知识底座：把立正在 Superlinear 社区与视频频道发表的内容、明确署名的英文社区资料、AI 翻译与综合，以及《真本事》的课程文字稿与框架参考，整理成可检索、可引用、可继续开发的开放仓库。

它不是一个替你模仿“立正口吻”的人格提示词，也不宣称能替本人回答。它更像一套有来源、有时间、有边界的公共材料：你可以用它做搜索、问答、视频推荐、研究索引，或开发自己的立正 Skill / Agent。

**[目录](INDEX.md)** · **[版权与许可](LICENSE.md)** · **[更新记录](CHANGELOG.md)**

> **最近更新（2026-10-03）**：补入《真本事》23 节课的文字稿和 3 篇社区新帖（包括哥大客座课「假学习的终结」的回放）；统一全仓库的版权，五类资料各用各的许可；新增[完整目录](INDEX.md)。详见[更新记录](CHANGELOG.md)。

## 从这里继续

这个仓库保存的是可以检索、引用和继续开发的公开版本；仓库更新、衍生 Skill、使用反馈和新的问题会继续在 Superlinear 社区里讨论。

**[查看仓库更新与衍生 Skill 讨论 →](https://www.superlinear.academy/c/tools/lizheng-context?utm_source=github&utm_medium=referral&utm_campaign=lizheng_open_context)**

这条讨论发生在免费的 Superlinear Academy。20,000+ 位成员已经在社区分享 700+ 个公开项目；如果你有一个正在做的问题、原型或失败复盘，可以[免费加入并继续讨论](https://www.superlinear.academy/community?utm_source=github&utm_medium=referral&utm_campaign=lizheng_open_context)。

继续看公开内容：[YouTube](https://www.youtube.com/@kedaibiao) · [Bilibili](https://space.bilibili.com/491306902)

## 这里有什么

| 层 | 内容 | 开放方式 |
|---|---|---|
| `context/` | 当前核心主张、公开简介、Public Axioms V1、《真本事》完整框架、阅读地图与判断卡 | AI 撰写的整理与综合，CC BY 4.0；底层原作归立正，不能当作本人亲笔或原话 |
| `corpus/course-lessons/` | 《真本事》会员课程 23 节视频课的文字稿，[按课程顺序的目录](index/zhenbenshi-course.md) | [立正参考使用许可](LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md)：可阅读、搜索、问答与短引用；课程视频与课件仍需会员 |
| `corpus/community-posts/` | 立正在 Superlinear 各正常空间发布的 252 篇第一方帖子 | 全文、原帖链接、日期、空间与原始可见性，CC BY 4.0 |
| `corpus/community-comments/` | 从 2,519 条本人评论中筛出的 10 条独立、有检索价值的公开补充 | 只纳入本人公开帖子下的公开评论；保留原评论链接，移除成员提及名称、联系方式、正文链接与敏感语境 |
| `catalog/community-posts.jsonl` / `community-comments.jsonl` | 上述帖子与纳入评论的机器可读目录 | 可用于 RAG、索引和增量同步，CC0 |
| `catalog/knowledge-bank.jsonl` | Knowledge Bank 的 169 篇公开文章目录 | 所有作者只列公开元数据；立正的 36 篇全文指向统一社区语料 |
| `catalog/videos.jsonl` | 立正YouTube频道的760条视频目录，包括已授权的会员视频快照 | 标题、日期、链接、字幕状态、访问与权利范围，CC0 |
| `corpus/videos/` | 421份字幕：206份本人主讲，215份会员视频（其中45份经核对是立正一人主讲，170份是对话）；218份标明会员视频 | 带YouTube时间码；本人主讲 CC BY 4.0，会员视频按立正参考使用许可，对话里嘉宾的话归嘉宾 |
| `corpus/english-community/` / `catalog/english-community.jsonl` | 50 篇已发布英文文章：11 篇源于立正、37 篇鸭哥、1 篇 Carl Guo、1 篇原作者待确认 | 49 个新增正文文件，另 1 篇指向已有正文；源于立正的 CC BY 4.0，其他作者保留原权利；保留原作者、发布账号、原文链接与 Bot 翻译／转载标记 |
| `corpus/english-translations/` | 77 份本人单讲视频的英文 AI 译稿 | 独立标注 AI 生成、原视频发布日期与译稿生成日期；属于阅读辅助，不冒充英文原话；CC BY 4.0 |
| [`INDEX.md`](INDEX.md) / `index/` | 全部资料的目录：《真本事》按课程顺序，帖子、视频、英文资料与 Knowledge Bank 按年份 | 由 catalog 自动生成，CC0 |
| `docs/` | 数据边界、回答协议、建 agent 指南 | 可直接作为开发规范，MIT |
| `scripts/` | 导出、搜索、目录生成与发布前检查 | MIT |

准确数量见[目录](INDEX.md)，每个文件的哈希与许可见 [`release-manifest.json`](release-manifest.json)。

## 30 秒开始

无需向量数据库，先用仓库自带的本地搜索：

```bash
python3 scripts/search.py "如何找到适合写在简历里的项目" --top 8
python3 scripts/search.py "fake work" --type knowledge-bank
python3 scripts/search.py "如何建立信念" --type community
python3 scripts/search.py "项目复盘" --type comment
python3 scripts/search.py "做出代表作" --type video
python3 scripts/search.py "context infrastructure" --type english --json
python3 scripts/search.py "个人价值公式" --type course
python3 scripts/search.py "如何建立信念" --license open
```

`--license open` 只检索可以自由再利用的资料（CC BY 4.0 与目录数据），做收费产品时用它；会员内容的文字只能用在不收费的工具里，见[版权与许可](LICENSE.md)。

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

帖子层保留已发布作者正文，并用 2026-10-03 的单帖可见正文补入 3 篇新帖、重新读取 21 篇 9 月 30 日后改动过的帖子，共 252 篇；未重新读取的旧文件保留原快照日期，继续排除归档与测试空间。正常空间即使需要会员权限，作者也已明确授权开放自己的正文；每个文件保留原始可见性和来源日期，不能因进入仓库就自动视为当前立场。历史评论仍使用 2026-08-30 的已审核快照。

搜索接口只负责发现帖子；正文重新从每个帖子页面的可见 HTML 取得。Circle 的搜索索引有时会把附件中可检索的文字拼到 `body`，如果直接导出，可能把访谈附件或其他隐藏索引误当成文章正文。仓库明确不采用那部分内容。

评论层不追求“全量越多越好”。2,519 条本人评论先收窄到我自己已纳入仓库的公开帖子之下，并只考虑原本就公开可见的评论；之后再限定知识与项目讨论空间，并要求去掉成员提及名称、链接后至少仍有 80 个有效字符。欢迎语、活动与招聘、自我介绍、第三方长引文、会员语境、归档/测试空间，以及带私聊、健康、收入、移民、未成年人、内部运营、课程购买资格、折扣或退款等敏感个人和商业语境的内容不进入仓库。最终纳入 10 条；正文中的成员提及名称、联系方式和所有链接都会移除，只保留该条评论自己的原始链接。具体规则见 [`config/community-comment-policy.json`](config/community-comment-policy.json)。仓库不复制评论周围的其他成员内容。

## 明确不在这里的内容

- 微信、短信、邮件、私信、私人聊天与未公开会议；
- 本次英文来源清单以外的其他成员正文，以及成员评论、个人资料、邮箱、用户 ID 与参与数据；
- 未通过公开评论规则的短回复、欢迎语、运营回复与可能带有私密语境的本人评论；
- 学员、客户、合作方的非公开信息；
- 合同、财务、定价策略、内部运营、路线图和商业机密；
- 未发布选题、草稿、未授权课程课件、会员视频文件与私有媒体；已授权的218份会员字幕是有清单的例外；
- 凭证、token、Cookie、环境变量、日志和本地绝对路径；
- 《真本事》出版社版式、插图、扫描件，以及不是由立正拥有权利的第三方素材；
- 付费课程的视频、课件、作业与评论；《真本事》23 节课的文字稿是有清单的例外，框架整理也已以作者自有版本完整开放；
- 本次会员字幕授权清单之外的嘉宾访谈完整逐字稿。

视频字幕采用正向 allowlist：新视频不会因为“暂时没发现嘉宾”就自动获得全文许可，必须先明确加入 `config/video-transcript-allowlist.txt`；任何与嘉宾索引或人工排除表冲突的 ID 会让导出直接失败。

公开可见不等于可以无条件再授权。英文社区资料是本次明确收录的例外：他人原作保留原权利，不纳入立正的 CC BY 授权；归属不明的文章按未知处理。完整边界见 [`docs/privacy-and-rights.md`](docs/privacy-and-rights.md) 与 [`LICENSE-CONTENT.md`](LICENSE-CONTENT.md)。

## 更新与纠错

这个仓库是版本化快照，不是假装永远最新的“数字分身”。每次发布会记录来源日期、筛选规则、数量和哈希，改动见[更新记录](CHANGELOG.md)。发现错字、归属错误、断链或隐私问题，请开 issue；涉及移除请求时，请只描述目标文件和原因，不要在 issue 里再次粘贴敏感内容。

## 用完之后，带一个结果回来

如果这个仓库帮你做出了一个答案、搜索工具、立正 Skill / Agent 或其他作品，欢迎同时把它带回 GitHub 和社区：

1. 开源一个可检查的版本，说明它使用了哪些来源、怎样区分引用与推断；
2. 提交 pull request，把它加入 [`COMMUNITY-PROJECTS.md`](COMMUNITY-PROJECTS.md)；
3. 在 [Share Your Projects](https://www.superlinear.academy/c/share-your-projects?utm_source=github&utm_medium=referral&utm_campaign=lizheng_open_context) 发布可运行版本、失败原因或复盘，并把帖子链接带回[仓库更新讨论](https://www.superlinear.academy/c/tools/lizheng-context?utm_source=github&utm_medium=referral&utm_campaign=lizheng_open_context)。

通过基本的链接、来源与权利检查后，项目会出现在这个上游仓库的社区实现列表里，给后来的 GitHub 访客多一个发现你的入口。社区也能围绕真实结果继续讨论，而不只停在“我也在用 AI”。

## License

资料分五类，各用各的许可，一页纸的说明见 [`LICENSE.md`](LICENSE.md)，细则见 [`LICENSE-CONTENT.md`](LICENSE-CONTENT.md)：

- **立正的文字**：帖子、评论、本人主讲视频字幕、源于立正的英文文章、英文 AI 译稿和 AI 整理，[CC BY 4.0](LICENSES/CC-BY-4.0.txt)，注明作者和出处即可转载、改编、商用；
- **会员内容的文字**：《真本事》课程文字稿和会员视频对话字幕，[立正参考使用许可](LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md)，可以阅读、搜索、放进不收费的 AI 问答工具和短引用，不能整篇转载、收费使用或训练模型；
- **他人的作品**：其他作者的英文文章、嘉宾的话、第三方引文和商标，[原作者保留](LICENSES/LicenseRef-Original-Rights-Retained.md)；
- **目录数据**：[CC0 1.0](LICENSES/CC0-1.0.txt)；
- **程序和说明文档**：[MIT](LICENSES/MIT.txt)。
