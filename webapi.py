"""Dünne Brücke JS ↔ Python-Kern für die Browser-Variante (Pyodide).

WICHTIG: Hier steht **keine Fach-Logik** — nur JSON rein / JSON raus über den
UNVERÄNDERTEN, mit dem Desktop geteilten Kern (``models``/``utils``/``db``). Die
gesamte Korrektheit (Plattenbelegung, LC-PRO-CSV) liegt in den geteilten Modulen
und ist über den Golden-Test byte-genau abgesichert. Diese Datei darf das Ergebnis
nur weiterreichen, nie selbst berechnen.

Alle öffentlichen Funktionen nehmen einen JSON-String und geben einen JSON-String
zurück — so gibt es keine heiklen PyProxy-Objekte über die Sprachgrenze."""
import json

from models.assay import Assay  # noqa: F401  (Vollständigkeit / Fehlermeldungen)
from models.plate_layout import calculate_layout, PLATE_96, PLATE_384
from utils.csv_export import (
    build_lcpro_csv, too_short_samples, oversized_samples,
    invalid_char_samples, MIN_SAMPLE_ID, MAX_SAMPLE_ID,
)
from db.assay_serialize import assay_from_dict, assay_to_dict
from utils.controls import shade
from utils.i18n import set_language


def _plate(fmt):
    return PLATE_384 if str(fmt) == "384" else PLATE_96


def _norm_sample(s):
    """Akzeptiert [well, name] oder nur name → (well, name)."""
    if isinstance(s, (list, tuple)):
        return (str(s[0]), str(s[1]))
    return ("", str(s))


def _assignment_to_dict(a):
    """WellAssignment → JSON-Dict für die Oberfläche (Platte einfärben) und Doku."""
    return {
        "well": a.well,
        "sample_id": a.sample_id,
        "role": a.role,
        "source_well": a.source_well,
        "targetname": a.targetname,
        "assay_id": a.assay.id,
        "assay_name": a.assay.display_name,
        "lcap_name": a.assay.lcap_name,
        "color": a.assay.color,
        # Fill-Farbe wie auf dem Desktop: Positivkontrollen dunkler, Negative heller
        # (aus dem GETEILTEN utils.controls.shade — keine Farb-Logik im JS doppeln).
        "fill": shade(a.role, a.assay.color),
    }


def set_lang(lang):
    """Sprache einmalig setzen (Standard 'de'). Betrifft nur Warnmeldungen aus dem Kern."""
    set_language("en" if str(lang).lower().startswith("en") else "de")
    return "ok"


def layout_and_csv(payload_json):
    """Kernaufruf für M1: Belegung rechnen UND LC-PRO-CSV erzeugen.

    payload = {assays:[dict], samples:[[well,name]|name], start_well, column_wise,
               plate_format, plate_id, plate_name}
    return  = {assignments:[dict], warnings:[str], csv:str}
    """
    p = json.loads(payload_json)
    assays = [assay_from_dict(d) for d in p.get("assays", [])]
    samples = [_norm_sample(s) for s in p.get("samples", [])]
    plate = _plate(p.get("plate_format", "96"))

    assignments, warnings = calculate_layout(
        assays, samples,
        start_well=p.get("start_well", "A1"),
        column_wise=bool(p.get("column_wise", True)),
        plate=plate,
    )
    csv_text = build_lcpro_csv(
        assignments,
        plate_id=p.get("plate_id", ""),
        plate_name=p.get("plate_name", ""),
        plate_type=str(p.get("plate_format", "96")),
    )
    # Eingabe-Kontrolle der Probennamen für den LightCycler PRO (GETEILTE Prüf-
    # funktionen aus csv_export → identische Regeln wie der Desktop, kein Drift):
    # < MIN_SAMPLE_ID Zeichen (PRO lehnt ab), > MAX_SAMPLE_ID (wird gekürzt),
    # unzulässige Zeichen (^ ~ \\ & | " + Trenner).
    checks = {
        "too_short": [[w, n] for (w, n) in too_short_samples(samples)],
        "too_long": [[w, n] for (w, n) in oversized_samples(assignments)],
        "bad_chars": [[w, n, "".join(ch)] for (w, n, ch) in invalid_char_samples(samples)],
        "min": MIN_SAMPLE_ID, "max": MAX_SAMPLE_ID,
    }
    return json.dumps({
        "assignments": [_assignment_to_dict(a) for a in assignments],
        "warnings": list(warnings),
        "csv": csv_text,
        "checks": checks,
    })


