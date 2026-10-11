# 对谈原稿与提炼

精校逐字稿是Raw资料：保留文字、时间码、说话人、来源版本和质量。摘要、阅读地图、主题解释与判断卡是Derived资料，回指原文。人物与节目目录是两层共用的结构化资料，见[资料架构](conversation-architecture.md)。

## 检索接口

```sh
python3 scripts/search.py "问题" --layer raw --json
python3 scripts/search.py "问题" --layer derived --json
```

原话摘录的引用块作为Raw，小标题与编者说明作为Derived，以相同`fragment_id`关联。已发表整理稿的分层规则在`config/source-section-layers.json`，绑定其源文件hash及原文中的实际分界。

## 结构化字幕

`corpus/dialogues/`每期一个JSON。下面是格式示例：

```json
{
  "schema_version": 1,
  "data_layer": "raw",
  "id": "youtube-ABCDEFGHIJK",
  "video_id": "ABCDEFGHIJK",
  "title": "示例对谈",
  "source_url": "https://www.youtube.com/watch?v=ABCDEFGHIJK",
  "source_type": "video-transcript",
  "units": [{
    "id": "cue-1",
    "start_seconds": 1.25,
    "end_seconds": 3.5,
    "text": "保留实际发言。",
    "speaker_id": "unknown",
    "speaker_name": "",
    "speaker_status": "unresolved"
  }]
}
```

正式文件另有来源、日期、许可及质量字段，格式由release validator校验。切块按时间和说话人边界进行。发言者确认依据保存在审核记录中，未确认的单元保留`unknown`。人物、姓名、别名与节目参与关系由`catalog/guests.json`统一提供，读取原稿时按来源ID关联；具体发言归属保存在字幕单元中。

## 本地整理与公开版本

`scripts/build_dialogue_candidates.py`从明确inventory及完整hash回执生成本地候选，保留每个cue的文字与时间。候选及原媒体、原字幕、校对依据在本地素材库保存。`scripts/search_dialogue_candidates.py --pack <候选目录> --verify-only`检查候选；去掉`--verify-only`并提供问题可直接在本机搜索。

公开原稿按`config/public-dialogue-policy.json`中的视频ID、源文件hash、匿名公开状态证据和许可收录。`python3 scripts/validate_release.py --write-manifest`校验并生成公开release。新的公开变更经过准确payload审阅；会员和未公开的新素材继续留在本地。

质量字段分别记录AI文字校对、改动复核、全文阅读、音频核验和待核数量。各阶段按其实际证据登记，消费者可据此判断一份原稿适合怎样使用。
