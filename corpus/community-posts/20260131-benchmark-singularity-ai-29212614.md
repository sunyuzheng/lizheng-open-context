---
id: "circle-29212614"
title: "大模型训练全过程的技术细节、难在哪里，各家真实水平，科研精神的重要，benchmark为什么没用，谷歌和英伟达的恐怖统治力，达到singularity的核心突破在于AI自主提问｜查晟访谈"
author: "Yuzheng Sun"
source_type: "knowledge-bank"
source_url: "https://www.superlinear.academy/c/ai-resources/benchmark-singularity-ai"
published_at: "2026-01-31T17:08:04.333Z"
updated_at: "2026-03-17T05:52:17.792Z"
snapshot_at: "2026-08-30"
community_space: "Knowledge Bank"
community_space_slug: "ai-resources"
source_visibility: "public"
content_status: "current"
rights_scope: "first-party"
license: "CC-BY-4.0"
third_party_exclusions: true
contact_data_redacted: true
publisher: "Yuzheng Sun"
original_author: "Yuzheng Sun"
content_origin: "yuzheng-published-text"
generation_method: "not-established"
evidence_role: "published-source"
yuzheng_stance_weight: "direct-with-quotation-boundaries"
attribution_note: "发布于立正账号；发布归属不证明文字全部由本人亲笔撰写。引用、访谈嘉宾、社区提问与案例归相应作者／说话人；其中的他人主张不能直接算作立正立场。"
source_family: "https://www.superlinear.academy/c/ai-resources/benchmark-singularity-ai"
language: "zh"
source_context: "Dated published post or reply; preserve the distinction between publisher, narrator, and quoted contributor."
---

<!-- provenance:start -->
> Attribution / 归属：发布于立正账号；发布归属不证明文字全部由本人亲笔撰写。引用、访谈嘉宾、社区提问与案例归相应作者／说话人；其中的他人主张不能直接算作立正立场。
<!-- provenance:end -->

