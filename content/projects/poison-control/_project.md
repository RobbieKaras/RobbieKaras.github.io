---
title: Poison Control
summary: A CTF red-vs-blue engine — red team extracts and fast-blasts SQL injection payloads, blue team scores and blocks them in real time.
tech: [Python, OWASP ZAP, OpenAI API, CTFd]
repo: https://github.com/RobbieKaras
status: Active
order: 1
---

Poison Control is a red-vs-blue automation project built around a CTF-style
scoreboard. The red team side extracts payloads from OWASP ZAP, runs a
GitHub command-injection payload repo, does Phase 0 fast-blast attacks, and
enumerates SQL tables and columns to capture flags before the blue team can
respond. The blue team side deploys regex scoring, evasion-aware LLM
confirmation, attack-prep detection, first-access endpoint blocking, and
per-IP rate limiting to neutralize attacks before payloads land.

The log below tracks the build session by session.
