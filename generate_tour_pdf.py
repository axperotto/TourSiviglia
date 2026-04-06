#!/usr/bin/env python3
"""
Generatore di PDF per il Tour di Siviglia e Córdoba
29 Aprile – 3 Maggio
"""

import io
import os
import urllib.request

import qrcode
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    Image,
    NextPageTemplate,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)

# ────────────────────────── PALETTE ──────────────────────────
GOLD = colors.HexColor("#C9A84C")
DARK_GOLD = colors.HexColor("#8B6914")
CREAM = colors.HexColor("#FDF6E3")
DARK_BROWN = colors.HexColor("#3E2723")
WARM_WHITE = colors.HexColor("#FFFDF7")
TERRACOTTA = colors.HexColor("#C0522A")
OLIVE = colors.HexColor("#6B7C3D")
LIGHT_GOLD = colors.HexColor("#F5E6C3")
BLUE_NIGHT = colors.HexColor("#1A2340")

PAGE_W, PAGE_H = A4  # 595.28 x 841.89

# ─────────────────────────── HELPERS ──────────────────────────


def fetch_image(url: str, fallback_color=LIGHT_GOLD, w_px=400, h_px=250) -> io.BytesIO:
    """Download an image from URL; return a BytesIO with JPEG data.
    On failure returns a solid-colour placeholder."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read()
        img = PILImage.open(io.BytesIO(data)).convert("RGB")
        img = img.resize((w_px, h_px), PILImage.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, "JPEG", quality=85)
        buf.seek(0)
        return buf
    except Exception:
        return _color_placeholder(fallback_color, w_px, h_px)


def _color_placeholder(color, w=400, h=250) -> io.BytesIO:
    """Create a solid-colour PIL image as JPEG BytesIO."""
    r = int(color.red * 255)
    g = int(color.green * 255)
    b = int(color.blue * 255)
    img = PILImage.new("RGB", (w, h), (r, g, b))
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    buf.seek(0)
    return buf


def make_qr(url: str, size: int = 120) -> io.BytesIO:
    qr = qrcode.QRCode(box_size=4, border=2)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((size, size), PILImage.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, "JPEG")
    buf.seek(0)
    return buf


def rl_image(buf: io.BytesIO, width=None, height=None) -> Image:
    """Wrap a BytesIO in a ReportLab Image flowable."""
    img = Image(buf, width=width, height=height)
    img.hAlign = "CENTER"
    return img


# ─────────────────────── DECORATIVE BORDER ────────────────────


def draw_ornate_border(canvas, doc):
    """Full-page decorative border for the cover."""
    canvas.saveState()
    # Outer gold rectangle
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(3)
    canvas.rect(12 * mm, 12 * mm, PAGE_W - 24 * mm, PAGE_H - 24 * mm, stroke=1, fill=0)
    # Inner thin line
    canvas.setStrokeColor(DARK_GOLD)
    canvas.setLineWidth(0.8)
    canvas.rect(14 * mm, 14 * mm, PAGE_W - 28 * mm, PAGE_H - 28 * mm, stroke=1, fill=0)
    # Corner ornaments
    for cx, cy in [
        (12 * mm, 12 * mm),
        (PAGE_W - 12 * mm, 12 * mm),
        (12 * mm, PAGE_H - 12 * mm),
        (PAGE_W - 12 * mm, PAGE_H - 12 * mm),
    ]:
        canvas.setFillColor(GOLD)
        canvas.circle(cx, cy, 3 * mm, fill=1)
    canvas.restoreState()


def draw_header_footer(canvas, doc):
    """Subtle header/footer for body pages."""
    canvas.saveState()
    # Top gold line
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(1.5)
    canvas.line(20 * mm, PAGE_H - 14 * mm, PAGE_W - 20 * mm, PAGE_H - 14 * mm)
    # Bottom gold line + page number
    canvas.line(20 * mm, 14 * mm, PAGE_W - 20 * mm, 14 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(DARK_GOLD)
    canvas.drawCentredString(PAGE_W / 2, 9 * mm, f"— {doc.page} —")
    # Header text
    canvas.setFont("Helvetica-Oblique", 8)
    canvas.setFillColor(DARK_GOLD)
    canvas.drawString(20 * mm, PAGE_H - 10 * mm, "✈  Tour Siviglia & Córdoba  ·  29 Aprile – 3 Maggio")
    canvas.restoreState()


# ─────────────────────── STYLE SHEET ─────────────────────────


def build_styles():
    styles = getSampleStyleSheet()

    def add(name, **kw):
        styles.add(ParagraphStyle(name=name, **kw))

    add(
        "CoverTitle",
        fontName="Helvetica-Bold",
        fontSize=36,
        textColor=GOLD,
        alignment=TA_CENTER,
        spaceAfter=6,
        leading=42,
    )
    add(
        "CoverSubtitle",
        fontName="Helvetica-Oblique",
        fontSize=16,
        textColor=CREAM,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    add(
        "CoverDates",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=GOLD,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    add(
        "DayHeader",
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=GOLD,
        alignment=TA_LEFT,
        spaceBefore=8,
        spaceAfter=4,
        leading=28,
    )
    add(
        "DaySubtitle",
        fontName="Helvetica-Oblique",
        fontSize=13,
        textColor=TERRACOTTA,
        alignment=TA_LEFT,
        spaceAfter=6,
    )
    add(
        "SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=13,
        textColor=DARK_BROWN,
        spaceBefore=8,
        spaceAfter=3,
    )
    add(
        "BodyText2",
        fontName="Helvetica",
        fontSize=10,
        textColor=DARK_BROWN,
        leading=15,
        spaceAfter=3,
        alignment=TA_JUSTIFY,
    )
    add(
        "BulletItem",
        fontName="Helvetica",
        fontSize=10,
        textColor=DARK_BROWN,
        leading=15,
        leftIndent=12,
        spaceAfter=2,
    )
    add(
        "TipBox",
        fontName="Helvetica-Oblique",
        fontSize=9.5,
        textColor=DARK_BROWN,
        leading=14,
        alignment=TA_JUSTIFY,
    )
    add(
        "CaptionStyle",
        fontName="Helvetica-Oblique",
        fontSize=8,
        textColor=DARK_GOLD,
        alignment=TA_CENTER,
        spaceAfter=4,
    )
    add(
        "MapCaption",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=BLUE_NIGHT,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    add(
        "TOCEntry",
        fontName="Helvetica",
        fontSize=11,
        textColor=DARK_BROWN,
        leading=20,
        leftIndent=10,
    )
    add(
        "TOCTitle",
        fontName="Helvetica-Bold",
        fontSize=20,
        textColor=DARK_BROWN,
        alignment=TA_CENTER,
        spaceAfter=14,
    )
    add(
        "TipTitle",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=TERRACOTTA,
        spaceAfter=3,
    )
    return styles


# ─────────────────────── COVER PAGE ───────────────────────────


def build_cover(styles):
    story = []

    # Hero image (Seville / Giralda)
    hero_url = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d5"
        "/Sevilla_desde_la_Giralda_-_2.jpg/1280px-Sevilla_desde_la_Giralda_-_2.jpg"
    )
    hero_buf = fetch_image(hero_url, fallback_color=TERRACOTTA, w_px=1000, h_px=420)
    story.append(rl_image(hero_buf, width=PAGE_W - 40 * mm, height=7.5 * cm))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("🌟 Tour Siviglia &amp; Córdoba", styles["CoverTitle"]))
    story.append(Paragraph("Guida di viaggio personalizzata", styles["CoverSubtitle"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(
        HRFlowable(
            width="70%",
            thickness=2,
            color=GOLD,
            hAlign="CENTER",
        )
    )
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph("📅  29 Aprile – 3 Maggio", styles["CoverDates"]))
    story.append(Spacer(1, 0.2 * cm))
    story.append(Paragraph("Andalusia · Spagna", styles["CoverSubtitle"]))
    story.append(Spacer(1, 0.6 * cm))

    # Summary table
    summary_data = [
        ["🌍 Destinazioni", "Siviglia + Córdoba (day trip)"],
        ["🏨 Notti", "4 (29 apr · 30 apr · 1 mag · 2 mag)"],
        ["☀️  Giorni pieni", "3 (30 apr · 1 mag · 2 mag)"],
        ["🚄 Trasferimento", "Treno AVE Siviglia → Córdoba (≈ 40 min)"],
        ["🎭 Stile", "Culturale · Autentico · Rilassato"],
    ]
    t = Table(summary_data, colWidths=[5.5 * cm, 10 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), LIGHT_GOLD),
                ("BACKGROUND", (1, 0), (1, -1), WARM_WHITE),
                ("TEXTCOLOR", (0, 0), (-1, -1), DARK_BROWN),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica"),
                ("FONTSIZE", (0, 0), (-1, -1), 10),
                ("GRID", (0, 0), (-1, -1), 0.5, GOLD),
                ("ROWBACKGROUNDS", (0, 0), (-1, -1), [LIGHT_GOLD, WARM_WHITE]),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    t.hAlign = "CENTER"
    story.append(t)
    story.append(Spacer(1, 0.8 * cm))

    # Bottom tagline
    tagline = (
        "<font color='#C9A84C'><b>«</b></font> "
        "Tre giorni pieni, ritmo umano, qualità sopra quantità."
        " <font color='#C9A84C'><b>»</b></font>"
    )
    story.append(Paragraph(tagline, styles["CoverSubtitle"]))
    story.append(Spacer(1, 0.3 * cm))
    story.append(
        HRFlowable(width="40%", thickness=1, color=GOLD, hAlign="CENTER")
    )

    return story


# ──────────────────────── TOC PAGE ────────────────────────────


def build_toc(styles):
    story = []
    story.append(Paragraph("Indice del Tour", styles["TOCTitle"]))
    story.append(HRFlowable(width="60%", thickness=1.5, color=GOLD, hAlign="CENTER"))
    story.append(Spacer(1, 0.5 * cm))

    entries = [
        ("📌", "Mappa Generale", ""),
        ("📍", "29 Aprile  –  Arrivo a Siviglia", "Sera"),
        ("🕌", "30 Aprile  –  Siviglia Iconica", "Mattina · Pomeriggio · Sera"),
        ("🕌", "1 Maggio  –  Day Trip a Córdoba", "Mattina · Pomeriggio"),
        ("🌊", "2 Maggio  –  Siviglia Autentica", "Mattina · Pomeriggio · Sera"),
        ("✈️", "3 Maggio  –  Partenza", "Mattina"),
        ("💡", "Consigli Pratici", "Biglietti · Trasporti · Ristoranti"),
        ("🗺", "Mappe e QR Code", "Links Utili"),
    ]
    for icon, title, sub in entries:
        line = f"<b>{icon}  {title}</b>"
        if sub:
            line += f"   <font color='#C0522A' size='9'>{sub}</font>"
        story.append(Paragraph(line, styles["TOCEntry"]))
    story.append(Spacer(1, 0.5 * cm))
    return story


# ─────────────────── MAP PAGE (static) ────────────────────────


def build_map_page(styles):
    story = []
    story.append(Paragraph("🗺  Mappa Generale del Tour", styles["DayHeader"]))
    story.append(
        HRFlowable(width="100%", thickness=1, color=GOLD, hAlign="CENTER")
    )
    story.append(Spacer(1, 0.3 * cm))

    story.append(
        Paragraph(
            "Il tour si concentra su <b>due città andaluse</b> raggiungibili in treno.",
            styles["BodyText2"],
        )
    )
    story.append(Spacer(1, 0.3 * cm))

    # Static map from OpenStreetMap via Wikimedia
    map_url = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/34"
        "/Andalusia_in_Spain_%28plus_Canarias%29_%28location_map_scheme%29.svg"
        "/640px-Andalusia_in_Spain_%28plus_Canarias%29_%28location_map_scheme%29.svg.png"
    )
    map_buf = fetch_image(map_url, fallback_color=OLIVE, w_px=600, h_px=320)
    story.append(rl_image(map_buf, width=14 * cm, height=7.5 * cm))
    story.append(
        Paragraph(
            "Andalusia, Spagna  ·  Siviglia (capitale regionale) e Córdoba (~143 km NE)",
            styles["CaptionStyle"],
        )
    )
    story.append(Spacer(1, 0.5 * cm))

    # Distance table
    dist_data = [
        ["Tratta", "Distanza", "Treno AVE", "Nota"],
        ["Siviglia → Córdoba", "≈ 143 km", "30–45 min", "Frequente, economico"],
        ["Siviglia → Granada", "≈ 260 km", "3+ ore (no AVE diretto)", "⚠️ Troppo lontana per day-trip"],
    ]
    t = Table(dist_data, colWidths=[5 * cm, 3 * cm, 3 * cm, 4.5 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), DARK_BROWN),
                ("TEXTCOLOR", (0, 0), (-1, 0), GOLD),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("BACKGROUND", (0, 1), (-1, 1), LIGHT_GOLD),
                ("BACKGROUND", (0, 2), (-1, 2), colors.HexColor("#FDECEA")),
                ("GRID", (0, 0), (-1, -1), 0.5, GOLD),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    t.hAlign = "CENTER"
    story.append(t)
    story.append(Spacer(1, 0.4 * cm))
    story.append(
        Paragraph(
            "💡 <b>Perché non Granada?</b>  Con soli 3 giorni pieni, aggiungere Granada "
            "significherebbe fare tutto di corsa e non godere nulla a fondo. "
            "Córdoba invece è perfetta: vicina, ricchissima, e si visita in mezza giornata.",
            styles["TipBox"],
        )
    )
    return story


# ──────────────────── GENERIC DAY BUILDER ────────────────────


def section(title: str, items: list, styles) -> list:
    """Build a timed section with bullet points."""
    blocks = []
    blocks.append(Paragraph(title, styles["SectionHeader"]))
    for item in items:
        blocks.append(Paragraph(f"• {item}", styles["BulletItem"]))
    return blocks


def tip_box(text: str, styles, title="💡 Consiglio") -> list:
    """Golden-bordered tip box."""
    t = Table([[Paragraph(f"<b>{title}</b><br/>{text}", styles["TipBox"])]], colWidths=[15.5 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), LIGHT_GOLD),
                ("BOX", (0, 0), (-1, -1), 1.5, GOLD),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    t.hAlign = "LEFT"
    return [t, Spacer(1, 0.25 * cm)]


# ─────────────────── DAY PAGES ───────────────────────────────


def day_header(date: str, title: str, subtitle: str, img_url: str,
               styles, fallback=TERRACOTTA) -> list:
    blocks = []
    img_buf = fetch_image(img_url, fallback_color=fallback, w_px=900, h_px=280)
    blocks.append(rl_image(img_buf, width=PAGE_W - 40 * mm, height=5.5 * cm))
    blocks.append(Spacer(1, 0.3 * cm))
    blocks.append(Paragraph(f"📅  {date}", styles["DaySubtitle"]))
    blocks.append(Paragraph(title, styles["DayHeader"]))
    blocks.append(HRFlowable(width="100%", thickness=1.2, color=GOLD, hAlign="LEFT"))
    blocks.append(Spacer(1, 0.2 * cm))
    if subtitle:
        blocks.append(Paragraph(subtitle, styles["BodyText2"]))
        blocks.append(Spacer(1, 0.2 * cm))
    return blocks


def build_day0(styles):
    """29 Aprile – Arrivo."""
    story = []
    img = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1e"
        "/Seville_night.jpg/1280px-Seville_night.jpg"
    )
    story += day_header(
        "29 Aprile",
        "Arrivo a Siviglia",
        "Un arrivo senza fretta, per iniziare nel modo giusto.",
        img,
        styles,
    )
    story += section(
        "🌙 Sera  (21:00 →)",
        [
            "Check-in in hotel / appartamento",
            "Breve passeggiata nel centro storico — la <b>Cattedrale</b> illuminata è uno spettacolo",
            "Tapas leggere in un bar vicino all'alloggio (evitare i posti turistici)",
            "A letto presto: domani si inizia di buon'ora",
        ],
        styles,
    )
    story.append(Spacer(1, 0.3 * cm))
    story += tip_box(
        "Non programmare nulla per questa sera. L'obiettivo è solo <b>entrare nel mood</b> "
        "della città. Siviglia si sente nell'aria — il profumo delle arance, i vicoli stretti, "
        "le luci calde. Non c'è bisogno di correre.",
        styles,
        title="👉 Filosofia del Viaggio",
    )

    # Small Seville at night image
    story.append(Spacer(1, 0.3 * cm))
    img2_url = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/5/53"
        "/Catedral_de_Sevilla_-_02.jpg/800px-Catedral_de_Sevilla_-_02.jpg"
    )
    img2_buf = fetch_image(img2_url, fallback_color=DARK_BROWN, w_px=600, h_px=300)
    story.append(rl_image(img2_buf, width=10 * cm, height=5 * cm))
    story.append(
        Paragraph("Cattedrale di Siviglia di notte", styles["CaptionStyle"])
    )
    return story


def build_day1(styles):
    """30 Aprile – Siviglia Iconica."""
    story = []
    img = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/3/3b"
        "/Real_Alcazar_Seville_2008.jpg/1280px-Real_Alcazar_Seville_2008.jpg"
    )
    story += day_header(
        "30 Aprile",
        "Siviglia Iconica",
        "La grande architettura andalusa: Alcázar, Cattedrale, Santa Cruz.",
        img,
        styles,
        fallback=TERRACOTTA,
    )

    story += section(
        "🌅 Mattina  (8:30 →)",
        [
            "<b>8:30</b> – Ingresso al <b>Real Alcázar di Siviglia</b> (prenotato in anticipo!)",
            "Visita i Saloni Reali, il Giardino del Labirinto e il Patio delle Bambole",
            "Tempo consigliato: <b>1h30 – 2h</b>",
            "<b>10:30</b> – <b>Cattedrale di Siviglia</b> (la più grande gotica del mondo) + Torre della <b>Giralda</b>",
            "Salita alla Giralda: rampa (non scale) — accessibile e panorama imperdibile",
            "Tempo consigliato: <b>1h30</b>",
        ],
        styles,
    )
    story.append(Spacer(1, 0.2 * cm))

    # Alcazar image
    alc_url = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/6/66"
        "/Real_Alcazar_of_Seville_-_Patio_de_las_Doncellas.jpg"
        "/800px-Real_Alcazar_of_Seville_-_Patio_de_las_Doncellas.jpg"
    )
    alc_buf = fetch_image(alc_url, fallback_color=LIGHT_GOLD, w_px=700, h_px=300)
    story.append(rl_image(alc_buf, width=11 * cm, height=5 * cm))
    story.append(Paragraph("Patio de las Doncellas – Real Alcázar", styles["CaptionStyle"]))
    story.append(Spacer(1, 0.3 * cm))

    story += tip_box(
        "Prenotare l'Alcázar <b>almeno 2 settimane prima</b> su alcazarsevilla.es. "
        "L'ingresso mattutino (8:30) è il meno affollato. "
        "Portare scarpe comode: i pavimenti di maioliche sono sdrucciolevoli.",
        styles,
        title="⚠️  Prenotazione Obbligatoria",
    )

    story += section(
        "☀️ Pomeriggio  (13:00 →)",
        [
            "<b>13:00</b> – Pranzo nel <b>Barrio Santa Cruz</b> (evitare i ristoranti sulla piazza, cercare i vicoli)",
            "<b>15:00</b> – Passeggiata libera nel quartiere ebraico: vicoli bianchi, gerani, fontane",
            "<b>16:30</b> – <b>Casa de Pilatos</b> — palazzo rinascimentale-mudéjar molto sottovalutato",
            "Ingresso ≈ 12€ · Tempo: 1h",
        ],
        styles,
    )
    story.append(Spacer(1, 0.2 * cm))

    story += section(
        "🌆 Sera  (20:00 →)",
        [
            "<b>20:00</b> – Aperitivo in Plaza de la Alfalfa (locale, autentico)",
            "<b>21:00</b> – Cena in un ristorante con prodotti locali (chiedere pesce fresco)",
            "<b>22:30</b> – Opzionale: spettacolo di <b>flamenco</b> in una tablao di qualità",
            "  → Tablao El Arenal o Casa de la Memoria (prenotare)",
        ],
        styles,
    )
    story.append(Spacer(1, 0.3 * cm))

    story += tip_box(
        "Per il flamenco: evitare gli spettacoli 'per turisti' nelle piazze. "
        "Casa de la Memoria (Calle Ximénez de Enciso) offre uno spettacolo autentico "
        "in un palazzo storico, max 100 posti. Prenotare online.",
        styles,
        title="🎭 Flamenco Autentico",
    )
    return story


def build_day2(styles):
    """1 Maggio – Córdoba."""
    story = []
    img = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d6"
        "/Mezquita_de_C%C3%B3rdoba_-_panoramio_%281%29.jpg"
        "/1280px-Mezquita_de_C%C3%B3rdoba_-_panoramio_%281%29.jpg"
    )
    story += day_header(
        "1 Maggio",
        "Day Trip a Córdoba",
        "La Mezquita-Cattedrale più straordinaria del mondo, la Judería, i patios.",
        img,
        styles,
        fallback=OLIVE,
    )

    # Train info box
    train_data = [
        ["🚄 Treno AVE  –  Siviglia → Córdoba", ""],
        ["Partenza consigliata", "7:50 – 8:20 da Siviglia Santa Justa"],
        ["Durata", "≈ 40 minuti"],
        ["Costo", "≈ 15–25 € a/r (prenotare su renfe.com)"],
        ["Rientro", "Tardo pomeriggio (17:00 – 18:30)"],
    ]
    t = Table(train_data, colWidths=[7 * cm, 8.5 * cm])
    t.setStyle(
        TableStyle(
            [
                ("SPAN", (0, 0), (1, 0)),
                ("BACKGROUND", (0, 0), (-1, 0), DARK_BROWN),
                ("TEXTCOLOR", (0, 0), (-1, 0), GOLD),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.5),
                ("BACKGROUND", (0, 1), (0, -1), LIGHT_GOLD),
                ("BACKGROUND", (1, 1), (1, -1), WARM_WHITE),
                ("FONTNAME", (0, 1), (0, -1), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, GOLD),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    t.hAlign = "CENTER"
    story.append(t)
    story.append(Spacer(1, 0.3 * cm))

    story += section(
        "🕌 Mattina a Córdoba  (9:00 →)",
        [
            "<b>9:00</b> – Arrivo in treno alla stazione di Córdoba",
            "<b>9:30</b> – <b>Mezquita-Catedral de Córdoba</b> — entrare appena apre (9:30), "
            "prima delle scolaresche",
            "La foresta di 856 colonne in marmo e granito è una delle meraviglie architettoniche del mondo",
            "Tempo: <b>1h30 – 2h</b>  ·  Biglietto: ≈ 13€",
            "<b>11:30</b> – <b>Judería</b> (quartiere ebraico) — Calle de las Flores, Sinagoga medievale",
            "<b>12:30</b> – Patios andalusi (tra aprile-maggio molti aprono al pubblico per il Festival dei Patios)",
        ],
        styles,
    )
    story.append(Spacer(1, 0.2 * cm))

    # Mezquita image
    mezq_url = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e"
        "/Mosque-Cathedral_of_Cordoba_interior.jpg"
        "/800px-Mosque-Cathedral_of_Cordoba_interior.jpg"
    )
    mezq_buf = fetch_image(mezq_url, fallback_color=CREAM, w_px=700, h_px=320)
    story.append(rl_image(mezq_buf, width=11 * cm, height=5.5 * cm))
    story.append(
        Paragraph(
            "Interno della Mezquita-Catedral — le celebri arcate bianche e rosse",
            styles["CaptionStyle"],
        )
    )
    story.append(Spacer(1, 0.3 * cm))

    story += section(
        "🌞 Pomeriggio  (13:30 →)",
        [
            "<b>13:30</b> – Pranzo in un patio tipico cordobese (non sulla strada turistica)",
            "<b>15:00</b> – <b>Ponte Romano</b> sul Guadalquivir — fotogenico e imperdibile",
            "<b>15:30</b> – <b>Alcázar de los Reyes Cristianos</b> (opzionale, giardini bellissimi)",
            "<b>17:00</b> – Rientro alla stazione per il treno verso Siviglia",
            "<b>18:00</b> – Arrivo a Siviglia, cena e riposo",
        ],
        styles,
    )
    story.append(Spacer(1, 0.3 * cm))

    story += tip_box(
        "Se il viaggio avviene durante il <b>Festival dei Patios di Córdoba</b> "
        "(prima metà di maggio), molte case private aprono i propri cortili fioriti. "
        "È uno spettacolo unico al mondo — Patrimonio Immateriale UNESCO.",
        styles,
        title="🌸 Festival dei Patios",
    )
    return story


def build_day3(styles):
    """2 Maggio – Siviglia Autentica."""
    story = []
    img = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/9/97"
        "/Triana%2C_Seville.jpg/1280px-Triana%2C_Seville.jpg"
    )
    story += day_header(
        "2 Maggio",
        "Siviglia Autentica",
        "Il lato vero della città: Triana, il Parco, Plaza de España e il tramonto.",
        img,
        styles,
        fallback=OLIVE,
    )

    story += section(
        "🌅 Mattina  (9:00 →)",
        [
            "<b>9:00</b> – <b>Quartiere Triana</b> — attraversare il Ponte di Isabella II a piedi",
            "Triana è la vera anima di Siviglia: ceramisti, baretti locali, flamenco nelle strade",
            "<b>10:00</b> – <b>Mercato di Triana</b> (Mercado de Abastos) — prodotti locali, tapas fresche",
            "<b>11:30</b> – Passeggiata lungo il Guadalquivir sulla riva di Triana",
        ],
        styles,
    )
    story.append(Spacer(1, 0.2 * cm))

    triana_url = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/8/85"
        "/Triana_Sevilla.jpg/800px-Triana_Sevilla.jpg"
    )
    triana_buf = fetch_image(triana_url, fallback_color=TERRACOTTA, w_px=700, h_px=280)
    story.append(rl_image(triana_buf, width=11 * cm, height=4.5 * cm))
    story.append(Paragraph("Quartiere Triana — ponti sul Guadalquivir", styles["CaptionStyle"]))
    story.append(Spacer(1, 0.3 * cm))

    story += section(
        "☀️ Pomeriggio  (13:00 →)",
        [
            "<b>13:00</b> – Pranzo in Triana o rientro nel centro",
            "<b>15:00</b> – <b>Plaza de España</b> — la piazza più bella di Siviglia",
            "Dettaglio: ogni provincia spagnola ha un proprio pannello in ceramica; cercate quello della vostra regione preferita",
            "<b>16:30</b> – <b>Parco di Maria Luisa</b> — stroll tra fontane e padiglioni liberty",
            "<b>18:00</b> – <b>Metropol Parasol</b> (Las Setas) — salire in cima per il tramonto su Siviglia",
            "Biglietto: ≈ 5€  ·  Include una consumazione al bar panoramico",
        ],
        styles,
    )
    story.append(Spacer(1, 0.2 * cm))

    # Plaza de España image
    plaza_url = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b4"
        "/Plaza_de_Espa%C3%B1a_%28Sevilla%29.jpg"
        "/800px-Plaza_de_Espa%C3%B1a_%28Sevilla%29.jpg"
    )
    plaza_buf = fetch_image(plaza_url, fallback_color=BLUE_NIGHT, w_px=700, h_px=280)
    story.append(rl_image(plaza_buf, width=11 * cm, height=4.5 * cm))
    story.append(Paragraph("Plaza de España — costruita per l'Esposizione Ibero-Americana del 1929", styles["CaptionStyle"]))
    story.append(Spacer(1, 0.3 * cm))

    story += section(
        "🌙 Sera  (20:30 →)  —  L'ultima sera",
        [
            "<b>20:30</b> – Cena più curata: scegliere un ristorante con menù degustazione o specialità di stagione",
            "Suggerimento: zona <b>Alameda de Hércules</b> per atmosfera bohémien e qualità",
            "<b>22:30</b> – Passeggiata lungo il <b>Paseo de Cristóbal Colón</b> (sul fiume)",
            "Goditi la città illuminata — domani si parte",
        ],
        styles,
    )
    story.append(Spacer(1, 0.3 * cm))

    story += tip_box(
        "Il Metropol Parasol (Las Setas) è la struttura in legno più grande del mondo. "
        "Al tramonto il cielo si tinge di arancione sopra i tetti di Siviglia — "
        "uno dei panorami più belli d'Andalusia.",
        styles,
        title="🌅 Tramonto Imperdibile",
    )
    return story


def build_day4(styles):
    """3 Maggio – Partenza."""
    story = []
    story.append(Paragraph("📅  3 Maggio", styles["DaySubtitle"]))
    story.append(Paragraph("Partenza", styles["DayHeader"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=GOLD, hAlign="LEFT"))
    story.append(Spacer(1, 0.3 * cm))
    story.append(
        Paragraph(
            "L'aeroporto di Siviglia (SVQ) è a circa <b>25 minuti</b> dal centro.",
            styles["BodyText2"],
        )
    )
    story.append(Spacer(1, 0.3 * cm))

    story += section(
        "🌄 Mattina",
        [
            "Colazione con calma — l'ultimo caffè andaluso",
            "Check-out dall'hotel",
            "Trasferimento all'aeroporto di Siviglia (SVQ)",
            "Tram EA: dal centro all'aeroporto in 35 min, economico e comodo",
        ],
        styles,
    )
    story.append(Spacer(1, 0.5 * cm))

    # Goodbye summary
    summary_data = [
        ["✅ RESOCONTO DEL VIAGGIO"],
        ["• 2 giorni pieni a Siviglia (monumenti + vita vera)"],
        ["• 1 giorno a Córdoba (Mezquita + Judería + Ponti)"],
        ["• Ritmo umano — senza correre, senza tour di gruppo"],
        ["• Qualità > quantità — ogni posto visitato davvero"],
    ]
    t = Table(summary_data, colWidths=[15.5 * cm])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), DARK_BROWN),
                ("TEXTCOLOR", (0, 0), (-1, 0), GOLD),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), LIGHT_GOLD),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 10),
                ("BOX", (0, 0), (-1, -1), 1.5, GOLD),
                ("GRID", (0, 1), (-1, -1), 0.3, GOLD),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ]
        )
    )
    t.hAlign = "CENTER"
    story.append(t)
    return story


# ────────────────── PRACTICAL TIPS PAGE ──────────────────────


def build_tips(styles):
    story = []
    story.append(Paragraph("💡  Consigli Pratici", styles["DayHeader"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=GOLD, hAlign="LEFT"))
    story.append(Spacer(1, 0.3 * cm))

    tips = [
        (
            "🎟  Biglietti",
            [
                "Real Alcázar: prenotare su <b>alcazarsevilla.es</b> — esaurito settimane prima",
                "Cattedrale + Giralda: prenotare su <b>catedraldesevilla.es</b>",
                "Mezquita Córdoba: biglietti su <b>mezquita-catedraldecordoba.es</b>",
                "Casa de Pilatos: nessuna prenotazione necessaria (≈ 12€)",
                "Treno AVE: prenotare su <b>renfe.com</b> o app Renfe",
            ],
        ),
        (
            "🚌  Trasporti a Siviglia",
            [
                "Centro storico: tutto a piedi — massimo 20 minuti tra i monumenti principali",
                "Tram T1: collega Santa Justa (stazione) con il centro",
                "Bus EA: stazione ↔ aeroporto (≈ 4€, 35 min)",
                "Taxi / Uber: disponibili, economici rispetto al nord Europa",
            ],
        ),
        (
            "🍽  Ristoranti (selezione)",
            [
                "<b>Siviglia</b> · Bar El Comercio (tapas autentiche, non turistico)",
                "<b>Siviglia</b> · Bodeguita Romero (montaditos tradizionali)",
                "<b>Siviglia</b> · Alameda de Hércules: zona per cena serale di qualità",
                "<b>Córdoba</b> · Taberna Salinas (dal 1879, patio interno magnifico)",
                "<b>Córdoba</b> · Bar Santos (tortilla di patate famosa in tutta la Spagna)",
            ],
        ),
        (
            "☀️  Abbigliamento & Meteo",
            [
                "Fine aprile / inizio maggio: temperatura 20–28°C di giorno, 15°C di sera",
                "Portare scarpe comode (molti pavimenti in pietra/maiolica)",
                "Cappellino e crema solare per Plaza de España e passeggiata lungo il fiume",
                "Una giacca leggera per le sere",
            ],
        ),
        (
            "📱  App Utili",
            [
                "<b>Maps.me</b> — mappe offline (utile senza roaming)",
                "<b>Renfe</b> — biglietti treno AVE",
                "<b>Google Translate</b> — molti locali anziani parlano solo spagnolo",
                "<b>TripAdvisor</b> — per leggere recensioni recenti dei ristoranti",
                "<b>Booking.com</b> / <b>Airbnb</b> — alloggio centrale preferibile",
            ],
        ),
    ]

    for title, items in tips:
        story.append(Paragraph(f"<b>{title}</b>", styles["SectionHeader"]))
        for item in items:
            story.append(Paragraph(f"• {item}", styles["BulletItem"]))
        story.append(Spacer(1, 0.2 * cm))

    return story


# ─────────────────── QR CODES PAGE ──────────────────────────


def build_qr_page(styles):
    story = []
    story.append(Paragraph("🔗  Mappe & QR Code Utili", styles["DayHeader"]))
    story.append(HRFlowable(width="100%", thickness=1.2, color=GOLD, hAlign="LEFT"))
    story.append(Spacer(1, 0.4 * cm))
    story.append(
        Paragraph(
            "Inquadra i QR code con la fotocamera del telefono per accedere rapidamente "
            "alle prenotazioni e alle mappe.",
            styles["BodyText2"],
        )
    )
    story.append(Spacer(1, 0.4 * cm))

    qr_links = [
        ("Real Alcázar", "https://www.alcazarsevilla.es/entradas/", "alcazarsevilla.es"),
        ("Cattedrale di Siviglia", "https://www.catedraldesevilla.es/", "catedraldesevilla.es"),
        ("Mezquita Córdoba", "https://mezquita-catedraldecordoba.es/", "mezquita-catedraldecordoba.es"),
        ("Treno AVE (Renfe)", "https://www.renfe.com/", "renfe.com"),
        ("Casa de la Memoria (Flamenco)", "https://www.casadelamemoria.es/", "casadelamemoria.es"),
        ("Metropol Parasol", "https://setasdesevilla.com/", "setasdesevilla.com"),
    ]

    # Build 3-column QR table
    qr_cells = []
    for name, url, label in qr_links:
        qr_buf = make_qr(url, size=100)
        qr_img = Image(qr_buf, width=2.8 * cm, height=2.8 * cm)
        qr_img.hAlign = "CENTER"
        cell_content = [
            [qr_img],
            [Paragraph(f"<b>{name}</b>", styles["MapCaption"])],
            [Paragraph(label, styles["CaptionStyle"])],
        ]
        inner = Table(cell_content, colWidths=[3.5 * cm])
        inner.setStyle(
            TableStyle(
                [
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("BACKGROUND", (0, 0), (-1, -1), WARM_WHITE),
                    ("BOX", (0, 0), (-1, -1), 0.5, GOLD),
                    ("TOPPADDING", (0, 0), (-1, -1), 5),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ]
            )
        )
        qr_cells.append(inner)

    # 3 per row
    rows = [qr_cells[i : i + 3] for i in range(0, len(qr_cells), 3)]
    for row in rows:
        while len(row) < 3:
            row.append("")
        t = Table([row], colWidths=[5.2 * cm, 5.2 * cm, 5.2 * cm])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"), ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        t.hAlign = "CENTER"
        story.append(t)
        story.append(Spacer(1, 0.4 * cm))

    return story


# ──────────────────── BACK COVER ─────────────────────────────


def build_back_cover(styles):
    story = []
    story.append(Spacer(1, 2 * cm))

    river_url = (
        "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e1"
        "/Seville_golden_tower.jpg/800px-Seville_golden_tower.jpg"
    )
    river_buf = fetch_image(river_url, fallback_color=TERRACOTTA, w_px=700, h_px=380)
    story.append(rl_image(river_buf, width=PAGE_W - 50 * mm, height=7 * cm))
    story.append(Spacer(1, 0.5 * cm))

    story.append(Paragraph("Torre del Oro sul Guadalquivir", styles["CaptionStyle"]))
    story.append(Spacer(1, 1 * cm))

    story.append(
        HRFlowable(width="60%", thickness=2, color=GOLD, hAlign="CENTER")
    )
    story.append(Spacer(1, 0.5 * cm))
    story.append(
        Paragraph(
            "Buon Viaggio! 🌟",
            ParagraphStyle(
                "BigWish",
                fontName="Helvetica-Bold",
                fontSize=28,
                textColor=GOLD,
                alignment=TA_CENTER,
            ),
        )
    )
    story.append(Spacer(1, 0.3 * cm))
    story.append(
        Paragraph(
            "Siviglia ti aspetta con le sue arance amare, i suoi patios fioriti e<br/>"
            "il profumo di gelsomino che riempie i vicoli al tramonto.",
            ParagraphStyle(
                "WishSub",
                fontName="Helvetica-Oblique",
                fontSize=13,
                textColor=CREAM,
                alignment=TA_CENTER,
                leading=20,
            ),
        )
    )
    story.append(Spacer(1, 1 * cm))
    story.append(
        HRFlowable(width="40%", thickness=1, color=GOLD, hAlign="CENTER")
    )
    story.append(Spacer(1, 0.5 * cm))
    story.append(
        Paragraph(
            "29 Aprile – 3 Maggio",
            ParagraphStyle(
                "FinalDate",
                fontName="Helvetica",
                fontSize=11,
                textColor=CREAM,
                alignment=TA_CENTER,
            ),
        )
    )
    return story


# ───────────────────── DOCUMENT BUILDER ──────────────────────


def build_document(output_path: str = "tour_siviglia.pdf"):
    print(f"📄 Generazione PDF: {output_path}")

    styles = build_styles()

    # Page templates
    cover_frame = Frame(
        0, 0, PAGE_W, PAGE_H,
        leftPadding=20 * mm,
        rightPadding=20 * mm,
        topPadding=18 * mm,
        bottomPadding=18 * mm,
        id="cover_frame",
    )
    body_frame = Frame(
        0, 0, PAGE_W, PAGE_H,
        leftPadding=20 * mm,
        rightPadding=20 * mm,
        topPadding=22 * mm,
        bottomPadding=22 * mm,
        id="body_frame",
    )

    cover_template = PageTemplate(
        id="Cover",
        frames=[cover_frame],
        onPage=draw_ornate_border,
        pagesize=A4,
    )
    body_template = PageTemplate(
        id="Body",
        frames=[body_frame],
        onPage=draw_header_footer,
        pagesize=A4,
    )
    back_template = PageTemplate(
        id="Back",
        frames=[cover_frame],
        onPage=draw_ornate_border,
        pagesize=A4,
    )

    doc = BaseDocTemplate(
        output_path,
        pagesize=A4,
        pageTemplates=[cover_template, body_template, back_template],
        title="Tour Siviglia & Córdoba – 29 Aprile–3 Maggio",
        author="Tour Planner",
        subject="Guida di viaggio personalizzata",
    )

    # Build full story
    story = []

    # Cover (no header/footer)
    story += build_cover(styles)
    story.append(NextPageTemplate("Body"))
    story.append(PageBreak())

    # TOC
    story += build_toc(styles)
    story.append(PageBreak())

    # Map overview
    story += build_map_page(styles)
    story.append(PageBreak())

    # Day 0 – Aprile 29
    story += build_day0(styles)
    story.append(PageBreak())

    # Day 1 – Aprile 30
    story += build_day1(styles)
    story.append(PageBreak())

    # Day 2 – Maggio 1
    story += build_day2(styles)
    story.append(PageBreak())

    # Day 3 – Maggio 2
    story += build_day3(styles)
    story.append(PageBreak())

    # Day 4 – Maggio 3
    story += build_day4(styles)
    story.append(PageBreak())

    # Tips
    story += build_tips(styles)
    story.append(PageBreak())

    # QR Codes
    story += build_qr_page(styles)

    # Back cover
    story.append(NextPageTemplate("Back"))
    story.append(PageBreak())
    story += build_back_cover(styles)

    doc.build(story)
    size_kb = os.path.getsize(output_path) // 1024
    print(f"✅ PDF generato con successo: {output_path}  ({size_kb} KB)")
    return output_path


# ────────────────────────── MAIN ─────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Genera il PDF del Tour di Siviglia e Córdoba"
    )
    parser.add_argument(
        "-o", "--output",
        default="tour_siviglia.pdf",
        help="Percorso del file PDF di output (default: tour_siviglia.pdf)",
    )
    args = parser.parse_args()
    build_document(args.output)
