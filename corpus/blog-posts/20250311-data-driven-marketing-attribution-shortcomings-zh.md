---
id: "statsig-blog-data-driven-marketing-attribution-shortcomings-zh"
title: "为什么「数据驱动」的营销归因模型兑现不了承诺"
original_title: "Why data-driven marketing attribution models don't work as promised"
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
source_url: "https://www.statsig.com/blog/data-driven-marketing-attribution-shortcomings"
original_source_url: "https://www.statsig.com/blog/data-driven-marketing-attribution-shortcomings"
source_family: "https://www.statsig.com/blog/data-driven-marketing-attribution-shortcomings"
published_at: "2025-03-11"
original_published_at: "2025-03-11"
translation_publication_status: "repository-reading-aid-not-platform-publication"
source_context: "Chinese adaptation of a post Yuzheng published on the Statsig blog, rewritten by AI in his Chinese voice; the date is the English original's. Figures are reduced to captions."
attribution_note: "立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。"
---

<!-- provenance:start -->
> Attribution / 归属：立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。
<!-- provenance:end -->

# 为什么「数据驱动」的营销归因模型兑现不了承诺

> **中文版** · 立正在Statsig博客发表的文章「Why data-driven marketing attribution models don't work as promised」的中文版，AI按他的中文习惯改写。按[立正参考使用许可](https://github.com/sunyuzheng/lizheng-open-context/blob/main/LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md)使用；图见[英文原文](https://www.statsig.com/blog/data-driven-marketing-attribution-shortcomings)。

- 原文标题：Why data-driven marketing attribution models don't work as promised
- 原文链接：https://www.statsig.com/blog/data-driven-marketing-attribution-shortcomings
- 发布日期：2025-03-11
- 作者：Yuzheng Sun（立正）

从大企业到小众电商品牌，每个做营销的人都在面对同一个根本问题：营销预算投到哪里，回报最大？

理想情况下，你希望有一个干干净净的算法告诉你：「渠道A贡献了25%的转化，渠道B贡献了40%，渠道C贡献了10%」，诸如此类。这就是营销归因的诱人之处：精确地指出哪些触点真正推动了结果，哪些只是干扰。

> 随口报出一串数字的表情包（图见英文原文）
*图1　「Claire's number dump」：一个人随口报出一串数字（「Eleventy-five」「Forty-twelve percent」）的表情包，截自美剧《摩登家庭》。*

