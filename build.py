#!/usr/bin/env python3
"""
build.py -- the whole static site generator.

Reads Markdown from content/, renders it through the Jinja2 templates in
templates/, and writes a complete static site into site/.

    python build.py     build once into site/
    python serve.py     build, then preview at http://localhost:8000

Content model
-------------
content/_home.md                        intro shown on the homepage
content/about.md                        -> /about/          (any *.md here
content/whatever.md                        becomes a standalone page)
content/posts/2026-08-01-slug.md        -> /posts/slug/
content/projects/<project>/_project.md  project metadata + overview
content/projects/<project>/2026-08-12-slug.md
                                        -> /projects/<project>/2026-08-12-slug/

Nothing needs registering anywhere. Drop a file in, it shows up.
"""

from __future__ import annotations

import html as html_lib
import re
import shutil
from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from email.utils import format_datetime
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pygments.formatters import HtmlFormatter

from config import SITE

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
OUTPUT = ROOT / "site"

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n?", re.DOTALL)
DATED_NAME_RE = re.compile(r"\A(\d{4}-\d{2}-\d{2})[-_](.+)\Z")
H1_RE = re.compile(r"\A\s*#\s+(.+?)[ \t]*(?:\n|\Z)")
HEADING_BLOCK_RE = re.compile(r"<h[1-6][^>]*>.*?</h[1-6]>", re.DOTALL | re.IGNORECASE)
HTML_TAG_RE = re.compile(r"<[^>]+>")
SLUG_CLEAN_RE = re.compile(r"[^a-z0-9]+")

MD_EXTENSIONS = ["extra", "admonition", "codehilite", "sane_lists", "smarty", "toc"]
MD_CONFIG = {
    "codehilite": {"guess_lang": False, "linenums": False},
    "toc": {"permalink": False},
}

_md = markdown.Markdown(extensions=MD_EXTENSIONS, extension_configs=MD_CONFIG)


# --------------------------------------------------------------------------
# small helpers
# --------------------------------------------------------------------------

def render_markdown(text: str) -> str:
    _md.reset()
    return _md.convert(text)


def url(path: str = "/") -> str:
    """Site-relative URL, respecting base_url."""
    base = SITE["base_url"].rstrip("/")
    path = "/" + str(path).lstrip("/")
    return base + re.sub(r"/{2,}", "/", path)


def abs_url(path: str = "/") -> str:
    """Absolute URL, for the feed and social metadata."""
    return SITE["url"].rstrip("/") + url(path)


def slugify(text: str) -> str:
    return SLUG_CLEAN_RE.sub("-", str(text).lower()).strip("-") or "untitled"


def coerce_date(value, fallback: date | None = None) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str) and value.strip():
        for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d %B %Y", "%B %d, %Y"):
            try:
                return datetime.strptime(value.strip(), fmt).date()
            except ValueError:
                continue
    return fallback


def as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [str(item).strip() for item in value if str(item).strip()]


def make_excerpt(body_html: str, limit: int = 190) -> str:
    """Plain-text preview: headings dropped, tags stripped, cut on a word."""
    text = HEADING_BLOCK_RE.sub(" ", body_html)
    text = HTML_TAG_RE.sub(" ", text)
    text = html_lib.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    if len(text) <= limit:
        return text
    return text[:limit].rsplit(" ", 1)[0].rstrip(",.;:-") + "…"


def long_date(value: date) -> str:
    """'August 12, 2026' -- built by hand because %-d is not portable."""
    return f"{value.strftime('%B')} {value.day}, {value.year}"


def split_frontmatter(path: Path) -> tuple[dict, str]:
    raw = path.read_text(encoding="utf-8")
    meta: dict = {}
    match = FRONTMATTER_RE.match(raw)
    if match:
        parsed = yaml.safe_load(match.group(1))
        if isinstance(parsed, dict):
            meta = parsed
        raw = raw[match.end():]
    return meta, raw


