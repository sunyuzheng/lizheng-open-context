# 对谈资料：原文先入库，提炼按需生成

精校后的逐字稿属于原始资料。时间码、说话人、来源、版本与质量是它的元数据；摘要、主题标签、语义判读和判断卡属于派生提炼。搜索原文不需要先生成 AI 摘要。两位说话人的发言都可以被找到，但嘉宾说过不等于立正赞同，立正提问或复述也不等于本人主张。

## 现有原文与提炼的分离

`scripts/search.py` 将 `video-excerpt` 文件的引用块读成 `data_layer=raw`，将小标题与背景说明读成单独的 `data_layer=derived`。说明用相同 `fragment_id` 回指引文。字幕正文只读取时间码对应的转录句子，不把编者提示、人物介绍和章节标题当作发言。原文件保持不变。

`python3 scripts/search.py "问题" --layer raw --json` 可直接检索原始资料；`--layer derived` 查询提炼。相关性分数不能证明归属或赞同。

已发表的访谈整理稿也须与逐字原话分开。`config/source-section-layers.json` 只登记原文中有明确依据的文件与分界，绑定完整源文件 SHA。刘嘉回放帖以“以下是Claude的总结”为界，前言仍保留原发布文字身份；王路回放帖明示引文经过顺读整理，全文作为派生整理稿。没有具体写作者的证据时保留“整理者（未确认）”，不默认归给 AI 或立正。同样登记原文明确声明的 Evomap、查晟、得觉、UP 主访谈总结；有结束标记时保留前言及后记的原发布文字。Evomap 正文中含发布者插注，保留混合写作、逐段归属未核的状态。两张旧判断卡移除整理稿依据，继续引用本人原话及已发表文字。文件正文与发布者均保持原样，检索片段继承各自归属；源文件或分界变化会使校验失败。

## 结构化原始字幕

`parse_raw_dialogue` 支持明确提供的 JSON 来源。每条 `unit` 保留稳定 ID、原始文字、起止秒数和说话人；切块不跨说话人边界。必要字段如下，示例只表示格式：

```json
{
  "schema_version": 1,
  "data_layer": "raw",
  "id": "youtube-ABCDEFGHIJK",
  "video_id": "ABCDEFGHIJK",
  "title": "示例对谈",
  "source_url": "https://www.youtube.com/watch?v=ABCDEFGHIJK",
  "source_type": "video-transcript",
  "speaker_classification": "mixed-or-unresolved",
  "content_origin": "mixed-or-unresolved-speech",
  "evidence_role": "speaker-attributed-speech",
  "yuzheng_stance_weight": "not-evidence",
  "units": [{
    "id": "cue-1",
    "start_seconds": 1.25,
    "end_seconds": 3.5,
    "text": "保留说话人的实际措辞。",
    "speaker_id": "unknown",
    "speaker_name": "",
    "speaker_status": "unresolved"
  }]
}
```

确认的人名须有可回查的逐段依据；格式中的 `reviewed-source-attribution` 或 `audio-anchor-reviewed` 只表示所记录的审核方式，不能用写入标签代替核实。未知片段保持 `unknown`；不从标题、嘉宾名单、第一人称或交替句式推断姓名。多人原文不默认增加立正的立场权重。

## 全库的本地候选

`scripts/build_dialogue_candidates.py` 从明确的候选 inventory 和完整 hash 校验的根复核字幕生成本地 JSON。它核对 source、AI 分片、拒绝项、原始与后续修订 receipt 和不可变父链；保留全部 cue 的文字与起止时间。默认 dry-run，`--apply` 仅写新建的 `.source-cache/` 子目录，不覆盖已有回执或原媒体／字幕。

候选覆盖来自既有多人分类与播客对谈分类的并集。这些标记不等于每项都是已核实的对谈，也不等于具有新的公开权限。所有自动转换的说话人先保留未知；AI 文字校对与改动复核不能称作逐句听校。现有人工字幕来源、原全文是否确实通读、剩余待核数量和人工音频核验分别记录。

`scripts/search_dialogue_candidates.py --pack .source-cache/<候选批次> --verify-only` 校验完整回执、文件与输入 hash；同一命令后带问题可在本机直接搜索。它只读取该回执列出的 raw 文件，不扫描整个日志、会员目录或私人文件，不接入公共产品。

## 从候选到公共语料

新公共 payload 需核对视频身份、当前匿名访问状态、原媒体／字幕质量、参与者归属、第三方私事及明确的权利分类，并展示准确变更、目的地和受众后取得批准。视频公开状态、允许收录文字与个人认同是三项不同事实。未公开材料仅留本地；原有会员字幕的精确授权快照不因为转换工具运行而更新。不得把局部成功、AI 校对成功或未知归属标成全部对谈已完成。

新逐字稿若公开到 `corpus/dialogues/`，还需完整的来源、日期、许可、权利和质量字段，并纳入具体收录政策及 release validator 的身份／hash 检查。仅有 JSON 解析支持不构成发布门禁。先原文，后按需要生成提炼；提炼可删改重建，始终回到实际原话核对。
