#!/usr/bin/env python3
"""Generate the site from papers.yml.

Outputs:
  index.html            — standalone home page and roadmap catalog
  roadmaps/<id>/index.html — one static, SEO-indexable page per roadmap
  sitemap.xml, robots.txt
"""
from __future__ import annotations

import html
import json
import os
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
# Home page
# ----------------------------------------------------------------------------
HOME_ICON_PATHS = {
    "llm-transformers": '<path d="M5 6.5h10a3 3 0 0 1 3 3v4a3 3 0 0 1-3 3h-4l-4 3v-3H5a3 3 0 0 1-3-3v-4a3 3 0 0 1 3-3Z"/><path d="M7 10h6M7 13h4"/>',
    "computer-vision": '<path d="M2.5 12s3.5-6 9.5-6 9.5 6 9.5 6-3.5 6-9.5 6-9.5-6-9.5-6Z"/><circle cx="12" cy="12" r="3"/>',
    "reinforcement-learning": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="3"/><path d="m15 9 5-5M16 4h4v4"/>',
    "distributed-systems": '<rect x="3" y="4" width="6" height="5" rx="1"/><rect x="15" y="4" width="6" height="5" rx="1"/><rect x="9" y="15" width="6" height="5" rx="1"/><path d="M6 9v3h12V9M12 12v3"/>',
    "graph-neural-networks": '<circle cx="5" cy="7" r="2.5"/><circle cx="19" cy="6" r="2.5"/><circle cx="12" cy="18" r="2.5"/><path d="m7.5 7 9-1M6.5 9l4.3 6.8M17.8 8.2l-4.5 7.5"/>',
    "database-systems": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v6c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 11v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
    "cryptography": '<path d="M12 2.5 20 6v5.5c0 5-3.4 8.2-8 10-4.6-1.8-8-5-8-10V6l8-3.5Z"/><rect x="8.5" y="10" width="7" height="6" rx="1.5"/><path d="M10 10V8.5a2 2 0 0 1 4 0V10"/>',
    "information-retrieval": '<circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5M8 8h5M8 11h4"/>',
    "computer-architecture": '<rect x="6" y="6" width="12" height="12" rx="2"/><rect x="9" y="9" width="6" height="6" rx="1"/><path d="M9 2v4M15 2v4M9 18v4M15 18v4M2 9h4M2 15h4M18 9h4M18 15h4"/>',
    "computational-biology": '<path d="M8 3c6 4 2 14 8 18M16 3C10 7 14 17 8 21M9 6h6M8 11h8M8 16h7"/>',
    "programming-languages": '<path d="m9 7-5 5 5 5M15 7l5 5-5 5M13 4l-2 16"/>',
    "ml-systems": '<rect x="3" y="4" width="18" height="6" rx="2"/><rect x="3" y="14" width="18" height="6" rx="2"/><path d="M7 7h.01M7 17h.01M11 7h6M11 17h6"/>',
}


def home_icon(roadmap_id: str, css_class: str = "icon") -> str:
    paths = HOME_ICON_PATHS.get(roadmap_id, '<path d="M5 3h11a3 3 0 0 1 3 3v15H8a3 3 0 0 1-3-3V3Z"/><path d="M8 3v15a3 3 0 0 0 3 3"/>')
    return f'<svg class="{css_class}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths}</svg>'


def product_mark(css_class: str = "product-mark") -> str:
    return f'''<svg class="{css_class}" viewBox="0 0 32 32" fill="none" aria-hidden="true">
  <rect width="32" height="32" rx="9" fill="currentColor"/>
  <path d="M7.5 9.25c3.3 0 6 .8 8.5 2.65v12.1c-2.5-1.85-5.2-2.65-8.5-2.65V9.25Zm17 0c-3.3 0-6 .8-8.5 2.65v12.1c2.5-1.85 5.2-2.65 8.5-2.65V9.25Z" stroke="white" stroke-width="1.7" stroke-linejoin="round"/>
  <path d="M11 7.5h6.5m0 0-2-2m2 2-2 2" stroke="#bef264" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>
</svg>'''


ARROW_ICON = '<svg class="arrow-icon" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M4 10h11M11 6l4 4-4 4"/></svg>'