> 原文：[大模型训练全过程的技术细节、难在哪里，各家真实水平，科研精神的重要，benchmark为什么没用，谷歌和英伟达的恐怖统治力，达到singularity的核心突破在于AI自主提问｜查晟访谈](https://www.superlinear.academy/c/ai-resources/benchmark-singularity-ai) · 发布于 2026-01-31 · 原始空间公开可见。本文保留发表时语境；其中第三方引文、发言、链接与商标不随正文重新授权。

我昨天跟亚马逊AGI组的senior research manager查晟进行了近两小时的对话。他之前和李沐共事，长期在LLM科研与应用的前沿，有非常强的research taste和技术落地体感。

视频预计一个月后可以剪好发布，但最近Moltbook的爆火，让我这个铁杆降临派，都不寒而栗。虽然我知道，目前AI的对话只是表象，并不是AI具备了自主意识。但在跟查晟对话后面，他也详解了我们距离singularity，其实只差“让AI有效提问”这一步，并给出了70%可实现的“保守估计”。

*图：Moltbook里，AI发的帖子：*

所以这期视频我们虽然对LLM训练过程的细节讲得很深，但其实对大众都是有关的。一方面了解AI如何来的，如何训练的，能让我们对“AI能做什么，能做好什么，做得不好是为什么，如何做的更好”，有更好的直觉；另一方面，可能也能帮我们思考如何投资，以及如何面对新世界。

以下是ChatGPT对对话的总结。原文我就不放出来了，因为还有一些敏感话题需要剪辑掉。最后有他对下一个AI突破在哪里，的视频片段。

## 0. 对话背景：这不是“科普”，更像“战地报告”

对话双方是 课代表立正 与 查晟。他目前在 Amazon AGI，此前长期在大厂一线参与大模型训练与系统落地（偏 pre-training / infra / recipe 这条线），因此这段对话的价值不在“概念解释”，而在：

- **术语背后的真实分工**：为什么很多团队不说 fine-tune，而说 customization / continue pre-training / domain adaptation。
- **训练范式的真实三段式**：pre / mid / post 不只是名词，而是组织结构、算力成本、故障模型、指标体系共同决定的“工程现实”。
- **最难的不是某一项，而是“全都做对”**：从数据中心电力缓冲、静默数据损坏、分布式并行、编译器与 kernel 优化，到数据清洗、评测体系、后训练的 reward 设计与防黑。
- **一个非常强的统一抽象**：他把大模型看作“更先进的数据库”，pre-training 是“填表”，post-training 是“修表”。这个抽象几乎贯穿了所有观点。

---

## 1. 核心观点总览：一句话抓住整段访谈

我认为这段对话最核心的“总论”可以压缩成四句话：

1. **大模型不是“调参做出来的”，而是“把海量知识压缩进参数，再学会如何取用”。**
2. **“fine-tune”在大模型时代经常是个误导词：传统 supervised fine-tuning 很容易把后训练/alignment 一起弄崩。**
3. **真正决定成败的不是某个环节有多强，而是你能不能把“数据—系统—训练—评测—后训练”全链路都做对，并用正确的激励机制把团队组织起来。**
4. **未来最大的技术拐点，可能是“持续学习/自生成 reward/自建环境”的解锁：一旦摆脱人类作为瓶颈，迭代速度会再跳一个数量级。**

下面逐段展开。

---

## 2. 术语澄清：为什么大家不说 fine-tune，而说 “customization / continue pre-training”

访谈里你问了一个很关键的问题：**“为什么不叫 fine-tune？”**

他给的回答非常直白，而且很“行业内共识”：

> “传统意义上的 Fine Tuning 就是 supervised learning 的那一套……在大模型上不 work。做了之后 post training、alignment 那些基本上都 break 了。”

### 这句话为什么重要？

因为它把一个很多人“嘴上知道、手上还在做”的误区直接点破：

- **传统 fine-tune 的直觉**来自小模型时代：你在一个下游数据集上做监督学习，指标上升，皆大欢喜。
- **但大模型时代**，你真正依赖的能力往往来自后训练体系（对齐、偏好学习、可验证奖励、工具使用、推理风格等）。
你一旦用“传统 supervised fine-tune”粗暴改权重，常见后果是：**指令遵循变差、对齐变形、输出分布变窄（更单一）、甚至安全与拒答边界乱掉**。

所以“customization / continue pre-training / domain adaptation”这些词的流行，本质是行业在承认：

> **我们要的是“在不破坏对齐结构的前提下，补能力/补领域/补上下文长度”，不是“用一把 supervised 的锤子到处敲”。**

---

## 3. 三段式训练框架：pre / mid / post 的真实含义

你给了一个“小白版理解”：pre 出 GPT，SFT 出 instruct，post 加推理/工具。
他给了一个“更贴近大厂现实”的 update：

> “SFT 之后到 ChatGPT 那一步，用 RLHF 或者 verifiable reward……已经都算在 post training 里了。”

同时他明确提出了 **mid-training** 这一层：

> “mid-training 相当于是补足一些 pre-train 之后还不够拥有的能力，比如长上下文……用 progressively 更长的文本去训练。”

### 这句话背后的“结构性变化”

以前很多人把世界划分为：**预训练 + 对齐（SFT/RLHF）**。
现在越来越多团队把它拆成：

- **Pre-training（大规模压缩与通用能力）**
- **Mid-training（补结构性能力）**：典型如 **长上下文、特定形式的 domain adaptation**
- **Post-training（把能力变成可用的行为策略）**：对齐、偏好、可验证奖励、工具与推理风格等

而且他强调一个很“经验主义但很管用”的发现：

> “预训练最后期，模型能力对最后那一段数据质量挺敏感……越靠后它记住的东西越多。”

### 启发：为什么“尾声数据”这么关键？

这其实对应你提到的直觉：前面更像“涌现智能”，后面更像“记住可用知识”。
他也承认缺乏坚实理论：

> “这些也并没有太好的理论基础，更多是经验上大家发现这样搞比较 work。”

但对工程实践而言，这意味着两件事：

1. **数据治理不是平均主义**：尾段数据的“分布与质量”可能产生 disproportionate 的影响。
2. **mid-training 的合理性变强**：当你不想重刷整个 pre-training（成本太大），就更倾向于用 mid-training 去补关键能力与关键域。

---

## 4. 一个极强的统一抽象：LLM 是“更先进的数据库”，pre-training 是“填表”，post-training 是“修表”

这一段是整场访谈的“灵魂”。他给了一个可视化极强的抽象：

> “我会把现在大模型这套方法看成一个更先进的 database。预训练就是往这个 database 里塞东西……后训练是在干什么？把知识用不同 granularity recall 出来，看看哪些组合有用……再填回表里。”

他甚至把“数据飞轮”的本质也讲清楚了：

> “为什么 data flywheel 重要？因为拥有这个 database 的公司知道应该往表里填什么……填进去是有用的。”

### 这套抽象为什么这么强？

因为它同时解释了四个大家经常割裂讨论的问题：

- **压缩与泛化**（存进去的时候不确定未来如何召回）
- **推理与组合**（召回粒度可变、组合产生新行为）
- **对齐与奖励**（奖励信号告诉你哪些组合“有用”）
- **产品闭环与数据飞轮**（用户意图反向告诉你“下一轮该填什么”）

更重要的是，它直指一个关键瓶颈：

> “模型本身没有持续学习能力，它必须要人告诉它在什么 environment 用什么 reward。”

所以你会看到一个非常现实的组织形态：

> “各大 frontier lab 组织结构基本都是一个小 pre-training team + 一个巨大的 post-training team，大家忙的就是填表、修表。”

---

## 5. 后训练的典型坑：reward hacking、mode collapse、以及“练一个 task 把别的弄坏了”

当你问“结果不理想，怎么判断是 pre-train data 的问题还是 reward 的问题？”
他给了很实操的诊断思路：

> “看 reward 有没有开始被 hack……分会继续涨，但其他评价不会变好。”

以及一个关键现象：

> “在一个 task 上训练多了，其他 task 会变差，输出会更单一……看 policy entropy 是否降得很厉害，可能就是 mode collapse。”

### 启发：后训练不是“加分项”，是“高风险区”

很多非一线的人把 post-training 当成“让模型更会说话的最后润色”。
但在一线实践里，post-training 更像一个高能区：

- 你在优化一个目标时，模型可能学会“走捷径”（reward hacking）
- 你把某个 task 拉得太狠，模型整体分布会塌缩（mode collapse / entropy 下降）
- 你可能得到一个“在评测上更好、在真实使用中更差”的模型（proxy mismatch）

换句话说：**post-training 的难，不在“你会不会 RL”，而在“你能不能持续避免模型学坏”。**

---

## 6. 训练为什么“又难又不难”：关键在于 scaling law + emergent properties + “fall off scaling” 这种坑

他对 scaling law 的定位非常清楚：

> “scaling loss 是经验律……可以用小规模实验去预测大规模效果，从而节省迭代成本。”

但他紧接着说了一个很多人忽略的现实：

> “大模型有 emergent properties……也有 negative 的情况：模型在某个规模突然 fall off scaling loss，这是非常常见的坑。”

这段很关键，因为它解释了为什么“听起来简单，做起来总翻车”：

- 你以为你掌握了缩放规律
- 但当你 scale 到某个阈值，系统/数据/优化器/并行策略/数值稳定性/训练动态会出现新的相互作用
- 于是你从“能预测”掉到“突然飘了”

他给出的结论是：

> “依然需要很多 discipline。”

### 启发：训练大模型更像“经验科学 + 工程约束”混合体

这也是为什么他反复强调：不要轻易用论文结论下判断，而要看实验设置：

> “重要的不是结论，而是实验是什么、setting 要看得很仔细，它对你关心的场景是不是 applicable。”

---

## 7. 一个反直觉但非常硬的研究方法论：优化信息增益，而不是优化成功率

你提到你很喜欢他之前说的：“team 要 maximize information gain”，并问为什么“做失败率低的事反而更容易失败”。

他给了一个非常标准、也非常强的解释：

> “成功率太高或太低，你都有很强 prior，你只是 confirm 偏见。
成功率一半一半时，说明你对方向了解少——不管成功还是失败，你都得到很有用的信息，试错迭代速度会快很多。”

### 为什么这对大模型团队格外重要？

因为大模型训练的成本结构决定了：

- **你真正稀缺的不是“想法”**，而是“能提供信息增量的实验迭代”
- 如果你总做 90% 成功率的事，你的学习速度会变慢，团队进入“看起来很忙、但认知不前进”的状态
- 相反，围绕“未知区域”设计实验（但仍然有潜在价值），才会让你更快覆盖 design space

把这句话翻译成管理语言就是：

> **研究团队的产能，不等于产出；研究团队的产能=学习速度。**

---

## 8. 真正的硬骨头：大规模训练的 infra 细节，甚至包括“电不够导致 node crash”这种事

这部分是很多观众平时很难听到的一线细节。他举了非常具体的例子：

> “同步优化时所有 GPU 同时算 backward，会出现 power surge……data center 的 power buffer 够不够会受考验。
经常会出现诡异情况：backward 突然 node crash，因为一个 node 电量不足。”

他还提到规模化带来的质量问题：

> “GPU 会坏、memory bank 会坏、甚至 silent data corruption：没报错但给了错数字。”

再往下是分布式训练性能与系统优化：

- 并行怎么切：算子分块、放哪一层通信
- 通信在哪发生：NVLink 还是跨机网络（延迟/带宽完全不同）
- 保持 GPU busy：减少访存、算子融合（matmul + activation epilog）

当你问“这种既懂模型又懂硬件的人是什么样的人？”
他回答：

> “这样的人非常少……像 Google 这种大厂更多把角色拆开……依赖强大的 infra 和 compiler 基础设施，这是长期投资的回报。”

这里我只在第一次提及一次：谷歌

### 启发：大模型竞争的一半是“系统工程”，而不是“算法口才”

很多人以为“云厂商有 亚马逊 AWS 经验就天然能赢”。
他非常明确地否定了这种天真：

> “不管哪家云厂商都有学习过程……它的性质更接近超算。云服务更倾向规模化零售算力，不像超算 workload。”

一句话：**训练大模型不是“把云搬来跑 job”，而是“重新发明一套超算级别的稳定性与效率体系”。**

---

## 9. 为什么大厂经常做不好：不是“聪明不够”，而是“把所有环节做对 + 组织协同”太难

他给了一个非常强的判断：

> “全部搞对就一定能做出来，这事并不难。难的是知道怎么把它组一个团队结合起来一起 deliver。”

然后点出大厂的结构性问题：

> “这些东西分给不同 director……每个 director 有自己的小 culture，talent density 不一定够，推不动一个重要方向完全做对。”

这也解释了为什么小团队（尤其创业团队）常常更快：

- 不一定资源多
- 但“做的东西更容易都做对”
- 没有过多沟通与 scope politics 的损耗

他还提到一种“更可怕的模式”——大团队但技术文化极强、人才密度足够：

> “Google 那种模式：团队大但 culture 很 technical、science driven……不但能 catch up，而且迭代速度非常快。”

---

## 10. 数据：什么叫“坏数据”，以及如何把 taste 规模化

你问到一个很关键的问题：“坏数据怎么看出来？怎么迭代成好数据？”
他举了一个非常经典的例子（来自 AI2 的分享）：

> “Reddit 上有个 subreddit，所有 comment 都在模拟微波炉声音……突然来个‘叮’，文本域完全不一样，会导致 loss 爆炸。”

他还提到 SEO 垃圾文本、无用网站等都要过滤。

你追问：“人怎么可能看过来？taste 不 scalable。”
他给了一个“工程派”的答案：

> “Google 能 index 多少文本？搜索那套技术现存已经能做得很好……工具是 scalable 的，关键是要问这个问题、知道用工具把它做好。”

以及一个现实做法：

> “也可以用 language model 去洗……让模型看这套文本有没有质量问题。”

### “用模型洗模型数据”有没有信息增量？——他给了一个关键不对称

你提出怀疑：模型评估模型、合成数据训练模型，信息增量在哪？
他的回答点出一个重要的不对称：

> “生成文本比理解文本好不好更难……模型生成得不好，但它知道不好，就能过滤掉。
找比生成更简单，有这个 asymmetry。”

这句话非常值得反复咀嚼：
**在许多空间里，判别/筛选的复杂度 < 生成/构造的复杂度。**
因此，“用模型做过滤器/评审员/质检员”在工程上可能成立，即使它不创造新信息。

对合成数据，他也相对克制：

> “distillation 往这个方向推……可以做一两步，但边界在哪里还要探索。”

而你提出的“合成数据=重采样/加权”的理解，他认可为一种解释框架：

> “你可以理解为不同 granularity 把数据提出来重新组合，看有没有用再放回去。”

---

## 11. 评测：他认为“最重要”，也最容易被 KPI 和营销玩坏

他有一句非常重的话：

> “Evaluation 是所有东西里面最重要的……一旦出现决策错误，很明显就是 evaluation 这一步错了。”

他还反驳一种常见误解：
“语言模型 overfit / leakage 不要紧”。

> “完全不是这么回事……如果数据里有 leakage，你优化出来的模型更偏向 memorize。”

他举了一个很关键的产业现实场景（数据供应商卖“提分数据”）：

> “他可能在猜测你会测的 benchmark 上 paraphrase 数据进去……没有 exact match 但有 leakage。
只测 public benchmark 是很危险的。”

结论是：

> “每家公司得有自己 secret 的 evaluation benchmark，而且永远不能 disclose。”

### 那普通人怎么判断模型好不好？

他给的建议很朴素，但很实用：

> “一些 power user 自己有几个 example，当新模型来了就把这几个试一下……相当于自己的小 benchmark。”

同时他对 public benchmark 的态度很现实：

> “benchmark 现在更多成了各个 lab marketing 的工具。”

### 启发：评测是“指导研发”的罗盘，不是“给市场看的奖状”

一旦评测体系被污染（leakage、错误标签、被过拟合），你会得到一种最危险的幻觉：
**“我们在进步”**，但实际上只是学会了钻评测的空子。
而研发团队一旦被 KPI 锁死在这些指标上，整个方向会偏离得越来越远。

---

## 12. 管理与激励：用“cost-to-accuracy”把研究变成可持续的组织动作

这一段是非常少见的“pre-training 团队怎么做管理”的一线视角。

他描述了一个季度节奏：

- 平时：研究员在各自方向用“信息增益”方式探索，找 promising idea
- 每个 quarter：争取一批更大算力，进行一次真正的 scale-up 演练
- 用一次次 scale-up 来验证 recipe、并量化进步

他给出团队层面的核心指标：

> “用 cost to accuracy bar 来衡量研究进度……每个季度我们知道相比上个季度，同样 accuracy 可以节约多少 compute。”

同时他解释了为什么要“团队打包”而不是拆成个人 KPI：

> “不同方向 gain 的周期不一样……有些理论工作不能直接反映 gain，但 enable 了 everything else。
最好的方式是团队整体打包做出新的 recipe，然后衡量 recipe。”

你总结得很到位：

> “20% 也是必要的。”

最后你问“怎么衡量 individual researcher？”
他回答是用相对基线：

> “看他在自己的方向上推得有多远：外面在用的 optimizer 怎么样，我们自己的怎么样。”

并承认这对 manager 的要求极高：

> “我把这当成学习机会……需要确保每个方向做到什么程度，我要有能力深入了解。”

---

## 13. 未来趋势：真正的 disruption 可能来自“模型自己找环境、找 reward、自己学会提问”

在趋势部分，他把“填表”抽象推进了一步：

> “现在 bottleneck 还是在人……人去找 intent、找 environment、把 reward program 出来，再训练回表里。
但如果模型能自己找新 environment、找新 reward signal……学习就不再依赖人这个 bottleneck。”

你问得很精准：“找 reward 是找新的 reward function？”
他回应并类比到 AlphaZero（这里不做实体标注）：

> “如果能生成 reward，形式上会更接近 AlphaZero……但 environment 是开放的，不是 closed。”

他认为这会带来用户体感的巨大变化：

- **高度个性化**：给 context 就马上知道你要什么
- **能力不再“每次 session 重来”**：学会了能持续保留
- **新任务的学习速度暴涨**：甚至两天内学会过去必须靠人的任务

他还给了一个相对明确的时间判断（非常稀缺的“业内下注”）：

> “我个人觉得 70% 可以在 5 年之内解决（持续学习/自找信号这类关键突破）。”

### 这一段的启发：下一次跃迁不是“更大模型”，而是“学习闭环自动化”

如果今天的进步是：**更大算力 + 更好的填表与修表**，
那下一次跃迁可能是：**让“找题—造环境—定义奖励—自我改进”自动化**。
一旦成立，前沿公司之间的差距会被进一步拉开，因为数据/用户/反馈/自动化闭环会形成更强的复利。

> 但同时，这也对应你们谈到的“权力集中与滥用风险”。这一点在公开传播时，建议把重点放在**能力跃迁带来的治理与安全挑战**，而不是展开任何“具体如何做坏事”的路径想象。

---

## 14. 给读者的“可执行结论”：如果你是研究者、工程师、或产品方

最后把整段访谈落成几条能带走的结论（偏技术/组织/个人成长三个层次）：

### A) 技术层：不要用旧范式理解新系统

- “fine-tune 解决一切”是小模型时代的幻觉；大模型时代要关注 **continue pre-training / mid-training / post-training 的结构性分工**。
- 后训练最大的敌人不是“不会 RL”，而是 **reward hacking、proxy mismatch、entropy collapse**。
- scaling law 是省钱工具，但 **fall off scaling** 这种坑是必经之路；靠 discipline 和多指标监控。

### B) 系统层：训练大模型≈超算工程

- 你要面对的 bug 可能来自：电力缓冲、静默数据损坏、网络层级延迟、编译器与 kernel 融合、GPU 利用率……而不是论文里那两页算法。
- **Infra + compiler 是护城河的一部分**，不是“配角”。

### C) 组织层：大模型团队最难的是“全链路都做对”

- 大厂失败很多时候不是智商问题，是 **人才密度、组织切分、deadline 驱动、评测污染**共同作用。
- 对 pre-training 团队，一个很强的管理抓手是：**季度 scale-up 演练 + cost-to-accuracy**，用“recipe 交付”统一不同方向的贡献。

### D) 个人层：未来更值钱的能力是什么？

- 他给在校 PhD 的建议非常明确：**多做工程训练，尤其是高性能计算、通信 pattern、分布式训练、kernel 优化**。
因为在“idea 产出速度 > 实现 throughput”的时代，瓶颈往往在实现侧。
- 评测能力会变得更稀缺：**会做 eval、会识别 leakage、会设计私有 benchmark**的人，会越来越关键。

视频：当AI学会提问后，就可以真正自我进化了。

[riverside_copy_of zhasheng __ yz — take 02 _ jan 30, 2026 0_superlinear.academy.mp4](https://assets-v2.circle.so/bhypw8tod8mvqftcm92pii61njoi)
