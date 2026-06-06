#!/usr/bin/env python3
"""Check every paper link in papers.yml."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

import requests
import yaml


ROOT = Path(__file__).resolve().parents[1]
PAPERS_FILE = ROOT / "papers.yml"
TIMEOUT_SECONDS = 10
MAX_RETRIES = 2
HEADERS = {"User-Agent": "Mozilla/5.0"}

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def iter_links(skip_arxiv: bool) -> Iterable[tuple[str, str, str]]:
    with PAPERS_FILE.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)

    for roadmap in data.get("roadmaps", []):
        roadmap_title = roadmap.get("title", roadmap.get("id", "Unknown roadmap"))
        for paper in roadmap.get("papers", []):
            url = paper.get("link", "")
            if skip_arxiv and url.startswith("https://arxiv.org"):
                continue
            yield roadmap_title, paper.get("title", "Untitled paper"), url


def check_url(url: str) -> tuple[bool, str]:
    if not url:
        return False, "missing URL"

    attempts = MAX_RETRIES + 1
    last_error = ""
    for attempt in range(1, attempts + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=TIMEOUT_SECONDS, allow_redirects=True)
            response.close()
            if 200 <= response.status_code < 300:
                return True, f"HTTP {response.status_code}"
            return False, f"HTTP {response.status_code}"
        except (requests.Timeout, requests.ConnectionError) as exc:
            last_error = exc.__class__.__name__
            if attempt == attempts:
                return False, last_error
    return False, last_error or "unknown error"


def main() -> int:
    parser = argparse.ArgumentParser(description="Check paper links in papers.yml")
    parser.add_argument("--skip-arxiv", action="store_true", help="Skip https://arxiv.org links")
    args = parser.parse_args()

    links = list(iter_links(args.skip_arxiv))
    ok_count = 0

    for roadmap_title, paper_title, url in links:
        ok, detail = check_url(url)
        if ok:
            ok_count += 1
            print(f"✅ OK   {url} — {roadmap_title}: {paper_title}")
        else:
            print(f"❌ DEAD {url} — {roadmap_title}: {paper_title} ({detail})")

    total = len(links)
    print(f"{ok_count}/{total} links OK.")
    return 0 if ok_count == total else 1


if __name__ == "__main__":
    sys.exit(main())