HOME_CSS = """
:root{--green:#137a45;--green-dark:#0b4d31;--green-ink:#073b27;--lime:#bef264;--green-soft:#eaf7ef;--ink:#101713;--muted:#5e6a62;--line:#dce5df;--paper:#fff;--wash:#f6f8f6;--shadow:0 22px 50px rgba(15,51,31,.09);--font:"Segoe UI Variable Text","Aptos","Segoe UI",system-ui,-apple-system,sans-serif}
*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--wash);color:var(--ink);font:400 16px/1.6 var(--font);-webkit-font-smoothing:antialiased}a{color:inherit}.wrap{width:min(1160px,calc(100% - 48px));margin:auto}.icon{width:27px;height:27px}.arrow-icon{width:18px;height:18px;transition:transform .18s}.product-mark{width:34px;height:34px;color:var(--green-dark);flex:0 0 auto}
.skip{position:absolute;left:-9999px}.skip:focus{left:16px;top:12px;z-index:30;background:#fff;border:1px solid var(--line);border-radius:8px;padding:8px 12px}.site-head{position:sticky;top:0;z-index:20;background:rgba(255,255,255,.88);border-bottom:1px solid rgba(220,229,223,.85);backdrop-filter:blur(16px)}.site-head .wrap{min-height:72px;display:flex;align-items:center;justify-content:space-between;gap:28px}.brand{display:inline-flex;align-items:center;gap:10px;font-size:18px;font-weight:760;letter-spacing:-.025em;text-decoration:none;transition:transform .18s}.brand:hover{transform:translateY(-1px)}.brand-name span{color:var(--green)}.head-links{display:flex;align-items:center;gap:5px;font-size:14px;font-weight:650}.head-links a{position:relative;text-decoration:none;color:var(--muted);padding:9px 12px;border-radius:9px;transition:color .18s,background .18s,transform .18s}.head-links a:after{content:"";position:absolute;left:12px;right:12px;bottom:5px;height:2px;border-radius:2px;background:var(--green);transform:scaleX(0);transform-origin:left;transition:transform .18s}.head-links a:hover,.head-links a:focus-visible{color:var(--green-dark);background:var(--green-soft);transform:translateY(-1px)}.head-links a:hover:after,.head-links a:focus-visible:after{transform:scaleX(1)}.head-links .nav-cta{margin-left:5px;padding-inline:15px;background:var(--green-dark);color:#fff}.head-links .nav-cta:after{display:none}.head-links .nav-cta:hover,.head-links .nav-cta:focus-visible{background:var(--green);color:#fff;box-shadow:0 7px 16px rgba(11,77,49,.16)}
.hero{position:relative;overflow:hidden;padding:94px 0 78px;background:radial-gradient(circle at 78% 12%,rgba(190,242,100,.27),transparent 25%),linear-gradient(145deg,#fff 0%,#f0f8f2 100%);border-bottom:1px solid var(--line)}.hero:after{content:"";position:absolute;inset:auto -8% -60% 48%;height:520px;background:radial-gradient(circle,rgba(19,122,69,.09),transparent 66%);pointer-events:none}.hero-grid{position:relative;z-index:1;display:grid;grid-template-columns:minmax(0,1.18fr) minmax(320px,.82fr);gap:72px;align-items:center}.eyebrow{display:flex;align-items:center;gap:9px;margin:0 0 17px;color:var(--green);font-weight:760;font-size:12px;letter-spacing:.12em;text-transform:uppercase}.eyebrow-line{width:25px;height:2px;background:var(--lime);box-shadow:10px 0 0 var(--green)}h1{max-width:760px;margin:0;font-size:clamp(44px,6.2vw,76px);font-weight:780;line-height:.99;letter-spacing:-.055em}.hero-copy{max-width:650px;margin:26px 0 0;color:var(--muted);font-size:19px;line-height:1.65}.actions{display:flex;flex-wrap:wrap;gap:12px;margin-top:32px}.button{display:inline-flex;align-items:center;justify-content:center;gap:9px;border-radius:10px;padding:12px 17px;text-decoration:none;font-weight:700;font-size:14px}.button.primary{background:var(--green-dark);color:#fff;box-shadow:0 8px 20px rgba(11,77,49,.18)}.button.primary:hover{background:#073d27}.button:hover .arrow-icon{transform:translateX(3px)}.button.secondary{background:rgba(255,255,255,.8);border:1px solid var(--line);color:var(--green-dark)}
.path-preview{position:relative;padding:25px;border:1px solid rgba(19,122,69,.18);border-radius:20px;background:rgba(255,255,255,.78);box-shadow:var(--shadow);backdrop-filter:blur(10px)}.preview-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px}.preview-title{font-size:13px;font-weight:750}.preview-badge{padding:4px 8px;border-radius:99px;background:var(--green-soft);color:var(--green-dark);font-size:11px;font-weight:700}.path-list{position:relative;display:grid;gap:12px}.path-list:before{content:"";position:absolute;left:17px;top:29px;bottom:29px;width:1px;background:#b7c9bd}.path-item{position:relative;display:grid;grid-template-columns:36px 1fr;gap:12px;align-items:center;padding:12px;border:1px solid var(--line);border-radius:12px;background:#fff}.path-num{position:relative;z-index:1;display:grid;place-items:center;width:36px;height:36px;border-radius:10px;background:var(--green-dark);color:#fff;font-size:11px;font-weight:750}.path-item:nth-child(2) .path-num{background:var(--green)}.path-item:nth-child(3) .path-num{background:#e7f8c6;color:var(--green-ink)}.path-copy b{display:block;font-size:13px}.path-copy span{display:block;margin-top:1px;color:var(--muted);font-size:11px}.preview-foot{display:flex;align-items:center;gap:8px;margin:18px 2px 0;color:var(--muted);font-size:11px}.preview-foot svg{width:15px;height:15px;color:var(--green)}
.stats{display:grid;grid-template-columns:repeat(3,1fr);margin-top:52px;border:1px solid var(--line);border-radius:14px;background:rgba(255,255,255,.8);overflow:hidden}.stat{padding:17px 20px;border-right:1px solid var(--line)}.stat:last-child{border:0}.stat b{display:block;font-size:23px;line-height:1.2;letter-spacing:-.03em}.stat span{font-size:12px;color:var(--muted)}section{scroll-margin-top:88px}.section{padding:82px 0}.section-head{display:flex;align-items:end;justify-content:space-between;gap:36px;margin-bottom:32px}h2{margin:0;font-size:clamp(31px,4vw,47px);font-weight:760;line-height:1.08;letter-spacing:-.045em}.section-head p{max-width:540px;margin:0;color:var(--muted)}
.roadmap-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:18px}.roadmap-card{position:relative;display:flex;flex-direction:column;min-height:300px;padding:22px;background:var(--paper);border:1px solid var(--line);border-radius:16px;text-decoration:none;overflow:hidden;transition:transform .18s,border-color .18s,box-shadow .18s}.roadmap-card:before{content:"";position:absolute;inset:0 0 auto;height:3px;background:linear-gradient(90deg,var(--green),var(--lime));opacity:0;transition:opacity .18s}.roadmap-card:hover,.roadmap-card:focus-visible{transform:translateY(-4px);border-color:#9fc4ad;box-shadow:var(--shadow)}.roadmap-card:hover:before,.roadmap-card:focus-visible:before{opacity:1}.card-top{display:flex;align-items:center;justify-content:space-between}.card-icon{display:grid;place-items:center;width:48px;height:48px;border-radius:13px;background:var(--green-soft);color:var(--green-dark)}.card-number{color:#9aa69e;font-size:11px;font-weight:750;letter-spacing:.08em}.roadmap-card h3{margin:18px 0 9px;font-size:21px;font-weight:750;line-height:1.2;letter-spacing:-.03em}.roadmap-card p{margin:0;color:var(--muted);font-size:13.5px;line-height:1.58}.card-meta{display:flex;flex-wrap:wrap;gap:7px;margin-top:18px}.card-meta span{padding:4px 8px;border:1px solid #dcebe2;border-radius:6px;background:#f5faf7;color:var(--green-dark);font-size:11px;font-weight:650}.card-link{display:flex;align-items:center;gap:6px;margin-top:auto;padding-top:21px;color:var(--green);font-weight:750;font-size:13px}.roadmap-card:hover .card-link .arrow-icon{transform:translateX(3px)}
.how{background:#fff;border-block:1px solid var(--line)}.steps{display:grid;grid-template-columns:repeat(3,1fr);gap:18px;margin-top:36px}.step{padding:24px;border:1px solid var(--line);border-radius:14px;background:var(--wash);transition:transform .18s,border-color .18s,box-shadow .18s}.step:hover{transform:translateY(-3px);border-color:#a9cbb6;box-shadow:0 14px 28px rgba(15,51,31,.07)}.step-num{display:grid;place-items:center;width:34px;height:34px;border-radius:10px;background:var(--green-dark);color:#fff;font-size:12px;font-weight:750}.steps h3{margin:17px 0 7px;font-size:17px}.steps p{margin:0;color:var(--muted);font-size:14px}.trust{display:grid;grid-template-columns:1.15fr .85fr;gap:38px;padding:42px;border-radius:20px;background:linear-gradient(135deg,#0b4d31,#073b27);color:#fff;box-shadow:var(--shadow)}.trust .eyebrow{color:var(--lime)}.trust p{color:#d9e9df}.trust-links{display:flex;flex-direction:column;justify-content:center;gap:10px}.trust-links a{display:flex;align-items:center;justify-content:space-between;gap:10px;background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.15);border-radius:10px;padding:12px 14px;text-decoration:none;font-size:13px;font-weight:650;transition:transform .18s,background .18s,border-color .18s}.trust-links a:hover,.trust-links a:focus-visible{transform:translateX(4px);background:rgba(255,255,255,.14);border-color:rgba(190,242,100,.45)}
.site-foot{padding:0 0 26px;background:#eef3ef;color:#405048}.footer-shell{display:grid;grid-template-columns:1.4fr .6fr .7fr;gap:54px;padding:42px 0 34px}.footer-intro{max-width:390px}.foot-brand{display:flex;align-items:center;gap:10px;color:var(--ink);font-size:17px;font-weight:760}.foot-brand .product-mark{width:31px;height:31px}.footer-intro p{margin:14px 0 0;color:var(--muted);font-size:13px}.footer-col{display:flex;flex-direction:column;align-items:flex-start;gap:7px}.footer-col b{margin-bottom:5px;color:var(--ink);font-size:11px;letter-spacing:.11em;text-transform:uppercase}.footer-col a{display:inline-flex;align-items:center;gap:6px;padding:5px 0;color:var(--muted);font-size:13px;font-weight:620;text-decoration:none;transition:color .18s,transform .18s}.footer-col a .arrow-icon{width:14px;height:14px;opacity:0;transform:translateX(-4px)}.footer-col a:hover,.footer-col a:focus-visible{color:var(--green-dark);transform:translateX(3px)}.footer-col a:hover .arrow-icon,.footer-col a:focus-visible .arrow-icon{opacity:1;transform:translateX(0)}.footer-bottom{display:flex;align-items:center;justify-content:space-between;gap:20px;padding-top:20px;border-top:1px solid #d3ded6;color:#6b776f;font-size:11px}.footer-status{display:inline-flex;align-items:center;gap:7px}.status-dot{width:7px;height:7px;border-radius:50%;background:var(--green);box-shadow:0 0 0 4px rgba(19,122,69,.11)}
@media(max-width:920px){.hero-grid{grid-template-columns:1fr;gap:42px}.path-preview{max-width:620px}.roadmap-grid{grid-template-columns:repeat(2,1fr)}.trust{grid-template-columns:1fr}.steps{grid-template-columns:1fr}.footer-shell{grid-template-columns:1.2fr .8fr .8fr;gap:28px}.hero{padding-top:68px}}@media(max-width:620px){.wrap{width:min(100% - 28px,1160px)}.head-links a:not(.keep):not(.nav-cta){display:none}.roadmap-grid{grid-template-columns:1fr}.stats{grid-template-columns:1fr}.stat{border-right:0;border-bottom:1px solid var(--line)}.section-head{align-items:flex-start;flex-direction:column}.hero{padding:54px 0 48px}.section{padding:56px 0}.path-preview{padding:18px}.trust{padding:27px}.brand-name{font-size:16px}.footer-shell{grid-template-columns:1fr 1fr;gap:28px}.footer-intro{grid-column:1/-1}.footer-bottom{align-items:flex-start;flex-direction:column}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.brand,.head-links a,.roadmap-card,.step,.trust-links a,.footer-col a,.arrow-icon{transition:none}.brand:hover,.head-links a:hover,.roadmap-card:hover,.step:hover,.trust-links a:hover,.footer-col a:hover{transform:none}}
"""