PDF_PATH = "/wd/WellDone_Pipettierschema.pdf"


def export_pdf(payload_json):
    """Erzeugt das Pipettierschema-PDF für dieselbe Belegung wie ``layout_and_csv``.

    payload = wie layout_and_csv (assays, samples, start_well, column_wise,
              plate_format, plate_id, plate_name) + optional source_plate_id/name, comment
    return  = {ok:true, pdf:<FS-Pfad>, warnings} bzw. {ok:false, error, warnings}
    """
    p = json.loads(payload_json)
    assays = [assay_from_dict(d) for d in p.get("assays", [])]
    samples = [_norm_sample(s) for s in p.get("samples", [])]
    plate = _plate(p.get("plate_format", "96"))

    assignments, warnings = calculate_layout(
        assays, samples,
        start_well=p.get("start_well", "A1"),
        column_wise=bool(p.get("column_wise", True)),
        plate=plate,
    )
    if not assignments:
        return json.dumps({"ok": False, "error": "empty", "warnings": list(warnings)})

    # Lazy: reportlab + PDF-Modul erst hier (im Browser via micropip installiert).
    # summarize_assignments ist die GETEILTE Zählung (auch der Desktop nutzt sie) →
    # die MasterMix-Mengen im PDF können nicht von der Desktop-Version abweichen.
    from utils.mastermix_calc import summarize_assignments
    from utils.pdf_export import export_pipetting_pdf
    mm_results = [mm for *_, mm in summarize_assignments(assignments)]
    export_pipetting_pdf(
        PDF_PATH, assignments, mm_results,
        plate_id=p.get("plate_id", ""), plate_name=p.get("plate_name", ""),
        warnings=list(warnings), comment=p.get("comment", ""),
        plate=plate,
        source_plate_id=p.get("source_plate_id", ""),
        source_plate_name=p.get("source_plate_name", ""),
    )
    return json.dumps({"ok": True, "pdf": PDF_PATH, "warnings": list(warnings)})


def import_samples(path):
    """Liest einen MagNA-Pure-96-Export ein und liefert die Proben je Well.

    .xml → BatchResultDataSet (utils.xml_import), sonst .csv/.txt im „General:Pos…"-
    bzw. generischen Stil (utils.csv_import). GLEICHE Parser wie der Desktop → kein
    Zweit-Parser, kein Drift; die Warnungen (zu kurze/unzulässige Namen) kommen mit.

    return = {ok:true, samples:[[well,name]], warnings:[str], n} bzw. {ok:false, error}
    """
    try:
        if str(path).lower().endswith(".xml"):
            from utils.xml_import import import_template_xml
            records, _meta, warnings = import_template_xml(path)
        else:
            from utils.csv_import import import_template_csv
            records, warnings = import_template_csv(path)
    except Exception as e:
        return json.dumps({"ok": False, "error": "parse", "detail": str(e)})
    samples = [[r.well, r.name] for r in records]
    return json.dumps({"ok": True, "samples": samples, "warnings": list(warnings), "n": len(samples)})


def echo_assay(assay_json):
    """Selbsttest: Assay durch den Kern schicken und kanonisch zurückgeben
    (prüft die geteilte Serialisierung im Browser)."""
    return json.dumps(assay_to_dict(assay_from_dict(json.loads(assay_json))))
