---
id: "youtube-9kh1YvzZYks-en-ai"
title: "A/B Testing: Important but Little-Known Insights | Class Representative Data Masterclass 5"
author: "AI"
original_author: "Yuzheng Sun"
publisher: "Yuzheng Sun"
source_type: "video-translation"
source_video_id: "9kh1YvzZYks"
source_url: "https://www.youtube.com/watch?v=9kh1YvzZYks"
original_source_url: "https://www.youtube.com/watch?v=9kh1YvzZYks"
source_family: "https://www.youtube.com/watch?v=9kh1YvzZYks"
published_at: "2025-09-24T19:36:08Z"
generated_at: "2026-04-19T20:59:48Z"
snapshot_at: "2026-09-17"
translation_publication_status: "repository-reading-aid-not-platform-publication"
language: "en"
original_language: "zh"
content_origin: "ai-translation"
generation_method: "ai-translation"
generation_model: "gpt-5.2"
evidence_role: "translation"
yuzheng_stance_weight: "verify-original"
rights_scope: "first-party-derivative"
license: "CC-BY-4.0"
third_party_exclusions: true
content_status: "current"
cue_alignment_status: "verified-against-source-srt"
source_context: "AI-generated English reading aid for an already published, included solo presentation. Publication date belongs to the original video, not to this English translation."
attribution_note: "AI-translated English, NOT Yuzheng's original English wording. Original speaker: Yuzheng Sun. Quoted community authors, audience questions and other people's experiences remain theirs, even if read aloud by Yuzheng. Verify speaker/quotation boundaries and exact claims against the original timestamped source. This translation and its Chinese source are one source family, not independent corroboration."
---

<!-- provenance:start -->
> Attribution / 归属：AI-translated English, NOT Yuzheng's original English wording. Original speaker: Yuzheng Sun. Quoted community authors, audience questions and other people's experiences remain theirs, even if read aloud by Yuzheng. Verify speaker/quotation boundaries and exact claims against the original timestamped source. This translation and its Chinese source are one source family, not independent corroboration.
<!-- provenance:end -->

# A/B Testing: Important but Little-Known Insights | Class Representative Data Masterclass 5

[00:00:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=3s) Hi, everyone.

[00:00:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=3s) Today I'm going to walk you through this—systematically and end to end.

[00:00:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=7s) A/B testing.

[00:00:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=7s) So you can go straight to the

[00:00:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=10s) highest-level understanding of A/B testing.

[00:00:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=11s) Why am I so confident I can say that?

