#!/usr/bin/env python3
"""
The Open Arena — static site builder.

Reads data/examples/*.json + data/groups/*.json and emits the whole site into site/.
No frameworks, no runtime dependencies — the OUTPUT is pure static HTML.
Run:  python3 build.py
"""

import html
import json
import pathlib
import re
import shutil
import sys
from datetime import date

ROOT = pathlib.Path(__file__).resolve().parent
GROUPS_DIR = ROOT / "data" / "groups"
EXAMPLES_DIR = ROOT / "data" / "examples"
OUT = ROOT / "site"

BRAND = "The Open Arena"
TAGLINE = "A free sports library"
COPYRIGHT_YEAR = date.today().year
SITE_URL = "https://adineo-cmd.github.io/the-open-arena/"
OPEN_DOJO_URL = "https://github.com/adineo-cmd/the-open-dojo"
EDITORS_EMAIL = "mailto:editors@openarena.example"

CATEGORIES = {
    "team-ball": {
        "name": "Ball & Team Sports", "glyph": "⚽", "var": "--cat-team",
        "blurb": "Eleven-a-side or five, on grass or ice — the games we play together.",
    },
    "racket": {
        "name": "Racket & Net Sports", "glyph": "🎾", "var": "--cat-racket",
        "blurb": "One net, two sides, and a ball that talks back.",
    },
    "combat": {
        "name": "Combat & Martial Arts", "glyph": "🥊", "var": "--cat-combat",
        "blurb": "The fighting arts — sport rules over ancient instincts.",
    },
    "athletics": {
        "name": "Athletics & Endurance", "glyph": "🏃", "var": "--cat-athletics",
        "blurb": "Run, walk, jump, throw, and keep going farther than seems sensible.",
    },
    "water": {
        "name": "Water Sports", "glyph": "🌊", "var": "--cat-water",
        "blurb": "Pools, rivers, and open sea — the sports that make peace with water.",
    },
    "winter": {
        "name": "Winter Sports", "glyph": "⛷️", "var": "--cat-winter",
        "blurb": "Snow and ice underfoot — gravity as a training partner.",
    },
    "cycling-motor": {
        "name": "Cycling & Motorsport", "glyph": "🚴", "var": "--cat-cycling",
        "blurb": "Two wheels, human or horsepower, and the racing line.",
    },
    "strength": {
        "name": "Strength & Power Sports", "glyph": "🏋️", "var": "--cat-strength",
        "blurb": "Iron, stones, and the barbell's honest arithmetic.",
    },
    "gymnastics-aesthetic": {
        "name": "Gymnastics & Aesthetic Sports", "glyph": "🤸", "var": "--cat-gym",
        "blurb": "Where sport becomes choreography and the body learns to fly.",
    },
    "precision": {
        "name": "Precision & Target Sports", "glyph": "🎯", "var": "--cat-precision",
        "blurb": "Steady hands, quiet breaths, and the smallest margins in sport.",
    },
    "outdoor-air": {
        "name": "Outdoor & Air Sports", "glyph": "🧗", "var": "--cat-outdoor",
        "blurb": "Cliffs, thermals, and race courses drawn on open maps.",
    },
    "equestrian": {
        "name": "Equestrian Sports", "glyph": "🏇", "var": "--cat-equestrian",
        "blurb": "The only Olympic family where your teammate has a heartbeat of its own.",
    },
    "mind": {
        "name": "Mind & Table Sports", "glyph": "♟️", "var": "--cat-mind",
        "blurb": "Games of perfect sweat and imperfect nerves — sport of the mind.",
    },
    "domains": {
        "name": "Training Domains", "glyph": "🧰", "var": "--cat-domains",
        "blurb": "The disciplines that build athletes before any single sport claims them.",
    },
}

SECTION_ORDER = [
    ("glance", "At a glance", "facts"),
    ("what", "What it is", "overview"),
    ("history", "How it got here", "history"),
    ("play", "Ways to play", "formats"),
    ("skills", "Core skills", "skills"),
    ("rules", "Rules you need", "rules"),
    ("gear", "Gear guide", "equipment"),
    ("training", "Training for it", "training"),
    ("pathway", "The pathway", "pathway"),
    ("events", "Where it's decided", "events"),
    ("legends", "Legends", "legends"),
    ("start", "Start this week", "getting_started"),
    ("glossary", "Glossary", "glossary"),
]

DOMAIN_HEADINGS = {
    "glance": "At a glance",
    "what": "What it is",
    "history": "How it took shape",
    "play": "Key methods",
    "skills": "Core qualities",
    "rules": "Principles",
    "gear": "A small toolkit",
    "training": "How to practice it",
    "pathway": "How people progress",
    "events": "Tests & benchmarks",
    "legends": "Voices & pioneers",
    "start": "Start this week",
    "glossary": "Glossary",
}


def esc(s) -> str:
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- data loading

