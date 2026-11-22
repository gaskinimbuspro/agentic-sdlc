#!/usr/bin/env python3
"""Render the proposed SDLC views as standalone SVG and PNG files.

Requires Python, Pillow and either Inkscape or a Playwright Chromium. Assets are
local; rendering uses no network. Pass diagram numbers to render a subset.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys

from PIL import Image, ImageFont, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/diagrams"
ASSETS = OUT / "assets/lucide"
LICENSE = (ASSETS / "LICENSE").read_text()
BRANDS = OUT / "assets/simple-icons"
AVATARS = OUT / "assets/avatars"
BRAND_COLORS = {
    "ansible": "#EE0000", "claude": "#D97757", "docker": "#2496ED", "github": "#181717",
    "githubactions": "#2088FF", "hetzner": "#D50C2D", "kubernetes": "#326CE5",
    "nvidia": "#76B900", "terraform": "#844FBA", "forgejo": "#FB923C", "vllm": "#30A2FF",
    "argo": "#EF7B4D", "k3s": "#FFC61C",
}
SLATE = "#52647C"
TINTS = {"#2563EB": "#EDF3FF", "#087F8C": "#E3F4F5", "#7756C8": "#F1ECFB", "#A76608": "#FFF2D9",
         SLATE: "#EEF2F8"}
RASTERIZE = """
const { chromium } = require('playwright');
(async () => {
  const [svg, png, height] = process.argv.slice(1);
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1800, height: Number(height) } });
  await page.goto('file://' + svg);
  await page.screenshot({ path: png });
  await browser.close();
})();
"""
BLUE, TEAL, PURPLE, AMBER = "#2563EB", "#087F8C", "#7756C8", "#A76608"
INK, MUTED, BORDER = "#13243C", "#52647C", "#D9E2EF"
# The cast: name, role, what it runs as, Lucide icon, color. Keep in step with docs/architecture/cast.md.
CAST = {
    "cooper": ("Cooper", "PRODUCT OWNER", "Decides · approves · merges", "user-round", AMBER),
    "voltran": ("Voltran", "ARCHITECT", "Claude", "pencil-ruler", PURPLE),
    "raymond": ("Raymond", "REVIEWER", "Claude · separate session", "eye", PURPLE),
    "debora": ("Debora", "COORDINATOR", "Python program · not a model", "workflow", BLUE),
    "patrick": ("Patrick", "BUILDER", "Qwen Code + Qwen model", "hammer", TEAL),
    "mccall": ("McCall", "CI GATE", "Woodpecker", "shield-check", TEAL),
    "dembe": ("Dembe", "MODEL SERVER", "vLLM · RunPod", "cpu", PURPLE),
    "teresa": ("Teresa", "MIRROR", "Forgejo push mirror", "copy", "#52647C"),
}


def measure(value: str, size: int, bold: bool = False) -> float:
    font = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    return ImageFont.truetype(font, size).getlength(value)


def wrap(value: str, width: int, size: int) -> list[str]:
    lines: list[str] = []
    line = ""
    for word in value.split():
        trial = f"{line} {word}".strip()
        if line and measure(trial, size) > width:
            lines.append(line)
            line = word
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


class Canvas:
    def __init__(self, title: str, subtitle: str, height: int = 1120):
        self.height = height
        self.parts = [
            f'<svg xmlns="http://www.w3.org/2000/svg" width="1800" height="{height}" '
            f'viewBox="0 0 1800 {height}" role="img" aria-labelledby="title desc">',
            f'<title id="title">{escape(title)}</title><desc id="desc">{escape(subtitle)}</desc>',
            f'<metadata>{escape(LICENSE)}</metadata>',
            '<defs>',
        ]
        for name, color in [("blue", BLUE), ("teal", TEAL), ("purple", PURPLE), ("gray", "#8292A8"), ("amber", AMBER)]:
            self.parts.append(f'<marker id="{name}" viewBox="0 0 10 10" refX="9" refY="5" '
                              f'markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
                              f'<path d="M 1 1 L 9 5 L 1 9" fill="none" stroke="{color}" stroke-width="1.6"/></marker>')
        self.parts.append('</defs>')
        self.rect(0, 0, 1800, height, "#F4F7FC", radius=0)
        self.rect(0, 0, 1800, 145, "#13243C", radius=0)
        self.text(64, 34, "AGENTIC SDLC  /  ARCHITECTURE VIEWS", 13, "#A7BEDA", bold=True)
        self.text(64, 82, title, 36, "#FFFFFF", bold=True)
        self.text(64, 116, subtitle, 17, "#C4D1E4")
        self.rect(1510, 44, 225, 43, "#FFF0CD", radius=21)
        self.text(1622, 71, "DRAFT · v0.1", 17, "#805100", bold=True, anchor="middle")

    def rect(self, x, y, w, h, fill, stroke="none", radius=18, dash=False, shadow=False):
        dash_attr = 'stroke-dasharray="7 6"' if dash else ''
        if shadow:
            self.parts.append(f'<rect x="{x}" y="{y + 4}" width="{w}" height="{h}" '
                              f'rx="{radius}" fill="#E1E8F2" opacity=".65"/>')
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{radius}" '
                          f'fill="{fill}" stroke="{stroke}" stroke-width="1.5" '
                          f'{dash_attr} '
                          '/>')

    def text(self, x, y, value, size=18, color=INK, bold=False, anchor="start"):
        self.parts.append(f'<text x="{x}" y="{y}" font-family="DejaVu Sans, sans-serif" '
                          f'font-size="{size}" fill="{color}" font-weight="{700 if bold else 400}" '
                          f'text-anchor="{anchor}">{escape(value)}</text>')

    def icon(self, x, y, name, color=BLUE, size=30):
        raw = (ASSETS / f"{name}.svg").read_text()
        inner = re.search(r"<svg\b[^>]*>(.*)</svg>", raw, re.S).group(1)
        self.parts.append(f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24" '
                          f'fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" '
                          f'stroke-linejoin="round">{inner}</svg>')

    def brand(self, x, y, name, size=30, color=None):
        raw = (BRANDS / f"{name}.svg").read_text()
        path = re.search(r'<path d="([^"]+)"', raw).group(1)
        self.parts.append(f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 24 24" '
                          f'fill="{color or BRAND_COLORS[name]}"><path d="{path}"/></svg>')

    def mark(self, x, y, name, color=BLUE, size=30):
        """Draw a product mark when one exists, otherwise a generic icon."""
        if (BRANDS / f"{name}.svg").exists():
            self.brand(x, y, name, size)
        else:
            self.icon(x, y, name, color, size)

    def portrait(self, x, y, key, size=62):
        """The character's own avatar (scripts/render_avatars.py)."""
        raw = (AVATARS / f"{key}.svg").read_text()
        inner = re.search(r"<svg\b[^>]*>(.*)</svg>", raw, re.S).group(1)
        inner = re.sub(r"<title>.*?</title>", "", inner)
        self.parts.append(f'<svg x="{x}" y="{y}" width="{size}" height="{size}" viewBox="0 0 64 64">{inner}</svg>')

    def node(self, x, y, w, h, title, sub, icon, color=BLUE, title_size=21, dashed=False):
        """Compact card: one icon, a short title and at most one short line.

        A dashed card marks something planned but not built."""
        if dashed:
            self.rect(x, y, w, h, "#F8FAFD", "#9AA8BC", dash=True)
        else:
            self.rect(x, y, w, h, "#FFFFFF", BORDER, shadow=True)
        branded = (BRANDS / f"{icon}.svg").exists()
        self.rect(x + 18, y + (h - 58) / 2, 58, 58, "#F3F5F9" if branded else TINTS[color], radius=14)
        self.mark(x + 30, y + (h - 34) / 2, icon, color, 34)
        assert measure(title, title_size, True) < w - 110, title
        assert measure(sub, 15) < w - 110, sub
        self.text(x + 94, y + h / 2 - (2 if sub else -7), title, title_size, INK, bold=True)
        if sub:
            self.text(x + 94, y + h / 2 + 22, sub, 15, MUTED)

    def character(self, x, y, w, h, key, sub=None):
        """A cast member: role kicker, character name and what it runs as."""
        name, role, runs, icon, color = CAST[key]
        sub = runs if sub is None else sub
        self.rect(x, y, w, h, "#FFFFFF", BORDER, shadow=True)
        self.portrait(x + 16, y + (h - 64) / 2, key, 64)
        for value, size, bold in ((role, 12, True), (name, 21, True), (sub, 15, False)):
            assert measure(value, size, bold) < w - 108, value
        self.text(x + 94, y + h / 2 - 22, role, 12, color, bold=True)
        self.text(x + 94, y + h / 2 + 4, name, 21, INK, bold=True)
        self.text(x + 94, y + h / 2 + 27, sub, 15, MUTED)

    def avatar(self, cx, y, key, size=40, label=True):
        """Small portrait with the character name underneath, centered on cx."""
        name = CAST[key][0]
        self.portrait(cx - size / 2, y, key, size)
        if label:
            self.text(cx, y + size + 26, name, 14, INK, anchor="middle")

    def badge(self, x, y, number, color=INK):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="15" fill="{color}" stroke="#FFFFFF" stroke-width="2.5"/>')
        self.text(x, y + 5, str(number), 14, "#FFFFFF", bold=True, anchor="middle")

    def pill(self, x, y, value, color=BLUE, size=14):
        """Centered rounded label; x is the horizontal center."""
        width = measure(value, size, True) + 28
        self.rect(x - width / 2, y, width, size + 16, TINTS[color], color, radius=(size + 16) / 2)
        self.text(x, y + size + 5, value, size, color, bold=True, anchor="middle")

    def zone(self, x, y, w, h, name, icon=None, color=BLUE):
        self.rect(x, y, w, h, "#EAF1FE", "#B8C9E8", dash=True)
        offset = 26
        if icon:
            self.mark(x + 24, y + 18, icon, color, 24)
            offset = 60
        self.text(x + offset, y + 36, name, 14, color, bold=True)

    def card(self, x, y, w, h, title, lines, icon, kicker, color=BLUE, tint="#EDF3FF", body_size=17):
        self.rect(x, y, w, h, "#FFFFFF", BORDER, shadow=True)
        self.rect(x + 20, y + 20, 49, 49, tint, radius=13)
        self.icon(x + 29, y + 29, icon, color, 31)
        assert measure(kicker, 12, True) < w - 102, kicker
        assert measure(title, 21, True) < w - 102, title
        self.text(x + 86, y + 34, kicker, 12, color, bold=True)
        self.text(x + 86, y + 61, title, 21, INK, bold=True)
        wrapped = [line for value in lines for line in wrap(value, w - 44, body_size)]
        assert 96 + (len(wrapped) - 1) * 25 < h - 15, (title, wrapped)
        for n, line in enumerate(wrapped):
            self.text(x + 22, y + 96 + n * 25, line, body_size, MUTED)

    def arrow(self, path, name="blue", dash=False, width=2.4, end=True, start=False):
        colors = {"blue": BLUE, "teal": TEAL, "purple": PURPLE, "gray": "#8292A8", "amber": AMBER}
        dash_attr = 'stroke-dasharray="7 6"' if dash else ''
        marker_attr = f'marker-end="url(#{name})"' if end else ''
        if start:
            marker_attr += f' marker-start="url(#{name})"'
        self.parts.append(f'<path d="{path}" fill="none" stroke="{colors[name]}" stroke-width="{width}" '
                          f'stroke-linecap="round" stroke-linejoin="round" '
                          f'{dash_attr} {marker_attr}/>')

    def label(self, x, y, value, color=MUTED, size=14, fill="#F4F7FC"):
        width = measure(value, size) + 20
        self.rect(x - width / 2, y - size, width, size + 10, fill, radius=5)
        self.text(x, y + 2, value, size, color, anchor="middle")

    def footer(self, number, note, brands=False):
        y = self.height - 64
        self.arrow(f"M64 {y} H1736", "gray", width=.6, end=False)
        self.text(64, y + 29, note, 14, MUTED)
        credit = "Icons: Lucide / Feather · ISC / MIT · Source and licenses in the repository"
        if brands:
            self.licenses = LICENSE + "\n\n" + (BRANDS / "LICENSE.md").read_text()
            credit = ("Icons: Lucide / Feather (ISC / MIT) · Simple Icons (CC0) · "
                      "Product marks identify products and belong to their owners")
        self.text(64, y + 49, credit, 11, MUTED)
        self.text(1736, y + 30, f"AGENTIC SDLC  /  {number}", 13, MUTED, bold=True, anchor="end")

    def save(self, name):
        self.parts.append('</svg>')
        svg = OUT / f"{name}.svg"
        png = OUT / f"{name}.png"
        svg.write_text("\n".join(self.parts) + "\n")
        env = dict(os.environ, XDG_CACHE_HOME="/tmp/agentic-sdlc-diagram-cache")
        if shutil.which("inkscape"):
            subprocess.run(["inkscape", str(svg), "--export-type=png", "--export-width=1800",
                            f"--export-filename={png}"], check=True, env=env, capture_output=True)
        else:
            subprocess.run(["node", "-e", RASTERIZE, str(svg), str(png), str(self.height)],
                           check=True, env=env, capture_output=True)
        with Image.open(png) as image:
            info = PngImagePlugin.PngInfo()
            info.add_text("Description", "Agentic SDLC draft architecture v0.1")
            info.add_text("Icon licenses", getattr(self, "licenses", LICENSE))
            image.convert("RGB").save(png, optimize=True, pnginfo=info)
        print(f"{name}: SVG + PNG")


