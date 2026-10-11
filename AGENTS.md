# Agent Guide

Open Context is the shared public data repository for Lizheng's source texts and structured catalog. The website presents this data; Context Infra builds retrieval and answers from pinned releases. See [the architecture](docs/conversation-architecture.md).

## Data ownership

- Published originals and media are the primary evidence. Open Context owns their traceable records; preserve the source URL, publication date, captured version and actual authorship when calibrating text or facts.
- Maintain public guest identities, names, aliases, programmes and participation in `catalog/guests.json`; maintain published reading links in `catalog/guest-articles.json`.
- Preserve stable entity and source IDs. Update facts at their owner, then regenerate consumer snapshots.
- Never edit derived copies by hand: `scripts/derive_catalogs.py` writes the guest names, programme titles and `dialogue_path` in `catalog/videos.jsonl`, the appearance `index`, and `catalog/guest-names.json`; `--write-manifest` runs it and validation fails while a copy is stale.
- Keep faithful text, timestamps, speaker attribution, quality and provenance in `corpus/`. Maintain AI summaries and reading aids separately, linked to their sources.
- Keep media, private drafts, processing evidence and local caches with their owning projects.
- Build correctness from stable IDs, source relationships, separate raw and derived layers, and pinned consumer snapshots. Generate counts from data. Tests verify these contracts; adding checks is not a substitute for fixing data ownership or an ambiguous model.

## Answering

1. Retrieve the relevant sources and preserve their author, date, URL and timestamp.
2. Distinguish source quotations, synthesis and inference. Attribute each speaker's words to that speaker; use the recorded status for unresolved turns.
3. Preserve publication dates and changes in views. Interpret translations through their originals and syntheses through their cited sources.
4. Recommend sources that help the question and explain their relevance. Treat search scores as relevance scores.
5. Inherit the source metadata on every retrieval chunk. Use the [source model](docs/source-model.md) and [answering contract](docs/answering-contract.md).

## Inclusion and rights

The committed policies bind the approved public snapshots. New material follows the policy for its source type and requires review of the exact public payload and destination.

| Material | Inclusion contract |
|---|---|
| First-party posts and public comments | `config/community-comment-policy.json`; preserve authorship and source links, remove surrounding member/private information |
| Solo-video text | `config/video-transcript-allowlist.txt` and the video rights policies |
| Member-video snapshot | `config/member-video-policy.json`; solo classifications in `config/member-solo-review.json` |
| Named conversation texts and quotations | `config/values-conversations-policy.json`; quoted text must match its source and time |
| Structured public dialogues | `config/public-dialogue-policy.json`; source identity, exact file hashes, visibility and rights |
| Course texts | `config/member-course-policy.json` |
| Chinese book and blog editions | `config/chinese-editions-policy.json`; retain original authors and translation status |
| English community articles | `config/english-source-policy.json`; retain authors, translator, publisher and rights |

Each source retains its license. Reference-use material supports reading, search, free Q&A and short quotation of at most 500 characters per document; paid reuse requires permission. Third-party works retain their authors' rights. See [LICENSE.md](LICENSE.md).

Private messages, unrelated member content, personal data, unpublished material, internal operations, credentials and private media stay outside the public release.

## Validation and releases

Run `python3 scripts/validate_release.py --write-manifest` to validate and generate `release-manifest.json`, `REUSE.toml`, `INDEX.md` and `index/`. These generated files share the same release inputs.

A push to main releases the approved data and triggers ask-lizheng's `update-context` workflow. Consumers record the upstream commit and manifest hash. Code and retrieval changes belong in the consuming repositories; material data or rights changes need explicit maintainer approval.