def load_sports():
    entries = []  # (dict, source_group)
    files = sorted(EXAMPLES_DIR.glob("*.json")) + sorted(GROUPS_DIR.glob("*.json"))
    for f in files:
        with open(f, encoding="utf-8") as fh:
            data = json.load(fh)
        if not isinstance(data, list):
            sys.exit(f"ERROR: {f} must contain a JSON array")
        for i, sport in enumerate(data):
            entries.append((sport, f"{f.name}[{i}]"))
    return entries


REQUIRED = [
    "slug", "name", "category", "glyph", "tagline", "origin", "tags",
    "overview", "facts", "history", "formats", "skills", "rules",
    "equipment", "training", "pathway", "events", "legends",
    "getting_started", "glossary", "related", "crosslink",
]
LIST_FIELDS = [
    "tags", "overview", "rules", "training", "getting_started",
]
PAIR_FIELDS = ["facts", "history", "formats", "equipment", "pathway", "events", "legends", "glossary"]
TRIPLE_FIELDS = ["skills"]


def validate(entries):
    problems = []
    seen = {}
    for s, src in entries:
        slug = s.get("slug", f"<no-slug@{src}>")
        for field in REQUIRED:
            if field not in s:
                problems.append(f"{src} ({slug}): missing field '{field}'")
        cat = s.get("category")
        if cat not in CATEGORIES:
            problems.append(f"{src} ({slug}): unknown category '{cat}'")
        if slug in seen:
            problems.append(f"{src} ({slug}): duplicate slug (first seen in {seen[slug]})")
        seen[slug] = src
        for lf in LIST_FIELDS:
            if lf in s and not (isinstance(s[lf], list) and s[lf]):
                problems.append(f"{src} ({slug}): '{lf}' should be a non-empty list")
        for pf in PAIR_FIELDS:
            if pf in s:
                for j, row in enumerate(s[pf]):
                    if not (isinstance(row, list) and len(row) >= 2):
                        problems.append(f"{src} ({slug}): '{pf}' row {j} is not a pair")
        for tf in TRIPLE_FIELDS:
            if tf in s:
                for j, row in enumerate(s[tf]):
                    if not (isinstance(row, list) and len(row) >= 3):
                        problems.append(f"{src} ({slug}): '{tf}' row {j} needs 3 columns")
        for rel in s.get("related", []):
            if rel not in {x.get("slug") for x, _ in entries}:
                problems.append(f"{src} ({slug}): related slug '{rel}' not found (yet)")
    return problems, seen


# ---------------------------------------------------------------- shared chrome

def favicon(seed: str) -> str:
    return (
        "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E"
        "%3Crect width='64' height='64' rx='12' fill='%232e6b46'/%3E"
        f"%3Ctext x='32' y='43' font-size='34' text-anchor='middle'%3E{seed}%3C/text%3E%3C/svg%3E"
    )


def header(*, title, desc, prefix, current, body_class=""):
    nav = f"""
      <nav class="site-nav" aria-label="Primary">
        <ul>
          <li><a href="{prefix}index.html"{' class="current" aria-current="page"' if current == 'home' else ''}>Home</a></li>
          <li class="has-sub">
            <a href="{prefix}index.html#browse">Categories</a>
            <ul class="submenu">
"""
    for cid, c in CATEGORIES.items():
        if cid == "domains":
            continue
        nav += f'              <li><a href="{prefix}index.html#{cid}">{esc(c["glyph"])} {esc(c["name"])}</a></li>\n'
    nav += f"""              <li class="subhead">Beyond sport</li>
              <li><a href="{prefix}index.html#domains">🧰 Training domains</a></li>
            </ul>
          </li>
          <li><a href="{prefix}sports-a-z.html"{' class="current" aria-current="page"' if current == 'az' else ''}>A–Z</a></li>
          <li><a href="{prefix}about.html"{' class="current" aria-current="page"' if current == 'about' else ''}>About</a></li>
        </ul>
        <form class="searchbox" action="{prefix}search.html" role="search">
          <input type="search" name="q" placeholder="Search the arena…" aria-label="Search the library">
        </form>
      </nav>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)} — {BRAND}</title>
  <meta name="description" content="{esc(desc)}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:opsz,wght@8..60,400;8..60,600;8..60,700&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{prefix}assets/css/site.css">
  <link rel="icon" href="{favicon('🏟')}">
</head>
<body{' class="' + body_class + '"' if body_class else ''}>
  <a class="skip-link" href="#main">Skip to content</a>

  <header class="site-header">
    <div class="container header-inner">
      <a class="brand" href="{prefix}index.html">
        <span class="brand-seal" aria-hidden="true">🏟</span>
        <span class="brand-text">{BRAND}
          <small>{TAGLINE}</small>
        </span>
      </a>{nav}
    </div>
  </header>

  <main id="main">
"""


