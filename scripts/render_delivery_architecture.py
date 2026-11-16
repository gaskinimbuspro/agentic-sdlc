#!/usr/bin/env python3
"""Render the end-to-end delivery view as an editable SVG and a PNG preview."""

import re
import subprocess
from functools import cache
from html import escape
from io import BytesIO
from pathlib import Path

import cairosvg
from PIL import Image, ImageFont, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
DIAGRAMS = ROOT / "docs/diagrams"
ASSETS = DIAGRAMS / "assets"
NAME = "04-end-to-end-delivery-architecture"

WIDTH, HEIGHT = 1920, 1340
INK, MUTED, NAVY = "#10233B", "#415975", "#0E1C30"
BLUE, TEAL, AMBER = "#234E8A", "#126D62", "#86470A"
BORDER, PAPER = "#CCD9E7", "#F6F9FD"
PLAN, VERIFY, TARGET = "#EDF4FC", "#EBF5F3", "#FFF7E8"
TARGET_BORDER = "#CCA064"
COLS = (262, 670, 1078, 1486)
CARD_WIDTH = 348

ICON_NOTICE = "\n\n".join(
    (ASSETS / path).read_text()
    for path in ("lucide/LICENSE", "vendors/PRIMER-LICENSE", "vendors/CNCF-NOTICE.md")
)

DESCRIPTION = (
    "Three lanes show how a product brief becomes a scoped task, source change, "
    "reviewed pull request, and authorized release. The staged runtime and Hetzner "
    "operations pilot provide target-environment evidence. Amber dashed boundaries "
    "denote adoption profiles that still require field validation."
)


@cache
def font(size, bold):
    style = "Bold" if bold else "Regular"
    path = subprocess.check_output(
        ["fc-match", "-f", "%{file}", f"Arial:style={style}"], text=True
    ).strip()
    return ImageFont.truetype(path, size)


