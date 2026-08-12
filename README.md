# RobbieKaras.Blog

A static personal blog and portfolio. Content is Markdown; a small Python
script (`build.py`) renders it to a plain HTML/CSS site with no framework.
Hosted free on GitHub Pages.

- **No database, no backend.** Markdown files in, static HTML out.
- **Adding a post = dropping one Markdown file in a folder.** Nothing to register.
- **Two-section entry format** — *What changed* / *Why I made this change* — so a
  session changelog drops in with almost no reformatting.

---

## Quick start (local)

You need Python 3.10+.

```bash
pip install -r requirements.txt
python serve.py          # builds, then serves at localhost:8000 and opens a browser
```

Or build once without serving:

```bash
python build.py          # output goes to site/  (git-ignored)
```

Re-run either after changing content. `serve.py 3000` uses a different port;
`serve.py --no-open` skips opening the browser.

---

## How content works

Everything lives under `content/`. The folder a file is in decides what it is.

```
content/
├── _home.md                     intro text on the homepage
├── about.md                     -> /about/   (any *.md here becomes a page)
├── posts/
│   └── 2026-08-01-why-i-keep-a-dev-log.md      -> /posts/why-i-keep-a-dev-log/
└── projects/
    ├── poison-control/
    │   ├── _project.md          project name, blurb, tech, repo link
    │   ├── 2026-08-08-rate-limit-per-ip.md
    │   └── 2026-08-12-llm-payload-confirmation.md
    └── defend-check/
        ├── _project.md
        └── 2026-07-30-baseline-drift-detection.md
```

- **A project** is a folder under `content/projects/`. Its `_project.md` holds
  the metadata. Every other `.md` in the folder is a dated update, listed
  newest-first on the project page, each with its own URL.
- **A standalone post** is a `.md` in `content/posts/`.
- **A standalone page** (like About) is a `.md` directly in `content/`.
- Files and folders starting with `_` are metadata/intro, not entries.

### Entry format

```markdown
---
title: Rewrote the URL parser
date: 2026-08-12
tags: [parsing, python]
---

## What changed

- `scanner/parse.py` — replaced regex matching with `urllib.parse`

## Why I made this change

The regex broke on encoded characters, so I switched to the stdlib parser...
```

The two headings are just normal `##` Markdown — the build gives them no
special handling. That's deliberate: a finished changelog entry pastes straight
in. Frontmatter is minimal and has fallbacks:

- **date** — taken from frontmatter, else from the `YYYY-MM-DD` prefix in the
  filename, else the file's modified time (with a warning).
- **title** — frontmatter `title`, else a leading `# H1` in the body, else the
  filename.
- **tags** — a list; optional. **summary** — optional; auto-generated from the
  first paragraph if omitted. **draft: true** — hides the entry from the build.

### `_project.md`

```markdown
---
title: Poison Control
summary: One-line description shown in project lists.
tech: [Python, OWASP ZAP, OpenAI API]
repo: https://github.com/RobbieKaras/poison-control
status: Active
order: 1
---

Longer overview paragraph(s), shown at the top of the project page.
```

`order` controls position in the project list (lower = higher up). All fields
except the folder name are optional.

---

## Helper scripts (optional)

```bash
# scaffold a correctly-named, pre-filled entry file:
python tools/new_entry.py poison-control "Rewrote the URL parser"
python tools/new_entry.py --post "Why I switched editors"

# split an accumulated changelog from a project repo into per-entry files:
python tools/split_log.py ../poison-control/poison-control-log.md poison-control
python tools/split_log.py ../poison-control/poison-control-log.md poison-control --dry-run
```

`split_log.py` reads a changelog where each session is a top-level `# ` heading
and writes one file per entry into the right project folder. It skips files that
already exist, so re-running only adds new entries.

---

## The session-logging workflow

`log-session-skill/SKILL.md` is a Claude Code skill for your **project** repos
(not this one). Copy it into a project repo like this:

```
poison-control/
└── .claude/
    └── skills/
        └── log-session/
            └── SKILL.md      <- copy log-session-skill/SKILL.md to here
```

Then at the end of a coding session, tell Claude Code *"log this session."* It
will summarize the technical facts, gauge how big the session was (one light
question for a small fix, a few for a real decision), and record **your** answers
verbatim in the *Why I made this change* section — grammar fixed, but no reasoning
added that you didn't say. The output matches this blog's entry format, so
`split_log.py` can pull it over later.

---

## Deploying to GitHub Pages

One-time setup:

1. Create a repo named **`RobbieKaras.Blog`** on GitHub and push this project to
   the `main` branch.

   ```bash
   git init
   git add .
   git commit -m "Initial site"
   git branch -M main
   git remote add origin https://github.com/RobbieKaras/RobbieKaras.Blog.git
   git push -u origin main
   ```

2. On GitHub: **Settings → Pages → Build and deployment → Source →
   "GitHub Actions"**. (Not "Deploy from a branch".)

That's it. The included workflow (`.github/workflows/deploy.yml`) runs on every
push to `main`: it installs Python, runs `build.py`, and publishes `site/`. You
never commit built HTML — `site/` is git-ignored.

Your site will be at:

```
https://robbiekaras.github.io/RobbieKaras.Blog/
```

**From then on, publishing is just:** add or edit a Markdown file, commit, push.
The site rebuilds itself in about a minute (watch the **Actions** tab).

### If you use a different repo name or a custom domain

Everything hosting-related is in `config.py`:

- **Root URL with no sub-path** — rename the repo to `robbiekaras.github.io`,
  then set `base_url` to `""` in `config.py`.
- **Custom domain** (e.g. you buy `robbiekaras.blog`) — set `cname` to your
  domain, `base_url` to `""`, and `url` to `https://your-domain`, then configure
  the domain under Settings → Pages. The build writes the `CNAME` file for you.

---

## Project layout

```
build.py          the generator — reads content/, writes site/
serve.py          local preview server
config.py         name, links, hosting settings — the only file you edit for those
requirements.txt  Python dependencies
templates/        Jinja2 HTML templates
static/           style.css, main.js, favicon
content/          your Markdown (the only folder you touch day to day)
tools/            new_entry.py, split_log.py
site/             build output (git-ignored, rebuilt each time)
.github/workflows/deploy.yml   GitHub Pages deploy
```
