#!/usr/bin/env python3
"""Write the cast avatars: a colored disc with a white emblem from each name's myth.

Output: docs/diagrams/assets/avatars/<key>.svg, one per key in CAST of
render_diagrams.py. Original artwork for this repository; no third-party marks.
Run render_diagrams.py afterwards.
"""

from pathlib import Path

out = Path(__file__).resolve().parents[1] / "docs/diagrams/assets/avatars"
out.mkdir(parents=True, exist_ok=True)
W = "#FFFFFF"
S = f'stroke="{W}" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round" fill="none"'


def disc(color: str, body: str, title: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
        f"<title>{title}</title>"
        f'<circle cx="32" cy="32" r="31" fill="{color}"/>'
        f'<circle cx="32" cy="32" r="27.5" fill="none" stroke="{W}" stroke-opacity=".3" stroke-width="1.4"/>'
        f"{body}</svg>\n"
    )


def eye(cx: float, cy: float, r: float, color: str) -> str:
    return (
        f'<path d="M{cx - r} {cy} Q{cx} {cy - r * 0.8} {cx + r} {cy} Q{cx} {cy + r * 0.8} {cx - r} {cy} Z" fill="{W}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="{r * 0.32}" fill="{color}"/>'
    )


def head(cx: float, cy: float, color: str) -> str:
    return (
        f'<polygon points="{cx - 6},{cy - 2} {cx - 5.5},{cy - 11} {cx - 1},{cy - 6}" fill="{W}"/>'
        f'<polygon points="{cx + 6},{cy - 2} {cx + 5.5},{cy - 11} {cx + 1},{cy - 6}" fill="{W}"/>'
        f'<circle cx="{cx}" cy="{cy}" r="6.5" fill="{W}"/>'
        f'<circle cx="{cx - 2.4}" cy="{cy - 0.8}" r="1.2" fill="{color}"/>'
        f'<circle cx="{cx + 2.4}" cy="{cy - 0.8}" r="1.2" fill="{color}"/>'
        f'<ellipse cx="{cx}" cy="{cy + 3.2}" rx="1.8" ry="1.2" fill="{color}"/>'
    )


AMBER, PURPLE, ARGUS, BLUE, TEAL, CERB, SLATE = (
    "#A76608", "#7756C8", "#5B47B0", "#2563EB", "#087F8C", "#0A6670", "#52647C",
)
avatars = {
    # Product owner: a person, nothing more.
    "gokhan": (AMBER, f'<circle cx="32" cy="24" r="8.5" fill="{W}"/>'
               f'<path d="M15 49 C16 38 24 35 32 35 C40 35 48 38 49 49 Z" fill="{W}"/>', "Gökhan, product owner"),
    # Atlas holds up the sphere.
    "atlas": (PURPLE, f'<circle cx="32" cy="22" r="11" {S}/><ellipse cx="32" cy="22" rx="4.6" ry="11" {S}/>'
              f'<path d="M21 22 H43" {S}/><circle cx="32" cy="41" r="4.2" fill="{W}"/>'
              f'<path d="M23 54 C24 47 40 47 41 54 Z" fill="{W}"/>'
              f'<path d="M26 49 L21 31 M38 49 L43 31" {S}/>', "Atlas, architect"),
    # Argus Panoptes, the watcher with many eyes.
    "argus": (ARGUS, eye(32, 33, 13, ARGUS) + eye(19, 18, 5.5, ARGUS) + eye(45, 18, 5.5, ARGUS)
              + eye(21, 49, 5, ARGUS) + eye(43, 49, 5, ARGUS), "Argus, reviewer"),
    # Iris, the messenger, travels on the rainbow.
    "iris": (BLUE, f'<path d="M12 44 A20 20 0 0 1 52 44" {S}/>'
             f'<path d="M18 44 A14 14 0 0 1 46 44" stroke="{W}" stroke-opacity=".8" stroke-width="2.6" fill="none" stroke-linecap="round"/>'
             f'<path d="M24 44 A8 8 0 0 1 40 44" stroke="{W}" stroke-opacity=".6" stroke-width="2.6" fill="none" stroke-linecap="round"/>'
             f'<path d="M45 17 L47 21 L51 23 L47 25 L45 29 L43 25 L39 23 L43 21 Z" fill="{W}"/>', "Iris, coordinator"),
    # Daedalus, the craftsman who built wings.
    "daedalus": (TEAL, f'<path d="M30 21 C21 14 11 18 9 29 C15 27 19 29 21 32 C17 33 14 36 13 41 C19 38 25 38 30 41 Z" fill="{W}"/>'
                 f'<path d="M34 21 C43 14 53 18 55 29 C49 27 45 29 43 32 C47 33 50 36 51 41 C45 38 39 38 34 41 Z" fill="{W}"/>'
                 f'<path d="M32 18 V47" {S}/>', "Daedalus, builder"),
    # Cerberus, the three-headed guard of the gate.
    "cerberus": (CERB, head(19, 35, CERB) + head(45, 35, CERB) + head(32, 28, CERB)
                 + f'<path d="M15 47 Q32 55 49 47" {S}/>', "Cerberus, CI gate"),
    # Pythia, the oracle on her tripod above the vapours.
    "pythia": (PURPLE, f'<path d="M21 34 H43 Q41 41 32 41 Q23 41 21 34 Z" fill="{W}"/>'
               f'<path d="M25 41 L21 51 M39 41 L43 51 M32 41 V51" {S}/>'
               f'<path d="M32 31 C26 27 33 22 29 14 C37 18 40 25 32 31 Z" fill="{W}"/>', "Pythia, model server"),
    # Echo, who repeats what she hears.
    "echo": (SLATE, f'<circle cx="20" cy="32" r="4" fill="{W}"/><path d="M27 24 A11 11 0 0 1 27 40" {S}/>'
             f'<path d="M32 18 A17 17 0 0 1 32 46" stroke="{W}" stroke-opacity=".75" stroke-width="2.6" fill="none" stroke-linecap="round"/>'
             f'<path d="M37 12 A23 23 0 0 1 37 52" stroke="{W}" stroke-opacity=".5" stroke-width="2.6" fill="none" stroke-linecap="round"/>', "Echo, mirror"),
}
for key, (color, body, title) in avatars.items():
    (out / f"{key}.svg").write_text(disc(color, body, title))
print(len(avatars), "avatars")
