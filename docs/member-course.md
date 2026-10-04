# 《真本事》课程文字稿维护

2026-10-04，作者明确要求把超线性学院会员课程《真本事》（课程空间 `work-wealth`，ID 1858870）23节视频课下方的文字稿补入 Open Context，供问问立正检索与回答。精确范围、标题、日期和每课文字的 SHA-256 在 [`../config/member-course-policy.json`](../config/member-course-policy.json)。四个只放课件的条目没有文字，不在其中。

`source_visibility=members-only` 描述原课程，`text_access=public` 描述获授权开放的文字，`membership_platform=superlinear`；课程视频、课件、作业、评论和其他课程都不在授权范围内。作者保留文字稿的原有权利（`LicenseRef-Original-Rights-Retained`），不随本仓库的 CC 许可再授权。每份文件开头标明「会员课程」，并链接课程页面。

```sh
# 输入是 Circle Admin API 对该课程空间 course_lessons 的导出（私有，不进仓库）。
# 默认只核对输入与授权清单；--apply 只写本地，不推送或部署。
python3 scripts/import_member_course.py --export /path/to/zhenbenshi-course-export.json
python3 scripts/import_member_course.py --export /path/to/zhenbenshi-course-export.json --apply
python3 -m unittest discover -s tests -q
python3 scripts/validate_release.py --write-manifest
python3 scripts/validate_release.py
```

课文改动后哈希会对不上，导入会拒绝：先审阅新文字，再更新授权清单里的哈希。下游问问立正用 `scripts/sync_context.py` 同步哈希校验包，再重建语义索引。公开发布仍需审阅精确差异与目的地。
