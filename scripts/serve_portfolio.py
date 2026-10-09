"""Serve the portfolio folder locally for previewing.

Usage:
    python scripts/serve_portfolio.py            # http://127.0.0.1:4173
    python scripts/serve_portfolio.py --port 8080 --open

The server binds to 127.0.0.1 only, so the preview is not reachable from
other machines on the network.
"""

from __future__ import annotations

import argparse
import functools
import http.server
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT / "portfolio"


class PortfolioHandler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript",
        ".mjs": "text/javascript",
        ".webmanifest": "application/manifest+json",
        ".svg": "image/svg+xml",
    }

    def end_headers(self) -> None:
        # Always serve the latest edit while iterating on a render.
        self.send_header("Cache-Control", "no-store")
        super().end_headers()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--port", type=int, default=4173)
    parser.add_argument("--open", action="store_true", help="open the page in the default browser")
    args = parser.parse_args()

    handler = functools.partial(PortfolioHandler, directory=str(PORTFOLIO))
    with http.server.ThreadingHTTPServer(("127.0.0.1", args.port), handler) as server:
        url = f"http://127.0.0.1:{args.port}/"
        print(f"Serving {PORTFOLIO} at {url}  (Ctrl+C to stop)")
        print(f"Observatory: {url}demos/celestial-observatory-cinematic.html")
        if args.open:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nStopped.")


if __name__ == "__main__":
    main()
