#!/usr/bin/env python3
"""
serve.py -- build the site and preview it locally.

    python serve.py            build, serve on http://localhost:8000, open browser
    python serve.py 3000       use a different port
    python serve.py --no-open  don't open a browser

Press Ctrl+C to stop. Re-run to pick up content changes (or just hit
`python build.py` in another terminal and refresh).
"""

from __future__ import annotations

import functools
import http.server
import socketserver
import sys
import threading
import webbrowser

from build import OUTPUT, SITE, build

DEFAULT_PORT = 8000


class Handler(http.server.SimpleHTTPRequestHandler):
    """Serves site/ and maps the configured base_url onto it."""

    base_url = SITE["base_url"].rstrip("/")

    def translate_path(self, path: str) -> str:
        if self.base_url and path.startswith(self.base_url):
            path = path[len(self.base_url):] or "/"
        return super().translate_path(path)

    def log_message(self, fmt, *args):  # quieter output
        if "404" in (fmt % args):
            sys.stderr.write("  404  %s\n" % (args[0] if args else ""))


def main() -> None:
    port = DEFAULT_PORT
    open_browser = "--no-open" not in sys.argv
    for arg in sys.argv[1:]:
        if arg.isdigit():
            port = int(arg)

    build()

    handler = functools.partial(Handler, directory=str(OUTPUT))
    socketserver.TCPServer.allow_reuse_address = True

    home = f"http://localhost:{port}{SITE['base_url'].rstrip('/')}/"
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"\nserving at {home}")
        print("Ctrl+C to stop\n")
        if open_browser:
            threading.Timer(0.5, webbrowser.open, args=[home]).start()
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nstopped")


if __name__ == "__main__":
    main()
