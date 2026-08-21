---
title: Six bugs a fresh install on someone else's Mac found that mine never would
date: 2026-08-20
tags: [electron, macos, debugging, nodejs]
---

## What changed

- Shipped ClawDeck as an actual downloadable `.dmg` on GitHub Releases for
  the first time, so it could be tested on a machine that wasn't mine.
- `app/launch.js` — wired in `apply-groups-config-ensure-patch.js`, a patch
  that existed in the codebase but was never actually called. Without it,
  creating any bot beyond the first one silently succeeded in the UI but
  left the bot with no container config — unreachable, invisible in the
  dashboard's bot tree.
- `app/claude-subscription-auth.js` — the "Sign in with Claude" flow now
  auto-installs the Claude Code CLI and a credential-vault CLI/gateway
  (OneCLI) if either is missing, instead of failing with an error telling
  the user to go run setup manually first.
- Replaced the sign-in flow's use of `script(1)` (wrapping the CLI in a fake
  terminal) with a real pseudo-terminal via `node-pty`. `script` was failing
  on a real machine in a way I couldn't reproduce on mine; rather than keep
  guessing at why, this removes the dependency on `script`'s own startup
  behavior entirely.
- Added an actual reachability check for the credential vault's gateway (a
  Docker container) before sign-in, instead of only checking that its CLI
  binary existed — a machine that had already signed in before could still
  have the gateway itself down. Restarts existing containers directly
  rather than re-running the full installer, since the docs for that
  installer warn it can disrupt other live sessions.
- Fixed the order of three chained patches to NanoClaw's own CLI
  (`new-session`, `answer-question`, `cleanup-sessions`) — one was running
  before the patches it depended on, which only breaks on a genuinely fresh
  install, never on one that's already been patched once.
- Added a way to pair an already-connected Telegram bot to a *second* chat
  — the UI had no path back to the pairing flow once a bot showed
  "Connected," even though the backend already supported it.
- Ran a fully isolated, throwaway install end-to-end (clone, patches,
  credential vault, service, container build, a second bot) to verify all
  of the above together before calling it done, then tore it down.

## Why I made this change

 I found these bugs becuase I wanted to test ClawDeck on an Apple Silicon Mac, (I have been building ClawDeck on an Intel Mac). Every one of these had been sitting in the code for a while, invisible,
because my own Mac already had everything configured from earlier
development, the patch that never got wired in, the CLI that was already
installed, the credential vault that was already running. None of that gets
re-tested just from me using the app day to day.

So I had my dad actually download the `.dmg` and set it up cold on his own
Mac. Almost every step he hit turned up something real: bots that looked
created but couldn't be talked to, a sign-in that crashed with an error I'd
never seen, then a different error after that fix, then a third. Some of
that back-and-forth was me getting the diagnosis wrong the first time — I
assumed the sign-in crash was a shadowed system binary, shipped a fix for
that, and it changed nothing, because the actual cause was something I
couldn't reproduce on my own machine at all. That's what pushed me toward
the node-pty rewrite instead of another patch on top of a mechanism I didn't
fully trust anymore.

The pattern by the end was clear enough that I stopped treating each bug as
one off, anything that only runs once, at first-install, on a machine that's
never touched this code before, is exactly the code path I have the least
real coverage on. So the last thing I did wasn't a bug fix at all, I built
a disposable, isolated install just to run that exact path myself and watch
it succeed, instead of shipping the sixth fix on faith the way the first one
went out.

One thing is still open: pairing two bots into the same Telegram group chat.
I know why it's not working from the code, but I haven't been able to
verify the fix live yet, since I'm not back at that Mac to test it. That's
next.