过去二十年，数字化的数据收集爆发式增长，随之而来的是一波复杂的「数据驱动」模型：马尔可夫链（Markov Chain）、Shapley值、算法驱动的多触点归因。它们承诺一劳永逸地解决归因问题。可是，尽管数学很强大、看板很漂亮，很多从业者最后还是失望了。[Gordon等人（2022）](https://arxiv.org/abs/2201.07055)提供了证据：即使数据很丰富，非实验的方法也没法很好地去掉数据里已知的偏差。这篇文章从定性的角度解释为什么。

### 问题：在复杂的环境里评估营销花费

归因的核心，是想**把营销花费和结果连起来**。数字渠道看起来为衡量提供了完美的条件：从点击率、网站停留时长，到再营销广告的曝光，什么都能追踪。营销人员设想，可以一清二楚地看到谁在哪天、按什么顺序点了什么，直到最后完成转化。只要把这条事件链详细地记录下来，就能可靠地算出每一步对最终购买贡献了多少。

随着渠道越来越多，搜索广告、展示广告、邮件、社交媒体、视频、联盟营销、应用内推广，用户旅程也越来越复杂。单独某一次「触达」可能不足以让用户下单。一次购买，可能是品牌曝光、再营销广告、用户评价、网红帖子，甚至纯线下因素累积起来的结果。看到这一点，供应商们开始推出**数据驱动归因**，宣称有一种客观、量化的方式，能把杂乱的路径数据提炼成可以行动的洞察。

### 数据驱动模型承诺了什么

这些方案的底层，很多依赖**马尔可夫链**、**Shapley值**或者**算法**方法，有时是三者的混合。它们在数学细节上各不相同，讲的却是同一个故事：

1. **全局的多触点归因**：不把功劳全算给第一次点击或最后一次点击，而是看整个用户旅程。
2. **数学上的严谨**：马尔可夫链通过模拟「去掉某个渠道会怎样」来估计转化概率；Shapley值按每个渠道在所有组合里的边际贡献分配功劳；机器学习用预测算法或逻辑回归，找出哪些渠道和转化相关。
3. **更准确的决策**：因为这些方法把很多路径的数据都纳入进来，包括转化了的和没转化的旅程，它们声称比固定规则更公平、偏差更小。按说，你会确切地知道该在哪里加大或收缩营销花费，才能获得最大的效果。
4. **更细的归因粒度**：老的「媒体组合」方法只能谈总体效果（比如电视和广播各占多少），数据驱动的系统看起来却能提供到用户级别、逐个渠道，甚至*逐次触达*的洞察。

这些特点合起来讲了一个故事：只要数据够多，模型就能把「哪些渠道和打法该得功劳」这个隐藏的真相挖出来。于是各方都期待拿到一张精确、确定的ROI地图，覆盖整个营销组合。

### 现实中它们做不到的地方

这样精确的指引始终可望而不可即。大多数尝试纯数据驱动归因模型的团队，最终都会撞上一些根本的限制，「一个模型统治一切」的梦想也就破灭了。

**1. 数据不完整、有噪音**

数字营销号称一切都能完美衡量，可现实世界到处是缝隙：跨设备使用、广告拦截、cookie缺失、最后一次线上触达之后跑到线下转化的用户，还有那些不产生可追踪点击的营销手段（比如口碑，或者没被点击的展示广告曝光）。马尔可夫链、Shapley值和基于机器学习的模型都假设：如果一个渠道有影响，这个影响就会体现在用户路径数据里。但实际上，这些数据常常缺了关键的几块拼图，归因结果就被扭曲了。

**2. 相关不等于因果**

马尔可夫链和Shapley值，都是围绕「把某个渠道从等式里去掉」，衡量转化概率的差，再把这个差值算回给这个渠道。只有当你相信历史数据代表的是真正的因果关系时，这才成立。很多渠道之所以出现在旅程的末端，只是因为人们本来就最可能在那里转化（比如品牌词搜索）。它们在这些模型里拿到了功劳，却未必真的在创造需求。

**3. 把用户旅程过度简化**

一阶马尔可夫链假设下一步只取决于紧挨着的上一个渠道；Shapley值甚至根本不考虑时间顺序（它关心的是所有可能的子集）。现实要流动得多：品牌印象可能几周前就形成了，受到一些在分析数据里根本看不到的经历影响。任何把用户行为塞进一条整齐的链、或者一个整齐的集合组合里的模型，都很难体现长期的认知和那些无形的影响，结果是过度看重最近观察到的渠道。

**4. 隐藏的或外部的因素**

价格调整、竞争对手的动作、经济形势、季节周期，这些在用户级别的营销数据里通常都看不到，却能大幅改变转化结果。竞争对手的网站宕机了，你的转化涨了，数据驱动的模型可能就错误地把你的再营销广告封为功臣。如果数据集捕捉不到真正的原因，模型的结果在数学上看起来很扎实，却和转化暴涨真正的原因对不上。

**5. 分配结果不稳定**

当渠道之间相互关联，或者加入了一个新渠道时，Shapley值可能会大幅变动。如果某些渠道序列的数据很稀疏，马尔可夫链同样可能给出不稳定的归因。用户行为一点小小的变化，或者一个新活动上线，都可能让分配的功劳大变，模型给出的指引也就更难让人信任，更难在预算上一以贯之地使用。

**6. 实验仍然必不可少**

确定真实增量提升的最好方式，是A/B实验或地域级别的实验。马尔可夫链和Shapley值天生依赖事后的相关性，机器学习也只能去猜去掉一个渠道会怎样影响用户行为。真正的提升，需要主动对一个对照组停投营销，而这类大规模的测试执行起来可能很复杂。当实验结果和模型的说法冲突时，你就会清楚地看到，纯观察性的方法没法完全「证明」因果。

### 结论

尽管数学很优雅、看板很直观，一碰到现实世界的复杂性，**数据驱动的归因模型常常承诺得多、兑现得少**。它们能捕捉你现有数据里的相关性，却不一定能拆解出驱动用户决策的更深层的力量。追踪的漏洞、外部的影响，以及观察和因果之间根本的鸿沟，意味着这些模型通常给不出一张确定的营销花费路线图。

但也不是全无用处。只要清楚它们的盲区，谨慎地用，马尔可夫链、Shapley值和类似的机器学习方法，仍然能就用户路径、渠道之间的协同以及潜在的优化方向，提供**方向性的洞察**。把这些模型和设计良好的增量测试、对照实验，甚至自上而下的市场组合分析结合起来，可以互相校验、互相制衡。简单说，完美的归因不存在一种「即插即用」的方法。认识到数据驱动方法的局限，是明智地使用它们、专注于真正有价值的洞察的第一步。
