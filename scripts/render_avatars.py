#!/usr/bin/env python3
"""Write the cast avatars: flat cartoon characters drawn from each name's myth.

Output: docs/diagrams/assets/avatars/<key>.svg, one per key in CAST of
render_diagrams.py. Original artwork for this repository; no third-party marks.
Each avatar is a disc in the character's color with a head-and-shoulders bust
clipped to it. Run render_diagrams.py afterwards.
"""

from pathlib import Path

OUT = Path(__file__).resolve().parents[1] / "docs/diagrams/assets/avatars"

INK = "#1F2937"
WHITE = "#FFFFFF"
SKIN = {"light": "#F2C9A0", "warm": "#E0AC69", "tan": "#C68642", "deep": "#8D5524"}


def eyes(cx: float, cy: float, closed: bool = False, gap: float = 4.2) -> str:
    if closed:
        return "".join(
            f'<path d="M{x - 2} {cy} Q{x} {cy + 1.8} {x + 2} {cy}" stroke="{INK}" '
            'stroke-width="1.3" fill="none" stroke-linecap="round"/>'
            for x in (cx - gap, cx + gap)
        )
    return "".join(
        f'<circle cx="{x}" cy="{cy}" r="1.9" fill="{INK}"/>'
        f'<circle cx="{x + 0.6}" cy="{cy - 0.6}" r="0.6" fill="{WHITE}"/>'
        for x in (cx - gap, cx + gap)
    )


def brows(cx: float, cy: float, color: str = INK, gap: float = 4.2) -> str:
    return "".join(
        f'<path d="M{x - 2.2} {cy} Q{x} {cy - 1.2} {x + 2.2} {cy}" stroke="{color}" '
        'stroke-width="1.2" fill="none" stroke-linecap="round"/>'
        for x in (cx - gap, cx + gap)
    )


def smile(cx: float, cy: float, color: str = INK) -> str:
    return (
        f'<path d="M{cx - 3} {cy} Q{cx} {cy + 2.6} {cx + 3} {cy}" stroke="{color}" '
        'stroke-width="1.3" fill="none" stroke-linecap="round"/>'
    )


def cheeks(cx: float, cy: float) -> str:
    return "".join(
        f'<circle cx="{x}" cy="{cy}" r="1.8" fill="#F28C8C" opacity=".45"/>'
        for x in (cx - 6.5, cx + 6.5)
    )


def head(cx: float, cy: float, skin: str, rx: float = 10.5, ry: float = 11.5) -> str:
    ears = "".join(
        f'<ellipse cx="{x}" cy="{cy + 1}" rx="2" ry="3" fill="{skin}"/>'
        for x in (cx - rx, cx + rx)
    )
    return ears + f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{skin}"/>'


def bust(color: str, neck_skin: str, top: float = 50, width: float = 22) -> str:
    return (
        f'<rect x="28.5" y="{top - 7}" width="7" height="9" fill="{neck_skin}"/>'
        f'<path d="M{32 - width} 66 C{32 - width} {top + 3} {32 - width / 2} {top} 32 {top} '
        f'C{32 + width / 2} {top} {32 + width} {top + 3} {32 + width} 66 Z" fill="{color}"/>'
    )


def short_hair(cx: float, cy: float, color: str) -> str:
    return (
        f'<path d="M{cx - 11} {cy - 1} C{cx - 12} {cy - 11} {cx - 5} {cy - 14} {cx + 1} {cy - 14} '
        f'C{cx + 8} {cy - 14} {cx + 12} {cy - 10} {cx + 11} {cy - 1} '
        f'C{cx + 9} {cy - 6} {cx + 5} {cy - 8} {cx} {cy - 8} C{cx - 5} {cy - 8} {cx - 9} {cy - 6} {cx - 11} {cy - 1} Z" '
        f'fill="{color}"/>'
    )


def face(cx: float, cy: float, closed: bool = False, mouth: str = INK, brow: str = INK) -> str:
    return brows(cx, cy - 4, brow) + eyes(cx, cy, closed) + cheeks(cx, cy + 4) + smile(cx, cy + 5.5, mouth)


def gokhan() -> str:
    skin = SKIN["light"]
    return (
        bust("#1E3A5F", skin)
        + '<path d="M27 50 L32 56 L29.5 57 L25.5 51 Z M37 50 L32 56 L34.5 57 L38.5 51 Z" fill="#FFFFFF"/>'
        + head(32, 31, skin) + short_hair(32, 31, "#3B2A20") + face(32, 32)
        + '<circle cx="44" cy="57" r="5" fill="#FFFFFF"/>'
        + '<path d="M41.6 57 L43.4 58.9 L46.6 55.2" stroke="#16A34A" stroke-width="1.6" fill="none" '
        'stroke-linecap="round" stroke-linejoin="round"/>'
    )


