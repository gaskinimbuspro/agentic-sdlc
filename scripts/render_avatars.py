#!/usr/bin/env python3
"""Write the cast avatars: flat cartoon people, one per character.

Output: docs/diagrams/assets/avatars/<key>.svg, one per key in CAST of
render_diagrams.py. Original artwork for this repository; no third-party marks.
Each avatar is a disc in the character's color with a head-and-shoulders bust
clipped to it, and one prop for the role. Cooper's is drawn after Cooper's
own portrait, on request. Run render_diagrams.py afterwards.
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
        f"C{cx + 8} {cy - 14} {cx + 12} {cy - 10} {cx + 11} {cy - 1} "
        f'C{cx + 9} {cy - 6} {cx + 5} {cy - 8} {cx} {cy - 8} C{cx - 5} {cy - 8} {cx - 9} {cy - 6} {cx - 11} {cy - 1} Z" '
        f'fill="{color}"/>'
    )


def face(
    cx: float, cy: float, closed: bool = False, mouth: str = INK, brow: str = INK
) -> str:
    return (
        brows(cx, cy - 4, brow)
        + eyes(cx, cy, closed)
        + cheeks(cx, cy + 4)
        + smile(cx, cy + 5.5, mouth)
    )


def glasses(
    cx: float, cy: float, r: float = 3.4, color: str = INK, square: bool = False
) -> str:
    lenses = "".join(
        (
            f'<rect x="{x - r}" y="{cy - r * 0.75}" width="{2 * r}" height="{1.5 * r}" rx="1" '
            if square
            else f'<circle cx="{x}" cy="{cy}" r="{r}" '
        )
        + f'fill="#FFFFFF" fill-opacity=".18" stroke="{color}" stroke-width="1.2"/>'
        for x in (cx - 4.4, cx + 4.4)
    )
    return (
        lenses
        + f'<path d="M{cx - 4.4 + r} {cy} H{cx + 4.4 - r}" stroke="{color}" stroke-width="1.1"/>'
    )


def grin(cx: float, cy: float) -> str:
    return (
        f'<path d="M{cx - 5.5} {cy} Q{cx} {cy + 6.5} {cx + 5.5} {cy} Q{cx} {cy + 2} {cx - 5.5} {cy} Z" fill="#7F2D2D"/>'
        f'<path d="M{cx - 4.4} {cy + 0.8} Q{cx} {cy + 2.9} {cx + 4.4} {cy + 0.8} L{cx + 3.6} {cy + 2.3} '
        f'Q{cx} {cy + 3.6} {cx - 3.6} {cy + 2.3} Z" fill="#FFFFFF"/>'
    )


def cooper() -> str:
    skin, line = "#D9A27A", "#B07A55"
    hair, grey = "#4E4B48", "#9A9794"
    return (
        bust("#1E2633", skin, top=50, width=23)
        + '<path d="M14 58 Q32 54 50 58 M12 63 Q32 59 52 63" stroke="#2F3B50" stroke-width="1.2" fill="none"/>'
        + '<path d="M28 47 Q32 51 36 47 L36.5 55 L27.5 55 Z" fill="#0E0E10"/>'
        + '<path d="M23.5 44 L28 47.5 L31 57 L25.5 54 L21 48 Z" fill="#2A3446"/>'
        + '<path d="M40.5 44 L36 47.5 L33 57 L38.5 54 L43 48 Z" fill="#2A3446"/>'
        + '<path d="M32 55 V66" stroke="#A3A8B3" stroke-width=".9" stroke-dasharray="1 .8"/>'
        + head(32, 31, skin, 10.8, 12)
        + '<path d="M21.4 32.5 C21.8 39.5 26.5 43 32 43 C37.5 43 42.2 39.5 42.6 32.5 C40.5 36.8 36.5 38.4 32 38.4 C27.5 38.4 23.5 36.8 21.4 32.5 Z" fill="#6B5A50" opacity=".2"/>'
        + f'<path d="M21.3 30 C21 26 21.8 23 23.6 21.4 L24.6 28 Z M42.7 30 C43 26 42.2 23 40.4 21.4 L39.4 28 Z" fill="{grey}"/>'
        + f'<path d="M22.4 25.8 L22.5 20.6 L23.8 17.6 L25.2 18 L26.3 15.2 L27.8 16.3 L29.3 13.9 L30.8 15.4 '
        f"L32.6 13.4 L34 15.2 L35.9 13.9 L36.9 15.9 L38.7 15.2 L39.3 17.4 L41 17.8 L41.8 21 L41.8 25.4 "
        f'C39.6 22.6 36 21.6 32 21.8 C28.2 22 24.6 23.4 22.4 25.8 Z" fill="{hair}"/>'
        + "".join(
            f'<path d="{d}" stroke="#7C7874" stroke-width=".6" fill="none" stroke-linecap="round"/>'
            for d in (
                "M24.6 22.8 Q25.2 19.6 26.8 16.8",
                "M27.4 22 Q28.2 18.6 30 15.4",
                "M30.4 21.6 Q31.4 18 33.4 15",
                "M33.4 21.6 Q34.8 18.2 36.6 15.6",
                "M36.4 22 Q38 19.4 39.4 17.6",
                "M39.2 22.8 Q40.4 21 41 19.4",
            )
        )
        + '<path d="M24.8 26.6 Q27.6 25.2 30.2 26.4 M33.8 26.4 Q36.4 25.2 39.2 26.6" stroke="#3A2E28" stroke-width="1.6" fill="none" stroke-linecap="round"/>'
        + "".join(
            f'<ellipse cx="{x}" cy="30.4" rx="1.8" ry="1.6" fill="#2B1A10"/><circle cx="{x + 0.6}" cy="29.8" r=".55" fill="#FFFFFF"/>'
            f'<path d="M{x - 2.2} 32.3 Q{x} 33.3 {x + 2.2} 32.3" stroke="{line}" stroke-width=".7" fill="none"/>'
            for x in (27.6, 36.4)
        )
        + f'<path d="M30.9 33.6 Q32 35.2 33.1 33.6" stroke="{line}" stroke-width="1" fill="none" stroke-linecap="round"/>'
        + f'<path d="M24.8 35 Q25.2 37.8 27 39.4 M39.2 35 Q38.8 37.8 37 39.4" stroke="{line}" stroke-width=".7" fill="none"/>'
        + grin(32, 37.4)
        + cheeks(32, 34.5)
    )


def voltran() -> str:
    skin, hair = SKIN["light"], "#1F1F24"
    return (
        f'<path d="M19.5 31 C18.5 18 25 14.5 32 14.5 C39 14.5 45.5 18 44.5 31 L45 44 L38 44 L38 34 L26 34 L26 44 L19 44 Z" fill="{hair}"/>'
        + bust("#374151", skin)
        + '<path d="M28 49 L32 56 L36 49 Z" fill="#F9FAFB"/>'
        + head(32, 31, skin, 10, 11.5)
        + f'<path d="M21.5 29 C22 21 26 18.5 32 18.5 C38 18.5 42 21 42.5 29 C38 26 34 23 29 22.6 C26.5 24.5 24 26.5 21.5 29 Z" fill="{hair}"/>'
        + face(32, 31)
        + glasses(32, 31)
    )


def raymond() -> str:
    skin, grey = SKIN["warm"], "#D1D5DB"
    return (
        bust("#7F1D1D", skin)
        + '<path d="M26 48 Q32 53 38 48" stroke="#991B1B" stroke-width="3" fill="none"/>'
        + head(32, 31, skin)
        + f'<path d="M21.5 30 C21 24 22.5 21 25 20 L25.5 28 Z M42.5 30 C43 24 41.5 21 39 20 L38.5 28 Z" fill="{grey}"/>'
        + f'<path d="M22.5 34 C22.5 43 27 46 32 46 C37 46 41.5 43 41.5 34 C39.5 38.5 36 39.6 32 39.6 C28 39.6 24.5 38.5 22.5 34 Z" fill="{grey}"/>'
        + brows(32, 27, "#9CA3AF")
        + eyes(32, 31)
        + '<path d="M29 38.6 Q32 40.4 35 38.6" stroke="#6B4F3A" stroke-width="1.3" fill="none" stroke-linecap="round"/>'
        + glasses(32, 31.4, 3.2, "#111827", square=True)
    )


def debora() -> str:
    skin, hair = SKIN["tan"], "#3B2416"
    curls = "".join(
        f'<circle cx="{x}" cy="{y}" r="{r}" fill="{hair}"/>'
        for x, y, r in (
            (20, 26, 6),
            (24, 18, 6.5),
            (32, 15, 7),
            (40, 18, 6.5),
            (44, 26, 6),
            (18, 34, 5),
            (46, 34, 5),
        )
    )
    return (
        curls
        + bust("#F8FAFC", skin)
        + head(32, 32, skin, 10, 11.5)
        + f'<path d="M22 29 C23 22 27 21 32 21 C37 21 41 22 42 29 C38 25.5 26 25.5 22 29 Z" fill="{hair}"/>'
        + face(32, 33)
        + '<path d="M20 31 C20 15 44 15 44 31" stroke="#111827" stroke-width="1.8" fill="none"/>'
        + '<rect x="17.2" y="28.5" width="5" height="7" rx="2" fill="#111827"/>'
        + '<path d="M20 35 C20 40 24 41.5 28 40.5" stroke="#111827" stroke-width="1.4" fill="none" stroke-linecap="round"/>'
        + '<circle cx="28.4" cy="40.4" r="1.4" fill="#111827"/>'
    )


def patrick() -> str:
    skin = SKIN["light"]
    return (
        bust("#4B5563", skin, width=22)
        + '<path d="M22 50 Q32 46 42 50 L40 54 Q32 51 24 54 Z" fill="#6B7280"/>'
        + '<path d="M29 52 V59 M35 52 V59" stroke="#F3F4F6" stroke-width="1" stroke-linecap="round"/>'
        + head(32, 32, skin)
        + '<path d="M21 28 C21 17 26 13.5 32 13.5 C38 13.5 43 17 43 28 Z" fill="#F97316"/>'
        + '<path d="M20.5 25 H43.5 V29.5 H20.5 Z" fill="#EA580C"/>'
        + '<circle cx="32" cy="12.5" r="2.4" fill="#FDBA74"/>'
        + face(32, 33.5)
        + '<path d="M24 37 C25 41 28 43 32 43 C36 43 39 41 40 37" stroke="#A16207" stroke-width=".8" fill="none" opacity=".5"/>'
    )


def mccall() -> str:
    skin = SKIN["deep"]
    return (
        bust("#1F2937", skin)
        + '<path d="M12 66 C12 54 20 50 27 50 L29 66 Z M52 66 C52 54 44 50 37 50 L35 66 Z" fill="#FACC15"/>'
        + '<path d="M13 58 L28 57 M51 58 L36 57" stroke="#E5E7EB" stroke-width="2.2"/>'
        + head(32, 32, skin)
        + '<path d="M21 27 C21 18 26 15 32 15 C38 15 43 18 43 27 Z" fill="#1E3A8A"/>'
        + '<path d="M19 26.5 H47 Q46 29.5 42 29.5 H21 Q19 29 19 26.5 Z" fill="#172554"/>'
        + '<circle cx="32" cy="21" r="2.2" fill="#FACC15"/>'
        + eyes(32, 33)
        + brows(32, 30)
        + '<path d="M27.5 38.2 Q32 36.2 36.5 38.2 Q32 39.2 27.5 38.2 Z" fill="#111827"/>'
        + smile(32, 39.6, "#3B1F12")
    )


def dembe() -> str:
    skin, hair = SKIN["warm"], "#E5E7EB"
    return (
        bust("#111827", skin)
        + '<path d="M26 47 H38 L37 52 H27 Z" fill="#1F2937"/>'
        + head(32, 32, skin, 10, 11.5)
        + f'<path d="M21.5 31 C20 20 25 15 32 15 C40 15 44 19 43 26 C40 22 34 21.5 29 23.5 C26 24.5 23 27 21.5 31 Z" fill="{hair}"/>'
        + '<path d="M29 23.5 C33 20 39 20 43 26 C38 24 33 24 29 23.5 Z" fill="#CBD5E1"/>'
        + face(32, 33)
        + '<circle cx="21.6" cy="37.5" r="1.3" fill="#FACC15"/><circle cx="42.4" cy="37.5" r="1.3" fill="#FACC15"/>'
    )


def teresa() -> str:
    skin, hair = SKIN["tan"], "#111827"
    curls = "".join(
        f'<circle cx="{x}" cy="{y}" r="3.6" fill="{hair}"/>'
        for x, y in (
            (23, 21),
            (27.5, 17.5),
            (32.5, 16.5),
            (37.5, 17.5),
            (41.5, 21),
            (21.5, 26),
            (42.5, 26),
        )
    )
    return (
        bust("#15803D", skin)
        + curls
        + head(32, 32, skin)
        + f'<path d="M22 28 C23 22 27 21 32 21 C37 21 41 22 42 28 C38 25 26 25 22 28 Z" fill="{hair}"/>'
        + face(32, 33)
        + '<path d="M19.5 32 C19.5 13 44.5 13 44.5 32" stroke="#E5E7EB" stroke-width="2.4" fill="none"/>'
        + '<rect x="16.5" y="28" width="6" height="9" rx="2.6" fill="#E5E7EB"/>'
        + '<rect x="41.5" y="28" width="6" height="9" rx="2.6" fill="#E5E7EB"/>'
        + '<rect x="18" y="29.6" width="3" height="5.8" rx="1.4" fill="#9CA3AF"/>'
        + '<rect x="43" y="29.6" width="3" height="5.8" rx="1.4" fill="#9CA3AF"/>'
    )


CAST = {
    "cooper": ("#A76608", cooper, "Cooper, product owner"),
    "voltran": ("#7756C8", voltran, "Voltran, architect"),
    "raymond": ("#5B47B0", raymond, "Raymond, reviewer"),
    "debora": ("#2563EB", debora, "Debora, coordinator"),
    "patrick": ("#087F8C", patrick, "Patrick, builder"),
    "mccall": ("#0A6670", mccall, "McCall, CI gate"),
    "dembe": ("#7756C8", dembe, "Dembe, model server"),
    "teresa": ("#52647C", teresa, "Teresa, mirror"),
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
