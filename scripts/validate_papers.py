#!/usr/bin/env python3
"""Validate papers.yml against the project schema."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator


ROOT = Path(__file__).resolve().parents[1]
PAPERS_FILE = ROOT / "papers.yml"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

SCHEMA = {
    "type": "object",
    "required": ["roadmaps"],
    "additionalProperties": False,
    "properties": {
        "roadmaps": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["id", "title", "papers"],
                "additionalProperties": False,
                "properties": {
                    "id": {"type": "string", "minLength": 1, "pattern": r"^[a-z0-9]+(?:-[a-z0-9]+)*$"},
                    "title": {"type": "string", "minLength": 1},
                    "description": {"type": "string"},
                    "icon": {"type": "string"},
                    "timeline": {"type": "string"},
                    "levels": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["n", "name"],
                            "additionalProperties": False,
                            "properties": {
                                "n": {"type": "integer", "minimum": 0, "maximum": 8},
                                "name": {"type": "string", "minLength": 1},
                                "tagline": {"type": "string"},
                            },
                        },
                    },
                    "papers": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": [
                                "id",
                                "level",
                                "title",
                                "authors",
                                "date",
                                "link",
                                "tldr",
                                "why",
                                "key_takeaway",
                            ],
                            "additionalProperties": False,
                            "properties": {
                                "id": {"type": "integer", "minimum": 1},
                                "level": {"type": "integer", "minimum": 0, "maximum": 8},
                                "title": {"type": "string", "minLength": 1},
                                "authors": {"type": "string", "minLength": 1},
                                "institution": {"type": "string"},
                                "date": {"type": "string", "minLength": 1},
                                "link": {"type": "string", "pattern": r"^http"},
                                "tldr": {"type": "string", "minLength": 20},
                                "why": {"type": "string"},
                                "prerequisites": {
                                    "type": "array",
                                    "items": {"type": ["integer", "string"]},
                                },
                                "key_takeaway": {"type": "string"},
                                "minimum_viable_path": {"type": "boolean"},
                            },
                        },
                    },
                },
            },
        }
    },
}


def load_yaml() -> dict:
    if not PAPERS_FILE.exists():
        raise FileNotFoundError(f"{PAPERS_FILE.name} not found")
    with PAPERS_FILE.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    if data is None:
        raise ValueError(f"{PAPERS_FILE.name} is empty")
    return data


def format_path(error_path) -> str:
    parts = []
    for item in error_path:
        if isinstance(item, int):
            parts.append(f"[{item}]")
        else:
            parts.append((".\\" if not parts else ".") + str(item))
    return "".join(parts) or "."


def validate_custom_rules(data: dict) -> list[str]:
    errors: list[str] = []
    roadmap_ids: set[str] = set()

    for roadmap in data.get("roadmaps", []):
        roadmap_id = roadmap.get("id", "<missing>")
        if roadmap_id in roadmap_ids:
            errors.append(f"Duplicate roadmap id: {roadmap_id}")
        roadmap_ids.add(roadmap_id)

        level_numbers = {level.get("n") for level in roadmap.get("levels", []) if "n" in level}
        paper_ids: set[int] = set()
        for paper in roadmap.get("papers", []):
            paper_id = paper.get("id")
            if paper_id in paper_ids:
                errors.append(f"{roadmap_id}: duplicate paper id {paper_id}")
            paper_ids.add(paper_id)

            if level_numbers and paper.get("level") not in level_numbers:
                errors.append(
                    f"{roadmap_id} paper {paper_id}: level {paper.get('level')} is not declared in roadmap levels"
                )

    return errors


def main() -> int:
    try:
        data = load_yaml()
    except Exception as exc:
        print(f"❌ Failed to load papers.yml: {exc}")
        return 1

    validator = Draft202012Validator(SCHEMA)
    schema_errors = sorted(validator.iter_errors(data), key=lambda error: list(error.path))
    if schema_errors:
        for error in schema_errors:
            print(f"❌ Validation error at {format_path(error.path)}: {error.message}")
        return 1

    custom_errors = validate_custom_rules(data)
    if custom_errors:
        for error in custom_errors:
            print(f"❌ Validation error: {error}")
        return 1

    roadmap_count = len(data["roadmaps"])
    paper_count = sum(len(roadmap["papers"]) for roadmap in data["roadmaps"])
    print(f"✅ papers.yml validated — {roadmap_count} roadmaps, {paper_count} papers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
