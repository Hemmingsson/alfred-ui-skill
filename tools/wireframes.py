#!/usr/bin/env python3
"""Draw the README's wireframes: one small SVG per layout and component, plus the runtime flow.

Usage: python3 tools/wireframes.py   (writes docs/wireframes/*.svg; takes no arguments)
"""

import math
import sys
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent.parent / "docs" / "wireframes"
W, H = 360, 200
INK, MUTED, LINE, FILL, CARD = "#1d1d1f", "#8e8e93", "#c7c7cc", "#f2f2f7", "#ffffff"
HIGHLIGHT = "#e5e5ea"
FONT = "-apple-system, BlinkMacSystemFont, 'SF Pro Text', Helvetica, Arial, sans-serif"


def rect(x, y, w, h, fill=FILL, stroke=LINE, r=6, dash=False, sw=1.2):
    d = ' stroke-dasharray="5 4"' if dash else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>'


def text(x, y, s, size=13, fill=INK, anchor="start", weight=400):
    return f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" font-weight="{weight}" fill="{fill}" text-anchor="{anchor}">{escape(s)}</text>'


def box(x, y, w, h, label, fill=FILL, size=12, colour=INK, **kw):
    return rect(x, y, w, h, fill=fill, **kw) + text(x + w / 2, y + h / 2 + size * 0.35, label, size, colour, "middle")


def line(x1, y1, x2, y2, stroke=LINE, sw=1.2):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round"/>'


def svg(body, w=W, h=H):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">'
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="14" fill="{CARD}" stroke="#e5e5ea"/>{body}</svg>\n'
    )


# --------------------------------------------------------------------------- layouts

def stack():
    b = ""
    for i, (label, fill) in enumerate((("1st child (bottom)", FILL), ("2nd", "#e5e5ea"), ("3rd child (top)", CARD))):
        b += rect(40 + i * 22, 30 + i * 22, 236, 110, fill=fill)
        b += text(52 + i * 22, 50 + i * 22, label, 12, MUTED if i < 2 else INK)
    return b


def border():
    return (
        box(20, 20, 320, 30, "top")
        + box(20, 58, 70, 84, "left")
        + box(98, 58, 164, 84, "centre", fill=HIGHLIGHT, stroke=INK)
        + box(270, 58, 70, 84, "right")
        + box(20, 150, 320, 30, "bottom")
    )