def footer(prefix=""):
    return f"""  </main>

  <footer class="site-footer">
    <div class="container footer-grid">
      <div>
        <div class="footer-brand">
          <span class="brand-seal" aria-hidden="true">🏟</span>
          <strong>{BRAND}</strong>
        </div>
        <p>A free, community-minded reference for every sport on Earth — from the schoolyard to the stadium, written to be read between sessions.</p>
        <p class="small">Sister library: <a href="{OPEN_DOJO_URL}">The Open Dojo</a> — the same idea, for the martial arts.</p>
      </div>
      <div>
        <h4>Browse</h4>
        <ul>
          <li><a href="{prefix}index.html#browse">All categories</a></li>
          <li><a href="{prefix}sports-a-z.html">Sports A–Z</a></li>
          <li><a href="{prefix}index.html#domains">Training domains</a></li>
          <li><a href="{prefix}search.html">Search</a></li>
          <li><a href="{prefix}about.html">About this library</a></li>
        </ul>
      </div>
      <div>
        <h4>Contributing</h4>
        <ul>
          <li><a href="{EDITORS_EMAIL}">Send a correction</a></li>
          <li><a href="{EDITORS_EMAIL}">Suggest a sport</a></li>
        </ul>
        <p class="small">Found a mistake? These pages improve the way athletes do — repetition with attention.</p>
      </div>
    </div>
    <div class="footer-legal">
      <div class="container">
        <span>© {COPYRIGHT_YEAR} {BRAND}. Original reference content, written for athletes and the curious.</span>
        <span>Informational only — train within your limits, and under qualified supervision when it matters.</span>
      </div>
    </div>
  </footer>
</body>
</html>
"""


# ---------------------------------------------------------------- fragments

def cat_style(cid: str) -> str:
    return f"--cat: var({CATEGORIES[cid]['var']});"


def wiki_table(headers, rows, first_col_key=False) -> str:
    head = "".join(f"<th scope=\"col\">{esc(h)}</th>" for h in headers)
    body = []
    for row in rows:
        cells = []
        for j, cell in enumerate(row):
            cls = ' class="k"' if first_col_key and j == 0 else ""
            cells.append(f"<td{cls}>{esc(cell)}</td>")
        body.append("<tr>" + "".join(cells) + "</tr>")
    return f"""<div class="table-wrap"><table class="wiki">
  <thead><tr>{head}</tr></thead>
  <tbody>{''.join(body)}</tbody>
</table></div>"""


def jump_list(sections) -> str:
    if not sections:
        return ""
    items = "".join(f'<li><a href="#{sid}">{esc(label)}</a></li>' for sid, label in sections)
    return f"<ul class=\"jump-list\" aria-label=\"On this page\">{items}</ul>"


# ---------------------------------------------------------------- sport page

