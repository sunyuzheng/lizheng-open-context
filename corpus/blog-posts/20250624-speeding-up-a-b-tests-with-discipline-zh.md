---
id: "statsig-blog-speeding-up-a-b-tests-with-discipline-zh"
title: "靠纪律给A/B实验提速"
original_title: "Speeding up A/B tests with discipline"
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
source_url: "https://www.statsig.com/blog/speeding-up-a-b-tests-with-discipline"
original_source_url: "https://www.statsig.com/blog/speeding-up-a-b-tests-with-discipline"
source_family: "https://www.statsig.com/blog/speeding-up-a-b-tests-with-discipline"
published_at: "2025-06-24"
original_published_at: "2025-06-24"
translation_publication_status: "repository-reading-aid-not-platform-publication"
source_context: "Chinese adaptation of a post Yuzheng published on the Statsig blog, rewritten by AI in his Chinese voice; the date is the English original's. Figures are reduced to captions."
attribution_note: "立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。"
---

<!-- provenance:start -->
> Attribution / 归属：立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。
<!-- provenance:end -->

# 靠纪律给A/B实验提速

> **中文版** · 立正在Statsig博客发表的文章「Speeding up A/B tests with discipline」的中文版，AI按他的中文习惯改写。按[立正参考使用许可](https://github.com/sunyuzheng/lizheng-open-context/blob/main/LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md)使用；图见[英文原文](https://www.statsig.com/blog/speeding-up-a-b-tests-with-discipline)。

- 原文标题：Speeding up A/B tests with discipline
- 原文链接：https://www.statsig.com/blog/speeding-up-a-b-tests-with-discipline
- 发布日期：2025-06-24
- 作者：Yuzheng Sun（立正）

如果手里没有合适的工具，A/B实验会像跑马拉松，而不是速通。

想象一下：你精心设计了一个提升结账转化的A/B实验，可按你现在的流量，每个组至少要40万笔交易，才能检测出1%的提升。也就是说，你要等**十一周**才能攒够用户数据。这比一个季度还长，比你的耐心还长，比你的路线图还长，而且……比离你下一次绩效评估的时间还长。

没有合适的工具，A/B实验一跑就是6到11周，被大样本量的要求和僵硬的统计计划拖着走。下面是一份实战指南，讲怎样用对的技术和工具，把这十一周缩短。

这篇文章会介绍一整套更聪明的统计方法，**给你的A/B实验提速**，把周期从几个月缩短到几周。

## 默认并行跑实验

第一个提速的杠杆很明显：让更多用户进入实验。但做法是靠*并行*，而不是靠加人。同时跑多个实验，而不是让它们排队。

如果你担心交互效应，Microsoft在2023年的研究[A/B Interactions: A Call to Relax](https://www.microsoft.com/en-us/research/articles/a-b-interactions-a-call-to-relax/)检查了几百个相互重叠的实验，发现真正的交互效应极其罕见。实践中，为了隔离每个实验而造成的延迟，远比偶尔出现一个古怪交互的风险糟糕。所以，让你的实验并排跑，事后再监控结果。你可以用自动化的检测工具，比如[Statsig的交互效应检测](https://www.statsig.com/blog/interaction-effect-detection)，替你做这份记账的工作。

如果你确实需要互斥的实验，仍然可以把实验放进[分层（layers）](https://docs.statsig.com/layers/)里。但要记住，每多一层，你的流量就被切得更薄。

## 用代理指标，而不是你的KPI

第二个杠杆，动的是*指标*，而不是用户。收入常被看作终极指标，但它动起来慢得要命，因为只有一小部分访客会买东西；消费金额的差异还会带来额外的噪音。换成一个代理指标，比如「点击『加入购物车』」，它的触发频率是购买的十倍，又和购买高度相关，相当于把样本量放大了十倍。

去找那些在逻辑上和你的目标一致、但能更快更早给出信号的代理指标，然后用历史数据做相关性分析来验证它们。一个代理指标好用，通常满足这几条：

- 它处在目标结果的**漏斗上游**；
- 历史数据显示它和下游KPI之间有**稳定的相关性**；
- 它不太容易受外部冲击影响（节假日、集中的营销投放）；
- 它的噪音更小。

你不用放弃收入指标，把它留作护栏指标就好；但实验结果的*决策*，以代理指标为准。

## 用审慎的统计方法，放大信号、降低噪音

噪音低，置信区间就窄，需要的样本也就少。经典的方法依然好用：

### 协变量调整（CUPED和CURE）

[CUPED](https://www.statsig.com/blog/cuped)减掉的是实验前协变量能解释的那部分波动。Statsig的[CURE](https://www.statsig.com/blog/announcing-cure)把这个技巧推广开来，用类似lasso的回归处理任意的协变量数据，最多能降低40%的方差，对新用户也有效。

对实践者来说，CURE和CUPED是极其强大的技术：你什么都不用牺牲（因为它们是一致估计量），只用简单的线性回归就降低了方差。而且，用上CUPED，你就已经完成了80%以上。其他大多数统计方法，都需要在偏差和方差之间做取舍。

话虽如此，别搞得太花哨，因为实验项目的完整性和可信度至关重要。如果你用了一个新奇的方法，结果被翻了过来，大家的整体信任会很快蒸发。

### 缩尾处理（winsorization）和设上限

消费金额这类重尾指标，会让传统的方差公式失灵。把最高的0.1%截掉，或者给每笔订单设个上限，比如1,000美元，就能把尾巴驯服。要小心地做，并且把规则写下来，免得有人喊不公平。

### 分层抽样

一开始就让各组平衡，而不是祈祷随机化能把大客户（whales）和路过的用户自然摊平。Statsig现在支持[分层分组（stratified assignment）](https://www.statsig.com/blog/introducing-stratified-sampling)，第一天就能让各组对称。

把这些技巧合起来，就能有纪律、严谨、可解释地降低噪音。我们是统计学家，不是魔术师，但这已经很接近魔术了。

## 自适应分配和快速决策

### 浅层实验用上下文老虎机

当决策规则是二选一（「选出赢家，干掉输家」），而且纯粹基于定量数据（比如转化率）时，上下文多臂老虎机（contextual multi-armed bandit，CMAB）会不断把流量推向表现最好的那个。它帮不了像素级的精细校准研究，但对标题文案或者颜色这类测试，效果拔群。如果你想要这套机制、又不想碰数学，Statsig的[AutoTune模块](https://docs.statsig.com/autotune/contextual/introduction/)一键就能用。

### 序贯检验

偷看实验结果被视为一种罪过，因为它会抬高长期的错误发现率。但只在实验跑完之后才看结果，是不现实的。我们就是想偷看。mSPRT这类方法，能让你在保住总体错误率（family-wise error rate）的同时，在证据压倒性的时候提前停止。

### 多指标用Benjamini–Hochberg

另外，在最终读结果时，如果你报告的是一大屏指标，BH程序可以控制错误发现率。它是防止在指标里「挖矿」的廉价保险，但它**不**处理反复查看的问题；把它和mSPRT结合起来，就能纠正p-hacking里常见的错误。

### 贝叶斯的表述

一个无先验（也就是Jeffreys先验）的贝叶斯读数，会把你的数据转换成「版本B更好」的概率。只有在手里有可信的历史证据时，才引入[带信息的先验](https://www.statsig.com/blog/informed-bayesian-ab-testing)，并且对此要诚实。[贝叶斯推断改变的是解读，不是数据](https://www.statsig.com/blog/bayesian-vs-frequentist-statistics)，所以把它当作讲清楚结果的工具，而不是一根魔杖。

### 最后一公里：解读和判断

用完所有的统计方法，我们还是得**思考**。Tom Cunningham把实验数据科学家的任务总结为：根据实验观察到的效应，1）解读真实效应；2）外推长期效应。对认真做产品实验的专业人士来说，[他这篇文章](https://tecunningham.github.io/posts/2023-04-18-experiment-interpretation-extrapolation.html)是必读的。

和几个真实用户聊一聊，看看会话回放，问问自己：*为什么*这个版本让指标动了？十次对话的样本，可能比一千万行日志揭示出更多的细节。

## 别破坏规则

提速不是偷工减料，而是把路清干净。并行跑更多的实验，更早地听到更响亮的信号，把数据里的噪音挤出去，把你的统计规范打理好。未来的你，只老了三周，而不是十一周，会感谢你的。
