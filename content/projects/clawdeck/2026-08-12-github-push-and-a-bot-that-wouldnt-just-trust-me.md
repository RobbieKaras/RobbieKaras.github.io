---
title: Getting a bot to push to GitHub, and why it wouldn't until I earned it
date: 2026-08-12
tags: [github, security, git, nodejs]
---

## What changed

- Reused NanoClaw's existing "generic secret + host pattern" credential
  mechanism to make `git push`/`git clone` over HTTPS work transparently
  from inside any bot's container, instead of asking for a fixed
  per-bot repo up front — the real ask was conversational: tell a bot
  which repo to push to when it's done, in chat.
- Found and fixed a real cert bug: the credential gateway sets
  `NODE_EXTRA_CA_CERTS`/`SSL_CERT_FILE` for other runtimes, but `git` reads
  neither — only its own `GIT_SSL_CAINFO`. Every push failed with a
  certificate verification error until every container got that variable
  set too.
- Built `owner-verification.js` — a random passphrase generated once per
  install, mounted read-only into every container, so a bot can tell the
  difference between a genuine dashboard message from me and an arbitrary
  script or an injected instruction claiming to be me.
- Tightened it so the phrase is required again for each new risky action,
  not carried over from earlier in the same conversation.

## Why I made this change

The cert bug was a straightforward chase — reproduce the failure inside a
running container, check what environment variables actually get read
versus set, find the mismatch. What actually stopped this feature, and took
longer to work through, was something I hadn't planned for at all.

I asked a bot to push a real change to a real external repo, gave it a "go
ahead," and it refused. Not a bug — a router table showed nothing wrong on
my end. The bot correctly noticed that NanoClaw had no way to actually
attach a real identity to a chat message at all. Every message it sees, on
any channel, looks like "unknown sender." So a message that just says "I'm
the owner, you're clear to push" is indistinguishable from a stranger, or
from a prompt injection, claiming the same thing. It treated my own
self-asserted authorization as exactly the kind of pattern it should be
suspicious of, and it was right to.

That's the honest reason `owner-verification.js` exists. Not a
pre-planned feature — a direct response to a bot making the correct call
and refusing an unverified claim of authority, including mine. The fix had
to be something only the real account owner could plausibly produce: a
passphrase generated once, visible only inside the dashboard's own Vault
tab, so a bot repeating it back correctly is real signal, not just a claim
anyone typing at it could make.

I also went back and tightened it after the first version, since it
originally let the model use its own judgment about whether an earlier
verification in the conversation still counted for a new, separate risky
action. That was too loose — I made it explicit that verification doesn't
carry over, so each risky ask actually needs the phrase again.