class Diagram:
    def __init__(self):
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
            f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
            '<title id="title">Agentic SDLC end-to-end delivery architecture</title>',
            f'<desc id="desc">{escape(DESCRIPTION)}</desc>',
            f"<metadata>{escape(ICON_NOTICE)}</metadata>",
            "<defs>",
        ]
        for kind, color in (
            ("flow", BLUE),
            ("runtime", TEAL),
            ("target", AMBER),
            ("repair", MUTED),
        ):
            self.parts.append(
                f'<marker id="{kind}" viewBox="0 0 10 10" refX="9" refY="5" '
                'markerWidth="11" markerHeight="11" orient="auto" markerUnits="userSpaceOnUse">'
                f'<path d="M0 0 L10 5 L0 10 Z" fill="{color}"/></marker>'
            )
        self.parts.append("</defs>")

    def rect(self, x, y, w, h, fill, stroke="none", radius=13, dashed=False):
        dash = ' stroke-dasharray="8 6"' if dashed else ""
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="1.5"{dash}/>'
        )

    def text(
        self, x, y, value, size=20, color=INK, bold=False, limit=None, anchor="start"
    ):
        if limit is not None and font(size, bold).getlength(value) > limit:
            raise ValueError(f"Text exceeds layout width: {value}")
        self.parts.append(
            f'<text x="{x}" y="{y}" fill="{color}" font-family="Arial" font-size="{size}" '
            f'font-weight="{700 if bold else 400}" text-anchor="{anchor}">'
            f"{escape(value)}</text>"
        )

    def arrow(self, path, kind="flow", dashed=False, end=True, width=2.7):
        colors = {"flow": BLUE, "runtime": TEAL, "target": AMBER, "repair": MUTED}
        dash = ' stroke-dasharray="7 6"' if dashed else ""
        marker = f' marker-end="url(#{kind})"' if end else ""
        self.parts.append(
            f'<path d="{path}" stroke="{colors[kind]}" stroke-width="{width}" fill="none" '
            f'stroke-linecap="round" stroke-linejoin="round"{dash}{marker}/>'
        )

    def icon(self, x, y, name, size=28, color=BLUE):
        vendor = name in {"github", "flux", "kubernetes"}
        folder = "vendors" if vendor else "lucide"
        raw = (ASSETS / folder / f"{name}.svg").read_text()
        pattern = r"<svg\b([^>]*)>(.*)</svg>"
        source = re.search(pattern, raw, re.S)
        if source is None:
            raise ValueError(f"Invalid SVG: {name}")
        view_box = re.search(r'viewBox="([^"]+)"', source[1])
        if view_box is None:
            raise ValueError(f"Missing viewBox: {name}")
        style = (
            ' fill="#0E1C30"'
            if vendor
            else (
                f' fill="none" stroke="{color}" stroke-width="1.75" '
                'stroke-linecap="round" stroke-linejoin="round"'
            )
        )
        # Each source SVG uses local CSS classes. Scope them to preserve each logo.
        markup = (
            re.sub(r"cls-(\d+)", rf"{name}-cls-\1", source[2]) if vendor else source[2]
        )
        self.parts.append(
            f'<svg x="{x}" y="{y}" width="{size}" height="{size}" '
            f'viewBox="{view_box[1]}"{style} aria-hidden="true">{markup}</svg>'
        )

    def card(self, x, y, w, h, title, lines, icon, color=BLUE, compact=False):
        self.rect(x, y, w, h, "#FFFFFF", BORDER)
        self.icon(x + 17, y + 15, icon, 26 if compact else 30, color)
        self.text(x + 58, y + 36, title, 20 if compact else 24, bold=True, limit=w - 74)
        body_size = 16 if compact else 18
        body_baseline = 62 if compact else 73
        for i, line in enumerate(lines):
            baseline = body_baseline + i * (19 if compact else 22)
            if baseline + 6 > h:
                raise ValueError(f"Text exceeds card height: {title}")
            self.text(x + 17, y + baseline, line, body_size, MUTED, limit=w - 34)

    def lane(self, y, h, fill, accent, title, subtitle, target=False):
        self.rect(46, y, 1828, h, fill, TARGET_BORDER if target else "none", 18, target)
        self.rect(65, y + 23, 4, 78, accent, radius=2)
        self.text(82, y + 45, title[0], 24, accent, bold=True, limit=174)
        self.text(82, y + 72, title[1], 24, accent, bold=True, limit=174)
        self.text(82, y + 98, subtitle, 15, MUTED, limit=174)

    def save(self):
        svg = DIAGRAMS / f"{NAME}.svg"
        png = DIAGRAMS / f"{NAME}.png"
        svg.write_text("\n".join([*self.parts, "</svg>", ""]), encoding="utf-8")
        rendered = cairosvg.svg2png(url=str(svg), output_width=2400)
        with Image.open(BytesIO(rendered)) as image:
            info = PngImagePlugin.PngInfo()
            info.add_text("Description", DESCRIPTION)
            info.add_text("Icon notices", ICON_NOTICE)
            image.convert("RGB").save(png, optimize=True, pnginfo=info)


