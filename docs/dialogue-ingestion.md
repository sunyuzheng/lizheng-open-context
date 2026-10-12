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
    "id": "youtube-ABCDEFGHIJK#cue-1",
    "start_seconds": 1.25,
    "end_seconds": 3.5,
    "text": "保留实际发言。",
    "speaker_id": "unknown",
    "speaker_name": "",
    "speaker_status": "unresolved"
  }]
}
```

正式文件另有来源、日期、许可及质量字段，格式由release validator校验。发言者确认依据保存在审核记录中，未确认的单元保留`unknown`。人物、姓名、别名与节目参与关系由`catalog/guests.json`统一提供，读取原稿时按来源ID关联；具体发言归属保存在字幕单元中。

## 本地整理与公开版本

`scripts/build_dialogue_candidates.py`从明确inventory及完整hash回执生成本地候选，保留每个cue的文字与时间。候选及原媒体、原字幕、校对依据在本地素材库保存。`scripts/search_dialogue_candidates.py --pack <候选目录> --verify-only`检查候选；去掉`--verify-only`并提供问题可直接在本机搜索。

公开原稿按`config/public-dialogue-policy.json`中的视频ID、源文件hash、匿名公开状态证据和许可收录。`python3 scripts/validate_release.py --write-manifest`校验并生成公开release。新的公开变更经过准确payload审阅；会员和未公开的新素材继续留在本地。

## 说话人归属

单元的说话人有两种确认方式，各有一份绑定在`config/public-dialogue-policy.json`里的记录：

- 文字核对（`reviewed-source-attribution`）：`config/raw-turn-attribution-policy.json`逐个单元记录说话人、言语行为和内容hash，依据是字幕里的自我介绍和上下文。
- 声纹比对（`audio-voice-match`）：`config/audio-speaker-policy.json`记录模型、阈值、检验结果和每期的hash。方法是先用立正单口视频的音频算出他的声音特征，再在每期对谈里找出最像他的句子作为他在这期的声音，在明显不像他的句子里找出其他人的声音；一句话只有和他的声音特征、和这期里的各个声音都对得上，并且领先第二名足够多，才标说话人。拿不准的句子保持`unknown`。嘉宾只在节目目录里恰好列了一位、且这期恰好找到一个其他声音时才标名字。每个标了说话人的单元都有言语行为（陈述、提问、介绍、回应、玩笑、转述），由模型按上下文判断，没判断出来的单元保持`unknown`。

每期的记录用hash绑定标注时的原文和全部标注：原文改了或标注改了而没有重做比对，校验就会失败。立正的声音特征本身是声纹，只留在维护者本机，记录里只有它的hash。

切块时，一期对谈产生两种片段：完整字幕片段按时间切分，不归给任何人；“某人在本期说的话”片段只汇集一位已确认的说话人被判断为陈述的句子，每行带时间点。立正的陈述片段可以作为他的直接来源，他的提问、介绍、回应、玩笑和转述只出现在完整字幕里。

新对谈收录后，在本机运行`scripts/voice_attribution.py`：`embed`（需要本地音频库、torch、pyannote.audio和ffmpeg）、`label`、`acts`（需要`AI_BUILDER_TOKEN`）、`apply`，再运行`python3 scripts/validate_release.py --write-manifest`。维护者确认过的节目（比如他指出哪个声音是自己）用`--checks`传入，记录在该期的`maintainer_check`里。

质量字段分别记录AI文字校对、改动复核、全文阅读、音频核验和待核数量。各阶段按其实际证据登记，消费者可据此判断一份原稿适合怎样使用。