def pop_h1(body: str) -> tuple[str | None, str]:
    """If the body opens with an H1, use it as the title and remove it."""
    match = H1_RE.match(body)
    if match:
        return match.group(1).strip(), body[match.end():]
    return None, body


# --------------------------------------------------------------------------
# content model
# --------------------------------------------------------------------------

@dataclass
class Doc:
    """A single renderable piece of writing: a project update or a post."""
    title: str
    slug: str
    url: str
    date: date
    tags: list[str]
    summary: str
    body_html: str
    source: Path
    kind: str = "post"            # "post" | "update" | "noah"
    project: "Project | None" = None
    draft: bool = False
    has_title: bool = True        # False = an untitled short note (feed style)

    @property
    def context_name(self) -> str:
        if self.project:
            return self.project.title
        return {"noah": "Noah", "post": "Post"}.get(self.kind, "Post")


@dataclass
class Project:
    slug: str
    title: str
    summary: str
    tech: list[str]
    repo: str | None
    status: str | None
    order: int
    body_html: str
    url: str
    updates: list[Doc] = field(default_factory=list)

    @property
    def latest_date(self) -> date | None:
        return self.updates[0].date if self.updates else None


@dataclass
class Page:
    title: str
    slug: str
    url: str
    body_html: str


def load_doc(path: Path, *, kind: str, url_for_slug, project=None) -> Doc | None:
    meta, body = split_frontmatter(path)

    stem = path.stem
    name_match = DATED_NAME_RE.match(stem)
    file_date = coerce_date(name_match.group(1)) if name_match else None
    file_slug = name_match.group(2) if name_match else stem

    h1_title, body = pop_h1(body)

    entry_date = coerce_date(meta.get("date"), file_date)
    if entry_date is None:
        entry_date = date.fromtimestamp(path.stat().st_mtime)
        print(f"  ! {path.relative_to(ROOT)}: no date in frontmatter or filename, "
              f"using file modified date ({entry_date})")

    explicit_title = meta.get("title") or h1_title
    title = explicit_title or file_slug.replace("-", " ").capitalize()
    slug = slugify(meta.get("slug") or file_slug)
    body_html = render_markdown(body)

    return Doc(
        title=str(title),
        slug=slug,
        url=url_for_slug(entry_date, slug),
        date=entry_date,
        tags=as_list(meta.get("tags")),
        summary=str(meta.get("summary") or "").strip() or make_excerpt(body_html),
        body_html=body_html,
        source=path,
        kind=kind,
        project=project,
        draft=bool(meta.get("draft", False)),
        has_title=bool(explicit_title),
    )


def load_projects() -> list[Project]:
    projects: list[Project] = []
    root = CONTENT / "projects"
    if not root.is_dir():
        return projects

    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        meta_file = folder / "_project.md"
        meta, body = split_frontmatter(meta_file) if meta_file.exists() else ({}, "")
        h1_title, body = pop_h1(body)

        slug = slugify(meta.get("slug") or folder.name)
        project = Project(
            slug=slug,
            title=str(meta.get("title") or h1_title or folder.name.replace("-", " ").title()),
            summary=str(meta.get("summary") or "").strip(),
            tech=as_list(meta.get("tech")),
            repo=meta.get("repo") or None,
            status=meta.get("status") or None,
            order=int(meta.get("order", 100)),
            body_html=render_markdown(body) if body.strip() else "",
            url=url(f"/projects/{slug}/"),
        )

        for md_file in sorted(folder.glob("*.md")):
            if md_file.name.startswith("_"):
                continue
            doc = load_doc(
                md_file,
                kind="update",
                url_for_slug=lambda d, s, _p=slug: url(f"/projects/{_p}/{d.isoformat()}-{s}/"),
                project=project,
            )
            if doc and not doc.draft:
                project.updates.append(doc)

        project.updates.sort(key=lambda d: (d.date, d.slug), reverse=True)
        projects.append(project)

    projects.sort(key=lambda p: (
        p.order,
        -(p.latest_date.toordinal() if p.latest_date else 0),
        p.title.lower(),
    ))
    return projects


