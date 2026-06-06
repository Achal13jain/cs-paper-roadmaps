# Scripts

| Script | Purpose | Run with |
|--------|---------|----------|
| `validate_papers.py` | Validates papers.yml against the schema | `python scripts/validate_papers.py` |
| `check_links.py` | Checks all paper links are accessible | `python scripts/check_links.py` |
| `generate_html.py` | Regenerates index.html from papers.yml | `python scripts/generate_html.py` |

## Local setup

```bash
pip install pyyaml jsonschema requests jinja2
```

Run all checks before opening a PR:

```bash
python scripts/validate_papers.py && python scripts/check_links.py
```
