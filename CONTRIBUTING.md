# Contributing

Contributions that improve retrieval, provenance, corrections, accessibility, and public-source coverage are welcome.

## Submit a derivative project

If you built a public Skill, Agent, search tool, or other project from this repository, add it to [`COMMUNITY-PROJECTS.md`](COMMUNITY-PROJECTS.md) in a pull request. Include a working public link, the author, the project form, a concrete one-sentence description, and a Superlinear community post where people can see the project, discuss tradeoffs, or follow later updates.

Listing is for discovery, not official endorsement. A submitted project must identify this repository as a source, preserve the applicable licenses, distinguish sourced material from synthesis or inference, and avoid private community content or unlicensed third-party text. You are also welcome to share the project in [Share Your Projects](https://www.superlinear.academy/c/share-your-projects?utm_source=github&utm_medium=referral&utm_campaign=lizheng_open_context) before opening the pull request.

Before opening a pull request:

1. confirm the canonical URL and original access state;
2. confirm the author or speaker and set the correct rights scope;
3. do not paste private messages, another member's content, leaked material, credentials, or personally identifying data; author-owned Superlinear posts from member spaces are accepted only through the maintainer's reviewed export;
4. preserve publication dates and source links;
5. run `python3 scripts/validate_release.py --write-manifest`, then `python3 scripts/validate_release.py`; the first regenerates `INDEX.md`, `index/`, `REUSE.toml`, and the manifest, which are never edited by hand;
6. describe whether the change adds source material, changes interpretation, or only fixes tooling.

A new full video transcript also requires a deliberate entry in `config/video-transcript-allowlist.txt`. Absence from the guest index is not approval. If a title, guest record, or manual exclusion conflicts with the allowlist, the export must fail until a maintainer resolves the classification.

New community comments must pass `config/community-comment-policy.json`. Do not work around the filter by manually copying a member name, surrounding conversation, contact detail, or private-context fragment into the corpus.

Do not open a public issue containing the sensitive material you want removed. Identify only the repository path and the reason at the minimum level needed for maintainers to act.

## Licensing of contributions

By contributing, you agree that code and documentation you add, including entries in `COMMUNITY-PROJECTS.md`, are licensed under MIT, and entries you add to `catalog/` or `config/` under CC0 1.0, matching [`LICENSE.md`](LICENSE.md). Do not submit content you do not have the right to license this way. New source material keeps its own declared `license` and needs maintainer review.
