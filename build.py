import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

from art import Sky, build_art_data_url

ROOT = Path(__file__).parent
CSS_LIMIT = 20_000


@dataclass(frozen=True)
class Theme:
    id: str
    name: str
    sources: tuple[str, ...]
    sky: Sky
    plus_pressed: str


THEMES = (
    Theme("nyx", "Nyx", ("theme.css",), Sky(480, 270, seed=7, speckles=True), ""),
    Theme(
        "nyx-plus",
        "Nyx Plus",
        ("theme.css", "plus.css"),
        Sky(400, 225, seed=8, speckles=False),
        ",[data-model-picker-sidebar] [aria-pressed=true]",
    ),
)

COLORS = {
    "canvas": "#000000",
    "chrome": "#000000",
    "toolbar": "#000000",
    "sidebar": "#000000",
    "sidebarBorder": "#16161d",
    "border": "#1f1f27",
    "accent": "#8a7fe8",
    "accentForeground": "#06061a",
    "focus": "#8a7fe8",
    "surface": "#0d0c20",
    "surfaceRaised": "#110f2a",
    "surfaceOverlay": "#0c0b1c",
    "input": "#24224a",
    "messageSurface": "#1e1b48",
    "messageAction": "#7f78e6",
    "messageActionForeground": "#ffffff",
    "messageActionHover": "#948df0",
    "update": "#8a7fe8",
    "updateForeground": "#b4aaff",
    "updateSurface": "#17152e",
    "muted": "#1a1840",
    "secondary": "#16143a",
    "secondaryForeground": "#f1f0ff",
    "mutedForeground": "#a6a3c0",
    "secondaryLabel": "#a6a3c0",
    "sidebarMutedForeground": "#9d9ab8",
    "sidebarControlSurface": "#000000",
    "codeBackground": "#08071a",
    "terminalBackground": "#06051a",
    "terminalCursor": "#b4aaff",
    "terminalSelection": "#2a2660",
}


SHORT_VARIABLES = {
    "--nyx-key-glow": "--kg",
    "--nyx-key-rim": "--kr",
    "--nyx-key": "--k",
    "--nyx-art-width": "--w",
    "--nyx-sheen-edge": "--s",
    "--nyx-grid": "--g",
    "--nyx-dot": "--d",
    "--nyx-art": "--a",
    "--nyx-sky": "--b",
    "--nyx-shine": "--h",
}


def minify(css: str) -> str:
    strings: list[str] = []

    def stash(match: re.Match) -> str:
        strings.append(match.group(0))
        return f"\x00{len(strings) - 1}\x00"

    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = re.sub(r'="([A-Za-z_][\w-]*)"\]', r"=\1]", css)
    css = re.sub(r'"[^"]*"|url\(data:[^)]*\)', stash, css)
    css = re.sub(r"\s+", " ", css)
    css = re.sub(r"\s*([{};,>])\s*", r"\1", css)
    css = re.sub(r":\s+", ":", css)
    css = re.sub(r"\s*!important", "!important", css)
    css = re.sub(r" ([*/]) ", r"\1", css)
    css = css.replace(";}", "}")
    css = re.sub(r"\btransparent\b", "#0000", css)
    css = re.sub(r"#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3(([0-9a-f])\5)?\b", lambda m: "#" + m.group(1) + m.group(2) + m.group(3) + (m.group(5) or ""), css, flags=re.I)
    css = re.sub(r"\s*([<>])\s*", r"\1", css)
    css = re.sub(r"(?<![\w.])0\.(\d)", r".\1", css)
    for long_name in sorted(SHORT_VARIABLES, key=len, reverse=True):
        css = css.replace(long_name, SHORT_VARIABLES[long_name])
    css = re.sub(r"(?<=[{};,])&(?: |(?=>))", "", css)
    css = re.sub(r"\x00(\d+)\x00", lambda m: strings[int(m.group(1))], css)
    return css.strip()


def build(theme: Theme) -> dict:
    css = minify("\n".join((ROOT / source).read_text() for source in theme.sources))
    css = (
        css.replace("__PLUS_PRESSED__", theme.plus_pressed)
        .replace("__ART_WIDTH__", str(theme.sky.width))
        .replace("__ART__", build_art_data_url(theme.sky))
    )
    if len(css) > CSS_LIMIT:
        sys.exit(f"{theme.id} css is {len(css)} characters; T3 accepts at most {CSS_LIMIT}")
    return {"version": 1, "name": theme.name, "appearance": "dark", "colors": COLORS, "css": css}


if __name__ == "__main__":
    for theme in THEMES:
        built = build(theme)
        out = ROOT / f"{theme.id}.json"
        out.write_text(json.dumps(built, indent=2) + "\n")
        print(f"{out.name}: {len(built['css'])} css characters")
