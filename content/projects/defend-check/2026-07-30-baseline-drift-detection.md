---
title: Added baseline comparison for config drift
date: 2026-07-30
tags: [blue-team, linux, json]
---

## What changed

- `checks/baseline.py` — new module. Saves the current audit result to a
  `baseline.json` and diffs later runs against it.
- `report.py` — findings that are new since the baseline are marked `drift:
  true` in the JSON output.

## Why I made this change

A one-time audit tells you the state right now, but the thing I actually care
about on a box is what *changed* since I last looked. A new listening port or a
new sudo user between two runs is way more interesting than the ports that were
always open. So I save a baseline and diff against it. Kept the diff dumb on
purpose — it just compares finding IDs, no fuzzy matching — because I wanted the
output to be obvious and easy to trust.
