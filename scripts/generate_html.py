#!/usr/bin/env python3
"""Generate the site from papers.yml.

Outputs:
  index.html            — data block + counts refreshed in place (unchanged behaviour)
  roadmaps/<id>/index.html — one static, SEO-indexable page per roadmap
  sitemap.xml, robots.txt
"""
from __future__ import annotations

import html
import json
import os
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
PAPERS_FILE = ROOT / "papers.yml"
INDEX_FILE = ROOT / "index.html"
SITE_URL = os.getenv(
    "SITE_URL", "https://achal13jain.github.io/cs-paper-roadmaps"
).rstrip("/")
REPO_URL = os.getenv(
    "REPO_URL", "https://github.com/Achal13jain/cs-paper-roadmaps"
).rstrip("/")
GA_MEASUREMENT_ID = os.getenv("GA_MEASUREMENT_ID", "G-NQGL8PZC3Z").strip()
if GA_MEASUREMENT_ID.lower() in {"disabled", "false", "none", "off"}:
    GA_MEASUREMENT_ID = ""
BRAND_NAME = "Papers in Order"
START_MARKER = "<!-- PAPERS_DATA_START -->"
END_MARKER = "<!-- PAPERS_DATA_END -->"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

e = html.escape


# ----------------------------------------------------------------------------
# Data
# ----------------------------------------------------------------------------
def load_data():
    data = yaml.safe_load(PAPERS_FILE.read_text(encoding="utf-8"))
    roadmaps = data.get("roadmaps", [])
    paper_count = sum(len(r.get("papers", [])) for r in roadmaps)
    return roadmaps, len(roadmaps), paper_count


# ----------------------------------------------------------------------------
# index.html: swap embedded JSON + refresh counts (legacy behaviour, kept)
# ----------------------------------------------------------------------------
def replace_data_block(html_text: str, json_data: str) -> str:
    block = "\n".join(
        [START_MARKER, "<script>", f"const ROADMAP_DATA = {json_data};", "</script>", END_MARKER]
    )
    pat = re.compile(rf"{re.escape(START_MARKER)}[\s\S]*?{re.escape(END_MARKER)}", re.MULTILINE)
    if pat.search(html_text):
        return pat.sub(lambda _m: block, html_text, count=1)
    raise RuntimeError("Could not find PAPERS_DATA markers in index.html.")


def update_static_counts(html_text: str, roadmap_count: int, paper_count: int) -> str:
    replacements = [
        (
            r"content=\"The shortest path through computer science research: \d+ landmark papers across \d+ fields",
            f"content=\"The shortest path through computer science research: {paper_count} landmark papers across {roadmap_count} fields",
        ),
        (
            r"content=\"\d+ curated, logically ordered reading lists covering \d+ foundational and frontier papers",
            f"content=\"{roadmap_count} curated, logically ordered reading lists covering {paper_count} foundational and frontier papers",
        ),
        (
            r"content=\"\d+ curated papers across \d+ fields of computer science",
            f"content=\"{paper_count} curated papers across {roadmap_count} fields of computer science",
        ),
        (r">\d+ fields · \d+ papers<", f">{roadmap_count} fields · {paper_count} papers<"),
        (r'id="stat-papers">\d+<', f'id="stat-papers">{paper_count}<'),
        (r'id="stat-roadmaps">\d+<', f'id="stat-roadmaps">{roadmap_count}<'),
    ]
    for pattern, replacement in replacements:
        html_text = re.sub(pattern, replacement, html_text, count=1)
    return html_text


def update_static_urls(html_text: str) -> str:
    """Keep homepage discovery URLs aligned with the selected production host."""
    replacements = [
        (r'(<link rel="canonical" href=")[^"]+', rf'\g<1>{SITE_URL}/'),
        (r'(<meta property="og:url" content=")[^"]+', rf'\g<1>{SITE_URL}/'),
        (r'(<meta property="og:image" content=")[^"]+', rf'\g<1>{SITE_URL}/s.png'),
    ]
    for pattern, replacement in replacements:
        html_text = re.sub(pattern, replacement, html_text, count=1)
    return html_text