def process():
    c = Canvas("From project brief to verified delivery", "Proposed lifecycle · decisions, responsibilities, and feedback")
    c.rect(64, 183, 1672, 70, "#E7EEF9", radius=15)
    c.icon(86, 204, "file-text", BLUE, 28)
    c.text(132, 211, "INPUT", 12, BLUE, bold=True)
    c.text(132, 236, "Project brief + shared engineering standards + working settings", 21, INK, bold=True)
    stages = [
        (64, 310, "Understand the brief", ["Read goals and constraints", "Expose unknowns and assumptions", "Identify user scenarios"], "file-text", "01 · CONTEXT", BLUE),
        (650, 310, "Clarify requirements", ["MVP, scope, and non-goals", "Acceptance criteria and quality targets", "Security and performance expectations"], "list-checks", "02 · REQUIREMENTS", BLUE),
        (1236, 310, "Design the architecture", ["UI flows, API, and data boundaries", "Language and framework profile", "Decisions, trade-offs, and diagrams"], "layers", "03 · DESIGN", PURPLE),
        (1236, 640, "Prepare and dispatch", ["Confirm GitHub owner and repo policy", "Planner splits work with test criteria", "Coordinator claims and assigns ready tasks"], "git-branch", "04 · READINESS", PURPLE),
        (650, 640, "Implement and verify", ["Code, developer tests, and trusted CI", "Independent review and acceptance evidence", "Repair failures within task budget"], "flask-conical", "05 · IMPLEMENTATION", TEAL),
        (64, 640, "Integrate and learn", ["Require evidence for the current candidate", "Release and smoke when in scope", "Feed lessons back into the standard"], "rocket", "06 · DELIVERY", TEAL),
    ]
    for x, y, title, lines, icon, kicker, color in stages:
        c.card(x, y, 500, 190, title, lines, icon, kicker, color)
    for path in ["M564 405 H645", "M1150 405 H1231", "M1486 500 V635", "M1236 735 H1155", "M650 735 H569"]:
        c.arrow(path)
    c.label(607, 388, "scenarios", size=12)
    c.label(1193, 388, "criteria", size=12)
    c.label(1550, 570, "design", size=13)
    c.label(1193, 718, "tasks", size=12)
    c.label(607, 718, "evidence", size=12)
    c.rect(64, 548, 1086, 56, "#FFF2D9", "#EAD1A1", radius=12)
    c.icon(85, 562, "user-round", AMBER, 27)
    c.text(130, 581, "HUMAN DIRECTION", 13, AMBER, bold=True)
    c.text(357, 581, "Scope · material decisions · outcome evaluation", 17, INK)
    c.arrow("M900 830 V910 H28 V280 H900 V305", "gray", dash=True)
    c.label(660, 935, "Test and review findings feed planning and repairs", size=17)
    c.text(64, 1005, "Solid arrows: main flow     Dashed arrow: feedback loop     Amber: human direction", 16, MUTED)
    c.footer("01", "Proposed process; the dispatcher and enforcement have not been implemented.")
    c.save("01-development-process")