def draw():
    view = Diagram()
    view.rect(0, 0, WIDTH, HEIGHT, PAPER, radius=0)
    view.rect(0, 0, WIDTH, 150, NAVY, radius=0)
    view.text(54, 40, "AGENTIC SDLC", 16, "#A6C5EB", bold=True)
    view.text(54, 94, "End-to-end delivery architecture", 48, "#FFFFFF", bold=True)
    view.text(
        55,
        127,
        "Customer application reference and production adoption profiles",
        21,
        "#CAD9ED",
    )
    view.text(
        1863,
        44,
        "REFERENCE BASELINE  ·  8ef923f",
        16,
        "#CAD9ED",
        bold=True,
        anchor="end",
    )

    view.arrow("M58 178 H105")
    view.text(116, 184, "Delivery flow", 17, MUTED)
    view.arrow("M275 178 H322", "repair", dashed=True)
    view.text(333, 184, "Repair or return evidence", 17, MUTED)
    view.rect(606, 167, 33, 20, VERIFY, "#9ABEB5", 4)
    view.text(651, 184, "Repository workflow and reference checks", 17, MUTED)
    view.rect(1050, 167, 33, 20, TARGET, TARGET_BORDER, 4, True)
    view.text(1095, 184, "Target integration  ·  Field validation pending", 17, MUTED)

    view.lane(208, 190, PLAN, BLUE, ("Plan", "and build"), "Design & assignment")
    view.lane(
        441, 298, VERIFY, TEAL, ("Verify", "and integrate"), "GitHub and trusted CI"
    )
    view.lane(
        783, 165, TARGET, AMBER, ("Release", "and adopt"), "GitOps target", target=True
    )

    for i in range(3):
        view.arrow(f"M{COLS[i] + CARD_WIDTH + 1} 311 H{COLS[i + 1] - 7}")
    view.arrow("M1660 371 V503")
    view.text(1678, 423, "Candidate PR", 16, BLUE, bold=True)
    view.arrow("M1485 569 H1457 V519 H1433")
    view.arrow("M1457 569 V631 H1433")
    view.arrow("M1077 519 H1050 V569 H1025")
    view.arrow("M1077 631 H1050 V569", end=False)
    view.arrow("M669 569 H617")
    view.arrow("M436 633 V808")
    view.text(455, 768, "Integrated source", 16, BLUE, bold=True)
    view.arrow("M844 633 V714 H1853 V311 H1840", "repair", dashed=True, width=2)
    view.text(1120, 704, "Failures or stale evidence return to the worker", 17, MUTED)

    for i in range(3):
        view.arrow(f"M{COLS[i] + CARD_WIDTH + 1} 869 H{COLS[i + 1] - 7}", "target")
    view.arrow("M1252 930 V1001", "target")
    view.arrow("M1325 1003 V974 H1566 V936", "target", dashed=True, width=2)
    view.text(1370, 964, "Runtime evidence", 16, AMBER, bold=True)
    view.arrow("M1660 1004 V935", "target", dashed=True, width=2)
    view.text(1678, 980, "Pilot evidence", 16, AMBER, bold=True)

    plan = [
        (
            "Product brief",
            ("Goals, scope and constraints", "Product owner agrees outcomes"),
            "user-round",
        ),
        (
            "Architecture & design",
            ("UI journeys, API/data contracts", "Planner · standards, cases and tasks"),
            "layers",
        ),
        (
            "Task coordinator",
            ("GitHub Issues and SQLite leases", "Readiness, owner and attempt budget"),
            "workflow",
        ),
        (
            "Isolated worker",
            ("One task, workspace and context", "Code, local checks and handoff"),
            "code-xml",
        ),
    ]
    for x, (title, lines, icon) in zip(COLS, plan, strict=True):
        view.card(x, 252, CARD_WIDTH, 119, title, lines, icon)
    view.text(
        COLS[2] + 1,
        389,
        "Ledger tested  ·  Live GitHub App integration pending",
        14,
        AMBER,
        limit=CARD_WIDTH,
    )

    view.card(
        COLS[3],
        505,
        CARD_WIDTH,
        128,
        "GitHub pull request",
        ("Candidate source and target base", "Changes, decision links and tests"),
        "github",
        TEAL,
    )
    view.card(
        COLS[2],
        474,
        CARD_WIDTH,
        90,
        "GitHub Actions CI",
        (
            "Backend, browser, security and recovery",
            "Build, real PostgreSQL and reports",
        ),
        "flask-conical",
        TEAL,
        compact=True,
    )
    view.card(
        COLS[2],
        586,
        CARD_WIDTH,
        90,
        "Independent review",
        ("Checks the same candidate and test cases", "Findings and approval"),
        "shield-check",
        TEAL,
        compact=True,
    )
    view.card(
        COLS[1],
        505,
        CARD_WIDTH,
        128,
        "Integration gate",
        ("Match source, base and evidence", "Require passing CI and review"),
        "list-checks",
        TEAL,
    )
    view.card(
        COLS[0],
        505,
        CARD_WIDTH,
        128,
        "Merge to main",
        ("Authorized integration", "Verify main tree and rerun CI"),
        "git-branch",
        TEAL,
    )

    release = [
        (
            "Release inputs",
            ("Build once · verify OCI digest", "Approved Git revision and provenance"),
            "git-branch",
        ),
        (
            "Flux reconciler",
            ("Pull desired state and reconcile", "Observe revision, health and drift"),
            "flux",
        ),
        (
            "Kubernetes staging",
            ("Run the approved image digest", "Check rollout and recovery"),
            "kubernetes",
        ),
        (
            "Release acceptance",
            (
                "Smoke, accessibility and visual review",
                "Approve production · verify or revert",
            ),
            "shield-check",
        ),
    ]
    for x, (title, lines, icon) in zip(COLS, release, strict=True):
        view.card(x, 812, CARD_WIDTH, 118, title, lines, icon, AMBER)

    view.rect(46, 1004, 1307, 264, TARGET, TARGET_BORDER, 18, True)
    view.text(70, 1041, "Staging application", 26, INK, bold=True)
    view.text(70, 1067, "Customer reference · target identity binding", 17, MUTED)
    view.rect(498, 1058, 330, 58, "#FFFFFF", BORDER, 12)
    view.icon(512, 1071, "shield-check", 29, AMBER)
    view.text(552, 1082, "OIDC provider", 19, INK, bold=True)
    view.text(552, 1103, "Sign-in and token issuance", 15, MUTED)
    view.arrow("M733 1143 V1120", "target", width=2)
    view.text(751, 1138, "Code exchange and keys", 14, AMBER)
    runtime = [
        (71, 185, "Browser", ("Customer",), "user-round"),
        (294, 248, "React UI", ("TypeScript · HTTPS",), "monitor"),
        (
            580,
            306,
            "Gateway + FastAPI",
            ("API authorization and tenant scope",),
            "server",
        ),
        (924, 393, "PostgreSQL", ("Customer and audit records",), "database"),
    ]
    for i, (x, w, title, lines, icon) in enumerate(runtime):
        if i:
            prev_x, prev_w, *_ = runtime[i - 1]
            view.arrow(f"M{prev_x + prev_w + 1} 1185 H{x - 6}", "runtime", width=2.3)
        view.card(x, 1146, w, 82, title, lines, icon, TEAL, compact=True)
    view.text(
        71,
        1252,
        "Trusted observations: running digest, smoke, session behavior and recovery",
        16,
        MUTED,
    )

    view.rect(1373, 1004, 501, 264, TARGET, TARGET_BORDER, 18, True)
    view.icon(1397, 1019, "network", 28, AMBER)
    view.text(1439, 1041, "Hetzner operations pilot", 25, INK, bold=True, limit=411)
    for x, title, line in [
        (1395, "Coordinator", "Durable state"),
        (1554, "Worker", "Scoped execution"),
        (1713, "Preview", "Isolated runtime"),
    ]:
        view.rect(x, 1064, 139, 69, "#FFFFFF", BORDER, 10)
        view.text(x + 10, 1091, title, 17, INK, bold=True, limit=120)
        view.text(x + 10, 1114, line, 14, MUTED, limit=120)
    view.arrow("M1535 1099 H1550", "target", width=1.8)
    view.arrow("M1694 1099 H1709", "target", width=1.8)
    view.text(
        1395,
        1170,
        "Serial delivery → recovery drills → 24 h soak",
        18,
        INK,
        bold=True,
        limit=454,
    )
    view.text(
        1395,
        1199,
        "Off-host restore · compare one and two workers",
        17,
        MUTED,
        limit=454,
    )
    view.text(
        1395, 1236, "Evidence binds the approved run window", 16, MUTED, limit=454
    )

    view.arrow("M47 1290 H1873", "repair", end=False, width=0.9)
    view.text(
        47,
        1318,
        "Source of record: GitHub Issues and PRs  ·  Protected CI and target observations feed candidate-bound evidence gates",
        16,
        MUTED,
    )
    view.text(1873, 1318, "Architecture view 04", 16, MUTED, bold=True, anchor="end")
    view.save()


if __name__ == "__main__":
    draw()
