---
title: I tried giving every bot a free model, and free models kept disappearing under me
date: 2026-07-21
tags: [openrouter, failure, debugging]
---

## What changed

- Built a second, free provider path alongside the paid Claude one — a
  `local`/OpenRouter agent meant for everyday chat, with the idea being one
  free "chat" bot and one paid "code" bot, connected so the free one could
  hand off real work to the paid one.
- Hit a stale setup guide that failed silently instead of erroring: it
  assumed environment variables were readable directly, when this codebase
  deliberately keeps `.env` out of `process.env` so secrets can't leak to
  child processes. Skipping that step doesn't error — it just quietly fails
  deep inside with a cryptic "no providers found."
- Found the curated list of "free" OpenRouter models I'd picked once was
  already dead by the time a real message went through it — all three
  models gone from the live free tier, confirmed against OpenRouter's own
  model list.
- Found and fixed a real bug where creating a second bot with a different
  free model silently reassigned the FIRST bot's model too, because the
  model choice was being written to one shared file both bots read from
  instead of each bot's own config.
- Found OpenRouter's free tier has a hard daily cap, and hit it directly
  mid-testing.

## Why I made this change

The idea was simple: not every conversation needs a paid model behind it,
so give people a free option for everyday chat and save the paid one for
real work. NanoClaw already supported per-bot providers and letting one bot
hand a task to another, so this felt like it should just work.

It mostly didn't, and every failure was a different flavor of "the free
tier is not a stable thing to build on." I'd pick three free models, verify
they worked, and by the time I actually tested a live reply, one or more of
them had already been pulled from OpenRouter's free tier entirely — no
warning, the bot's own error message was the first sign. Then I hit the
daily free-request cap partway through a normal testing session, which
isn't a bug, just a real ceiling I hadn't planned test sessions around.

The bug where two bots shared one model was the one that actually worried
me, because it wasn't loud — nothing crashed, both bots just quietly
answered with the wrong model, and I only found it because I happened to
ask each bot directly which model it thought it was running. That's the
kind of bug that's genuinely dangerous specifically because there's no
error to notice.

I didn't rip this out. The backend is still there, tested at the plumbing
level, just not wired into the UI anymore — dead free models and hard rate
caps aren't something I can fix, only work around, and I decided the
free-tier tradeoffs weren't worth presenting as a first-class option to
someone setting this up for the first time.