def agents():
    c = Canvas("Backend roles, task context, and evidence", "Proposed responsibilities · exclusive coding ownership · independent review · trusted checks", 1200)
    c.card(64, 180, 350, 145, "Cooper", ["Goals, priorities, material decisions"], "user-round", "PRODUCT OWNER", AMBER, "#FFF2D9", 16)
    c.card(480, 180, 475, 145, "Project brief", ["Scenarios, scope, and constraints"], "file-text", "PROJECT INPUT", BLUE)
    c.card(1040, 180, 696, 145, "Shared standards and settings", ["Language and test profiles · GitHub · task schema"], "settings-2", "VERSIONED GUIDANCE", PURPLE)
    c.arrow("M414 252 H475", "amber")
    c.arrow("M717 325 V367 H900 V405")
    c.arrow("M1388 325 V465 H1155", "purple")
    c.label(1390, 373, "standards / permissions", PURPLE)
    c.arrow("M239 325 V495 H645", "amber")
    c.label(432, 477, "decisions / direction", AMBER)
    c.card(650, 410, 500, 170, "Coordinator", ["Check readiness and dependency completion", "Claim, assign, budget, and track tasks", "Evaluate evidence before marking done"], "workflow", "DISPATCH AND STATE CONTROL", BLUE)
    c.arrow("M900 580 V635", end=False)
    c.arrow("M254 635 H1544", end=False)
    roles = [
        (64, "Architect / Planner", ["Requirements, decisions, test plan", "Split and order bounded tasks"], "layers", "DECOMPOSITION", BLUE),
        (494, "Implementer", ["One scoped task per coding context", "Code, tests, PR, durable handoff"], "code-xml", "ONE CODING OWNER", TEAL),
        (924, "Independent review", ["Separate context; inspect the candidate", "Challenge cases and report blockers"], "shield-check", "CANDIDATE REVIEW", PURPLE),
        (1354, "CI verification", ["Execute checks; reject missing results", "Bind reports to revision and artifact"], "flask-conical", "DETERMINISTIC SYSTEM", TEAL),
    ]
    for x, title, lines, icon, kicker, color in roles:
        c.arrow(f"M{x + 190} 635 V695")
        c.card(x, 700, 380, 170, title, lines, icon, kicker, color, body_size=16)
        c.arrow(f"M{x + 190} 870 V906", "gray", width=1.8)
    c.rect(64, 911, 1672, 53, "#E7EEF9", radius=12)
    c.icon(84, 924, "file-text", BLUE, 25)
    c.text(128, 944, "DURABLE STATE AND OUTPUTS", 13, BLUE, bold=True)
    c.text(480, 944, "Requirements · decisions · claims · issue / PR · trusted reports", 18, INK)
    c.arrow("M64 938 H28 V550 H645", "gray", dash=True)
    c.label(339, 573, "results / state feedback", size=14)
    c.rect(64, 1002, 1672, 90, "#FFFFFF", BORDER, radius=15)
    c.text(86, 1027, "TOOLS  /  Access is limited by role and task", 13, MUTED, bold=True)
    for x, name, icon in [(86, "GitHub", "git-branch"), (390, "Terminal / code", "code-xml"), (720, "Test / CI", "flask-conical"), (1020, "Browser", "monitor"), (1330, "Documents", "file-text")]:
        c.icon(x, 1044, icon, BLUE, 26)
        c.text(x + 41, 1064, name, 18, INK)
    c.footer("02", "One task, one coding owner, isolated workspace/context; review separately. Proposed workflow, not a running service.")
    c.save("02-agent-structure")


