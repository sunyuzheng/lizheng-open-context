# 更新记录

## 2026-10-11 297期对谈按声纹标出说话人

297期公开对谈按声纹比对标出说话人：立正49,271句、嘉宾100,889句，拿不准的句子保持待核；嘉宾只在节目恰好列了一位、且只找到一个其他声音时标名字。每句另有言语行为，立正的提问、介绍、回应、玩笑和转述不算他的观点。检验：人工核对过的47句里，立正的15句全部认出，嘉宾的话没有一句被标成立正；29句嘉宾自我介绍、18句对立正说话的句子和8期立正没出声的节目里也没有。声音和目录记录对不上、或认不出立正的38期对谈先不标，等立正听过样本确认。

## 2026-10-11 节目里的嘉宾介绍

113位嘉宾有了出自节目的介绍（`introductions`，共154条）：每条写明是哪期节目、在字幕的哪几句、几秒开始，并保存原话；原话必须与公开字幕逐字一致，由校验核对。介绍由AI按原话撰写，只用原话说出的事实，反映节目当时的身份。没有节目介绍的嘉宾，网站把目录里的职位与公司作为“简介”显示，不再称为节目中的介绍。

## 2026-10-11 对谈的说话人归属与切分

对谈单元可以由声纹比对确定说话人（`audio-voice-match`），方法、阈值、检验结果和每期的hash记录在`config/audio-speaker-policy.json`，绑定在对谈收录清单里；原文或标注改动而没有重做比对时校验失败。`scripts/voice_attribution.py`在本机完成嵌入、标注、言语行为和写入，立正的声纹特征不进入仓库。对谈切成两种片段：完整字幕片段按时间切分、不归给任何人；说话人片段按说话人和言语行为汇集，只有陈述能代表说话人的观点。对谈片段和视频字幕片段每行只写时间，链接由片段地址和秒数生成。

## 2026-10-11 组合与成员

7个多人组合写明了成员（`members`），成员自己有人物页时直接关联：组合的节目自动列入成员页，名字表里成员名指向本人，「Mandy」不再同时指向本人和「Leo & Mandy」两条记录。组合名字里列出的人必须都是声明过的成员，校验检查两边一致。

## 2026-10-11 重复事实自动生成

视频目录里的嘉宾名字、嘉宾节目标题和对谈原稿位置改由人物目录与对谈授权清单自动推出：65期过期或缺失的嘉宾名字、4个旧标题随之更正，331期有结构化原稿的节目不再被记为只有目录。参与关系按节目日期编号。新增名字表`catalog/guest-names.json`，收录括号前的本名、括号里的称呼、组合成员与主持人名字，网站和问问立正按同一张表找人。目录条目在检索中标为Structured层，不再算作原文；有嘉宾的视频改按人物目录做权利检查。

## 2026-10-11 发表来源与资料维护

明确已发表原文与媒体是主要事实依据，Open Context统一维护可回源的文本和结构化记录。架构区分采集、资料校准、提炼与调用，在线产品使用固定快照。README的动态资料数量统一指向数据生成的目录与manifest，移除发布脚本对README重复计数的要求。

## 2026-10-11 资料版本与消费者验收

资料架构明确消费者的固定版本合同：网站目录快照与版本记录一起生成并在构建时校验；问答语料先完成候选校验再替换。最终验收按各处实际部署的release核对来源、目录和索引。

**Changelog** · 每次发布的准确数量、来源快照日期与文件哈希见 [`release-manifest.json`](release-manifest.json)。

## 2026-10-11 本人材料与对谈索引

人物目录按明确来源维护参与关系，补齐个人与多人组合的记录及同名检索入口。视频导出直接读取这份共享目录，并保留已授权的对谈快照。249份单人主讲文字稿与对谈分开列出；旧视频表的发言归属与结构化原稿统一，一份误列为单人主讲的AI译稿退出公开译稿目录。原句和时间码保留。问问立正按用途组织材料：普通回答使用立正的直接来源，找资料检索全库；发言归属检查覆盖正文、推荐理由及后续问题。

## 2026-10-11 对谈原稿与统一嘉宾目录

新增339份结构化公开对谈原稿、248,599条字幕单元，保留原文字、时间码、来源版本与发言归属。原稿可直接检索；摘要、阅读地图与判断卡作为独立提炼层回指原文。文字经过AI校对和改动复核，具体质量与待核数量保存在每份原稿中。

嘉宾资料并入`catalog/guests.json`：人物和别名、节目、参与关系、稳定ID与旧页面链接统一维护。`catalog/guest-articles.json`关联23篇已发表的伴读文章。网站从固定release生成嘉宾页，问问立正从同一release构建检索；来源字段贯穿回答、历史与分享。目录合并后，同一个节目的标题、日期和链接由一条记录提供。