def atlas() -> str:
    skin = SKIN["tan"]
    beard = "#2B1B12"
    return (
        # Arms raised to hold the globe.
        f'<path d="M16 60 L21 20 M48 60 L43 20" stroke="{skin}" stroke-width="5" stroke-linecap="round"/>'
        + bust("#F3F4F6", skin, top=52, width=20)
        + '<path d="M20 58 L40 52 L42 56 L22 62 Z" fill="#B45309"/>'
        + f'<circle cx="21.5" cy="18" r="3.2" fill="{skin}"/><circle cx="42.5" cy="18" r="3.2" fill="{skin}"/>'
        + '<circle cx="32" cy="12" r="8" fill="#3B82F6"/>'
        + '<path d="M24.5 12 H39.5 M32 4 C28 8 28 16 32 20 C36 16 36 8 32 4" stroke="#FFFFFF" stroke-width="1" fill="none"/>'
        + '<path d="M27 9 C29 8 30 10 29 12 C27 13 26 11 27 9 Z M34 13 C37 12 38 15 36 17 C34 17 33 15 34 13 Z" fill="#22C55E"/>'
        + head(32, 36, skin, 10, 11)
        + f'<path d="M22 31 C21 26 25 24 32 24 C39 24 43 26 42 31 C40 28 36 27.5 32 27.5 C28 27.5 24 28 22 31 Z" fill="{beard}"/>'
        + f'<path d="M22 36 C22 46 27 50 32 50 C37 50 42 46 42 36 C40 41 36 42.5 32 42.5 C28 42.5 24 41 22 36 Z" fill="{beard}"/>'
        + brows(32, 32, beard) + eyes(32, 35.5)
        + f'<path d="M29 41 Q32 43 35 41" stroke="{SKIN["light"]}" stroke-width="1.3" fill="none" stroke-linecap="round"/>'
    )


def argus() -> str:
    skin = SKIN["light"]
    band = "#FBBF24"

    def small_eye(x: float, y: float) -> str:
        return (
            f'<path d="M{x - 2.6} {y} Q{x} {y - 2.2} {x + 2.6} {y} Q{x} {y + 2.2} {x - 2.6} {y} Z" fill="#FFFFFF"/>'
            f'<circle cx="{x}" cy="{y}" r="1.1" fill="#5B47B0"/>'
        )

    return (
        bust("#3B2F7A", skin)
        + head(32, 31, skin) + short_hair(32, 31, "#6B7280")
        + f'<path d="M21.2 24.5 C25 22 39 22 42.8 24.5 L42.6 28 C39 25.8 25 25.8 21.4 28 Z" fill="{band}"/>'
        + small_eye(26, 25.4) + small_eye(38, 25.4)
        + '<path d="M28.6 25 Q32 21.8 35.4 25 Q32 28.2 28.6 25 Z" fill="#FFFFFF" stroke="#5B47B0" stroke-width=".6"/>'
        + '<circle cx="32" cy="25" r="1.5" fill="#5B47B0"/>'
        + eyes(32, 32) + cheeks(32, 36) + smile(32, 37.5)
    )


def iris() -> str:
    skin = SKIN["warm"]
    bands = ["#EF4444", "#F59E0B", "#FACC15", "#22C55E", "#FFFFFF"]
    halo = "".join(
        f'<path d="M{32 - r} 34 A{r} {r} 0 0 1 {32 + r} 34" stroke="{c}" stroke-width="2.4" fill="none"/>'
        for r, c in zip((22, 19.6, 17.2, 14.8, 12.4), bands, strict=True)
    )
    wing = (
        '<path d="M{x} 28 C{a} 24 {b} 22 {c} 20 C{d} 25 {e} 28 {x} 31 Z" fill="#FFFFFF"/>'
    )
    return (
        halo
        + '<path d="M19 38 C19 24 26 19 32 19 C38 19 45 24 45 38 L45 48 L19 48 Z" fill="#1F2937"/>'
        + bust("#E0F2FE", skin)
        + head(32, 32, skin, 10, 11)
        + '<path d="M21.5 30 C22 22 27 20 32 20 C37 20 42 22 42.5 30 C39 26 35 25 32 25 C29 25 25 26 21.5 30 Z" fill="#1F2937"/>'
        + wing.format(x=21, a=18, b=15, c=12, d=14, e=17)
        + wing.format(x=43, a=46, b=49, c=52, d=50, e=47)
        + face(32, 33)
    )