def application():
    c = Canvas("An illustrative backend architecture", "Example web application · technology, service count, and deployment profile remain project decisions", 1200)
    c.card(64, 180, 350, 150, "User", ["Uses the web interface"], "user-round", "ACTOR", BLUE, body_size=16)
    c.card(540, 180, 430, 150, "Web interface", ["Screens, forms, and user journeys"], "monitor", "PRESENTATION", BLUE, body_size=16)
    c.card(1270, 180, 466, 150, "Identity service", ["Authentication and sessions"], "shield-check", "EXTERNAL IF REQUIRED", PURPLE)
    c.arrow("M414 255 H535")
    c.label(477, 238, "HTTPS", size=13)
    c.arrow("M970 255 H1265", "purple")
    c.label(1120, 238, "sign-in / session", PURPLE)
    c.rect(64, 400, 1672, 435, "#EAF1FE", "#B8C9E8", dash=True)
    c.text(90, 434, "APPLICATION BOUNDARY", 14, BLUE, bold=True)
    c.text(620, 434, "Logical responsibilities · physical service boundaries are a design decision", 16, MUTED)
    c.arrow("M755 330 V365 H347 V485")
    c.label(550, 352, "HTTPS / JSON")
    c.card(120, 490, 455, 190, "API / entry layer", ["Authentication, authorization, validation", "Consistent response and error contract", "API and authorization tests"], "server", "ENTRY BOUNDARY", BLUE)
    c.card(665, 490, 455, 190, "Business behavior", ["Use cases, invariants, and behavior", "Separated from UI and data access", "Unit and behavior tests"], "brain-circuit", "DOMAIN", PURPLE)
    c.card(1210, 490, 470, 190, "Data and integration", ["Data and external service connections", "Timeout and failure policies", "Integration and contract tests"], "network", "ADAPTERS", TEAL)
    c.arrow("M575 585 H660")
    c.label(620, 568, "call", size=12)
    c.arrow("M1120 585 H1205", "purple")
    c.label(1165, 568, "interface", size=12)
    c.rect(120, 725, 1000, 74, "#FFFFFF", "#D5E1F3", radius=12)
    c.icon(139, 746, "workflow", TEAL, 26)
    c.text(184, 749, "SHARED EXPECTATIONS", 13, TEAL, bold=True)
    c.text(184, 777, "Structured logs · metrics / traces · configuration · security · test evidence", 15, INK)
    c.arrow("M1340 680 V850 H347 V895", "teal")
    c.label(645, 843, "data operations", TEAL, 13)
    c.arrow("M1550 680 V878 H892 V895", "teal")
    c.label(1115, 870, "external API calls", TEAL, 13)
    c.arrow("M1670 835 V895", "gray", dash=True)
    c.label(1698, 870, "runtime", size=12)
    c.card(120, 900, 455, 150, "Data store", ["Database or storage as needed"], "database", "PERSISTENCE", TEAL, body_size=16)
    c.card(665, 900, 455, 150, "External systems", ["Services and integrations as needed"], "network", "INTEGRATION", TEAL, body_size=16)
    c.card(1210, 900, 470, 150, "Runtime and telemetry", ["Hosting, scaling, and operations profile"], "settings-2", "PLATFORM", BLUE, body_size=16)
    c.footer("03", "Illustrative view: boxes represent responsibilities, not a microservice decision. Arrows show runtime interaction.")
    c.save("03-project-architecture")


