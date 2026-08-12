---
title: Added LLM confirmation to cut false positives on the blue team scorer
date: 2026-08-12
tags: [blue-team, detection, llm, python]
---

## What changed

- `blue/scorer.py` — added an `llm_confirm()` step that runs after the regex
  match. A request only counts as a real injection attempt if the regex fires
  *and* the LLM check agrees.
- `blue/scorer.py` — moved the old regex-only decision into a
  `regex_prescreen()` helper so the LLM only sees traffic that already looks
  suspicious. Nothing else calls the model.
- `blue/llm_client.py` — new file. Wraps the OpenAI call, sends a fixed system
  prompt plus the raw request body, and parses a strict `injection: yes/no`
  response. Times out at 2s and fails open (treats a timeout as "not an
  attack") so the scorer never stalls.
- `config.yml` — added `llm_confirmation: true` and a `max_llm_calls_per_min`
  cap so a flood can't run up the API bill.
- `tests/test_scorer.py` — added cases for the two-stage path: regex-miss short
  circuits, regex-hit-LLM-no is dropped, regex-hit-LLM-yes scores.

The regex layer is unchanged in what it matches. This only adds a second gate
behind it. The decision path is now:

```python
def score_request(req):
    if not regex_prescreen(req):
        return CLEAN                      # fast path — most traffic stops here
    if not llm_confirm(req):              # only suspicious traffic reaches the model
        return CLEAN                      # regex hit, LLM disagreed -> false positive
    return INJECTION_ATTEMPT
```

## Why I made this change

During the last scrimmage the blue team scorer kept flagging normal login
traffic as SQL injection. It was killing our score because every false positive
blocked a real user endpoint and the CTFd health check counted that against us.

I tried just making the regex stricter first. That didn't really work — every
time I tightened it to stop the false positives, the red team's Phase 0
fast-blast payloads started slipping through because they were slightly
obfuscated and didn't match the tighter pattern anymore. So I was stuck
choosing between too many false positives or too many misses and I couldn't get
both low at once with just regex.

The thing that was actually tricky was latency. I didn't want to send every
request to the LLM because it's slow and there's a rate limit, and the red team
attacks come in bursts. So I made the regex a prescreen — it's fast and catches
the obvious stuff, and only the maybe-suspicious ones go to the model. That
kept the LLM call count low enough to stay under the limit during a burst. I
also made it fail open on a timeout because if the model is slow I'd rather miss
one attack than freeze the whole scorer and drop every request in the queue.

Still not sure the 2 second timeout is the right number. I picked it because it
felt safe but I haven't actually measured what the model's normal response time
is under load, so that's the next thing to check.
