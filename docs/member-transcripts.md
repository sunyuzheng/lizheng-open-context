# 会员字幕维护

2026-10-02，频道发布者明确要求将本地归档的全部218份会员视频字幕补入Open Context，供问问立正检索与回答，并突出显示会员来源。精确授权范围、标题、日期、字幕来源与输入SHA-256保存在[`../config/member-video-policy.json`](../config/member-video-policy.json)。本次新增215份全文，3份既有已审阅主讲字幕保留原文并补标会员身份；209条视频此前不在目录中。

`source_visibility=members-only`描述原视频，`text_access=public`描述获授权开放的文字。`membership_platform=youtube`及加入链接仅对应YouTube频道会员；不改变问问立正的免费次数或Superlinear Founding验证。字幕与视频会员身份在每个检索块上保留，模型不负责生成徽标、会员链接或时间码。

新字幕未做逐段说话人划分，因此使用`mixed-or-unresolved`，原始说话人、嘉宾、提问和引文不可整体归成立正。采用`publisher-authorized-transcript`与`LicenseRef-Original-Rights-Retained`，记录发布者的收录授权，不声称获得嘉宾的新许可。已有单讲审阅不因本次更新失效。此例外只覆盖指定218条，不为后来任意会员视频自动授权。

字幕来源包括20份Studio导出、55份人工字幕、18份本地精校（其中5份时间格式已规范化）、11份未校正Qwen转录、114份来源未确认的本地字幕。校对状态不是收录门槛；未知不写成人工字幕，ASR不写成精校。四份仅有Studio显示日期的资料使用日期级精度，不补造时刻。原始字幕文件与私有路径不复制到公开仓库；联系方式和本地路径按原有规则替换。

```sh
# 默认只验证输入与列出本地变更；--apply也只写本地，不推送或部署。
python3 scripts/import_member_transcripts.py --archive /path/to/member-transcript-archive
python3 scripts/import_member_transcripts.py --archive /path/to/member-transcript-archive --apply
python3 -m unittest discover -s tests -q
python3 scripts/validate_release.py --write-manifest
python3 scripts/validate_release.py
```

重复运行按YouTube ID合并；已有文本不重复增加。公开频道导出会保留这批独立授权快照，归属重建不会把多人字幕升级为本人直接立场。后续新字幕或访问状态改变应更新明确政策与哈希，经审阅重新导入；不只依标题中的“限免”判断。

下游问问立正先用`scripts/sync_context.py`同步哈希校验包，再重建语义索引。最终回答的出处快照、主页消费端及独立Ops读取端都必须接受这些可选访问字段，避免会员来源导致归档拒绝。公开发布仍需审阅精确差异与目的地。
