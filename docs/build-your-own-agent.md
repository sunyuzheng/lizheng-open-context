# 用这个仓库开发自己的立正 Agent

## 最小可用版本

一个真正有用的 V1 只需要五步：

```text
用户问题
  → 同时检索当前 context、社区帖子、精选评论、视频字幕和视频目录
  → 按来源质量、语义相关性与时间排序
  → 生成答案，并标记直接来源 / 综合 / 推断
  → 返回 2–4 个带理由的文章或时间码视频
```

先让这个闭环可靠，再考虑人格、语气或复杂工作流。

## 推荐的检索单元

- `context/*.md`：按二级标题切块，权重最高但不替代具体证据；
- `corpus/community-posts/*.md`：按标题与段落切块，保存文章 URL、日期、空间与原始可见性；
- `corpus/community-comments/*.md`：每条评论作为一个检索单元，权重低于完整文章；它适合补充边界、例子和历史讨论，不应单独升级成当前立场；
- `corpus/videos/*.md`：按 60–120 秒窗口合并相邻字幕，保存起始时间码；
- `catalog/videos.jsonl`：用于发现没有纳入全文的嘉宾访谈或缺字幕视频；
- `context/zhenbenshi-frameworks.md`：按七套框架及小节切块，是《真本事》建议与检索的主要内容源；
- `context/zhenbenshi-reading-map.md`：用于章节定位、常见问题路由和官方阅读入口。

## 排序建议

最终相关性可以组合：

```text
语义相关性
+ 标题精确命中
+ 当前 context 的来源优先级
+ 与问题所需证据类型的匹配
+ 较新材料的轻量加权
- 只有词面相似但任务不匹配
- 缺少可追溯链接
```

“新”不自动等于“对”；稳定主张与历史判断使用不同时间逻辑。

## 生成时给模型的最小约束

```text
只根据给定材料回答。把直接来源、跨来源综合和你的推断分开。
每个重要事实附原始链接；视频引用附时间码。
如果材料不足，明确说不足，不要补成立正的观点。
最后推荐 2–4 个最相关来源，并逐条解释为什么。
```

完整约束见 [`answering-contract.md`](answering-contract.md)。

## 一个应通过的评测

问题：

> 如何找到适合写在简历里的项目？如何复盘自己做过的项目？

一个合格结果至少要做到：

- 不只搜索标题，也能找到《真本事》的“打造产品”“投入—产出—成果”“真实市场反馈”等框架；
- 将“项目”解释为可以遇到真实反馈的工作，而不要求它必须宏大或成功；
- 给出一个可执行的项目发现与复盘流程；
- 推荐少量真正相关的视频或文章，而不是堆链接；
- 不杜撰“立正说过”的原句。

仓库在 `evals/questions.jsonl` 保存这类问题，方便不同实现比较。

## 不推荐的产品承诺

- “立正数字分身”或“100% 还原本人”；
- 自动替本人做背书、商务承诺或高风险判断；
- 未标明独立开发，却使用容易造成官方误认的名字、头像和品牌；
- 把私有社区、付费课程或书籍全文偷偷补进向量库。

最好的衍生产品不是最像一个人说话，而是最能帮助用户理解材料、发现出处、形成自己的判断。

## 可参考的现有 skill

如果产品只处理《真本事》里的职业、价值、杠杆和收入问题，可以先看公开的 [`zhenbenshi-advisor`](https://github.com/sunyuzheng/zhenbenshi-advisor)。它展示了怎样把书中框架压缩成一个小型建议流程。本仓库的 [`zhenbenshi-frameworks.md`](../context/zhenbenshi-frameworks.md) 提供更完整、可授权复用的框架正文；更大的仓库则继续把书、文章与视频的源材料规范化，让不同 skill / agent 能自行检索、引用和综合。

## 保留作者和生成方式

读取 `docs/source-model.md` 的归属字段，并在每个 chunk 以及送入 LLM 的材料中保留它们。`search.py --json` 已返回作者、发布者、AI 生成方式、语境、证据权重与 source_family。词面 score 不等于立场证据权重；原文与译文不应作为两份独立支持。AI synthesis 明确署名 AI，社区作者的观点明确归原作者。

维护时先导出获准的源语料，再运行 `scripts/enrich_provenance.py --english-cache <sanitized-English-cache>`；如果导入已获准的本人视频英译，再运行 `scripts/import_english_translations.py`。最后运行 `python3 -m unittest discover -s tests`、`python3 scripts/validate_release.py --write-manifest` 和 `python3 scripts/validate_release.py`。原始缓存不能提交；新增来源或修改公开范围后，先形成可审阅差异再发布。
