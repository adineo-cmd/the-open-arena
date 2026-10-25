# The Open Arena 🏟

**A free reference library for every sport** — the sister site of [The Open Dojo](https://github.com/adineo-cmd/the-open-dojo) (the free martial-arts library).

Where The Open Dojo answers "what do I need to know about the martial arts?", The Open Arena asks the same question for **every sport on Earth**: ball games and barbell sports, mind games and mountain sports, the schoolyard and the stadium.

**The live site is deployed to the `gh-pages` branch by GitHub Actions on every push to `main` — enable GitHub Pages (Settings → Pages → Source: `gh-pages` branch, `/` root) to publish it.**

## What's inside

- **A dedicated page per sport** — 119+ sports, each with the same thirteen rooms:
  at a glance · what it is · history · ways to play · core skills (with drills) ·
  the rules you actually need · gear guide · training · the pathway ·
  major competitions · legends · a first-week plan · glossary.
- **13 families of sport** — Ball & Team, Racket & Net, Combat, Athletics & Endurance,
  Water, Winter, Cycling & Motorsport, Strength, Gymnastics & Aesthetic,
  Precision & Target, Outdoor & Air, Equestrian, Mind & Table.
- **11 training domains** — the non-sport disciplines that build athletes:
  strength & conditioning, functional fitness, endurance, speed, plyometrics,
  mobility, nutrition, rucking, youth sports, women's training, tactical fitness.
- **Hub + A–Z index + instant client-side search** across every page.

## How it works

```
data/
  examples/soccer.json    <- the exemplar every sport follows
  groups/*.json           <- all sport + domain content (JSON)
build.py                  <- generates site/ from data (python3 build.py)
assets/css/site.css       <- the single stylesheet
.github/workflows/        <- builds + deploys the site on every push
site/                     <- generated output (on the gh-pages branch)
```

No frameworks. No JavaScript framework, no CDN, no tracking. The built site is
plain HTML + CSS with one tiny vanilla-JS search.

### Rebuild

```bash
python3 build.py
```

The builder also validates the data (schema, duplicate slugs, broken related
links) and fails loudly with warnings.

### Edit a page

Find the sport's JSON in `data/groups/`, fix the fact, rerun `build.py`, commit —
GitHub Actions rebuilds and redeploys automatically. Corrections are the way this
library grows - like kata, repetition with attention.

## Content notes

- Combat/martial-arts pages carry a callout linking to **The Open Dojo** for the
  deeper tradition (styles, kata, techniques, terminology).
- Coaching-platform category lists were mapped as follows: real sports got
  dedicated pages (Powerlifting, Rugby, Water Polo, Roller Derby, Gaelic
  Football, ...); training disciplines became domain pages (Nutrition, Mobility,
  Plyometrics, Speed, Endurance, Rucking, Strength & Conditioning, Women's
  Training, Youth Sports, Tactical/First Responders).
- Facts were written with care but by humans+AI; sport knowledge is tribal -
  if something is wrong, send a correction (see the site footer).

## License

Original reference content for the common good. Cite the arena, train safe.