# ----------------------------------------------------------------------------
# Per-roadmap pages
# ----------------------------------------------------------------------------
PAGE_CSS = """
:root{
  --primary:#006b2c; --primary-soft:#e2f4e5; --primary-dim:#62df7d;
  --bg:#f7f9fb; --surface:#ffffff; --surface-low:#f2f4f6; --surface-high:#e6e8ea;
  --ink:#191c1e; --ink-soft:#3e4a3d; --line:#bdcaba; --line-soft:#dde5db;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
  font:400 16px/1.6 Inter,system-ui,sans-serif;-webkit-font-smoothing:antialiased}
a{color:var(--primary)}
.wrap{max-width:880px;margin:0 auto;padding:0 20px}
.site-head{border-bottom:1px solid var(--line-soft);background:var(--surface)}
.site-head .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;padding:14px 20px}
.brand{font:600 17px/1 Newsreader,Georgia,serif;color:var(--ink);text-decoration:none}
.brand span{color:var(--primary)}
.head-links{display:flex;gap:18px;font-size:14px}
.head-links a{text-decoration:none;color:var(--ink-soft)}
.head-links a:hover{color:var(--primary)}
.crumbs{font-size:13px;color:var(--ink-soft);margin:22px 0 6px}
.crumbs a{color:var(--ink-soft);text-decoration:none}
.crumbs a:hover{color:var(--primary)}
h1{font:600 clamp(30px,5vw,40px)/1.2 Newsreader,Georgia,serif;letter-spacing:-.02em;margin:4px 0 10px}
.lede{color:var(--ink-soft);max-width:64ch;margin:0 0 14px}
.meta-row{display:flex;flex-wrap:wrap;gap:8px 20px;font-size:14px;color:var(--ink-soft);
  padding:12px 0 18px;border-bottom:1px solid var(--line-soft)}
.meta-row b{color:var(--ink);font-weight:600}
.section-title{font:600 24px/1.3 Newsreader,Georgia,serif;margin:36px 0 8px}
.mvrp-box{background:var(--surface);border:1px solid var(--line-soft);border-radius:10px;padding:16px 18px;margin-top:10px}
.mvrp-box ol{margin:8px 0 2px;padding-left:22px}
.mvrp-box li{margin:5px 0}
.mvrp-box a{text-decoration:none}
.mvrp-box a:hover{text-decoration:underline}
.progress-box{display:grid;grid-template-columns:1fr auto;gap:10px 16px;align-items:center;
  background:var(--surface);border:1px solid var(--line-soft);border-radius:10px;padding:16px 18px;margin:18px 0 0}
.progress-copy{font-size:14px;color:var(--ink-soft)}
.progress-copy strong{color:var(--ink)}
.progress-box progress{grid-column:1/-1;width:100%;height:9px;accent-color:var(--primary)}
.reset-progress{border:0;background:none;color:var(--primary);font:500 13px Inter,sans-serif;cursor:pointer;padding:4px}
.reset-progress:hover{text-decoration:underline}
.toolbar{position:sticky;top:0;z-index:5;background:var(--bg);padding:12px 0;margin-top:26px;
  border-bottom:1px solid var(--line-soft)}
.toolbar input{width:100%;padding:10px 14px;font:inherit;font-size:15px;color:var(--ink);
  background:var(--surface);border:1px solid var(--line);border-radius:8px}
.toolbar input:focus{outline:2px solid var(--primary);outline-offset:1px}
.level-head{display:flex;align-items:baseline;gap:12px;margin:34px 0 4px}
.level-badge{background:var(--primary);color:#fff;font:600 12px/1 Inter,sans-serif;
  padding:6px 10px;border-radius:999px;white-space:nowrap}
.level-name{font:600 20px/1.3 Newsreader,Georgia,serif}
.level-tag{font-size:13px;color:var(--ink-soft)}
.paper{background:var(--surface);border:1px solid var(--line-soft);border-radius:10px;margin:12px 0}
.paper[data-mvrp="1"]{border-left:3px solid var(--primary)}
.paper summary{display:flex;gap:12px;align-items:baseline;padding:14px 16px;cursor:pointer;list-style:none}
.paper summary::-webkit-details-marker{display:none}
.paper summary:hover{background:var(--surface-low);border-radius:10px}
.p-num{font:500 13px/1.6 ui-monospace,SFMono-Regular,monospace;color:var(--ink-soft);min-width:2.2em}
.p-title{font:500 18px/1.45 Newsreader,Georgia,serif;flex:1}
.p-flag{font-size:11px;font-weight:600;color:var(--primary);background:var(--primary-soft);
  padding:3px 8px;border-radius:6px;white-space:nowrap;align-self:center}
.p-body{padding:0 16px 16px 16px;border-top:1px solid var(--line-soft)}
.p-byline{font-size:13.5px;color:var(--ink-soft);margin:12px 0 10px}
.p-field{margin:10px 0}
.p-field b{display:block;font-size:12.5px;font-weight:600;color:var(--primary);margin-bottom:2px}
.p-field p{margin:0;font-size:15px}
.p-link{display:inline-block;margin-top:12px;font-size:14.5px;font-weight:500;
  color:var(--primary);text-decoration:none;border-bottom:1px solid var(--primary-dim)}
.p-link:hover{border-bottom-color:var(--primary)}
.paper-actions{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-top:12px}
.read-check{display:inline-flex;align-items:center;gap:7px;font-size:14px;color:var(--ink-soft);cursor:pointer}
.read-check input{width:17px;height:17px;accent-color:var(--primary)}
.paper.is-read{opacity:.72}
.paper.is-read .p-title{text-decoration:line-through;text-decoration-thickness:1px}
.pager{display:flex;justify-content:space-between;gap:16px;margin:48px 0 24px;font-size:15px}
.pager a{text-decoration:none;background:var(--surface);border:1px solid var(--line-soft);
  border-radius:8px;padding:12px 16px;color:var(--ink);max-width:48%}
.pager a:hover{border-color:var(--primary)}
.pager .dir{display:block;font-size:12.5px;color:var(--ink-soft);margin-bottom:2px}
.site-foot{border-top:1px solid var(--line-soft);margin-top:20px;padding:22px 0 34px;
  font-size:13.5px;color:var(--ink-soft)}
.site-foot a{color:var(--ink-soft)}
.hidden{display:none}
mark{background:var(--primary-soft);color:inherit}
@media (max-width:560px){
  .paper summary{flex-wrap:wrap}
  .pager{flex-direction:column}
  .pager a{max-width:100%}
}
"""

