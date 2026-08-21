---
title: ClawDeck
summary: A native macOS app and self-hosted dashboard for running a personal AI agent — guided setup wizard, multi-bot management, and a credential vault, wrapped in a distributable Electron app.
tech: [Electron, Node.js, Docker, macOS]
repo: https://github.com/RobbieKaras/clawdeck
status: Active
order: 3
---

ClawDeck started from a simple want: my own AI assistant, running on my own
hardware, that I actually control — not a chat window owned by someone else's
cloud. That part is genuinely possible today. The problem is that getting there
means Docker, API keys, config files, and a dozen quiet ways to get it wrong.
Fine for me. A non-starter for anyone who doesn't live in a terminal.

So ClawDeck is the front door. It's a Node/Express dashboard wrapped in a native
macOS (Electron) app that installs and runs a self-hosted agent — NanoClaw — on
someone's own Mac: a guided setup wizard that checks your keys *before* they can
silently fail, multi-bot creation, Telegram and Discord connections, and a local
credential vault. Packaged as a normal double-clickable app instead of a README
full of commands.

The interesting part — and the reason this log exists — is that almost none of
the work is the dashboard. It's everything underneath. ClawDeck wraps a
fast-moving open-source project, so most sessions are spent finding the thing
that's quietly broken: a bot that looked paired for weeks and had never once
replied, a provider patch that drifted out from under a new release, a Docker
command that hangs forever on exactly this machine — and making it so the person
installing this never has to see any of it.

The log below tracks the build session by session.
