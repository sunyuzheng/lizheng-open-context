---
id: "statsig-blog-technical-insights-to-a-scalable-experimentation-system-zh"
title: "让实验系统能规模化：几条技术洞察"
original_title: "Technical insights to a scalable experimentation system"
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
source_url: "https://www.statsig.com/blog/technical-insights-to-a-scalable-experimentation-system"
original_source_url: "https://www.statsig.com/blog/technical-insights-to-a-scalable-experimentation-system"
source_family: "https://www.statsig.com/blog/technical-insights-to-a-scalable-experimentation-system"
published_at: "2024-08-28"
original_published_at: "2024-08-28"
translation_publication_status: "repository-reading-aid-not-platform-publication"
source_context: "Chinese adaptation of a post Yuzheng published on the Statsig blog, rewritten by AI in his Chinese voice; the date is the English original's. Figures are reduced to captions."
attribution_note: "立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。"
---

<!-- provenance:start -->
> Attribution / 归属：立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。
<!-- provenance:end -->

# 让实验系统能规模化：几条技术洞察

> **中文版** · 立正在Statsig博客发表的文章「Technical insights to a scalable experimentation system」的中文版，AI按他的中文习惯改写。按[立正参考使用许可](https://github.com/sunyuzheng/lizheng-open-context/blob/main/LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md)使用；图见[英文原文](https://www.statsig.com/blog/technical-insights-to-a-scalable-experimentation-system)。

- 原文标题：Technical insights to a scalable experimentation system
- 原文链接：https://www.statsig.com/blog/technical-insights-to-a-scalable-experimentation-system
- 发布日期：2024-08-28
- 作者：Yuzheng Sun（立正）

## 一、引言

[Ron Kohavi等人（2022）](https://exp-platform.com/abtestingintuitionbusters/)指出过，要让人信任实验结果，是很难的。

我们（Statsig）是做实验平台的。我们观察到，在科技行业里，一个实验项目能不能成功，靠的不是实验做得多复杂，而是整个项目是否可信、能否规模化。

复杂的实验反而可能削弱大家对整个实验项目的信任：它引入了更多的自由度，p-hacking的风险也就更高。如果激励机制奖励的是「做出显著结果」的人，这个问题会更严重。

在大多数科技公司，实验系统很容易起步，却很难规模化，原因是信息上和管理上的复杂度。这两样东西不那么看得见摸得着，所以常常被忽略，结果是大量资源投进了一个没法规模化的系统。这种情况下，多维护一些实验的成本是超线性增长的，收益却是亚线性增长的。

我们服务着几千家公司，覆盖每月超过20亿的终端用户。这篇文章把我们的经验和教训提炼成几条关键的技术洞察：通过用心的系统设计，解决信息过载和管理复杂度的问题，让实验系统能够规模化。

## 二、限制实验规模化的两个无形因素

任何系统要能规模化，运营成本的增长都必须慢于规模的增长。现在数据库、计算和存储都很发达，对大多数实验系统来说，看得见的成本并不是主要问题。真正限制规模化的，是两个看不见的因素：信息过载和管理复杂度。

### 2.1 信息过载

实验会产生海量的信息，而且信息量通常是多项式级增长的：

- **参数**：参数空间和实验数、指标数、变体数、用户分群数都相关。实验越复杂，这几个维度都膨胀得越快。
- **历史关联**：实验既服务于决策，也服务于学习，所以既要全面理解当前的实验，也要理解过去的实验。
- **系统里的混乱**：严谨的实验流程里到处是坑，包括样本比例不匹配（SRM）、多重比较、偷看结果（peeking）、网络效应、功效不足、日志错误和数据管道出错。

如果公司没有一套系统来处理和整合这些信息，往往就只能靠人来扛这些复杂度，而这天然是没法规模化的。

### 2.2 管理复杂度

管理上的负担比信息更看不见，但不能忽略：

1. 大多数工程师和产品经理缺少必要的统计知识，没法正确解读实验结果，也没法从观察到的效应正确推断真实效应（[Cunningham，2023](https://tecunningham.github.io/posts/2023-04-18-experiment-interpretation-extrapolation.html)）。
2. 管理上的激励常常鼓励有害的行为，比如p-hacking。
3. 实验结束后，配置留在代码库里，会变成技术债。

这些问题都能解决，但因为委托代理问题和资源限制，中层管理者通常没有动力去解决它们。设计系统的时候，必须认真考虑这些因素。

### 2.3 两难：边际成本比边际收益涨得快

如果没有一套设计良好的系统，实验的投资回报率（ROI）会随着规模增大而下降，因为：

- 实验的边际收益随规模线性或亚线性增长，因为能用来把信息变成影响的精力越来越少；
- 实验的边际成本随规模超线性增长，因为信息和管理的负担越来越重。

这两点让很多实验团队陷入两难：他们成了自己成功的受害者。好在这个两难是能解决的。如果系统从一开始就设计对了，多跑实验的成本就能亚线性增长，省下来的资源可以用来把实验结果转化成影响。

## 三、可扩展实验系统的技术洞察

在实践中，我们总结出让实验能够规模化的四条关键洞察。

### 3.1 通过和feature flag集成，让A/B实验默认开启

A/B实验需要三样东西：实验组的体验、随机化，以及一个综合评估标准（OEC）。把随机化和指标系统跟feature flag（功能开关）集成在一起，就能把这几样自动化，让每一次功能上线都能自动触发A/B实验，不需要多少额外的工程工作。这样做还有三个附带的好处：1）工程师可以自助开实验；2）可以做低代码的实验；3）曝光数据和日志数据都原生地属于实验流程，观察整个系统、做额外分析、排查问题都容易得多。

### 3.2 把指标、日志和实验分开

指标是业务结果的代理，会随着业务重点的变化而演变；但底层的日志数据和数据管道应该保持稳定。把指标的定义和日志分开，实验就能直接用已有的配置，指标也能很方便地调整，而不影响日志的完整性。我们会在演讲里分享我们的实验架构和数据管道的有向无环图（DAG）。

### 3.3 数据要一体化

从数据到决策，链条很长：打日志，跑DAG，定义指标，再到大家怎样理解和使用这些数据。每一步都很容易产生偏差和误解，让信息过载更严重。唯一的事实来源（single source of truth）、诊断信息和上下文，应该放在同一个地方，并且端到端可见。

### 3.4 围绕业务决策做自动检查

统计上正确的东西，和对业务决策有用的东西，中间常常有一道缝。比如，在实验开始之前，两组的基线就有差异：这在统计上并不构成偏差，但对业务决策来说是不理想的，通常需要重新开始实验。一个自动化的系统，不仅要检测出样本比例不匹配这样的错误，还要能发现、标记并减轻各种「噪音」，比如异质效应、交互效应和有偏的抽样。此外，系统应该通过用户界面（UI）引导最佳实践：用序贯检验来抑制偷看结果，要求在实验之前写好假设，一开始就提供多重比较校正，以及不鼓励在实验进行中改p值阈值。

## 四、可扩展的实验是什么样子

我们总结出可扩展实验系统的七个关键特征：

1. 所有新功能默认开实验；
2. 指标定义一次，到处使用；
3. 数据可靠、可追溯、透明；
4. 统计引擎可信、实用，没有「魔法」数学；
5. 自动检查错误（比如SRM），并标出警告（比如两组基线有差异）；
6. 为产品决策有意识地分层呈现实验信息；
7. 围绕实验结果有协作的上下文。

具备这些特征的系统，除了能降低多跑实验的成本，还能带来两个主要的结果。

### 4.1 实验变成一件协作的事

不同角色各自发挥长处：工程师按最佳实践管理系统；产品经理提出假设、推动协作、提供定性的证据；数据科学家专注于实验设计、评审和更深入的分析。这样一来，数据科学家可以把精力放在自己的专长上，而不用盯着A/B实验生命周期的每一个环节，实验的整体价值也会提高。

### 4.2 持续地从实验里获得价值

实验提供的是可信的因果证据，但没有好的想法和好的执行，它本身产生不了回报。把实验当作一件协作的事，目标是让整个产品开发团队都学会衡量、学习和改进，长期来看创造更高的回报。

## 五、延伸阅读

除了这篇摘要，我们还有一份[打磨过的演讲稿](https://docs.google.com/presentation/d/1wg5kU12z5jM-deoRqQln2W_deSlWo-GZ1GTRvYjha9I/edit?usp=sharing)，已经给许多公司的几百位数据科学家讲过，帮助他们把实验做成。我们也有和业内实践者的[播客访谈](https://youtube.com/playlist?list=PL-ezxB8afRd-wYfsd73hvIerND-qOpq5c&si=RQ193gf_649Nk4mG)，为这里讨论的观点提供了一些实际的佐证。
