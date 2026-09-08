# Production deployment

The site is fully static. GitHub Pages is the default production target; Cloudflare Pages is recommended when using a custom domain.

## Generate locally

```bash
python -m pip install pyyaml
python scripts/validate_papers.py
python scripts/generate_html.py
```

Generated files are `index.html`, `roadmaps/*/index.html`, `sitemap.xml`, and `robots.txt`.

## Configuration

The generator accepts these environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `SITE_URL` | `https://achal13jain.github.io/cs-paper-roadmaps` | Canonical, Open Graph, sitemap, and robots URLs |
| `REPO_URL` | `https://github.com/Achal13jain/cs-paper-roadmaps` | GitHub and contribution links |
| `GA_MEASUREMENT_ID` | Current GA4 property | Analytics; set to `disabled` to disable |

PowerShell example:

```powershell
$env:SITE_URL = "https://example.org"
python scripts/generate_html.py
```

## Cloudflare Pages

Connect the GitHub repository in Workers & Pages and use:

- Framework preset: None
- Build command: `pip install pyyaml && python scripts/validate_papers.py && python scripts/generate_html.py`
- Build output directory: `.`
- Production branch: `main`
- Environment variable: `SITE_URL=https://your-domain.example`

Add the custom domain in Cloudflare before requesting indexing. Regenerate committed artifacts with the same production `SITE_URL`, or allow the Cloudflare build to generate them for the deployment artifact.

## Search launch checklist

1. Verify the custom-domain property in Google Search Console.
2. Submit `/sitemap.xml`.
3. Inspect and request indexing for the homepage and the strongest roadmap pages.
4. Confirm that canonical URLs resolve to the production domain.
5. Confirm analytics on direct visits to a standalone roadmap page.
6. Preserve redirects from any previous public URL.