def home_page(roadmaps: list[dict], paper_count: int) -> str:
    cards = []
    for index, roadmap in enumerate(roadmaps, start=1):
        papers = roadmap.get("papers", [])
        mvrp_count = sum(1 for paper in papers if paper.get("minimum_viable_path"))
        cards.append(
            f"""<a class="roadmap-card" href="roadmaps/{e(roadmap['id'])}/">
  <span class="card-top"><span class="card-icon">{home_icon(roadmap['id'])}</span><span class="card-number">{index:02d}</span></span>
  <h3>{e(roadmap['title'])}</h3>
  <p>{e(roadmap.get('description', ''))}</p>
  <div class="card-meta"><span>{len(papers)} papers</span><span>{len(roadmap.get('levels', []))} levels</span><span>{mvrp_count} in the focused path</span></div>
  <span class="card-link">Open roadmap {ARROW_ICON}</span>
</a>"""
        )

    json_ld = json.dumps(
        {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "WebSite", "name": BRAND_NAME, "url": f"{SITE_URL}/", "description": "Curated computer science paper roadmaps ordered by prerequisite."},
                {
                    "@type": "ItemList",
                    "name": "Computer science paper roadmaps",
                    "numberOfItems": len(roadmaps),
                    "itemListElement": [
                        {"@type": "ListItem", "position": index + 1, "name": roadmap["title"], "url": f"{SITE_URL}/roadmaps/{roadmap['id']}/"}
                        for index, roadmap in enumerate(roadmaps)
                    ],
                },
            ],
        },
        ensure_ascii=False,
    )
    analytics = ""
    if GA_MEASUREMENT_ID:
        analytics = f"""<script async src="https://www.googletagmanager.com/gtag/js?id={e(GA_MEASUREMENT_ID)}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{window.dataLayer.push(arguments)}}
gtag('js',new Date());gtag('config','{e(GA_MEASUREMENT_ID)}',{{anonymize_ip:true}});</script>"""

    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{BRAND_NAME} | Computer Science Papers in Reading Order</title>