def daedalus() -> str:
    skin = SKIN["warm"]
    hair = "#6B4226"
    def wing(m: int) -> str:
        def x(v: float) -> float:
            return 32 + m * (v - 32)

        return (
            f'<path d="M{x(24)} 50 C{x(16)} 40 {x(10)} 28 {x(9)} 12 C{x(15)} 18 {x(20)} 26 {x(23)} 34 Z" fill="#FFFFFF"/>'
            f'<path d="M{x(24)} 54 C{x(15)} 48 {x(9)} 40 {x(6)} 30 C{x(13)} 34 {x(18)} 38 {x(24)} 42 Z" fill="#E2E8F0"/>'
            f'<path d="M{x(24)} 58 C{x(16)} 55 {x(10)} 50 {x(6)} 44 C{x(13)} 46 {x(18)} 48 {x(24)} 50 Z" fill="#FFFFFF"/>'
        )

    return (
        wing(1) + wing(-1)
        + bust("#92400E", skin, width=18)
        + '<path d="M25 52 H39 V66 H25 Z" fill="#B45309"/>'
        + head(32, 32, skin) + short_hair(32, 32, hair)
        + f'<path d="M23 36 C23 44 27 47 32 47 C37 47 41 44 41 36 C39 40 36 41 32 41 C28 41 25 40 23 36 Z" fill="{hair}"/>'
        + '<path d="M21.5 25 H42.5" stroke="#374151" stroke-width="1.4"/>'
        + '<circle cx="27.6" cy="25" r="3.3" fill="#FBBF24" stroke="#374151" stroke-width="1.2"/>'
        + '<circle cx="36.4" cy="25" r="3.3" fill="#FBBF24" stroke="#374151" stroke-width="1.2"/>'
        + eyes(32, 33) + f'<path d="M29.5 39 Q32 40.6 34.5 39" stroke="{SKIN["light"]}" stroke-width="1.3" fill="none" stroke-linecap="round"/>'
    )


def dog(cx: float, cy: float, s: float) -> str:
    fur, ear, muzzle = "#A0693F", "#5C3A21", "#E3C8A2"
    return (
        f'<path d="M{cx - 7 * s} {cy - 6 * s} C{cx - 12 * s} {cy - 5 * s} {cx - 12 * s} {cy + 4 * s} {cx - 9 * s} {cy + 6 * s} '
        f'L{cx - 5 * s} {cy - 2 * s} Z" fill="{ear}"/>'
        f'<path d="M{cx + 7 * s} {cy - 6 * s} C{cx + 12 * s} {cy - 5 * s} {cx + 12 * s} {cy + 4 * s} {cx + 9 * s} {cy + 6 * s} '
        f'L{cx + 5 * s} {cy - 2 * s} Z" fill="{ear}"/>'
        f'<ellipse cx="{cx}" cy="{cy}" rx="{8 * s}" ry="{7.6 * s}" fill="{fur}"/>'
        f'<ellipse cx="{cx}" cy="{cy + 3.6 * s}" rx="{4.6 * s}" ry="{3.4 * s}" fill="{muzzle}"/>'
        f'<ellipse cx="{cx}" cy="{cy + 2.2 * s}" rx="{1.8 * s}" ry="{1.3 * s}" fill="{INK}"/>'
        f'<path d="M{cx - 1.4 * s} {cy + 5 * s} Q{cx} {cy + 8 * s} {cx + 1.4 * s} {cy + 5 * s} Z" fill="#F472B6"/>'
        f'<circle cx="{cx - 3.2 * s}" cy="{cy - 1.6 * s}" r="{1.4 * s}" fill="{INK}"/>'
        f'<circle cx="{cx + 3.2 * s}" cy="{cy - 1.6 * s}" r="{1.4 * s}" fill="{INK}"/>'
        f'<circle cx="{cx - 2.8 * s}" cy="{cy - 2 * s}" r="{0.45 * s}" fill="{WHITE}"/>'
        f'<circle cx="{cx + 3.6 * s}" cy="{cy - 2 * s}" r="{0.45 * s}" fill="{WHITE}"/>'
    )


