# 来源模型

一份资料同时记录它说了什么、谁表达、何时发表、经过怎样的处理，以及可怎样使用。检索、引用和回答继承这些信息。

## 来源依据与资料版本

事实依据主要来自已发表的文章、视频和节目。Open Context统一维护它们的文本和结构化记录；引用通过来源地址及时间定位回到实际发表内容，通过版本信息回到当次使用的资料。

`published_at`记录来源的发表时间，`snapshot_at`记录采集时间，`generated_at`记录处理产物的生成时间。源文件hash固定使用过的内容；文字校准形成新的记录版本，保留其对应来源与质量状态。原稿和精校稿都以忠实保留发表内容为目的。

节目介绍、本人表达和第三方说法各自提供其所能支持的依据。介绍中的身份信息保留节目时间；发言记录支持“这个人当时这样说”，客观事实判断需要相应的事实来源。结构化记录和AI提炼都沿来源关系回查。

## 原始资料、结构化记录与提炼

原稿与忠实精校文本属于Raw层。文字、时间码、发言者、质量和版本关系保留在来源记录中；精校提高原文的可靠性。

人物、节目、参与关系和只有标题的目录条目属于Structured层（`data_layer: structured`）。它们帮助定位资料，本身没有发言，`speaker_status`为`not-speech`。

摘要、阅读地图、主题解释和判断卡属于Derived层，记录撰写方式与来源片段，独立更新。原文和提炼分别检索：

```sh
python3 scripts/search.py "问题" --layer raw --json
python3 scripts/search.py "问题" --layer derived --json
```

同一已发表文件可以包含不同层的段落。`config/source-section-layers.json`用文件hash和实际段落分界记录这种结构；原话摘录与编者说明通过`fragment_id`关联。

## 作者与发言者

原作者、发布者、翻译者和整理者分别记录。节目参与关系属于目录数据；字幕单元记录具体发言者及确认状态。人物别名用于发现节目，引用采用实际发言归属。

单人主讲按整份文件归属：视频里朗读或播放的他人内容也带着立正的`speaker_id`，引用时须读懂语境。对谈原稿按字幕单元归属。

引文、提问、假设、案例和本人判断保留其语境。对“立正怎样想”的回答，使用有明确归属和日期的本人表达。跨来源综合由回答者承担，标明对应依据。

## 字段合同

| 字段组 | 字段 | 用途 |
|---|---|---|
| 身份与定位 | `id`, `source_type`, `source_url`, `source_family` | 标识资料、回查来源、关联原作及其不同版本 |
| 作者 | `author`, `publisher`, `original_author`, `original_source_url` | 保留表达、发布和原作归属 |
| 处理方式 | `content_origin`, `generation_method`, `language` | 区分本人发表、他人作品、翻译与整理 |
| 时间 | `published_at`, `generated_at`, `snapshot_at` | 分别记录发表、生成和采集时间 |
| 片段与版本 | `data_layer`, `fragment_id`, `source_snapshot_sha256` | 区分资料层，定位原文版本及片段 |
| 人物与节目 | 目录中的`entity_id`, `source_id`与参与关系；检索时提供`participant_entity_ids`, `participant_names`, `participant_aliases` | 按人物发现相关节目 |
| 发言 | `speaker_id`, `speaker_name`, `speaker_status`, `speech_act` | 记录发言者、确认状态与表达性质 |
| 使用角色 | `evidence_role`, `yuzheng_stance_weight`, `source_context` | 区分原文、参考资料、翻译、综合与目录入口 |
| 质量 | `transcript_source_kind`, `transcript_quality` | 记录字幕来源、校对阶段和待核信息 |
| 访问与权利 | `source_visibility`, `text_access`, `rights_scope`, `license` | 分开原材料的访问方式和本份文字的使用许可 |

RAG切块继承这些字段。原文与翻译按source family关联，多个片段保持各自定位。检索分数用于排序；来源角色用于决定如何引用。

## 由脚本推出的字段

同一事实只在一处维护，其他地方的副本由`scripts/derive_catalogs.py`推出，`python3 scripts/validate_release.py --write-manifest`会重新生成，副本过期时校验失败。

| 字段 | 唯一来源 |
|---|---|
| `catalog/videos.jsonl`的`guest_names` | `catalog/guests.json`的参与关系 |
| `catalog/videos.jsonl`里嘉宾节目的标题（只有目录的行） | `catalog/guests.json`的节目记录 |
| `catalog/videos.jsonl`的`dialogue_path` | `config/public-dialogue-policy.json` |
| `catalog/guests.json`参与关系的`index`（每人按节目日期从0编号） | 节目日期 |
| 组合成员（有自己页面的）在组合节目里的参与关系 | 组合的`members`与组合的参与关系 |
| `catalog/guest-names.json`（名字表） | `catalog/guests.json`与`config/speaker-names.json` |

组合（`entity_type: group`）用`members`写明成员：每位成员有`name`，可加英文名`en_name`；成员自己有人物页时用`entity_id`指向它。组合的显示名和别名里列出的名字（「王臻 & Nick」「The Tech Roast Show（Austin、Jesse、Nikita）」）必须都是声明过的成员，校验同时检查成员确实出现在组合名字里。有人物页的成员自动列入组合的每期节目，网站的组合页和成员页互相链接；组合名字里没写成员时`members`为空列表。

名字表列出每个名字指向哪些人物：显示名、别名、括号前的本名（「硅谷徐老师（Howie Xu）」里的「硅谷徐老师」）、括号里的称呼或节目标签、组合成员的名字（有人物页的成员指向本人，其他成员指向组合），以及主持人的名字。括号里的标签和公司名同时作为区分同名者的限定词。名字的键先做NFKC和大小写折叠，再去掉空白和标点，规则与示例写在文件里，消费者按同一规则处理问题再查表。名字表只用于找人；合并或拆分身份仍要回到来源。

## 许可与版本

每份文件声明一项许可，release manifest记录其hash和许可。会员媒体的访问方式与已授权文字的开放方式分别保存；嘉宾、第三方作者和合著者的作品保留其归属。具体规则见[版权与许可](../LICENSE.md)。

数据更新在Open Context完成。消费者按commit和manifest构建可重现的副本，保存引用所用版本；实际来源、质量和许可随该版本一起进入回答。字幕结构与导入流程见[对谈资料](dialogue-ingestion.md)。
