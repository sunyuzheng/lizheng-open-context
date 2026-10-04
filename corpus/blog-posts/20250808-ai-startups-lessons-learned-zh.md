---
id: "statsig-blog-ai-startups-lessons-learned-zh"
title: "被浪打翻，还是乘浪而起：从创业公司看AI产品怎样上线"
original_title: "Sink, swim, or scale: What startups teach us about launching AI"
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
original_author: "Alexey Komissarouk, Yuzheng Sun"
source_type: "blog-post"
source_url: "https://www.statsig.com/blog/ai-startups-lessons-learned"
original_source_url: "https://www.statsig.com/blog/ai-startups-lessons-learned"
source_family: "https://www.statsig.com/blog/ai-startups-lessons-learned"
published_at: "2025-08-08"
original_published_at: "2025-08-08"
translation_publication_status: "repository-reading-aid-not-platform-publication"
source_context: "Chinese adaptation of a post Yuzheng published on the Statsig blog, rewritten by AI in his Chinese voice; the date is the English original's. Figures are reduced to captions."
attribution_note: "立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。本文由Alexey Komissarouk和立正合著，文中的观点属于两位作者，不能整篇当作立正一个人的立场。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。"
co_authors: ["Alexey Komissarouk"]
---

<!-- provenance:start -->
> Attribution / 归属：立正发表在Statsig官方博客的英文文章的中文版：AI按立正的中文表达习惯完整改写，不是他亲笔的中文。本文由Alexey Komissarouk和立正合著，文中的观点属于两位作者，不能整篇当作立正一个人的立场。文中引用的他人观点和经历归原作者。具体说法请回到英文原文核对；原文和图片在Statsig博客。
<!-- provenance:end -->

# 被浪打翻，还是乘浪而起：从创业公司看AI产品怎样上线