def grid():
    b = ""
    for i in range(6):
        b += box(20 + (i % 3) * 108, 24 + (i // 3) * 80, 100, 72, str(i + 1), size=16, colour=MUTED)
    return b


def inline():
    b = text(20, 34, "horizontal", 11, MUTED)
    for i, w in enumerate((70, 110, 60)):
        b += box(20 + sum((70, 110, 60)[:i]) + i * 8, 44, w, 34, "ABC"[i])
    b += text(20, 112, "vertical", 11, MUTED)
    for i in range(2):
        b += box(20, 122 + i * 34, 150, 28, "AB"[i])
    return b


def form():
    b = ""
    for i, (label, value) in enumerate((("Name", "Example"), ("Domain", "example.com"), ("", "Save"))):
        y = 26 + i * 52
        if label:
            b += text(96, y + 22, label + ":", 13, INK, "end")
            b += rect(110, y, 230, 34, fill=CARD) + text(122, y + 22, value, 13, MUTED)
        else:
            b += box(110, y, 90, 34, value, fill=CARD, size=13)
            b += text(96, y + 22, "{ }", 12, MUTED, "end")
    return b


def flex():
    return (
        box(20, 20, 210, 70, "colspan 2", fill=HIGHLIGHT, stroke=INK)
        + box(238, 20, 102, 70, "1 × 1")
        + box(20, 98, 102, 82, "rowweight 2")
        + box(130, 98, 100, 82, "1 × 1")
        + box(238, 98, 102, 82, "1 × 1")
    )


# --------------------------------------------------------------------------- components

def view():
    return (
        rect(20, 20, 320, 160, fill=CARD, dash=True)
        + text(32, 40, "view  ·  layout: inline", 11, MUTED)
        + box(36, 56, 130, 40, "label")
        + box(176, 56, 148, 40, "button")
        + box(36, 106, 288, 56, "another view")
    )


def label():
    return (
        text(30, 78, "Title", 22, INK, weight=600)
        + text(30, 106, "Secondary text", 14, MUTED)
    )


def button():
    return (
        rect(40, 48, 130, 38, fill=CARD, r=8)
        + text(105, 72, "Cancel", 14, INK, "middle")
        + rect(190, 48, 130, 38, fill=INK, stroke=INK, r=8)
        + text(255, 72, "Save", 14, CARD, "middle")
        + rect(40, 112, 38, 38, fill=CARD, r=8)
        + f'<path d="M53 131 h12 M59 125 v12" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>'
        + rect(92, 112, 130, 38, fill=CARD, r=8)
        + f'<path d="M108 131 a6 6 0 1 0 12 0 a6 6 0 1 0 -12 0 M119 136 l4 4" fill="none" stroke="{INK}" stroke-width="1.8" stroke-linecap="round"/>'
        + text(166, 136, "Search", 14, INK, "middle")
    )


def checkbox():
    b = ""
    for i, (on, s) in enumerate(((True, "Show hidden files"), (False, "Remember my choice"))):
        y = 68 + i * 46
        b += rect(100, y, 20, 20, fill=INK if on else CARD, stroke=INK if on else LINE, r=5)
        if on:
            b += f'<path d="M105 {y + 10} l4 4 l7 -8" fill="none" stroke="{CARD}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>'
        b += text(132, y + 15, s, 14)
    return b


def picker():
    x = 95
    return (
        rect(x, 30, 170, 34, fill=CARD, r=7)
        + text(x + 14, 52, "Medium", 14)
        + text(x + 156, 52, "⌄", 14, MUTED, "end")
        + rect(x, 70, 170, 104, fill=CARD, r=7)
        + rect(x + 6, 76, 158, 28, fill=INK, stroke=INK, r=5)
        + text(x + 18, 95, "Medium", 13, CARD)
        + text(x + 18, 127, "Small", 13)
        + text(x + 18, 159, "Large", 13)
    )


def field(content, colour):
    return rect(30, 70, 300, 40, fill=CARD, stroke=INK, r=8, sw=1.6) + text(46, 96, content, 15, colour)


def textfield():
    return field("Search", MUTED)


def passwordfield():
    return field("••••••••••", INK)


def textarea():
    b = rect(30, 24, 300, 152, fill=CARD, r=8)
    for i, w in enumerate((250, 270, 210, 260, 140)):
        b += rect(46, 42 + i * 26, w, 8, fill="#e5e5ea", stroke="none", r=4)
    return b


def markdownarea():
    return (
        rect(30, 20, 300, 160, fill=CARD, r=8)
        + text(46, 50, "Notes", 18, INK, weight=700)
        + text(46, 80, "•  First item", 13)
        + text(46, 102, "•  Second item", 13)
        + text(46, 132, "A link", 13, INK)
    )


def progress():
    cx, cy, r = 180, 132, 28
    end = (cx + r * math.sin(2 * math.pi * 0.6), cy - r * math.cos(2 * math.pi * 0.6))
    return (
        text(40, 40, "linear", 11, MUTED)
        + rect(40, 52, 280, 8, fill="#e5e5ea", stroke="none", r=4)
        + rect(40, 52, 168, 8, fill=INK, stroke="none", r=4)
        + text(40, 98, "round", 11, MUTED)
        + f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="#e5e5ea" stroke-width="6"/>'
        + f'<path d="M{cx} {cy - r} A{r} {r} 0 1 1 {end[0]:.1f} {end[1]:.1f}" fill="none" stroke="{INK}" stroke-width="6" stroke-linecap="round"/>'
        + text(cx, cy + 4, "60%", 11, INK, "middle")
    )


def imageview():
    return (
        rect(80, 24, 200, 152, fill=FILL, r=10)
        + '<circle cx="230" cy="62" r="14" fill="#c7c7cc"/>'
        + '<path d="M80 150 L140 90 L190 135 L215 112 L280 160 L280 166 Q280 176 270 176 L90 176 Q80 176 80 166 Z" fill="#c7c7cc"/>'
    )


def dataview():
    b = ""
    rows = (("example.com", "Main site", True), ("docs.example.com", "Documentation", False),
            ("blog.example.com", "Blog", False))
    for i, (title, sub, on) in enumerate(rows):
        y = 18 + i * 56
        if on:
            b += rect(16, y, 328, 50, fill=INK, stroke=INK, r=8)
        b += rect(26, y + 9, 52, 32, fill="#e5e5ea" if not on else "#636366", stroke="none", r=4)
        b += text(90, y + 22, title, 13, CARD if on else INK, weight=600)
        b += text(90, y + 39, sub, 12, CARD if on else MUTED)
    return b


def webkitview():
    return (
        rect(20, 20, 320, 160, fill=CARD, r=8)
        + rect(20, 20, 320, 26, fill=FILL, r=8)
        + text(34, 37, "https://example.com", 11, MUTED)
        + rect(40, 62, 120, 12, fill="#e5e5ea", stroke="none", r=3)
        + rect(40, 84, 280, 60, fill=HIGHLIGHT, stroke="none", r=6)
        + rect(40, 154, 130, 10, fill="#e5e5ea", stroke="none", r=3)
        + rect(190, 154, 130, 10, fill="#e5e5ea", stroke="none", r=3)
    )


# --------------------------------------------------------------------------- runtime

def runtime():
    def arrow(x1, y1, x2, y2, label="", dy=-8):
        head = f'<path d="M{x2} {y2} l-7 -4 v8 z" fill="{MUTED}"/>' if x2 > x1 else f'<path d="M{x2} {y2} l7 -4 v8 z" fill="{MUTED}"/>'
        return line(x1, y1, x2, y2, MUTED, 1.4) + head + (text((x1 + x2) / 2, y1 + dy, label, 11, MUTED, "middle") if label else "")

    return (
        box(20, 70, 120, 60, "Keyword", fill=CARD, size=13)
        + box(220, 50, 200, 100, "", fill=HIGHLIGHT, stroke=INK)
        + text(320, 92, "Alfred UI window", 14, INK, "middle", 600)
        + text(320, 112, "ui.json", 12, MUTED, "middle")
        + box(500, 70, 140, 60, "Next objects", fill=CARD, size=13)
        + box(245, 200, 150, 44, "Your script", fill=CARD, size=13)
        + arrow(140, 100, 218, 100, "argument")
        + arrow(422, 100, 498, 100, "finish")
        + line(300, 152, 300, 198, MUTED, 1.4) + f'<path d="M300 198 l-4 -7 h8 z" fill="{MUTED}"/>'
        + line(340, 198, 340, 152, MUTED, 1.4) + f'<path d="M340 152 l-4 7 h8 z" fill="{MUTED}"/>'
        + text(292, 180, "event", 11, MUTED, "end")
        + text(348, 180, "JSON: update the view", 11, MUTED)
    )


def main():
    if sys.argv[1:]:
        help_asked = sys.argv[1:] in (["-h"], ["--help"])
        print(__doc__.strip(), file=sys.stdout if help_asked else sys.stderr)
        sys.exit(0 if help_asked else 2)
    OUT.mkdir(parents=True, exist_ok=True)
    drawings = {f.__name__: f for f in (stack, border, grid, inline, form, flex, view, label, button, checkbox, picker,
                                         textfield, passwordfield, textarea, markdownarea, progress, imageview,
                                         dataview, webkitview)}
    for name, draw in drawings.items():
        (OUT / f"{name}.svg").write_text(svg(draw()))
    (OUT / "runtime.svg").write_text(svg(runtime(), 660, 264))
    print(f"wrote {len(drawings) + 1} files to {OUT}")


if __name__ == "__main__":
    main()