def sport_page(s: dict, pool, seen_slugs) -> str:
    slug = s["slug"]
    cid = s["category"]
    cat = CATEGORIES[cid]
    is_domain = cid == "domains"
    headings = DOMAIN_HEADINGS if is_domain else {sid: label for sid, label, _ in SECTION_ORDER}

    # category-mates pager
    mates = sorted([x for x in seen_slugs.keys()], key=str)
    same_cat = sorted([x for x in pool if x["category"] == cid], key=lambda x: x["name"])
    idx = next((i for i, x in enumerate(same_cat) if x["slug"] == slug), -1)
    prev_s = same_cat[idx - 1] if idx > 0 else (same_cat[-1] if len(same_cat) > 1 else None)
    next_s = same_cat[idx + 1] if 0 <= idx < len(same_cat) - 1 else (same_cat[0] if len(same_cat) > 1 else None)
    prefix = "../"

    crumbs = (
        f'<p class="crumbs"><a href="{prefix}index.html">Home</a> › '
        f'<a href="{prefix}index.html#{cid}">{esc(cat["name"])}</a> › {esc(s["name"])}</p>'
    )
    sections_present = [sid for sid, _label, field in
                        [(a, b, c) for a, b, c in SECTION_ORDER] if s.get(field)]
    jumps = jump_list([(sid, headings[sid]) for sid in sections_present])

    head = header(
        title=s["name"],
        desc=s["tagline"],
        prefix=prefix,
        current="",
        body_class="sport-page",
    )

    hero = f"""    <section class="page-hero">
      <div class="container">
        {crumbs}
        <div class="hero-flex">
          <div class="hero-glyph-badge" aria-hidden="true">{esc(s["glyph"])}</div>
          <div>
            <span class="cat-tag" style="{cat_style(cid)}">{esc(cat["name"])}</span>
            <h1>{esc(s["name"])}</h1>
            <p class="lede">{esc(s["tagline"])}<br>
            <span class="small muted">{esc(s["origin"])} · {' · '.join(esc(t) for t in s['tags'])}</span></p>
          </div>
        </div>
        {jumps}
      </div>
    </section>
"""

    parts = [hero]

    # At a glance
    if s.get("facts"):
        parts.append(f"""    <section class="section-tight" id="glance">
      <div class="container">
        <h2>{esc(headings['glance'])}</h2>
        {wiki_table(["", ""], s["facts"], first_col_key=True).replace("<thead><tr><th scope=\"col\"></th><th scope=\"col\"></th></tr></thead>", "")}
      </div>
    </section>""")

    # Overview
    if s.get("overview"):
        paras = "".join(f"<p>{esc(p)}</p>" for p in s["overview"])
        parts.append(f"""    <section class="section-tight" id="what">
      <div class="container">
        <h2>{esc(headings['what'])}</h2>
        {paras}
      </div>
    </section>""")

    # History timeline
    if s.get("history"):
        items = "".join(
            f"<li><span class=\"when\">{esc(when)}</span><span class=\"what\">{esc(what)}</span></li>"
            for when, what in s["history"]
        )
        parts.append(f"""    <section class="section-tight" id="history">
      <div class="container">
        <h2>{esc(headings['history'])}</h2>
        <ul class="timeline">{items}</ul>
      </div>
    </section>""")

    # Formats
    if s.get("formats"):
        parts.append(f"""    <section class="section-tight" id="play">
      <div class="container">
        <h2>{esc(headings['play'])}</h2>
        {wiki_table(["Format", "What it is"], s["formats"], first_col_key=True)}
      </div>
    </section>""")

    # Skills
    if s.get("skills"):
        parts.append(f"""    <section class="section-tight" id="skills">
      <div class="container">
        <h2>{esc(headings['skills'])}</h2>
        {wiki_table(["Skill", "What it is", "How to train it"], s["skills"], first_col_key=True)}
      </div>
    </section>""")

    # Rules
    if s.get("rules"):
        lis = "".join(f"<li>{esc(r)}</li>" for r in s["rules"])
        parts.append(f"""    <section class="section-tight" id="rules">
      <div class="container">
        <h2>{esc(headings['rules'])}</h2>
        <div class="panel"><ul class="rules-list">{lis}</ul></div>
      </div>
    </section>""")

    # Equipment
    if s.get("equipment"):
        panels = "".join(
            f"<div class=\"panel\"><h3>{esc(name)}</h3><p>{esc(desc)}</p></div>"
            for name, desc in s["equipment"]
        )
        parts.append(f"""    <section class="section-tight" id="gear">
      <div class="container">
        <h2>{esc(headings['gear'])}</h2>
        <div class="equipment-grid">{panels}</div>
      </div>
    </section>""")

    # Training
    if s.get("training"):
        lis = "".join(f"<li>{esc(t)}</li>" for t in s["training"])
        extra = ""
        if not is_domain:
            extra = (f'<p class="anchor-note">Want the engine behind all of this? '
                     f'The <a href="{prefix}domains/strength-and-conditioning.html">strength &amp; conditioning</a> '
                     f'page covers programming, and the other <a href="{prefix}index.html#domains">training domains</a> '
                     f'cover the rest.</p>')
        parts.append(f"""    <section class="section-tight" id="training">
      <div class="container">
        <h2>{esc(headings['training'])}</h2>
        <ul>{lis}</ul>
        {extra}
      </div>
    </section>""")

    # Pathway
    if s.get("pathway"):
        parts.append(f"""    <section class="section-tight" id="pathway">
      <div class="container">
        <h2>{esc(headings['pathway'])}</h2>
        {wiki_table(["Stage", "What it looks like"], s["pathway"], first_col_key=True)}
      </div>
    </section>""")

    # Events
    if s.get("events"):
        parts.append(f"""    <section class="section-tight" id="events">
      <div class="container">
        <h2>{esc(headings['events'])}</h2>
        {wiki_table(["Competition", "What it is"], s["events"], first_col_key=True)}
      </div>
    </section>""")

    # Legends
    if s.get("legends"):
        rows = "".join(
            f"<div><dt>{esc(name)}</dt><dd>{esc(desc)}</dd></div>" for name, desc in s["legends"]
        )
        parts.append(f"""    <section class="section-tight" id="legends">
      <div class="container">
        <h2>{esc(headings['legends'])}</h2>
        <dl class="term-grid">{rows}</dl>
      </div>
    </section>""")

    # Getting started
    if s.get("getting_started"):
        lis = "".join(f"<li>{esc(st)}</li>" for st in s["getting_started"])
        parts.append(f"""    <section class="section-tight" id="start">
      <div class="container">
        <h2>{esc(headings['start'])}</h2>
        <ol class="steps">{lis}</ol>
      </div>
    </section>""")

    # Glossary
    if s.get("glossary"):
        parts.append(f"""    <section class="section-tight" id="glossary">
      <div class="container">
        <h2>{esc(headings['glossary'])}</h2>
        {wiki_table(["Term", "Meaning"], s["glossary"], first_col_key=True)}
      </div>
    </section>""")

    # Cross-link to The Open Dojo (combat sports)
    if s.get("crosslink"):
        parts.append(f"""    <section class="section-tight">
      <div class="container">
        <div class="callout callout--kin">
          <h3>The deeper tradition lives at The Open Dojo</h3>
          <p>This page covers the sport; our sister library <a href="{OPEN_DOJO_URL}">The Open Dojo</a> is the same idea built for the martial arts — styles, kata and forms, techniques, terminology, and training syllabi in depth.</p>
        </div>
      </div>
    </section>""")

    # Related
    rel_names = []
    for rel in s.get("related", []):
        target = pool_by_slug.get(rel)
        if target:
            href = f"{prefix}{'domains/' if target['category'] == 'domains' else 'sports/'}{rel}.html"
            rel_names.append(f'<a class="chip chip--cat" style="{cat_style(target["category"])}" href="{href}">{esc(target["glyph"])} {esc(target["name"].split(" (")[0])}</a>')
    if rel_names:
        parts.append(f"""    <section class="section-tight">
      <div class="container">
        <h2>Related pages</h2>
        <div class="chips">{''.join(rel_names)}</div>
      </div>
    </section>""")

    # Pager
    pager_bits = []
    if prev_s:
        pager_bits.append(f'<a href="{prefix}{"domains/" if prev_s["category"] == "domains" else "sports/"}{prev_s["slug"]}.html">← {esc(prev_s["name"].split(" (")[0])}</a>')
    if next_s and next_s["slug"] != (prev_s["slug"] if prev_s else None):
        pager_bits.append(f'<a href="{prefix}{"domains/" if next_s["category"] == "domains" else "sports/"}{next_s["slug"]}.html">{esc(next_s["name"].split(" (")[0])} →</a>')
    if pager_bits:
        parts.append(f"""    <section class="section-tight">
      <div class="container">
        <p class="back-top"><a href="{prefix}index.html#{cid}">↑ More {esc(cat['name'].lower())}</a></p>
        <div class="pager">{''.join(pager_bits)}</div>
      </div>
    </section>""")

    # Safety
    parts.append(f"""    <section class="section-tight">
      <div class="container">
        <div class="callout callout--safety">
          <h3>Before you try anything here</h3>
          <p>Pages can describe; they cannot spot your form. Learn new skills with a qualified coach, progress gradually, and treat this library as the reading between sessions — not the session itself. <strong>Train smart, and the library will still be here tomorrow.</strong></p>
        </div>
      </div>
    </section>""")

    return head + "\n".join(parts) + footer(prefix)


