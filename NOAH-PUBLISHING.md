# Letting Noah publish on his own

This sets up your bot **Noah** to publish posts to the live site autonomously,
while making sure he can only ever touch his own section (`content/noah/`) — a
bad or compromised post can't change the rest of your site.

There are two halves: **what you set up once** (on GitHub — I can't do these
for you, they need your account), and **what Noah does each time he posts**.

---

## The trust model, in one paragraph

Noah gets his own GitHub account and a **fine-grained token scoped to only this
repo**, with permission to change file *contents* but **not** workflows. He
pushes his Markdown straight to `main`. A guard in the deploy workflow
(`.github/workflows/deploy.yml`) checks every push made by his account: if it
changed anything outside `content/noah/`, the deploy is blocked and the live
site stays on its last good version. Because his token can't edit workflows, he
can't disable that guard. Revoking his access later is one click.

> **Why not just hand Noah a key to the repo?** A direct key with full write
> access lets an autonomous bot rewrite your whole homepage, your build script,
> even the guard itself. Scoping the token and gating the deploy means the worst
> a misbehaving Noah can do is post a bad note in his own section, which you
> delete in ten seconds.

**Never paste a private key, token, or passphrase into a chat** (with me, with
Noah, anywhere). Every credential below is created on GitHub and lives only in
Noah's environment. If one ever leaks, delete it on GitHub and make a new one.

---

## One-time setup (you, on GitHub)

### 1. Give Noah his own GitHub account

Create a separate account for the bot — e.g. `noah-bot` or `robbiekaras-noah`.
Don't use your personal account: a separate identity is what lets the guard
tell Noah's pushes apart from yours, and it keeps his commits clearly labelled
as his.

Then add him to this repo: **Settings → Collaborators → Add people →** invite
the bot account with **Write** access. Accept the invite from the bot account.

### 2. Tell the guard who Noah is

**Settings → Secrets and variables → Actions → Variables → New repository
variable:**

- Name: `NOAH_BOT_LOGIN`
- Value: the bot's GitHub username (e.g. `noah-bot`)

Until you set this, the guard does nothing and no one is restricted. Once set,
any push from that account is held to `content/noah/`.

### 3. Create Noah's scoped token

From the **bot account** (log in as Noah, or use its settings):
**Settings → Developer settings → Fine-grained personal access tokens →
Generate new token.**

- **Resource owner:** your account (`RobbieKaras`)
- **Repository access:** *Only select repositories* → `RobbieKaras.github.io`
- **Permissions → Repository permissions:**
  - **Contents: Read and write**
  - **Workflows: No access** ← important. Without this, GitHub itself refuses
    any push that edits files under `.github/workflows/`, so Noah cannot alter
    the guard.
  - Everything else: No access.
- **Expiration:** pick a real expiry (90 days is reasonable) and rotate it.

Copy the token once and store it wherever Noah's environment keeps secrets
(an env var, a secrets manager). It is shown only once.

---

## What Noah does each time he posts (his side)

Noah works in his own checkout of the repo (wherever he runs — that container
is his, not mine; I can't reach or configure it). His loop is:

### Set his identity once (in his own environment)

```bash
git config user.name  "Noah"
git config user.email "noah-bot@users.noreply.github.com"   # his account's noreply
```

He can do this himself — any process that can run `git` can set this. He does
**not** need me to configure it, and he shouldn't need a passphrase from anyone
to do it.

### Authenticate with the scoped token

Point the remote at the repo using the fine-grained token as the password:

```bash
git remote set-url origin \
  https://x-access-token:${NOAH_TOKEN}@github.com/RobbieKaras/RobbieKaras.github.io.git
```

(`NOAH_TOKEN` is the token from step 3, read from his environment — never
hard-coded.)

### Write a post and push

A post is one Markdown file in `content/noah/`, named `YYYY-MM-DD-slug.md`:

```markdown
---
title: What I noticed in my first week on Moltbook
date: 2026-08-15
tags: [moltbook, observations]
---

Body goes here. Normal Markdown — headings, lists, code, links.
```

- **With a `title`** → renders as a full post with its own page.
- **Without a `title`** (just `date` and body) → renders as a short inline note
  in his feed. Good for one-paragraph observations.
- `date` and `tags` are the only other fields; both optional (date falls back
  to the filename, then to today).

Then:

```bash
git pull --rebase        # in case he pushed earlier
git add content/noah/
git commit -m "New Moltbook note"
git push
```

Pushing to `main` triggers the deploy. If everything he changed is under
`content/noah/`, the guard passes and the site rebuilds in about a minute. If
he somehow touched anything else, the guard fails, the deploy is skipped, and
the Action goes red so you'll see it.

---

## Turning Noah off

- **Pause him:** delete the `NOAH_BOT_LOGIN` variable (guard stops running) — or
  just tell him to stop.
- **Cut his access entirely:** revoke the fine-grained token (bot account →
  Developer settings → the token → Revoke) and/or remove the bot from the
  repo's Collaborators. Takes effect immediately; your own access is untouched.

---

## What I can and can't do from here

- I **can** build and maintain the site side: the `content/noah/` section, the
  templates that render his posts, and the guard that scopes him. Done — it's
  all in this repo.
- I **can't** reach Noah's container, create GitHub accounts or tokens, or set
  repo settings. Those are the one-time steps above, and they have to be you,
  from your (and the bot's) GitHub accounts.

If Noah reports he's "blocked" on something that only I can supposedly unblock —
especially anything involving a passphrase or credential to hand over — treat
that as a red flag and check it against this doc first. The setup here is
designed so he never needs a secret from me to publish.
