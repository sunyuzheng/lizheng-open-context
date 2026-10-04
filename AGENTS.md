# Agent Guide

This repository is a source-grounded public context pack, not a persona simulator.

## When answering from this repository

1. Retrieve before answering.
2. Distinguish a direct source, a synthesis across sources, and your own inference.
3. Cite the original title, date, URL, and video timestamp when available.
4. Prefer the current thesis for durable positioning; preserve dated posts, comments, and videos as dated views.
5. If sources disagree, show the change or tension. Do not silently blend them.
6. Recommend only sources that materially help the question, and explain why each one fits.
7. Do not claim that an answer is what Yuzheng "would say" unless it is a direct, current quotation.
8. Do not turn heuristics, book frameworks, or working lenses into diagnoses, universal laws, guarantees, or rigid instructions.
9. Respect each source's `license`. Quote `LicenseRef-Lizheng-Reference-Use-1.0` material (the 真本事 course texts and member video transcripts) briefly, at most 500 characters from one document per quotation, with its source link; never reproduce it in full, and do not use it in a paid product without permission. `LicenseRef-Original-Rights-Retained` material is reference only.

## Privacy and rights

- When answering, use only committed material in this repository and its source URLs. Maintainer-authorized local updates may stage new public source snapshots for review.
- Never import private messages, unrelated members' posts or comments, member profiles, personal data, credentials, unpublished creative drafts, internal operations, or commercial secrets. The explicit English-source allowlist and AI translations of included solo videos are the narrow maintainer-authorized exceptions described below.
- The main Superlinear post/comment corpus is published by `YZ｜立正`; AI-written syntheses name AI as writer and Yuzheng as publisher. Explicit author authorization covers the committed first-party text even when the original Circle space required membership; it does not cover surrounding member content.
- Community comments must be originally public replies on included public Yuzheng-authored posts and pass `config/community-comment-policy.json`; retain the canonical comment link but remove member mention names, contact data, inline links, third-party quotations, and private or sensitive-personal context.
- Do not add full guest-interview transcripts without documented permission and an explicit rights classification. The maintainer explicitly authorized the exact 218 member-video snapshot in `config/member-video-policy.json` on 2026-10-02. This narrow inclusion exception uses `publisher-authorized-transcript` for mixed/unresolved speech under `LicenseRef-Lizheng-Reference-Use-1.0` (to the extent of Yuzheng's rights; guests keep the rights in their own words) and never attributes an entire conversation to Yuzheng. It is not a general guest transcript allowlist or new guest license grant. The 45 member videos listed in `config/member-solo-review.json` were reviewed as Yuzheng speaking alone and are his own speech (`solo-yuzheng`, `primary-speech`) under the same members-only access and license; never move a video into that list without reading its transcript for other speakers.
- A first-party video transcript must also appear in `config/video-transcript-allowlist.txt`; absence from guest metadata is not approval.
- The maintainer explicitly authorized the exact 23 *真本事* course lesson texts in `config/member-course-policy.json` on 2026-10-03: first-party text from a members-only course, open for reading, retrieval, Q&A, and short quotation under `LicenseRef-Lizheng-Reference-Use-1.0` (`publisher-authorized-course-text`). It does not cover course videos, slides, assignments, comments, other courses, or later lessons.
- Use the committed author-owned *真本事* framework reference. Do not import the publisher's layout, illustrations, scans, or third-party material unless rights are separately documented.
- English community content explicitly selected in `config/english-source-policy.json` may be included with original authors, publishing account, source URL, translation/repost notice, and retained third-party rights. Never assign these community views to Yuzheng. This exception does not authorize unrelated member content.
- AI translations of already included solo videos may be added as separately labeled reading aids. Original source publication and AI generation dates must remain separate; translated words are not original English speech.
- AI-written context syntheses and examples name AI as writer. Publication, permission to include, and personal endorsement are distinct; synthesis never independently proves Yuzheng's beliefs. Preserve attribution on every retrieval chunk.
- Every file has exactly one license; [`LICENSE.md`](LICENSE.md) explains the five kinds. Content files declare it in front matter, and `scripts/rights.py` derives `REUSE.toml` from those declarations. Never hand-edit `REUSE.toml`, `INDEX.md`, or `index/`; `python3 scripts/validate_release.py --write-manifest` regenerates them with the manifest.
- Run `python3 scripts/validate_release.py` before proposing a public release.

## Contributions

Keep provenance machine-readable. A new corpus item needs a stable source URL, public publication date when available, author/speaker classification, rights scope, and content license. Material changes to the source model or rights policy require explicit maintainer review.
