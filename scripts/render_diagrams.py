#!/usr/bin/env python3
"""Render the proposed SDLC views as standalone SVG and PNG files.

Requires Python, Pillow and Inkscape. Assets are local; rendering uses no network.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
import os
import re
import subprocess

from PIL import Image, ImageFont, PngImagePlugin

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs/diagrams"
ASSETS = OUT / "assets/lucide"
LICENSE = (ASSETS / "LICENSE").read_text()
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
        self.text(64, 34, "AGENTIC SDLC  /  TASARIM GÖRÜNÜMLERİ", 13, "#A7BEDA", bold=True)
        self.text(64, 82, title, 36, "#FFFFFF", bold=True)
        self.text(64, 116, subtitle, 17, "#C4D1E4")
        self.rect(1510, 44, 225, 43, "#FFF0CD", radius=21)
        self.text(1622, 71, "TASLAK · v0.1", 17, "#805100", bold=True, anchor="middle")

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

    def arrow(self, path, name="blue", dash=False, width=2.4, end=True):
        colors = {"blue": BLUE, "teal": TEAL, "purple": PURPLE, "gray": "#8292A8", "amber": AMBER}
        dash_attr = 'stroke-dasharray="7 6"' if dash else ''
        marker_attr = f'marker-end="url(#{name})"' if end else ''
        self.parts.append(f'<path d="{path}" fill="none" stroke="{colors[name]}" stroke-width="{width}" '
                          f'stroke-linecap="round" stroke-linejoin="round" '
                          f'{dash_attr} {marker_attr}/>')

    def label(self, x, y, value, color=MUTED, size=14):
        width = measure(value, size) + 20
        self.rect(x - width / 2, y - size, width, size + 10, "#F4F7FC", radius=5)
        self.text(x, y + 2, value, size, color, anchor="middle")

    def footer(self, number, note):
        y = self.height - 64
        self.arrow(f"M64 {y} H1736", "gray", width=.6, end=False)
        self.text(64, y + 29, note, 14, MUTED)
        self.text(64, y + 49, "İkonlar: Lucide / Feather · ISC / MIT · Kaynak ve lisans repoda", 11, MUTED)
        self.text(1736, y + 30, f"AGENTIC SDLC  /  {number}", 13, MUTED, bold=True, anchor="end")

    def save(self, name):
        self.parts.append('</svg>')
        svg = OUT / f"{name}.svg"
        png = OUT / f"{name}.png"
        svg.write_text("\n".join(self.parts) + "\n")
        env = dict(os.environ, XDG_CACHE_HOME="/tmp/agentic-sdlc-diagram-cache")
        subprocess.run(["inkscape", str(svg), "--export-type=png", "--export-width=1800", f"--export-filename={png}"],
                       check=True, env=env, capture_output=True)
        with Image.open(png) as image:
            info = PngImagePlugin.PngInfo()
            info.add_text("Description", "Agentic SDLC taslak mimari görünümü v0.1")
            info.add_text("Icon licenses", LICENSE)
            image.convert("RGB").save(png, optimize=True, pnginfo=info)
        print(f"{name}: SVG + PNG")


def process():
    c = Canvas("Proje fikrinden doğrulanmış teslimata", "Önerilen yaşam döngüsü · kararlar ve geri bildirim akışı")
    c.rect(64, 183, 1672, 70, "#E7EEF9", radius=15)
    c.icon(86, 204, "file-text", BLUE, 28)
    c.text(132, 211, "GİRDİ", 12, BLUE, bold=True)
    c.text(132, 236, "Proje dokümanı + ortak mühendislik standartları + çalışma ayarları", 21, INK, bold=True)
    stages = [
        (64, 310, "Fikri ve bağlamı anla", ["Proje dokümanını oku", "Eksikleri ve varsayımları çıkar", "Kullanıcı senaryolarını belirle"], "file-text", "01 · BAĞLAM", BLUE),
        (650, 310, "Gereksinimleri netleştir", ["MVP, kapsam ve kapsam dışı işler", "Kabul kriterleri ve kalite hedefleri", "Güvenlik / performans beklentileri"], "list-checks", "02 · GEREKSİNİMLER", BLUE),
        (1236, 310, "Mimariyi tasarla", ["UI akışları, API ve veri sınırları", "Dil ve framework profilleri", "Kararlar, gerekçeler ve diyagramlar"], "layers", "03 · TASARIM", PURPLE),
        (1236, 640, "Repo ve görevleri hazırla", ["GitHub sahibi, repo yapısı ve şablon", "Bağımlılıklar ve kabul kriterleri", "Gereksinim → issue bağlantısı"], "git-branch", "04 · HAZIRLIK", PURPLE),
        (650, 640, "Geliştir ve doğrula", ["Kod + local test + CI", "Bağımsız review ve kabul kanıtı", "Bulgulara göre düzelt"], "flask-conical", "05 · UYGULAMA", TEAL),
        (64, 640, "Teslim et ve öğren", ["Sürüme bağlı doğrulama sonuçları", "Yayın / smoke / işletim bilgisi", "Öğrenilenleri standarda geri taşı"], "rocket", "06 · TESLİMAT", TEAL),
    ]
    for x, y, title, lines, icon, kicker, color in stages:
        c.card(x, y, 500, 190, title, lines, icon, kicker, color)
    for path in ["M564 405 H645", "M1150 405 H1231", "M1486 500 V635", "M1236 735 H1155", "M650 735 H569"]:
        c.arrow(path)
    c.label(607, 388, "senaryolar", size=12)
    c.label(1193, 388, "kriterler", size=12)
    c.label(1550, 570, "tasarım", size=13)
    c.label(1193, 718, "görevler", size=12)
    c.label(607, 718, "kanıt", size=12)
    c.rect(64, 548, 1086, 56, "#FFF2D9", "#EAD1A1", radius=12)
    c.icon(85, 562, "user-round", AMBER, 27)
    c.text(130, 581, "İNSAN YÖNLENDİRMESİ", 13, AMBER, bold=True)
    c.text(357, 581, "Kapsam · önemli tasarım kararları · sonuç değerlendirmesi", 17, INK)
    c.arrow("M900 830 V910 H28 V280 H900 V305", "gray", dash=True)
    c.label(660, 935, "Test / review bulguları planlamaya geri döner", size=17)
    c.text(64, 1005, "Düz ok: ana ilerleme     Kesikli ok: düzeltme döngüsü     Sarı alan: insanın karar ve yönlendirmesi", 16, MUTED)
    c.footer("01", "Süreç taslağıdır; seçilmiş bir framework veya çalışan otomasyon göstermez.")
    c.save("01-development-process")


def agents():
    c = Canvas("Ajanlar, bağlam ve araçlar birlikte nasıl çalışır?", "Önerilen sorumluluklar · koordinasyon · ortak çıktılar · araç sınırları", 1200)
    c.card(64, 180, 350, 145, "Gökhan", ["Amaç, öncelik ve önemli kararlar"], "user-round", "ÜRÜN SAHİBİ", AMBER, "#FFF2D9", 16)
    c.card(480, 180, 475, 145, "Proje dokümanı", ["Senaryolar, kapsam ve kısıtlar"], "file-text", "PROJEYE ÖZEL GİRDİ", BLUE)
    c.card(1040, 180, 696, 145, "Ortak kurallar ve çalışma ayarları", ["Dil / UI / test profilleri · GitHub · görev şeması"], "settings-2", "SÜRÜMLENEN BAĞLAM", PURPLE)
    c.arrow("M414 252 H475", "amber")
    c.arrow("M717 325 V367 H900 V405")
    c.arrow("M1388 325 V465 H1155", "purple")
    c.label(1390, 373, "standartlar / yetkiler", PURPLE)
    c.arrow("M239 325 V495 H645", "amber")
    c.label(432, 477, "kararlar / yönlendirme", AMBER)
    c.card(650, 410, 500, 170, "İş akışını koordine et", ["Sıradaki işi ve bağımlılıkları belirle", "Uygun rolü çağır, durumu kaydet", "Kesintide kaldığı yerden devam et"], "workflow", "KOORDİNASYON SORUMLULUĞU", BLUE)
    c.arrow("M900 580 V635", end=False)
    c.arrow("M254 635 H1544", end=False)
    roles = [
        (64, "Analiz ve ürün", ["Senaryolar · kapsam · kabul", "Gereksinimler ve açık sorular"], "list-checks", "ÜRÜN PERSPEKTİFİ", BLUE),
        (494, "Mimari ve UX", ["Sistem sınırları · kullanıcı akışı", "Kararlar ve diyagramlar"], "layers", "TASARIM PERSPEKTİFİ", PURPLE),
        (924, "Geliştirme", ["Kod · geliştirici testleri · PR", "Seçilen standartlara uyum"], "code-xml", "UYGULAMA PERSPEKTİFİ", TEAL),
        (1354, "Doğrulama ve review", ["Kabul kriterleri · bulgular", "Bağımsız doğrulama kanıtı"], "shield-check", "KALİTE PERSPEKTİFİ", TEAL),
    ]
    for x, title, lines, icon, kicker, color in roles:
        c.arrow(f"M{x + 190} 635 V695")
        c.card(x, 700, 380, 170, title, lines, icon, kicker, color, body_size=16)
        c.arrow(f"M{x + 190} 870 V906", "gray", width=1.8)
    c.rect(64, 911, 1672, 53, "#E7EEF9", radius=12)
    c.icon(84, 924, "file-text", BLUE, 25)
    c.text(128, 944, "PAYLAŞILAN DURUM VE ÇIKTILAR", 13, BLUE, bold=True)
    c.text(480, 944, "Gereksinimler · mimari / UX kararları · issue / PR · test raporları", 18, INK)
    c.arrow("M64 938 H28 V550 H645", "gray", dash=True)
    c.label(339, 573, "sonuç / durum geri bildirimi", size=14)
    c.rect(64, 1002, 1672, 90, "#FFFFFF", BORDER, radius=15)
    c.text(86, 1027, "ARAÇLAR  /  Erişim, rol ve göreve göre sınırlandırılır", 13, MUTED, bold=True)
    for x, name, icon in [(86, "GitHub", "git-branch"), (390, "Terminal / kod", "code-xml"), (720, "Test / CI", "flask-conical"), (1020, "Tarayıcı", "monitor"), (1330, "Dokümanlar", "file-text")]:
        c.icon(x, 1044, icon, BLUE, 26)
        c.text(x + 41, 1064, name, 18, INK)
    c.footer("02", "Roller sorumlulukları gösterir; ayrı ve sürekli çalışan ajan sayısı henüz belirlenmedi.")
    c.save("02-agent-structure")


def application():
    c = Canvas("Bir proje için üretilecek teknik mimari görünümü", "Örnek web uygulaması · teknoloji, servis sayısı ve deployment profili seçilmedi", 1200)
    c.card(64, 180, 350, 150, "Kullanıcı", ["Web arayüzünden işlem yapar"], "user-round", "AKTÖR", BLUE, body_size=16)
    c.card(540, 180, 430, 150, "Web arayüzü", ["Ekranlar, formlar ve kullanıcı akışları"], "monitor", "SUNUM", BLUE, body_size=16)
    c.card(1270, 180, 466, 150, "Kimlik hizmeti", ["Giriş ve oturum mekanizması"], "shield-check", "GEREKTİĞİNDE DIŞ SİSTEM", PURPLE)
    c.arrow("M414 255 H535")
    c.label(477, 238, "HTTPS", size=13)
    c.arrow("M970 255 H1265", "purple")
    c.label(1120, 238, "giriş / oturum", PURPLE)
    c.rect(64, 400, 1672, 435, "#EAF1FE", "#B8C9E8", dash=True)
    c.text(90, 434, "UYGULAMA SINIRI", 14, BLUE, bold=True)
    c.text(620, 434, "Mantıksal sorumluluklar · fiziksel servis sınırları tasarımda belirlenir", 16, MUTED)
    c.arrow("M755 330 V365 H347 V485")
    c.label(550, 352, "HTTPS / JSON")
    c.card(120, 490, 455, 190, "API / giriş katmanı", ["Kimlik, yetki ve girdi doğrulama", "Tutarlı yanıt ve hata sözleşmesi", "API / yetkilendirme testleri"], "server", "GİRİŞ SINIRI", BLUE)
    c.card(665, 490, 455, 190, "İş kuralları", ["Kullanım senaryoları ve davranış", "UI ve veri erişiminden ayrılmış", "Unit / davranış testleri"], "brain-circuit", "DOMAIN", PURPLE)
    c.card(1210, 490, 470, 190, "Veri ve entegrasyon", ["Veri ve dış servis bağlantıları", "Timeout / hata politikaları", "Integration / contract testleri"], "network", "ADAPTER'LAR", TEAL)
    c.arrow("M575 585 H660")
    c.label(620, 568, "çağrı", size=12)
    c.arrow("M1120 585 H1205", "purple")
    c.label(1165, 568, "arayüz", size=12)
    c.rect(120, 725, 1000, 74, "#FFFFFF", "#D5E1F3", radius=12)
    c.icon(139, 746, "workflow", TEAL, 26)
    c.text(184, 749, "ORTAK BEKLENTİLER", 13, TEAL, bold=True)
    c.text(184, 777, "Yapılandırılmış log · metrik / trace · konfigürasyon · güvenlik · test kanıtı", 15, INK)
    c.arrow("M1340 680 V850 H347 V895", "teal")
    c.label(645, 843, "veri işlemleri", TEAL, 13)
    c.arrow("M1550 680 V878 H892 V895", "teal")
    c.label(1115, 870, "dış API çağrıları", TEAL, 13)
    c.arrow("M1670 835 V895", "gray", dash=True)
    c.label(1698, 870, "ortam", size=12)
    c.card(120, 900, 455, 150, "Veri kaynağı", ["İhtiyaca göre veritabanı / depolama"], "database", "KALICI VERİ", TEAL, body_size=16)
    c.card(665, 900, 455, 150, "Dış sistemler", ["İhtiyaca göre servis ve entegrasyon"], "network", "ENTEGRASYON", TEAL, body_size=16)
    c.card(1210, 900, 470, 150, "Çalıştırma ve izleme", ["Ortam, ölçekleme ve işletim profili"], "settings-2", "PLATFORM", BLUE, body_size=16)
    c.footer("03", "Örnek görünüm: kutular mikroservis kararı değildir. Oklar çalışma zamanındaki etkileşimleri gösterir.")
    c.save("03-project-architecture")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    process()
    agents()
    application()
