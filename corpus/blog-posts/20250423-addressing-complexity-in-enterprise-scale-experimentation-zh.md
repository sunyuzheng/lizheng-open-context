---
id: "statsig-blog-addressing-complexity-in-enterprise-scale-experimentation-zh"
title: "实验跑到成千上万个时，怎样应对复杂度"
original_title: "Addressing complexity in enterprise-scale experimentation"
author: "AI"
publisher: "Yuzheng Sun"
snapshot_at: "2026-10-04"
generated_at: "2026-10-04"
content_status: "current"
rights_scope: "publisher-authorized-adaptation"
license: "LicenseRef-Lizheng-Reference-Use-1.0"
review_status: "maintainer-authorized"
content_origin: "ai-translation"
generation_method: "ai-translation"
evidence_role: "translation"
yuzheng_stance_weight: "verify-original"
language: "zh"
original_language: "en"
source_visibility: "public"
text_access: "public"
third_party_exclusions: true
inclusion_authorization: "maintainer-request-2026-10-04-chinese-editions"
original_author: "Yuzheng Sun"
source_type: "blog-post"
source_url: "https://www.statsig.com/blog/addressing-complexity-in-enterprise-scale-experimentation"
original_source_url: "https://www.statsig.com/blog/addressing-complexity-in-enterprise-scale-experimentation"
source_family: "https://www.statsig.com/blog/addressing-complexity-in-enterprise-scale-experimentation"
published_at: "2025-04-23"
original_published_at: "2025-04-23"
translation_publication_status: "repository-reading-aid-not-platform-publication"
source_context: "Chinese adaptation of a post Yuzheng published on the Statsig blog, rewritten by AI in his Chinese voice; the date is the English original's. Figures are reduced to captions."
attribution_note: "立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。"
---

<!-- provenance:start -->
> Attribution / 归属：立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。
<!-- provenance:end -->

# 实验跑到成千上万个时，怎样应对复杂度

