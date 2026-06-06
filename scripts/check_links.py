#!/usr/bin/env python3
"""Check paper links in papers.yml."""

from __future__ import annotations

import argparse
import subprocess
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


LinkEntry = tuple[str, str, str, str, str]


def load_papers_file() -> dict:
    with PAPERS_FILE.open("r", encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def load_base_papers(base_ref: str) -> dict | None:
    result = subprocess.run(
        ["git", "show", f"{base_ref}:papers.yml"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return None
    return yaml.safe_load(result.stdout)


def flatten_links(data: dict) -> dict[tuple[str, int], LinkEntry]:
    links: dict[tuple[str, int], LinkEntry] = {}
    for roadmap in data.get("roadmaps", []):
        roadmap_id = roadmap.get("id", "")
        roadmap_title = roadmap.get("title", roadmap.get("id", "Unknown roadmap"))
        for paper in roadmap.get("papers", []):
            paper_id = paper.get("id")
            if not isinstance(paper_id, int):
                continue
            links[(roadmap_id, paper_id)] = (
                roadmap_id,
                str(paper_id),
                roadmap_title,
                paper.get("title", "Untitled paper"),
                paper.get("link", ""),
            )
    return links


def iter_links(skip_arxiv: bool) -> Iterable[LinkEntry]:
    links = flatten_links(load_papers_file()).values()
    for entry in links:
        url = entry[4]
        if skip_arxiv and url.startswith("https://arxiv.org"):
            continue
        yield entry


def iter_changed_links(base_ref: str, skip_arxiv: bool) -> Iterable[LinkEntry]:
    current_links = flatten_links(load_papers_file())
    base_data = load_base_papers(base_ref)
    if base_data is None:
        print(f"ℹ️ No baseline papers.yml found at {base_ref}; skipping changed-only link check.")
        return []

    base_links = flatten_links(base_data)
    changed = []
    for key, entry in current_links.items():
        url = entry[4]
        base_entry = base_links.get(key)
        base_url = base_entry[4] if base_entry else None
        if url != base_url:
            if skip_arxiv and url.startswith("https://arxiv.org"):
                continue
            changed.append(entry)
    return changed


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
    parser.add_argument("--changed-only", action="store_true", help="Check only links added or changed versus base")
    parser.add_argument("--base-ref", default="origin/main", help="Git ref to compare against for --changed-only")
    args = parser.parse_args()

    if args.changed_only:
        links = list(iter_changed_links(args.base_ref, args.skip_arxiv))
    else:
        links = list(iter_links(args.skip_arxiv))

    if args.changed_only and not links:
        print("✅ No new or changed links to check.")
        return 0

    ok_count = 0

    for _roadmap_id, _paper_id, roadmap_title, paper_title, url in links:
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
