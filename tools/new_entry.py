#!/usr/bin/env python3
"""
new_entry.py -- scaffold a blank, correctly-named entry file.

    python tools/new_entry.py poison-control "Rewrote the URL parser"
    python tools/new_entry.py --post "Why I switched editors"

Creates content/projects/<project>/<today>-<slug>.md (or content/posts/... with
--post), pre-filled with frontmatter and the two section headings, so you never
have to remember the format. Prints the path it created.

Uses today's date. Pass --date YYYY-MM-DD to override.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "untitled"


TEMPLATE = """\
---
title: {title}
date: {date}
tags: []
---

## What changed

-

## Why I made this change


"""

POST_TEMPLATE = """\
---
title: {title}
date: {date}
tags: []
---

Write your post here.
"""


def main() -> None:
    p = argparse.ArgumentParser(description="Scaffold a new entry.")
    p.add_argument("project", help="project folder slug, or the title if using --post")
    p.add_argument("title", nargs="?", help="entry title (omit when using --post)")
    p.add_argument("--post", action="store_true", help="create a standalone post instead of a project update")
    p.add_argument("--date", help="YYYY-MM-DD (defaults to today)")
    args = p.parse_args()

    entry_date = args.date or date.today().isoformat()
    if not re.match(r"\d{4}-\d{2}-\d{2}", entry_date):
        sys.exit(f"error: --date must be YYYY-MM-DD, got {entry_date!r}")

    if args.post:
        title = args.project
        slug = slugify(title)
        dest = CONTENT / "posts" / f"{entry_date}-{slug}.md"
        body = POST_TEMPLATE.format(title=title, date=entry_date)
    else:
        if not args.title:
            sys.exit("error: provide a title, e.g.\n  python tools/new_entry.py poison-control \"Fixed the parser\"")
        project = slugify(args.project)
        title = args.title
        slug = slugify(title)
        folder = CONTENT / "projects" / project
        if not folder.exists():
            sys.exit(f"error: no project folder at {folder.relative_to(ROOT)}\n"
                     f"       create it with a _project.md first, or check the name.")
        dest = folder / f"{entry_date}-{slug}.md"
        body = TEMPLATE.format(title=title, date=entry_date)

    if dest.exists():
        sys.exit(f"error: {dest.relative_to(ROOT)} already exists")

    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(body, encoding="utf-8")
    print(f"created {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
