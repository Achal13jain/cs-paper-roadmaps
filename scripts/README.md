# Scripts

| Script | Purpose | Run with |
|--------|---------|----------|
| `validate_papers.py` | Validates papers.yml against the schema | `python scripts/validate_papers.py` |
| `check_links.py` | Checks all paper links are accessible | `python scripts/check_links.py` |
| `generate_html.py` | Regenerates the homepage, standalone roadmap pages, sitemap, and robots file | `python scripts/generate_html.py` |
| `audit_site.py` | Checks generated metadata, JSON-LD, sitemap coverage, and internal links | `python scripts/audit_site.py` |

## Local setup

```bash
pip install pyyaml jsonschema requests
```

Run all checks before opening a PR:

```bash
python scripts/validate_papers.py && python scripts/check_links.py
```

For PR-style link checks against only new or changed links:

```bash
git fetch origin main
python scripts/check_links.py --changed-only --base-ref origin/main
```
