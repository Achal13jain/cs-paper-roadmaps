#!/usr/bin/env python3
"""Audit generated pages for discoverability and broken internal navigation."""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


ROOT = Path(__file__).resolve().parents[1]

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


class PageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.canonicals: list[str] = []
        self.descriptions: list[str] = []
        self.hrefs: list[str] = []
        self.h1_count = 0
        self.title_count = 0
        self._in_title = False
        self._json_ld = False
        self._json_chunks: list[str] = []
        self.json_documents: list[object] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        values = dict(attrs)
        if tag == "title":
            self.title_count += 1
            self._in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "a" and values.get("href"):
            self.hrefs.append(values["href"])
        elif tag == "link" and values.get("rel") == "canonical":
            self.canonicals.append(values.get("href", ""))
        elif tag == "meta" and values.get("name") == "description":
            self.descriptions.append(values.get("content", ""))
        elif tag == "script" and values.get("type") == "application/ld+json":
            self._json_ld = True
            self._json_chunks = []

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "script" and self._json_ld:
            self._json_ld = False
            raw = "".join(self._json_chunks).strip()
            if raw:
                self.json_documents.append(json.loads(raw))

    def handle_data(self, data: str) -> None:
        if self._json_ld:
            self._json_chunks.append(data)


def local_target(page: Path, href: str) -> Path | None:
    parsed = urlsplit(href)
    if parsed.scheme or parsed.netloc or href.startswith(("#", "mailto:", "javascript:")):
        return None
    relative = unquote(parsed.path)
    if not relative:
        return None
    target = ROOT / relative.lstrip("/") if relative.startswith("/") else page.parent / relative
    target = target.resolve()
    if ROOT not in target.parents and target != ROOT:
        return Path("__outside_site_root__")
    if relative.endswith("/") or target.is_dir():
        target /= "index.html"
    return target


def main() -> int:
    errors: list[str] = []
    data = yaml.safe_load((ROOT / "papers.yml").read_text(encoding="utf-8"))
    expected_roadmaps = {roadmap["id"] for roadmap in data["roadmaps"]}
    roadmap_pages = {path.parent.name for path in (ROOT / "roadmaps").glob("*/index.html")}
    if roadmap_pages != expected_roadmaps:
        errors.append(
            f"Roadmap pages differ from papers.yml: missing={sorted(expected_roadmaps-roadmap_pages)}, "
            f"extra={sorted(roadmap_pages-expected_roadmaps)}"
        )

    pages = [ROOT / "index.html", *(ROOT / "roadmaps").glob("*/index.html")]
    canonical_urls: set[str] = set()
    home_canonical = ""
    for page in pages:
        text = page.read_text(encoding="utf-8")
        parser = PageParser()
        try:
            parser.feed(text)
        except json.JSONDecodeError as exc:
            errors.append(f"{page.relative_to(ROOT)}: invalid JSON-LD ({exc})")
            continue

        label = str(page.relative_to(ROOT))
        if parser.title_count != 1:
            errors.append(f"{label}: expected one title, found {parser.title_count}")
        if parser.h1_count != 1:
            errors.append(f"{label}: expected one h1, found {parser.h1_count}")
        if len(parser.descriptions) != 1 or not parser.descriptions[0].strip():
            errors.append(f"{label}: expected one non-empty meta description")
        if len(parser.canonicals) != 1:
            errors.append(f"{label}: expected one canonical URL")
        else:
            canonical_urls.add(parser.canonicals[0])
            if page == ROOT / "index.html":
                home_canonical = parser.canonicals[0]

        for href in parser.hrefs:
            target = local_target(page, href)
            if target is not None and not target.exists():
                errors.append(f"{label}: broken internal link {href}")

        if page.parent.parent.name == "roadmaps":
            required = ["progress-bar", "paper-done", "aria-live=\"polite\"", "BreadcrumbList"]
            for marker in required:
                if marker not in text:
                    errors.append(f"{label}: missing generated feature {marker}")
            if not parser.json_documents:
                errors.append(f"{label}: missing JSON-LD")

    sitemap_text = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
    sitemap_urls = {
        part.split("</loc>", 1)[0]
        for part in sitemap_text.split("<loc>")[1:]
    }
    if sitemap_urls != canonical_urls:
        errors.append("sitemap URLs do not match page canonical URLs")

    robots_text = (ROOT / "robots.txt").read_text(encoding="utf-8")
    expected_sitemap = f"{home_canonical.rstrip('/')}/sitemap.xml"
    if not home_canonical or expected_sitemap not in robots_text:
        errors.append("robots.txt does not reference the generated sitemap")

    if errors:
        for error in errors:
            print(f"❌ {error}")
        return 1

    print(f"✅ Site audit passed — {len(pages)} pages, {len(canonical_urls)} canonical URLs, no broken internal links.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