def load_posts() -> list[Doc]:
    root = CONTENT / "posts"
    if not root.is_dir():
        return []
    posts = []
    for md_file in sorted(root.glob("*.md")):
        if md_file.name.startswith("_"):
            continue
        doc = load_doc(md_file, kind="post",
                       url_for_slug=lambda d, s: url(f"/posts/{s}/"))
        if doc and not doc.draft:
            posts.append(doc)
    posts.sort(key=lambda d: (d.date, d.slug), reverse=True)
    return posts


def load_noah() -> list[Doc]:
    """Noah is an AI agent who pushes his own Markdown into content/noah/.

    Entries are dated-URL'd (like project updates) so short notes that share a
    slug on different days never collide. Titled files render as full posts;
    untitled files render inline as feed notes.
    """
    root = CONTENT / "noah"
    if not root.is_dir():
        return []
    notes = []
    for md_file in sorted(root.glob("*.md")):
        if md_file.name.startswith("_"):
            continue
        doc = load_doc(
            md_file, kind="noah",
            url_for_slug=lambda d, s: url(f"/noah/{d.isoformat()}-{s}/"),
        )
        if doc and not doc.draft:
            notes.append(doc)
    notes.sort(key=lambda d: (d.date, d.slug), reverse=True)
    return notes


def load_pages() -> list[Page]:
    pages = []
    for md_file in sorted(CONTENT.glob("*.md")):
        if md_file.name.startswith("_"):
            continue
        meta, body = split_frontmatter(md_file)
        h1_title, body = pop_h1(body)
        slug = slugify(meta.get("slug") or md_file.stem)
        pages.append(Page(
            title=str(meta.get("title") or h1_title or slug.replace("-", " ").title()),
            slug=slug,
            url=url(f"/{slug}/"),
            body_html=render_markdown(body),
        ))
    return pages


def load_intro(path: Path) -> str:
    """Render an optional intro file (drops a leading H1), or return ''."""
    if not path.exists():
        return ""
    _, body = split_frontmatter(path)
    _, body = pop_h1(body)
    return render_markdown(body) if body.strip() else ""


# --------------------------------------------------------------------------
# output
# --------------------------------------------------------------------------

def build_pygments_css() -> str:
    """Syntax highlighting for light and dark, generated from Pygments."""
    def defs(candidates: list[str], selector: str) -> str:
        for name in candidates:
            try:
                return HtmlFormatter(style=name).get_style_defs(selector)
            except Exception:
                continue
        return ""

    light = defs(["friendly", "default"], ".codehilite")
    dark_media = defs(["github-dark", "monokai"],
                      ':root:not([data-theme="light"]) .codehilite')
    dark_forced = defs(["github-dark", "monokai"],
                       ':root[data-theme="dark"] .codehilite')

    return "\n".join([
        "/* generated by build.py -- do not edit, changes will be overwritten */",
        light,
        "@media (prefers-color-scheme: dark) {",
        dark_media,
        "}",
        dark_forced,
    ])


def make_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.globals.update(site=SITE, url=url, abs_url=abs_url)
    env.filters["datefmt"] = long_date
    env.filters["shortdate"] = lambda d: f"{d.strftime('%b')} {d.day}, {d.year}"
    env.filters["isodate"] = lambda d: d.isoformat()
    env.filters["slug"] = slugify
    env.filters["rfc822"] = lambda d: format_datetime(
        datetime.combine(d, time(12, 0), tzinfo=timezone.utc)
    )
    return env


def write(rel_path: str, content: str) -> None:
    out = OUTPUT / rel_path.lstrip("/")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(content, encoding="utf-8")


def render_to(env: Environment, template: str, rel_path: str, **ctx) -> None:
    write(rel_path, env.get_template(template).render(**ctx))