> **中文版** · 立正在Statsig博客发表的文章「Sink, swim, or scale: What startups teach us about launching AI」的中文版，AI按他的中文习惯改写。按[立正参考使用许可](https://github.com/sunyuzheng/lizheng-open-context/blob/main/LICENSES/LicenseRef-Lizheng-Reference-Use-1.0.md)使用；图见[英文原文](https://www.statsig.com/blog/ai-startups-lessons-learned)。

- 原文标题：Sink, swim, or scale: What startups teach us about launching AI
- 原文链接：https://www.statsig.com/blog/ai-startups-lessons-learned
- 发布日期：2025-08-08
- 作者：Alexey Komissarouk（客座作者，增长工程顾问）、Yuzheng Sun（立正，Statsig数据科学家），按原文署名顺序
- 合著说明：本文是两人共同署名的文章，原文把Alexey标注为客座作者。文中的「我们」指两位作者，文中的观察和建议属于两人共同的总结，不应视为立正一人的观点。

> **关于客座作者**：Alexey Komissarouk是一位[增长工程顾问](https://alexeymk.com)，在Reforge上教[增长工程](http://course.alexeymk.com)课程，此前是MasterClass的增长工程负责人。

## 有的创业公司乘着浪冲向超高速增长，有的被AI掀起的大浪吞没

2025年3月7日，智能体助手**Manus.im**在X和Hacker News上一夜爆红。病毒式传播带来了巨大的早期关注，创始人们欣喜若狂，直到他们发现自己的GPU集群被汹涌而来的注册压垮了。公司冻结了邀请，围绕[Manus.im](http://manus.im/)的热度来得快，去得也快。

ChatGPT上线的时候没有设候补名单，因为OpenAI以为它只是一个研究演示，结果迎来了前所未有的需求。但他们扛住了需求。据ChatGPT负责人Nick Turley说，不设候补名单最后成了ChatGPT成功的关键因素之一，因为每个人都能看到别人怎么用，大家一起学。

这个对比抓住了AI时代增长的核心：有的创业公司乘着浪冲向超高速增长，有的被浪吞没。自[Friendster的年代](https://highscalability.com/friendster-lost-lead-because-of-a-failure-to-scale/)以来，还没有哪个本来领先的产品，是因为扛不住增长的流量而输掉的。当一家公司能不能规模化取决于大模型的算力时，从传统SaaS里总结出来的增长最佳实践，就得重新想一遍。

过去几年，我们的工作让我们和很多快速增长的AI公司有了密切接触。下面是我们到目前为止的观察总结：AI产品特有的四个关乎增长的挑战，以及怎样应对。

## 四个规律

### 1. 病毒式爆发的悖论

2021年2月，多伦多的创业公司**Wombo**发布了一款对口型app，结果「像火箭一样起飞」：第一个月下载2,500万次，十个月内7,400万次。这波暴涨让它的AWS账单「比（它）融到的所有钱还高一个数量级」，公司面临破产，直到[AWS出手](https://aws.amazon.com/startups/learn/how-aws-supported-wombos-wildly-popular-ai-powered-app?lang=en-US)，提供了额度和架构上的帮助。

#### 为什么重要

机会只有一次。如果你接不住快速增长的需求，就会失去网络效应、用来微调模型的新数据，以及千金难买的口碑背书。

#### 可执行的打法

别指望一成功就有Amazon来救你。应该提前在规模化准备上做那些投入产出比高的投资。具体来说：

- 事先和供应商谈好突发容量（spot GPU、备用云、经销商额度），这样几分钟内就能扩容，也不会收到意外的账单；
- 流量超出你的承受能力怎么办？提前想好，并上线一套[服务降级方案](https://aliceevebob.com/2017/04/25/service-degradation-actually-a-good-thing/)：缩短上下文窗口、压缩输出，或者进入排队模式，而不是直接报错；
- 产品能用了以后，可以考虑每个季度做一次「黑色星期五」演练：在压测环境里重放10倍于预期的流量，找出规模化的薄弱环节，包括登录认证和计费。

### 2. 用量和成本的螺旋

2023年3月，**Midjourney**叫停了非常受欢迎的免费套餐，[理由](https://www.theverge.com/2023/3/30/23662940/deepfake-viral-ai-misinformation-midjourney-stops-free-trials?utm_source=chatgpt.com)是「需求异常旺盛，以及试用被滥用」，甚至让付费用户也去排队。这次突然的暂停在Discord上引发了众怒，大量用户取消订阅，公司几周后不得不重新开放限流的访问。

#### 为什么重要

在传统SaaS里，随着用量增长，计算成本会变得越来越微不足道。但用大模型，推理成本直接随用户参与度增长，也就是说，你自己的增长可能把毛利率炸掉。突然涨价或者限流，会撕裂用户的信任，在你最需要推荐循环的时候让它哑火。

#### 可执行的打法

- 想一想，你的产品用量能不能按token或GPU秒来计量，而不是按自然月；如果按月固定收费仍然是最好的选择，可以考虑给低档付费套餐设明确的每月或每日用量上限；
- 提供一个「欢乐时光」式的非高峰套餐，吸收业余用户的流量，又不影响高级用户的响应速度；
- 接上一个单位经济的「熔断器」：如果每个用户的毛利跌破设定的底线，就自动关掉付费投放，并限制新用户注册，直到你扩充了供给或者提了价。

### 3. 提示词疲劳的新用户引导

2022年11月，**Notion AI**开放候补名单时，团队预计会有20万人注册。五周后，人数达到了一百万。但早期用户抱怨说，他们「还是不知道这东西能拿来干什么」。[Notion调整了方向](https://www.notion.com/blog/lessons-we-learned-from-launching-notion-ai)，从「AI替你写」转向「AI帮你改进你已经写好的东西」，重新设计了起步的提示词。探索的心理成本降下来以后，使用量上去了。

#### 为什么重要

你最有价值的用户不是提示词工程师。如果创造价值的过程像做作业，没完没了地试错写指令，激活就会停滞，口碑也就死了。

#### 可执行的打法

- 用按角色设计的起步选项和一键自动填充的示例，代替空白的提示词输入框；
- 把「重写提示词」和「撤销」这类事件当作挫败信号埋点，每周围绕它们做漏斗复盘；
- 提供一个「解释我上一条提示词」的开关，把试错变成有引导的学习。

### 4. 给一个结果有概率性的产品定价

Perplexity最初按token计量的API看起来很合理，却适得其反，让客户看到价格就被吓到，最终在2025年推出了[三档「搜索模式」](https://docs.perplexity.ai/guides/pricing)。

类似地，[Notion AI最初按用量付费的定价](https://www.notion.com/blog/lessons-we-learned-from-launching-notion-ai)，让测试版客户囤着额度不敢试，严重打击了使用。正式上线前几周，团队拆掉了按用量计费，换成一个简单的固定附加费，用不完美的单位经济换来更快的习惯养成。

#### 为什么重要

AI的用量忽高忽低，用户也不熟悉；他们没法预测自己会烧掉多少token。如果定价让人感觉像高峰溢价，探索就停了，升级率也就平了。

#### 可执行的打法

- 财务上可行的话，先用一个固定价格的套餐，消除用户心里的交易成本；等用户真的碰到上限了，再叠加按用量计费的超额部分；
- 把「到目前为止烧了多少token」直接显示在界面里，而不是藏在计费后台；
- 价格敏感度实验要在*已经用起来*的用户群上做，而不是在漏斗顶端的新注册用户上做。用户要先觉得自己用熟了，付费意愿才会跟上来。

## 凡事适度，包括适度本身

说到底，死于没人关注的创业公司，远比死于关注太多的多。别把这些建议当成「上线之前先把一切准备到能扛互联网级流量」的理由。不管是不是AI，创业公司的第一要务，始终是做出人们想要的东西。

不过，只要在定价、易用性和规划上做一些有策略的投入，AI创业公司就能做好准备，乘上关注的浪潮，而不是被浪打翻。