# ---------------------------------------------------------------- hub page

def sport_card(s: dict, prefix="") -> str:
    href = f"{prefix}{'domains/' if s['category'] == 'domains' else 'sports/'}{s['slug']}.html"
    return f"""          <article class="sport-card">
            <div class="glyph" aria-hidden="true">{esc(s["glyph"])}</div>
            <div class="origin">{esc(s["origin"])}</div>
            <h3>{esc(s["name"].split(" (")[0])}</h3>
            <p>{esc(s["tagline"])}</p>
            <a class="more" href="{href}">Read about {esc(s["name"].split(" (")[0])}</a>
          </article>"""


def build_index(pool):
    sports = [s for s in pool if s["category"] != "domains"]
    domains = [s for s in pool if s["category"] == "domains"]
    cats = [c for c in CATEGORIES if c != "domains"]

    featured_slugs = [
        "soccer", "basketball", "tennis", "track-and-field", "swimming", "formula-1",
        "boxing", "artistic-gymnastics", "golf", "chess", "esports", "curling",
    ]
    by_slug = {s["slug"]: s for s in pool}
    featured = [by_slug[x] for x in featured_slugs if x in by_slug][:12]

    cat_cards = "".join(
        f"""          <a class="section-card" href="#{cid}">
            <span class="glyph" aria-hidden="true">{esc(c["glyph"])}</span>
            <h3>{esc(c["name"])}</h3>
            <p>{esc(c["blurb"])}</p>
          </a>"""
        for cid, c in CATEGORIES.items()
    )

    featured_grid = "\n".join(sport_card(s) for s in featured)

    master = []
    for cid in cats:
        group = sorted([s for s in sports if s["category"] == cid], key=lambda x: x["name"])
        lis = "".join(
            f"<li><a href=\"sports/{s['slug']}.html\">{esc(s['name'].split(' (')[0])}</a></li>"
            for s in group
        )
        master.append(
            f"<div class=\"master-list\" id=\"{cid}\"><h3><span class=\"cat-dot\" style=\"{cat_style(cid)}\" aria-hidden=\"true\"></span>"
            f"{esc(CATEGORIES[cid]['glyph'])} {esc(CATEGORIES[cid]['name'])} <span class=\"count\">{len(group)} sports</span></h3>"
            f"<p class=\"section-intro\">{esc(CATEGORIES[cid]['blurb'])}</p><ul>{lis}</ul></div>"
        )

    domain_cards = "".join(
        f"""          <a class="section-card" href="domains/{s['slug']}.html">
            <span class="glyph" aria-hidden="true">{esc(s["glyph"])}</span>
            <h3>{esc(s["name"])}</h3>
            <p>{esc(s["tagline"])}</p>
          </a>"""
        for s in sorted(domains, key=lambda x: x["name"])
    )

    n_sports = len(sports)
    n_pages = len(pool)

    head = header(
        title="A free reference library for every sport",
        desc="The Open Arena is a free reference for every sport on Earth — ball games and barbell sports, mind games and mountain sports. No account, no fee, open whenever you train.",
        prefix="",
        current="home",
    )

    body = f"""    <section class="hero">
      <div class="container">
        <div class="hero-grid">
          <div class="hero-copy hero-load">
            <h1>Every sport deserves a library.</h1>
            <p class="lede">The Open Arena is a free reference for all of them — {n_sports} sports from soccer to sumo, each with its own page of history, skills, rules, gear, and how to actually start. No account, no fee, open whenever you are.</p>
            <form class="hero-search" action="search.html" role="search">
              <input type="search" name="q" placeholder="Try “pickleball”, “tug of war”, or “bouldering”" aria-label="Search the library">
              <button type="submit">Search</button>
            </form>
            <div class="stat-row">
              <div class="stat"><b>{n_sports}</b><span>sports, one page each</span></div>
              <div class="stat"><b>13</b><span>families of sport</span></div>
              <div class="stat"><b>{len(domains)}</b><span>training domains</span></div>
              <div class="stat"><b>0</b><span>accounts, fees, ads</span></div>
            </div>
          </div>
          <figure class="hero-glyph hero-load" style="animation-delay:.12s">
            <span class="glyph" aria-hidden="true">🏆</span>
            <figcaption><span class="romaji">agon</span> — the Greek word for the gathering where people contest. Every sport on these pages is its own answer to the same human instinct.</figcaption>
          </figure>
        </div>
        <hr class="arena-stripe" aria-hidden="true" title="One stripe for each family of sport">
      </div>
    </section>

    <section class="section-tight" id="browse">
      <div class="container">
        <h2>Browse by family</h2>
        <p class="section-intro">Thirteen families cover the whole sporting world, and one more covers the training that builds athletes before any single sport claims them.</p>
        <div class="section-cards">
{cat_cards}
        </div>
      </div>
    </section>

    <section class="section">
      <div class="container">
        <h2>Start anywhere</h2>
        <p class="section-intro">Twelve pages to wander into. The <a href="sports-a-z.html">full A–Z index</a> holds everything else.</p>
        <div class="sport-grid">
{featured_grid}
        </div>
      </div>
    </section>

    <section class="section-tight">
      <div class="container">
        <h2>The master list</h2>
        <p class="section-intro">Every page in the arena, family by family. If humans compete at it, it should be here — and if it is missing, <a href="{EDITORS_EMAIL}">tell the editors</a>.</p>
        {''.join(master)}
      </div>
    </section>

    <section class="section-tight" id="domains">
      <div class="container">
        <h2>Training domains</h2>
        <p class="section-intro">Not sports themselves — the disciplines that build athletes for all of them. Strength &amp; conditioning, nutrition, mobility, speed, and the rest.</p>
        <div class="section-cards section-cards--domains">
{domain_cards}
        </div>
      </div>
    </section>

    <section class="section-tight">
      <div class="container">
        <div class="callout callout--kin">
          <h3>Trained in the fighting arts?</h3>
          <p>Our sister library <a href="{OPEN_DOJO_URL}">The Open Dojo</a> is this same idea, built for martial arts — styles, kata, techniques, terminology, and syllabi in depth. The combat pages here cover the sport; the Dojo covers the tradition.</p>
        </div>
        <div class="callout callout--plain">
          <p><strong>This is a wiki at heart.</strong> Sport belongs to everyone who plays it, so the reference should grow from your corrections too — send notes to <a href="{EDITORS_EMAIL}">the editors</a> and they'll be folded in.</p>
        </div>
      </div>
    </section>
"""
    return head + body + footer()


