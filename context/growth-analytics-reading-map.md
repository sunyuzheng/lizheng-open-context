---
id: "growth-analytics-reading-map-v1"
title: "增长数据分析与实验阅读地图"
author: "AI"
source_type: "context"
snapshot_at: "2026-10-04"
rights_scope: "first-party-summary"
license: "CC-BY-4.0"
publisher: "Yuzheng Sun"
original_author: "See cited sources"
content_origin: "ai-synthesis"
generation_method: "ai-written"
evidence_role: "secondary-synthesis"
yuzheng_stance_weight: "secondary-only"
attribution_note: "本文件由 AI 撰写／综合，整理对象是立正及所引来源；不是立正亲笔、逐字原话或逐句认可的证明。请回到原文核实，不能用综合层覆盖直接来源。"
source_family: "growth-analytics-reading-map-v1"
language: "zh"
source_context: "AI-authored repository synthesis of public sources; not a new statement by Yuzheng."
source_url: "https://github.com/sunyuzheng/lizheng-open-context/blob/main/context/growth-analytics-reading-map.md"
---

<!-- provenance:start -->
> Attribution / 归属：本文件由 AI 撰写／综合，整理对象是立正及所引来源；不是立正亲笔、逐字原话或逐句认可的证明。请回到原文核实，不能用综合层覆盖直接来源。
<!-- provenance:end -->

# 增长数据分析与实验阅读地图

立正讲「用数据做增长」和「A/B实验」的材料分在三处：