<meta name="description" content="Choose from {len(roadmaps)} curated computer science roadmaps containing {paper_count} papers, ordered to build understanding step by step.">
<link rel="canonical" href="{SITE_URL}/"><link rel="icon" href="favicon.svg" type="image/svg+xml">
<meta property="og:type" content="website"><meta property="og:site_name" content="{BRAND_NAME}"><meta property="og:title" content="{BRAND_NAME} — computer science research, sequenced"><meta property="og:description" content="{len(roadmaps)} focused reading roadmaps. Choose a field, then read its papers in conceptual order."><meta property="og:url" content="{SITE_URL}/"><meta property="og:image" content="{SITE_URL}/s.png"><meta property="og:image:width" content="1280"><meta property="og:image:height" content="640"><meta property="og:image:alt" content="{BRAND_NAME} computer science paper roadmaps"><meta name="twitter:card" content="summary_large_image">
{analytics}<style>{HOME_CSS}</style><script type="application/ld+json">{json_ld}</script></head>
<body><a class="skip" href="#main">Skip to main content</a>
<header class="site-head"><div class="wrap"><a class="brand" href="./" aria-label="{BRAND_NAME} home">{product_mark()}<span class="brand-name">Papers <span>in Order</span></span></a><nav class="head-links" aria-label="Primary"><a class="keep" href="#roadmaps">Roadmaps</a><a href="#how-it-works">How it works</a><a href="{REPO_URL}/blob/main/EDITORIAL_POLICY.md">Editorial policy</a><a class="nav-cta" href="{REPO_URL}/blob/main/CONTRIBUTING.md">Contribute</a></nav></div></header>
<main id="main"><section class="hero"><div class="wrap"><div class="hero-grid"><div class="hero-content"><p class="eyebrow"><span class="eyebrow-line" aria-hidden="true"></span>Curated for learning, not collecting</p><h1>Find the next paper that makes the field click.</h1><p class="hero-copy">Start from one clear catalog, choose a field, and continue on a dedicated roadmap page. Every list is bounded, ordered by prerequisite, and changes require human review.</p><div class="actions"><a class="button primary" href="#roadmaps">Browse all roadmaps {ARROW_ICON}</a><a class="button secondary" href="{REPO_URL}/blob/main/EDITORIAL_POLICY.md">How papers are chosen</a></div><div class="stats"><div class="stat"><b>{len(roadmaps)}</b><span>standalone roadmaps</span></div><div class="stat"><b>{paper_count}</b><span>curated papers</span></div><div class="stat"><b>1</b><span>focused path per field</span></div></div></div><aside class="path-preview" aria-label="Example of a sequenced reading path"><div class="preview-head"><span class="preview-title">A roadmap, not a reading dump</span><span class="preview-badge">Concept first</span></div><div class="path-list"><div class="path-item"><span class="path-num">01</span><span class="path-copy"><b>Foundation</b><span>Learn the vocabulary and core problem</span></span></div><div class="path-item"><span class="path-num">02</span><span class="path-copy"><b>Breakthrough</b><span>See the idea that changed the field</span></span></div><div class="path-item"><span class="path-num">03</span><span class="path-copy"><b>Modern practice</b><span>Connect the concept to today's systems</span></span></div></div><div class="preview-foot"><svg viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.7" aria-hidden="true"><path d="M10 2.5 16.5 5v4.5c0 4-2.7 6.5-6.5 8-3.8-1.5-6.5-4-6.5-8V5L10 2.5Z"/><path d="m7 10 2 2 4-4"/></svg><span>Each addition requires human editorial review</span></div></aside></div></div></section>
<section class="section" id="roadmaps"><div class="wrap"><div class="section-head"><div><p class="eyebrow">Roadmap catalog</p><h2>Choose a field</h2></div><p>The home page helps you choose. Each card opens a separate page with that field's levels, paper notes, prerequisites, and saved reading progress.</p></div><div class="roadmap-grid">{''.join(cards)}</div></div></section>
<section class="section how" id="how-it-works"><div class="wrap"><p class="eyebrow">A calmer way into research</p><h2>From orientation to understanding</h2><div class="steps"><div class="step"><span class="step-num">1</span><h3>Pick one field</h3><p>Use the catalog to compare scope, length, and the size of each focused path.</p></div><div class="step"><span class="step-num">2</span><h3>Start at your level</h3><p>Roadmap levels are field-specific. Begin where the prerequisites already feel familiar.</p></div><div class="step"><span class="step-num">3</span><h3>Read with context</h3><p>Open each paper with a concise explanation of what it adds and what should come first.</p></div></div></div></section>
<section class="section"><div class="wrap"><div class="trust"><div><p class="eyebrow">Trust the path</p><h2>Curation quality is the product.</h2><p>This is not an exhaustive bibliography or a live feed. Additions should close a real conceptual gap, use open primary sources, and receive human editorial review.</p></div><div class="trust-links"><a href="{REPO_URL}/blob/main/EDITORIAL_POLICY.md"><span>Read the editorial policy</span>{ARROW_ICON}</a><a href="{REPO_URL}/blob/main/CONTRIBUTING.md"><span>Improve a roadmap</span>{ARROW_ICON}</a><a href="{REPO_URL}/issues"><span>Report a stale or incorrect link</span>{ARROW_ICON}</a></div></div></div></section></main>
<footer class="site-foot"><div class="wrap"><div class="footer-shell"><div class="footer-intro"><span class="foot-brand">{product_mark()}<span>{BRAND_NAME}</span></span><p>Curated computer science papers in a sequence that builds understanding.</p></div><nav class="footer-col" aria-label="Explore"><b>Explore</b><a href="#roadmaps"><span>All roadmaps</span>{ARROW_ICON}</a><a href="#how-it-works"><span>How it works</span>{ARROW_ICON}</a></nav><nav class="footer-col" aria-label="Project"><b>Project</b><a href="{REPO_URL}"><span>GitHub</span>{ARROW_ICON}</a><a href="{REPO_URL}/blob/main/CONTRIBUTING.md"><span>Contribute</span>{ARROW_ICON}</a><a href="{REPO_URL}/blob/main/EDITORIAL_POLICY.md"><span>Editorial policy</span>{ARROW_ICON}</a></nav></div><div class="footer-bottom"><span>Content licensed CC BY 4.0</span><span class="footer-status"><span class="status-dot" aria-hidden="true"></span>Static, fast, and account-free</span></div></div></footer></body></html>"""


# ----------------------------------------------------------------------------
# Per-roadmap pages
# ----------------------------------------------------------------------------
PAGE_CSS = """
:root{
  --primary:#006b2c; --primary-soft:#e2f4e5; --primary-dim:#62df7d;
  --bg:#f7f9fb; --surface:#ffffff; --surface-low:#f2f4f6; --surface-high:#e6e8ea;
  --ink:#191c1e; --ink-soft:#3e4a3d; --line:#bdcaba; --line-soft:#dde5db;
  --font:"Segoe UI Variable Text","Aptos","Segoe UI",system-ui,-apple-system,sans-serif;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;background:var(--bg);color:var(--ink);
  font:400 16px/1.6 var(--font);-webkit-font-smoothing:antialiased}