# ---------------------------------------------------------------- A–Z page

def build_az(pool):
    sports = sorted([s for s in pool if s["category"] != "domains"], key=lambda x: x["name"].split(" (")[0].lower())
    domains = sorted([s for s in pool if s["category"] == "domains"], key=lambda x: x["name"].lower())

    letters = {}
    for s in sports:
        first = s["name"].split(" (")[0][:1].upper()
        if not first.isalpha():
            first = "#"
        letters.setdefault(first, []).append(s)

    blocks = []
    for letter in sorted(letters):
        lis = "".join(
            f"<li><a href=\"sports/{s['slug']}.html\">{esc(s['name'].split(' (')[0])}</a>"
            f"<span class=\"cat-name\">{esc(CATEGORIES[s['category']]['name'])}</span></li>"
            for s in letters[letter]
        )
        blocks.append(f'<div class="letter-block" data-letter="{letter}"><h2>{letter}</h2><ul>{lis}</ul></div>')

    domain_lis = "".join(
        f"<li><a href=\"domains/{s['slug']}.html\">{esc(s['name'])}</a></li>" for s in domains
    )

    head = header(
        title="Sports A–Z",
        desc="Every sport in The Open Arena, from A to Z — ball games, combat arts, endurance, precision, and more.",
        prefix="",
        current="az",
    )
    body = f"""    <section class="page-hero">
      <div class="container">
        <h1>Sports A–Z</h1>
        <p class="lede">{len(sports)} sports and {len(domains)} training domains — the whole arena on one index. Training domains are listed at the bottom.</p>
      </div>
    </section>
    <section class="section-tight">
      <div class="container">
        {''.join(blocks)}
        <div class="letter-block">
          <h2>Training domains</h2>
          <ul>{domain_lis}</ul>
        </div>
      </div>
    </section>
"""
    return head + body + footer()


