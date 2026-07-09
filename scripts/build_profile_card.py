#!/usr/bin/env python3
"""Build the profile README SVG cards."""

from __future__ import annotations

import argparse
import calendar
import html
from collections.abc import Iterable
from datetime import date
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps


ROOT = Path(__file__).resolve().parents[1]
WIDTH = 1280
HEIGHT = 720
ASCII_COLS = 60
ASCII_ROWS = 48
ASCII_FONT_SIZE = 12
ASCII_LINE_HEIGHT = 12.6
TERM_X = 535
TERM_Y = 88
TERM_LINE_HEIGHT = 25
TERM_FONT_SIZE = 19
TERM_COLUMNS = 57

DATE_OF_BIRTH = date(2002, 12, 21)


def age_since(start: date, today: date | None = None) -> str:
    today = today or date.today()
    years = today.year - start.year
    months = today.month - start.month
    days = today.day - start.day

    if days < 0:
        months -= 1
        previous_month = today.month - 1 or 12
        previous_year = today.year if today.month > 1 else today.year - 1
        days += calendar.monthrange(previous_year, previous_month)[1]
    if months < 0:
        years -= 1
        months += 12

    return f"{years} years, {months} months, {days} days"


def profile_lines() -> list[tuple[str, str | None]]:
    return [
        ("System", None),
        ("OS", "macOS 26.5, Linux servers"),
        ("Uptime", age_since(DATE_OF_BIRTH)),
        ("Host", "cloud servers + backend systems"),
        ("Kernel", "Darwin 25.5.0, zsh"),
        ("Focus", "backend, cloud, security"),
        ("Mode", "build, break, automate, ship"),
        ("", ""),
        ("Work", None),
        ("Cloud.Backend", "APIs, VPS ops, infra automation"),
        ("Security", "bug bounty, harnesses, backend-only design"),
        ("AI.Automation", "agents, scrapers, workflows"),
        ("Languages", "TypeScript, Python, Go, C++, JavaScript"),
        ("", ""),
        ("Contact", None),
        ("GitHub", "github.com/CryptoMaN-Rahul"),
        ("LinkedIn", "linkedin.com/in/0x-rahul"),
        ("X", "@100x_rahul"),
        ("", ""),
        ("GitHub Stats", None),
        ("Repos", "58 public | Stars: 5 | Forks: 2"),
        ("Commits", "3,303 visible default-branch commits"),
        ("Contribs", "1,404 visible + 1,334 private"),
        ("Followers", "15"),
    ]


THEMES = {
    "dark": {
        "file": "dark_mode.svg",
        "canvas": "#0d1117",
        "panel": "#161b22",
        "border": "#30363d",
        "ascii": "#c9d1d9",
        "title": "#e6edf3",
        "muted": "#6e7681",
        "label": "#ffa657",
        "value": "#a5d6ff",
        "green": "#3fb950",
    },
    "light": {
        "file": "light_mode.svg",
        "canvas": "#ffffff",
        "panel": "#f6f8fa",
        "border": "#d0d7de",
        "ascii": "#57606a",
        "title": "#24292f",
        "muted": "#8c959f",
        "label": "#bc4c00",
        "value": "#0969da",
        "green": "#1a7f37",
    },
}


def escape_text(value: str) -> str:
    return html.escape(value, quote=False)


def photo_to_ascii(photo: Path) -> list[str]:
    image = Image.open(photo).convert("L")
    image = ImageOps.autocontrast(image)
    image = ImageEnhance.Contrast(image).enhance(1.45)
    image = image.resize((ASCII_COLS, ASCII_ROWS), Image.Resampling.LANCZOS)

    ramp = "    .,:;irsXA253hMHGS#9B&@"
    rows: list[str] = []
    for y in range(ASCII_ROWS):
        chars = []
        for x in range(ASCII_COLS):
            pixel = image.getpixel((x, y))
            index = int((255 - pixel) / 255 * (len(ramp) - 1))
            chars.append(ramp[index])
        rows.append("".join(chars).rstrip())
    return rows


