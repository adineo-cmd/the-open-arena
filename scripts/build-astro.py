"""Build the site through Astro.

Runs the existing generator (build.py -> site/), then adapts its output
into the Astro project: pages become src/raw/** + src/pages/** routes and
assets land in public/**. Root-absolute refs are rewritten relative so
project Pages URLs resolve. Regenerates everything on each build.
"""
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = os.path.join(ROOT, "site")
RAW = os.path.join(ROOT, "src", "raw")
PAGES = os.path.join(ROOT, "src", "pages")
PUBLIC = os.path.join(ROOT, "public")

PAGE_TEMPLATE = '''---
import Layout from "{rel}layouts/Layout.astro";
import raw from "{rel}raw/{path}?raw";
const head = (raw.match(/<head[^>]*>([\\s\\S]*?)<\\/head>/i)?.[1] ?? "")
  .replace(/<title[\\s\\S]*?<\\/title>/i, "");
const body = raw.match(/<body[^>]*>([\\s\\S]*?)<\\/body>/i)?.[1] ?? raw;
const title = raw.match(/<title[^>]*>([\\s\\S]*?)<\\/title>/i)?.[1]?.trim() ?? "Page";
---
<Layout title={title} head={head} body={body} />
'''


def main():
    subprocess.run([sys.executable, os.path.join(ROOT, "build.py")], check=True)
    for d in (RAW, PAGES, PUBLIC):
        shutil.rmtree(d, ignore_errors=True)
    count = 0
    for dirpath, _, filenames in os.walk(SITE):
        for name in filenames:
            src = os.path.join(dirpath, name)
            rel = os.path.relpath(src, SITE)
            dest_root = RAW if rel.endswith(".html") else PUBLIC
            dest = os.path.join(dest_root, rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            if rel.endswith(".html"):
                html = open(src, encoding="utf-8", errors="replace").read()
                html = re.sub(r'(href|src)="/(?!/)', r'\1="', html)
                open(dest, "w", encoding="utf-8").write(html)
                page_rel = rel[:-5] + ".astro"
                page = os.path.join(PAGES, page_rel)
                os.makedirs(os.path.dirname(page), exist_ok=True)
                depth = rel.count("/")
                open(page, "w").write(
                    PAGE_TEMPLATE.replace("{rel}", "../" * (depth + 1))
                    .replace("{path}", rel))
                count += 1
            else:
                shutil.copy2(src, dest)
    print(f"astro adapter: {count} pages + assets ready")


if __name__ == "__main__":
    main()