def system_map():
    c = Canvas("How the system works", "Proposed target · who decides, who builds, who checks", 1150)
    c.character(64, 180, 380, 104, "cooper")
    c.character(520, 180, 380, 104, "voltran")
    c.character(976, 180, 380, 104, "raymond")
    c.zone(64, 360, 1240, 450, "WORK SERVER  ·  your machine", "server")
    c.zone(1330, 360, 406, 450, "GPU SERVER", "nvidia")
    c.character(100, 420, 300, 104, "mccall")
    c.node(480, 420, 340, 104, "Forge", "Forgejo · repo · issues · PRs", "forgejo", BLUE)
    c.character(940, 420, 320, 104, "debora", "Python program")
    c.character(100, 640, 300, 104, "teresa")
    c.node(480, 640, 340, 104, "Argo CD", "Deploys staging · prod", "argo", BLUE)
    c.character(940, 640, 320, 104, "patrick")
    c.character(1356, 640, 354, 104, "dembe")
    c.node(100, 860, 300, 90, "GitHub", "Code copy only", "github", BLUE, 19)
    c.text(440, 912, "The standards repository lives on GitHub. Projects only mirror their code there.", 15, MUTED)
    c.arrow("M444 232 H515", "amber")
    c.arrow("M640 284 V415", "purple")
    c.arrow("M820 455 H935")
    c.arrow("M940 495 H825", "teal")
    c.arrow("M1100 524 V635")
    c.arrow("M1260 692 H1351", "purple", start=True)
    c.arrow("M480 472 H405", "teal")
    c.arrow("M740 524 V635", "teal")
    c.arrow("M1166 284 V340 H760 V415", "purple")
    c.arrow("M254 284 V340 H560 V415", "amber")
    c.arrow("M600 524 V588 H250 V635", "gray")
    c.arrow("M250 744 V855", "gray")
    steps = [
        (480, 232, 480, 208, "idea", AMBER), (640, 360, 700, 318, "issues", PURPLE),
        (878, 455, 878, 431, "pick", BLUE), (1100, 580, 1172, 585, "sandbox", BLUE),
        (1305, 692, 1305, 668, "prompts", PURPLE),
        (878, 495, 878, 535, "pull request", TEAL), (442, 472, 442, 448, "checks", TEAL),
        (960, 340, 960, 316, "review", PURPLE), (400, 340, 400, 316, "approve · merge", AMBER),
        (740, 580, 800, 585, "deploy", TEAL), (250, 820, 316, 825, "mirror", SLATE),
    ]
    for number, (bx, by, lx, ly, name, color) in enumerate(steps, 1):
        inside = 360 < ly < 810
        c.label(lx, ly, name, color, 14, "#EAF1FE" if inside else "#F4F7FC")
        c.badge(bx, by, number)
    c.rect(64, 975, 1672, 60, "#FFFFFF", BORDER, radius=14)
    names = ["Idea", "Issues", "Pick", "Sandbox", "Generate", "PR", "Checks", "Review", "Merge", "Deploy", "Mirror"]
    for number, name in enumerate(names, 1):
        x = 100 + (number - 1) * 152
        c.badge(x, 1005, number)
        c.text(x + 24, 1011, name, 16, INK, bold=True)
    c.footer("04", "Proposed target; the platform, gates and deployment were tried on a sandbox cluster. Names: see the cast (08).", brands=True)
    c.save("04-system-map")


def lifecycle():
    c = Canvas("Who does what", "Proposed lifecycle · owner, output and gate for every stage", 900)
    stages = [
        ("Discover", "lightbulb", AMBER, ["cooper", "voltran"], ["Brief"], "Scope agreed"),
        ("Specify", "list-checks", BLUE, ["voltran", "cooper"], ["Requirements", "+ examples"], "RQ rules"),
        ("Design", "pencil-ruler", PURPLE, ["voltran", "cooper"], ["Architecture", "+ UI packet"], "AR · U rules"),
        ("Plan", "square-kanban", PURPLE, ["voltran"], ["Issues", "in Forge"], "G0 Ready"),
        ("Build", "code-xml", TEAL, ["debora", "patrick"], ["Code + tests"], "G1 Local"),
        ("Verify", "shield-check", TEAL, ["mccall", "raymond"], ["Checks", "+ verdict"], "G2 · G3"),
        ("Release", "rocket", BLUE, ["cooper"], ["Merged", "change"], "G4 · G5"),
    ]
    for y, name in [(250, "STAGE"), (395, "WHO"), (515, "OUTPUT"), (608, "GATE")]:
        c.text(64, y, name, 13, MUTED, bold=True)
    for n, (title, icon, color, owners, output, gate) in enumerate(stages):
        x = 190 + n * 222
        mid = x + 104
        c.rect(x, 185, 208, 125, "#FFFFFF", BORDER, shadow=True)
        c.rect(mid - 29, 200, 58, 58, TINTS[color], radius=14)
        c.icon(mid - 17, 212, icon, color, 34)
        c.text(mid, 292, title, 20, INK, bold=True, anchor="middle")
        if n < len(stages) - 1:
            c.arrow(f"M{x + 209} 247 H{x + 221}", "gray", width=2)
        c.rect(x, 335, 208, 110, "#FFFFFF", BORDER, radius=14)
        for k, key in enumerate(owners):
            c.avatar(mid + (k - (len(owners) - 1) / 2) * 96, 352, key)
        c.rect(x, 470, 208, 78, "#EEF2F8", radius=14)
        for k, line in enumerate(output):
            assert measure(line, 16, True) < 196, line
            c.text(mid, 516 + (k - (len(output) - 1) / 2) * 22, line, 16, INK, bold=True, anchor="middle")
        c.pill(mid, 588, gate, color)
    c.arrow("M1404 630 V690 H1182 V630", "gray", dash=True)
    c.label(1293, 690, "repair", size=14)
    c.arrow("M1626 630 V745 H294 V630", "gray", dash=True)
    c.label(960, 745, "lessons become standard changes", size=14)
    c.footer("05", "Cooper approves scope, requirements, design and merge. Gates block the next stage until they pass.", brands=True)
    c.save("05-who-does-what")


