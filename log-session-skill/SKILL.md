---
name: log-session
description: >
  Log a coding session to this project's changelog file. Use at the end of a
  work session when the user says "log this session", "write a dev log",
  "update the changelog", or similar. Summarizes the technical facts of what
  changed, then asks the user for their own reasoning and records it verbatim.
---

# log-session

Append an entry to this project's changelog for the session that just happened.
The entry has two parts: **What changed** (facts, written by you) and **Why I
made this change** (reasoning, written by the *user* in their own words). The
whole point of this skill is that the reasoning is genuinely theirs, so the
hard rule below matters more than anything else here.

## The one hard rule

**Never write reasoning the user did not say.** The "Why I made this change"
section contains the user's own words. You may fix grammar, spelling, and
punctuation, and lightly tidy sentence structure. You may NOT add motivations,
justifications, trade-offs, or explanations they didn't give you — not even
plausible-sounding ones, not even to make it read better. If they gave you two
sentences, the Why section is two sentences. If they had nothing to say, the
section is short or omitted. Padding this section defeats the purpose of the
log.

Everything else in this skill is in service of that rule.

## Where the log lives

Look for an existing changelog in the repo root — a file like
`<project>-log.md`, `CHANGELOG.md`, `devlog.md`, or `log.md`. If one exists,
append to it. If none exists, ask the user what to name it (suggest
`<project>-log.md`) and create it. New entries go at the **top** of the file,
under any title line, so the newest is first.

## Step 1 — Summarize the technical facts (you write this)

Figure out what actually changed this session. Use the tools available to you:
check `git diff` / `git status` / `git log` for this session's commits, and
draw on what you did together in the conversation. Write a tight,
factual **What changed** list:

- Files touched, and what changed in each (added / removed / fixed / moved).
- New or deleted functions, modules, endpoints, config keys, dependencies.
- Keep it to facts. No reasoning, no "this improves…", no praise. If you're
  tempted to write why, stop — that's the user's section.

Format each item like `` `path/to/file.py` `` — what changed, one bullet each.

## Step 2 — Gauge the size of the session, THEN ask

Before asking anything, decide how big this session was. This controls how many
questions you ask. Do not ask a fixed number every time — that produces
repetitive, low-value prompts on days when nothing interesting happened.

**Small session** — a minor fix, a rename, a version bump, a formatting pass,
anything mechanical with no real decision behind it:
- Ask **at most one** light question, or **none** if there's genuinely nothing
  to reflect on. A reasonable single question: *"Anything worth noting about
  why, or was this just a straightforward fix?"*
- If they say it was nothing, accept that. Write a short or empty Why section.
  Do not fish for more.

**Substantial session** — a real design decision, a non-obvious approach, a
tricky bug, something they chose one way over another:
- Ask **a few** short questions, **one at a time** (wait for each answer before
  asking the next — don't dump a list). Draw from:
  - "Why did you decide to make this change?"
  - "What did you try first, and why didn't it work?"
  - "Was there anything tricky or unexpected in this session?"
- Stop once you have their reasoning. Three questions is a ceiling, not a quota
  — if the first answer covers it, don't force the rest.

When unsure which bucket you're in, lean toward fewer questions. It's better to
under-ask than to nag.

## Step 3 — Write the entry

Assemble the entry in this exact shape and append it (newest at top):

```markdown
# YYYY-MM-DD — <short title describing the change>

## What changed

- `file` — what changed
- ...

## Why I made this change

<the user's answers, in their own words, grammar-fixed only>
```

Notes:
- Use today's date. Get it from the environment/context; don't guess.
- The title is a short factual description of the change (you write this).
- Combine the user's answers into readable prose, but keep their wording,
  their reasoning, and their level of detail. Don't merge in facts from the
  What-changed section to bulk it up.
- If the user answered a question with "not really" or "no", don't represent
  that as insight. Just leave it out. A short Why section is fine and expected.

## Step 4 — Confirm

Show the user the finished entry and confirm it's appended. If they want to edit
their own wording, let them — it's their section.

---

This structure (What changed / Why I made this change) matches the blog these
logs feed into, so a finished entry can be dropped into the site with the
`split_log.py` tool and minimal reformatting.
