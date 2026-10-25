# The Open Arena — sport data schema

Each sport is ONE JSON object in a group file (an array of objects).
Group files: `data/groups/<group>.json` → `[ { ...sport... }, ... ]`

**Rules**
- Valid JSON (UTF-8). No trailing commas. Validate with `python3 -m json.tool <file>`.
- Strings are PLAIN TEXT. No HTML, no markdown, no emoji inside strings (the `glyph` field is the only emoji).
- Every field listed below must be present (empty arrays are not allowed — write real content).
- FACTS MUST BE REAL: real years, real governing bodies, real people, real competitions. No invented names.
- Write for a smart beginner + a current athlete. Concrete, warm, no fluff. Style = the sibling site "The Open Dojo": crisp prose, em dashes, occasional dry wit.

## Professional-guide standard (non-negotiable, for every sport)

- **Every sport — global giant or local gem — gets the FULL treatment**: all 22 fields, full depth. Never compress niche or regional sports into stubs. A kabaddi page must be as professional as a soccer page.
- Write like a professional publication: a national governing body's athlete handbook crossed with a quality encyclopedia. Precise terminology, correct technique names, real training science, real competitive structures.
- `skills`: use the sport's real technical vocabulary (boxing: jab, cross, hook, uppercut, footwork — never "punching"; rowing: catch, drive, finish, recovery). The "how to train it" column carries real prescriptions: sets, reps, durations, targets.
- `training`: name real methods and energy systems (aerobic base, anaerobic alactic power, lactate threshold, periodization) and real injury-prevention exercises (Nordic curls, Copenhagen planks, FMS-style screens).
- `rules`: the actual competitive rules with real measurements — court/pitch dimensions, scoring values, time periods, weight classes, equipment specs.
- `history`, `events`, `legends`: verified real facts — dates, federations, competitions, athletes. Uncertain details are omitted rather than invented.
- Zero filler. Every sentence must teach something a coach would say. Ban: "practicing regularly will improve your game", "this sport is fun for all ages", and every sentence of their species.

## Fields

| field | type | what it is |
|---|---|---|
| `slug` | string | EXACTLY the slug assigned to you (used in URLs) |
| `name` | string | Display name, e.g. "Soccer (Association Football)" |
| `category` | string | Category id assigned to you (e.g. "team-ball") |
| `glyph` | string | ONE emoji that identifies the sport, e.g. "⚽" |
| `tagline` | string | One vivid line for cards + search (~8-14 words) |
| `origin` | string | Short origin label, e.g. "England · 1863" |
| `tags` | string[] | 3-4 short labels, e.g. ["Team sport","Olympic","World Cup"] |
| `overview` | string[] | EXACTLY 3 paragraphs (each 2-4 sentences): what it is; why people love it / cultural weight; what a newcomer should know |
| `facts` | [string,string][] | 6-8 rows for the "At a glance" table (Origin, Governing body, Team size / format, Match/duration, Playing area, Olympic status, First world championship, Global reach...) |
| `history` | [string,string][] | 5-7 rows [year-or-era, one-sentence milestone], roughly chronological |
| `formats` | [string,string][] | 4-6 rows [format/discipline name, description] — variants, disciplines, editions |
| `skills` | [string,string,string][] | 6-8 rows [skill, what it is, how to train it] |
| `rules` | string[] | 5-7 bullets — the rules a newcomer must know |
| `equipment` | [string,string][] | 5-7 rows [item, description incl. rough cost tier] |
| `training` | string[] | 4-6 bullets — conditioning & practice specific to this sport (energy systems, strength, injury prevention, skill reps) |
| `pathway` | [string,string][] | 4-5 rows [stage, what it looks like] — first touch → elite |
| `events` | [string,string][] | 4-6 rows [competition, one-line description incl. cadence] |
| `legends` | [string,string][] | 4-5 rows [name, who they are/why they matter] |
| `getting_started` | string[] | 5-7 bullets, concrete first-30-days advice |
| `glossary` | [string,string][] | 8-10 rows [term, one-line definition] |
| `related` | string[] | 3-5 slugs FROM THE MASTER SLUG LIST (exact slugs) |
| `crosslink` | boolean | true ONLY for combat sports (boxing, wrestling, judo, brazilian-jiu-jitsu, karate, taekwondo, muay-thai, kickboxing, mixed-martial-arts, fencing, sumo, sambo, kendo, capoeira) |

## Master slug list (use these EXACT slugs in `related`)

team-ball: soccer, basketball, cricket, baseball, softball, rugby-union, rugby-league, american-football, flag-football, touch-rugby, field-hockey, ice-hockey, lacrosse, volleyball, beach-volleyball, handball, netball, gaelic-football, hurling, australian-rules-football, ultimate-frisbee, futsal, beach-soccer, dodgeball, kabaddi, sepak-takraw, floorball, bandy, korfball, polo, roller-derby, water-polo

racket: tennis, badminton, table-tennis, squash, racquetball, padel, pickleball, jai-alai

combat: boxing, wrestling, judo, brazilian-jiu-jitsu, karate, taekwondo, muay-thai, kickboxing, mixed-martial-arts, fencing, sumo, sambo, kendo

athletics: track-and-field, marathon, cross-country-running, race-walking, ultrarunning, triathlon, obstacle-course-racing, adventure-racing, modern-pentathlon

water: swimming, open-water-swimming, artistic-swimming, diving, rowing, canoe-sprint, canoe-slalom, dragon-boat-racing, sailing, surfing, windsurfing, kitesurfing, wakeboarding, freediving

winter: alpine-skiing, cross-country-skiing, freestyle-skiing, ski-jumping, nordic-combined, snowboarding, biathlon, figure-skating, speed-skating, short-track-speed-skating, bobsleigh, skeleton, luge, curling

cycling-motor: road-cycling, track-cycling, mountain-biking, cyclocross, bmx-racing, bmx-freestyle, formula-1, rallying, motogp, motocross, karting

strength: powerlifting, olympic-weightlifting, bodybuilding, strongman, crossfit, arm-wrestling, tug-of-war

gymnastics-aesthetic: artistic-gymnastics, rhythmic-gymnastics, trampoline-gymnastics, breaking, parkour, cheerleading, skateboarding, dancesport, capoeira

precision: archery, shooting-sport, golf, darts, snooker, pool-billiards, tenpin-bowling, disc-golf, petanque

outdoor-air: sport-climbing, bouldering, mountaineering, orienteering, paragliding, skydiving, drone-racing

equestrian: horse-racing, show-jumping, dressage, eventing, rodeo

mind: chess, go, bridge, esports