def placement():
    c = Canvas("Where it runs", "Proposed placement · three places, each with its own credentials", 1090)
    c.character(90, 185, 380, 100, "cooper", "Laptop · browser")
    c.node(710, 185, 380, 100, "Voltran · Raymond", "Claude · called on demand", "claude")
    c.node(1330, 185, 380, 100, "GitHub", "Standards · code mirror", "github")
    c.arrow("M470 235 H705", "amber")
    c.zone(64, 380, 1026, 470, "WORK SERVER  ·  no GPU", "server")
    c.zone(1150, 380, 586, 470, "GPU SERVER  ·  RunPod (pilot)", "nvidia")
    c.arrow("M760 285 V318 H520 V455", "purple")
    c.label(640, 318, "plan · review", PURPLE)
    c.arrow("M680 455 V350 H1520 V290", "gray")
    c.label(1150, 350, "Teresa · scheduled mirror", SLATE)
    c.character(100, 460, 300, 110, "debora", "Python program")
    c.node(430, 460, 300, 110, "Forge", "Forgejo", "forgejo", BLUE, 19)
    c.character(760, 460, 300, 110, "mccall")
    c.rect(112, 628, 300, 110, "#FFFFFF", BORDER)
    c.rect(106, 634, 300, 110, "#FFFFFF", BORDER)
    c.character(100, 640, 300, 110, "patrick", "1 task = 1 sandbox")
    c.node(430, 640, 300, 110, "Registry", "Forgejo · by digest", "package", BLUE, 19)
    c.node(760, 640, 300, 110, "Staging · prod", "Argo CD deploys", "argo", BLUE, 19)
    c.arrow("M400 515 H425", "blue")
    c.arrow("M730 515 H755", "teal")
    c.arrow("M250 570 V625")
    c.arrow("M910 570 V605 H600 V635", "teal")
    c.arrow("M730 695 H755", "teal")
    c.node(1190, 460, 506, 110, "Model weights", "Pinned version", "hard-drive", PURPLE)
    c.character(1190, 640, 506, 110, "dembe", "vLLM · serves the Qwen model")
    c.arrow("M1440 570 V640", "gray", end=False)
    c.arrow("M250 750 V800 H1440 V755", "purple", start=True)
    c.label(1120, 800, "API key only", PURPLE, fill="#EAF1FE")
    c.icon(1036, 789, "lock", PURPLE, 22)
    c.rect(64, 885, 1672, 90, "#FFFFFF", BORDER, radius=15)
    c.text(86, 912, "BUILT AND REBUILT FROM CODE", 13, MUTED, bold=True)
    for x, name, icon in [(86, "Terraform", "terraform"), (370, "k3s", "k3s"), (600, "Argo CD · Workflows", "argo"),
                          (930, "Forgejo", "forgejo"), (1170, "Woodpecker", "shield-check"), (1450, "vLLM", "vllm")]:
        c.mark(x, 928, icon, TEAL, 28)
        c.text(x + 42, 949, name, 18, INK)
    c.footer("06", "Proposed placement; tried on a sandbox cluster, no server ordered yet. Patrick holds no git token.", brands=True)
    c.save("06-where-it-runs")


STATUS = {
    "tried": ("TRIED IN SANDBOX", TEAL),
    "partly": ("PARTLY TRIED", AMBER),
    "built": ("BUILT · NOT USED YET", BLUE),
    "missing": ("NOT BUILT", SLATE),
}


