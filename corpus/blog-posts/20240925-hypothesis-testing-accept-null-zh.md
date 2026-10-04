---
id: "statsig-blog-hypothesis-testing-accept-null-zh"
title: "做假设检验，为什么你应该「接受」原假设"
original_title: "Why you should \"accept\" the null hypothesis when hypothesis testing"
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
source_url: "https://www.statsig.com/blog/hypothesis-testing-accept-null"
original_source_url: "https://www.statsig.com/blog/hypothesis-testing-accept-null"
source_family: "https://www.statsig.com/blog/hypothesis-testing-accept-null"
published_at: "2024-09-25"
original_published_at: "2024-09-25"
translation_publication_status: "repository-reading-aid-not-platform-publication"
source_context: "Chinese adaptation of a post Yuzheng published on the Statsig blog, rewritten by AI in his Chinese voice; the date is the English original's. Figures are reduced to captions."
attribution_note: "立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。"
---

<!-- provenance:start -->
> Attribution / 归属：立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。
<!-- provenance:end -->

# 做假设检验，为什么你应该「接受」原假设

> **中文版** · 立正在Statsig博客发表的文章「Why you should "accept" the null hypothesis when hypothesis testing」的中文版，AI按他的中文习惯改写。按[立正参考使用许可](https://github.com/sunyuzheng/lizheng-open-context/blob/main/LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md)使用；图见[英文原文](https://www.statsig.com/blog/hypothesis-testing-accept-null)。

- 原文标题：Why you should "accept" the null hypothesis when hypothesis testing
- 原文链接：https://www.statsig.com/blog/hypothesis-testing-accept-null
- 发布日期：2024-09-25
- 作者：Yuzheng Sun（立正）

「原假设永远不能被接受！只能说无法拒绝！」这句话流传很广，但它根本上是有问题的。

这个误解让很多人，甚至包括资深的统计学家，对假设检验的本质感到困惑。

> 关于能否接受原假设的投票（图见英文原文）
*图1　一个关于「你能接受原假设吗？」的投票：45票里，89%选「不能，只能说无法拒绝」，4%选「能」，7%选「看情况」。*

这篇文章把这件事讲清楚：

1. 这个误解是从哪来的；
2. 为什么大家认为不应该接受原假设；
3. 为什么、以及在什么情况下，你其实应该接受它。

## 这个误解从哪来

根源在于，现代教科书经常把Fisher的显著性检验和Neyman-Pearson的假设检验混在一起讲，却不解释两者之间的关键区别（[参考](https://en.wikipedia.org/wiki/Statistical_hypothesis_test)）。

这就像把两种运动的规则搅在一起。能不能用手碰球？要看你打的是篮球还是足球。在篮球场上说「用手碰球犯规」，毫无道理；可在假设检验框架下宣布「接受原假设是错的」，本质上就是在干这件事。

那么，你到底能不能「接受」原假设？在Fisher的框架里，不能。在Neyman-Pearson的框架里，能，而且必须。

## 在Fisher的框架下，为什么「接受原假设」不好

第一，光凭观察，我们永远没法确定地「证明」一个假设。因为对任何一个观察，可能为真的假设都有无穷多个，只是各自的概率不同。

第二，在严格的Fisher p值框架里，根本没有备择假设。我们可以给拒绝原假设定一个阈值（比如p < 0.05），但如果没能拒绝原假设，并没有一条同样清楚的规则告诉我们该「接受」哪个备择假设。Neyman-Pearson框架就不一样，那里有一个具体的备择假设，以及它对应的具体的β。

第三，Fisher本来的立场就是，我们不应该把原假设当作百分之百确定为真。事实上，他并不支持一个固定的显著性水平（比如0.05），而是主张把p值看作一个连续的、反对原假设的证据强度。

总结一下，在p值框架里说「接受一个假设」，危险在于：

- 很多人会把「接受」原假设误读成「证明」了原假设，这是错的；
- 「接受原假设」不是一个有严格定义的概念，而且偏离了检验的核心目的：根据观察，决定要不要拒绝原假设。

所以，在Fisher的p值框架里，说「接受原假设」基本上是不成立的。但要注意，**备择假设、α、β、power和最小可检测效应（MDE）这些说法，在这个语境里同样不该出现。**如果有人一边用这些词，一边又说接受假设是犯规的，那这个人自己就不一致。

## 在Neyman-Pearson的框架下，为什么「接受原假设」是必要的

在Neyman-Pearson框架里，「接受」原假设和备择假设，不仅是允许的，而且是必要的。不过，**「接受」一个假设，不代表你相信它，只代表你按它为真来行动。**

回想一下，做假设检验的时候，我们能把原假设和备择假设画出来，精确地算出α和β。如果不暂时假定其中一个假设为真，这一步根本做不了。

Neyman-Pearson框架，也就是通常说的假设检验框架，是一套数学上自洽的方法，把观察、假设和决策规则连在一起，同时算出相关的概率。我有一期[15分钟的视频](https://youtu.be/9q1Tn1HnY6I)，配了很多可视化，一步步带你走一遍这个框架。如果你曾经被教科书搞糊涂过，强烈推荐看一看。

## 选读：Fisher的框架和Neyman-Pearson的框架

如果你是第一次听说这是两套不同的框架，请先暂时忘掉你学过的东西，把这两套框架当成篮球和足球。下面是两者的对比。

### Fisher的框架

- **重点是显著性检验**：Fisher提出了显著性检验的概念，主要目标是判断观察到的数据是否提供了足够强的证据，让我们拒绝原假设。
- **原假设是默认的出发点**：在Fisher的方法里，原假设（H₀）代表一个默认的立场：没有效应，或者没有差别。它是一个具体的假设，检验它的时候不一定要指定备择假设。
- **p值是核心**：p值衡量的是，假设原假设为真，观察到和眼前一样极端、甚至更极端的数据的概率。p值越小，反对H₀的证据越强。
- **没有固定的显著性水平**：Fisher不主张一个固定的显著性水平（比如0.05），而是建议把p值解读为反对H₀的连续的证据强度。

### Neyman-Pearson的框架

- **把假设检验当作决策**：Neyman和Pearson把假设检验形式化为在两个相互竞争的假设之间做决策的过程：原假设（H₀）和备择假设（H₁）。
- **原假设和备择假设对称对待**：H₀和H₁都有明确的定义，检验的设计就是根据数据在两者之间做出选择。
- **控制错误率**：这个框架引入了第一类错误（H₀为真时拒绝了H₀）和第二类错误（H₁为真时没能拒绝H₀）。显著性水平（α）和power（1−β）都是事先定好的，用来控制这两种错误率。
- **用临界区域做判断**：Neyman-Pearson的方法不用p值，而是基于似然比或检验统计量，用临界值和临界区域来决定是否拒绝H₀。

## 两套框架定义原假设的主要区别

1. **目的和解读**
   - *Fisher*：原假设是一个有待检验的临时假定。它不一定要被明确地接受或拒绝，而是用来衡量反对它的证据有多强。
   - *Neyman-Pearson*：原假设是两个相互竞争的假设之一，检验程序的设计目的，就是在控制错误概率的前提下，对接受还是拒绝H₀做出明确的决定。
2. **备择假设的角色**
   - *Fisher*：备择假设往往是隐含的，或者没有正式指定，重点在于评估反对H₀的证据。
   - *Neyman-Pearson*：备择假设（H₁）有明确的定义，检验就是为了区分H₀和H₁而构造的。
3. **做决策还是评估证据**
   - *Fisher*：强调衡量反对H₀的证据，不一定要做出最终的决定。
   - *Neyman-Pearson*：强调在H₀和H₁之间做出决定，并把长期来看各类错误发生的频率考虑进去。

## 小结

- **Fisher的原假设**：一个独一无二的具体假设，检验的是有没有显著的证据反对它，用p值来衡量证据。
- **Neyman-Pearson的原假设**：决策框架里两个明确定义的假设之一，检验的设计目的是控制错误率，并在H₀和H₁之间做出选择。

**参考文献：**

- Fisher, R.A. (1925). *Statistical Methods for Research Workers.*
- Neyman, J., & Pearson, E.S. (1933). "On the Problem of the Most Efficient Tests of Statistical Hypotheses." *Philosophical Transactions of the Royal Society A*, 231(694-706), 289-337.
