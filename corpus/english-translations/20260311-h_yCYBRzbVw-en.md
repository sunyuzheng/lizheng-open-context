---
id: "youtube-h_yCYBRzbVw-en-ai"
title: "Why OpenClaw Is Bound to Fail—But I Still Recommend You Try It"
author: "AI"
original_author: "Yuzheng Sun"
publisher: "Yuzheng Sun"
source_type: "video-translation"
source_video_id: "h_yCYBRzbVw"
source_url: "https://www.youtube.com/watch?v=h_yCYBRzbVw"
original_source_url: "https://www.youtube.com/watch?v=h_yCYBRzbVw"
source_family: "https://www.youtube.com/watch?v=h_yCYBRzbVw"
published_at: "2026-03-11T16:52:18Z"
generated_at: "2026-04-18T15:18:45Z"
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

# Why OpenClaw Is Bound to Fail—But I Still Recommend You Try It

[00:00:00](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=0s) What are the three things OpenAI also got right that make it seem incredibly smart and experienced? First: a single entry point and a unified context. Second: persistent memory. Third: rich skills. With these three design choices, users feel like the “little crayfish” just gets better the more you use it—like it understands you more, more like a constantly present assistant. So how does it actually pull that off under the hood?

[00:00:21](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=21s) Let me start with a bold prediction that’s very easy to prove wrong: OpenCL—what everyone calls “little crayfish”—will go through a classic three-act destiny. Act one is right now: it’s insanely hot. You’ll see tutorials and deployment guides everywhere, and cloud vendors will jump in too. After people set it up, they get this strong “mind blown” feeling—like, wow, AI doesn’t just chat with me, it can actually manage things for me, read my files, run tasks across platforms, and keep working continuously. It gives you this intense sense that the future has arrived.

[00:00:49](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=49s) Act two is about one or two months later. A lot of people’s crayfish will “die,” and even the ones who keep it alive will find it gets more awkward the more they use it. For example, it might carry your preferences from Project A into Project B. Or you carefully organize a research doc, and it shrinks it down to three lines.

[00:01:05](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=65s) You want to know what it’s doing in the background, but all you can do is stare at a “typing…” indicator. The deeper you go, the more you feel: yes, it’s powerful, but it’s also kind of twisted and frustrating. Act three is the shakeout—some people who just want something flashy keep it on their phones and use it lightly once in a while. But people who truly care about productivity will migrate to other, more effective tools. That “hot first, then cool off” fate won’t happen because OpenCL is weak—on the contrary, it’s precisely because it’s too strong.

[00:01:31](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=91s) In pushing agentic AI to the masses, it made some extremely drastic trade-offs. Its design philosophy is: to serve the broadest possible audience, these compromises are necessary—and it’s exactly those compromises—

[00:01:44](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=104s) that make it destined to blow up, but not suited for deep productivity—meaning it’s also destined to cool down in the future. But by then, it will have completed its historical mission: showing everyone that agentic AI has reached this stage, and it can do all these things now. Once the “little crayfish” has educated the market, more and better agentic AI tools will definitely emerge. So today’s video isn’t saying, “Since the crayfish is bound to fade, we don’t need to pay attention to it.” It’s the opposite.

[00:02:12](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=132s) In this video, we’ll do a deep breakdown of how the crayfish got so popular—why it caught on, and what it teaches us. Second: what did the crayfish actually get right? What bold experiments did it make in key areas?

[00:02:24](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=144s) That pushed it into the spotlight. Third: where do these design compromises or trade-offs gradually make it less usable, and why can’t it meet the demands of deep productivity?

[00:02:36](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=156s) And fourth: if we want to build something that truly lets AI deliver productivity, what should we do? We’ve actually already built it, open-sourced it for everyone, and open-sourced a lot of very useful Skills too—feel free to try it for free. We’ll touch on some technical topics, but I promise I’ll explain them clearly and simply—you don’t need to be a programmer to follow along. If you’re already using Web Code, you’ll feel even more strongly what the real craft is here.

[00:03:00](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=180s) This episode is basically a video walkthrough of a technical article by Brother Ya from our community. If you want more precise technical terminology and want to hear Brother Ya’s thinking directly,