FILTER_JS = """
const q=document.getElementById('paper-filter');
const cards=[...document.querySelectorAll('.paper')];
const levels=[...document.querySelectorAll('.level-block')];
const counter=document.getElementById('filter-count');
const roadmapId=document.body.dataset.roadmap;
const storageKey=`papers-in-order:${roadmapId}:read`;
const checks=[...document.querySelectorAll('.paper-done')];
const progressCount=document.getElementById('progress-count');
const progressBar=document.getElementById('progress-bar');

function track(name,params={}){
  if(typeof window.gtag==='function') window.gtag('event',name,{roadmap_id:roadmapId,...params});
}
function loadRead(){
  try{return new Set(JSON.parse(localStorage.getItem(storageKey)||'[]'));}
  catch(_err){return new Set();}
}
let read=loadRead();
function saveRead(){
  try{localStorage.setItem(storageKey,JSON.stringify([...read]));}
  catch(_err){/* Progress still works for this tab when storage is unavailable. */}
}
function renderProgress(){
  checks.forEach(c=>{
    const done=read.has(c.dataset.paperId);
    c.checked=done;
    c.closest('.paper').classList.toggle('is-read',done);
  });
  progressCount.textContent=read.size;
  progressBar.value=read.size;
  progressBar.setAttribute('aria-valuetext',`${read.size} of ${cards.length} papers read`);
}
checks.forEach(c=>c.addEventListener('change',()=>{
  c.checked?read.add(c.dataset.paperId):read.delete(c.dataset.paperId);
  saveRead();
  renderProgress();
  track('reading_progress',{paper_id:c.dataset.paperId,completed:c.checked,completed_count:read.size});
}));
document.getElementById('reset-progress').addEventListener('click',()=>{
  if(!read.size||!window.confirm('Clear your saved reading progress for this roadmap?'))return;
  read.clear();
  try{localStorage.removeItem(storageKey)}catch(_err){}
  renderProgress();track('reading_progress_reset');
});
document.querySelectorAll('.p-link').forEach(a=>a.addEventListener('click',()=>
  track('paper_open',{paper_id:a.dataset.paperId,paper_title:a.dataset.paperTitle})));
q.addEventListener('input',()=>{
  const t=q.value.trim().toLowerCase();
  let shown=0;
  cards.forEach(c=>{
    const hit=!t||c.dataset.text.includes(t);
    c.classList.toggle('hidden',!hit);
    if(hit)shown++;
  });
  levels.forEach(l=>l.classList.toggle('hidden',
    ![...l.querySelectorAll('.paper')].some(c=>!c.classList.contains('hidden'))));
  counter.textContent=t?`${shown} matching paper${shown===1?'':'s'}`:'';
});
renderProgress();
track('roadmap_view',{paper_count:cards.length});
"""


