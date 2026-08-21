---
title: Wiring up Discord, and a bot that correctly refused to trust me
date: 2026-07-28
tags: [discord, security, debugging]
---

## What changed

- Registered a real Discord bot through the Developer Portal and wired it to
  the same agent group Telegram already talks to, via NanoClaw's own
  `setup/index.ts --step register`.
- `app/vendor/nanoclaw-patches/discord/files/src/channels/discord.ts` —
  stripped a `ChannelDefaults` type and `defaults:` field that only exist on
  NanoClaw's `channels` trunk branch, not at the commit ClawDeck is actually
  pinned to. The vendored file had drifted ahead of the pin instead of
  behind it, which is the direction I hadn't been checking for.
- Manually granted my own Discord identity (`discord:<id>`) the same owner
  role my Telegram identity already has, via the same internal functions
  Telegram's pairing flow uses.
- Deleted an agent group that got auto-created by mistake, and rewired its
  Discord DM to the existing "robk" agent group instead, so a DM and the
  server channel share one identity and memory.

## Why I made this change

I wanted a second real channel, not just Telegram, so I built a Discord bot
using the same instructions NanoClaw ships. Also I figured it could be used inside of discord servers aswell. The build failed with a type
error the moment I tried it, the vendored Discord file I'd copied in was
newer than the commit everything else in this install is pinned to. I'd
been assuming drift only ever goes one direction, trunk moving ahead of what
I vendored. This was the opposite the file I copied in was ahead of my own
pin. Fixed it by just stripping the fields that didn't exist yet at my pin.

Then I actually @-mentioned the bot from my own Discord account, and it got
silently dropped. Not an error, just nothing happened. The reason was
`unknown_sender_strict`. NanoClaw treats every (channel, external id) pair
as a completely separate identity, so being the owner as `telegram:<id>`
means nothing to `discord:<id>`, a different string for the same actual
person. The bot had no way to know that was me. I had to go grant my own
Discord identity the same role by hand.

Genuinely, my first reaction was mild annoyance that I'd built this and it
didn't just work for me immediately. But sitting with it for a second, this
is exactly the behavior I'd want if I found this bug from the other side,
a bot that assumes an unrecognized identity is the owner just because it
claims to be would be a real hole. It refusing me was the system working
correctly on an edge case I hadn't set up yet, not a bug in the trust model
itself.

Last thing from the same session, a Discord DM to the bot spun up as a
brand new, separate agent, different memory, different identity from
"robk," created automatically the first time I approved the DM request.
That's the right default for someone unplanned messaging the bot cold, but
wrong for my own DM to my own bot. I deleted the auto created agent and
rewired the DM to share the same identity Telegram and the server channel
already use.