现有218份会员字幕授权快照、6份指定公开对话及132段本人发言摘录继续保留。结构化公开对谈按`config/public-dialogue-policy.json`的精确ID与hash收录。原文、提炼和目录的职责见[资料架构](docs/conversation-architecture.md)。

## 2026-10-07 视频资料更新

新增《AI时代，为什么必须要做“个人网站”？》的公开原文；更新《如何炒作一个AI概念？以Jev为例…》的字幕。问问立正已同步该版本。

## 2026-10-04 塑造价值观的对话：问道、赵智沉、王路、Leon

**为什么做。** 立正说，问道（格桑泽仁）和他跟王路、赵智沉、Leon 的对话，是他价值观塑造的重要组成部分，要求把它们找出来认真分析，整理成底层素材并提炼用好。

**十二场对话的字幕。** 其中六场是会员视频，字幕原本就在仓库里：问道、赵智沉两场、Leon 的《如何赚第一桶金，和超越中产阶级》和与露露谈教育两期。这次按同样的条件补入六场公开对话的字幕全文：2021 年的《Influence Without Authority》《打工人如何获得财富自由？》，2023 年 Multiple-Fire 系列三期，以及 2026 年和王路聊《金刚经》。都在 [`corpus/videos/`](corpus/videos/)，按[立正参考使用许可](LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md)开放，嘉宾的话归嘉宾本人。精确范围和字幕哈希见 [`config/values-conversations-policy.json`](config/values-conversations-policy.json)，导入脚本是 `scripts/import_values_conversations.py`。视频目录里的「@charisma-Leo」系列是另一位嘉宾，不在其中。

**他本人说的话。** 字幕不标说话人，整篇不能当作立正的立场。这次逐场通读，只摘出能从上下文确认是他说的段落，共 132 段，放在 [`corpus/conversation-excerpts/`](corpus/conversation-excerpts/)，每段带时间码和一句 AI 写的背景；嘉宾的话、说话人不确定的段落和涉及第三方私事的内容都不摘。引文与字幕逐字一致，`validate_release.py` 会逐段核对引文和时间点，对不上就不能发布。会员视频里的摘录按立正参考使用许可，公开视频里的按 CC BY 4.0。按对话的目录见 [`index/values-conversations.md`](index/values-conversations.md)。

**说明写在哪里。** 12 份对话字幕开头都加了一段说明：嘉宾是谁，字幕不标说话人，嘉宾的话归嘉宾本人、不代表立正的观点，他本人的话摘在哪里。README 新增「塑造价值观的对话」一节；嘉宾希望修改或撤下自己的部分，可以在 GitHub 开 issue，维护者会撤下并在这里说明。

**阅读地图和判断卡。** 新增[塑造价值观的对话：阅读地图](context/values-conversations-map.md)，按时间和主题梳理他在每场对话里带进去了什么、接住了什么、后来写进了哪些帖子和课。新增 8 张判断卡：科学的边界、一体与公平、「自」和「我」、自己定义意义、方法比答案重要、少证明自己、降伏其心、教孩子，依据是这些摘录和他的帖子；另给良质、指标与产出、沟通、个人品牌 4 张旧卡接上了对话里的原话。判断卡共 29 张。

**English:** At Yuzheng's request, the twelve conversations he names as formative for his values (问道 with 格桑泽仁, two with 赵智沉, one with 王路, eight with Leon) are now source material. Six were member videos already included; the transcripts of the six public ones are added under the same terms (Lizheng Reference Use License; guests keep the rights in their own words). His own turns were reviewed speaker by speaker and excerpted (132 passages in `corpus/conversation-excerpts/`); every quotation must match its transcript verbatim at the stated time, which the release validator checks. A reading map and eight new reasoning cards build on them; there are now 29 cards.

## 2026-10-04 《Growth Data Analytics Playbook》和Statsig博客文章的中文版、增长与实验判断卡

