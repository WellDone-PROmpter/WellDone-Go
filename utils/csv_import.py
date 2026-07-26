"""Template-Import für WellDone!

Liest den Export der MagNA Pure 96 (oder eine generische CSV) ein und liefert
je Well: Name, Note, Sample-ID und Prep-Notes.

MagNA-Pure-96-Format (;-getrennt, Werte in Anführungszeichen):
    "General:Pos";"General:Sample Name";"General:Sample Note";"General:Sample ID";"General:Sample Prep Notes"
    "A1";"1";"2";"A1";"1021_202402211210 Failed R03"

Generische CSV: Spalten wie 'Well'/'Position' und 'Sample'/'Name' genügen.
"""
import csv
from dataclasses import dataclass, field

from utils.csv_export import MIN_SAMPLE_ID, forbidden_chars, FORBIDDEN_SAMPLE_ID
from utils.i18n import tr


@dataclass
class TemplateRecord:
    well: str
    name: str
    note: str = ""
    sample_id: str = ""
    prep_notes: str = ""

    def meta(self) -> dict:
        return {"note": self.note, "sample_id": self.sample_id, "prep_notes": self.prep_notes}


# Kandidaten je Feld (normalisiert: klein, ohne 'general:'-Präfix, getrimmt)
_WELL = ("pos", "position", "well", "wellposition")
_NAME = ("sample name", "name", "probe", "sample")
_NOTE = ("sample note", "note")
_SID = ("sample id", "sampleid", "id")
_PREP = ("sample prep notes", "prep notes", "prep", "prepnotes")


def _norm_header(h: str) -> str:
    h = (h or "").strip().lower()
    if ":" in h:               # 'General:Sample Name' → 'sample name'
        h = h.split(":", 1)[1].strip()
    return h


def _find(fields: list[str], candidates: tuple[str, ...]) -> str | None:
    """Liefert den ORIGINAL-Spaltennamen, dessen normalisierte Form passt (genau, sonst enthält)."""
    norm = {f: _norm_header(f) for f in fields}
    for cand in candidates:                       # exakte Treffer zuerst
        for original, n in norm.items():
            if n == cand:
                return original
    for cand in candidates:                       # dann 'enthält'
        for original, n in norm.items():
            if cand in n:
                return original
    return None


def import_template_csv(filepath: str) -> tuple[list[TemplateRecord], list[str]]:
    """Liest die Datei ein. Liefert (Datensätze, Warnungen)."""
    warnings: list[str] = []
    with open(filepath, newline="", encoding="utf-8-sig") as f:
        head = f.read(4096)
        f.seek(0)
        delimiter = ";" if head.count(";") >= head.count(",") else ","
        reader = csv.DictReader(f, delimiter=delimiter)
        fields = [h for h in (reader.fieldnames or []) if h is not None]

        well_col = _find(fields, _WELL)
        name_col = _find(fields, _NAME)
        if not well_col or not name_col:
            return [], [tr(
                "CSV nicht erkannt. Es werden Spalten für Well/Position und "
                "Sample/Name benötigt.\nGefundene Spalten: {fields}", fields=", ".join(fields))]
        # 'Sample ID' darf nicht zugleich als Name verwendet werden
        sid_col = _find(fields, _SID)
        if name_col == sid_col:
            sid_col = None
        note_col = _find(fields, _NOTE)
        prep_col = _find(fields, _PREP)

        records: list[TemplateRecord] = []
        seen: set[str] = set()
        for row in reader:
            well = (row.get(well_col) or "").strip().upper().replace(" ", "")
            name = (row.get(name_col) or "").strip()
            if not well or not name:
                continue
            if well in seen:
                warnings.append(tr("Well {well} kommt mehrfach vor — nur der erste Eintrag wird genutzt.", well=well))
                continue
            seen.add(well)
            records.append(TemplateRecord(
                well=well,
                name=name,
                note=(row.get(note_col) or "").strip() if note_col else "",
                sample_id=(row.get(sid_col) or "").strip() if sid_col else "",
                prep_notes=(row.get(prep_col) or "").strip() if prep_col else "",
            ))

    if not records:
        warnings.append(tr("Keine Proben in der Datei gefunden."))

    short = [r.name for r in records if 0 < len(r.name.strip()) < MIN_SAMPLE_ID]
    if short:
        sample = ", ".join(f"„{s}“" for s in short[:8]) + (" …" if len(short) > 8 else "")
        warnings.append(tr(
            "{n} Probe(n) mit weniger als {min} Zeichen — der "
            "LightCycler PRO benötigt mindestens {min} Zeichen: {sample}",
            n=len(short), min=MIN_SAMPLE_ID, sample=sample))

    bad = [r.name for r in records if forbidden_chars(r.name, FORBIDDEN_SAMPLE_ID)]
    if bad:
        sample = ", ".join(f"„{s}“" for s in bad[:8]) + (" …" if len(bad) > 8 else "")
        warnings.append(tr(
            "{n} Probe(n) mit unzulässigen Zeichen — der LightCycler PRO "
            "akzeptiert keine der Zeichen ^ ~ \\ & | \" , ; : {sample}",
            n=len(bad), sample=sample))
    return records, warnings
