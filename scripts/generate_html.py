#!/usr/bin/env python3
"""Regenerate index.html's embedded roadmap data from papers.yml."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PAPERS_FILE = ROOT / "papers.yml"
INDEX_FILE = ROOT / "index.html"
START_MARKER = "<!-- PAPERS_DATA_START -->"
END_MARKER = "<!-- PAPERS_DATA_END -->"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def load_data() -> tuple[list[dict], int, int]:
    with PAPERS_FILE.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    roadmaps = data.get("roadmaps", [])
    paper_count = sum(len(roadmap.get("papers", [])) for roadmap in roadmaps)
    return roadmaps, len(roadmaps), paper_count


def replace_data_block(html: str, json_data: str) -> str:
    block = "\n".join(
        [
            START_MARKER,
            "<script>",
            f"const ROADMAP_DATA = {json_data};",
            "</script>",
            END_MARKER,
        ]
    )

    marker_pattern = re.compile(
        rf"{re.escape(START_MARKER)}[\s\S]*?{re.escape(END_MARKER)}",
        re.MULTILINE,
    )
    if marker_pattern.search(html):
        return marker_pattern.sub(block, html, count=1)

    legacy_pattern = re.compile(
        r"<script id=\"data-script\">[\s\S]*?</script>",
        re.MULTILINE,
    )
    if legacy_pattern.search(html):
        return legacy_pattern.sub(block, html, count=1)

    raise RuntimeError(
        "Could not find PAPERS_DATA markers or the legacy <script id=\"data-script\"> block."
    )


def update_static_counts(html: str, roadmap_count: int, paper_count: int) -> str:
    replacements = [
        (
            r"content=\"\d+ curated, logically ordered reading lists covering \d+ foundational and frontier papers",
            f"content=\"{roadmap_count} curated, logically ordered reading lists covering {paper_count} foundational and frontier papers",
        ),
        (
            r"content=\"\d+ curated papers across \d+ fields of computer science",
            f"content=\"{paper_count} curated papers across {roadmap_count} fields of computer science",
        ),
        (
            r">\d+ fields · \d+ papers<",
            f">{roadmap_count} fields · {paper_count} papers<",
        ),
        (
            r'id="stat-papers">\d+<',
            f'id="stat-papers">{paper_count}<',
        ),
        (
            r'id="stat-roadmaps">\d+<',
            f'id="stat-roadmaps">{roadmap_count}<',
        ),
    ]
    for pattern, replacement in replacements:
        html = re.sub(pattern, replacement, html, count=1)
    return html


def main() -> int:
    roadmaps, roadmap_count, paper_count = load_data()
    json_data = json.dumps(roadmaps, ensure_ascii=False, separators=(",", ":"))

    html = INDEX_FILE.read_text(encoding="utf-8")
    html = replace_data_block(html, json_data)
    html = update_static_counts(html, roadmap_count, paper_count)
    INDEX_FILE.write_text(html, encoding="utf-8")

    print(f"✅ index.html regenerated — {roadmap_count} roadmaps, {paper_count} papers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
