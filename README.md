# 立正 · Open Context

立正的公开资料库：以已发表的原文和媒体为依据，保存原文、精校文本，以及人物、节目和来源关系。给人和AI提供可检索、可引用、可继续开发的数据。个人网站与问问立正消费同一份版本。

**[资料目录](INDEX.md)** · **[架构](docs/conversation-architecture.md)** · **[版权与许可](LICENSE.md)** · **[更新记录](CHANGELOG.md)**

## 数据结构

| 目录 | 内容 | 用途 |
|---|---|---|
| `corpus/` | 文章、课程与书籍文字、视频字幕、对谈原稿、原话摘录及译稿 | 阅读、检索与引用，保留作者、日期、时间码和质量 |
| `catalog/` | 人物、别名、节目、参与关系、伴读链接及来源目录 | 共享结构化事实，按人物和来源发现资料 |
| `context/` | AI整理的阅读地图、框架与判断卡 | 独立的提炼层，帮助阅读并回指原文 |
| `index/` | 按来源、时间与主题组织的目录 | 导航，由数据自动生成 |
| `scripts/` | 校验、导入、目录生成与本地搜索 | 维护和使用资料 |
| `docs/` | 数据合同、引用协议与开发说明 | 接入不同产品 |

`catalog/guests.json`分别保存实体、来源与参与关系，`catalog/guest-articles.json`保存已发表伴读文章的链接，`catalog/guest-names.json`是由它们生成的名字表。人物ID稳定，姓名、别名、介绍和链接可持续校准。结构化对谈原稿保留字幕单元及各自的时间码、发言者和质量。

当前资料数量、时间与许可由数据生成，见[目录](INDEX.md)；文件版本由[`release-manifest.json`](release-manifest.json)固定。

## 使用

无需向量数据库，可先运行本地搜索：

```sh
python3 scripts/search.py "如何建立信念" --layer raw --json
python3 scripts/search.py "职业发展" --layer derived --json
python3 scripts/search.py "growth accounting" --type book
python3 scripts/search.py "项目复盘" --type video
python3 scripts/search.py "科学能解释的东西很少" --type excerpt
```

结果带原文片段、来源、日期和归属，视频可定位到对应时间点。原稿与AI提炼分别检索；节目参与者用于发现资料，字幕单元用于确认具体发言。

接入Agent或其他产品：

1. [资料架构](docs/conversation-architecture.md)：数据、提炼与Context Infra的分工。
2. [来源模型](docs/source-model.md)：身份、作者、时间、版本、归属和质量字段。
3. [对谈格式](docs/dialogue-ingestion.md)：结构化字幕与导入流程。
4. [回答协议](docs/answering-contract.md)：引用、综合与推断的呈现。
5. [开发指南](docs/build-your-own-agent.md)：检索和推荐的参考流程。

## 维护

资料修改在本仓库完成，校验后生成release。网站从固定commit和manifest生成嘉宾页快照；Context Infra重建语料副本、索引与证据包。更新数据与调整检索策略各在其所属项目进行。

```sh
python3 scripts/validate_release.py --write-manifest
python3 scripts/validate_release.py
```

原稿、精校版本和质量依据保留可追溯关系。公开release按已审阅的源文件及许可收录，具体规则在`config/`。新素材在本地整理后，审阅准确公开变更，再发布到main。发现错字、归属问题或断链可[开issue](https://github.com/sunyuzheng/lizheng-open-context/issues)。

## 许可

每份资料保留自己的许可：

- 立正的自有文字与AI整理：CC BY 4.0。
- 已授权的课程、会员与对谈文字，以及书和博客中文版：立正参考使用许可，支持阅读、搜索、免费问答与短引用。
- 他人的作品和嘉宾发言：原作者保留权利。
- 目录数据：CC0 1.0。
- 程序和说明：MIT。

具体使用条件见[LICENSE.md](LICENSE.md)。`--license open`可限定搜索自由再利用的资料。

## 使用与交流

实际产品：[个人网站](https://www.lizheng.ai/guests) · [问问立正](https://ask.lizheng.ai)

参考实现：[真本事Advisor](https://github.com/sunyuzheng/zhenbenshi-advisor) · [Superlinear Advisor](https://github.com/wyuebei-cloud/superlinear-advisor) · [社区项目](COMMUNITY-PROJECTS.md)

欢迎带着使用结果、问题或新的实现加入[仓库讨论](https://www.superlinear.academy/c/tools/lizheng-context?utm_source=github&utm_medium=referral&utm_campaign=lizheng_open_context)。
