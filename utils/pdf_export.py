"""
Pipettierschema als PDF — kompakt auf EINER A4-Seite (Querformat).

Aufbau:
  Kopf: Sessionname/Plattenname · Plate-ID · Bearbeiter/Kommentar · Datum
  1. MasterMix-Tabelle (farbig je Assay): je Einzelreaktion UND aufsummiert,
     plus Template-/Reaktionsvolumen.
  2. Farbcodierte 96-Well-Plattengrafik: Assay-Name über jeder Spalte,
     Probenname / PTC / NTC in jedem Well.

Probennamen werden NICHT abgeschnitten (wordWrap='CJK' → harter Umbruch).
Zahlen im deutschen Format (Komma). Alles ist so dimensioniert, dass es auch
bei 6 Assays auf eine einzige Seite passt.
"""
import html
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas
from datetime import datetime

from models.plate_layout import PLATE_96
from utils.fmt import de
from utils.i18n import tr
from utils.controls import is_control, is_standard, label as control_label, shade, lighten


def _hex(color: str) -> colors.Color:
    try:
        return colors.HexColor(color)
    except Exception:
        return colors.white


def _is_light(hex_color: str) -> bool:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return True
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (0.299 * r + 0.587 * g + 0.114 * b) > 150


def _esc(text) -> str:
    return html.escape(str(text or ""))


def _is_compact_plate(plate) -> bool:
    return len(plate.cols) > 12          # 384 (16×24) → kompakte Darstellung


