---
title: Making the dashboard reachable from my laptop, without exposing it to the internet
date: 2026-07-30
tags: [tailscale, security, macos, launchd]
---

## What changed

- Bound the dashboard server to this Mac's Tailscale IP in addition to
  `127.0.0.1`, instead of `0.0.0.0` or building real login first.
- Turned the dashboard into a real `launchd` service
  (`com.clawdeck.dashboard`) with `RunAtLoad`/`KeepAlive`, instead of
  starting it by hand in a terminal every session.
- Fixed a real bug the persistent service introduced: `launchd`'s own
  default `PATH` doesn't include `/usr/local/bin`, so every endpoint that
  shells out to `pnpm`/NanoClaw's own CLI — which is most of them — failed
  silently once the dashboard stopped being launched from a normal shell.
- Fixed a second, narrower version of the same bug a few days later: the
  real `claude` CLI binary lives at `~/.local/bin/claude`, which wasn't in
  that `PATH` either, so "Sign in with Claude" specifically kept failing
  through the persistent service even after the first fix.

## Why I made this change

The dashboard has zero authentication on any endpoint — create a bot, read
the vault, delete anything — by deliberate design, since it's meant to be
one person's own install on their own machine, not a shared product. That
meant I couldn't just widen the bind to the whole network to reach it from
my laptop. Tailscale was the obvious answer: it's already an encrypted,
private network between my own devices, so binding to that IP specifically
gets me remote access without changing the actual security tradeoff at all.

The PATH bug was the more interesting problem, mostly because of how it
first showed up: everything had worked fine right up until I stopped
running the server by hand in a terminal and let it run persistently
instead. A terminal shell inherits a real, full PATH. A background service
launched by `launchd` does not — it gets a bare minimum one. I hadn't
thought about that distinction at all until things that worked a minute
earlier started failing with `ENOENT` the moment the exact same code ran as
a service instead.

Even after I thought I'd fixed it, a narrower version of the same bug came
back days later for one specific binary that lived somewhere I hadn't added
yet. That's the part that actually stuck with me — this wasn't one bug, it
was a whole category of bug, and I was going to keep hitting narrower
versions of it anywhere a GUI- or service-launched process shells out to
something that isn't on that minimal default PATH.
