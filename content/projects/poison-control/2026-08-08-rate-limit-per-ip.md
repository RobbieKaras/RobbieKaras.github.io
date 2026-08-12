---
title: Switched rate limiting from global to per-IP
date: 2026-08-08
tags: [blue-team, python]
---

## What changed

- `blue/ratelimit.py` — replaced the single global counter with a per-IP
  token bucket keyed on the source address.
- `config.yml` — `rate_limit` is now `requests_per_ip_per_min` instead of a
  flat total.

## Why I made this change

The global limit was punishing everyone at once. One attacker burst would trip
it and then legit traffic got throttled too, which cost us points. Per-IP means
the noisy source gets slowed down and everyone else is unaffected. Pretty small
change, it just moved the counter into a dict keyed by IP.
