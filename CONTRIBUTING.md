# Contributing

Thanks for helping improve CS Paper Roadmaps. Curation is the product here: every paper should sharpen the reading path, not just increase the count.

## The Golden Rule

Contributors edit only `papers.yml`.

Do not edit `index.html` in paper contribution PRs. The site is regenerated from `papers.yml` after merge, and GitHub Actions deploys the updated page automatically.

## How to Add a Paper

1. Fork the repo.
2. Open `papers.yml`.
3. Find the right roadmap by `id`.
4. Add the paper under the correct roadmap and level.
5. Optionally run `python scripts/validate_papers.py` locally.
6. Open a PR titled `[Add Paper] <Roadmap> — <Paper Title>`.

Use this schema for each paper:

```yaml
- id: 30
  level: 8
  title: "Paper Title"
  authors: "First Author et al."
  institution: "Institution"
  date: "Mon YYYY"
  link: "https://arxiv.org/abs/..."
  tldr: "Two or three sentences in your own words explaining what the paper does."
  why: "Why this paper belongs at this point in the roadmap."
  prerequisites: [4, 12]
  key_takeaway: "The one idea a reader should remember."
  minimum_viable_path: false
```

Notes:

- `id` is the next paper number within that roadmap.
- `level` must match one of the roadmap's declared `levels`.
- `prerequisites` should preferably reference IDs of earlier papers in the same roadmap. Use short strings only when the prerequisite is a concept rather than an existing paper.
- `minimum_viable_path` should be `true` only for the small critical reading path.

## How to Add a New Roadmap Topic

Open an issue first using the new roadmap topic template so we can discuss scope.

If accepted, add a new top-level entry under `roadmaps:` in `papers.yml`. A new roadmap must include:

- `id` in kebab-case
- `title`
- `description`
- `icon`
- `timeline`
- `levels`
- at least 5 seed papers

## Paper Quality Guidelines

- The paper must be peer-reviewed or have 100+ citations on Google Scholar.
- The link must be arXiv, OpenReview, an author's page, a conference archive, or another open-access source. Never link to a paywall.
- TL;DR text must be your own words, not the abstract.
- The paper should fill a real gap in the sequence.
- Prerequisites should point backward in the roadmap, not forward.
- Avoid hype words. Placement in the roadmap should communicate importance.

## What Happens After You Open a PR

1. Automated checks validate `papers.yml`.
2. Automated checks verify paper links are accessible.
3. A bot comments with a short contribution summary and labels the PR `needs-review`.
4. A maintainer manually reviews paper quality, ordering, and wording.
5. Once merged, `index.html` is regenerated and GitHub Pages deploys the site.

## Local Development

Install dependencies:

```bash
pip install pyyaml jsonschema requests jinja2
```

Validate the YAML:

```bash
python scripts/validate_papers.py
```

Preview the generated site locally:

```bash
python scripts/generate_html.py
open index.html   # or: python -m http.server 8080
```

If you run `generate_html.py` while preparing a paper PR, do not include the generated `index.html` diff unless you are maintaining the site pipeline itself.

## License of Contributions

By contributing, you agree that:

- Your prose contributions are licensed under [CC BY 4.0](./LICENSE-CONTENT).
- Your code contributions are licensed under [MIT](./LICENSE-CODE).
- You have the right to license what you contribute.
