#!/usr/bin/env python3
"""
split_log.py -- split an accumulated changelog into per-entry post files.

In your *project* repos you keep one running changelog, e.g.
poison-control-log.md, where each session is a top-level `# ` heading. This
splits that file into one Markdown file per entry, named and placed so the blog
picks them up automatically.

    python tools/split_log.py ../poison-control/poison-control-log.md poison-control

    # preview without writing anything:
    python tools/split_log.py ../poison-control/poison-control-log.md poison-control --dry-run

Each `# ` section in the source becomes
content/projects/<project>/<date>-<slug>.md. The date comes from a `Date:` or
`date:` line in the section, or a YYYY-MM-DD anywhere in the heading, and falls
back to today with a warning. Existing files are skipped, never overwritten, so
re-running only adds new entries.

The expected section shape (what /log-session produces) is:

    # 2026-08-12 — Rewrote the URL parser

    ## What changed
    - ...

    ## Why I made this change
    ...

Anything roughly like that works. The `# ` line becomes the title; a leading
date in it is stripped from the title and used for the filename.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"

DATE_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
DATE_LINE_RE = re.compile(r"^\s*date\s*[:=]\s*(\d{4}-\d{2}-\d{2})", re.IGNORECASE | re.MULTILINE)
# strip a leading date and common separators from a heading to get the title
TITLE_CLEAN_RE = re.compile(r"^\s*\d{4}-\d{2}-\d{2}\s*[—\-–:·|]*\s*")


def slugify(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-") or "entry"


def split_sections(text: str) -> list[str]:
    """Split on top-level '# ' headings, keeping the heading with its body."""
    # normalise line endings
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    parts = re.split(r"(?m)^(?=\# )", text)
    return [p.strip("\n") for p in parts if p.strip() and p.lstrip().startswith("# ")]


def parse_section(block: str) -> tuple[str, date | None, str]:
    lines = block.split("\n")
    heading = lines[0].lstrip("# ").strip()
    body = "\n".join(lines[1:]).strip("\n")

    # date: from a Date: line, else from the heading, else None
    found = DATE_LINE_RE.search(block)
    if not found:
        found = DATE_RE.search(heading)
    entry_date = None
    if found:
        try:
            entry_date = date.fromisoformat(found.group(1))
        except ValueError:
            entry_date = None

    title = TITLE_CLEAN_RE.sub("", heading).strip() or heading
    # drop a standalone Date: line from the body so it doesn't render
    body = DATE_LINE_RE.sub("", body).strip("\n")
    return title, entry_date, body


def main() -> None:
    p = argparse.ArgumentParser(description="Split a changelog into per-entry files.")
    p.add_argument("logfile", help="path to the accumulated changelog markdown")
    p.add_argument("project", help="project folder slug under content/projects/")
    p.add_argument("--dry-run", action="store_true", help="show what would happen, write nothing")
    args = p.parse_args()

    src = Path(args.logfile)
    if not src.exists():
        sys.exit(f"error: no such file: {src}")

    project = slugify(args.project)
    folder = CONTENT / "projects" / project
    if not folder.exists() and not args.dry_run:
        sys.exit(f"error: no project folder at {folder.relative_to(ROOT)}\n"
                 f"       create it (with a _project.md) before splitting into it.")

    sections = split_sections(src.read_text(encoding="utf-8"))
    if not sections:
        sys.exit("error: found no '# ' sections in that file. Each entry needs a top-level '# ' heading.")

    created = skipped = 0
    for block in sections:
        title, entry_date, body = parse_section(block)

        # Skip a section that isn't really an entry — typically the file's own
        # title header at the top of the changelog. An entry has either a date
        # or '## ' subheadings (What changed / Why...). A bare title has neither.
        if entry_date is None and not re.search(r"(?m)^\#\# ", body):
            print(f"  skip  '{title}' (looks like a file title, not an entry)")
            skipped += 1
            continue

        if entry_date is None:
            entry_date = date.today()
            print(f"  ! '{title}': no date found, using today ({entry_date})")

        slug = slugify(title)
        dest = folder / f"{entry_date.isoformat()}-{slug}.md"

        front = f"---\ntitle: {title}\ndate: {entry_date.isoformat()}\ntags: []\n---\n\n"
        content = front + body + "\n"

        if dest.exists():
            print(f"  skip  {dest.relative_to(ROOT)} (exists)")
            skipped += 1
            continue

        if args.dry_run:
            print(f"  would create {dest.relative_to(ROOT)}")
        else:
            dest.write_text(content, encoding="utf-8")
            print(f"  create {dest.relative_to(ROOT)}")
        created += 1

    verb = "would create" if args.dry_run else "created"
    print(f"\n{verb} {created}, skipped {skipped}")


if __name__ == "__main__":
    main()