# ---------------------------------------------------------------- search

def build_search_index(pool) -> str:
    entries = []
    for s in pool:
        is_domain = s["category"] == "domains"
        href = f"{'domains/' if is_domain else 'sports/'}{s['slug']}.html"
        keywords = " ".join(
            [s["name"], s.get("slug", ""), s.get("tagline", ""), s.get("origin", "")]
            + s.get("tags", [])
            + [t for t, _ in s.get("glossary", [])]
            + [n for n, _ in s.get("legends", [])]
            + [n for n, _ in s.get("formats", [])]
            + [n for n, _ in s.get("events", [])]
        ).lower()
        entries.append({
            "t": s["name"].split(" (")[0],
            "full": s["name"],
            "u": href,
            "c": CATEGORIES[s["category"]]["name"],
            "d": s["tagline"],
            "k": keywords,
        })
    return "window.ARENA_INDEX = " + json.dumps(entries, ensure_ascii=False) + ";\n"


def build_search_page(pool):
    head = header(
        title="Search",
        desc="Search every page of The Open Arena — sports, families, terms, and legends.",
        prefix="",
        current="search",
        body_class="search-page",
    )
    body = f"""    <section class="page-hero">
      <div class="container">
        <h1>Search the arena</h1>
        <p class="lede">Names, terms, legends, competitions — try “nutmeg”, “Nadia”, “everest”, or “zone 2”.</p>
      </div>
    </section>
    <section class="section-tight">
      <div class="container">
        <form class="searchbox-big" role="search">
          <input type="search" id="q" placeholder="Search {len(pool)} pages…" aria-label="Search the library">
          <button type="submit">Search</button>
        </form>
        <p class="result-count" id="count"></p>
        <div id="results"></div>
      </div>
    </section>
    <script src="assets/js/search-index.js"></script>
    <script>
      (function () {{
        var index = window.ARENA_INDEX || [];
        var box = document.getElementById('q');
        var out = document.getElementById('results');
        var count = document.getElementById('count');

        function render(q) {{
          q = (q || '').trim().toLowerCase();
          out.innerHTML = '';
          if (!q) {{ count.textContent = index.length + ' pages indexed — type to search.'; return; }}
          var words = q.split(/\\s+/);
          var hits = index.filter(function (e) {{
            var hay = (e.t + ' ' + e.full + ' ' + e.c + ' ' + e.d + ' ' + e.k).toLowerCase();
            return words.every(function (w) {{ return hay.indexOf(w) !== -1; }});
          }});
          count.textContent = hits.length + ' result' + (hits.length === 1 ? '' : 's') + ' for “' + q + '”';
          var html = '';
          hits.forEach(function (e) {{
            html += '<a class="result" href="' + e.u + '">'
                 + '<div class="r-title">' + e.t + '</div>'
                 + '<div class="r-cat">' + e.c + '</div>'
                 + '<div class="r-desc">' + e.d + '</div></a>';
          }});
          if (!hits.length) html = '<p class="no-results">Nothing found. Try a broader word — or <a href="index.html#browse">browse the families</a>.</p>';
          out.innerHTML = html;
        }}

        document.querySelector('.searchbox-big').addEventListener('submit', function (ev) {{
          ev.preventDefault();
          render(box.value);
          if (box.value) location.hash = encodeURIComponent(box.value);
        }});
        box.addEventListener('input', function () {{ render(box.value); }});
        var q0 = decodeURIComponent(location.hash.replace(/^#/, ''));
        if (q0) {{ box.value = q0; }}
        render(q0);
      }})();
    </script>
"""
    return head + body + footer()


# ---------------------------------------------------------------- about page