a{color:var(--primary)}
.wrap{max-width:880px;margin:0 auto;padding:0 20px}
.skip{position:absolute;left:-9999px}.skip:focus{left:16px;top:12px;z-index:30;background:#fff;border:1px solid var(--line);border-radius:8px;padding:8px 12px}
.site-head{position:sticky;top:0;z-index:10;border-bottom:1px solid rgba(221,229,219,.9);background:rgba(255,255,255,.9);backdrop-filter:blur(16px)}
.site-head .wrap{display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:68px;padding:10px 20px}
.product-mark{width:32px;height:32px;color:var(--primary);flex:0 0 auto}
.brand{display:inline-flex;align-items:center;gap:9px;color:var(--ink);font-size:17px;font-weight:760;letter-spacing:-.025em;text-decoration:none;transition:transform .18s}
.brand-name span{color:var(--primary)}
.brand:hover{transform:translateY(-1px)}
.head-links{display:flex;align-items:center;gap:4px;font-size:13.5px;font-weight:650}
.head-links a{position:relative;padding:8px 10px;border-radius:8px;text-decoration:none;color:var(--ink-soft);transition:color .18s,background .18s,transform .18s}
.head-links a:after{content:"";position:absolute;left:10px;right:10px;bottom:4px;height:2px;border-radius:2px;background:var(--primary);transform:scaleX(0);transform-origin:left;transition:transform .18s}
.head-links a:hover,.head-links a:focus-visible{color:var(--primary);background:var(--primary-soft);transform:translateY(-1px)}
.head-links a:hover:after,.head-links a:focus-visible:after{transform:scaleX(1)}
.head-links .nav-cta{margin-left:3px;padding-inline:13px;background:#064d28;color:#fff}.head-links .nav-cta:after{display:none}.head-links .nav-cta:hover,.head-links .nav-cta:focus-visible{background:var(--primary);color:#fff;box-shadow:0 7px 16px rgba(0,107,44,.16)}
.crumbs{font-size:13px;color:var(--ink-soft);margin:22px 0 6px}
.crumbs a{color:var(--ink-soft);text-decoration:none}
.crumbs a:hover{color:var(--primary)}
h1{font-size:clamp(32px,5vw,43px);font-weight:780;line-height:1.12;letter-spacing:-.04em;margin:4px 0 10px}
.lede{color:var(--ink-soft);max-width:64ch;margin:0 0 14px}
.meta-row{display:flex;flex-wrap:wrap;gap:8px 20px;font-size:14px;color:var(--ink-soft);
  padding:12px 0 18px;border-bottom:1px solid var(--line-soft)}
.meta-row b{color:var(--ink);font-weight:600}
.section-title{font-size:24px;font-weight:750;line-height:1.3;letter-spacing:-.025em;margin:36px 0 8px}
.mvrp-box{background:var(--surface);border:1px solid var(--line-soft);border-radius:12px;padding:16px 18px;margin-top:10px;transition:border-color .18s,box-shadow .18s}
.mvrp-box:hover{border-color:#a9c9b0;box-shadow:0 10px 25px rgba(19,60,35,.06)}
.mvrp-box ol{margin:8px 0 2px;padding-left:22px}
.mvrp-box li{margin:5px 0}
.mvrp-box a{text-decoration:none}
.mvrp-box a:hover{text-decoration:underline}
.progress-box{display:grid;grid-template-columns:1fr auto;gap:10px 16px;align-items:center;
  background:var(--surface);border:1px solid var(--line-soft);border-radius:12px;padding:16px 18px;margin:18px 0 0;box-shadow:0 8px 20px rgba(19,60,35,.035)}
.progress-copy{font-size:14px;color:var(--ink-soft)}
.progress-copy strong{color:var(--ink)}
.progress-box progress{grid-column:1/-1;width:100%;height:9px;accent-color:var(--primary)}
.reset-progress{border:0;background:none;color:var(--primary);font:650 13px var(--font);cursor:pointer;padding:4px}
.reset-progress:hover{text-decoration:underline}
.toolbar{position:sticky;top:68px;z-index:5;background:var(--bg);padding:12px 0;margin-top:26px;
  border-bottom:1px solid var(--line-soft)}
.toolbar input{width:100%;padding:10px 14px;font:inherit;font-size:15px;color:var(--ink);
  background:var(--surface);border:1px solid var(--line);border-radius:8px}
.toolbar input:focus{outline:2px solid var(--primary);outline-offset:1px}
.level-head{display:flex;align-items:baseline;gap:12px;margin:34px 0 4px}
.level-badge{background:var(--primary);color:#fff;font:700 12px/1 var(--font);
  padding:6px 10px;border-radius:999px;white-space:nowrap}
.level-name{font-size:20px;font-weight:730;line-height:1.3;letter-spacing:-.02em}
.level-tag{font-size:13px;color:var(--ink-soft)}
.paper{background:var(--surface);border:1px solid var(--line-soft);border-radius:11px;margin:12px 0;transition:transform .18s,border-color .18s,box-shadow .18s}
.paper:hover{transform:translateY(-2px);border-color:#a8c8af;box-shadow:0 12px 26px rgba(19,60,35,.065)}
.paper[data-mvrp="1"]{border-left:3px solid var(--primary)}
.paper summary{display:flex;gap:12px;align-items:baseline;padding:14px 16px;cursor:pointer;list-style:none}
.paper summary::-webkit-details-marker{display:none}
.paper summary:hover{background:var(--surface-low);border-radius:10px}
.p-num{font:500 13px/1.6 ui-monospace,SFMono-Regular,monospace;color:var(--ink-soft);min-width:2.2em}
.p-title{font-size:18px;font-weight:650;line-height:1.45;letter-spacing:-.015em;flex:1}
.p-flag{font-size:11px;font-weight:600;color:var(--primary);background:var(--primary-soft);
  padding:3px 8px;border-radius:6px;white-space:nowrap;align-self:center}
.p-body{padding:0 16px 16px 16px;border-top:1px solid var(--line-soft)}
.p-byline{font-size:13.5px;color:var(--ink-soft);margin:12px 0 10px}
.p-field{margin:10px 0}
.p-field b{display:block;font-size:12.5px;font-weight:600;color:var(--primary);margin-bottom:2px}
.p-field p{margin:0;font-size:15px}
.p-link{display:inline-block;margin-top:12px;font-size:14.5px;font-weight:650;
  color:var(--primary);text-decoration:none;border-bottom:1px solid var(--primary-dim);transition:color .18s,border-color .18s,transform .18s}
.p-link:hover{border-bottom-color:var(--primary);transform:translateX(2px)}
.paper-actions{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;margin-top:12px}
.read-check{display:inline-flex;align-items:center;gap:7px;font-size:14px;color:var(--ink-soft);cursor:pointer}
.read-check input{width:17px;height:17px;accent-color:var(--primary)}
.paper.is-read{opacity:.72}
.paper.is-read .p-title{text-decoration:line-through;text-decoration-thickness:1px}
.pager{display:flex;justify-content:space-between;gap:16px;margin:48px 0 24px;font-size:15px}
.pager a{text-decoration:none;background:var(--surface);border:1px solid var(--line-soft);
  border-radius:10px;padding:12px 16px;color:var(--ink);max-width:48%;transition:transform .18s,border-color .18s,box-shadow .18s}
.pager a:hover,.pager a:focus-visible{transform:translateY(-2px);border-color:var(--primary);box-shadow:0 10px 20px rgba(19,60,35,.06)}
.pager .dir{display:block;font-size:12.5px;color:var(--ink-soft);margin-bottom:2px}
.site-foot{margin-top:32px;padding:28px 0;background:#eaf2ec;border-top:1px solid #d5e2d8;color:var(--ink-soft)}
.roadmap-footer{display:flex;align-items:center;justify-content:space-between;gap:28px}
.roadmap-foot-brand{display:flex;align-items:center;gap:11px}.roadmap-foot-brand .product-mark{width:36px;height:36px}.roadmap-foot-brand strong{display:block;color:var(--ink);font-size:15px}.roadmap-foot-brand span{display:block;margin-top:1px;font-size:11.5px}
.roadmap-foot-links{display:flex;align-items:center;gap:5px}.roadmap-foot-links a{padding:8px 10px;border-radius:8px;color:var(--ink-soft);font-size:13px;font-weight:650;text-decoration:none;transition:color .18s,background .18s,transform .18s}.roadmap-foot-links a:hover,.roadmap-foot-links a:focus-visible{color:var(--primary);background:#fff;transform:translateY(-1px)}.roadmap-foot-links .foot-cta{margin-left:4px;padding-inline:13px;background:#064d28;color:#fff}.roadmap-foot-links .foot-cta:hover,.roadmap-foot-links .foot-cta:focus-visible{background:var(--primary);color:#fff;box-shadow:0 7px 16px rgba(0,107,44,.14)}
.hidden{display:none}
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}
mark{background:var(--primary-soft);color:inherit}
@media (max-width:560px){
  .head-links a:not(.nav-cta){display:none}
  .brand-name{font-size:15px}
  .paper summary{flex-wrap:wrap}
  .pager{flex-direction:column}
  .pager a{max-width:100%}
  .roadmap-footer{align-items:flex-start;flex-direction:column}
  .roadmap-foot-links{flex-wrap:wrap}
}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}.brand,.head-links a,.mvrp-box,.paper,.p-link,.pager a,.roadmap-foot-links a{transition:none}.brand:hover,.head-links a:hover,.paper:hover,.p-link:hover,.pager a:hover,.roadmap-foot-links a:hover{transform:none}}
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
<style>{PAGE_CSS}</style>
<script type="application/ld+json">{json_ld}</script>
</head>
<body data-roadmap="{e(r['id'])}">
<a class="skip" href="#main">Skip to main content</a>
<header class="site-head">
  <div class="wrap">
    <a class="brand" href="../../" aria-label="{BRAND_NAME} home">{product_mark()}<span class="brand-name">Papers <span>in Order</span></span></a>
    <nav class="head-links" aria-label="Primary">
      <a href="../../">Home</a>
      <a href="../../#roadmaps">All roadmaps</a>
      <a class="nav-cta" href="{REPO_URL}/blob/main/CONTRIBUTING.md">Contribute</a>
    </nav>
  </div>
</header>
<main class="wrap" id="main">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="../../">Home</a> / <a href="../../#roadmaps">Roadmaps</a> / {e(r['title'])}</nav>
  <h1>{e(r['title'])}</h1>
  <p class="lede">{e(r.get('description',''))}</p>
  <div class="meta-row">
    <span><b>{len(papers)}</b> papers</span>
    <span><b>{len(by_level)}</b> levels</span>
    <span>Included papers <b>{e(r.get('timeline',''))}</b></span>
    <span>MVRP <b>{len(mvrp)}</b> papers</span>
  </div>
  <div class="progress-box">
    <div class="progress-copy"><strong><span id="progress-count">0</span> of {len(papers)}</strong> papers read. Progress stays in this browser.</div>
    <button class="reset-progress" id="reset-progress" type="button">Reset</button>
    <progress id="progress-bar" max="{len(papers)}" value="0" aria-label="Reading progress"></progress>
  </div>
  {mvrp_html}
  <div class="toolbar">
    <label for="paper-filter" class="sr-only">Filter papers</label>
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
  <div class="wrap roadmap-footer">
    <div class="roadmap-foot-brand">{product_mark()}<div><strong>{BRAND_NAME}</strong><span>One of {roadmap_count} curated roadmaps · CC BY 4.0</span></div></div>
    <nav class="roadmap-foot-links" aria-label="Footer">
      <a href="../../">Home</a>
      <a href="../../#roadmaps">All roadmaps</a>
      <a class="foot-cta" href="{REPO_URL}/blob/main/CONTRIBUTING.md">Suggest a paper</a>
    </nav>
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
    INDEX_FILE.write_text(home_page(roadmaps, paper_count), encoding="utf-8")

    write_roadmap_pages(roadmaps)
    write_sitemap(roadmaps)

    print(
        f"✅ Site regenerated — {roadmap_count} roadmaps, {paper_count} papers, "
        f"{roadmap_count} roadmap pages, sitemap.xml, robots.txt."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