def paper_card(p: dict) -> str:
    prereqs = ", ".join(p.get("prerequisites", []))
    inst = f" · {e(p['institution'])}" if p.get("institution") else ""
    mvrp = p.get("minimum_viable_path")
    search_text = e(
        f"{p['title']} {p.get('authors','')} {p.get('institution','')} "
        f"{p.get('tldr','')} {p.get('key_takeaway','')}".lower()
    )
    return f"""
<details class="paper" id="paper-{p['id']}" data-mvrp="{1 if mvrp else 0}" data-text="{search_text}">
  <summary>
    <span class="p-num">{p['id']:02d}</span>
    <span class="p-title">{e(p['title'])}</span>
    {'<span class="p-flag">MVRP</span>' if mvrp else ''}
  </summary>
  <div class="p-body">
    <p class="p-byline">{e(p.get('authors',''))}{inst} · {e(p.get('date',''))}</p>
    <div class="p-field"><b>TL;DR</b><p>{e(p.get('tldr',''))}</p></div>
    <div class="p-field"><b>Why read this</b><p>{e(p.get('why',''))}</p></div>
    {f'<div class="p-field"><b>Prerequisites</b><p>{e(prereqs)}</p></div>' if prereqs else ''}
    <div class="p-field"><b>Key takeaway</b><p>{e(p.get('key_takeaway',''))}</p></div>
    <div class="paper-actions">
      <a class="p-link" href="{e(p.get('link',''))}" target="_blank" rel="noopener"
        data-paper-id="{p['id']}" data-paper-title="{e(p['title'])}">Read the paper</a>
      <label class="read-check">
        <input class="paper-done" type="checkbox" data-paper-id="{p['id']}"
          aria-label="Mark {e(p['title'])} as read"> Mark as read
      </label>
    </div>
  </div>
</details>"""


