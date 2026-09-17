---
id: "circle-36336024"
title: "Intake Skill：用好苹果设备，把上下文留在自己手里"
author: "Yuzheng Sun"
source_type: "community-post"
source_url: "https://www.superlinear.academy/c/tools/intake-skill-apple-voice-memos-context"
published_at: "2026-09-10T16:49:02.143Z"
updated_at: "2026-09-13T12:50:14.972Z"
snapshot_at: "2026-09-17"
community_space: "Toolbox"
community_space_slug: "tools"
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
source_family: "https://www.superlinear.academy/c/tools/intake-skill-apple-voice-memos-context"
language: "zh"
source_context: "Dated published post or reply; preserve the distinction between publisher, narrator, and quoted contributor."
---

<!-- provenance:start -->
> Attribution / 归属：发布于立正账号；发布归属不证明文字全部由本人亲笔撰写。引用、访谈嘉宾、社区提问与案例归相应作者／说话人；其中的他人主张不能直接算作立正立场。
<!-- provenance:end -->

> 原文：[Intake Skill：用好苹果设备，把上下文留在自己手里](https://www.superlinear.academy/c/tools/intake-skill-apple-voice-memos-context) · 发布于 2026-09-10 · 原始空间公开可见。本文保留发表时语境；其中第三方引文、发言、链接与商标不随正文重新授权。

如果大家平时需要把线下聊天、会议里说的话，整理成 AI 可以使用的上下文，最好的方式往往不是再买一个录音豆或者专门的硬件，而是先把手上的苹果设备用好：Apple Watch、手机和电脑。

这样做有三个好处。

**第一，录音和同步的质量、可靠性都很好。**苹果已经把这些基础能力做得很成熟，平时顺手录下来，录音自动同步到电脑，整个过程很无感。

**第二，上下文自己掌握。**音频、转录和整理结果都作为自己的文件保留下来。无论模型和硬件以后怎么换，我们都能保留这份最重要的资产，不把自己的积累锁在某一个产品或生态里。

**第三，可以自由叠加自己想做的事。**从搜索、回顾讨论，到整理会议笔记、写文章，都可以在这些材料上继续做，根据自己的需要增加功能。

我自己用的是苹果原生的语音备忘录，加上鸭哥的 Intake Skill。苹果负责录音和设备同步，Intake 接着转录、整理，把日常说过的话变成以后还能继续使用的上下文。按照[鸭哥的理念，这个skill是一个种子](https://www.superlinear.academy/c/tools/superlinear-skill-registry)，你应该拿着这个skill，跟AI一起，改成适合你自己的版本。

先看实际怎么用。出去聊天，手表已经戴在手上。我把 Apple Watch Ultra 的操作按钮设成了“语音备忘录”，按一下就开始录音，回到表盘也可以继续录。

手机和电脑也是一样，打开苹果自带的语音备忘录就能录。聊天时把手机放在合适的位置，坐在电脑旁就直接用 Mac，选当时最顺手、能把话录清楚的那个。

设备登录同一个 Apple 账户，并打开[语音备忘录的 iCloud 同步](https://support.apple.com/guide/voice-memos/see-your-recordings-on-all-your-apple-devices-vma6cc4d0571/mac)，录音就能汇集到 Mac 上。下面这张图里，Mac 上的 **Recording 104，就是刚才视频中在手表上开始录的那一条**，时间也是上午 9:17。录完以后，不需要再手动发给电脑。

录音到了 Mac，Intake 接着把它收进按日期组织的本地目录，用本机运行的 Qwen3 语音识别模型转成文字，再交给 Codex 整理成每日记录、会议笔记，保存为 Markdown 和 HTML。

**Intake 还有一个本地 dashboard，可以直接看到这套流程跑到了哪里。**

这是我电脑上的实际界面。看板里已经累计有 24 段音频，共 24 小时 25 分钟。上面能看到新增录音的待处理队列、运行状态；下面按日期列出音频、转录和报告，能看到 Markdown 是否已生成，也可以点 HTML 打开报告。哪一天还缺转录、哪次运行需要检查，也会显示出来。

右边的 Generate now 可以手动触发处理，也可以设置每天处理的时间。配置好以后，Mac 保持唤醒，已经同步过来的录音就可以按计划整理。设备同步由苹果完成，Intake 负责接住 Mac 上已有的录音；本机转录和文件保存之外，iCloud 同步、Codex 使用的模型服务仍然会用到云端。

我很喜欢这套方案背后的判断。**鸭哥很厉害的一点，恰好是知道该选什么、该把力气花在哪里。**

我们究竟在优化什么？对我来说，是当下很容易开始录，录完不用搬来搬去，之后要用的时候找得到，找到了还能接着加工。收音只是其中一环。

手机、手表、电脑，我们已经花了很多钱买过。苹果也花了很大的投入，把麦克风、录音体验、设备之间的同步做得很好。这个基础就在手里，在它上面补上转录和整理，就能解决我的日常需求。

如果再买一个录音豆或者专门的软件，我会先问：它具体让哪一段变得更好了？是现有设备确实录不清楚，还是按下录音更方便？省下了哪些操作？会不会又多一件要充电、随身携带、导出文件的东西？

如果确实解决了一个重要问题，就有购买的理由。但只因为看到一个“AI 录音设备”，就默认自己缺这个东西，很容易把问题想窄。

**技术选型很难，因为你得看懂整个使用过程，判断哪些能力已经足够成熟，哪些地方值得增加投入。** Intake 的选择好在，它把苹果已经做好的部分用起来了，把开发投入放在了让录音成为可用上下文的那一段。这是[很值得学的 Architect 判断](https://www.superlinear.academy/c/aa/sections/812394/lessons/3089125)。

对我来说，这里面还有一个更重要的选择：**把上下文留在自己手里。**

我跟朋友出去聊天、跟家人讨论事情、参加会议，都会有以后值得回头看的内容。AI 不会凭空知道我们经历过什么、讨论过什么，也不知道一个决定背后的考虑。这些具体材料，才是它下一次帮我做事时最有价值的上下文。

Intake 留下的音频、转录和 Markdown 文件，就在自己的目录里。我可以搜索、修改、备份，也可以换一个模型继续处理。很多需求，用搜索加 Markdown 文件就能解决：

- 回顾几次会议，找出当时为什么没有选某个方案。
- 把围绕同一个问题的几次讨论找出来，带着原来的考虑继续往下做。
- 把聊天里值得展开的内容整理成笔记、文章，或者下一次讨论的准备材料。

前两天我跟韦晓亮老师聊教育 AI、产品和上下文，后来整理成了[这篇社区文章](https://www.superlinear.academy/c/ai-resources/result-certainty-general-intelligence-wei-xiaoliang)。录音转成文字之后，再做选材、核对和编辑，就有了可以分享给大家的内容。这是留下上下文以后的一种用法，类似的加工可以继续叠加。

文件多了，还可以配上 Registry 里的[本地文件语义搜索 Skill](https://skills.superlinear.academy/?skill=semantic-search-skill)，从已有材料里找出相关片段，再交给 AI。今天想写文章，就组织成文章；明天换了需求，就用同一批材料解决新问题。

所以选工具时，我会对“这些东西最后留在哪里”特别敏感。能不能完整拿出来？离开这个工具以后，还能不能搜索和继续使用？**对我而言，最有价值的积累就是自己的上下文。工具可以换，这些积累要跟着我走，不能被工具绑架。**

想试的同学，可以从 [Skill Registry 的 Intake 页面](https://skills.superlinear.academy/?skill=intake-skill)进入，登录后查看安装提示；也可以直接使用[鸭哥的开源项目](https://github.com/grapeot/intake-skill)。默认方案适合使用苹果语音备忘录、并有 Apple 芯片 Mac 的同学。Apple Watch Ultra 可以在“设置 → 操作按钮”中选择“语音备忘录”；其他型号直接打开语音备忘录录音即可。

把项目地址交给 AI 编程助手，让它帮你装起来，先用一小段录音跑通：

> 请阅读 https://github.com/grapeot/intake-skill 的 README 和 skills/skill_intake.md，检查我的 Mac 和所需依赖，帮我在指定目录安装。先用一条我选定的测试录音跑通转录和整理，再打开 dashboard，让我看到生成的文件在哪里。跑通以后，再帮我设置日常处理时间。

如果还需要群里提到的 speaker diarization，也就是区分不同说话人的片段，可以看我的[视频制作项目中的说话人归因流程](https://github.com/sunyuzheng/lizheng-video-production#%E5%8F%AF%E9%80%89%E8%AF%B4%E8%AF%9D%E4%BA%BA%E5%BD%92%E5%9B%A0)。它使用音频和带时间轴的字幕做后续处理；Intake 本身不做分人。

Intake 可以直接拿去用。我更希望大家也学会背后的判断：自己在优化什么，手里已经有哪些好用的能力，以及哪些积累一定要掌握在自己手里。换一个问题，你仍然能选出合理的方案。这也是我们在 [AI Builders](https://www.superlinear.academy/c/ai) 和 [AI Architect](https://www.superlinear.academy/c/aa) 里要练的能力。
