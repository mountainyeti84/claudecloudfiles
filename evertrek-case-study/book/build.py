"""Assemble The Meta Growth Gap from its parts.
Writes meta-growth-gap.html (local fonts, for PDF) and, if given an output dir,
an artifact version that uses Google Fonts and has no document skeleton."""
import pathlib, re, sys
here = pathlib.Path(__file__).parent
parts = sorted(here.glob("0*.html"))
html = "".join(p.read_text() for p in parts)
local = html.replace("<!--FONTS-->", '<link rel="stylesheet" href="fonts/fonts.css">')
(here.parent / "meta-growth-gap.html").write_text(local)
if len(sys.argv) > 1:
    gf = ('<link rel="preconnect" href="https://fonts.googleapis.com">\n'
          '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600'
          '&family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,500&display=swap">')
    art = html.replace("<!--FONTS-->", gf)
    art = re.sub(r"<!doctype html>\s*<html[^>]*>\s*<head>\s*", "", art)
    art = re.sub(r'<meta charset="utf-8">\s*<meta name="viewport"[^>]*>\s*', "", art)
    art = art.replace("</head>\n<body>", "").replace("</body>\n</html>", "")
    out = pathlib.Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    (out / "meta-growth-gap.html").write_text(art)