def project_start():
    c = Canvas("How a project runs", "Today's flow · from an idea to production, with what exists and what is missing", 1150)
    steps = [
        ("Idea", "Cooper", "Describes the product in plain words", "lightbulb", AMBER, None),
        ("Discovery", "Voltran asks · Cooper answers", "11 stages, each approved before the next", "messages-square", AMBER, "built"),
        ("Specify and design", "Voltran writes · Cooper approves", "Requirements · architecture · UI packet", "pencil-ruler", PURPLE, "built"),
        ("Tasks in Forge", "Voltran plans · Cooper merges", "Plan file becomes issues; ready when deps merge", "square-kanban", PURPLE, "tried"),
        ("Project setup", "Platform scripts", "Deploy repo · bots · protection · Argo CD", "settings-2", BLUE, "tried"),
        ("Build", "Debora + Patrick", "One issue, one sandbox, one pull request", "hammer", TEAL, "partly"),
        ("Review and merge", "McCall · Raymond · Cooper", "Checks pass, review, only Cooper merges", "git-merge", TEAL, "partly"),
        ("Release", "McCall · Argo CD · Cooper", "Staging automatic, prod by approved PR", "rocket", BLUE, "tried"),
    ]
    notes = {
        "Build": "stand-in builder; real Qwen not tried",
        "Review and merge": "Raymond review is manual",
    }
    c.text(190, 180, "STEP", 13, MUTED, bold=True)
    c.text(520, 180, "WHO", 13, MUTED, bold=True)
    c.text(900, 180, "WHAT HAPPENS", 13, MUTED, bold=True)
    c.text(1600, 180, "STATUS", 13, MUTED, bold=True, anchor="middle")
    c.arrow("M90 230 V880", "gray", width=1.2, end=False)
    for n, (title, who, what, icon, color, status) in enumerate(steps):
        y = 198 + n * 88
        missing = status == "missing"
        if missing:
            c.rect(120, y, 1616, 76, "#F8FAFD", "#9AA8BC", radius=14, dash=True)
        else:
            c.rect(120, y, 1616, 76, "#FFFFFF", BORDER, radius=14, shadow=True)
        c.badge(90, y + 38, n + 1)
        c.rect(140, y + 12, 52, 52, "#F3F5F9" if missing else TINTS[color], radius=12)
        c.icon(152, y + 24, icon, SLATE if missing else color, 28)
        for value, width, size, bold in ((title, 300, 20, True), (who, 270, 16, False), (what, 470, 16, False)):
            assert measure(value, size, bold) < width, value
        c.text(214, y + 45, title, 20, INK, bold=True)
        faces = sorted((key for key in CAST if CAST[key][0] in who), key=lambda k: who.index(CAST[k][0]))
        for k, key in enumerate(faces):
            c.portrait(520 + k * 30, y + 22, key, 32)
        c.text(520 + (len(faces) * 30 + 10 if faces else 0), y + 45, who, 16, INK)
        c.text(900, y + (38 if title in notes else 45), what, 16, MUTED)
        if title in notes:
            c.text(900, y + 60, notes[title], 14, AMBER, bold=True)
        if status:
            label, tone = STATUS[status]
            c.pill(1600, y + 23, label, tone, 13)
    for n in (1, 2, 3, 6):
        c.icon(486, 198 + n * 88 + 27, "circle-check", AMBER, 22)
    c.rect(64, 920, 1672, 112, "#FFFFFF", BORDER, radius=16)
    c.icon(86, 942, "lock", SLATE, 22)
    c.text(120, 960, "NOT BUILT YET, OUTSIDE THE STEPS ABOVE", 13, SLATE, bold=True)
    c.text(120, 992, "Pull-request previews · migrations as a pre-sync job · secrets manager · staging smoke test before the prod PR", 16, INK)
    c.icon(1380, 942, "circle-check", AMBER, 22)
    c.text(1412, 960, "= Cooper approves here", 15, INK)
    c.footer("07", "Status as of 21 November 2026. Tried means run end to end on a temporary sandbox cluster, not on a real server.", brands=True)
    c.save("07-project-start")


def release_path():
    c = Canvas("From merge to production", "Tried in a sandbox · one image, built once, promoted by digest", 1070)
    c.character(64, 190, 420, 104, "cooper", "Approves and merges the PR")
    c.character(580, 190, 440, 104, "mccall", "Checks again · builds image once")
    c.node(1116, 190, 420, 104, "Forgejo registry", "image @ sha256 digest", "package", BLUE)
    c.arrow("M484 242 H575", "amber")
    c.label(530, 230, "main", AMBER, 13)
    c.arrow("M1020 242 H1111", "teal")
    c.label(1066, 230, "push", TEAL, 13)
    c.zone(64, 360, 1672, 230, "DEPLOY REPOSITORY  ·  one per project", "forgejo", BLUE)
    c.node(110, 430, 520, 120, "overlays/staging", "Release bot writes the digest", "git-branch", TEAL)
    c.node(800, 430, 520, 120, "overlays/prod", "Pull request · Cooper merges", "git-pull-request", AMBER)
    c.node(1380, 430, 300, 120, "Everything else", "Cooper merges", "lock", SLATE, 19)
    c.arrow("M800 294 V335 H560 V425", "teal")
    c.label(680, 335, "digest", TEAL, 13)
    c.arrow("M630 490 H795", "amber")
    c.label(712, 478, "promote", AMBER, 13, "#EAF1FE")
    c.node(520, 650, 420, 110, "Argo CD", "The only one that deploys", "argo", BLUE)
    c.arrow("M370 550 V615 H660 V645", "blue")
    c.arrow("M1060 550 V615 H800 V645", "blue")
    c.label(730, 615, "sync", BLUE, 13)
    c.node(1100, 630, 400, 90, "Staging", "Automatic after each merge", "kubernetes", TEAL, 19)
    c.node(1100, 740, 400, 90, "Prod", "Only the approved digest", "kubernetes", AMBER, 19)
    c.arrow("M940 680 H1095", "blue")
    c.arrow("M940 730 H1020 V785 H1095", "blue")
    c.arrow("M1536 242 H1710 V785 H1505", "gray", dash=True)
    c.label(1710, 700, "pull by digest", SLATE, 13)
    c.rect(64, 875, 1672, 110, "#FFFFFF", BORDER, radius=16)
    guards = [
        (90, "Agents never merge or push to main"),
        (650, "Release token: push events only, refused to PRs"),
        (1230, "No agent holds cluster credentials"),
    ]
    for x, text in guards:
        c.icon(x, 912, "lock", "#B42318", 24)
        assert measure(text, 17) < 500, text
        c.text(x + 36, 931, text, 17, INK)
    c.text(90, 966, "Each was tried: the bot's merge, its push to prod and a PR reading the token were all refused.", 15, MUTED)
    c.footer("10", "Tried end to end on a sandbox cluster on 21 November 2026; not yet on a real server.", brands=True)
    c.save("10-release-path")