[00:03:08](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=188s) you’re welcome to go read the article in the community. The information density in that piece is much higher than my explanation. Alright—if you still want my walkthrough, let’s go point by point. First: why did the crayfish get so popular? Here’s a spicy take: the crayfish’s explosive popularity is the same phenomenon as last year’s DeepSeek boom, with an extra Pop Mart factor layered on top. Let’s unpack it one by one—what was the DeepSeek boom, exactly?

[00:03:30](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=210s) Even now, I bet a lot of people still don’t know why DeepSeek became such a breakout hit last year. Sure, there were “made-in-China” factors, the small-company factor, the cost factor—DeepSeek didn’t have it easy. But the key reason people suddenly found it so usable was that it exploited a timing gap. DeepSeek was the first to expose the Chinese mass market to reasoning models, because before that—especially O1 and O1 Pro—reasoning models

[00:03:55](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=235s) had been out for months. When we were teaching and talking about it in the community, we were honestly amazed at how powerful reasoning models were. But O1 Pro, for example, required a 200-yuan subscription, so most people never touched it. Even the non-Pro O1 later still needed a $20 subscription—only a small group got to experience how good it was. But once DeepSeek arrived, tons of everyday users felt it: AI doesn’t just chat with me—it can think.

[00:04:18](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=258s) It can search. It can reason. And we can see its reasoning process and find that it actually makes a lot of sense—suddenly AI felt much smarter. That impact was huge, so it went viral fast. And note this: the core point is that DeepSeek didn’t blow up because it utterly crushed competitors on capability. What it really did was bring a capability that a small group was already enjoying to the general public.

[00:04:42](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=282s) OpenCL was the same. When OpenCL appeared—early 2026—there was a clear gap in GenAI. On one side, what most people interacted with were chat-style products like ChatGPT or DeepSeek.

[00:04:54](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=294s) They were popular, but the interaction was still just back-and-forth, one sentence at a time. On the other side were agent tools like Cursor, Cloud Code, CodeX, and Open Code. They have local permissions, can read and write files, and can run commands.

[00:05:06](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=306s) They can tap into your computer’s full compute. They can keep pushing tasks forward. In essence, they’re all agents. In terms of productivity, they’re already a whole generation ahead. In fact, back at the end of ’24, we were already telling everyone to switch to agents and stop using tools like ChatGPT. Our entire 2025 curriculum was built around agentic topics, and if you look in our community, so many of the things people built were made using an agents approach.

[00:05:32](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=332s) You could say the biggest leap in how you use AI is moving from a chat box like ChatGPT to agents like Cursor. We even posted a dedicated article about this in the community.

[00:05:43](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=343s) You’ll feel a massive 10x, 100x boost in productivity, because agents can orchestrate compute and use tools; and they’re closed-loop—they can keep pushing the task forward and iterate on their own. ChatGPT is constrained by you: you have to keep talking to it, and it’s open-loop.

[00:05:58](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=358s) So with an open-loop setup like that, you can’t truly leverage AI’s compute to automatically get things done for you. Alright—despite how long we’ve taught this and emphasized it, the problem is that agents are still too niche. We even made a dedicated lesson—Practical AI Programming Basics—to help people get over that hurdle. But only about 3,000 people took that course, and outside of those 3,000, most people still don’t know how to get past that barrier.

[00:06:21](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=381s) The moment they see a Terminal or an IDE, they instinctively feel scared. They think, “This isn’t for me. I’m not a programmer. I can’t use this.” But you actually can. It’s just that with this limiting mindset, you can’t get past that initial hurdle.

[00:06:34](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=394s) For most people, if you stay in a chat box like ChatGPT or DeepSeek, it can feel like AI hasn’t made any huge progress—pretty much the same as two years ago. But once you really use Agents, you realize just how earth-shattering the change has been. And it’s not just ordinary users—plenty of people at big tech companies too. If they haven’t used Cursor, haven’t used Cloud Code, haven’t programmed in an agent-based way, they’ll think AI is just so-so. But after they actually try it, they’ll be like, “Oh. So my job really is about to be replaced by AI.”

[00:07:01](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=421s) Alright—this is 2026. Agents are already here. But most people are still using AI at the ChatGPT level; that’s where their perception is. Then OpenCLoud “Crayfish” shows up, and for the first time it brings these agents—able to read and write files, run commands, keep persistent memory, and iterate continuously—to the general public through a chat-window interface. So for the first time, a lot of regular people realize AI isn’t just a chatbot where you ask and it answers, but something that can actually help you move a task forward.

