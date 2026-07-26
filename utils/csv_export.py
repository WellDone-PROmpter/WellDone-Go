"""LC-PRO CSV-Export für WellDone! — erzeugt das offizielle 12-spaltige Importformat.

Hinweise aus der Roche-Anleitung ("Tips for creating .csv files for effective
LC PRO plate setup"):
  - Spaltenstruktur und -reihenfolge dürfen NICHT verändert werden.
  - Pflichtfelder: PlateType, SampleId, WellPosition, AssayName, RunProfileName, SampleRole.
  - SampleId darf max. 23 Zeichen lang sein (längere kann die ISW nicht speichern)
    → wir kürzen beim Export hinten (der Anfang bleibt erhalten).
  - AssayName = LCAP-Name; RunProfileName = PCR-Profil (100% case-sensitive).
  - Nur eine PlateID pro Datei.
"""
import csv
import io
from models.plate_layout import WellAssignment

MAX_SAMPLE_ID = 23
MIN_SAMPLE_ID = 2   # der LightCycler PRO akzeptiert keine 1-Zeichen-Probennamen

HEADER = [
    "PlateId", "PlatesetupName", "PlateType", "SampleId", "WellPosition",
    "AssayName", "Targetname", "Dilution", "MasterMixName", "LotNumber",
    "RunProfileName", "SampleRole",
]

# ── Vom LightCycler PRO nicht unterstützte Zeichen je Feld (Roche-CSV-Spezifikation) ──
# Komma und Semikolon kommen überall dazu: als Zellwert zerstören sie den Import,
# weil die ISW naiv am Komma trennt.
_SEP = {",", ";"}
FORBIDDEN_SAMPLE_ID = {"^", "~", "\\", "&", "|", '"'} | _SEP
FORBIDDEN_PLATE_ID = {"|", "&", "~", "^", "\\"} | _SEP
FORBIDDEN_PLATESETUP = {"|", "%", "^", "[", "]", "{", "}", "\\"} | _SEP


def forbidden_chars(text: str, charset: set) -> list[str]:
    """Die in ``text`` vorkommenden unzulässigen Zeichen aus ``charset`` (eindeutig, sortiert)."""
    return sorted({ch for ch in (text or "") if ch in charset})


def invalid_char_samples(pairs, charset: set = FORBIDDEN_SAMPLE_ID) -> list[tuple[str, str, list[str]]]:
    """``(source_well, name, [unzulässige Zeichen])`` für Proben mit unzulässigen
    Zeichen – eindeutig nach (Well, Name), in Reihenfolge des ersten Auftretens.
    ``pairs`` ist eine Folge von ``(source_well, name)``."""
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str, list[str]]] = []
    for well, name in pairs:
        n = (name or "").strip()
        bad = forbidden_chars(n, charset)
        if bad and (well, n) not in seen:
            seen.add((well, n))
            out.append((well, n, bad))
    return out


def trim_sample_id(name: str, limit: int = MAX_SAMPLE_ID) -> str:
    """Kürzt einen Probennamen für die LC-PRO-Datei: hinten abschneiden (Anfang behalten)."""
    name = (name or "").strip()
    return name[:limit]


def too_short_samples(pairs, minimum: int = MIN_SAMPLE_ID) -> list[tuple[str, str]]:
    """``(source_well, name)`` der Proben, deren Name weniger als ``minimum``
    Zeichen hat (vom LightCycler PRO nicht akzeptiert) – eindeutig nach
    (Probenplatten-Well, Name), in Reihenfolge des ersten Auftretens.
    ``pairs`` ist eine Folge von ``(source_well, name)``."""
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str]] = []
    for well, name in pairs:
        n = (name or "").strip()
        if 0 < len(n) < minimum and (well, n) not in seen:
            seen.add((well, n))
            out.append((well, n))
    return out


def oversized_samples(assignments, limit: int = MAX_SAMPLE_ID) -> list[tuple[str, str]]:
    """Liefert ``(source_well, name)`` der Proben, die für den LC-PRO-Export
    gekürzt werden (Name länger als ``limit`` Zeichen) – eindeutig nach
    (Probenplatten-Well, Name) und in Reihenfolge des ersten Auftretens.
    Dient dazu, den Nutzer VOR dem Export zu warnen und ihm das betroffene
    Feld der Probenplatte zu nennen."""
    seen: set[tuple[str, str]] = set()
    out: list[tuple[str, str]] = []
    for a in assignments:
        name = (a.sample_id or "").strip()
        if len(name) <= limit:
            continue
        key = (a.source_well, name)
        if key in seen:
            continue
        seen.add(key)
        out.append(key)
    return out


def _lcpro_rows(
    assignments: list[WellAssignment],
    plate_id: str,
    plate_name: str,
    plate_type: str,
) -> list[list[str]]:
    """Die CSV-Zeilen (inkl. Kopfzeile) als reine Datenstruktur — EINZIGE Quelle
    des Zeilenformats. Sowohl die Datei-Ausgabe (Desktop) als auch die
    String-Ausgabe (Web/Pyodide) bauen darauf auf, damit das Format nicht
    auseinanderdriften kann."""
    rows: list[list[str]] = [list(HEADER)]
    for a in assignments:
        rows.append([
            plate_id,                       # PlateId (eine pro Datei)
            plate_name,                     # PlatesetupName
            plate_type,                     # PlateType (96 / 384)
            trim_sample_id(a.sample_id),    # SampleId (max. 23 Zeichen)
            a.well,                         # WellPosition
            a.assay.lcap_name,              # AssayName (= LCAP-Name)
            getattr(a, "targetname", ""),   # Targetname (Pflicht bei Standards RS/MS)
            "",                             # Dilution (nur bei In-run-QS – hier nicht genutzt)
            "",                             # MasterMixName
            "",                             # LotNumber
            a.assay.pcr_profile,            # RunProfileName (= PCR-Profil)
            a.role,                         # SampleRole (Unknown/PTC/NTC/…/RS/MS)
        ])
    return rows


def build_lcpro_csv(
    assignments: list[WellAssignment],
    plate_id: str = "",
    plate_name: str = "",
    plate_type: str = "96",
) -> str:
    """Liefert die LC-PRO-CSV als Text (identisch zum Datei-Inhalt von
    ``export_lcpro_csv``). Für die Browser-Variante, die keine Datei schreibt,
    sondern den String als Download/Blob ausgibt."""
    buf = io.StringIO(newline="")   # newline="" → csv-eigenes \r\n bleibt unverändert
    csv.writer(buf, delimiter=",").writerows(
        _lcpro_rows(assignments, plate_id, plate_name, plate_type))
    return buf.getvalue()


def export_lcpro_csv(
    assignments: list[WellAssignment],
    filepath: str,
    plate_id: str = "",
    plate_name: str = "",
    plate_type: str = "96",
):
    """Schreibt eine CSV-Datei im LightCycler-PRO-Importformat.

    plate_type: „96" oder „384" – wird in die Spalte PlateType geschrieben.
    """
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        csv.writer(f, delimiter=",").writerows(
            _lcpro_rows(assignments, plate_id, plate_name, plate_type))