def cast():
    c = Canvas("The cast", "Proposed roles · one name and one avatar for each actor", 1000)
    never = {
        "cooper": "Reminds agents to test",
        "voltran": "Writes the implementation",
        "raymond": "Approves its own work",
        "debora": "Makes product decisions",
        "patrick": "Pushes or picks tasks",
        "mccall": "Waives a failing check",
        "dembe": "Holds code or git tokens",
        "teresa": "Carries issues, PRs or CI",
    }
    does = {
        "cooper": "Decides and approves",
        "voltran": "Plans and splits work",
        "raymond": "Reviews each pull request",
        "debora": "Hands out tasks, sets limits",
        "patrick": "Builds one task + tests",
        "mccall": "Runs checks on every PR",
        "dembe": "Serves the model",
        "teresa": "Copies code to GitHub",
    }
    for n, key in enumerate(CAST):
        name, role, runs, icon, color = CAST[key]
        x, y = 64 + (n % 4) * 424, 185 + (n // 4) * 330
        c.rect(x, y, 400, 300, "#FFFFFF", BORDER, shadow=True)
        c.portrait(x + 22, y + 22, key, 84)
        c.text(x + 120, y + 52, role, 13, color, bold=True)
        c.text(x + 120, y + 86, name, 28, INK, bold=True)
        assert measure(runs, 16) < 352, runs
        c.text(x + 24, y + 145, runs, 16, MUTED)
        c.arrow(f"M{x + 24} {y + 170} H{x + 376}", "gray", width=.6, end=False)
        c.icon(x + 24, y + 192, "circle-check", TEAL, 22)
        c.text(x + 58, y + 210, does[key], 16, INK)
        c.icon(x + 24, y + 238, "lock", "#B42318", 22)
        c.text(x + 58, y + 256, "Never: " + never[key], 16, INK)
        assert measure("Never: " + never[key], 16) < 330, key
    c.rect(64, 860, 1672, 54, "#EAF1FE", "#B8C9E8", radius=12)
    c.brand(86, 873, "forgejo", 26)
    c.text(126, 893, "Forge (Forgejo) is the shared place where repositories, issues and pull requests live. It is a place, not an actor.", 16, INK)
    c.footer("08", "Characters name roles; products keep their own names. See docs/architecture/cast.md.", brands=True)
    c.save("08-cast")


def two_loops():
    c = Canvas("Two loops", "Proposed working rhythm · fast inside the sandbox, strict at acceptance", 1100)
    c.zone(64, 185, 870, 660, "INNER LOOP  ·  inside one sandbox  ·  minutes", "hammer", TEAL)
    c.zone(980, 185, 756, 660, "OUTER LOOP  ·  acceptance in Forge", "shield-check", TEAL)
    c.node(100, 270, 360, 104, "Edit code", "From the issue and examples", "code-xml", TEAL)
    c.node(530, 270, 370, 104, "Run checks", "Same scripts as CI", "flask-conical", TEAL)
    c.node(530, 455, 370, 104, "Commit", "Only when checks pass", "git-branch", TEAL)
    c.node(530, 640, 370, 104, "Preview", "Planned · not built", "kubernetes", SLATE, dashed=True)
    c.node(100, 640, 360, 104, "Try it", "Cooper or a tester", "user-round", AMBER, dashed=True)
    c.character(100, 455, 360, 104, "patrick", "Runs this loop")
    c.arrow("M460 322 H525", "teal")
    c.arrow("M715 374 V450", "teal")
    c.arrow("M715 559 V635", "gray", dash=True)
    c.arrow("M530 692 H465", "gray", dash=True)
    c.arrow("M280 640 V564", "gray", dash=True)
    c.label(320, 602, "feedback", size=13, fill="#EAF1FE")
    c.arrow("M280 455 V379", "gray", dash=True)
    c.arrow("M900 322 H975", "blue")
    c.label(938, 300, "done", BLUE, 13)
    c.character(1016, 270, 330, 104, "debora", "Pushes · opens PR")
    c.character(1016, 410, 330, 104, "mccall", "Same checks, clean")
    c.character(1016, 550, 330, 104, "raymond", "Reviews the PR")
    c.character(1016, 690, 330, 104, "cooper", "Approves · merges")
    for y in (374, 514, 654):
        c.arrow(f"M1181 {y} V{y + 31}", "teal")
    c.arrow("M1016 462 H944", "gray", dash=True)
    c.label(976, 492, "fail → fix", size=13, fill="#EAF1FE")
    c.node(1390, 410, 320, 104, "Release", "Staging · prod PR", "argo", BLUE)
    c.arrow("M1346 715 H1366 V462 H1385", "blue")
    c.character(1390, 690, 320, 104, "teresa", "Scheduled push")
    c.arrow("M1346 742 H1385", "gray")
    c.node(1390, 910, 320, 90, "GitHub", "Code copy only", "github", BLUE, 19)
    c.arrow("M1550 794 V905", "gray")
    c.label(1550, 860, "only this leaves your servers", SLATE, 13)
    c.text(100, 905, "Inner loop: no CI wait. Outer loop: nothing merges without passing checks and approval.", 17, INK, bold=True)
    c.text(100, 935, "The checks are scripts in the repository, so the same command runs in the sandbox and in CI.", 16, MUTED)
    c.footer("09", "Proposed working rhythm; target times are measured in the pilot, not promised.", brands=True)
    c.save("09-two-loops")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    views = {"01": process, "02": agents, "03": application, "04": system_map,
             "05": lifecycle, "06": placement, "07": project_start, "08": cast, "09": two_loops,
             "10": release_path}
    for number in sys.argv[1:] or views:
        views[number]()