[00:07:30](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=450s) So I’ll say it again: like DeepSeek, Open Cloud doesn’t represent some fundamental underlying technical breakthrough—it just takes capabilities a small group of people were already used to, and the “ceiling” they’d already experienced, and suddenly puts it in front of everyone.

[00:07:42](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=462s) That’s incredibly powerful. Peter—the founder of Open Cloud—has said himself that he doesn’t think Open Cloud has any truly amazing technology, but when you put all these things together, it feels kind of magical. A lot of product innovation is like this: innovation isn’t only about inventing some groundbreaking core tech. Bringing something to the masses can be an extremely powerful innovation in itself. Benz invented the automobile, but it took Ford inventing the assembly line and massively cutting costs for cars to truly become widespread.

[00:08:10](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=490s) So which innovation matters more, Ford or Benz? I think both matter. And Pop Mart—there’s even less to say; that’s consumer psychology. People really do love to follow trends. Honestly, if you don’t know how to “install” OpenCLoud, then even if you do install it, you’ll basically end up killing your “crayfish.”

[00:08:28](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=508s) Because keeping a “crayfish” alive still takes some know-how. We’ll also release some public classes later to teach you how to raise your survival rate—but it’s not simple. If you want the “crayfish” to be useful, that’s not simple. If you want it to create value, that’s not simple either. Usually it only delivers value when you have real business work you’re pushing forward yourself. So there’s definitely a barrier to using the “crayfish” well.

[00:08:48](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=528s) In my mind, the barrier is even higher than learning Cursor or learning Claude. I can get you to learn how to use Cursor and Claude in an hour or an evening, and get you doing lots of things in an agent-based way. But I’m not confident I can get your “crayfish” working really well in a single night. Still, a lot of people will jump on the bandwagon and use the “crayfish.” And I’d say the Pop Mart factor plays a huge role here: other people have it, it’s trendy, and if I don’t use it I’ll fall behind. That kind of bandwagon mindset drives lots of people to try it. But that mindset also makes it shoot up higher and…

[00:09:17](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=557s) …faster—and I actually think that’s a bad thing. Because if you use Open Cloud and find that nothing works, you’ll think, “Well then I’m even less interested in learning Cursor.” You’ll feel like, “Open Cloud is already this hard to use—then Cursor or Cloud Code must be even harder.” But that’s not true. Cursor and Open Cloud are actually easier to learn and easier to use. Your “crayfish” is the thing that’s harder to learn and harder to use.

[00:09:36](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=576s) But if you blindly followed the trend, decided agentic AI isn’t for you, and then from that point on you’re afraid to use agentic AI at all—that’s a huge danger. Everyone needs to understand: if the “crayfish” is hard to use, it’s hard by nature. It’s inherently difficult. Don’t let that make you give up on learning and using agentic AI.

[00:09:55](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=595s) Coming back to it, here’s a key takeaway: when a product goes viral, the people who benefit in the long run—even with DeepSeek—aren’t the ones who rushed to try it first. They’re the ones who understood why it got hot. For example, with DeepSeek, they understood how important search and reasoning are, and they truly integrated those two factors into their own workflows to do things they couldn’t do before.

[00:10:17](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=617s) And likewise, if we look at Open Cloud, if we really want to benefit, we need to understand why it’s popular—understand the design philosophy behind it—extract the transferable insights, and fold them into our own workflows. Because tools like this will definitely cool off and go out of fashion, but your understanding of what’s behind the tool won’t expire. Alright, next let’s break down what Open Cloud got right and what its ceiling is. In this piece, I actually listed three technical highlights in “A-Ge”’s article.

[00:10:40](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=640s) Along with four corresponding limitations. Before we unpack those highlights, I want to talk about a crucial point that many people overlook: why did the “crayfish” break out? Because it put the entry point inside a chat interface.

[00:10:51](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=651s) But that also severely limits its ceiling. First, why does putting it in a chat window make it blow up? Because for most people, if you look at daily screen time, it’s basically spent inside chat apps.