> **中文版** · 立正在Statsig博客发表的文章「Addressing complexity in enterprise-scale experimentation」的中文版，AI按他的中文习惯改写。按[立正参考使用许可](https://github.com/sunyuzheng/lizheng-open-context/blob/main/LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md)使用；图见[英文原文](https://www.statsig.com/blog/addressing-complexity-in-enterprise-scale-experimentation)。

- 原文标题：Addressing complexity in enterprise-scale experimentation
- 原文链接：https://www.statsig.com/blog/addressing-complexity-in-enterprise-scale-experimentation
- 发布日期：2025-04-23
- 作者：Yuzheng Sun（立正）

## 当实验数以千计，要重新想覆盖率、指标和假设

对一家每个月上线一个功能的创业公司来说，A/B实验是个不错的副业。对一家每天上线几十个版本的全球化大企业来说，实验会变成一套操作系统：决策、激励，甚至技术架构，都会围着它转。

复杂度就这样悄悄爬进来。不是因为数学变难了，而是因为人和组织的接触面扩大了好几个数量级。

从我们在Statsig的视角看，我们常常发现，有三个杠杆决定了这些复杂度是会催生洞察，还是会让进展陷入停滞：1）**覆盖率**，2）**指标的成熟度**，3）**假设的质量**。

### 覆盖率：产品改动里，真正被实验过的占多少？

如果只有20%的功能接入了实验，实验就显得可有可无，工期一紧，第一个被砍的就是它。如果覆盖率是100%，实验就是发布的关卡：数据说安全之前，任何功能都不算「上线」。

- **大企业为什么做不到**：多条路线图并行，老旧的代码路径，还有来自外部、要求每个季度出成绩的压力，都在鼓励「先上了再说」。
- **覆盖不全的隐性代价**：盲区会累积。团队过度看重少数几样他们确实测了的东西，领导层也开始相信一条不完整的趋势线。
- **怎样往上走**：
  - 把feature flag和实验集成起来，让每个功能**默认**都*可以*是一个实验；
  - 让工程团队的KPI和指标上的影响挂钩，而不是和功能上线挂钩；
  - 把没法接入实验的老代码下线，它会给以后的每一个决策交税。

### 指标的成熟度：从单点KPI到整体的OEC

点击率很诱人：它动得快，放在看板上看着很清爽。但当转化率（CVR）提升、留存却崩了的时候，这个幻觉就破了。成熟的实验项目会升级到**综合评估标准（Overall Evaluation Criterion，OEC）**：把收入、用户参与度、风险和用户情绪加权组合在一起。

| 成熟度 | 纳入的指标 | 通常回答的问题 |
| --- | --- | --- |
| **基础** | 转化率、加购、页面速度 | 「大家点得更多了吗？」 |
| **进阶** | 留存、付费转化、流失 | 「它创造了持久的价值吗？」 |
| **全面** | 融合了收入、LTV、客服工单、风险评分的OEC | 「长期来看，这对客户和业务都是好事吗？」 |

- **大企业为什么做不到**：每个业务团队只拥有一块数据；把它们合到一起，需要跨组织达成共识，还需要能容忍延迟的数据管道。
- **怎样往上走**：
  - 指标是公司的语言。用一个集中的指标目录，让它们清楚、透明；
  - 每个实验选几个主要指标和几个护栏指标（guardrail metrics），在相似的实验之间尽量统一；
  - 让一个分析团队负责OEC，维护核心指标清单，并理解这些指标之间的取舍。

### 假设的质量：从「看看哪个能成」到不断积累的学习

如果每个实验都是一次孤立的抛硬币，从来不影响下一个决策，那跑几千个实验也没有意义。

- **反模式**：梳理待办事项变成了比谁人气高，谁嗓门大，谁的实验就先做。
- **成熟的标志**：
  - 每张实验卡片都以一个可以被证伪的陈述开头（「如果我们把新用户引导缩短一步，第7天留存会提升至少1%」）；
  - 实验后的总结是必须做的，不管赢还是输，学到的东西都要进入一个集中的知识库；
  - 下一批想法必须引用之前的证据（「上个季度我们看到，简化步骤B比简化步骤A更重要；这个实验在B上挖得更深」）。
- **怎样往上走**：
  - 教PM因果推断的基础，让他们写出更锋利的假设；
  - 在梳理待办之前，开一个有时间限制的「证据回顾」会；
  - 投资建设可搜索的实验档案。团队一重组，上下文很快就过时了。

## 合在一起：一个实用的成熟度矩阵

| 维度 | 打基础 | 发展中 | 成熟 |
| --- | --- | --- | --- |
| **覆盖率** | 被实验的功能不到40% | 40%到80% | 80%到100%，实验优先的发布流程 |
| **指标** | 单一KPI | KPI加下游指标 | 稳定的OEC加模板 |
| **假设** | 临时起意，追着结果跑 | 有一些假设上的纪律 | 和证据关联，不断积累的学习 |

进步很少是齐头并进的。一家公司可能有一套漂亮的OEC，却仍然只给旗舰功能做实验。这个矩阵能让你看清，下一个数量级的提升要靠打开哪个关节。

#### 矩阵之外：在取舍之间找路

- **速度和覆盖率**：全覆盖听起来很理想，直到它拖慢了上线节奏。关键在于把feature flag和实验集成起来，看影响的读数不应该带来额外的工程工作。
- **信号和数据过载**：一套丰富的OEC容易让人陷入分析瘫痪。一个集中的平台，用可信的统计引擎和直观的界面把信息整合起来，可以提升整个公司的数据素养。
- **好奇心和纪律**：鼓励天马行空的想法，但坚持要求它们落成可检验的假设。创新在护栏之内才能长得好。

### 最后

复杂度不是敌人，失控的复杂度才是。

拥抱全覆盖、整体的指标和有纪律的假设的企业，会把实验变成一个飞轮：每转一圈，都比上一圈更容易、更快、更有洞察。把实验当成一次次孤立赌博的企业，会淹没在自己产生的数据废气里。差别很少只在工具上，而在于一个战略选择：*主动驾驭*复杂度，而不是回避它。
