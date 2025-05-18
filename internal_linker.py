#!/usr/bin/env python3
"""Simple internal linker – scans content directory and adds related links."""
import pathlib, re
content_dir = pathlib.Path("seo_site/content")
files = list(content_dir.glob("*.md"))
lookup = {f.stem.split('-vs-')[0]: f.name for f in files}
for f in files:
    txt = f.read_text(encoding="utf-8")
    team = f.stem.split('-vs-')[0]
    links = [f"[See all {k} matches]({v})" for k, v in lookup.items() if k != team][:5]
    txt += "\n\n---\n" + "\n".join(links)
    f.write_text(txt, encoding="utf-8")
print("Internal links appended.")
