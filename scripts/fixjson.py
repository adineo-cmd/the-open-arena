#!/usr/bin/env python3
"""Repair common JSON authoring slips in data/group files, then validate.

Disease patterns (from muscle-memory list endings):
  A) plain item ends '"]' followed by '},'   ->  item '"', then '],', skip '}'
  B) plain item ends '"]' followed by '],'   ->  strip the stray ']'
  C) row starts with '["' but missing ']'    ->  re-append ']'
  D) '},' line directly before a property    ->  drop it (double-close)
  E) doubled '],' lines                      ->  keep one
"""
import json
import pathlib
import sys

ARTIFACTS = ['? —', '(avoid)', ' — no —', 'обход', '导航']


def fix(path: pathlib.Path) -> int:
    lines = path.read_text(encoding='utf-8').split('\n')
    out = []
    changed = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        nxt = lines[i + 1].strip() if i + 1 < len(lines) else ''
        stripped = line.rstrip()
        ls = stripped.lstrip()

        # C: unterminated pair/triple row
        if ls.startswith('["') and stripped.endswith('"') and not stripped.endswith('"]'):
            out.append(stripped + ']')
            changed += 1
            i += 1
            continue

        # A: plain item '"]' + '},'  -> item + '],'
        if ls.startswith('"') and stripped.endswith('"]') and nxt == '},':
            out.append(stripped[:-1])
            out.append('    ],')
            changed += 1
            i += 2
            continue

        # B: plain item '"]' + '],'  -> strip stray ]
        if ls.startswith('"') and stripped.endswith('"]') and nxt.startswith('],'):
            out.append(stripped[:-1])
            changed += 1
            i += 1
            continue

        # D: '},' immediately before a property line, where previous emitted line already closes
        if stripped == '},' and nxt.startswith('"') and out and out[-1].rstrip().endswith('],'):
            changed += 1
            i += 1
            continue

        out.append(line)
        i += 1

    # E: collapse doubled '],'
    final = []
    for line in out:
        if line.strip() == '],' and final and final[-1].strip() == '],':
            changed += 1
            continue
        final.append(line)

    if changed:
        path.write_text('\n'.join(final), encoding='utf-8')
    return changed


def main():
    ok = True
    for path in sorted(pathlib.Path('data/groups').glob('*.json')) + sorted(pathlib.Path('data/examples').glob('*.json')):
        n = fix(path)
        n2 = fix(path)  # second pass catches cascaded patterns
        try:
            d = json.load(open(path))
            arts = []
            for s in d:
                txt = json.dumps(s, ensure_ascii=False)
                for bad in ARTIFACTS:
                    if bad in txt:
                        arts.append((s.get('slug'), bad))
            note = f' (+{n}+{n2} fixes)' if (n or n2) else ''
            print(f'{path.name}: VALID{note}, {len(d)} entries', '| ARTIFACTS: ' + str(arts) if arts else '')
            if arts:
                ok = False
        except json.JSONDecodeError as e:
            ok = False
            print(f'{path.name}: STILL BROKEN: {e}')
            lines = path.read_text().split('\n')
            ln = e.lineno
            print('\n'.join(f'{j+1}: {l}' for j, l in enumerate(lines[max(0, ln-3):ln+2], start=max(0, ln-3))))
    sys.exit(0 if ok else 1)


if __name__ == '__main__':
    main()
