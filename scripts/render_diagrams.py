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
BRAND_COLORS = {
    "ansible": "#EE0000", "claude": "#D97757", "docker": "#2496ED", "github": "#181717",
    "githubactions": "#2088FF", "hetzner": "#D50C2D", "kubernetes": "#326CE5",
    "nvidia": "#76B900", "terraform": "#844FBA",
}
TINTS = {"#2563EB": "#EDF3FF", "#087F8C": "#E3F4F5", "#7756C8": "#F1ECFB", "#A76608": "#FFF2D9"}
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

    def node(self, x, y, w, h, title, sub, icon, color=BLUE, title_size=21):
        """Compact card: one icon, a short title and at most one short line."""
        self.rect(x, y, w, h, "#FFFFFF", BORDER, shadow=True)
        branded = (BRANDS / f"{icon}.svg").exists()
        self.rect(x + 18, y + (h - 58) / 2, 58, 58, "#F3F5F9" if branded else TINTS[color], radius=14)
        self.mark(x + 30, y + (h - 34) / 2, icon, color, 34)
        assert measure(title, title_size, True) < w - 110, title
        assert measure(sub, 15) < w - 110, sub
        self.text(x + 94, y + h / 2 - (2 if sub else -7), title, title_size, INK, bold=True)
        if sub:
            self.text(x + 94, y + h / 2 + 22, sub, 15, MUTED)

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
    c.card(64, 180, 350, 145, "Gökhan", ["Goals, priorities, material decisions"], "user-round", "PRODUCT OWNER", AMBER, "#FFF2D9", 16)
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
    c = Canvas("How the system works", "Proposed target · who decides, who builds, who checks", 1100)
    c.node(90, 190, 400, 106, "You", "Idea · decisions · approval", "user-round", AMBER)
    c.node(700, 190, 400, 106, "Claude", "Architect · reviewer", "claude")
    c.node(1310, 190, 400, 106, "GitHub", "Repo · issues · CI", "github")
    c.node(700, 410, 400, 110, "Coordinator", "Assigns · checks gates", "workflow", BLUE)
    c.zone(64, 640, 1672, 260, "YOUR SERVERS", "server")
    c.arrow("M490 243 H695", "amber")
    c.arrow("M1100 243 H1305")
    c.arrow("M1420 296 V465 H1105")
    c.arrow("M900 520 V745")
    c.arrow("M700 805 H535", "purple", start=True)
    c.arrow("M1000 750 V590 H1600 V301", "teal")
    c.arrow("M1100 805 H1265", "teal")
    c.arrow("M900 410 V301", "purple", start=True)
    c.arrow("M700 465 H290 V301", "amber")
    c.node(130, 750, 400, 110, "Open model", "GPU server", "cpu", PURPLE)
    c.node(700, 750, 400, 110, "Coding agents", "One task each", "bot", TEAL)
    c.node(1270, 750, 400, 110, "Test cluster", "Preview · smoke", "kubernetes")
    steps = [
        (592, 243, 592, 216, "idea", AMBER), (1202, 243, 1202, 216, "plan · tasks", BLUE),
        (1420, 380, 1262, 448, "tasks · evidence", BLUE), (900, 580, 828, 585, "one task", BLUE),
        (617, 805, 617, 778, "prompts", PURPLE), (1300, 590, 1300, 563, "pull request", TEAL),
        (1182, 805, 1182, 778, "preview", TEAL), (900, 355, 968, 360, "review", PURPLE),
        (495, 465, 495, 438, "accept · blocked", AMBER),
    ]
    for number, (bx, by, lx, ly, name, color) in enumerate(steps, 1):
        inside = ly > 640
        c.label(lx, ly, name, color, 14, "#EAF1FE" if inside else "#F4F7FC")
        c.badge(bx, by, number)
    c.rect(64, 930, 1672, 62, "#FFFFFF", BORDER, radius=14)
    names = ["Idea", "Plan", "Ready task", "Assign", "Generate", "Pull request", "Preview", "Review", "Accept"]
    for number, name in enumerate(names, 1):
        x = 110 + (number - 1) * 182
        c.badge(x, 961, number)
        c.text(x + 25, 967, name, 16, INK, bold=True)
    c.footer("04", "Proposed target architecture; not a running system.", brands=True)
    c.save("04-system-map")