def roadmap_page(r: dict, prev_r: dict, next_r: dict, roadmap_count: int) -> str:
    papers = sorted(r["papers"], key=lambda p: (p["level"], p["id"]))
    levels = {l["n"]: l for l in r.get("levels", [])}
    mvrp = sorted((p for p in r["papers"] if p.get("minimum_viable_path")), key=lambda p: p["id"])

    by_level: dict[int, list] = {}
    for p in papers:
        by_level.setdefault(p["level"], []).append(p)

    level_blocks = []
    for n in sorted(by_level):
        lv = levels.get(n, {})
        tag = f'<span class="level-tag">{e(lv["tagline"])}</span>' if lv.get("tagline") else ""
        cards = "\n".join(paper_card(p) for p in by_level[n])
        level_blocks.append(
            f"""<section class="level-block" id="level-{n}">
  <div class="level-head">
    <span class="level-badge">Level {n}</span>
    <span class="level-name">{e(lv.get('name', f'Level {n}'))}</span>
    {tag}
  </div>
  {cards}
</section>"""
        )

    mvrp_html = ""
    if mvrp:
        items = "\n".join(
            f'<li><a href="#paper-{p["id"]}">{e(p["title"])}</a></li>' for p in mvrp
        )
        mvrp_html = f"""
<h2 class="section-title">Minimum viable reading path</h2>
<div class="mvrp-box">
  <p style="margin:0;color:var(--ink-soft);font-size:14.5px">
    The {len(mvrp)} papers that give you most of the field's mental model, in reading order.</p>
  <ol>{items}</ol>
</div>"""

    def pager_link(rm, direction):
        if not rm:
            return "<span></span>"
        return (
            f'<a href="../{rm["id"]}/"><span class="dir">{direction}</span>'
            f"{e(rm['title'])}</a>"
        )

    desc = (
        f"{r['title']} reading roadmap: {len(papers)} papers across "
        f"{len(by_level)} levels with TL;DRs, prerequisites, and key takeaways."
    )
    json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@graph": [
                {
                    "@type": "BreadcrumbList",
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": 1,
                            "name": BRAND_NAME,
                            "item": f"{SITE_URL}/",
                        },
                        {
                            "@type": "ListItem",
                            "position": 2,
                            "name": r["title"],
                            "item": f"{SITE_URL}/roadmaps/{r['id']}/",
                        },
                    ],
                },
                {
                    "@type": "ItemList",
                    "name": f"{r['title']} paper roadmap",
                    "description": r.get("description", ""),
                    "numberOfItems": len(papers),
                    "itemListElement": [
                        {
                            "@type": "ListItem",
                            "position": i + 1,
                            "name": p["title"],
                            "url": p.get("link", ""),
                        }
                        for i, p in enumerate(papers)
                    ],
                },
            ],
        },
        ensure_ascii=False,
    )

    analytics = ""
    if GA_MEASUREMENT_ID:
        analytics = f"""<script async src="https://www.googletagmanager.com/gtag/js?id={e(GA_MEASUREMENT_ID)}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments)}}
gtag('js',new Date());gtag('config','{e(GA_MEASUREMENT_ID)}',{{anonymize_ip:true}});</script>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(r['title'])} Research Paper Roadmap | {BRAND_NAME}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{SITE_URL}/roadmaps/{r['id']}/">
<link rel="icon" href="../../favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{BRAND_NAME}">
<meta property="og:title" content="{e(r['title'])} Research Paper Roadmap">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{SITE_URL}/roadmaps/{r['id']}/">
<meta property="og:image" content="{SITE_URL}/s.png">
<meta property="og:image:width" content="1280">
<meta property="og:image:height" content="640">
<meta property="og:image:alt" content="{e(r['title'])} roadmap from {BRAND_NAME}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(r['title'])} Research Paper Roadmap">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image:alt" content="{e(r['title'])} roadmap from {BRAND_NAME}">
{analytics}
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&display=swap" rel="stylesheet">
<style>{PAGE_CSS}</style>
<script type="application/ld+json">{json_ld}</script>
</head>
<body data-roadmap="{e(r['id'])}">
<header class="site-head">
  <div class="wrap">
    <a class="brand" href="../../">Papers <span>in Order</span></a>
    <nav class="head-links">
      <a href="../../">All roadmaps</a>
      <a href="{REPO_URL}">GitHub</a>
    </nav>
  </div>
</header>
<main class="wrap">
  <nav class="crumbs"><a href="../../">Roadmaps</a> / {e(r['title'])}</nav>
  <h1>{e(r['title'])}</h1>
  <p class="lede">{e(r.get('description',''))}</p>
  <div class="meta-row">
    <span><b>{len(papers)}</b> papers</span>
    <span><b>{len(by_level)}</b> levels</span>
    <span>Timeline <b>{e(r.get('timeline',''))}</b></span>
    <span>MVRP <b>{len(mvrp)}</b> papers</span>
  </div>
  <div class="progress-box">
    <div class="progress-copy"><strong><span id="progress-count">0</span> of {len(papers)}</strong> papers read. Progress stays in this browser.</div>
    <button class="reset-progress" id="reset-progress" type="button">Reset</button>
    <progress id="progress-bar" max="{len(papers)}" value="0" aria-label="Reading progress"></progress>
  </div>
  {mvrp_html}
  <div class="toolbar">
    <label for="paper-filter" class="hidden">Filter papers</label>
    <input id="paper-filter" type="search"
      placeholder="Filter {len(papers)} papers by title, author, or summary…" autocomplete="off">
    <div id="filter-count" aria-live="polite" style="font-size:13px;color:var(--ink-soft);margin-top:6px"></div>
  </div>
  {''.join(level_blocks)}
  <nav class="pager">
    {pager_link(prev_r, '← Previous roadmap')}
    {pager_link(next_r, 'Next roadmap →')}
  </nav>
</main>
<footer class="site-foot">
  <div class="wrap">
    One of {roadmap_count} roadmaps ·
    <a href="../../">Papers in Order</a> ·
    CC BY 4.0 ·
    <a href="{REPO_URL}/blob/main/CONTRIBUTING.md">Suggest a paper</a>
  </div>
</footer>
<script>{FILTER_JS}</script>
</body>
</html>"""


