---
id: "statsig-blog-what-is-a-b-testing-and-why-is-it-important-zh"
title: "什么是A/B实验，它为什么重要？"
original_title: "What is A/B testing and why is it important?"
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
source_url: "https://www.statsig.com/blog/what-is-a-b-testing-and-why-is-it-important"
original_source_url: "https://www.statsig.com/blog/what-is-a-b-testing-and-why-is-it-important"
source_family: "https://www.statsig.com/blog/what-is-a-b-testing-and-why-is-it-important"
published_at: "2024-09-05"
original_published_at: "2024-09-05"
translation_publication_status: "repository-reading-aid-not-platform-publication"
source_context: "Chinese adaptation of a post Yuzheng published on the Statsig blog, rewritten by AI in his Chinese voice; the date is the English original's. Figures are reduced to captions."
attribution_note: "立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。"
---

<!-- provenance:start -->
> Attribution / 归属：立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。
<!-- provenance:end -->

# 什么是A/B实验，它为什么重要？

> **中文版** · 立正在Statsig博客发表的文章「What is A/B testing and why is it important?」的中文版，AI按他的中文习惯改写。按[立正参考使用许可](https://github.com/sunyuzheng/lizheng-open-context/blob/main/LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md)使用；图见[英文原文](https://www.statsig.com/blog/what-is-a-b-testing-and-why-is-it-important)。

- 原文标题：What is A/B testing and why is it important?
- 原文链接：https://www.statsig.com/blog/what-is-a-b-testing-and-why-is-it-important
- 发布日期：2024-09-05
- 作者：Yuzheng Sun（立正）

## A/B实验是获得证据最可靠的方式

A/B实验背后的概念是随机对照试验（randomized controlled trial，RCT），它是寻找因果关系的黄金标准。

下面是著名的[证据等级金字塔](https://www.researchgate.net/figure/Hierarchy-of-evidence-pyramid-The-pyramidal-shape-qualitatively-integrates-the-amount-of_fig1_311504831)。基本上，唯一比RCT更强的证据形式，就是对多个RCT做的元分析。争论的时候拿出一个RCT，争论基本就结束了。

> 证据等级金字塔（图见英文原文）
*图1　证据等级金字塔：从下往上依次是社论和专家意见、机理研究、病例报告和案例研究、横断面研究和调查、病例对照研究、队列研究、随机对照试验，最顶端是对RCT的系统综述和元分析。越往上，证据质量越高，偏差风险越低。图片来源：[ResearchGate](https://www.researchgate.net/figure/Hierarchy-of-evidence-pyramid-The-pyramidal-shape-qualitatively-integrates-the-amount-of_fig1_311504831)，原文引用。*

RCT的威力来自两个技术上的洞察：

1. **样本足够大的时候，随机化会把偏差抵消掉。**这就是大数定律。它保证了在大样本下，我们不需要操心两组在可观察和不可观察的变量上有什么差别，随机化会替我们处理好。
2. 在随机分组的前提下，实验组和对照组之间的差异是**由处理造成的**。

「由处理造成的」，这是一句非常强的话。在大多数比较里，也就是没有RCT的研究里，两组之间的差异通常是选择偏差造成的，而不是处理造成的。

举一个简单的例子，顺便说明什么是「随机分组」，以及它为什么重要。

## 用一个例子理解处理效应

假设我说我有一种神奇的药丸，一颗100美元，能让高中生一年多长1英寸（约2.5厘米）。我给你看我研究里的两组真实结果：

1. **实验组**：1000名一年前自愿吃了这种药的学生。一年前他们的平均身高是60英寸，今年是62英寸。
2. **对照组**：来自同一批学校、年龄相同的1000名学生。一年前他们的平均身高是60英寸，今年是61英寸。

我们能得出结论说这药有效吗？大家都知道这种神药不存在，但这个研究的漏洞在哪里？

漏洞是「选择偏差」。实验组里的人是（自己）选择进来的。自愿参加的人可能来自更富裕的家庭，因为他们买得起药；或者他们更想长高，除了吃药还试了别的办法。任何一个这样的因素，都会破坏这个研究里的因果关系。

但如果我们有2000名学生，随机决定谁吃药，就消除了选择偏差。根据大数定律，两组的各项平均指标（身高、家庭财富、身高的增长、想长高的程度，等等）应该是一样的，两组身高增长的差异就一定是由处理，也就是这颗药，造成的。

### 产品开发里的选择偏差

把这个例子放到产品开发里，就能看出，如果没有A/B实验的思维方式，我们每天都可能犯这样的错。比如：

**时间序列上的选择偏差：**

- **说法**：我们上线了一个功能，指标涨了10%。
- **现实**：没有这个功能，指标也会涨10%。比如在黑色星期五之前上线一个黑五活动的横幅。

**横截面上的选择偏差：**

- **说法**：我们上线了一个功能，用了这个功能的用户，指标涨了10%。
- **现实**：自己选择去用这个功能的那批用户，没有这个功能，指标也会涨10%。比如给重度用户加一个按钮（参考：[为什么大多数aha moment都是错的？](https://youtu.be/fuyXA7CXx-o)）。

## A/B实验是一种强大的衡量手段

除了因果，A/B实验本身也是一种强大的衡量手段。彼得·德鲁克说过：「无法衡量，就无法改变。」在管理摩擦很多的大公司里，这一点尤其明显。

[我们和Rec Room的客户案例](https://www.statsig.com/customers/recroom)就是很好的例子。他们做了一次很漂亮的界面改版，结果核心指标下降了30%以上。没有A/B实验，他们根本不会注意到。

> Rec Room改版前后的个人主页界面（图见英文原文）
*图2　Rec Room改版前（左）和改版后（右）的个人主页界面。新界面看起来更漂亮，却带来了核心指标的大幅下降。*

> Rec Room三个版本上线后的指标变化（图见英文原文）
*图3　Rec Room迭代过程中核心指标相对V0基线的变化：V1上线后跌到约−35%，V2上线后回升到约−20%，直到V3上线才超过基线。*

产品开发不是一锤子买卖，而是一个持续迭代、积累小胜利的过程。可如果你没法把赢和输区分开来衡量，你就赢不了。人们一开始做A/B实验就会发现，[自己70%到90%的想法其实是没用的](https://exp-platform.com/abtestingintuitionbusters/)。

所以，不做A/B实验的人，会在不知不觉中上线很多坏想法。

> 功能效果的分布与产品指标的长期走势（图见英文原文）
*图4　左：上线的功能里，有的达到了预期效果，有的需要继续迭代，有的应该关掉。右：如果把有负面影响的功能X、Y、Z都上线了，产品指标走的是下面那条绿红曲线；没上线它们，走的是上面那条黑色曲线。图片来源：Vineeth Madhusudanan，Statsig。*

简单说，A/B实验之所以强大、重要，是因为：

- 人很不擅长归因，而且受各种偏差的影响；
- 人很不擅长预测自己的想法会带来什么结果。

A/B实验提供了必要的衡量和因果，让我们对现实保持诚实。
