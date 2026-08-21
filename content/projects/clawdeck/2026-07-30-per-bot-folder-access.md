---
title: Letting a specific bot see a specific folder on the host
date: 2026-07-30
tags: [docker, security, nodejs]
---

## What changed

- `app/apply-groups-config-mount-patch.js` — patches NanoClaw's own CLI with
  `groups config add-mount`/`remove-mount`, giving per-bot control over an
  existing host-folder allowlist system that already had the security logic
  built in, just no way to actually drive it per bot.
- `app/folder-access.js` — grows the allowlist automatically the first time
  a new top-level folder gets used, instead of making me pick one root
  folder upfront. New Folders modal per bot: link an existing folder, or
  create the bot its own folder under `~/ClawDeck-Bots/<name>`.
- Confirmed the operational nuance: the allowlist is cached in NanoClaw's
  host process memory, so a brand-new top-level folder needs a full service
  restart to take effect (every bot briefly drops), while a folder under an
  already-covered root only restarts that one bot's own container.

## Why I made this change

I wanted a bot to be able to read and write real files on my Mac, not just
operate inside its own sandboxed workspace. NanoClaw already had a real
security allowlist for exactly this, it just had no CLI surface to
actually manage it per bot, so I added one instead of building a new
permission system from scratch.

The part I went back and forth on was whether to make the user pick one
root folder during setup, the way a lot of tools do. I decided against it,
requiring someone to think that far ahead before they've even used the
feature once felt like the wrong default. Growing the allowlist the first
time a folder actually gets used means there's nothing to configure until
there's something to configure.

I didn't just trust that mounting worked because no error got thrown. I
mounted a real folder into a real bot, asked it to read a file I'd created
on the host and write a new one into a nested subfolder, then went and
checked the actual filesystem myself to confirm the write landed where I
expected. Nested folders being included automatically was something I
checked for specifically, not something I assumed from the code.