def cerberus() -> str:
    spikes = "".join(f'<path d="M{x - 2} 52 L{x} 47.5 L{x + 2} 52 Z" fill="#E5E7EB"/>' for x in range(16, 50, 6))
    return (
        '<path d="M8 66 C8 52 18 46 32 46 C46 46 56 52 56 66 Z" fill="#A0693F"/>'
        + dog(16, 36, 0.8) + dog(48, 36, 0.8)
        + '<path d="M10 52 C20 49 44 49 54 52 L54 56 C44 53 20 53 10 56 Z" fill="#1F2937"/>' + spikes
        + dog(32, 30, 1.05)
    )


def pythia() -> str:
    skin = SKIN["light"]
    leaves = "".join(
        f'<ellipse cx="{x}" cy="{y}" rx="2.4" ry="1.2" fill="#22C55E" transform="rotate({r} {x} {y})"/>'
        for x, y, r in ((24, 25, -35), (27.5, 22.8, -18), (32, 22, 0), (36.5, 22.8, 18), (40, 25, 35))
    )
    return (
'<path d="M12 66 C12 42 17 16 32 14 C47 16 52 42 52 66 Z" fill="#3B1D7A"/>'
        + '<path d="M20 66 C20 50 25 46 32 46 C39 46 44 50 44 66 Z" fill="#6D4BC4"/>'
        + head(32, 33, skin, 9.6, 10.8)
        + '<path d="M22 30 C22 24 26 21 32 21 C38 21 42 24 42 30 C39 27 36 26.5 32 26.5 C28 26.5 25 27 22 30 Z" fill="#1F2937"/>'
        + leaves
        + "".join(
            f'<path d="M{x} 46 C{x - 3} 41 {x + 3} 37 {x} 32 C{x - 3} 27 {x + 3} 24 {x} 20" '
            'stroke="#FFFFFF" stroke-width="1.6" fill="none" stroke-linecap="round" opacity=".8"/>'
            for x in (8, 56)
        )
        + brows(32, 29.5) + eyes(32, 33.5, closed=True) + cheeks(32, 37) + smile(32, 38.5)
    )


def echo() -> str:
    skin = SKIN["deep"]
    hair = "#111827"
    return (
        bust("#CBD5E1", skin)
        + f'<circle cx="32" cy="16" r="6" fill="{hair}"/>'
        + head(32, 32, skin)
        + f'<path d="M21 31 C20 22 26 19 32 19 C38 19 44 22 43 31 C41 26 37 25 32 25 C27 25 23 26 21 31 Z" fill="{hair}"/>'
        + face(32, 33, brow=hair, mouth="#F2C9A0")
        # A hand cupped at the ear, then the sound coming back.
        + f'<path d="M41 27 C47 26 49 31 48 36 C47 40 44 41 42 39 Z" fill="{skin}"/>'
        + f'<path d="M44.5 40 L46 50" stroke="{skin}" stroke-width="3" stroke-linecap="round"/>'
        + '<path d="M51 27 A7 7 0 0 1 51 39" stroke="#FFFFFF" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
        + '<path d="M55 23 A12 12 0 0 1 55 43" stroke="#FFFFFF" stroke-width="1.8" fill="none" stroke-linecap="round" opacity=".7"/>'
    )


CAST = {
    "gokhan": ("#A76608", gokhan, "Gökhan, product owner"),
    "atlas": ("#7756C8", atlas, "Atlas, architect"),
    "argus": ("#5B47B0", argus, "Argus, reviewer"),
    "iris": ("#2563EB", iris, "Iris, coordinator"),
    "daedalus": ("#087F8C", daedalus, "Daedalus, builder"),
    "cerberus": ("#0A6670", cerberus, "Cerberus, CI gate"),
    "pythia": ("#7756C8", pythia, "Pythia, model server"),
    "echo": ("#52647C", echo, "Echo, mirror"),
}


def avatar(key: str, color: str, body: str, title: str) -> str:
    return (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64" width="64" height="64">'
        f"<title>{title}</title>"
        f'<defs><clipPath id="clip-{key}"><circle cx="32" cy="32" r="31"/></clipPath></defs>'
        f'<circle cx="32" cy="32" r="31" fill="{color}"/>'
        f'<g clip-path="url(#clip-{key})">{body}</g>'
        f'<circle cx="32" cy="32" r="30.4" fill="none" stroke="{WHITE}" stroke-opacity=".55" stroke-width="1.2"/>'
        "</svg>\n"
    )


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for key, (color, draw, title) in CAST.items():
        (OUT / f"{key}.svg").write_text(avatar(key, color, draw(), title))
    print(f"{len(CAST)} avatars in {OUT}")