[00:00:12](https://www.youtube.com/watch?v=9kh1YvzZYks&t=12s) Because I actually worked at Amazon

[00:00:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=14s) and at Meta.

[00:00:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=16s) Back then,

[00:00:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=16s) I realized very early on how important A/B testing is,

[00:00:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=18s) and I put out a lot of videos about A/B testing.

[00:00:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=21s) The company I'm at now,

[00:00:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=22s) Statsig, is the leading

[00:00:24](https://www.youtube.com/watch?v=9kh1YvzZYks&t=24s) A/B testing software on the market,

[00:00:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=25s) or you could say an A/B testing platform provider.

[00:00:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=27s) We're a SaaS company.

[00:00:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=28s) Companies like OpenAI, Anthropic, Atlassian, Notion, and Figma

[00:00:32](https://www.youtube.com/watch?v=9kh1YvzZYks&t=32s) are all our customers.

[00:00:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=33s) And here, as an evangelist,

[00:00:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=35s) my job is to

[00:00:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=37s) not only work with our customers,

[00:00:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=38s) but also keep exchanging ideas—academically and in practice—with many so-called industry leader (industry leaders).

[00:00:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=41s) through ongoing discussions.

[00:00:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=43s) I also have in-depth exchanges with companies like Lyft, DoorDash, and Netflix that aren't our customers.

[00:00:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=46s) I've personally had very deep conversations with them.

[00:00:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=48s) So I really do know

[00:00:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=48s) what the overall industry level looks like

[00:00:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=50s) and where I stand.

[00:00:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=52s) All right, let's jump in.

[00:00:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=52s) I'll break this into a few parts.

[00:00:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=54s) First: why do we run experiments?

[00:00:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=55s) What's the value of experimentation?

[00:00:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=56s) This is actually different from what a lot of people assume.

[00:00:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=58s) Second, I'll focus on the goals of experiments

[00:01:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=61s) and explain

[00:01:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=62s) how an experimentation system should really be set up.

[00:01:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=64s) How should we

[00:01:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=65s) build our experimentation system around those goals?

[00:01:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=67s) Third, I'll cover

[00:01:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=69s) the most basic and most important statistics you need for A/B testing.

[00:01:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=71s) hypothesis testing (hypothesis testing)

[00:01:13](https://www.youtube.com/watch?v=9kh1YvzZYks&t=73s) and why

[00:01:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=74s) the hypothesis testing taught in textbooks is wrong.

[00:01:17](https://www.youtube.com/watch?v=9kh1YvzZYks&t=77s) It mixes Fisher's p-value framework

[00:01:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=79s) with the Neyman–Pearson

[00:01:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=81s) hypothesis testing framework

[00:01:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=83s) and blends them together inconsistently.

[00:01:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=85s) That creates a lot of misunderstandings.

[00:01:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=87s) So basically, what you learn

[00:01:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=88s) about applying hypothesis testing in A/B tests

[00:01:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=91s) rests on an inconsistent foundation,

[00:01:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=93s) and it's mostly wrong.

[00:01:34](https://www.youtube.com/watch?v=9kh1YvzZYks&t=94s) So we need to build the right foundation.

[00:01:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=96s) And on top of that,

[00:01:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=96s) I'll introduce three relatively advanced tests.

[00:01:39](https://www.youtube.com/watch?v=9kh1YvzZYks&t=99s) One is CUPED (a regression-adjusted variance reduction method),

[00:01:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=100s) a.k.a. regression adjustment.

[00:01:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=102s) Another is Bayesian methods.

[00:01:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=103s) What's the difference between Bayesian and frequentist approaches,

[00:01:45](https://www.youtube.com/watch?v=9kh1YvzZYks&t=105s) and what are frequentists actually doing?

[00:01:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=106s) How should you think about them?

[00:01:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=108s) And why do we do sequential testing?

[00:01:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=110s) As for things like switchback tests,

[00:01:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=112s) grid search,

[00:01:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=112s) and geo testing,

[00:01:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=113s) I'll briefly explain what they are.

[00:01:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=115s) But they won't be the focus.

[00:01:57](https://www.youtube.com/watch?v=9kh1YvzZYks&t=117s) All right—let's get started.

[00:01:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=118s) First: why do we run experiments?

[00:01:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=119s) A lot of people have a misunderstanding.

[00:02:00](https://www.youtube.com/watch?v=9kh1YvzZYks&t=120s) They think we run experiments

[00:02:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=121s) to see whether the result is positive

[00:02:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=123s) and then decide whether to launch it.

[00:02:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=125s) But I want to emphasize one thing:

[00:02:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=127s) the value of experimentation

[00:02:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=129s) comes from surprises.

[00:02:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=131s) The goal of running an experiment

[00:02:12](https://www.youtube.com/watch?v=9kh1YvzZYks&t=132s) isn't to confirm your original 'good' idea.

[00:02:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=135s) It's to challenge your idea.

[00:02:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=136s) If a good idea gets validated by your experiment,

[00:02:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=138s) The experiment itself doesn't create any value.

[00:02:20](https://www.youtube.com/watch?v=9kh1YvzZYks&t=140s) All the value comes from the idea.

[00:02:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=142s) But if an idea you think is good turns out—through an experiment—

[00:02:24](https://www.youtube.com/watch?v=9kh1YvzZYks&t=144s) to be a bad idea,

[00:02:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=145s) or

[00:02:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=146s) an idea you thought was nothing special

[00:02:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=148s) turns out to be a great idea,

[00:02:30](https://www.youtube.com/watch?v=9kh1YvzZYks&t=150s) that's the value of experimentation.

[00:02:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=151s) In Ron Kohavi's book,

[00:02:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=153s) he talks about this:

[00:02:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=153s) Bing Search made a very, very small change

[00:02:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=155s) and it led to a sales lift worth hundreds of millions of dollars.

[00:02:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=157s) That—both the positive and the negative—is the value of experiments.

[00:02:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=160s) And in Ron Kohavi's book and papers,

[00:02:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=162s) he also mentions

[00:02:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=163s) that at the companies he worked at,

[00:02:45](https://www.youtube.com/watch?v=9kh1YvzZYks&t=165s) especially early on,

[00:02:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=166s) the success rate of hypotheses was only 3% to 30%,

[00:02:49](https://www.youtube.com/watch?v=9kh1YvzZYks&t=169s) usually around 20%.

[00:02:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=170s) So the value of experiments comes from surprise.

[00:02:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=173s) And about 80% of the time, you'll be surprised.

[00:02:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=175s) In other words, when you run an experiment,

[00:02:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=178s) if you write your hypothesis down—

[00:02:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=179s) like, 'If I ship this feature,'

[00:03:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=181s) 'what metric change will it drive?'

[00:03:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=183s) Most of the time we build a feature

[00:03:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=184s) because we expect it to move metrics in a positive direction.

[00:03:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=186s) But 80% of the time, when you test,

[00:03:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=188s) you'll find that it doesn't hold.

[00:03:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=189s) Why is that so important?

[00:03:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=191s) Because you might assume your metrics grow like this,

[00:03:13](https://www.youtube.com/watch?v=9kh1YvzZYks&t=193s) but if you don't actually know

[00:03:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=195s) which launched features are positive

[00:03:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=196s) and which are negative,

[00:03:17](https://www.youtube.com/watch?v=9kh1YvzZYks&t=197s) you'll have a lot of things you thought were positive

[00:03:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=199s) that are actually negative.

[00:03:20](https://www.youtube.com/watch?v=9kh1YvzZYks&t=200s) Then your metric growth

[00:03:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=201s) goes up and down,

[00:03:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=202s) up and down,

[00:03:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=203s) and it's hard for that to compound.

[00:03:24](https://www.youtube.com/watch?v=9kh1YvzZYks&t=204s) If you do experimentation well,

[00:03:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=206s) even if you don't do anything extra because of it,

[00:03:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=208s) even if you change nothing else—

[00:03:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=209s) as long as you kill features

[00:03:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=211s) that have a negative impact,

[00:03:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=213s) you can get a much higher growth curve.

[00:03:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=216s) That's the most fundamental meaning of experimentation.

[00:03:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=218s) (The value of experiments comes from surprise.)

[00:03:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=221s) So we should do everything we can to

[00:03:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=223s) increase experimentation coverage.

[00:03:45](https://www.youtube.com/watch?v=9kh1YvzZYks&t=225s) We want every new feature we build

[00:03:47](https://www.youtube.com/watch?v=9kh1YvzZYks&t=227s) to be tested.

[00:03:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=228s) Not, 'I think this idea is good,'

[00:03:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=230s) 'I'm confident in it,'

[00:03:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=230s) 'so I'll run an experiment.'

[00:03:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=231s) You see a lot of companies doing experiments ad hoc,

[00:03:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=234s) and the result is

[00:03:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=235s) they only test the things they're confident about.

[00:03:57](https://www.youtube.com/watch?v=9kh1YvzZYks&t=237s) They only put those into experiments.

[00:03:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=238s) That basically isn't very meaningful.

[00:03:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=239s) At this point some of you might ask:

[00:04:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=241s) Can we really experiment on 100% of things?

[00:04:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=242s) Is that even possible?

[00:04:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=243s) I'm telling you—it absolutely is.

[00:04:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=244s) Companies like Meta do exactly that.

[00:04:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=247s) And many of our Statsig customers

[00:04:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=248s) including OpenAI do it the same way.

[00:04:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=251s) Among companies that aren't Meta and don't use our product,

[00:04:13](https://www.youtube.com/watch?v=9kh1YvzZYks&t=253s) so far I know one: Canva.

[00:04:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=255s) That Canva—the 'Photoshop for the web.'

[00:04:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=258s) They do it this way too.

[00:04:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=258s) There's a key technical insight here:

[00:04:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=261s) How do you actually make this happen?

[00:04:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=262s) You have to design feature gates and experiments

[00:04:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=265s) as a single object.

[00:04:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=267s) At Meta,

[00:04:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=267s) they call it Gatekeeper and Delta.

[00:04:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=269s) Anyway, a feature gate

[00:04:30](https://www.youtube.com/watch?v=9kh1YvzZYks&t=270s) is a conditional rule

[00:04:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=271s) that decides whether this feature

[00:04:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=273s) the user can actually see it.

[00:04:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=275s) You can set all kinds of conditions.

[00:04:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=276s) For example: are they an internal employee?

[00:04:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=278s) If you only need an internal test,

[00:04:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=280s) you make the feature visible only to employees

[00:04:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=282s) and invisible to people outside the company.

[00:04:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=283s) Or you can say, '10% in Canada,'

[00:04:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=286s) or '50% in the U.S.'

[00:04:47](https://www.youtube.com/watch?v=9kh1YvzZYks&t=287s) You can set the corresponding conditional rules.

[00:04:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=290s) Or target iOS,

[00:04:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=291s) or Android.

[00:04:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=292s) In practice, 100% of users

[00:04:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=293s) receive the code,

[00:04:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=294s) but the feature gate

[00:04:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=296s) is a layer of configuration on top

[00:04:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=298s) that controls whether a given user

[00:05:00](https://www.youtube.com/watch?v=9kh1YvzZYks&t=300s) can see the feature.

[00:05:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=302s) In U.S. companies at least,

[00:05:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=303s) this is basically standard.

[00:05:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=304s) These days, when you launch a feature,

[00:05:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=306s) you almost always use feature gates

[00:05:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=308s) to do a staged rollout.

[00:05:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=310s) That is,

[00:05:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=310s) you gradually roll it out—1% first,

[00:05:13](https://www.youtube.com/watch?v=9kh1YvzZYks&t=313s) see if there are any bugs,

[00:05:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=314s) then 10%, then 100%.

[00:05:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=315s) Last year's CrowdStrike airport blue-screen incident

[00:05:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=319s) was because they didn't use feature gates.

[00:05:20](https://www.youtube.com/watch?v=9kh1YvzZYks&t=320s) A lot of people online roasted them for it.

[00:05:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=321s) Like, something this basic—

[00:05:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=322s) it's already 2024,

[00:05:24](https://www.youtube.com/watch?v=9kh1YvzZYks&t=324s) and you still aren't using something this basic?

[00:05:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=325s) It's become the default

[00:05:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=327s) developer best practice.

[00:05:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=329s) In that situation,

[00:05:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=329s) a feature gate

[00:05:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=331s) decides whether a user sees

[00:05:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=333s) a feature or not.

[00:05:34](https://www.youtube.com/watch?v=9kh1YvzZYks&t=334s) If you add randomization on top of that,

[00:05:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=336s) it becomes an A/B test.

[00:05:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=337s) So at the system level,

[00:05:39](https://www.youtube.com/watch?v=9kh1YvzZYks&t=339s) when you design things,

[00:05:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=340s) you make feature gates and experiments

[00:05:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=341s) the same kind of object.

[00:05:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=343s) Then you just take a feature gate

[00:05:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=344s) add randomization,

[00:05:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=346s) and add your stats engine

[00:05:47](https://www.youtube.com/watch?v=9kh1YvzZYks&t=347s) to do the statistical calculations,

[00:05:49](https://www.youtube.com/watch?v=9kh1YvzZYks&t=349s) and you can run experiments on 100% of features.

[00:05:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=351s) Every feature can be experimented on.

[00:05:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=353s) Because for that feature,

[00:05:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=354s) you don't need any additional setup.

[00:05:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=355s) When an engineer builds a feature,

[00:05:57](https://www.youtube.com/watch?v=9kh1YvzZYks&t=357s) during rollout,

[00:05:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=358s) they're already using a feature gate.

[00:05:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=359s) And naturally,

[00:06:00](https://www.youtube.com/watch?v=9kh1YvzZYks&t=360s) you get the corresponding experiment for free.

[00:06:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=362s) In the end, you just need your system

[00:06:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=364s) to plug in the metrics via the stats engine,

[00:06:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=367s) and then you can choose

[00:06:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=369s) for any feature shipped through a feature gate

[00:06:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=371s) whether you want to look at its experiment readout.

[00:06:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=374s) That's the underlying infra.

[00:06:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=375s) And that's why

[00:06:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=376s) Meta's A/B testing system can be so strong.

[00:06:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=378s) And an infra like this

[00:06:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=379s) also, behind the scenes,

[00:06:20](https://www.youtube.com/watch?v=9kh1YvzZYks&t=380s) brings another really important aspect of A/B testing:

[00:06:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=383s) a cultural one.

[00:06:24](https://www.youtube.com/watch?v=9kh1YvzZYks&t=384s) That cultural aspect

[00:06:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=385s) is

[00:06:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=386s) it gives frontline engineers a lot of agency

[00:06:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=389s) without needing everyone to reach consensus before building.

[00:06:32](https://www.youtube.com/watch?v=9kh1YvzZYks&t=392s) If you don't do experiments,

[00:06:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=393s) the culture at most companies is:

[00:06:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=396s) we discuss first,

[00:06:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=396s) reach a consensus,

[00:06:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=398s) or make a plan,

[00:06:39](https://www.youtube.com/watch?v=9kh1YvzZYks&t=399s) and then engineers implement it.

[00:06:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=401s) But in that case,

[00:06:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=401s) consensus-building takes a long time—

[00:06:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=404s) it can take weeks.

[00:06:45](https://www.youtube.com/watch?v=9kh1YvzZYks&t=405s) If you use experiments,

[00:06:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=406s) you'll find that the rollout itself

[00:06:49](https://www.youtube.com/watch?v=9kh1YvzZYks&t=409s) has a controllable scope.

[00:06:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=410s) So most companies

[00:06:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=411s) choose this path:

[00:06:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=412s) test behind a gate,

[00:06:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=415s) or test behind an experiment.

[00:06:57](https://www.youtube.com/watch?v=9kh1YvzZYks&t=417s) First, let's build a demo of this.

[00:06:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=419s) Then we decide what to do next.

[00:07:00](https://www.youtube.com/watch?v=9kh1YvzZYks&t=420s) For example, we can test it internally first.

[00:07:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=423s) Then we roll it out to 1% of users.

[00:07:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=425s) See if it has any major negative effects.

[00:07:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=427s) If it doesn't have any major negative effects,

[00:07:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=429s) we try 10%.

[00:07:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=429s) At that point you probably have enough users

[00:07:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=431s) to see whether it helps or hurts your metrics,

[00:07:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=434s) and by how much.

[00:07:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=435s) If it's still positive,

[00:07:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=436s) keep launching it to more users,

[00:07:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=438s) until you get to 100%.

[00:07:20](https://www.youtube.com/watch?v=9kh1YvzZYks&t=440s) Then 50% is test,

[00:07:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=441s) and 50% is control.

[00:07:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=442s) Once we've confirmed

[00:07:24](https://www.youtube.com/watch?v=9kh1YvzZYks&t=444s) this feature is actually beneficial,

[00:07:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=445s) we move the treatment,

[00:07:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=447s) the newly built feature,

[00:07:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=449s) to 100% of users.

[00:07:30](https://www.youtube.com/watch?v=9kh1YvzZYks&t=450s) The benefit of doing it this way is:

[00:07:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=451s) when we're discussing

[00:07:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=453s) whether this feature should launch,

[00:07:34](https://www.youtube.com/watch?v=9kh1YvzZYks&t=454s) or what percentage to launch it to,

[00:07:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=456s) we're bringing data,

[00:07:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=457s) and we're bringing the feature itself—

[00:07:39](https://www.youtube.com/watch?v=9kh1YvzZYks&t=459s) what it actually is.

[00:07:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=460s) It's already built,

[00:07:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=461s) so we don't have to argue

[00:07:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=463s) about a bunch of hypotheticals.

[00:07:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=463s) Otherwise,

[00:07:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=464s) that's why 80% of hypotheses are wrong.

[00:07:47](https://www.youtube.com/watch?v=9kh1YvzZYks&t=467s) When I interviewed MIT professor Kevin,

[00:07:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=470s) he mentioned

[00:07:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=470s) that 90% of their experiments are wrong too.

[00:07:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=472s) I asked him why,

[00:07:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=473s) and he said it's because all products today

[00:07:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=475s) are trying to do hard things.

[00:07:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=476s) If you were doing something easy,

[00:07:57](https://www.youtube.com/watch?v=9kh1YvzZYks&t=477s) you'd have a 100% success rate.

[00:07:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=479s) it probably wasn't worth doing in the first place.

[00:08:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=481s) Honestly.

[00:08:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=481s) Because our product is already very mature,

[00:08:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=484s) our ecosystem is already pretty complex,

[00:08:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=485s) so even small improvements are hard.

[00:08:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=486s) So the human brain just can't

[00:08:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=488s) before doing the work,

[00:08:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=489s) predict everything.

[00:08:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=491s) Here's an example.

[00:08:13](https://www.youtube.com/watch?v=9kh1YvzZYks&t=493s) When I was putting together case studies for companies,

[00:08:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=496s) there was one company:

[00:08:17](https://www.youtube.com/watch?v=9kh1YvzZYks&t=497s) Rec Room—in our real customer study—

[00:08:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=499s) they changed their UI,

[00:08:20](https://www.youtube.com/watch?v=9kh1YvzZYks&t=500s) and redesigned it into a completely new UI.

[00:08:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=502s) And their key metric,

[00:08:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=503s) the number of chat threads created,

[00:08:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=506s) dropped dramatically.

[00:08:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=507s) After you spot that big drop,

[00:08:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=509s) and then you look at the UI that looks amazing,

[00:08:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=511s) you get it.

[00:08:32](https://www.youtube.com/watch?v=9kh1YvzZYks&t=512s) That "message" button

[00:08:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=513s) used to be in the middle,

[00:08:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=515s) really prominent,

[00:08:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=516s) but it got moved to the corner.

[00:08:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=517s) Even though it's its own button,

[00:08:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=518s) it's tucked away in the corner,

[00:08:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=520s) so people can't find it.

[00:08:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=521s) Once you see the data,

[00:08:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=522s) and then you hear the explanation,

[00:08:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=523s) it makes total sense.

[00:08:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=524s) But if you don't look at the data,

[00:08:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=526s) and you only look at the UI,

[00:08:47](https://www.youtube.com/watch?v=9kh1YvzZYks&t=527s) I don't think anyone

[00:08:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=528s) would spot that problem.

[00:08:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=530s) That's also what Professor Xu keeps emphasizing:

[00:08:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=532s) intellectual honesty.

[00:08:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=533s) Human cognition is very narrow.

[00:08:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=536s) The way we understand the world is pretty shallow.

[00:08:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=538s) Our brains aren't well suited to dealing with complex environments.

[00:09:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=541s) That's why experiments are necessary:

[00:09:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=543s) they give us intellectual honesty.

[00:09:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=545s) They help us validate things,

[00:09:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=547s) and let the facts tell us

[00:09:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=548s) where our thinking falls short,

[00:09:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=550s) which is where the value comes from.

[00:09:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=551s) And it can make engineers better,

[00:09:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=554s) and build a culture with more agency,

[00:09:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=556s) so people can move faster,

[00:09:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=558s) instead of spending time debating

[00:09:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=561s) and arguing about things nobody can prove either way.

[00:09:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=563s) That's why we run experiments.

[00:09:24](https://www.youtube.com/watch?v=9kh1YvzZYks&t=564s) The second point I hinted at is:

[00:09:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=566s) around

[00:09:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=567s) a goal like this,

[00:09:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=568s) what kind of experimentation system should we build?

[00:09:30](https://www.youtube.com/watch?v=9kh1YvzZYks&t=570s) First, like I said earlier,

[00:09:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=571s) your feature gate and your experiment

[00:09:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=573s) should be the same object.

[00:09:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=575s) When I train other companies,

[00:09:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=577s) I tell them an experimentation system has three steps.

[00:09:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=580s) If you want to build an experimentation system,

[00:09:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=582s) there are usually three steps.

[00:09:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=583s) A/B testing is the easiest place to start,

[00:09:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=586s) but it's one of the hardest systems to scale.

[00:09:47](https://www.youtube.com/watch?v=9kh1YvzZYks&t=587s) If you just want to get started,

[00:09:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=588s) any data scientist can hand you

[00:09:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=590s) a notebook,

[00:09:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=591s) and you can run experiments.

[00:09:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=592s) You don't even need a notebook.

[00:09:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=593s) Give me a Google Sheet,

[00:09:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=594s) give me an Excel file,

[00:09:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=595s) and I can run an experiment for you.

[00:09:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=596s) Isn't it just putting one group in treatment and one group in control,

[00:09:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=598s) then running a t-test,

[00:09:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=599s) and calculating the standard error?

[00:10:00](https://www.youtube.com/watch?v=9kh1YvzZYks&t=600s) That math is really, really simple.

[00:10:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=603s) And with a notebook,

[00:10:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=604s) it seems like you can automate it.

[00:10:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=605s) But it's actually very easy to mess up.

[00:10:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=609s) And if everyone does it again themselves,

[00:10:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=611s) you'll find the results can be very different.

[00:10:12](https://www.youtube.com/watch?v=9kh1YvzZYks&t=612s) Randomization,

[00:10:13](https://www.youtube.com/watch?v=9kh1YvzZYks&t=613s) and assignment are also easy to get wrong.

[00:10:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=616s) So step two is usually to automate

[00:10:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=618s) the data in the middle—

[00:10:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=619s) automate all the calculations,

[00:10:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=621s) and automate as much of the pipeline as possible.

[00:10:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=622s) That lets a company

[00:10:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=625s) go from 5 experiments a year

[00:10:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=626s) to 50 a year.

[00:10:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=627s) But that still isn't enough.

[00:10:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=628s) Because at that point,

[00:10:30](https://www.youtube.com/watch?v=9kh1YvzZYks&t=630s) every experiment

[00:10:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=631s) still needs an engineer to help you set it up,

[00:10:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=633s) to set up the experiment,

[00:10:34](https://www.youtube.com/watch?v=9kh1YvzZYks&t=634s) and your

[00:10:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=635s) metrics, a lot of the time,

[00:10:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=636s) keep getting worse in terms of data quality.

[00:10:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=637s) So you need scalable

[00:10:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=640s) experimentation infrastructure,

[00:10:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=641s) you need to tie feature gates

[00:10:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=642s) and experiments together.

[00:10:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=644s) Then

[00:10:45](https://www.youtube.com/watch?v=9kh1YvzZYks&t=645s) engineers don't need to spend time

[00:10:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=646s) doing additional experiment setup.

[00:10:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=648s) experiments are default-on.

[00:10:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=650s) Then you can scale from 50 experiments to

[00:10:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=651s) 5,000, 50,000, 500,000 experiments.

[00:10:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=653s) It depends on your company,

[00:10:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=654s) how many features you're launching.

[00:10:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=656s) At that point, running experiments

[00:10:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=658s) won't slow anything down at all,

[00:11:00](https://www.youtube.com/watch?v=9kh1YvzZYks&t=660s) because experiments are basically free.

[00:11:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=662s) At this stage,

[00:11:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=663s) the constraint is how many new ideas they have.

[00:11:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=666s) Experimentation itself isn't a constraint.

[00:11:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=668s) Once you have a system like this,

[00:11:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=670s) I also talk about this:

[00:11:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=671s) data quality becomes important again.

[00:11:13](https://www.youtube.com/watch?v=9kh1YvzZYks&t=673s) Your data needs to be trustworthy.

[00:11:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=675s) People can trust the process,

[00:11:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=676s) but if they don't trust the data, it still won't work.

[00:11:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=678s) At Tencent,

[00:11:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=679s) I did a lot of data-cleaning work too.

[00:11:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=681s) I found you can get the data right at first,

[00:11:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=682s) but as time goes on,

[00:11:24](https://www.youtube.com/watch?v=9kh1YvzZYks&t=684s) the data gets worse again.

[00:11:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=685s) Why?

[00:11:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=685s) Because you have logging tables,

[00:11:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=687s) and you have metrics.

[00:11:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=688s) Those two

[00:11:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=689s) look like tables to everyone,

[00:11:30](https://www.youtube.com/watch?v=9kh1YvzZYks&t=690s) but in between,

[00:11:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=691s) there are lots of convoluted pipelines,

[00:11:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=693s) and lots of code.

[00:11:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=695s) That code is really hard to maintain,

[00:11:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=697s) and the pipeline data

[00:11:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=698s) is highly fragmented.

[00:11:39](https://www.youtube.com/watch?v=9kh1YvzZYks&t=699s) And analytics tenure is usually only 1 to 1.5 years,

[00:11:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=702s) so a lot of what gets built

[00:11:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=704s) walks out the door, and you don't even know what it does.

[00:11:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=706s) Then you can't change it.

[00:11:47](https://www.youtube.com/watch?v=9kh1YvzZYks&t=707s) You change something upstream,

[00:11:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=708s) and six layers down,

[00:11:49](https://www.youtube.com/watch?v=9kh1YvzZYks&t=709s) six steps later,

[00:11:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=710s) you find it breaks somewhere else.

[00:11:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=712s) And none of the data reconciles.

[00:11:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=713s) Like you're trying to reconcile revenue,

[00:11:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=714s) and reconcile, say,

[00:11:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=715s) active users.

[00:11:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=716s) In these convoluted pipelines,

[00:11:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=719s) finding a single source of truth

[00:12:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=721s) is really hard.

[00:12:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=722s) So the product our company provides

[00:12:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=724s) is a metrics catalog.

[00:12:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=725s) It adds a layer,

[00:12:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=726s) a productized layer,

[00:12:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=728s) with a visual, drag-and-drop interface,

[00:12:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=730s) so after you define your logging tables,

[00:12:13](https://www.youtube.com/watch?v=9kh1YvzZYks&t=733s) on top of those tables,

[00:12:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=736s) you can do all kinds of aggregations,

[00:12:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=738s) group-bys,

[00:12:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=739s) filtering,

[00:12:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=741s) and even set up time windows.

[00:12:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=743s) These basic operations

[00:12:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=745s) cover 80–90%,

[00:12:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=748s) and for most companies,

[00:12:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=749s) they cover basically 100%

[00:12:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=751s) of the step from logging to metrics.

[00:12:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=753s) Then all your metrics

[00:12:34](https://www.youtube.com/watch?v=9kh1YvzZYks&t=754s) live in one product,

[00:12:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=756s) centrally defined,

[00:12:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=757s) so everything is fully end-to-end traceable.

[00:12:39](https://www.youtube.com/watch?v=9kh1YvzZYks&t=759s) Any metric—like revenue—

[00:12:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=761s) you open it and you can see

[00:12:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=762s) which table it comes from,

[00:12:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=763s) how it's calculated,

[00:12:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=764s) what arithmetic was used,

[00:12:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=766s) whether it's a count, a sum,

[00:12:47](https://www.youtube.com/watch?v=9kh1YvzZYks&t=767s) a count distinct,

[00:12:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=768s) a percentile, or something else.

[00:12:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=770s) You can see whether the filters are set appropriately.

[00:12:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=771s) It's completely end-to-end traceable,

[00:12:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=773s) and everyone can understand it.

[00:12:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=774s) At that point,

[00:12:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=775s) your data is trustworthy.

[00:12:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=776s) Now you've got

[00:12:57](https://www.youtube.com/watch?v=9kh1YvzZYks&t=777s) simple definition on the experiment a simple definition of the experiment.

[00:12:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=778s) and you have trustworthy data.

[00:13:00](https://www.youtube.com/watch?v=9kh1YvzZYks&t=780s) Then you can do whatever it takes

[00:13:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=782s) to get your experiment coverage to 100%.

[00:13:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=784s) You can run more experiments,

[00:13:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=786s) and you can do what we talked about earlier:

[00:13:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=788s) use experiments to speed up development,

[00:13:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=791s) and understand, for every launch,

[00:13:13](https://www.youtube.com/watch?v=9kh1YvzZYks&t=793s) what impact that feature actually has.

[00:13:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=795s) That's the second point.

[00:13:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=796s) How you should design your experimentation system.

[00:13:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=798s) And at this point,

[00:13:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=799s) a lot of data scientists actually become counterproductive.

[00:13:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=802s) Data scientists—

[00:13:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=803s) especially junior data scientists—

[00:13:24](https://www.youtube.com/watch?v=9kh1YvzZYks&t=804s) or what I call

[00:13:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=806s) pedantic data scientists—

[00:13:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=807s) the more academic type—

[00:13:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=808s) those data scientists

[00:13:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=809s) have a really bad habit:

[00:13:30](https://www.youtube.com/watch?v=9kh1YvzZYks&t=810s) they think the value of their job

[00:13:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=813s) comes from making things complicated.

[00:13:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=815s) Not by making things simpler.

[00:13:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=817s) The simpler you make it,

[00:13:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=818s) the more standardized it is,

[00:13:39](https://www.youtube.com/watch?v=9kh1YvzZYks&t=819s) the more scalable the experiment becomes.

[00:13:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=822s) See? If you make the experiment complicated,

[00:13:45](https://www.youtube.com/watch?v=9kh1YvzZYks&t=825s) you have to ask yourself,

[00:13:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=826s) what value are you actually getting?

[00:13:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=828s) Is it worth it?

[00:13:49](https://www.youtube.com/watch?v=9kh1YvzZYks&t=829s) Because when you complicate it,

[00:13:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=830s) other people can’t understand it,

[00:13:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=832s) your experiment slows down,

[00:13:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=834s) your results become harder to communicate,

[00:13:57](https://www.youtube.com/watch?v=9kh1YvzZYks&t=837s) and it’s harder for the business side to buy in.

[00:13:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=839s) If that’s the case,

[00:14:00](https://www.youtube.com/watch?v=9kh1YvzZYks&t=840s) you shouldn’t be doing the complicated version.

[00:14:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=842s) Unless that complexity

[00:14:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=843s) is solving a real, existing problem.

[00:14:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=846s) I see a lot of data scientists who,

[00:14:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=848s) as soon as they see an experiment,

[00:14:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=849s) their first reaction is,

[00:14:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=850s) should we do some nonparametric test?

[00:14:12](https://www.youtube.com/watch?v=9kh1YvzZYks&t=852s) And should we do all kinds of

[00:14:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=854s) new experimental methods the papers talk about?

[00:14:17](https://www.youtube.com/watch?v=9kh1YvzZYks&t=857s) Should we use reinforcement learning?

[00:14:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=859s) Should we use GenAI?

[00:14:20](https://www.youtube.com/watch?v=9kh1YvzZYks&t=860s) To me, that’s all missing the point

[00:14:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=862s) of what an experiment is actually worth.

[00:14:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=863s) It’s like holding a hammer

[00:14:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=865s) and going around looking for a nail,

[00:14:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=866s) just to build your own career value.

[00:14:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=868s) Like I said in a previous video,

[00:14:30](https://www.youtube.com/watch?v=9kh1YvzZYks&t=870s) harder things are more valuable (the harder, the more valuable)

[00:14:32](https://www.youtube.com/watch?v=9kh1YvzZYks&t=872s) is a huge misconception.

[00:14:34](https://www.youtube.com/watch?v=9kh1YvzZYks&t=874s) That’s something school drills into us,

[00:14:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=876s) a deeply rooted mental trap.

[00:14:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=878s) We have to overcome it.

[00:14:39](https://www.youtube.com/watch?v=9kh1YvzZYks&t=879s) We need to understand it’s not

[00:14:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=880s) harder things are more valuable (the harder, the more valuable)

[00:14:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=882s) more valuable things are more valuable (valuable things are what’s valuable)

[00:14:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=884s) So what actually is valuable?

[00:14:45](https://www.youtube.com/watch?v=9kh1YvzZYks&t=885s) It’s making your experiments cover as much as possible

[00:14:47](https://www.youtube.com/watch?v=9kh1YvzZYks&t=887s) of your new feature development,

[00:14:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=890s) and constantly uncover surprises,

[00:14:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=893s) so they help you be more objective and more quantitative,

[00:14:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=896s) and use causal data

[00:14:57](https://www.youtube.com/watch?v=9kh1YvzZYks&t=897s) to guide your product’s evolution.

[00:14:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=899s) Alright—that’s the second big point.

[00:15:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=901s) Next:

[00:15:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=901s) how should we design an experimentation system?

[00:15:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=903s) And the third point is the corresponding statistical knowledge.

[00:15:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=905s) Here,

[00:15:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=906s) I want to give everyone watching

[00:15:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=908s) some essential statistical background.

[00:15:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=910s) In other words, when it comes to experiments—like I just said—

[00:15:12](https://www.youtube.com/watch?v=9kh1YvzZYks&t=912s) when we’re trying to run more of them, faster,

[00:15:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=914s) as data scientists,

[00:15:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=916s) how do we stay rigorous,

[00:15:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=918s) and improve the quality of decisions across the whole decision system?

[00:15:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=921s) First,

[00:15:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=922s) we need to understand hypothesis testing,

[00:15:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=923s) power,

[00:15:24](https://www.youtube.com/watch?v=9kh1YvzZYks&t=924s) minimum detectable delta,

[00:15:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=926s) and sample size—very clearly.

[00:15:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=927s) Why is that important?

[00:15:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=929s) Because experiments always involve a trade-off.

[00:15:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=933s) We usually assume sample size

[00:15:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=935s) is fixed.

[00:15:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=936s) Sample size is generally determined by your business,

[00:15:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=938s) by how many samples your business has,

[00:15:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=940s) and it’s hard to just increase it.

[00:15:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=941s) So in that situation,

[00:15:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=942s) the trade-off is:

[00:15:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=944s) the longer you run the experiment,

[00:15:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=946s) the smaller an effect you can detect.

[00:15:49](https://www.youtube.com/watch?v=9kh1YvzZYks&t=949s) you can be more accurate (more precise),

[00:15:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=951s) you can get more signal,

[00:15:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=952s) whatever you want to call it.

[00:15:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=953s) All of those are pointing to the same thing:

[00:15:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=956s) the longer you run the experiment,

[00:15:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=958s) the stronger the signal you get,

[00:15:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=959s) and the smaller the effect you can detect.

[00:16:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=962s) Now, if the feature you’re launching

[00:16:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=963s) is highly impactful,

[00:16:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=965s) say it delivers a 10% incremental lift,

[00:16:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=966s) then you might only need to run it for a few days

[00:16:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=968s) to know.

[00:16:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=968s) You’ll see it’s a great feature,

[00:16:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=970s) and you can just launch it.

[00:16:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=971s) What we really, as data scientists,

[00:16:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=974s) need to deal with

[00:16:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=974s) is usually more like this:

[00:16:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=975s) at a company like Meta,

[00:16:17](https://www.youtube.com/watch?v=9kh1YvzZYks&t=977s) can you detect a 0.1% or 0.2% effect?

[00:16:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=981s) At a more typical company,

[00:16:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=982s) it’s whether you can detect a 0.5%, 1%, or 2% effect.

[00:16:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=986s) In that case,

[00:16:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=987s) if you do certain things,

[00:16:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=989s) you might detect it in one or two weeks;

[00:16:32](https://www.youtube.com/watch?v=9kh1YvzZYks&t=992s) if you don’t,

[00:16:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=993s) it might take five weeks

[00:16:34](https://www.youtube.com/watch?v=9kh1YvzZYks&t=994s) or six weeks to detect.

[00:16:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=995s) There are a few important points here.

[00:16:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=997s) First,

[00:16:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=998s) running concurrent experiments is fine.

[00:16:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1000s) You should run lots of experiments in parallel.

[00:16:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1003s) Interaction effects usually aren’t a big problem.

[00:16:45](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1005s) That is, when a user

[00:16:47](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1007s) is in experiment A,

[00:16:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1008s) and also in experiment B,

[00:16:49](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1009s) are the readouts for experiment A and experiment B

[00:16:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1012s) still accurate?

[00:16:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1012s) In academia,

[00:16:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1014s) we treat that as a big deal.

[00:16:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1015s) But

[00:16:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1015s) if you actually look at empirical data,

[00:16:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1018s) you’ll find the problems are extremely rare.

[00:17:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1021s) It’s not worth designing your whole process around it,

[00:17:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1023s) like insisting you must run experiment A before B.

[00:17:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1025s) You can run A and B at the same time,

[00:17:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1027s) as long as they’re orthogonal.

[00:17:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1029s) You can run ten thousand experiments at once,

[00:17:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1030s) as long as they’re orthogonal.

[00:17:12](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1032s) If you’re worried they might interact,

[00:17:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1034s) there’s something called interaction-effects detection.

[00:17:17](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1037s) By “interaction,”

[00:17:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1039s) I mean a user

[00:17:20](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1040s) is in the treatment group of experiment A,

[00:17:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1042s) and also in the treatment group of experiment B.

[00:17:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1043s) Then you look at a two-by-two (2x2):

[00:17:24](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1044s) treat–treat vs. control–control,

[00:17:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1046s) and treat–control vs. control–treat,

[00:17:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1048s) and ask what the test effect really is.

[00:17:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1051s) Then you can see

[00:17:32](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1052s) what’s actually driving the treatment effect,

[00:17:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1053s) and where it’s coming from.

[00:17:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1055s) Only in rare cases

[00:17:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1056s) do interaction effects become a problem.

[00:17:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1058s) For example,

[00:17:39](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1059s) experiment A makes the text red,

[00:17:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1061s) and experiment B makes the background red—

[00:17:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1062s) combine A and B,

[00:17:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1063s) and you can’t see anything.

[00:17:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1064s) That’s a problem.

[00:17:45](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1065s) In cases like that,

[00:17:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1066s) you should call it out in your experiment design.

[00:17:49](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1069s) But in practice,

[00:17:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1072s) it’s extremely rare.

[00:17:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1073s) Don’t avoid concurrent experiments just because of these extreme edge cases,

[00:17:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1076s) and decide not to run concurrent experiments.

[00:17:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1078s) Be bold and run concurrent experiments,

[00:18:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1081s) because it can massively speed up experimentation.

[00:18:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1084s) In the same amount of time,

[00:18:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1085s) you can run many more experiments.

[00:18:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1086s) Second,

[00:18:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1087s) you need to do variance reduction.

[00:18:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1088s) Do everything you can to reduce variance.

[00:18:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1091s) But before that,

[00:18:12](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1092s) I probably have to talk about hypothesis testing.

[00:18:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1094s) In this episode,

[00:18:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1095s) because it’s something that really,

[00:18:17](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1097s) to explain clearly from start to finish,

[00:18:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1098s) takes at least 15 minutes,

[00:18:20](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1100s) so

[00:18:20](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1100s) I’ll link my English video here,

[00:18:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1102s) if you’re interested, go watch it.

[00:18:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1103s) And when I get the chance,

[00:18:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1105s) I’ll make a Chinese version too.

[00:18:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1106s) Anyway, hypothesis testing tells you how

[00:18:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1109s) sample size,

[00:18:30](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1110s) minimum detectable effect,

[00:18:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1111s) null hypothesis,

[00:18:32](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1112s) alternative hypothesis,

[00:18:34](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1114s) alpha,

[00:18:34](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1114s) beta,

[00:18:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1115s) and power relate to each other.

[00:18:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1116s) Once you understand those relationships,

[00:18:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1118s) you’ll realize sample size is basically fixed.

[00:18:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1121s) And the test itself—

[00:18:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1122s) your feature—determines what the effect is.

[00:18:45](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1125s) So what we want to do

[00:18:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1126s) is find ways to lower the

[00:18:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1128s) minimum detectable effect,

[00:18:49](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1129s) so we can shorten the experiment,

[00:18:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1131s) or reduce how much sample size we need.

[00:18:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1134s) In that case,

[00:18:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1135s) the only lever a data scientist really has is to

[00:18:57](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1137s) reduce variance.

[00:18:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1138s) reduce noise from the experiment.

[00:19:00](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1140s) So how do you reduce variance?

[00:19:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1142s) The most effective approach, generally,

[00:19:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1144s) is regression adjustment,

[00:19:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1145s) or CUPED.

[00:19:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1146s) And something a bit more advanced

[00:19:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1149s) is multivariate regression adjustment,

[00:19:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1151s) which my company calls CURE.

[00:19:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1155s) That is,

[00:19:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1155s) you can use pre-experimental data

[00:19:17](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1157s) to predict post-experiment data

[00:19:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1159s) and reduce variance,

[00:19:20](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1160s) and you can also use other attributes of the user

[00:19:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1162s) or experimental unit

[00:19:24](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1164s) to fit the regression,

[00:19:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1165s) further reducing variance.

[00:19:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1167s) As for CUPED,

[00:19:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1168s) I also have a 30–40 minute English video

[00:19:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1171s) with a Meta research scientist,

[00:19:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1173s) Kenneth Huang,

[00:19:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1173s) who previously did a math PhD at UC Berkeley,

[00:19:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1175s) a math PhD,

[00:19:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1176s) and now works at Meta as a research scientist.

[00:19:39](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1179s) We made an episode together.

[00:19:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1180s) He’s also done a lot of related papers and research.

[00:19:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1182s) We explain it really clearly in that video.

[00:19:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1184s) If you’re interested,

[00:19:45](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1185s) go watch that episode.

[00:19:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1186s) Bottom line:

[00:19:47](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1187s) CUPED is, to a large extent,

[00:19:49](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1189s) the difference-in-differences idea,

[00:19:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1191s) but applied at the unit level,

[00:19:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1194s) using regression adjustment.

[00:19:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1196s) So it can dramatically reduce variance.

[00:19:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1198s) But after you do CUPED,

[00:20:00](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1200s) there isn’t much variance left

[00:20:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1202s) to squeeze out.

[00:20:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1203s) A rough way to think about it:

[00:20:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1204s) CUPED can reduce about 80%

[00:20:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1206s) of the variance you can realistically reduce.

[00:20:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1207s) So if you haven’t done CUPED,

[00:20:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1209s) you should do CUPED.

[00:20:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1210s) And if you’ve already done CUPED,

[00:20:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1211s) there isn’t that much else worth doing.

[00:20:12](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1212s) Don’t spend too much time and energy

[00:20:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1214s) dreaming up fancy techniques.

[00:20:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1215s) Don’t jump to deep learning and things like that

[00:20:17](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1217s) just to try to reduce variance.

[00:20:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1218s) It’s not worth it.

[00:20:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1219s) That’s CUPED.

[00:20:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1219s) Next: Bayesian vs. frequentist.

[00:20:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1222s) Bayesian vs. frequentist.

[00:20:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1223s) This is another topic that pedantic data scientists

[00:20:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1226s) love to argue about.

[00:20:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1227s) They think Bayesian methods

[00:20:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1228s) are this amazing thing,

[00:20:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1229s) something really worth talking about.

[00:20:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1231s) But I’d say,

[00:20:32](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1232s) the upside of Bayesian methods is that

[00:20:34](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1234s) they’re a different philosophy from frequentist approaches,

[00:20:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1237s) and Bayesian methods

[00:20:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1238s) can give you a very internally consistent explanatory framework.

[00:20:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1242s) That's the benefit.

[00:20:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1243s) Kenneth and I also have a video about Bayesian statistics,

[00:20:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1246s) about 40 minutes long.

[00:20:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1246s) If you're interested, you can check it out.

[00:20:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1248s) But what's really important here

[00:20:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1248s) is one thing everyone should understand:

[00:20:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1250s) Bayesian and frequentist approaches

[00:20:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1252s) don't actually change your data.

[00:20:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1254s) Your experimental data

[00:20:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1255s) is still your experimental data.

[00:20:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1256s) Nothing changes.

[00:20:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1258s) They just provide

[00:21:00](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1260s) different interpretations of the same data.

[00:21:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1261s) If you're using Bayesian methods

[00:21:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1262s) with a non-informative prior,

[00:21:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1264s) and it's not informative—

[00:21:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1265s) basically uninformative—

[00:21:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1267s) that kind of Bayesian approach,

[00:21:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1268s) you'll find that

[00:21:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1270s) even though they give different interpretations,

[00:21:12](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1272s) all the numbers you get,

[00:21:13](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1273s) including the decision rule behind them,

[00:21:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1275s) are exactly the same.

[00:21:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1276s) So then we know

[00:21:17](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1277s) this is a baseline:

[00:21:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1278s) Bayesian and frequentist

[00:21:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1279s) aren't really that different.

[00:21:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1281s) Where they start to differ

[00:21:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1282s) is what we call Bayesian with priors.

[00:21:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1285s) And Bayesian with priors comes in two types.

[00:21:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1286s) The first is:

[00:21:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1287s) you put a prior on the point estimate.

[00:21:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1289s) For example,

[00:21:30](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1290s) I previously believed this should be 2%,

[00:21:32](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1292s) so afterward,

[00:21:34](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1294s) my experimental data isn't treated as starting from 0,

[00:21:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1296s) it's treated as starting from 2%.

[00:21:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1298s) And obviously that creates a problem:

[00:21:39](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1299s) how do you define your prior?

[00:21:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1301s) Say a VP tells me,

[00:21:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1302s) I just want to launch this feature.

[00:21:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1304s) Say I give it a 10% prior.

[00:21:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1306s) Your experiment might collect a lot of data,

[00:21:47](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1307s) and you can only move it from 10% to 9%.

[00:21:49](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1309s) Either way, you're going to launch.

[00:21:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1311s) But if you use a frequentist approach,

[00:21:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1313s) your experimental result might go from 0% to -1%,

[00:21:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1316s) and you'll realize you shouldn't launch it.

[00:21:57](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1317s) So who's right—your prior or the data?

[00:21:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1319s) I think that's very dangerous,

[00:22:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1321s) and very easy to abuse.

[00:22:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1322s) So in the field,

[00:22:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1323s) very few people recommend this

[00:22:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1325s) kind of prior for point estimation.

[00:22:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1327s) Now the other type

[00:22:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1328s) is a prior on your confidence interval.

[00:22:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1330s) That can actually be meaningful.

[00:22:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1331s) Meaning:

[00:22:12](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1332s) you shouldn't be overconfident and launch on too little data.

[00:22:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1335s) That part makes sense.

[00:22:17](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1337s) And why does it make sense?

[00:22:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1338s) Let's go back to the frequentist view:

[00:22:20](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1340s) with the same test,

[00:22:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1342s) if you ran it 100 times,

[00:22:24](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1344s) and the confidence interval is 95%,

[00:22:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1346s) then the true value

[00:22:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1347s) would fall inside my interval 95 times out of 100.

[00:22:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1349s) But there's a problem:

[00:22:30](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1350s) in those 100 runs,

[00:22:32](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1352s) each time I'm not actually getting the true value.

[00:22:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1355s) In other words, the experiment gives you

[00:22:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1357s) a point estimate,

[00:22:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1358s) and that point estimate

[00:22:39](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1359s) almost 100%

[00:22:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1360s) is not your actual treatment effect.

[00:22:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1363s) So what issue does that create?

[00:22:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1364s) The issue is:

[00:22:45](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1365s) when you run lots of experiments,

[00:22:47](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1367s) and you add the results up,

[00:22:49](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1369s) you'll see lots of cases where 1+1 doesn't equal 2.

[00:22:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1370s) the “1+1 is less than 2” problem,

[00:22:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1371s) and

[00:22:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1372s) you end up launching a lot of things that shouldn't be launched.

[00:22:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1375s) So your false discovery rate is very high.

[00:22:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1378s) But this isn't something only Bayesian methods can solve.

[00:23:00](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1380s) A frequentist approach plus a simple rule

[00:23:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1383s) can solve it too.

[00:23:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1383s) I recommend Cunningham's paper.

[00:23:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1385s) If you're interested in the details,

[00:23:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1386s) I can post the relevant stuff

[00:23:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1388s) in the comments,

[00:23:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1388s) or I can make a dedicated video later

[00:23:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1390s) to explain it clearly.

[00:23:12](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1392s) But if you just want a conclusion,

[00:23:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1394s) and you trust me,

[00:23:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1395s) then you know:

[00:23:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1396s) Bayesian and frequentist

[00:23:17](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1397s) are really just

[00:23:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1398s) different interpretations of the same data.

[00:23:20](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1400s) They come from different philosophies,

[00:23:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1401s) but in the end they don't change the data.

[00:23:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1403s) So

[00:23:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1403s) I really don't think it's that big a deal.

[00:23:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1405s) And it's easy to use simple methods

[00:23:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1407s) to bridge the difference between them.

[00:23:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1409s) In the end, the decision rule you get is the same,

[00:23:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1411s) and the decision you make is the same.

[00:23:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1413s) It's simply not worth

[00:23:34](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1414s) having such a huge debate about it.

[00:23:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1416s) Third: sequential testing.

[00:23:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1418s) And while we're on sequential testing,

[00:23:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1421s) let me talk about

[00:23:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1422s) something really important we need to do:

[00:23:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1423s) reduce the false discovery rate.

[00:23:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1426s) Let me ask everyone a question:

[00:23:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1428s) an experiment that should be launched

[00:23:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1431s) doesn't get launched,

[00:23:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1431s) versus an experiment that shouldn't be launched

[00:23:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1434s) does get launched—

[00:23:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1435s) which one is more harmful?

[00:23:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1436s) It might actually be a really good result,

[00:23:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1439s) but it doesn't get launched.

[00:24:00](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1440s) Or it might be a bad result,

[00:24:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1441s) but it gets launched.

[00:24:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1442s) Which is more harmful?

[00:24:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1443s) Usually the latter is more harmful.

[00:24:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1444s) Why?

[00:24:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1445s) Because experiments

[00:24:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1446s) are generally cheap,

[00:24:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1447s) but once an experiment gets launched,

[00:24:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1449s) it becomes expensive.

[00:24:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1450s) Expensive in the sense that I may have to spend more money,

[00:24:12](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1452s) I may affect more users,

[00:24:13](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1453s) and also in the sense that the code

[00:24:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1455s) now goes into the codebase,

[00:24:17](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1457s) and it becomes

[00:24:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1458s) a long-term maintenance cost.

[00:24:20](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1460s) So when you launch an experiment,

[00:24:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1462s) the cost

[00:24:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1463s) compared to just running the experiment

[00:24:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1465s) is totally disproportionate—

[00:24:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1466s) it's much higher on the launch side.

[00:24:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1467s) So if you launch something bad,

[00:24:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1469s) the cost is very high.

[00:24:30](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1470s) And that's what people mean by

[00:24:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1471s) why we need to

[00:24:32](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1472s) control your false discovery rate.

[00:24:34](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1474s) So why do you end up with

[00:24:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1475s) a false discovery rate?

[00:24:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1476s) There are lots of reasons,

[00:24:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1477s) including p-hacking,

[00:24:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1478s) and sloppy data work,

[00:24:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1480s) but one very common cause

[00:24:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1483s) is peeking—

[00:24:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1484s) before you run the experiment,

[00:24:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1486s) you do a sample size calculation,

[00:24:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1488s) you do a power analysis,

[00:24:49](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1489s) and you find you need two weeks

[00:24:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1491s) to detect, say, a 2%

[00:24:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1492s) minimum detectable effect.

[00:24:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1494s) And I say this experiment needs to run for two weeks.

[00:24:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1496s) But in the first week you see—hey—

[00:24:58](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1498s) it's at 3%.

[00:25:00](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1500s) it's statistically significantly positive.

[00:25:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1502s) So I say, alright, let's launch it.

[00:25:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1503s) That's peeking.

[00:25:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1504s) And the decision you make

[00:25:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1506s) while you're peeking

[00:25:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1507s) is very likely to lead to false discovery,

[00:25:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1510s) or in the long run,

[00:25:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1511s) it will definitely increase your false discovery rate.

[00:25:13](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1513s) Why?

[00:25:13](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1513s) Because think about it:

[00:25:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1514s) suppose your experiment—

[00:25:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1515s) intuitively speaking—

[00:25:17](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1517s) each data point in an experiment

[00:25:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1519s) is just an observation.

[00:25:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1521s) Like I said earlier,

[00:25:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1521s) every point estimate

[00:25:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1523s) comes with a confidence interval,

[00:25:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1525s) it's not a true, 100% accurate

[00:25:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1527s) point estimate of the true effect.

[00:25:30](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1530s) So it might just happen to jump

[00:25:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1533s) to the top of that confidence interval,

[00:25:35](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1535s) or even outside that confidence interval,

[00:25:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1536s) making it look positive.

[00:25:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1537s) Then if you observe for a bit longer,

[00:25:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1540s) as more data comes in,

[00:25:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1541s) it may move back,

[00:25:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1542s) back into the non-significant range.

[00:25:45](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1545s) But humans are biased,

[00:25:47](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1547s) so when people see a

[00:25:49](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1549s) statistically positive result,

[00:25:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1551s) they want to launch it right away—

[00:25:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1552s) whether they're a PM, DS,

[00:25:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1553s) or engineer.

[00:25:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1554s) Because promotions

[00:25:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1555s) come from launching new features, right?

[00:25:57](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1557s) So you carry that bias,

[00:25:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1559s) and you end up with false discovery,

[00:26:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1561s) and you do this,

[00:26:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1562s) which over time raises your false discovery rate.

[00:26:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1565s) So what does sequential testing do?

[00:26:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1567s) It “spends” your power—

[00:26:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1569s) that's a good way to think about it.

[00:26:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1570s) spend beta.

[00:26:10](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1570s) That's basically spending your power.

[00:26:12](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1572s) So at the beginning,

[00:26:14](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1574s) it gives you a wider confidence interval,

[00:26:17](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1577s) making it harder to get a significant result.

[00:26:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1579s) As the experiment goes on,

[00:26:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1581s) that confidence interval

[00:26:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1582s) gradually approaches

[00:26:24](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1584s) what you'd get without sequential testing.

[00:26:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1586s) If you've planned your experiment,

[00:26:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1588s) and the duration

[00:26:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1588s) is, say, two weeks,

[00:26:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1589s) then after two weeks, your

[00:26:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1591s) sequential testing adjusted confidence interval (sequential-testing-adjusted confidence interval)

[00:26:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1593s) will match your unadjusted confidence interval,

[00:26:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1596s) they become consistent,

[00:26:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1597s) the same width.

[00:26:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1598s) This approach

[00:26:39](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1599s) can help reduce the false discovery rate.

[00:26:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1602s) And behind it is an important philosophy:

[00:26:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1604s) your adjustment

[00:26:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1606s) should be as conservative as possible.

[00:26:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1608s) In other words, that initial confidence interval

[00:26:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1610s) should be as wide as possible.

[00:26:51](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1611s) Of course, not infinitely wide—

[00:26:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1612s) but as wide as possible given your design.

[00:26:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1615s) Why?

[00:26:55](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1615s) Because you have to assume infinite peeking.

[00:26:57](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1617s) In the sequential testing literature,

[00:26:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1619s) there's a ton of discussion about this,

[00:27:00](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1620s) like beta-spending,

[00:27:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1621s) alpha-spending.

[00:27:02](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1622s) Most of it is basically about

[00:27:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1624s) how to spend

[00:27:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1625s) your beta,

[00:27:05](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1625s) should it decay linearly,

[00:27:07](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1627s) or what,

[00:27:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1628s) and how you should

[00:27:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1628s) assume your peeking plan.

[00:27:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1629s) In practice, I don't think any of that makes sense.

[00:27:11](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1631s) In practice you should just assume

[00:27:13](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1633s) people peek infinitely—

[00:27:15](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1635s) they'll check every day,

[00:27:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1636s) whenever they feel like it.

[00:27:18](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1638s) You’re unlikely to do this before you even start the experiment.

[00:27:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1641s) You’re not going to set up a “no peeking” rule from the beginning.

[00:27:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1643s) Just assume people will keep checking as much as they want.

[00:27:25](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1645s) In that case,

[00:27:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1646s) it’s actually a pretty good decision rule.

[00:27:28](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1648s) Because you generally shouldn’t ship early,

[00:27:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1651s) but you can abandon early.

[00:27:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1653s) Meaning,

[00:27:34](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1654s) when your result is negative—i.e., it’s statsig negative—

[00:27:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1658s) and it’s beyond your confidence interval,

[00:27:40](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1660s) you can kill the experiment.

[00:27:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1662s) Because at that point there’s usually a bug,

[00:27:43](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1663s) or some really bad

[00:27:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1664s) negative user experience.

[00:27:45](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1665s) And it’s totally fine to stop it.

[00:27:47](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1667s) But we don’t need

[00:27:48](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1668s) your test to be so sensitive

[00:27:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1670s) that it detects a positive effect early on,

[00:27:53](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1673s) because that doesn’t really bring long-term benefits.

[00:27:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1674s) Just wait until the experiment reaches

[00:27:56](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1676s) its planned two-week mark,

[00:27:57](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1677s) and then make the launch decision.

[00:27:59](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1679s) From a management perspective,

[00:28:01](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1681s) I think this is how you should

[00:28:03](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1683s) properly motivate people.

[00:28:04](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1684s) So if you combine management

[00:28:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1686s) with human nature,

[00:28:06](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1686s) you should use a very conservative

[00:28:08](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1688s) sequential testing approach

[00:28:09](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1689s) to adjust your confidence interval,

[00:28:12](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1692s) to penalize peeking,

[00:28:13](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1693s) and systematically reduce your false discovery rate.

[00:28:16](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1696s) Those are the ones I think are especially important:

[00:28:19](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1699s) a few different tests—

[00:28:20](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1700s) CUPED,

[00:28:21](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1701s) Bayesian methods, and sequential testing.

[00:28:22](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1702s) There are also some other tests,

[00:28:23](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1703s) if you’re interested—

[00:28:24](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1704s) whether it’s switchback tests,

[00:28:26](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1706s) grid search,

[00:28:27](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1707s) or tests like search interleaving.

[00:28:29](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1709s) If you’re interested, feel free to leave a comment below.

[00:28:31](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1711s) If we get the chance, we can talk about them more.

[00:28:33](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1713s) For today, I just wanted to share the main points.

[00:28:36](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1716s) I know this goes pretty deep,

[00:28:37](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1717s) but I believe

[00:28:38](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1718s) for any data scientist running experiments,

[00:28:41](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1721s) or a PM, or an engineer,

[00:28:42](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1722s) this will all be useful.

[00:28:44](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1724s) It’s getting late over here,

[00:28:46](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1726s) hope you like this little campfire I’ve got next to me.

[00:28:49](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1729s) Alright, that’s it for this episode.

[00:28:50](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1730s) I’m right here—

[00:28:52](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1732s) I’ve even got a flask, so cheers.

[00:28:54](https://www.youtube.com/watch?v=9kh1YvzZYks&t=1734s) See you next time.
