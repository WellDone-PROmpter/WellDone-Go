"""XML-Import für WellDone! — MagNA Pure 96/24 „BatchResultDataSet"-Export.

Gilt gleichermaßen für die MagNA Pure 96 UND die MagNA Pure 24: beide Geräte
exportieren pro Lauf dasselbe „BatchResultDataSet"-Schema (nur die Ausgabe-
Geometrie unterscheidet sich — 96-Well-Platte vs. 8er-Streifen, Positionen A1–H3).

Liefert dieselben Probendaten wie der CSV-/TXT-Export (Pos · Name · Note · ID · Prep-Notes)
PLUS die Platten-/Lauf-Metadaten, die nur im XML stehen (Barcodes, Kit, Protokoll, Volumina …).

Aufbau der Datei (Namespace http://tempuri.org/BatchResultDataSet.xsd):
    <BatchInformation>   … OutputPlateId, OrderID, SamplePlateId, Operator, BatchId, RunState …
    <BatchTestparameter> … KitName, PurificationProtocol, SampleVolume, ElutionVolume
    <SampleData>*        … Number, SampleID, Comment, SamplePos, Flags, ResultStatus
"""
import xml.etree.ElementTree as ET

from utils.csv_import import TemplateRecord
from utils.csv_export import MIN_SAMPLE_ID, forbidden_chars, FORBIDDEN_SAMPLE_ID
from utils.i18n import tr


def _local(tag: str) -> str:
    """Lokaler Tag-Name ohne Namespace ('{…}SampleData' → 'SampleData')."""
    return tag.split("}")[-1] if "}" in tag else tag


def _clean(v: str) -> str:
    """Leerwert-Platzhalter neutralisieren: MP24 (und teils MP96) schreiben „n/a"
    in leere Felder – das soll nicht in Feldern (z. B. Quellplatte-ID) oder in den
    Prep-Notes landen. Leerstring/„n/a" → „", sonst unverändert."""
    return "" if str(v).strip().lower() in ("", "n/a") else v


def _translate_flags(flags_str: str, flag_map: dict[str, str]) -> str:
    """Hängt an jeden Flag-Code aus dem Feld <Flags> seine Klartext-Erklärung aus den
    <FlagDefinitions> an, z. B. „R03" → „R03 (Reagent Expiration Rule overridden)".
    Mehrere Codes (durch Leerzeichen/Komma/Semikolon getrennt) werden einzeln übersetzt;
    ein Code ohne Definition bleibt unverändert (wir erfinden keine Erklärung)."""
    out = []
    for code in flags_str.replace(",", " ").replace(";", " ").split():
        desc = flag_map.get(code)
        out.append(f"{code} ({desc})" if desc else code)
    return " ".join(out)


