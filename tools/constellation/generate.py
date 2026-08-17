#!/usr/bin/env python3
"""
Constellation Check — OG report card generator.

Reads a per-case record from content/constellation/{slug}.json, validates it
against the information contract, derives the scoreboard from the star verdicts,
and renders a 1200x630 PNG to public/assets/og/constellation/{slug}.png.

The scoreboard is computed here and never read from the case file: a hand-typed
scoreboard drifts the moment one verdict is edited, and the scoreboard is the
single most quotable thing on the card.

Usage:
    python3 tools/constellation/generate.py            # every case
    python3 tools/constellation/generate.py <slug>     # one case
    python3 tools/constellation/generate.py --check    # validate only, render nothing
"""
import html
import json
import os
import subprocess
import sys
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CASES = os.path.join(ROOT, "content", "constellation")
OUT_DIR = os.path.join(ROOT, "public", "assets", "og", "constellation")
WORK = os.path.join(ROOT, ".cache", "constellation")
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

HERE = os.path.dirname(os.path.abspath(__file__))
GEOM = json.load(open(os.path.join(HERE, "orion-geometry.json")))
STYLE = json.load(open(os.path.join(HERE, "verdict-style.json")))

VERDICTS = ("CONFIRMED", "VIOLATED", "NOT_ENGAGED", "AMBIGUOUS")
FIT_TYPES = ("DIRECT", "EXTENSION")
STAR_ORDER = ["Betelgeuse", "Bellatrix", "Rigel", "Saiph", "Alnitak", "Alnilam", "Mintaka"]


class InvalidCase(Exception):
    pass


def validate(case, path):
    """Enforce the information contract. Every failure is fatal — a card that
    cannot show its own provenance honestly should not be generated at all."""
    for field in ("case_slug", "case_title", "checked_on", "source_url"):
        if not case.get(field):
            raise InvalidCase(f"{path}: missing required field '{field}'")

    if "scoreboard" in case:
        raise InvalidCase(
            f"{path}: 'scoreboard' must not be authored — it is derived from the star verdicts")

    stars = case.get("stars") or []
    if len(stars) != 7:
        raise InvalidCase(f"{path}: expected exactly 7 stars, found {len(stars)}")

    for i, s in enumerate(stars):
        want_n, want_name = i + 1, STAR_ORDER[i]
        if s.get("star_number") != want_n:
            raise InvalidCase(f"{path}: star {i} has star_number {s.get('star_number')}, expected {want_n}")
        if s.get("star_name") != want_name:
            raise InvalidCase(f"{path}: star {want_n} is {s.get('star_name')}, expected {want_name} (fixed order)")
        if s.get("verdict") not in VERDICTS:
            raise InvalidCase(f"{path}: star {want_n} has invalid verdict {s.get('verdict')!r}")

        fit = s.get("fit_type")
        if s["verdict"] == "NOT_ENGAGED":
            if fit is not None:
                raise InvalidCase(f"{path}: star {want_n} is NOT_ENGAGED so fit_type must be null")
        else:
            # A CONFIRMED/VIOLATED/AMBIGUOUS verdict without a fit_type cannot show
            # whether it applied the star's own text or extended its logic — that is
            # silent overclaiming, so it is rejected rather than rendered.
            if fit not in FIT_TYPES:
                raise InvalidCase(
                    f"{path}: star {want_n} is {s['verdict']} and needs a fit_type "
                    f"(DIRECT or EXTENSION), got {fit!r}")

        reason = s.get("reason_short") or ""
        if not reason:
            raise InvalidCase(f"{path}: star {want_n} is missing reason_short")
        if len(reason) > 90:
            raise InvalidCase(f"{path}: star {want_n} reason_short is {len(reason)} chars (max 90)")
    return stars


def scoreboard(stars):
    """Derived, never authored."""
    c = Counter(s["verdict"] for s in stars)
    return {
        "confirmed": c["CONFIRMED"],
        "violated": c["VIOLATED"],
        "not_engaged": c["NOT_ENGAGED"],
        "ambiguous": c["AMBIGUOUS"],
    }