[00:11:01](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=661s) When we do anything—even just jotting something down—sometimes it feels easier to note it in WeChat than to open a separate notes app. Not to mention that right now the alternative is: if I want to use an Agent tool, I have to open a Terminal or an IDE—things that make a lot of people’s heads hurt just looking at them. On the other side, I open Slack or I open Feishu—an interface I’m extremely familiar with. So naturally, a chat window feels friendly and low-friction.

[00:11:24](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=684s) But the chat window also determines the ceiling of this software. Why? First, a chat window is linear—one sentence after another, line after line down the page.

[00:11:33](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=693s) But deep knowledge work doesn’t work like that. A lot of the time you need branching. You need to reference information from another thread. Sometimes you need to branch at a node, generate different options, compare them, and then choose one. That workflow is natural in Cursor or Open Code, but in a chat window it becomes really awkward. The second issue is information density.

[00:11:54](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=714s) For lightweight tasks, a chat window is fine. But once things get even a little more complex—say you want to produce an analysis report with mixed text and images, you need tables, you want a long formatted document, you want diffs across multiple files—like comparing what’s different between this file and that file. Or you want a structured knowledge asset. You quickly find that the chat window’s way of organizing things is very unnatural. So it’s not because the AI behind it isn’t strong enough—it’s because the medium isn’t suited to serious work.

[00:12:19](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=739s) The third issue is observability of the process. If you hand AI a simple task and it finishes it, you don’t need to observe anything. But once you add even a bit of complexity, you start wondering: what is it doing? Is it stuck in a loop, or is it repeatedly thinking things through—

[00:12:33](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=753s) —and continuously trying new approaches? What tools did it call? What files did it change? What errors did it hit? All of that really matters—especially when it involves your key technical assets or knowledge assets. In professional Agent tools, those changes are visible and controllable. But in chat software, what you see is just “typing…” or a little red…

[00:12:51](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=771s) This problem gets worse the more complex the task is, because with complex tasks you’re not just waiting for an answer—you’re really waiting for an entire process. And that process, in a chat window, is really—

[00:13:01](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=781s) Pretty visible, right? So do you see it? The “compromise” here is: does Open Cloud know about these issues? Of course it does. But what path did it choose? It chose the path that’s easiest for the general public to pick up—using chat apps. And once you choose chat apps, it means you’re sacrificing all the stuff that comes after. This isn’t a capability issue, right? It’s a choice issue. This isn’t saying Open Cloud is bad—it’s telling everyone that this choice, by its nature, brings these limitations.

[00:13:26](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=806s) Next is some technical analysis that engineers might find more interesting: beneath the surface of this chat window, what three things did OpenAI get right that make it look so smart and so seasoned? They are: a unified entry point and unified context; second, persistent memory; third, a rich set of skills.

[00:13:44](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=824s) With these three design choices, users feel like Xiaolongxia gets better the more you use it—the more you use it, the more it understands you; the more you use it, the more it feels like a continuously present assistant. So how does it actually pull this off? First: a unified entry point and unified context. If you’ve used Cursor, you’ll know the context there is isolated by project—each project, each folder, has its own

[00:14:04](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=844s) context. Open project A and you get A’s context; open project B and you get B’s, and the contexts don’t carry over between A and B. Cloud Code, CodeX, and so on follow a similar design. Open Cloud’s design is the opposite: it mixes all context together.

[00:14:17](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=857s) In the morning you ask it on Telegram to organize emails, in the afternoon you ask it on Slack to write a report, and at night you ask it on WhatsApp to write your weekly update—it puts all of that context together. And once it’s all together, users feel like, “No matter where I told you something, you know it.” So you’re not just a tool like that—you’re an assistant that increasingly understands me. Because I talk to you across different apps and in the end you know it all—like, from my email you can even know what my schedule is tomorrow.

[00:14:40](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=880s) And from my day-to-day stuff you also know what’s written in my report. Second is persistent memory, because context alone isn’t enough. If you just shove all the context together, that context window fills up fast—it gets saturated.

[00:14:52](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=892s) All its brainpower goes into processing that context, and then it can’t execute tasks as well. So it introduces a persistent memory system, turning context into memory. Xiaolongxia makes memory into something maintainable. It’s not just stacking tokens—the core is a file-based memory system. For example, it has `soul.md`, `memory.md`, and `user.md`. `soul` defines your assistant’s personality—some people prefer someone very blunt, and that gets defined there.

