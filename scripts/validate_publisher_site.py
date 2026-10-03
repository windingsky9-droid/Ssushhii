from pathlib import Path
from html.parser import HTMLParser
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[1] / "publisher-site"

class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.title = False
        self.description = False
        self.canonical = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "title":
            self.title = True
        if tag == "meta" and attrs.get("name") == "description" and attrs.get("content"):
            self.description = True
        if tag == "link" and attrs.get("rel") == "canonical" and attrs.get("href", "").startswith("https://"):
            self.canonical = True

results = {
    "html_files": 0,
    "broken_links": [],
    "missing_title": [],
    "missing_description": [],
    "missing_canonical": [],
    "secret_flags": [],
    "asset_errors": [],
}

for page in ROOT.rglob("*.html"):
    results["html_files"] += 1
    text = page.read_text(encoding="utf-8", errors="ignore")
    parser = PageParser()
    parser.feed(text)
    rel = str(page.relative_to(ROOT))

    if not parser.title:
        results["missing_title"].append(rel)
    if not parser.description:
        results["missing_description"].append(rel)
    if not parser.canonical:
        results["missing_canonical"].append(rel)

    for href in parser.links:
        if href.startswith(("http:", "https:", "mailto:", "#")):
            continue
        target = (page.parent / href.split("#")[0]).resolve()
        if href and not target.exists():
            results["broken_links"].append({"from": rel, "href": href})

    for pattern in (
        r"sk-[A-Za-z0-9_-]{20,}",
        r"AKIA[0-9A-Z]{16}",
        r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----",
    ):
        if re.search(pattern, text):
            results["secret_flags"].append(rel)

try:
    json.loads((ROOT / "site.webmanifest").read_text(encoding="utf-8"))
except Exception:
    results["asset_errors"].append("invalid site.webmanifest")

favicon = ROOT / "favicon.svg"
if not favicon.exists() or favicon.stat().st_size < 100:
    results["asset_errors"].append("favicon.svg missing or suspiciously small")

if not (ROOT / ".well-known" / "security.txt").exists():
    results["asset_errors"].append(".well-known/security.txt missing")

sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
if sitemap.count("<loc>https://") < results["html_files"]:
    results["asset_errors"].append("sitemap is missing absolute page URLs")

robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
if "https://sushir-systems-lab.netlify.app/sitemap.xml" not in robots:
    results["asset_errors"].append("robots.txt does not reference the absolute sitemap URL")

headers = (ROOT / "_headers").read_text(encoding="utf-8")
for required in (
    "Content-Security-Policy:",
    "X-Frame-Options: DENY",
    "X-Content-Type-Options: nosniff",
    "Referrer-Policy:",
    "Permissions-Policy:",
    "Cross-Origin-Opener-Policy:",
):
    if required not in headers:
        results["asset_errors"].append(f"missing security header rule: {required}")

if (ROOT / "preview.png").exists():
    results["asset_errors"].append("preview.png should not be deployed")

print(json.dumps(results, indent=2))

failed = any(results[key] for key in (
    "broken_links",
    "missing_title",
    "missing_description",
    "missing_canonical",
    "secret_flags",
    "asset_errors",
))

sys.exit(1 if failed else 0)