def scoreboard_line(sb):
    return (f"{sb['confirmed']} confirmed · {sb['violated']} violated · "
            f"{sb['not_engaged']} not engaged · {sb['ambiguous']} ambiguous")


def alt_text(case, sb):
    return (f"{case['case_title']} — Constellation Check: {sb['violated']} violated, "
            f"{sb['confirmed']} confirmed, {sb['not_engaged']} not engaged, "
            f"{sb['ambiguous']} ambiguous")


# ------------------------------------------------------------------ rendering

# Constellation panel geometry within the 1200x630 card.
PANEL = {"x": 700, "y": 128, "w": 340, "h": 372}


def star_markup(stars):
    """Plot the seven stars in their true relative Orion arrangement.
    Verdict drives colour; fit_type drives fill — DIRECT solid, EXTENSION hollow."""
    pts = {}
    for s in stars:
        g = GEOM["star_positions"][s["star_name"]]
        pts[s["star_name"]] = (PANEL["x"] + g["x"] * PANEL["w"],
                               PANEL["y"] + g["y"] * PANEL["h"])

    # Faint figure lines: shoulders, belt, legs — so the shape reads as Orion.
    links = [("Betelgeuse", "Bellatrix"), ("Betelgeuse", "Alnitak"), ("Bellatrix", "Mintaka"),
             ("Alnitak", "Alnilam"), ("Alnilam", "Mintaka"),
             ("Alnitak", "Saiph"), ("Mintaka", "Rigel")]
    out = []
    for a, b in links:
        (x1, y1), (x2, y2) = pts[a], pts[b]
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                   f'stroke="{STYLE["muted"]}" stroke-width="1" opacity="0.35"/>')

    for s in stars:
        x, y = pts[s["star_name"]]
        colour = STYLE["verdict_style"][s["verdict"]]["colour"]
        engaged = s["verdict"] != "NOT_ENGAGED"
        r = 11 if engaged else 7
        if s.get("fit_type") == "EXTENSION":
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" '
                       f'stroke="{colour}" stroke-width="3"/>')
        else:
            op = "1" if engaged else "0.75"
            out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{colour}" opacity="{op}"/>')
        out.append(f'<text x="{x:.1f}" y="{y - r - 7:.1f}" text-anchor="middle" '
                   f'font-family="JetBrains Mono, monospace" font-size="11" '
                   f'fill="{STYLE["muted"]}">{s["star_number"]}</text>')
    return "\n".join(out)


def legend_markup(sb):
    """Colour key only. The scoreboard line above carries all four counts, including
    zeroes, so repeating the numbers here would be duplication rather than information."""
    rows, x, y = [], 80, 500
    for key in ("CONFIRMED", "VIOLATED", "NOT_ENGAGED", "AMBIGUOUS"):
        st = STYLE["verdict_style"][key]
        rows.append(f'<circle cx="{x}" cy="{y - 5}" r="6" fill="{st["colour"]}"/>')
        rows.append(f'<text x="{x + 14}" y="{y}" font-family="JetBrains Mono, monospace" '
                    f'font-size="15" fill="{STYLE["muted"]}">{st["label"].lower()}</text>')
        x += 14 + len(st["label"]) * 9 + 30
    return "\n".join(rows)


def engaged_line(stars):
    """Name the stars that actually moved, so a reader can tell which of the seven
    the counts refer to without opening the page."""
    def names(v):
        return [s["star_name"] for s in stars if s["verdict"] == v]
    parts = []
    for key in ("VIOLATED", "CONFIRMED", "AMBIGUOUS"):
        n = names(key)
        if n:
            # commas within a group, em dash between groups: SVG collapses runs of
            # whitespace, so the separator has to be a glyph rather than spacing
            parts.append(f'{STYLE["verdict_style"][key]["label"]}: ' + ", ".join(n))
    return " — ".join(parts)