def build() -> None:
    print("building site...")

    projects = load_projects()
    posts = load_posts()
    noah = load_noah()
    pages = load_pages()
    intro_html = load_intro(CONTENT / "_home.md")
    noah_intro_html = load_intro(CONTENT / "noah" / "_about.md")

    all_updates = [u for p in projects for u in p.updates]
    all_docs = sorted(all_updates + posts + noah,
                      key=lambda d: (d.date, d.slug), reverse=True)

    tags: dict[str, list[Doc]] = {}
    for doc in all_docs:
        for tag in doc.tags:
            tags.setdefault(tag, []).append(doc)
    sorted_tags = sorted(tags.items(), key=lambda kv: (-len(kv[1]), kv[0].lower()))

    # clean output directory
    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    OUTPUT.mkdir(parents=True)

    env = make_env()

    # static assets
    if STATIC.is_dir():
        shutil.copytree(STATIC, OUTPUT / "static", dirs_exist_ok=True)
    write("static/pygments.css", build_pygments_css())

    # tell GitHub Pages not to run Jekyll over our output
    write(".nojekyll", "")
    if SITE.get("cname"):
        write("CNAME", SITE["cname"] + "\n")

    # homepage
    render_to(env, "home.html", "index.html",
              active="home",
              intro_html=intro_html,
              projects=projects,
              recent_posts=posts[:SITE["home_recent_posts"]],
              recent_updates=all_updates[:SITE["home_recent_updates"]],
              recent_noah=noah[:SITE["home_recent_noah"]])

    # projects index + one page per project + one page per update
    render_to(env, "projects.html", "projects/index.html",
              active="projects", projects=projects)

    for project in projects:
        render_to(env, "project.html", f"projects/{project.slug}/index.html",
                  active="projects", project=project)

        for i, doc in enumerate(project.updates):
            newer = project.updates[i - 1] if i > 0 else None
            older = project.updates[i + 1] if i + 1 < len(project.updates) else None
            render_to(env, "entry.html",
                      f"projects/{project.slug}/{doc.date.isoformat()}-{doc.slug}/index.html",
                      active="projects", doc=doc, project=project,
                      newer=newer, older=older)

    # standalone posts
    render_to(env, "posts.html", "posts/index.html", active="posts", posts=posts)
    for i, doc in enumerate(posts):
        newer = posts[i - 1] if i > 0 else None
        older = posts[i + 1] if i + 1 < len(posts) else None
        render_to(env, "entry.html", f"posts/{doc.slug}/index.html",
                  active="posts", doc=doc, project=None, newer=newer, older=older)

    # noah's section: feed-style index + one page per note
    render_to(env, "noah.html", "noah/index.html",
              active="noah", notes=noah, intro_html=noah_intro_html)
    for i, doc in enumerate(noah):
        newer = noah[i - 1] if i > 0 else None
        older = noah[i + 1] if i + 1 < len(noah) else None
        render_to(env, "entry.html",
                  f"noah/{doc.date.isoformat()}-{doc.slug}/index.html",
                  active="noah", doc=doc, project=None, newer=newer, older=older)

    # standalone pages (about.md, etc.)
    for page in pages:
        render_to(env, "page.html", f"{page.slug}/index.html",
                  active=page.slug, page=page)

    # tags
    render_to(env, "tags.html", "tags/index.html", active="", tags=sorted_tags)
    for tag, docs in sorted_tags:
        render_to(env, "tag.html", f"tags/{slugify(tag)}/index.html",
                  active="", tag=tag, docs=docs)

    # feed
    render_to(env, "feed.xml", "feed.xml",
              docs=all_docs[:SITE["feed_limit"]],
              build_date=all_docs[0].date if all_docs else date.today())

    # 404
    render_to(env, "404.html", "404.html", active="")

    print(f"  {len(projects)} projects, {len(all_updates)} updates, "
          f"{len(posts)} posts, {len(noah)} noah, {len(pages)} pages, "
          f"{len(sorted_tags)} tags")
    print(f"  -> {OUTPUT}")


if __name__ == "__main__":
    build()