def write_roadmap_pages(roadmaps: list[dict]) -> None:
    out_root = ROOT / "roadmaps"
    out_root.mkdir(exist_ok=True)
    for i, r in enumerate(roadmaps):
        prev_r = roadmaps[i - 1] if i > 0 else None
        next_r = roadmaps[i + 1] if i < len(roadmaps) - 1 else None
        page_dir = out_root / r["id"]
        page_dir.mkdir(exist_ok=True)
        (page_dir / "index.html").write_text(
            roadmap_page(r, prev_r, next_r, len(roadmaps)), encoding="utf-8"
        )


def write_sitemap(roadmaps: list[dict]) -> None:
    urls = [f"{SITE_URL}/"] + [f"{SITE_URL}/roadmaps/{r['id']}/" for r in roadmaps]
    entries = "\n".join(f"  <url><loc>{u}</loc></url>" for u in urls)
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{entries}\n</urlset>\n",
        encoding="utf-8",
    )
    (ROOT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\n\nSitemap: {SITE_URL}/sitemap.xml\n", encoding="utf-8"
    )


def main() -> int:
    roadmaps, roadmap_count, paper_count = load_data()
    json_data = json.dumps(roadmaps, ensure_ascii=False, separators=(",", ":"))

    html_text = INDEX_FILE.read_text(encoding="utf-8")
    html_text = replace_data_block(html_text, json_data)
    html_text = update_static_counts(html_text, roadmap_count, paper_count)
    html_text = update_static_urls(html_text)
    INDEX_FILE.write_text(html_text, encoding="utf-8")

    write_roadmap_pages(roadmaps)
    write_sitemap(roadmaps)

    print(
        f"✅ Site regenerated — {roadmap_count} roadmaps, {paper_count} papers, "
        f"{roadmap_count} roadmap pages, sitemap.xml, robots.txt."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