def build_svg(case, stars, sb):
    title = html.escape(case["case_title"])
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="{STYLE['ground']}"/>

  <text x="80" y="92" font-family="JetBrains Mono, monospace" font-size="22"
        letter-spacing="6" fill="{STYLE['accent']}">CONSTELLATION CHECK</text>
  <rect x="80" y="116" width="120" height="2" fill="{STYLE['accent']}"/>

  <text x="80" y="215" font-family="Playfair Display, Georgia, serif" font-weight="700"
        font-size="66" fill="{STYLE['ink']}">{title}</text>

  <text x="80" y="272" font-family="Inter, system-ui, sans-serif" font-size="23"
        fill="{STYLE['muted']}">Checked against the seven stars</text>

  <text x="80" y="352" font-family="JetBrains Mono, monospace" font-size="21"
        fill="{STYLE['ink']}">{html.escape(scoreboard_line(sb))}</text>

  <text x="80" y="392" font-family="Inter, system-ui, sans-serif" font-size="19"
        fill="{STYLE['muted']}">{html.escape(engaged_line(stars))}</text>

  <text x="80" y="440" font-family="JetBrains Mono, monospace" font-size="14"
        letter-spacing="2" fill="{STYLE['muted']}">SOLID = DIRECT · HOLLOW = EXTENSION</text>

  {star_markup(stars)}
  {legend_markup(sb)}

  <text x="80" y="580" font-family="JetBrains Mono, monospace" font-size="26"
        letter-spacing="5" fill="{STYLE['ink']}">CVPE<tspan fill="{STYLE['accent']}">.</tspan>EU</text>
  <text x="1120" y="580" text-anchor="end" font-family="JetBrains Mono, monospace"
        font-size="20" letter-spacing="2" fill="{STYLE['muted']}">{html.escape(case['checked_on'])}</text>
</svg>"""


def render(case, stars, sb):
    os.makedirs(WORK, exist_ok=True)
    os.makedirs(OUT_DIR, exist_ok=True)
    slug = case["case_slug"]
    svg = build_svg(case, stars, sb)
    page = f"""<!DOCTYPE html><html><head><meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Inter:wght@300;400&family=JetBrains+Mono:wght@400&display=swap" rel="stylesheet">
<style>*{{margin:0;padding:0}}body{{width:1200px;height:630px;overflow:hidden}}</style>
</head><body>{svg}</body></html>"""
    work = os.path.join(WORK, f"{slug}.html")
    open(work, "w").write(page)
    out = os.path.join(OUT_DIR, f"{slug}.png")
    subprocess.run([CHROME, "--headless", "--disable-gpu", f"--screenshot={out}",
                    "--window-size=1200,630", "--hide-scrollbars",
                    "--virtual-time-budget=8000", f"file://{work}"], capture_output=True)
    return out


def main():
    args = [a for a in sys.argv[1:]]
    check_only = "--check" in args
    args = [a for a in args if not a.startswith("--")]

    files = ([os.path.join(CASES, f"{args[0]}.json")] if args
             else sorted(os.path.join(CASES, f) for f in os.listdir(CASES)
                         if f.endswith(".json") and not f.startswith("_")))
    if not files:
        print("no constellation cases found"); return 0

    failures = 0
    for path in files:
        case = json.load(open(path))
        try:
            stars = validate(case, os.path.basename(path))
        except InvalidCase as e:
            print(f"  INVALID  {e}"); failures += 1; continue
        sb = scoreboard(stars)
        if check_only:
            print(f"  ok       {case['case_slug']}: {scoreboard_line(sb)}")
            continue
        out = render(case, stars, sb)
        size = os.path.getsize(out) // 1024 if os.path.exists(out) else 0
        print(f"  rendered {case['case_slug']}.png ({size} KB) — {scoreboard_line(sb)}")
        print(f"           alt: {alt_text(case, sb)}")
        if case.get("_status"):
            print(f"           NOTE: {case['_status'][:72]}...")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
