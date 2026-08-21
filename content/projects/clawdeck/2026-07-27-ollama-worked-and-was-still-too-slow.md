---
title: Local Ollama worked. It was just too slow to actually use.
date: 2026-07-27
tags: [ollama, failure, macos]
---

## What changed

- Built a full local provider for NanoClaw using Ollama — reused the same
  mechanism the OpenRouter provider uses, so local and OpenRouter bots could
  coexist without clobbering each other's config.
- Confirmed Docker's `host.docker.internal` reaches Ollama's default,
  loopback-only bind with zero extra configuration on this Mac — didn't
  need the network exposure change most Ollama guides assume you do.
- Found and worked around a real compatibility wall: the current Ollama
  release requires macOS 14+ and refuses to launch on this Ventura Mac at
  all. Pinned the installer to the last release that still supports it.
- Tested two model sizes directly against the real workload, not a toy
  prompt, and confirmed neither one actually worked for a different reason
  each.
- Left the backend in place, fully built and tested at the plumbing level,
  and didn't wire it into the UI.

## Why I made this change

I wanted a genuinely free option that didn't depend on OpenRouter's free
tier staying available, so running a model locally seemed like the obvious
answer — no rate limits, no models disappearing overnight, nothing external
at all.

The plumbing side actually went fine. Docker reaching Ollama without extra
config, the macOS version wall — those were normal, solvable problems. The
part that stopped me wasn't a bug, it was just my own hardware. I tried a
small model first, about 2GB, fast enough to finish a real turn in under
two minutes. It was too weak to reliably do one specific thing NanoClaw
needs — correctly filling in who a reply is addressed to — so it kept
echoing its own instructions back instead of a real answer, and no reply
ever landed. I stepped up to a bigger model that actually followed that
instruction correctly, confirmed directly against Ollama itself. But once I
ran it through NanoClaw's real system prompt, not a short test prompt, a
single reply took almost two and a half minutes on this Mac's CPU — no
GPU acceleration available to it at all — which blows past the point where
the container gives up and calls the turn timed out.

That was the actual dead end: going bigger fixed the instruction-following
problem and made the speed problem worse, and going smaller did the
opposite. There wasn't a middle model size that solved both at once on this
particular machine, and I didn't have a fix for that, just a decision to
make. I chose to stop here rather than keep throwing different model sizes
at a problem that was really about the hardware, not the models. The code
is still there, still working, just not something I point anyone at right
now. If I pick it back up, the real next thing to try isn't a bigger model
— it's a small model actually tuned for tool use instead of general chat.
