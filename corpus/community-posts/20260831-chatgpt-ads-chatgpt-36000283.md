---
id: "circle-36000283"
title: "ChatGPT Ads的根本矛盾：广告靠影响选择赚钱，Agent靠完成选择创造价值"
author: "Yuzheng Sun"
source_type: "community-post"
source_url: "https://www.superlinear.academy/c/news/chatgpt-ads-chatgpt"
published_at: "2026-08-31T20:39:56.550Z"
updated_at: "2026-09-06T21:35:57.075Z"
snapshot_at: "2026-09-17"
community_space: "Deep News"
community_space_slug: "news"
source_visibility: "members-only"
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
source_family: "https://www.superlinear.academy/c/news/chatgpt-ads-chatgpt"
language: "zh"
source_context: "Dated published post or reply; preserve the distinction between publisher, narrator, and quoted contributor."
---

<!-- provenance:start -->
> Attribution / 归属：发布于立正账号；发布归属不证明文字全部由本人亲笔撰写。引用、访谈嘉宾、社区提问与案例归相应作者／说话人；其中的他人主张不能直接算作立正立场。
<!-- provenance:end -->

> 原文：[ChatGPT Ads的根本矛盾：广告靠影响选择赚钱，Agent靠完成选择创造价值](https://www.superlinear.academy/c/news/chatgpt-ads-chatgpt) · 发布于 2026-08-31 · 原始空间可能需要社区会员权限。本文保留发表时语境；其中第三方引文、发言、链接与商标不随正文重新授权。

**TL;DR：**ChatGPT Ads很可能做成百亿美元级别的生意，问题不在规模，而在战略方向。Agent本来是广告互联网的counter-positioning：它通过消灭搜索、比较和点击，为用户完成决定；广告却通过影响这些决定赚钱。如果Ads成为OpenAI的核心收入，Google、Meta所受的incumbent constraint也会随之进入ChatGPT。真正AI-native的商业模式，应该在中立决策之后，按能力、任务完成和实际结果收费。

## ChatGPT Ads的十亿美元ARR Run Rate里程碑

> OpenAI 说，广告可以补贴更广泛的 AI access。但当 ChatGPT 从一个回答问题的工具变成用户的 agent，它最珍贵的资产已经不再是注意力，而是用户授权它代表自己作出判断的那份信任。

8 月 31 日，我的前老板 Vijaye Raji（VJ，现任 OpenAI Applications CTO）在 LinkedIn 上宣布：ChatGPT Ads 上线不到 200 天，年化收入 run rate 已达到 10 亿美元。这是 OpenAI 历史上达到这一里程碑最快的产品。

这个里程碑值得认真对待，因为它背后已经不只是答案下面的一个 banner。今天的公告列出了数万广告主、40 多个国家、50 多家技术与测量合作伙伴，以及已经占多数的 CPC 和 outcome-optimized bidding，再加上 Pixel、Conversions API、product feeds 和 custom audiences。OpenAI 已经在很短时间里搭出了 performance marketing 的关键骨架，把 Google、Meta 验证过的广告购买、归因和竞价体系迅速移植进 ChatGPT。[OpenAI 公告](https://openai.com/index/expanding-access-to-ai-with-chatgpt-ads/)

凭借超过10亿周活用户、大量明确的商业决策场景和现成的全球广告预算池，ChatGPT Ads完全可能成为一个百亿美元级别的生意。但这恰好让真正的问题变得更尖锐：**一个生意可以很大、毛利很好、增长很快，却仍然不是这家公司最应该拥有的收入。**

## “广告补贴普惠”还没有回答最重要的问题

OpenAI 对广告的官方叙事非常完整：广告只出现在 Free 和 Go，Plus、Pro、Business 和 Enterprise 保持无广告；广告与答案清楚分开，不影响回答，也不出售对话数据；收入则帮助更多人以更少的使用限制、甚至不用付费的方式获得 AI。[OpenAI 的广告原则](https://openai.com/index/our-approach-to-advertising-and-expanding-access/)

这套说法最有吸引力的地方，是它把广告描绘成一项 mission-aligned 的融资工具：免费推理需要钱，广告主替用户付钱，于是 OpenAI 可以把更强的 AI 分发给更多人。

问题在于，钱是统一的。免费 ChatGPT 并不需要在自己的账上直接挣回每一美元成本，才算是一项成立的业务。

免费用户首先是 OpenAI 的分发系统。他们形成使用习惯，其中一部分转为个人订阅；他们把 ChatGPT 带进工作场景，降低企业试点、培训和推广的阻力；他们构成开发者、apps、agents 和商家愿意接入 ChatGPT 的需求侧。OpenAI 自己披露，消费者普及已经在推动企业增长：熟悉 ChatGPT 的数亿用户让企业 pilot 更短、rollout 摩擦更低；当时 ChatGPT for Work 已超过 700 万席位，Enterprise 席位同比增长 9 倍。[OpenAI 企业业务披露](https://openai.com/index/1-million-businesses-putting-ai-to-work/)

如果免费使用最终降低了企业获客成本、推动了组织采购，那么企业收入本身就是免费用户商业价值的实现，只是它发生在另一张账单上。就像一个操作系统、浏览器或开发者平台不必向每一个入口用户收费，免费分发完全可以是订阅、企业和平台业务的获客成本。

当然，广告也有其他模式很难替代的作用：它能从没有订阅意愿、也未必会推动企业采购的使用中回收价值。尤其在低支付意愿市场，它可能是最容易规模化的交叉补贴机制，能够降低每增加一个免费用户的净成本。这是 Ads 最强、也最真实的战略理由。

但“Ads 的收入可以补贴免费用户”仍然只是一个会计描述，不是充分的战略证明。订阅可以补贴，企业收入可以补贴，API 和未来的 outcome revenue 也可以补贴。真正的问题是：**广告独有的补贴价值，是否足以补偿它对代理关系的长期压力；在所有能够捕获免费分发价值的方式里，它是不是回报最高、外部性最低、最能强化 OpenAI 长期优势的那一种？**

问题不在Ads能否做大，而在于agent原本代表着与广告互联网相反的产品与盈利逻辑；把Ads变成核心收入，会把incumbent的约束重新带进OpenAI。

## ChatGPT 最稀缺的资产不是注意力，而是代理权

互联网历史让广告看起来像一个非常自然的答案。Meta 把 attention 变成 inventory；Google 把 query intent 变成竞价；Amazon 把交易现场里的货架位置变成广告位。

ChatGPT 的确同时拥有三者的一部分：用户停留在这里，主动表达需求，也越来越接近购买和行动。OpenAI 今天甚至把广告业务所在的位置概括成“Where decisions take shape”。

但 ChatGPT 与这些平台有一个决定性的不同。

用户在 Instagram 上消费内容，并没有授权 Instagram 代表自己判断。在传统 Google 搜索体验中，用户通常仍然需要点开链接、比较信息、自己做决定。用户进入 Amazon，也知道自己身处一个商家竞争货架的 marketplace。

而当一个人告诉 ChatGPT 自己的预算、偏好、家庭安排、工作背景和真实约束，然后问“我到底应该选哪个”，他交出去的不只是注意力和 intent，而是一部分**代理权**：请你理解我的利益，替我压缩选择，甚至替我采取行动。

这也是为什么 ChatGPT 的上限远高于搜索框。它最有价值的未来，不是给用户更多链接，而是成为一个越来越了解用户、能够跨工具执行任务的 agent。OpenAI 自己也把下一阶段定义为能够长期保持 context、跨工具行动的 agents 和 workflow automation。[OpenAI CFO 对业务模式的阐述](https://openai.com/index/a-business-that-scales-with-the-value-of-intelligence/)

一旦产品走到这里，广告就不再只是界面上的一种 monetization format，而会制造一个标准的 principal-agent conflict：用户希望 ChatGPT 为自己优化；广告主付钱，希望提高自己被选择的概率。

OpenAI公布的数据表明，在当前广告载量下，trust、relevance和overall experience指标仍然稳定。这说明广告与回答清楚分离时，两者可以共存。但这些原则约束的是当下的产品设计，无法单独消除广告收入扩大之后的组织激励。

如果广告永远与回答、推荐候选集和 agent action 完全分开，它就会越来越像一个附着在核心体验外面的 sponsored module：相对安全，但价值和天花板有限。反过来，如果 OpenAI 要让广告更 native、更高转化，它迟早会面对更难的问题：付费能否影响哪些商品进入候选集、哪个 app 被调用、哪个商家被展示、ChatGPT 建议的下一步是什么。

**ChatGPT Ads 出售的并不是一块页面空间，而是接近用户决策的权利。可那项决策，正是用户委托 ChatGPT 代为维护的东西。**

## Agent 本来就是广告模式的 counter-positioning

如果用 Hamilton Helmer 的 7 Powers 来描述，agent 本来可以构成对广告资助型互联网的 counter-positioning：它不只是提供更强的模型，而是连同一套按能力与任务完成收费的新商业模式，消灭 incumbent 必须保留的搜索、比较和点击环节。广告平台若完整复制，伤害的正是自己的利润来源。

传统广告业务靠 funnel 存在：用户浏览、搜索、比较、点击，广告主在这些尚未完成的步骤里购买影响力。一个 performance ads 系统会自然地学习如何识别更多 commercial moments，增加可竞价的触点，并优化点击和转化。

但一个优秀 agent 的任务，恰恰是压缩这些步骤。它应该减少搜索，减少 tab，减少重复比较，在足够的信息下迅速完成正确的决定和行动。

这并不意味着更好的 agent 一定带来更少的广告收入。更少的 impression，完全可能被更高的 intent、更高的 conversion 和更高的 CPC 或 CPA 抵消；越接近行动的商业时刻，反而越值钱。

可这使冲突更强，而不是更弱。**广告在决定完成之前，出售影响选择的概率；agent 在替用户完成决定时创造价值。** 当 ChatGPT 能从十个选项中替用户挑出一个，并直接调用工具执行，这个唯一候选位会比十个搜索链接更值钱，广告主也会更愿意付钱进入它。广告增长最诱人的空间，因此恰好位于它最不应该进入的地方：候选集、工具选择和行动排序。

所以，ChatGPT Ads 的 fundamental flaw 并不是广告收入与 agent 能力存在简单的负相关。更准确地说，**agent 越强，每一个商业决策点越值钱；Ads 越想充分捕获这份价值，就越必须接近 agent 的决策函数。** 如果它停留在答案下方，冲突可控但捕获有限；如果付费开始改变选择概率，收入空间变大，代理关系却被改写。

OpenAI原本没有需要保护的搜索广告现金牛，因此可以比广告平台更彻底地减少搜索、比较和点击。Google、Meta若采用同样的产品逻辑，就必须承担压缩现有广告inventory的代价。建设Ads，则会把这项原本属于incumbent的约束带入OpenAI自己的产品和组织。

Counter-positioning不是说agent与任何广告都不能共存；它意味着，一旦广告成为核心收入，OpenAI就很难毫无保留地把“消灭可被商业影响的中间环节”设为产品目标。

更值得关注的不是今天答案下方那个明确标注的广告，而是广告业务扩大后形成的组织激励：公司会更有动力增加inventory、提高ad load，并让更多尚未完成的用户决定变成可商业化的触点。

所以，百亿美元级别的收入预测本身并不是最重要的问题。我认为这个量级可以达到。真正重要的是：OpenAI 需要让广告多深地进入 ChatGPT 的决定与行动，才能达到它。

这就是为什么 agent 需要一套新的 business model：它必须在减少决策摩擦、完成更多任务时赚得更多，而不能依赖保留更多可被影响的决策点赚钱。

## AI-native 的商业模式，应该在行动之后收费

既然 agent 的竞争优势来自减少中间环节，它的商业模式就必须让系统在更快、更好地完成任务时赚得更多。这并不意味着商家不能为 ChatGPT 创造的价值付钱。关键不只是谁付钱，还在于付款买到了什么，以及这笔钱是否改变 agent 的选择和优化目标。

广告让商家在结果发生之前，为“影响被选择的概率”付钱。一个更符合 agent 逻辑的模式，是在中立选择之后，为一次被用户授权、并且成功完成的行动付钱。消费者或雇主可以为能力、可靠性和 workflow 付费；app 与 agent 提供者可以为 runtime、分发和 billing 付费；商家可以为成交或任务完成支付基础设施费用；能够审计结果的企业场景，则可以采用 outcome、savings 或 IP-based pricing。形式不同，它们捕获的都是 agent 已经创造的价值，而不是出售左右其判断的权利。

这些模式也不会天然中立：成交费同样可能污染排序，outcome pricing 也可能诱发指标 gaming。它们只有在费率透明、付费与排序分离、用户明确授权、结果可以审计时，才真正维持 agent 与用户利益的一致。共同原则只有一个：**让收入随着 ChatGPT 把事情做得更好而增长，而不是随着 ChatGPT 更能影响用户而增长。**

OpenAI 其实已经做过最接近这一逻辑的实验。2025 年推出的 Instant Checkout 中，商品结果保持 organic、按相关性排序；商家只在交易完成后支付小额费用，手续费本身不影响推荐。需要说明的是，是否支持即时结账仍可能作为同一商品不同商家排序时的体验因素之一。[Instant Checkout 与 Agentic Commerce Protocol](https://openai.com/index/buy-it-in-chatgpt/)

但到 2026 年，OpenAI 承认初版 Instant Checkout 无法给商家足够的灵活性，于是让商家使用自己的 checkout，自己则退回 product discovery。Walmart 的 ChatGPT app 是更深集成的一个具体案例，保留了账号连接、loyalty 和 Walmart payments。[OpenAI 2026 年的 shopping 调整](https://openai.com/index/powering-product-discovery-in-chatgpt/)

这段变化非常重要。它说明 agentic commerce 比广告难得多：OpenAI 必须处理实时商品数据、身份、权限、支付、履约、退货、责任和商家关系；企业 outcome pricing 也必须解决归因、审计与风险分配。相比之下，广告可以复用成熟的买方、预算、计费和测量标准，因此商业化速度远快于交易基础设施。

所以 ChatGPT Ads 的 200 天，本质上证明了旧互联网商业基础设施有多容易复用，并没有证明它比 agent-native 的商业模式更优。广告是那条最快的路，只是因为更好的路还没有铺完。

## 一套商业模式，会让 OpenAI 复利哪一种能力

Counter-positioning 最终不是一句产品原则，而是整家公司选择复利哪一组能力。这件事不能被简化成“把广告工程师调去训练模型”：这些业务需要的并不是同一批人，一个盈利的广告团队也完全可以为自己的人力买单。

真正稀缺、也真正互相冲突的资源，是 ChatGPT 的核心产品 surface、用户授权、管理层注意力，以及整家公司最终优化的目标函数。

订阅收入要求 OpenAI 把 agent 做得更有用。企业收入要求它把模型接进更深的 workflow，建立身份、权限、数据连接、evals 和治理。Apps 与 transaction revenue 要求它提高执行成功率，扩大能完成的任务范围。这些投入都会让 ChatGPT 的能力、状态和切换成本继续复利。

广告收入则主要要求 OpenAI 提高对商业意图的识别、匹配、竞价与归因能力。广告主会 multi-home，预算随 ROAS 流动；拍卖、Pixel、CAPI 和 audience targeting 本身并不是 OpenAI 独有的 moat。ChatGPT Ads 真正不可复制的优势，是用户在对话里主动交出的 context 与信任。

ChatGPT Ads的差异化恰好来自用户主动交出的context与信任，广告化越深入，越可能消耗这项优势。它的财务质量可能很好：现金来得快、广告主预算巨大、基础设施建成后的边际毛利也可能很高。但它的战略质量低于订阅和企业收入，因为广告主的切换成本低，对ChatGPT核心产品的强化作用也更弱。订阅和企业收入促使OpenAI提高agent能力、可靠性和workflow深度；广告收入则促使它增加可识别、可归因、可购买的商业触点。

如果 OpenAI 要保住这项战略优势，投入边界就应该非常清楚：product feeds、商家身份、实时库存、转化验证、支付、权限和 action protocols 值得建设，因为它们可以从广告复用于 agentic commerce；面向广告 load、行为 targeting、更多竞价位置和 revenue-driven ranking 的专用能力，则不值得成为 ChatGPT 的战略中心。前者让系统更会完成事情，后者让系统更会出售影响力。

## 我的预测

我的中央判断是：Ads会先利用现成预算快速扩大，但纯Ads不会成为OpenAI在2030年最重要、质量最高的收入来源。随着ChatGPT从discovery进入execution，商家侧收入更可能逐步转向apps、tool calls、completed transactions和可验证outcomes。这个迁移取决于app billing、action protocols和outcome attribution真正成熟——今天它们还没有成熟——但它比不断把竞价位置推进agent决策层更符合OpenAI的产品利益。那部分收入可能仍被组织在一个广义的commercial business里，经济本质上却已经不再是广告。

判断 OpenAI 是否仍然保有这项优势，不需要等待一个遥远的收入数字，只要观察一条边界：**商家付的钱，究竟是在中立决定之后为成功行动结算，还是在决定之前购买进入候选集和影响选择的概率。**

OpenAI 当然可以用广告收入让更多人免费使用 ChatGPT。但“可以补贴增长”从来不等于“这是最好的增长方式”。如果补贴的代价，是让一个本应只代表用户的 agent 同时对广告主负责，那么它扩大的是 reach，消耗的却是 delegated authority。

对一个agent而言，更可持续的终局不是更聪明的广告位，而是因为替用户把事情做好而获得报酬。