def lifecycle():
    c = Canvas("Who does what", "Proposed lifecycle · owner, output and gate for every stage", 900)
    stages = [
        ("Discover", "lightbulb", AMBER, [("user-round", "You"), ("claude", "Claude")], ["Brief"], "Scope agreed"),
        ("Specify", "list-checks", BLUE, [("claude", "Claude"), ("user-round", "You")], ["Requirements", "+ examples"], "RQ rules"),
        ("Design", "pencil-ruler", PURPLE, [("claude", "Claude"), ("user-round", "You")], ["Architecture", "+ UI packet"], "AR · U rules"),
        ("Plan", "square-kanban", PURPLE, [("claude", "Claude")], ["Issues", "+ sub-issues"], "G0 Ready"),
        ("Build", "code-xml", TEAL, [("bot", "Agents"), ("workflow", "Coordinator")], ["Code + tests"], "G1 Local"),
        ("Verify", "shield-check", TEAL, [("githubactions", "CI"), ("claude", "Claude")], ["Evidence", "+ verdict"], "G2 · G3"),
        ("Release", "rocket", BLUE, [("user-round", "You"), ("workflow", "Coordinator")], ["Running", "version"], "G4 · G5"),
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
        for k, (owner_icon, owner) in enumerate(owners):
            ox = mid + (k - (len(owners) - 1) / 2) * 96
            owner_color = AMBER if owner == "You" else TEAL if owner == "Agents" else BLUE
            c.mark(ox - 16, 352, owner_icon, owner_color, 32)
            assert measure(owner, 14) < 94, owner
            c.text(ox, 412, owner, 14, INK, anchor="middle")
        c.rect(x, 470, 208, 78, "#EEF2F8", radius=14)
        for k, line in enumerate(output):
            assert measure(line, 16, True) < 196, line
            c.text(mid, 516 + (k - (len(output) - 1) / 2) * 22, line, 16, INK, bold=True, anchor="middle")
        c.pill(mid, 588, gate, color)
    c.arrow("M1404 630 V690 H1182 V630", "gray", dash=True)
    c.label(1293, 690, "repair", size=14)
    c.arrow("M1626 630 V745 H294 V630", "gray", dash=True)
    c.label(960, 745, "lessons become standard changes", size=14)
    c.footer("05", "You approve scope, requirements, design and release. Gates block the next stage until they pass.", brands=True)
    c.save("05-who-does-what")


def placement():
    c = Canvas("Where it runs", "Proposed placement · three places, each with its own credentials", 1090)
    c.node(90, 185, 380, 100, "You", "Laptop · browser", "user-round", AMBER)
    c.node(710, 185, 380, 100, "Claude", "Called on demand", "claude")
    c.node(1330, 185, 380, 100, "GitHub", "Repo · issues · CI", "github")
    c.arrow("M470 235 H705", "amber")
    c.arrow("M1090 235 H1325")
    c.zone(64, 380, 1026, 470, "WORK SERVER  ·  no GPU", "server")
    c.zone(1150, 380, 586, 470, "GPU SERVER", "nvidia")
    c.arrow("M360 460 V330 H800 V290", "purple")
    c.label(580, 330, "plan · review", PURPLE)
    c.arrow("M640 446 V352 H1520 V290", "teal")
    c.label(1150, 352, "scoped token", TEAL)
    c.icon(1056, 340, "lock", TEAL, 22)
    c.arrow("M400 515 H425")
    c.arrow("M724 515 H755", "teal")
    c.arrow("M250 570 V635", "gray")
    c.arrow("M910 570 V635", "gray")
    c.arrow("M580 756 V800 H1440 V756", "purple", start=True)
    c.label(1120, 800, "private network", PURPLE, fill="#EAF1FE")
    c.icon(1020, 789, "lock", PURPLE, 22)
    c.arrow("M1440 570 V640", "gray", end=False)
    c.node(100, 460, 300, 110, "Coordinator", "Assigns tasks", "workflow", BLUE, 19)
    c.rect(442, 448, 280, 110, "#FFFFFF", BORDER)
    c.rect(436, 454, 280, 110, "#FFFFFF", BORDER)
    c.node(430, 460, 280, 110, "Sandboxes", "1 task = 1 box", "docker", TEAL, 19)
    c.node(760, 460, 300, 110, "Test cluster", "kind", "kubernetes", BLUE, 19)
    c.node(100, 640, 300, 110, "Task ledger", "Claims · attempts", "database", BLUE, 19)
    c.node(430, 640, 300, 110, "Coding agents", "Run in sandboxes", "bot", TEAL, 19)
    c.node(760, 640, 300, 110, "Preview apps", "Per pull request", "globe", BLUE, 19)
    c.arrow("M570 640 V572", "gray", end=False)
    c.node(1190, 460, 506, 110, "Model weights", "Pinned version", "hard-drive", PURPLE)
    c.node(1190, 640, 506, 110, "Model server", "Serves the open model", "cpu", PURPLE)
    c.rect(64, 885, 1672, 90, "#FFFFFF", BORDER, radius=15)
    c.text(86, 912, "BUILT AND REBUILT FROM CODE", 13, MUTED, bold=True)
    for x, name, icon in [(86, "Terraform", "terraform"), (420, "Ansible", "ansible"), (720, "Docker", "docker"),
                          (1010, "Kubernetes", "kubernetes"), (1340, "Hetzner (candidate)", "hetzner")]:
        c.brand(x, 928, icon, 28)
        c.text(x + 42, 949, name, 18, INK)
    c.footer("06", "Proposed placement; no server has been ordered or installed. Provider and tools are candidates.", brands=True)
    c.save("06-where-it-runs")


def project_start():
    c = Canvas("How a project starts", "Proposed sequence · from an idea to the first accepted change", 1010)
    steps = [
        ("Idea", "You", "lightbulb", AMBER),
        ("Discovery talk", "You + Claude", "messages-square", AMBER),
        ("Requirements", "Claude writes · you approve", "list-checks", BLUE),
        ("Design", "Architecture + UI packet", "pencil-ruler", PURPLE),
        ("Repo + issues", "Coordinator creates", "github", BLUE),
        ("Environment", "Sandbox · preview", "container", BLUE),
        ("First task", "Agent builds · CI checks", "bot", TEAL),
        ("Accepted", "Claude reviews · you accept", "circle-check", TEAL),
    ]
    spots = [(64 + k * 424, 200) for k in range(4)] + [(64 + k * 424, 430) for k in range(3, -1, -1)]
    for number, ((x, y), (title, sub, icon, color)) in enumerate(zip(spots, steps), 1):
        c.node(x, y, 400, 120, title, sub, icon, color)
        c.badge(x + 8, y + 8, number)
    for k in range(3):
        c.arrow(f"M{464 + k * 424} 260 H{483 + k * 424}", "gray")
        c.arrow(f"M{1336 - k * 424} 490 H{1317 - k * 424}", "gray")
    c.arrow("M1536 320 V425", "gray")
    for x, y in [(1260, 200), (1684, 200), (464, 430)]:
        c.pill(x - 62, y - 15, "you approve", AMBER, 12)
    c.rect(64, 620, 1672, 250, "#FFFFFF", BORDER, radius=18)
    c.brand(90, 645, "github", 26)
    c.text(128, 665, "HOW TASKS ARE STORED", 14, BLUE, bold=True)
    tree = [
        (120, "Journey", "What the user achieves", "route", AMBER),
        (660, "Task", "One slice + its tests", "square-kanban", BLUE),
        (1200, "Sub-task", "Only when needed", "list-checks", TEAL),
    ]
    for x, title, sub, icon, color in tree:
        c.node(x, 710, 440, 110, title, sub, icon, color)
    c.arrow("M560 765 H655", "gray")
    c.arrow("M1100 765 H1195", "gray")
    c.footer("07", "Every task carries its own tests. A task with an open decision is not dispatched.", brands=True)
    c.save("07-project-start")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    views = {"01": process, "02": agents, "03": application, "04": system_map,
             "05": lifecycle, "06": placement, "07": project_start}
    for number in sys.argv[1:] or views:
        views[number]()
