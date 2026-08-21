---
title: A live activity feed, a vault tab, and actually being able to edit a bot
date: 2026-07-29
tags: [dashboard, nodejs, docker]
---

## What changed

- `app/activity-feed.js` — tails NanoClaw's own host logs and streams
  structural events (message routed, container spawned/killed, agent
  hand-offs, delivery) to the dashboard live over a WebSocket. Message
  content stays out of it on purpose — just what's happening, not what's
  being said.
- `app/vault.js` — new Vault tab exposing two things the credential gateway
  already had underneath: named API keys that get auto-injected into a
  bot's outbound calls to a matching host, and pre-built OAuth connections
  (Gmail, Notion, GitHub) that hand off to the gateway's own local setup
  page instead of me reimplementing OAuth.
- `app/multi-bot.js` — real edit/delete for bots: rename, edit instructions,
  full cleanup on delete (folder, vault entry, any per-bot Telegram
  instance). The primary bot can't be deleted since it's tied to the real
  Telegram/Discord identity.
- First UI for connecting two already-existing bots to each other after the
  fact, instead of only being able to wire a parent to a brand-new child at
  creation time.
- A real Docker compatibility fix: Docker Desktop's minimum OS requirement
  moved past what this Mac runs, so the install flow now points at the last
  version that still supports it instead of the generic latest-only page.

## Why I made this change

Up to this point I could create bots and talk to them, but I had no
visibility into what was actually happening in the background, and no way
to fix a bot's setup without deleting it and starting over. The activity
feed was the one I wanted most — I kept wondering whether a message had
actually routed or just silently vanished, and had no way to check without
digging through raw log files by hand.

I decided early to keep it structural only, not the actual message text.
That wasn't a technical limitation — the data's right there in the same
logs — it was a deliberate choice to keep this feed about system health, not
turn the dashboard into something that also mirrors every conversation.

The Docker fix was the most annoying one to track down, only because it
looked like a NanoClaw bug at first. Docker just stopped installing on this
Mac one day, no obvious reason. Turned out Docker Desktop had quietly
raised its own minimum macOS version past what my machine runs, and the
install page only ever links to the newest build. Once I knew that, the fix
was simple — pin to the last version that still supports this OS instead of
trusting the generic download link.