[00:15:20](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=920s) You’ll see people online say, “Why does this Xiaolongxia have so much personality?”—that’s all defined by `soul`. `user.md` is the user profile—what kind of person the user is—and over time it organizes that into this document. And `memory.md` records the long-term memory it needs, plus some daily raw logs. The clever part is: the user doesn’t have to maintain it. It continuously organizes and maintains things on its own, constantly updating those documents, and it will review recent logs and extract what’s worth keeping into the long-term log.

[00:15:44](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=944s) At the same time, it cleans out outdated content. The end result of this design is that the user doesn’t have to manage much—they just talk to Xiaolongxia every day, and over time Xiaolongxia develops its own—

[00:15:52](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=952s) It learns more about your personality and builds up more long-term memory, which makes you feel like it understands you better and better. And these documents are controllable.

[00:16:01](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=961s) They don’t let the context become uncontrollable. But do you see? It’s not that Xiaolongxia is getting smarter and smarter—it’s that, as you use it, these documents accumulate more and more data.

[00:16:09](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=969s) There’s only one “shortcut” here: if you see someone whose Xiaolongxia is especially useful, copy and paste those three documents and you’ll get a Xiaolongxia like theirs. Of course, that Xiaolongxia may understand them really well, not you. But either way, you’ll get one that feels like theirs.

[00:16:32](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=992s) So the “soul” and core of Xiaolongxia is in these three documents. The third design choice—one many engineers underestimate—is rich skills. Engineers think, “Isn’t it just wiring up a few tools?” It’s not that simple.

[00:16:44](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=1004s) The value of tools doesn’t increase linearly—it increases combinatorially. For example, if you connect Slack, it can chat in Slack, receive status updates, and produce reports; connect search, and it can do research; connect PPT, and it can draft and produce a deck; connect the file system and command line, and it can run commands on your machine. But once you stack those four together, it’s no longer a set of scattered features—complete business workflows start to emerge.

[00:17:09](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=1029s) What do I mean? You can use Slack to tell it to pull some existing documents from your system, then say, “Search this for me, add in these case studies, and then directly make me a PPT.” Miss any one of those capabilities and it can’t do a task that complex. But with four different skills, it can. That’s the combinatorial effect of skills.

[00:17:34](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=1054s) And it’s not just additive—those three things we just talked about also form a flywheel: a unified entry point plus memory creates a data dividend.

[00:17:43](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=1063s) Your behavior across different scenarios and platforms all gets aggregated into memory, so Xiaolongxia understands you more and more. Then memory plus skills creates self-evolution: the skills it learns today will still be there tomorrow. And if it wants to do something but doesn’t know how, because it can write code, it can even write a skill for itself.

[00:18:01](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=1081s) So it keeps learning—constantly building new tools and new ways to use them—and it remembers them: “Oh, I can use this skill.” And because the chat entry point has such a low barrier, it drives high-frequency use.

[00:18:14](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=1094s) That keeps the flywheel spinning through user behavior, so Open Call really is an impressive piece of software. It’s not just a little showmanship—it builds the entire flywheel extremely well, and ordinary users can actually feel how powerful that flywheel is. That’s why it’s so good. I’m realizing this video is already too long, so its limitations—and how we go on to surpass Open Call—

[00:18:34](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=1114s) I’ll save that for the next episode. If you’re interested in this and don’t want to wait, just go to our community and read Ya Ge’s article—he breaks it down very clearly. In this Knowledge Bank, there are lots of similar, high-quality original technical articles, and I’m sure you’ll get a lot out of them. After you join our community, remember to sign up for a membership—then these technical articles will be delivered to your inbox by email. That way, you can read them in the community, and you’ll also have a copy saved in your email forever, and you can forward it to others who are interested too.

[00:19:01](https://www.youtube.com/watch?v=h_yCYBRzbVw&t=1141s) Let’s take a look. Alright—last episode we talked about why OpenCL crayfish blew up, and the truly impressive technical highlights behind that popularity. In the second half, we’ll talk about why those very strengths can actually become its ceiling, and how we should overcome that to build more useful productivity products, and what our open-source project actually looks like and how you should use it. That’s it for this video—bye!
