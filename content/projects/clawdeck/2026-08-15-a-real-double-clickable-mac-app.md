---
title: Turning a terminal-run dashboard into a real double-clickable Mac app
date: 2026-08-15
tags: [electron, macos, launchd, debugging]
---

## What changed

- Wrapped the existing dashboard in Electron — a menu bar tray icon and a
  native window loading the same backend, without changing the backend
  itself at all. Chose Electron over Tauri specifically because the backend
  already shells out heavily to `docker`/`pnpm`/`git`/`tailscale` — Tauri
  would have meant rewriting all of that in Rust.
- Built as a universal binary (Intel and Apple Silicon in one `.app`),
  packaged with `electron-builder`, unsigned — no Apple Developer Program
  fee, which means a real Gatekeeper warning on first open that I'll need to
  document when I actually post this.
- Real window/UX fixes: real macOS traffic-light buttons over the
  dashboard's own header instead of a second redundant title bar, a scroll
  bug in the setup wizard, a chat-bubble bug where the primary bot's own
  replies were misrendering as hand-offs to another bot because of how its
  destination got named before a later naming convention existed.
- Confirmed the background service stays fully independent of the app
  window — closing the tray app never stops the bots or the dashboard
  service, by design.
- Tested the whole thing from a second physical device (a Windows PC on the
  same Tailscale network) — created a new bot from the Windows browser and
  watched it appear live on the Mac's own app window.

## Why I made this change

The original plan was just a browser tab, start the server from a
terminal, open `localhost:4001`, use it there. That's fine for me, sitting
at my own Mac while I'm building it. It's not something I could ever hand to
someone else. Nobody who doesn't know computers is opening a terminal and typing a start command just
to try an app, so at some point this had to stop being "a local web page you
run" and become an actual double clickable Mac app instead.

The decision that mattered most in getting there wasn't really technical,
it was whether to pay for an Apple Developer account so the app opens
without a warning. I decided to skip it for now, right-click-to-open once
isn't a huge ask, and I'd rather ship something real and document that one
step clearly than delay shipping anything at all over a $99/year fee.

The cross-device test is the part I actually learned the most from. The
plan was simple, open the dashboard from a different machine over
Tailscale and confirm it worked. It didn't, and the reason took two real
attempts to actually fix. Building the Electron app had reintroduced the
exact PATH problem I'd already fixed twice before, in a new place: the
app's own main process rewrote the background service's config on every
launch, and hardcoded it back to loopback-only. My first fix looked right
and didn't work, I'd made the same GUI-process-has-a-minimal-PATH mistake
a third time, this time inside the Electron app's own process trying to
call `tailscale` directly.

What actually got me to a real fix was refusing to trust the log line that
said "bound to X." I checked with `lsof` directly on the port instead of
reading what the app claimed about itself, and that's what proved the fix
had actually taken effect versus just looking like it had in an older,
still running process. That's stuck as a real habit since: a log line
saying something worked is a claim, not a verification.
