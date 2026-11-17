#!/usr/bin/env python3
"""Turns the emulator's screenshots into the site's images: python3 tools/make_screens.py <folder>
where <folder> has nl/, fr/ and en/ with 2-overview.png, 3-advice.png and 4-details.png (the
"Screenshots" workflow's screenshot-images branch). Writes screens/<code>/<name>.webp: no status bar, 460 px wide."""
import os, sys
from PIL import Image

NAMES = (("2-overview", "overview"), ("3-advice", "advice"), ("4-details", "details"))
src = sys.argv[1]
for code in ("nl", "fr", "en"):
    os.makedirs(f"screens/{code}", exist_ok=True)
    for source, name in NAMES:
        im = Image.open(f"{src}/{code}/{source}.png").convert("RGB").crop((0, 125, 1080, 2400))
        im = im.resize((460, round(460 * im.height / im.width)), Image.LANCZOS)
        im.save(f"screens/{code}/{name}.webp", "WEBP", quality=84, method=6)
        print(code, name, im.size, os.path.getsize(f"screens/{code}/{name}.webp"))