def import_template_xml(filepath: str) -> tuple[list[TemplateRecord], dict, list[str]]:
    """Liest die XML-Datei ein. Liefert (Datensätze, Metadaten, Warnungen)."""
    warnings: list[str] = []
    try:
        root = ET.parse(filepath).getroot()
    except Exception as e:
        return [], {}, [tr("XML konnte nicht gelesen werden: {e}", e=e)]

    # Kopf-/Lauf-Infos + Flag-Erklärungen + Reagenz-Barcodes einsammeln
    info: dict[str, str] = {}
    flags: list[tuple[str, str]] = []        # (Flag, Erklärung), z. B. ("R03", "Reagent Expiration …")
    reagents: list[tuple[str, str]] = []     # (Bezeichnung, Barcode), z. B. ("MGP", "0012…")
    for el in root:
        ln = _local(el.tag)
        if ln in ("BatchInformation", "BatchTestparameter"):
            for child in el:
                info[_local(child.tag)] = (child.text or "").strip()
        elif ln == "FlagDefinitions":
            d = {_local(c.tag): (c.text or "").strip() for c in el}
            if d.get("Flag"):
                flags.append((d["Flag"], d.get("Description", "")))
        elif ln == "AuditTrail":
            # Der „Processing started"-Eintrag listet im Info-Freitext alle Reagenz-/Lot-Barcodes
            # als Zeilen „<Bezeichnung> - BC: <Barcode>".
            d = {_local(c.tag): (c.text or "") for c in el}
            for line in (d.get("Info") or "").splitlines():
                if "- BC:" in line:
                    label, _, bc = line.partition("- BC:")
                    label, bc = label.strip(), bc.strip()
                    if label and bc:
                        reagents.append((label, bc))

    # MP24 (und teils MP96) füllen leere Felder mit „n/a" statt leer → neutralisieren,
    # damit „n/a" nicht in „Quellplatte-ID"/„Bezeichnung" oder in den Prep-Notes landet.
    info = {k: _clean(v) for k, v in info.items()}

    # Proben (SampleData → TemplateRecord), konsistent zum CSV-Mapping
    records: list[TemplateRecord] = []
    seen: set[str] = set()
    batch_id = info.get("BatchId", "")
    flag_map = dict(flags)   # Code → Erklärung (für die Inline-Übersetzung in den Prep-Notes)
    for el in root:
        if _local(el.tag) != "SampleData":
            continue
        d = {_local(c.tag): (c.text or "").strip() for c in el}
        well = d.get("SamplePos", "").upper().replace(" ", "")
        name = d.get("SampleID", "")
        if not well or not name:
            continue
        if well in seen:
            warnings.append(tr("Well {well} kommt mehrfach vor — nur der erste Eintrag wird genutzt.", well=well))
            continue
        seen.add(well)
        prep = " ".join(x for x in (
            batch_id, d.get("ResultStatus", ""), _translate_flags(d.get("Flags", ""), flag_map)
        ) if x)
        records.append(TemplateRecord(
            well=well, name=name, note=d.get("Comment", ""), sample_id=well, prep_notes=prep,
        ))

    if not records:
        warnings.append(tr("Keine Proben (SampleData) in der XML-Datei gefunden."))

    # Gleiche Hinweise wie beim CSV-Import (zu kurze / unzulässige Namen)
    short = [r.name for r in records if 0 < len(r.name.strip()) < MIN_SAMPLE_ID]
    if short:
        sample = ", ".join(f"„{s}“" for s in short[:8]) + (" …" if len(short) > 8 else "")
        warnings.append(tr("{n} Probe(n) mit weniger als {min} Zeichen: {sample}",
                           n=len(short), min=MIN_SAMPLE_ID, sample=sample))
    bad = [r.name for r in records if forbidden_chars(r.name, FORBIDDEN_SAMPLE_ID)]
    if bad:
        sample = ", ".join(f"„{s}“" for s in bad[:8]) + (" …" if len(bad) > 8 else "")
        warnings.append(tr("{n} Probe(n) mit unzulässigen Zeichen: {sample}",
                           n=len(bad), sample=sample))

    # Metadaten für Felder (Quellplatte-ID/Plattenbezeichnung) + „Details Platte"-Popup
    meta = {
        "output_plate_id": info.get("OutputPlateId", ""),     # → Quellplatte-ID (Eluat-Platte)
        "order_id": info.get("OrderID", ""),                  # → Plattenbezeichnung
        "sample_plate_id": info.get("SamplePlateId", ""),     # Eingangs-/Rohplatte
        "operator": info.get("Operator", ""),
        "batch_id": batch_id,
        "run_state": info.get("RunState", ""),
        "instrument": info.get("InstrumentSerialNumber", ""),
        "kit": info.get("KitName", ""),
        "protocol": info.get("PurificationProtocol", ""),
        "sample_volume": info.get("SampleVolume", ""),
        "elution_volume": info.get("ElutionVolume", ""),
        "batch_start": info.get("BatchStartDateTime", ""),
        "batch_end": info.get("BatchEndDateTime", ""),
        "order_comment": info.get("OrderComment", ""),
        "flags": flags,                                   # [(Flag, Erklärung), …]
        "reagents": reagents,                             # [(Bezeichnung, Barcode), …]
    }
    return records, meta, warnings
