---
id: "statsig-blog-marketplace-challenges-in-ab-testing-zh"
title: "在双边市场里做A/B实验：难在哪，怎么办"
original_title: "Marketplace challenges in A/B testing and how to address them"
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
source_url: "https://www.statsig.com/blog/marketplace-challenges-in-ab-testing"
original_source_url: "https://www.statsig.com/blog/marketplace-challenges-in-ab-testing"
source_family: "https://www.statsig.com/blog/marketplace-challenges-in-ab-testing"
published_at: "2025-03-26"
original_published_at: "2025-03-26"
translation_publication_status: "repository-reading-aid-not-platform-publication"
source_context: "Chinese adaptation of a post Yuzheng published on the Statsig blog, rewritten by AI in his Chinese voice; the date is the English original's. Figures are reduced to captions."
attribution_note: "立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。"
---

<!-- provenance:start -->
> Attribution / 归属：立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。
<!-- provenance:end -->

# 在双边市场里做A/B实验：难在哪，怎么办

> **中文版** · 立正在Statsig博客发表的文章「Marketplace challenges in A/B testing and how to address them」的中文版，AI按他的中文习惯改写。按[立正参考使用许可](https://github.com/sunyuzheng/lizheng-open-context/blob/main/LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md)使用；图见[英文原文](https://www.statsig.com/blog/marketplace-challenges-in-ab-testing)。

- 原文标题：Marketplace challenges in A/B testing and how to address them
- 原文链接：https://www.statsig.com/blog/marketplace-challenges-in-ab-testing
- 发布日期：2025-03-26
- 作者：Yuzheng Sun（立正）

在marketplace，也就是双边或多边市场里做A/B实验，会比较棘手，因为买家、卖家和平台本身这几方一直在互相影响。

测试一个新功能时，你不能忽略这几方之间的重叠，也不能忽略供需可能以意想不到的方式变化。传统的按用户随机分组，常常会造成「跨组污染」：市场一边处在实验组的人，和另一边处在对照组的人发生了交互。

网络效应让事情更复杂，因为一边的一个小改动，可能在整个系统里层层传开。哪怕只是调整一下费用，也可能推动需求或供给发生变化，从对照组「抢走」流量，把你的指标虚高或者压低。

尽管有这些障碍，随机实验仍然是衡量因果影响的黄金标准。关键在于，既要保住随机化的原则，又要面对多边市场的现实。下面是几种应对marketplace常见陷阱的实用方法，最后再谈谈身份识别（identity resolution）和怎样选对实验方法。

## 方法

### 1. [按簇随机（cluster-based randomization）](https://docs.statsig.com/metrics/different-id/)

不按单个用户随机，而是按整个簇随机：城市、品类或者地理区域。这样，同一个区域或品类里的所有人看到的是同一个版本，大大降低了实验组的买家碰上对照组卖家（或者反过来）的可能。

#### 为什么有效

把天然有联系的人放在一组，能减少跨组污染，更干净地分离出实验的影响。比如你在试一个新的运费政策，可以在一个州实行，同时把一个相似的地区留作对照。

#### 取舍

不同的簇之间可能在一些重要方面有差别（比如经济走势或者人口规模），所以需要足够多的簇，才能把这些差别平衡掉。另外，因为同一个簇内部的差异更小，你通常需要更大的样本量，才能得到清楚、可靠的结果。

### 2. [轮换实验（switchback testing）](https://www.statsig.com/blog/switchback-experiments)

轮换实验是让同一个单元，比如一个城市或者整个平台，在不同的时间段分别处于实验组或对照组。比如今天跑实验组，明天切回对照组，然后一直这样交替下去。

#### 它怎样帮上忙

整个市场同一时间只跑一个版本，用户就不可能同时看到两个版本，跨组污染也就少了。它还有助于捕捉周期性的规律（比如周末和工作日的行为差别），因为每个版本都会经历各种不同的日子和时段。

#### 例子

一个外卖app可能周一测试新的高峰溢价算法，周二切回旧算法，依此类推。几周下来，每个版本都经历了多个工作日和周末。这样可以确认新的定价是否真的缩短了等待时间，同时没有伤害订单量和骑手的供给。

#### 实用建议

随机决定哪个时间块跑哪个版本，并且让实验跑得足够久，覆盖各种情况：高峰时段、低谷时段、周末和节假日。注意可能溢出到下一个时间块的「残留」（carryover）效应。

### 3. [分阶段放量（phased rollouts）](https://www.statsig.com/blog/release-management-best-practices)

分阶段放量是逐步扩大看到新功能的用户或簇的比例（比如从1%到10%再到50%），每一步都用随机分组。分阶段放量在marketplace之外也很常见，几乎任何大规模的产品都能这么做。但面对多边市场时，有几件事要额外注意。

#### marketplace的特殊之处

如果你的功能可能打破买卖双方之间的平衡，分阶段的做法尤其有用。你可以从小规模开始，看看会不会出现连锁反应，比如卖家流失，或者买家蜂拥而入；如果一切都在可控范围内，再往前推。这种循序渐进的做法，能让你在整个市场都暴露之前，尽早发现负面信号。

#### 关键建议

给每个阶段足够的时间稳定下来，因为供需需要一段时间才能调整到位。如果你太频繁地重新分组，就没法干净地分辨哪些变化是功能带来的，哪些只是市场的正常波动。

### 4. 加权随机（[多臂老虎机，multi-armed bandits](https://docs.statsig.com/multi-armed-bandit/)）

多臂老虎机算法一开始把流量比较平均地分给多个版本，然后随着时间推移，把更多流量分给「赢家」。快速放大有希望的版本，可以减少一个可能很差的版本带来的负面影响。

#### 对marketplace的提醒

在网络效应很强的市场里，如果一个版本开始以牺牲另一个版本为代价把用户吸过来，老虎机算法就会出问题。实时的流量重新分配，可能让你看不到供需稳定下来之后的真实情况。

老虎机算法用得不小心，可能得到有偏的结果，或者因为过度优化短期指标而在无意中伤害市场的某一边。对网络效应影响很大的实验，可以考虑坚持用更传统的、能保持流量分配稳定的A/B实验方法（按簇随机或轮换实验）。

## 管理[身份识别](https://docs.statsig.com/statsig-warehouse-native/features/id-resolution/)和[实体属性](https://docs.statsig.com/statsig-warehouse-native/configuration/entity-properties/)

在很多市场里，同一个人既可以是买家，也可以是卖家（或者既是司机又是乘客，等等）。一个用户可能在一个场景里是买家，同时又挂了东西在卖。这种双重角色让随机化变复杂了：你希望一个人不管以哪个身份出现，看到的都是一致的版本；或者，如果你需要分开追踪同一个人的两个身份，那就得有一套清楚的策略。

#### 实用建议

- **定义清楚身份**：事先决定怎样在两种角色里识别每个用户。可以用一个主ID，再加一个「实体属性」（entity property）来区分买家行为和卖家行为。
- **保证分组一致**：如果你希望同一个用户作为买家和卖家时看到的是同一个版本，就要把这一点写进随机化的逻辑。
- **必要时把角色分开**：在有些实验里，把同一个人的买家行为和卖家行为区别对待是合理的。但如果这两个角色之间可能有交互，分开的方式要能避免交叉污染。

## 为什么这些方法有效

这些方法都坚持随机化的原则，只是调整了怎样给用户分组，或者什么时候跑哪个版本。这样一来，不同的实验条件之间就隔得足够开，避免了污染；同时也把那些塑造市场行为的独特周期和地域差异考虑了进去。

不管是把一个区域里的所有人放在一起，还是在不同的日子之间来回切换，或者分阶段上线一个新功能，这些方法都能帮你看清供需怎样在新的均衡下稳定下来，而不混进太多的混杂因素。

---

## 参考文献和延伸阅读

- DoorDash Engineering Blog. (2020). "Exploring Switchback Experiments to Mitigate Network Spillovers."
- Kohavi, R., Tang, D., & Xu, Y. (2020). *Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing.* Cambridge University Press.
- eBay Tech Blog. (2019). "Managing Search Ranking Experiments in a Two-Sided Marketplace."
- Uber Engineering Blog. (2021). "Designing City-Level A/B Tests in Multi-Sided Platforms."
