---
title: Rebuilding the chat tab, and the CSS bug that only showed up as a 2px line
date: 2026-08-13
tags: [frontend, css, debugging, nodejs]
---

## What changed

- `app/chat-transcript.js` — parses Claude Code's own full-detail session
  transcripts (real tool-use/tool-result blocks, already written to disk)
  instead of the old chat path's single flattened reply string, which had
  zero tool-call detail available anywhere.
- New frontend: a dependency-free markdown renderer, plus a tool-call block
  view with a red/green diff for edits and a content preview for writes —
  everything shown inline live, not collapsed behind a "show work" toggle.
- Found and fixed a real CSS bug: tool-call boxes had correct DOM content
  and correct CSS, but rendered as 2px-tall lines. `overflow:hidden` on a
  flex item silently changes its automatic minimum size to `0` instead of
  content-based — fixed with `flex-shrink:0`.
- Added a "New conversation" button (`groups new-session`, a new NanoClaw
  core patch) — NanoClaw always reused a group's existing session forever
  with no way to force a fresh one.
- A few smaller usability fixes from the same session: plain-language error
  messages instead of raw backend errors, and a one-click insert for the
  owner-verification phrase instead of copying it from a different tab.

## Why I made this change

I wanted the chat tab to actually feel like watching a real coding session, like it does when using claude code. The data to do that already existed, it just wasn't being read. Claude
Code writes full session transcripts to disk regardless of whether anything
reads them, so this was really about building a real parser for something
that was already there, not adding new instrumentation.

The CSS bug was the most frustrating part of the whole session, because
everything about it looked correct. Right DOM, right styles as written,
wrong result on screen. I couldn't find it by reading the CSS, I only found
it by opening dev tools, clicking the actual broken element, and checking
its Computed height. Once I saw it reporting 2px despite content that
clearly needed more, I knew it had to be a sizing calculation, not a missing
style. `flex-shrink` on an item with `overflow` set is a genuinely
well known gotcha, but I didn't know it going in, I found the mechanism
because the symptom pointed straight at "something is computing a size,"
not because I recognized the pattern up front.

The reset button came out of a side conversation about whether long chats
degrade in quality over time, they do, and turned into a real feature
because NanoClaw genuinely had no way to force a fresh session before this.
One thing worth remembering from testing it, resetting clears the
conversation the model sees immediately, but the bot is separately
instructed to search its own past transcript files when something
references earlier context. So it correctly went and read its own history
back when I asked what we'd just done, right after a reset, which looked
like a broken reset at first glance and wasn't one.