def build_about(pool):
    n = len(pool)
    head = header(
        title="About this library",
        desc="What The Open Arena is, how it was built, and how to make it better.",
        prefix="",
        current="about",
    )
    body = f"""    <section class="page-hero">
      <div class="container">
        <h1>About this library</h1>
        <p class="lede">{BRAND} is a free reference for every sport — {n} pages, one per sport, written to be read between sessions.</p>
      </div>
    </section>
    <section class="section-tight">
      <div class="container">
        <h2>Why it exists</h2>
        <p>Great references exist for a few big sports and almost nobody else. Meanwhile, the person who just signed up for pickleball, the kid who joined the rowing club, and the adult who signed up for their first judo class all have the same questions: what is this, where did it come from, what do I need, and what do I do first? This library answers those questions the same way for every sport it covers.</p>
        <h2>How each page works</h2>
        <p>Every sport page has the same thirteen rooms: at a glance, what it is, history, ways to play, core skills with drills, the rules you actually need, gear, training, the pathway from beginner to elite, the big competitions, legends, a first-week plan, and a glossary. Combat and martial-arts pages link onward to <a href="{OPEN_DOJO_URL}">The Open Dojo</a>, our sister library that goes deep on technique and tradition.</p>
        <h2>How it was built</h2>
        <p>Pure static HTML and CSS — no frameworks, no build step for readers, no tracking. The pages are generated from open data files in the <a href="https://github.com/adineo-cmd/the-open-arena">repository</a>; correcting an entry is a one-line edit.</p>
        <h2>Contributing</h2>
        <p>Sport knowledge is tribal and wider than any single writing team. If a fact is wrong, a legend is missing, or your sport is not here at all, send a note to <a href="{EDITORS_EMAIL}">the editors</a> or open an issue in the repository. Corrections are folded in the way training plans are — steadily, and with thanks.</p>
        <div class="callout callout--safety">
          <h3>A note on safety</h3>
          <p>Nothing here replaces a qualified coach watching you move. Use these pages to walk in prepared, not to skip instruction — especially in combat sports, water, heights, and anything involving loads or speed.</p>
        </div>
      </div>
    </section>
"""
    return head + body + footer()


# ---------------------------------------------------------------- misc files

def build_404():
    return header(title="Page not found", desc="That page is not in the arena.", prefix="",
                  current="") + """    <section class="page-hero">
      <div class="container">
        <h1>Off the field.</h1>
        <p class="lede">That page doesn't exist — try the <a href="index.html">home page</a>, the <a href="sports-a-z.html">A–Z index</a>, or <a href="search.html">search</a>.</p>
      </div>
    </section>
""" + footer()


def build_sitemap(all_pages):
    urls = []
    for rel in all_pages:
        urls.append(f"  <url><loc>{SITE_URL}{rel}</loc></url>")
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls) + "\n</urlset>\n")


ROBOTS = "User-agent: *\nAllow: /\nSitemap: " + SITE_URL + "sitemap.xml\n"


# ---------------------------------------------------------------- main

def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    (OUT / "sports").mkdir(parents=True)
    (OUT / "domains").mkdir(parents=True)
    (OUT / "assets" / "css").mkdir(parents=True)
    (OUT / "assets" / "js").mkdir(parents=True)

    # copy static assets
    shutil.copy2(ROOT / "assets" / "css" / "site.css", OUT / "assets" / "css" / "site.css")

    entries = load_sports()
    problems, seen = validate(entries)
    for p in problems:
        print("WARN:", p)
    pool = [s for s, _ in entries]
    pool_by_slug.clear()
    for s in pool:
        pool_by_slug[s["slug"]] = s

    # sport + domain pages
    written = ["index.html", "sports-a-z.html", "search.html", "about.html", "404.html"]
    for s in pool:
        is_domain = s["category"] == "domains"
        path = (OUT / "domains" if is_domain else OUT / "sports") / f"{s['slug']}.html"
        path.write_text(sport_page(s, pool, seen), encoding="utf-8")
        written.append(f"{'domains/' if is_domain else 'sports/'}{s['slug']}.html")

    # hub + index pages
    (OUT / "index.html").write_text(build_index(pool), encoding="utf-8")
    (OUT / "sports-a-z.html").write_text(build_az(pool), encoding="utf-8")
    (OUT / "search.html").write_text(build_search_page(pool), encoding="utf-8")
    (OUT / "about.html").write_text(build_about(pool), encoding="utf-8")
    (OUT / "404.html").write_text(build_404(), encoding="utf-8")

    # search index
    (OUT / "assets" / "js" / "search-index.js").write_text(build_search_index(pool), encoding="utf-8")

    # sitemap + robots
    (OUT / "sitemap.xml").write_text(build_sitemap(written), encoding="utf-8")
    (OUT / "robots.txt").write_text(ROBOTS, encoding="utf-8")

    print(f"Built {len(written)} pages into site/ ({len([w for w in written if w.startswith('sports/')] )} sports, "
          f"{len([w for w in written if w.startswith('domains/')] )} domains).")
    if problems:
        print(f"{len(problems)} validation warnings — fix before publishing.")


pool_by_slug = {}

if __name__ == "__main__":
    main()
