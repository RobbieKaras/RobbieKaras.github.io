---
title: The bot had been paired since July 1 and never replied once
date: 2026-07-27
tags: [telegram, debugging, nodejs]
---

## What changed

- `app/telegram-channels.js` — added `ensureTelegramWirings(installPath)`. Scans
  every Telegram `messaging_groups` row for ones with no matching
  `messaging_group_agents` row, and wires the ones it finds — to a per-bot
  agent group when the pairing's `instance` field is an agent-group id, or to
  the primary bot's own group as the fallback.
- `app/launch.js` — calls it after every pairing attempt, and again on its
  own so a pairing that finishes after the pairing step's own timeout window
  still gets picked up.
- Confirmed the real damage first: NanoClaw's own `unregistered_senders`
  table had been logging real inbound messages, dropped with reason
  `no_agent_wired`, since the day the bot was first paired.

## Why I made this change

I went looking at NanoClaw's `unregistered_senders` table for an unrelated
reason and found real messages sitting there, all with the same drop reason,
going back to July 1. That's the day I originally set up the primary bot's
Telegram pairing. It had been sitting there for weeks looking connected —
paired chat, no errors anywhere — and had never actually sent a single
reply.

The pairing flow proves you own the chat and records it. That's it. It
doesn't create the separate row that tells the router which agent should
actually handle messages from that chat — a completely different table. Two
different things that look like they should be the same step, and nothing
in the UI or the logs made the gap obvious, because pairing itself succeeds
either way.

The part that made me actually go add the fix instead of just patching this
one install by hand was realizing the pairing step's own code has a real
timing gap — its wait-for-a-code window can expire before someone actually
sends the code back, so trying to wire inline, right after pairing, isn't
even reliable. That's why `ensureTelegramWirings` is its own idempotent
reconciliation pass instead of a one-time step glued to pairing — it has to
be safe to call again later and pick up something that finished after the
original call already gave up.