class _NumberedCanvas(canvas.Canvas):
    """Zeichnet auf JEDE Seite eine Fußzeile: Plattenname links, „Seite X von Y"
    rechts – damit getrennte Blätter eindeutig zugeordnet werden können."""
    def __init__(self, *args, footer_text="", **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_states = []
        self._footer_text = footer_text

    def showPage(self):
        self._saved_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        total = len(self._saved_states)
        for state in self._saved_states:
            self.__dict__.update(state)
            self._draw_footer(total)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def _draw_footer(self, total):
        w = self._pagesize[0]
        self.setFont("Helvetica", 7)
        self.setFillColor(colors.grey)
        self.drawString(1.0 * cm, 0.4 * cm, str(self._footer_text)[:90])
        self.drawRightString(w - 1.0 * cm, 0.4 * cm,
                             tr("Seite {p} von {total}", p=self._pageNumber, total=total))


def _numbered_canvas_factory(footer_text: str):
    def _make(*args, **kwargs):
        return _NumberedCanvas(*args, footer_text=footer_text, **kwargs)
    return _make


def _standards_legend(assignments, avail_w):
    """Kleine Legende der Standards (RS/MS) mit Name · Target · optionaler Notiz –
    Doku-Hilfe, da im Raster (v.a. 384) nur das Kürzel „RS"/„MS" steht.
    Linksbündig unter der Überschrift; bei mehreren Einträgen mehrspaltig (bleibt
    flach → Seite 1). Leer → None."""
    seen, cells = set(), []
    left = ParagraphStyle("stdcell", fontName="Helvetica", fontSize=6.5, leading=8.5,
                          alignment=TA_LEFT, wordWrap="CJK")
    for a in assignments:
        if not is_standard(a.role):
            continue
        key = (a.assay.display_name, a.role, a.sample_id)
        if key in seen:
            continue
        seen.add(key)
        note = a.assay.standard_note(a.role, a.sample_id)
        dot = f'<font color="{_esc(a.assay.color)}" size="9">•</font> '   # Farbpunkt = Assay-Farbe
        txt = (f"{dot}<b>{_esc(a.role)}</b> {_esc(a.sample_id)} · {_esc(a.assay.display_name)}"
               + tr(" · Target: {target}", target=_esc(a.targetname)))
        if note:
            txt += f" · {_esc(note)}"
        cells.append(Paragraph(txt, left))
    if not cells:
        return None
    # Flach halten, damit alles neben dem Raster auf Seite 1 bleibt: max ~3 Zeilen.
    n_cols = min(4, max(1, (len(cells) + 2) // 3))
    n_rows = (len(cells) + n_cols - 1) // n_cols
    data = [[Paragraph("", left) for _ in range(n_cols)] for _ in range(n_rows)]
    for idx, cell in enumerate(cells):                 # spaltenweise füllen
        data[idx % n_rows][idx // n_rows] = cell
    col_w = min(8.0 * cm, avail_w / n_cols)            # schmal → linksbündig, nicht volle Breite
    tbl = Table(data, colWidths=[col_w] * n_cols, hAlign="LEFT")
    tbl.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING",    (0, 0), (-1, -1), 0.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0.5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
    ]))
    return tbl


def _source_mapping(assignments) -> dict:
    """{Quell-Well: Probenname} aus den Transferdaten (erste Probe je Quell-Well)."""
    mapping: dict[str, str] = {}
    for a in assignments:
        if a.source_well and not is_control(a.role):
            mapping.setdefault(a.source_well, a.sample_id)
    return mapping


def _source_plate_grid(mapping: dict, avail_w) -> Table:
    """8×12-Quellplatten-Raster (96) mit Probenname je Well (mapping: {well: name}).
    Eindeutiger als eine Tabelle: die Position entspricht 1:1 der MP96-/Eluat-Platte.
    Belegte Wells hellblau (wie im Programmfenster)."""
    R96, C96 = PLATE_96.rows, PLATE_96.cols
    style = [
        ("ALIGN",     (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",      (0, 1), (-1, -1), 0.4, colors.grey),
        ("LINEBELOW", (1, 0), (-1, 0), 0.5, colors.black),
    ]
    data = [[_para("", 7)] + [_para(f"<b>{c}</b>", 7) for c in C96]]
    for r_i, r in enumerate(R96, start=1):
        line = [_para(f"<b>{r}</b>", 7)]
        for c_i, c in enumerate(C96, start=1):
            name = mapping.get(f"{r}{c}", "")
            line.append(_para(_esc(name), 6))
            if name:
                style.append(("BACKGROUND", (c_i, r_i), (c_i, r_i), colors.HexColor("#DCE6F1")))
        data.append(line)

    label_w = 0.7 * cm
    well_w = min((avail_w - label_w) / len(C96), 2.15 * cm)
    tbl = Table(data, colWidths=[label_w] + [well_w] * len(C96),
                rowHeights=[0.5 * cm] + [0.92 * cm] * len(R96))
    tbl.setStyle(TableStyle(style))
    return tbl


def _para(text_html: str, size: float = 6, color=colors.black, bold: bool = False) -> Paragraph:
    style = ParagraphStyle(
        "cell", fontName="Helvetica-Bold" if bold else "Helvetica",
        fontSize=size, leading=size + 1.1, alignment=TA_CENTER,
        textColor=color, wordWrap="CJK",
    )
    return Paragraph(text_html, style)


def export_pipetting_pdf(
    filepath: str,
    assignments,
    mm_results,
    plate_id: str = "",
    plate_name: str = "",
    warnings: list[str] = None,
    comment: str = "",
    plate=PLATE_96,
    source_plate_id: str = "",
    source_plate_name: str = "",
):
    doc = SimpleDocTemplate(
        filepath, pagesize=landscape(A4),
        leftMargin=1.0 * cm, rightMargin=1.0 * cm,
        topMargin=0.8 * cm, bottomMargin=0.8 * cm,
    )
    styles = getSampleStyleSheet()
    title_st = ParagraphStyle("t", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=12, leading=14)
    meta_st = ParagraphStyle("m", parent=styles["Normal"], fontSize=8, leading=10)
    section = ParagraphStyle("s", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=11)

    avail_w = landscape(A4)[0] - doc.leftMargin - doc.rightMargin
    story = []

    # ── Kopf mit Platteninfos ──
    head = tr("WellDone! — Pipettierschema")
    if plate_name:
        head += f"   |   {_esc(plate_name)}"
    if plate_id:
        head += tr("   |   Plate-ID: {id}", id=_esc(plate_id))
    story.append(Paragraph(head, title_st))
    meta = tr("Erstellt: {when}", when=f"{datetime.now():%d.%m.%Y %H:%M}")
    sp = " / ".join(x for x in (source_plate_name, source_plate_id) if x)
    if sp:
        meta += "   |   " + tr("Quellplatte: {sp}", sp=_esc(sp))
    if comment:
        meta += f"   |   {_esc(comment)}"
    story.append(Paragraph(meta, meta_st))
    if warnings:
        story.append(Paragraph("⚠ " + _esc(" · ".join(warnings)),
                               ParagraphStyle("w", parent=meta_st, textColor=colors.red)))
    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph(tr("1. MasterMix ansetzen und je Well verteilen"), section))
    story.append(Spacer(1, 0.1 * cm))
    story.append(_mastermix_table(mm_results, avail_w))
    story.append(Spacer(1, 0.3 * cm))

    compact = _is_compact_plate(plate)
    grid_caption = (tr("2. Proben verteilen (Quell-Koordinate je Well)") if compact
                    else tr("2. Proben verteilen (Template je Well separat zugeben)"))
    story.append(Paragraph(grid_caption, section))
    story.append(Spacer(1, 0.1 * cm))
    story.append(_plate_grid(assignments, avail_w, plate))

    # Standards-Legende bleibt auf Seite 1 (klein, gehört zum Raster)
    std_legend = _standards_legend(assignments, avail_w)
    if std_legend is not None:
        story.append(Spacer(1, 0.3 * cm))
        story.append(Paragraph(tr("Standards (RS/MS)"), section))
        story.append(Spacer(1, 0.1 * cm))
        story.append(std_legend)

    if compact:                          # 384: Quellplatte als Raster IMMER auf Seite 2
        story.append(PageBreak())
        cap = tr("3. Quellplatte (96) — Probenname je Well")
        if sp:
            cap += f"   ·   {_esc(sp)}"
        story.append(Paragraph(cap, section))
        note_st = ParagraphStyle("mapnote", fontName="Helvetica-Oblique", fontSize=7.5,
                                 textColor=colors.HexColor("#555"), leading=10)
        story.append(Paragraph(tr("Position auf der MP96-/Eluat-Platte = Quell-Well der Probe."), note_st))
        story.append(Spacer(1, 0.15 * cm))
        story.append(_source_plate_grid(_source_mapping(assignments), avail_w))

    foot = plate_name or plate_id or "WellDone! — Pipettierschema"
    doc.build(story, canvasmaker=_numbered_canvas_factory(foot))


def export_source_plate_pdf(filepath: str, samples: dict, source_plate_id: str = "",
                            source_plate_name: str = "", meta: dict = None):
    """Eigenes Doku-Blatt für die Proben-/Quellplatte: 96er-Raster mit Probennamen +
    alle MP96-Lauf-Details (Barcodes, Kit, Protokoll, Volumina, Reagenz-/Lot-Barcodes,
    Flags). samples: {well: name} (die geladene Proben-Platte)."""
    meta = meta or {}
    doc = SimpleDocTemplate(filepath, pagesize=landscape(A4),
                            leftMargin=1.0 * cm, rightMargin=1.0 * cm,
                            topMargin=0.8 * cm, bottomMargin=0.8 * cm)
    styles = getSampleStyleSheet()
    title_st = ParagraphStyle("t", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=12, leading=14)
    meta_st = ParagraphStyle("m", parent=styles["Normal"], fontSize=8, leading=10)
    section = ParagraphStyle("s", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=11)
    avail_w = landscape(A4)[0] - doc.leftMargin - doc.rightMargin
    story = []

    sp = " / ".join(x for x in (source_plate_name, source_plate_id) if x)
    head = tr("WellDone! — Proben-Platte (MP96)") + (f"   |   {_esc(sp)}" if sp else "")
    story.append(Paragraph(head, title_st))
    story.append(Paragraph(tr("Erstellt: {when}", when=f"{datetime.now():%d.%m.%Y %H:%M}"), meta_st))
    story.append(Spacer(1, 0.2 * cm))

    story.append(Paragraph(tr("Proben (Position = Quell-Well der MP96-/Eluat-Platte)"), section))
    story.append(Spacer(1, 0.1 * cm))
    story.append(_source_plate_grid(samples, avail_w))
    story.append(Spacer(1, 0.3 * cm))

    detail_rows = [
        (tr("Auftrag (OrderID)"), meta.get("order_id")),
        (tr("Eluat-Platte (Output)"), meta.get("output_plate_id") or source_plate_id),
        (tr("Quell-/Eingangsplatte"), meta.get("sample_plate_id")),
        (tr("Bearbeiter"), meta.get("operator")), (tr("Batch-ID"), meta.get("batch_id")),
        (tr("Status"), meta.get("run_state")), (tr("Gerät (SN)"), meta.get("instrument")),
        (tr("Kit"), meta.get("kit")), (tr("Protokoll"), meta.get("protocol")),
        (tr("Probenvolumen"), f"{meta.get('sample_volume')} µl" if meta.get("sample_volume") else ""),
        (tr("Elutionsvolumen"), f"{meta.get('elution_volume')} µl" if meta.get("elution_volume") else ""),
        (tr("Start"), meta.get("batch_start")), (tr("Ende"), meta.get("batch_end")),
        (tr("Kommentar (Auftrag)"), meta.get("order_comment")),
    ]
    detail_rows = [(k, v) for k, v in detail_rows if v]
    if detail_rows:
        story.append(Paragraph(tr("Lauf-Details"), section))
        story.append(Spacer(1, 0.1 * cm))
        lbl_st = ParagraphStyle("dl", fontName="Helvetica-Bold", fontSize=7.5, leading=9, alignment=TA_RIGHT)
        val_st = ParagraphStyle("dv", fontName="Helvetica", fontSize=7.5, leading=9, alignment=TA_LEFT)
        data = [[Paragraph(_esc(k), lbl_st), Paragraph(_esc(str(v)), val_st)] for k, v in detail_rows]
        t = Table(data, colWidths=[4.5 * cm, 9 * cm], hAlign="LEFT")    # Label rechts, Wert links, eng
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("TOPPADDING", (0, 0), (-1, -1), 0.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 0.5),
                               ("RIGHTPADDING", (0, 0), (0, -1), 6), ("LEFTPADDING", (1, 0), (1, -1), 0)]))
        story.append(t)
        story.append(Spacer(1, 0.2 * cm))

    reag = meta.get("reagents") or []
    if reag:
        story.append(Paragraph(tr("Reagenz-/Lot-Barcodes"), section))
        story.append(Spacer(1, 0.1 * cm))
        rl_st = ParagraphStyle("rl", fontName="Helvetica-Bold", fontSize=7, leading=8.5, alignment=TA_RIGHT)
        rb_st = ParagraphStyle("rb", fontName="Helvetica", fontSize=7, leading=8.5, alignment=TA_LEFT)
        n_pairs = 2 if len(reag) > 6 else 1
        n_rows = (len(reag) + n_pairs - 1) // n_pairs
        data = [[Paragraph("", rb_st) for _ in range(n_pairs * 2)] for _ in range(n_rows)]
        for i, (lbl, bc) in enumerate(reag):              # spaltenweise; je Eintrag Label|Barcode
            r, c = i % n_rows, (i // n_rows) * 2
            data[r][c] = Paragraph(_esc(lbl), rl_st)
            data[r][c + 1] = Paragraph(_esc(bc), rb_st)
        col_w = [3.8 * cm, 4.2 * cm] * n_pairs            # je Paar: Label rechts | Barcode links
        style = [("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 0),
                 ("TOPPADDING", (0, 0), (-1, -1), 0.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 0.5)]
        for p in range(n_pairs):                          # kleiner Abstand Label→Barcode + zwischen Paaren
            style.append(("RIGHTPADDING", (p * 2, 0), (p * 2, -1), 5))
            if p > 0:
                style.append(("LEFTPADDING", (p * 2, 0), (p * 2, -1), 16))
        t = Table(data, colWidths=col_w, hAlign="LEFT")
        t.setStyle(TableStyle(style))
        story.append(t)
    flags = meta.get("flags") or []
    if flags:
        story.append(Spacer(1, 0.15 * cm))
        story.append(Paragraph(tr("Flags"), section))
        for f, d in flags:
            story.append(Paragraph(f"<b>{_esc(f)}</b> – {_esc(d)}", meta_st))

    foot = source_plate_name or source_plate_id or "WellDone! — Proben-Platte"
    doc.build(story, canvasmaker=_numbered_canvas_factory(foot))


def _mastermix_table(mm_results, avail_w) -> Table:
    if not mm_results:
        return Table([[tr("Keine Assays auf der Platte.")]])

    n = len(mm_results)
    label_w = 3.0 * cm
    pair_w = min((avail_w - label_w) / n, 5.0 * cm)
    je_w, ges_w = pair_w * 0.42, pair_w * 0.58
    col_widths = [label_w] + [je_w, ges_w] * n

    header = [_para(f"<b>{tr('Komponente (µl)')}</b>", 7.5, colors.white)]
    for r in mm_results:
        nm = _esc(r.assay.display_name)
        header.append(_para(f"<b>{nm}</b><br/>{tr('je 1 Rkt')}", 6.5, colors.white))
        header.append(_para(f"<b>{nm}</b><br/>{tr('gesamt ({n}×)', n=r.n_reactions_label)}", 6.5, colors.white))

    def row(label, per_fn, tot_fn):
        cells = [label]
        for r in mm_results:
            cells += [de(per_fn(r)), de(tot_fn(r))]
        return cells

    data = [header]
    data.append(row(tr("Wasser"),          lambda r: r.water_per_reaction,     lambda r: r.water_total))
    data.append(row(tr("Primer/Probes"),   lambda r: r.primer_per_reaction,    lambda r: r.primer_total))
    data.append(row(tr("MasterMix"),       lambda r: r.mastermix_per_reaction, lambda r: r.mastermix_total))
    data.append(row(tr("RT-Enzym"),        lambda r: r.rt_per_reaction,        lambda r: r.rt_enzyme_total))
    data.append(row(tr("Summe MasterMix"), lambda r: r.mastermix_volume_per_well, lambda r: r.grand_total))
    tmpl = [tr("+ Template/Probe")]
    rxn = [tr("= Reaktion gesamt")]
    for r in mm_results:
        tmpl += [de(r.template_per_well), tr("pro Well")]
        rxn += [de(r.reaction_volume), ""]
    data.append(tmpl)
    data.append(rxn)

    tbl = Table(data, colWidths=col_widths, repeatRows=1)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2C3E50")),
        ("FONTSIZE",   (0, 0), (-1, -1), 7.5),
        ("GRID",       (0, 0), (-1, -1), 0.3, colors.grey),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN",      (1, 1), (-1, -1), "CENTER"),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ("FONTNAME",   (0, 5), (0, 5), "Helvetica-Bold"),
        ("FONTNAME",   (0, 7), (-1, 7), "Helvetica-Bold"),
        ("BACKGROUND", (0, 5), (-1, 5), colors.HexColor("#ECF0F1")),
        ("BACKGROUND", (0, 7), (-1, 7), colors.HexColor("#FCF3CF")),
    ]
    for i, r in enumerate(mm_results):
        gcol = 2 + i * 2
        # Je Assay zwei Spalten in Well-Farben (wie die Plattenbelegung):
        #   „je 1 Rkt" = aufgehellt im NTC-Ton, „gesamt" = volle Probenfarbe.
        # Schrift hell/dunkel je nach Helligkeit für gute Lesbarkeit.
        fill = r.assay.color
        light = lighten(fill)        # NTC-Ton (aufgehellt)
        style.append(("BACKGROUND", (gcol - 1, 1), (gcol - 1, 6), _hex(light)))
        style.append(("TEXTCOLOR",  (gcol - 1, 1), (gcol - 1, 6),
                      colors.black if _is_light(light) else colors.white))
        style.append(("BACKGROUND", (gcol, 1), (gcol, 6), _hex(fill)))
        style.append(("TEXTCOLOR",  (gcol, 1), (gcol, 6),
                      colors.black if _is_light(fill) else colors.white))
    tbl.setStyle(TableStyle(style))
    return tbl


def _plate_grid(assignments, avail_w, plate=PLATE_96) -> Table:
    """Plattengrafik. Bei 384 (>12 Spalten) zu dicht für Texte → Farb-Map ohne
    Probennamen (Details stehen im Bildschirm-Widget); der Assay-Kopf je Spalte
    entfällt dann, weil eine Spalte im Quadranten-Modus mehrere Assays enthält."""
    rows, cols = plate.rows, plate.cols
    compact = len(cols) > 12
    grid = {a.well: a for a in assignments}

    # Kopfzeilen: bei 96 zusätzlich Assay-Namen je Spalte, sonst nur Spaltennummern.
    header_rows = []
    if not compact:
        col_assay = {}
        for a in assignments:
            col_assay[int(a.well[1:])] = a.assay
        header_assay = [_para("", 6)]
        for c in cols:
            txt = f"<b>{_esc(col_assay[c].display_name)}</b>" if c in col_assay else ""
            header_assay.append(_para(txt, 5.5))
        header_rows.append(header_assay)
    num_pt = 4.5 if compact else 7
    header_rows.append([_para("", 6)] + [_para(f"<b>{c}</b>", num_pt) for c in cols])
    n_header = len(header_rows)

    data = list(header_rows)
    for r in rows:
        line = [_para(f"<b>{r}</b>", num_pt)]
        for c in cols:
            w = f"{r}{c}"
            if w in grid:
                a = grid[w]
                ctrl = is_control(a.role)
                fill = shade(a.role, a.assay.color)
                tcol = colors.black if _is_light(fill) else colors.white
                std = is_standard(a.role)
                if compact:              # 384: Quell-Koordinate (Probe) bzw. Kontroll-/Standard-Kürzel
                    disp = a.source_well or (a.role if (ctrl or std) else "")
                    line.append(_para(_esc(disp), 4.5, tcol, bold=ctrl or std))
                elif ctrl:
                    line.append(_para(_esc(control_label(a.role, ascii_symbol=True, name=a.sample_id)), 6, tcol, bold=True))
                elif std:
                    line.append(_para(_esc(f"{a.role} {a.sample_id}"), 5.5, tcol, bold=True))
                else:
                    line.append(_para(_esc(a.sample_id), 6, tcol))
            else:
                line.append(_para("", 6))
        data.append(line)

    label_w = 0.7 * cm
    max_well_w = 1.15 * cm if compact else 2.15 * cm
    well_w = min((avail_w - label_w) / len(cols), max_well_w)
    body_h = 0.62 * cm if compact else 0.92 * cm
    header_h = [0.30 * cm] if compact else [0.85 * cm, 0.42 * cm]
    col_widths = [label_w] + [well_w] * len(cols)
    row_heights = header_h + [body_h] * len(rows)

    tbl = Table(data, colWidths=col_widths, rowHeights=row_heights)
    style = [
        ("ALIGN",     (0, 0), (-1, -1), "CENTER"),
        ("VALIGN",    (0, 0), (-1, -1), "MIDDLE"),
        ("GRID",      (0, n_header), (-1, -1), 0.3 if compact else 0.4, colors.grey),
        ("LINEBELOW", (1, n_header - 1), (-1, n_header - 1), 0.5, colors.black),
    ]
    if compact:
        style += [
            ("LEFTPADDING",  (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING",   (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
        ]
    for r_i, r in enumerate(rows):
        for c_i, c in enumerate(cols):
            w = f"{r}{c}"
            if w in grid:
                a = grid[w]
                cell = (c_i + 1, r_i + n_header)
                # Positivkontrolle dunkler, Negativkontrolle heller; Proben unverändert
                style.append(("BACKGROUND", cell, cell, _hex(shade(a.role, a.assay.color))))
    tbl.setStyle(TableStyle(style))
    return tbl