def leader(label: str, value: str) -> str:
    prefix = f"{label}: "
    dot_count = max(3, TERM_COLUMNS - len(prefix) - len(value) - 1)
    return "." * dot_count


def section_label(name: str) -> str:
    fill = "-" * max(3, TERM_COLUMNS - len(name) - 5)
    return f"- {name} {fill}"


def svg_text_lines(lines: Iterable[str], x: int, y: int) -> str:
    result = []
    for index, line in enumerate(lines):
        safe = escape_text(line)
        result.append(
            f'<tspan x="{x}" y="{y + index * ASCII_LINE_HEIGHT:.1f}">{safe}</tspan>'
        )
    return "\n".join(result)


def terminal_lines(theme: dict[str, str]) -> str:
    y = TERM_Y
    parts = [
        f'<text x="{TERM_X}" y="{y}" class="terminal title">'
        f'rahul@cryptoman-rahul <tspan class="muted">{"-" * 27}</tspan>'
        "</text>"
    ]
    y += TERM_LINE_HEIGHT + 12

    for label, value in profile_lines():
        if label == "" and value == "":
            y += TERM_LINE_HEIGHT // 2
            continue
        if value is None:
            parts.append(
                f'<text x="{TERM_X}" y="{y}" class="terminal muted">'
                f"{escape_text(section_label(label))}</text>"
            )
            y += TERM_LINE_HEIGHT
            continue

        dots = leader(label, value)
        value_class = "value"
        if label == "Contribs":
            parts.append(
                f'<text x="{TERM_X}" y="{y}" class="terminal">'
                f'<tspan class="label">{escape_text(label)}:</tspan> '
                f'<tspan class="muted">{dots}</tspan> '
                f'<tspan class="value">1,404 visible</tspan> '
                f'<tspan class="green">+ 1,334 private</tspan>'
                "</text>"
            )
            y += TERM_LINE_HEIGHT
            continue
        if label == "Followers":
            value_class = "green"
        parts.append(
            f'<text x="{TERM_X}" y="{y}" class="terminal">'
            f'<tspan class="label">{escape_text(label)}:</tspan> '
            f'<tspan class="muted">{dots}</tspan> '
            f'<tspan class="{value_class}">{escape_text(value)}</tspan>'
            "</text>"
        )
        y += TERM_LINE_HEIGHT

    return "\n".join(parts)


def build_svg(ascii_lines: list[str], theme: dict[str, str]) -> str:
    ascii_spans = svg_text_lines(ascii_lines, 68, 92)
    return f'''<svg width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-labelledby="title desc">
  <title id="title">Rahul R M GitHub profile card</title>
  <desc id="desc">A terminal-style GitHub profile card with ASCII art generated from Rahul R M's photo.</desc>
  <style>
    .ascii {{
      fill: {theme["ascii"]};
      font: {ASCII_FONT_SIZE}px "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
      white-space: pre;
    }}
    .terminal {{
      font: 700 {TERM_FONT_SIZE}px "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
      letter-spacing: 0;
    }}
    .title {{ fill: {theme["title"]}; }}
    .muted {{ fill: {theme["muted"]}; }}
    .label {{ fill: {theme["label"]}; }}
    .value {{ fill: {theme["value"]}; }}
    .green {{ fill: {theme["green"]}; }}
  </style>
  <rect width="{WIDTH}" height="{HEIGHT}" rx="18" fill="{theme["canvas"]}"/>
  <rect x="24" y="24" width="{WIDTH - 48}" height="{HEIGHT - 48}" rx="18" fill="{theme["panel"]}" stroke="{theme["border"]}" stroke-width="2"/>
  <text class="ascii" xml:space="preserve">
{ascii_spans}
  </text>
  {terminal_lines(theme)}
</svg>
'''


def build(photo: Path) -> None:
    ascii_lines = photo_to_ascii(photo)
    for theme in THEMES.values():
        (ROOT / theme["file"]).write_text(build_svg(ascii_lines, theme), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("photo", type=Path, help="Photo to convert into ASCII art")
    args = parser.parse_args()
    build(args.photo.expanduser().resolve())


if __name__ == "__main__":
    main()