- **书**：他和Mengying Li、Joe Kumar合著的《Growth Data Analytics Playbook》（Statsig Press，2025）。中文版在[lizheng.ai](https://www.lizheng.ai/book/growth-data-analytics-playbook)免费读，全文在[`corpus/book-chapters/`](../corpus/book-chapters/)，目录见[`index/growth-data-analytics-playbook-zh.md`](../index/growth-data-analytics-playbook-zh.md)。
- **Statsig博客**：他2024到2025年在Statsig官方博客发表的19篇文章（2篇合著），中文版在[`corpus/blog-posts/`](../corpus/blog-posts/)，目录见[`index/statsig-blog.md`](../index/statsig-blog.md)。
- **视频**：「课代表数据大师课」等他本人主讲的视频，字幕在[`corpus/videos/`](../corpus/videos/)。

这份地图按问题把三处连起来。书和博客的中文版是AI按立正的中文习惯改写的，具体说法要回到英文原文核对；书和合著文章里的「我们」不能整段当作立正一个人的立场。要判断立正本人怎么想，以他自己讲的视频和发的帖子为准。

## 按问题找

### 产品有没有找到PMF？

- 书：[第2章　找到产品价值的早期信号](../corpus/book-chapters/20251118-gdap-zh-ch02.md)：留存曲线的三种形态、怎么读cohort表、留存上的四个坑，以及留存太慢时怎么找领先指标。
- 视频：[关于留存的所有知识｜课代表数据大师课3](../corpus/videos/20211207-Yj9XouK-hi0.md)（2021-12-07）：留存要先定义人群、时间和行为；微笑曲线可以靠补贴买出来。
- 视频：[Adoption很重要，但经常被忽视｜课代表数据大师课2](../corpus/videos/20211002-qgtijiTjfgw.md)（2021-10-02）：判断一个功能有没有找到PMF，看adoption和retention；adoption要分四步看：有资格看到、真的看到、点进去、完成核心动作。
- 判断卡：`retention-definition-matters`。

### 增长从哪来？日活为什么不涨？

- 书：[第1章　用增长分析驱动产品成功](../corpus/book-chapters/20251118-gdap-zh-ch01.md)是全书地图；[第3章　用growth accounting打地基](../corpus/book-chapters/20251118-gdap-zh-ch03.md)把北极星指标拆成新增、留存、流失、回流和沉睡。
- 视频：[Meta、Notion、腾讯内部的增长专业课，我们写成了一本书](../corpus/videos/20251117-W09mt7WxSas.md)（2025-11-17）：立正本人对这本书五块内容的概括，以及「成熟产品的活跃变化大多来自留存」。
- 判断卡：`growth-accounting-first`。

### 怎么拿到高质量用户？渠道怎么看？

- 书：[第4章　获取并培养高质量用户](../corpus/book-chapters/20251118-gdap-zh-ch04.md)：LTV、ARPU、病毒系数、注册漏斗，以及一道按渠道算投入产出的练习。
- 视频：[增长和转化的底层逻辑｜漏斗｜课代表数据大师课4](../corpus/videos/20250108-VFTf3_sYBms.md)（2025-01-08）：群体行为有规律；漏斗要横竖结合看；用现有资源撬动更大的漏斗；从数字回到人。
- 博客：[为什么「数据驱动」的营销归因模型兑现不了承诺](../corpus/blog-posts/20250311-data-driven-marketing-attribution-shortcomings-zh.md)、[数字营销归因模型：一份技术综述](../corpus/blog-posts/20250417-marketing-attribution-models-tech-survey-zh.md)。
- 判断卡：`bigger-funnel-first`。

### 留住用户，找回流失的用户

- 书：[第5章　留住用户，让他们常来](../corpus/book-chapters/20251118-gdap-zh-ch05.md)（黏性、DAU/MAU、Lness、重度用户）；[第6章　把流失的用户找回来](../corpus/book-chapters/20251118-gdap-zh-ch06.md)（流失预测、通知、少发反而更好的长期实验）。
- 博客：[关于新奇效应，你需要知道的都在这里](../corpus/blog-posts/20240320-novelty-effects-zh.md)：新功能刚上线时的效果会因为「新」而偏离，要看处理效应的时间序列。

### 变现、性能和增长飞轮

- 书：[第7章　加速转化，增加收入](../corpus/book-chapters/20251118-gdap-zh-ch07.md)：四种收入模式、收入的growth accounting、NRR和GRR、PLG和SLG、定价。
- 书：[第8章　优化性能，打造增长飞轮](../corpus/book-chapters/20251118-gdap-zh-ch08.md)：性能看P90和P95、人为减速实验、放弃曲线、创作者飞轮。

### 怎么定增长目标

- 书：[第9章　估算增长空间，定可实现的目标](../corpus/book-chapters/20251118-gdap-zh-ch09.md)：目标、制衡和护栏指标；基线、自上而下和自下而上；拆解目标时别忘了自然增长。

### 为什么要做实验，怎么做对

- 书：[第10章　设计并实施有效的实验](../corpus/book-chapters/20251118-gdap-zh-ch10.md)：证据金字塔、大多数想法会失败、Marketplace白底图和降低视频画质两个实验、可规模化的实验体系。
- 视频：[AB实验，有哪些重要却不为人知的知识？｜课代表数据大师课5](../corpus/videos/20250924-9kh1YvzZYks.md)（2025-09-24）：实验的价值来自意外；功能开关和实验做成同一个东西；假设检验的常见误解；CUPED、贝叶斯和序贯检验。
- 视频：[Facebook的AB Testing是什么样子的？为什么对公司文化有这么大影响？](../corpus/videos/20210128-ET9D_nildHw.md)（2021-01-28）、[AB Testing概览](../corpus/videos/20200824-vx15aj-ah1c.md)（2020-08-24）。
- 博客：[什么是A/B实验，它为什么重要？](../corpus/blog-posts/20240905-what-is-a-b-testing-and-why-is-it-important-zh.md)、[Meta怎样把我变成了A/B实验的铁杆支持者](../corpus/blog-posts/20240910-meta-a-b-testing-zh.md)、[为什么说A/B实验最终是定性的](../corpus/blog-posts/20250409-why-ab-testing-is-ultimately-qualitative-zh.md)、[靠纪律给A/B实验提速](../corpus/blog-posts/20250624-speeding-up-a-b-tests-with-discipline-zh.md)、[A/B实验平台怎样让数据科学变得更有意思](../corpus/blog-posts/20241016-how-ab-testing-platforms-make-data-science-more-interesting-zh.md)（Ronny Kohavi一场分享的回顾，引号里的话属于他）。
- 判断卡：`experiments-value-from-surprises`；坏结果怎么报告，见`hard-truths-with-people`。

### 统计：假设检验、贝叶斯、相关和因果

- 博客：[四步讲清楚假设检验](../corpus/blog-posts/20240722-hypothesis-testing-explained-zh.md)、[做假设检验，为什么你应该「接受」原假设](../corpus/blog-posts/20240925-hypothesis-testing-accept-null-zh.md)、[贝叶斯和频率学派之争，没那么大不了？](../corpus/blog-posts/20250211-bayesian-vs-frequentist-statistics-zh.md)、[带信息先验的贝叶斯A/B实验：两种做法](../corpus/blog-posts/20250313-informed-bayesian-ab-testing-zh.md)、[怎样想清楚相关和因果的关系](../corpus/blog-posts/20250227-correlation-vs-causation-guide-zh.md)。

### 搭实验平台和实验体系

- 博客：[让实验系统能规模化：几条技术洞察](../corpus/blog-posts/20240828-technical-insights-to-a-scalable-experimentation-system-zh.md)、[实验系统怎样平衡规模、成本和性能](../corpus/blog-posts/20250211-balancing-scale-cost-performance-experimentation-systems-zh.md)（与Pushpendra Nagtode合著）、[实验跑到成千上万个时，怎样应对复杂度](../corpus/blog-posts/20250423-addressing-complexity-in-enterprise-scale-experimentation-zh.md)、[在双边市场里做A/B实验：难在哪，怎么办](../corpus/blog-posts/20250326-marketplace-challenges-in-ab-testing-zh.md)。

### AI产品怎样上线

- 博客：[被浪打翻，还是乘浪而起：从创业公司看AI产品怎样上线](../corpus/blog-posts/20250808-ai-startups-lessons-learned-zh.md)（与Alexey Komissarouk合著）。

### 数据科学这份工作

- 博客：[为什么我要开一个数据科学YouTube频道](../corpus/blog-posts/20240208-pragmatic-data-science-launch-zh.md)。
- 视频：[数据科学到底在做什么？ - 2022总结版](../corpus/videos/20230105-hveZx2CN8Sg.md)（2023-01-05）。

## 使用提醒

- 书和博客的中文版证据权重是「核对原文」（`verify-original`）：适合找思路、找例子，引用具体数字和说法前回到英文原文。
- 视频字幕是立正本人的话，但视频里引用的他人观点和案例仍归原作者。
- 产品形态、平台能力和行业数字会变，引用时保留原始日期。