**书的中文版。** 立正和Mengying Li、Joe Kumar合著的《Growth Data Analytics Playbook》（Statsig Press，2025）有了免费中文版：AI按立正的中文习惯整本改写，保留全部框架、案例和练习，几道练习补了计算过程或注意事项。中文版在[lizheng.ai](https://www.lizheng.ai/book/growth-data-analytics-playbook)每章一页免费读，也可以下载EPUB和PDF。这里收文字，共12份（关于这本书、10章和结语），在 [`corpus/book-chapters/`](corpus/book-chapters/)，目录见 [`index/growth-data-analytics-playbook-zh.md`](index/growth-data-analytics-playbook-zh.md)。

**Statsig博客文章的中文版。** 立正2024到2025年在Statsig官方博客发表的19篇文章，同样由AI按他的中文习惯完整改写：论证、例子、数字和结论都保留，没有加原文没有的事实或经历；2篇合著文章写明了合著者，观点属于两位作者。在 [`corpus/blog-posts/`](corpus/blog-posts/)，目录见 [`index/statsig-blog.md`](index/statsig-blog.md)。

两组都按[立正参考使用许可](LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md)开放；证据权重是「核对英文原文」（`verify-original`），不能当作立正亲笔的中文。只收文字，图只保留图注。精确范围和每份文字的哈希见 [`config/chinese-editions-policy.json`](config/chinese-editions-policy.json)，导入脚本是 `scripts/import_chinese_editions.py`。

**增长与实验的判断卡和阅读地图。** 新增4张判断卡，都以立正本人主讲的视频为依据：看增长先拆账（成熟产品的活跃变化大多来自留存）、留存先定义清楚（哪群人、隔多久、做了什么才算回来）、实验的价值来自意外（大多数想法会失败，新功能默认都要测）、先把漏斗做大再抠转化率。判断卡共21张。新增[增长数据分析与实验阅读地图](context/growth-analytics-reading-map.md)，按问题把书的章节、博客文章和「课代表数据大师课」等视频连起来。

## 2026-10-03 《真本事》课程文字稿、社区新帖、统一版权、完整目录

**课程文字稿。** 作者授权把超线性学院会员课程《真本事》23 节视频课下方的文字稿补入，供检索与问答：宣导片和第 01–21 课（第 11 课分上下），约 15 万字，在 [`corpus/course-lessons/`](corpus/course-lessons/)，按课程顺序的目录见 [`index/zhenbenshi-course.md`](index/zhenbenshi-course.md)。课程视频与课件仍只对会员开放；开放的是文字，不是课程本身。精确范围和每课文字的哈希见 [`config/member-course-policy.json`](config/member-course-policy.json)，维护流程见[课程文字稿说明](docs/member-course.md)。

**社区新帖。** 补入 3 篇新帖：[《建议每个人都用Opus 5.5做一下个人主页》](corpus/community-posts/20261001-personal-homepage-with-opus-5-5-36993423.md)、[《问问立正：直接问我讲过的内容，Founding Member不限次》](corpus/community-posts/20261002-ask-lizheng-37030030.md)、[《AI替你做出来以后，你还会什么？｜哥大客座课程回放》](corpus/community-posts/20261003-columbia-ai-learning-and-judgment-20261002-37077565.md)（立正讲「假学习的终结」，鸭哥讲求职与晋升；鸭哥的部分和同学提问归他们本人）。另外重新读取了 21 篇 9 月 30 日之后改动过的帖子：多数只是更新时间变了；4 篇正文或位置有变化，其中两篇活动回放从「论坛」移到「活动回放」，链接随之更新。帖子共 252 篇，Knowledge Bank 目录 169 篇不变，英文空间没有新文章。

**判断卡接上新内容。** [判断卡](context/decision-cards.json)是问答时按问题加载的推理导航：讲清一个判断在什么条件下成立、不能推出什么，并指向该读的原文。新增 8 张《真本事》判断卡，分别是职业选择（道天地将法）、个人价值公式、少数高价值工作、三种思维、财务自由与投资、手艺与坚持、赚钱这门手艺、沟通，每张都以课文为原文依据。旧卡接上两篇新帖：「交付结果与能力增长」接上哥大讲座，「先明确内容要放大什么」接上个人主页。现在共 16 张。

**会员视频里你自己讲的部分。** 215 份会员视频字幕原先都按多人节目处理，不能当作立正的观点。逐份核对后，45 份只有立正一人讲述（比如 Marketplace 系列、高价值工作、80 分陷阱、Framing、不可规模化的事），改为本人主讲，问问立正可以引用为他的观点；会员身份和许可不变。清单见 [`config/member-solo-review.json`](config/member-solo-review.json)。其中相关的接进了判断卡，另新增一张「坏消息要说实话，也要让人接得住」（来自 Marketplace 系列），判断卡共 17 张。

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

**English:** Adds the lesson texts of the members-only *真本事* course (23 lessons) for retrieval and Q&A; the course videos and slides stay members-only. Adds 3 new community posts (including the companion post for the Columbia guest lecture "The End of Fake Learning") and re-reads 21 posts edited since 2026-09-30, for 252 posts in total. Adds 8 reasoning cards grounded in the course lesson texts and links two new posts into existing cards. Reviews the member video transcripts: 45 in which Yuzheng speaks alone now count as his own speech (same access and license) and feed the cards, plus one new card from the Marketplace series, for 17 cards. The repository's rights are now one scheme of five kinds: Yuzheng Sun's writing (CC BY 4.0), text from members-only content (the new Lizheng Reference Use License 1.0: read, search, use in free AI tools, quote briefly; no full republication, paid use, or model training), other people's work (original rights retained), catalog data (CC0), and code and documentation (MIT). `LICENSE.md` replaces the MIT-only `LICENSE`, `REUSE.toml` maps every file, and `INDEX.md` plus `index/` index all material. Corrects the course authorization date to 2026-10-03.

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
