"""
Plattenbeleg-Algorithmus für WellDone!  (V3 — Durchlauf-Modell, kumulativ)

Grundidee (Spalten-Modus, Standard):
  - Jeder Assay belegt eine eigene Spalte (für die Mehrkanal-Pipette).
  - Pro Assay GENAU EINE Positivkontrolle (PTC) am Anfang und GENAU EINE
    Negativkontrolle (NTC) ganz am Ende — NICHT mehr je Spalte.
  - Die Proben laufen durch: erst die erste Assay-Spalte von oben nach unten;
    läuft sie über, geht es in der nächsten Spalte desselben Assays weiter.
  - Bei N aktiven Assays liegen die Assay-Spalten verschachtelt nebeneinander
    (Assay1=Sp1, Assay2=Sp2, …). Dieselbe Probe steht je Assay in derselben
    Zeile nebeneinander — ideal fürs zeilenweise Eintragen der Templates.

Kontroll-Platzierung (pro Assay einstellbar, ``Assay.control_layout``):
  - ``pos_samples_neg`` (Standard): Positiv → Proben → Negativ.
  - ``neg_samples_pos``: Negativ → Proben → Positiv (Reihenfolge gedreht).
  - ``fixed``: Die Kontrollen liegen an FESTEN, gewählten Wells (``fixed_wells``,
    typisch im Randbereich); die Proben beginnen am Startpunkt und fließen normal,
    überspringen aber jedes feste Kontroll-Well. Feste Kontrollen werden je Assay
    nur EINMAL gesetzt und „wandern" nicht.

Startpunkt:
  Beim ERSTEN Transfer beginnt die Belegung GENAU im geklickten Well (Zeile UND
  Spalte). Klick auf C11 → PTC sitzt in C11, Proben C11→D11→…; läuft die Spalte
  über, geht es oben in der nächsten Assay-Spalte weiter.

Kumulativ:
  Jeder weitere Transfer beginnt hinter den bereits belegten Wells (nächste
  freie Spalten-/Zeilengruppe, oben beginnend).
  Kontrollen bleiben dabei EINZIG je Assay (über alle Transfers hinweg): eine
  bereits vorhandene vordere Kontrolle wird nicht erneut gesetzt; die bisherige
  hintere Kontrolle wird entfernt und am neuen Ende neu gesetzt — sie „wandert"
  also ans Ende. Diese Regel steckt in apply_transfer(); calculate_transfer()
  selbst platziert weiterhin genau das, was ihm vorgegeben wird.

Zeilen-Modus: um 90° gedreht (Assay = Zeile, vordere Kontrolle links, Proben nach
  rechts, hintere Kontrolle am Ende; läuft die Zeile über, geht es in der nächsten
  Assay-Zeile weiter).
"""
from dataclasses import dataclass
from models.assay import (
    Assay, LAYOUT_FIXED, LAYOUT_NEG_SAMPLES_POS,
    LAYOUT_SAMPLES_POS_NEG, LAYOUT_SAMPLES_NEG_POS,
)
from utils.controls import POSITIVE_CONTROLS, NEGATIVE_CONTROLS, is_control
from utils.i18n import tr


ROWS = "ABCDEFGH"
COLS = list(range(1, 13))  # 1–12

# 384-Well: 16 Zeilen (A–P) × 24 Spalten. _ALL_ROWS ist das Superset, mit dem
# _row_idx/_col_num für BEIDE Größen funktionieren (A–H ist Teilmenge von A–P).
ROWS_384 = "ABCDEFGHIJKLMNOP"
COLS_384 = list(range(1, 25))  # 1–24
_ALL_ROWS = ROWS_384


@dataclass
class WellAssignment:
    well: str            # z.B. "A1"
    sample_id: str       # z.B. "Sample001", "PTC", "NTC", Standardname
    assay: Assay
    role: str            # "PTC" | "NTC" | "Unknown" | "RS" | "MS"
    source_well: str = ""  # Herkunfts-Well auf der Template-Platte (nur bei Proben)
    targetname: str = ""   # nur bei Standards (RS/MS): Ziel-Nukleinsäuresequenz (Pflicht in der CSV)


class PlateSize:
    """Abstraktion der Plattengröße – ermöglicht spätere 384-Well-Erweiterung."""
    def __init__(self, rows: str = ROWS, cols: list[int] = None):
        self.rows = rows
        self.cols = cols if cols is not None else COLS

    @property
    def n_rows(self) -> int:
        return len(self.rows)

    @property
    def n_cols(self) -> int:
        return len(self.cols)

    @property
    def total_wells(self) -> int:
        return self.n_rows * self.n_cols


PLATE_96 = PlateSize()
PLATE_384 = PlateSize(ROWS_384, COLS_384)


def _row_idx(well: str) -> int:
    return _ALL_ROWS.index(well[0])


def _col_num(well: str) -> int:
    return int(well[1:])


# ── 96 → 384 Quadranten-Abbildung (96-Kanal-Stempel) ───────────────────────
# Ein 96er-Layout wird verschachtelt in einen 384-Quadranten abgebildet:
#   96-Zeile r (A=0…)  → 384-Zeile 2*r + row_off  (A,C,E,… bzw. B,D,F,…)
#   96-Spalte c (1-bas.) → 384-Spalte 2*(c-1)+1 + col_off  (1,3,5,… bzw. 2,4,6,…)
# Ein Quadrant ist das Offset-Paar (row_off, col_off) ∈ {0,1}×{0,1};
# die Ursprünge sind A1 (0,0), A2 (0,1), B1 (1,0), B2 (1,1).
# Reihenfolge der vier Stempel — im bzw. gegen den Uhrzeigersinn ab A1:
QUAD_CW = [(0, 0), (0, 1), (1, 1), (1, 0)]   # A1 → A2 → B2 → B1
QUAD_CCW = [(0, 0), (1, 0), (1, 1), (0, 1)]  # A1 → B1 → B2 → A2
N_QUADRANTS = 4


def map96_to_384(well96: str, quadrant: tuple[int, int]) -> str:
    """Bildet ein 96-Well (A1…H12) auf seine 384-Position im Quadranten ab."""
    row_off, col_off = quadrant
    r = _ALL_ROWS.index(well96[0])          # 0–7 (A–H)
    c = int(well96[1:])                     # 1–12
    new_row = _ALL_ROWS[2 * r + row_off]    # A,C,E,… bzw. B,D,F,…
    new_col = 2 * (c - 1) + 1 + col_off     # 1,3,5,… bzw. 2,4,6,…
    return f"{new_row}{new_col}"


def remap_assignments_to_quadrant(assignments: list[WellAssignment],
                                  quadrant: tuple[int, int]) -> list[WellAssignment]:
    """Verschiebt eine fertige 96-Belegung in den angegebenen 384-Quadranten
    (nur das Ziel-Well ändert sich; Probe/Assay/Rolle/Herkunft bleiben)."""
    return [
        WellAssignment(map96_to_384(a.well, quadrant), a.sample_id, a.assay, a.role, a.source_well)
        for a in assignments
    ]


def quadrant_order(clockwise: bool) -> list[tuple[int, int]]:
    """Die vier Quadranten-Offsets in Füll-Reihenfolge (CW oder CCW)."""
    return QUAD_CW if clockwise else QUAD_CCW


def _norm(item) -> tuple[str, str]:
    """Akzeptiert 'name' oder (source_well, name) und liefert (source_well, name)."""
    if isinstance(item, (tuple, list)):
        return str(item[0]), str(item[1])
    return "", str(item)


# ── Kontroll-Rollen je nach Layout ─────────────────────────────────────────
_POS_ROLES = ("PTC", "PPC")   # Reihenfolge: PTC vor PPC
_NEG_ROLES = ("NPC", "NTC")   # Reihenfolge: NPC vor NTC


def _enabled_pos(assay: Assay) -> list[dict]:
    """Positivkontrollen als INSTANZEN (`{type,name}`) – mehrere je Typ möglich."""
    return assay.positive_controls()


def _enabled_neg(assay: Assay) -> list[dict]:
    """Negativkontrollen als INSTANZEN (`{type,name}`) – mehrere je Typ möglich."""
    return assay.negative_controls()


def _ctypes(controls: list[dict]) -> set[str]:
    """Vorkommende Kontroll-TYPEN einer Instanz-Liste (für die Fluss-Klassifikation).
    Der Migrations-Motor entscheidet je Rolle (vorn behalten / hinten wandern) –
    das gilt uniform für beliebig viele Kontrollen desselben Typs."""
    return {c["type"] for c in controls}


def _front_roles(assay: Assay) -> set[str]:
    """Kontroll-TYPEN VORNE im Fluss (je Assay nur EINMAL gesetzt). Bei fixed/proben-zuerst: keine."""
    if assay.control_layout in (LAYOUT_FIXED, LAYOUT_SAMPLES_POS_NEG, LAYOUT_SAMPLES_NEG_POS):
        return set()
    if assay.control_layout == LAYOUT_NEG_SAMPLES_POS:
        return _ctypes(_enabled_neg(assay))
    return _ctypes(_enabled_pos(assay))


def _standard_roles(assay: Assay) -> set[str]:
    """Rollen der aktiven Standards (RS/MS) – sie liegen IMMER am Ende und wandern
    wie End-Kontrollen mit (genau ein Satz je Assay, auch über mehrere Transfers)."""
    return {s["role"] for s in assay.enabled_standards()}


def _end_roles(assay: Assay) -> set[str]:
    """Items HINTEN im Fluss (wandern ans neue Ende). Standards (RS/MS) gehören
    IMMER dazu – auch im festen Layout."""
    std = _standard_roles(assay)
    if assay.control_layout == LAYOUT_FIXED:
        return std
    if assay.control_layout == LAYOUT_NEG_SAMPLES_POS:
        return _ctypes(_enabled_pos(assay)) | std
    if assay.control_layout in (LAYOUT_SAMPLES_POS_NEG, LAYOUT_SAMPLES_NEG_POS):
        return _ctypes(_enabled_pos(assay)) | _ctypes(_enabled_neg(assay)) | std   # ALLE Kontrollen am Ende
    return _ctypes(_enabled_neg(assay)) | std


def _build_sequence(assay: Assay, samples: list[tuple[str, str]],
                    include_front: bool = True) -> list[tuple[str, str, str]]:
    """Fluss-Reihenfolge eines Assays → [(sample_id, role, source_well)].

    - pos_samples_neg (Standard): Positive vorne, Proben, Negative hinten.
    - neg_samples_pos: Negative vorne, Proben, Positive hinten.
    - fixed: KEINE Kontrollen im Fluss (sie liegen fest) → nur Proben.

    include_front=False lässt die vorderen Kontrollen weg (Folge-Transfer, der
    bereits eine vordere Kontrolle auf der Platte hat). Die hinteren Kontrollen
    stehen IMMER am Ende dieses Transfers — der Aufrufer entfernt dafür die
    bisherige hintere Kontrolle, damit es je Assay nur eine gibt."""
    # Items als 4-Tupel: (sample_id, role, source_well, targetname).
    sample_items = [(name, "Unknown", src, "") for src, name in samples]
    std_items = [(s["name"], s["role"], "", s["target"]) for s in assay.enabled_standards()]
    if assay.control_layout == LAYOUT_FIXED:
        return sample_items + std_items                 # Kontrollen liegen fest, Standards ans Ende
    if assay.control_layout == LAYOUT_NEG_SAMPLES_POS:
        front_list, end_list = _enabled_neg(assay), _enabled_pos(assay)
    elif assay.control_layout == LAYOUT_SAMPLES_POS_NEG:
        front_list, end_list = [], _enabled_pos(assay) + _enabled_neg(assay)   # alle ans Ende
    elif assay.control_layout == LAYOUT_SAMPLES_NEG_POS:
        front_list, end_list = [], _enabled_neg(assay) + _enabled_pos(assay)
    else:  # pos_samples_neg (Standard)
        front_list, end_list = _enabled_pos(assay), _enabled_neg(assay)
    front = [(assay.control_key(c), c["type"], "", "") for c in front_list] if include_front else []
    end = [(assay.control_key(c), c["type"], "", "") for c in end_list]
    return front + sample_items + end + std_items       # Standards ganz ans Ende


def _is_plate_well(well: str, plate: PlateSize) -> bool:
    return (len(well) >= 2 and well[0] in plate.rows
            and well[1:].isdigit() and int(well[1:]) in plate.cols)


def assay_fixed_wells(assay: Assay) -> set[str]:
    """Feste Kontroll-Wells eines Assays (leer, wenn kein festes Layout)."""
    return {w for w, _ in assay.fixed_control_wells()}


def fixed_wells_conflict(assay: Assay, others: list[Assay]) -> set[str]:
    """Feste Wells von ``assay``, die mit denen anderer Assays kollidieren.

    Genutzt für die Sperre: zwei gleichzeitig aktive Assays dürfen kein
    gemeinsames festes Kontroll-Well haben (sonst landeten zwei Kontrollen im
    selben Well)."""
    used: set[str] = set()
    for o in others:
        if o.id != assay.id:
            used |= assay_fixed_wells(o)
    return assay_fixed_wells(assay) & used


def plate_profiles(active_assays, existing_assignments) -> set[str]:
    """Alle nicht-leeren PCR-Profile, die nach dem Belegen der ``active_assays``
    auf der Platte lägen (inkl. der bereits belegten Wells). Mehr als ein Eintrag
    = Konflikt: eine Platte darf nur EIN Thermoprofil tragen (der LightCycler PRO
    erlaubt nur ein Run-Profil je Platte, sonst scheitert schon der CSV-Import)."""
    profs = {(getattr(a, "pcr_profile", "") or "").strip() for a in (active_assays or [])}
    profs |= {(getattr(x.assay, "pcr_profile", "") or "").strip() for x in (existing_assignments or [])}
    return {p for p in profs if p}


# ── Quadranten-Belegung (96-Kanal-Stempel, OHNE Fluss) ─────────────────────

def _quadrant_control_order(assay: Assay) -> list[str]:
    """Aktive Kontrollen in Platzierungs-Reihenfolge (für den Quadranten-Modus)."""
    if assay.control_layout in (LAYOUT_NEG_SAMPLES_POS, LAYOUT_SAMPLES_NEG_POS):
        return _enabled_neg(assay) + _enabled_pos(assay)
    return _enabled_pos(assay) + _enabled_neg(assay)


def _quadrant_extra_wells(assay: Assay, sample_wells: list[str],
                          plate96: PlateSize = PLATE_96) -> list[tuple[str, str, str, str]]:
    """[(quell_well_96, role, sample_id, target)] für Kontrollen UND Standards im
    Quadranten-Modus. Kontrollen an festen Wells bzw. an freien 96-Positionen NACH
    den Proben; Standards (RS/MS, mit Targetname) danach an die nächsten freien."""
    seq = [f"{plate96.rows[r]}{c}" for c in plate96.cols for r in range(plate96.n_rows)]
    occupied = set(sample_wells)
    out: list[tuple[str, str, str, str]] = []

    def _free_wells() -> list[str]:
        """Freie 96-Positionen: bevorzugt NACH der letzten belegten Position, sonst
        auf frühere freie Wells ausweichen – so werden Kontrollen/Standards IMMER
        platziert (auch wenn eine Probe im letzten Well H12 liegt)."""
        last = max((seq.index(w) for w in occupied if w in seq), default=-1)
        return ([w for w in seq[last + 1:] if w not in occupied]
                + [w for w in seq[:last + 1] if w not in occupied])

    controls = _quadrant_control_order(assay)   # Instanzen ({type,name})
    if assay.control_layout == LAYOUT_FIXED:
        fw = assay.fixed_wells or {}
        for c in controls:
            w = fw.get(assay.control_key(c)) or fw.get(c["type"], "")
            if w:
                out.append((w, c["type"], assay.control_key(c), ""))
                occupied.add(w)
    else:
        for c, w in zip(controls, _free_wells()):
            out.append((w, c["type"], assay.control_key(c), ""))
            occupied.add(w)

    for s, w in zip(assay.enabled_standards(), _free_wells()):
        out.append((w, s["role"], s["name"], s["target"]))
        occupied.add(w)
    return out


def build_quadrant_layout(active_assays: list[Assay], samples: list,
                          quadrant_offsets: list[tuple[int, int]]) -> list[WellAssignment]:
    """Quadranten-Belegung OHNE Fluss: jedes Quell-Well bleibt an seiner Stelle und
    wird in seinen 2×2-Block abgebildet. ``active_assays[i]`` kommt in
    ``quadrant_offsets[i]``. Kontrollen + Standards je Assay an freie 96-Positionen
    (bzw. feste Wells) – ebenfalls in den Block gestempelt."""
    norm = [_norm(s) for s in samples]                 # (src_well, name)
    sample_wells = [w for w, _ in norm]
    out: list[WellAssignment] = []
    for assay, off in zip(active_assays, quadrant_offsets):
        items = [(w, name, "Unknown", "") for (w, name) in norm]          # (well96, sid, role, target)
        items += [(w, sid, role, target)
                  for (w, role, sid, target) in _quadrant_extra_wells(assay, sample_wells)]
        for w96, sid, role, target in items:
            w384 = map96_to_384(w96, off)
            src = w96 if role == "Unknown" else ""
            out.append(WellAssignment(w384, sid, assay, role, src, target))
    return out


def calculate_transfer(
    active_assays: list[Assay],
    template_samples: list,
    occupied_wells: set[str] | None = None,
    start_well: str = "A1",
    column_wise: bool = True,
    plate: PlateSize = PLATE_96,
    force_start: bool = False,
    front_done: set | None = None,
    reserved_wells: set[str] | None = None,
) -> tuple[list[WellAssignment], list[str]]:
    """Berechnet die Wells für EINEN Transfer.

    force_start=False: schließt an occupied_wells an (nächste freie Spalte/Zeile).
    force_start=True : beginnt EXAKT bei start_well (auch wenn schon Wells belegt
        sind). Ist das nicht möglich (kein Platz oder belegte Wells im Weg), wird
        NICHTS belegt und eine Fehlermeldung zurückgegeben.
    front_done: Menge von Assay-IDs, die bereits ihre vordere Kontrolle auf der
        Platte haben → für diese wird in diesem Transfer KEINE vordere Kontrolle
        gesetzt.
    reserved_wells: feste Kontroll-Wells (aus früheren Transfers), die der
        Probenfluss überspringt und die NICHT zur „weiter geht's"-Spalte zählen.

    Feste Kontrollen (Assays mit control_layout='fixed') werden hier an ihre
    gewählten Wells gesetzt (je Well nur einmal); der Probenfluss überspringt
    alle festen Wells.
    """
    warnings: list[str] = []
    occupied = occupied_wells or set()
    fdone = front_done or set()
    reserved = set(reserved_wells or set())

    if not active_assays:
        return [], [tr("Keine Assays ausgewählt.")]
    if not template_samples:
        return [], [tr("Keine Proben im Template eingetragen.")]

    samples = [_norm(s) for s in template_samples]
    n = len(active_assays)

    # Feste Kontrollen (Layout 'fixed') platzieren bzw. nur reservieren, wenn schon da.
    fixed_assignments: list[WellAssignment] = []
    for assay in active_assays:
        for well, c in assay.fixed_control_wells():
            if not _is_plate_well(well, plate):
                continue
            if well in occupied or well in reserved:
                reserved.add(well)          # schon gesetzt → nur Proben fernhalten
                continue
            fixed_assignments.append(WellAssignment(well, assay.control_key(c), assay, c["type"], ""))
            reserved.add(well)              # neu gesetzt → ebenfalls reservieren

    assignments: list[WellAssignment] = []
    overflow = False

    if column_wise:
        if occupied and not force_start:
            start_col = max(_col_num(w) for w in occupied) + 1
            start_row0 = 0
        else:
            start_col = _col_num(start_well)
            start_row0 = _row_idx(start_well)

        for j, assay in enumerate(active_assays):
            seq = _build_sequence(assay, samples, include_front=assay.id not in fdone)
            base_col = start_col + j
            stream = 0
            row = start_row0
            for sid, role, src, target in seq:
                placed = False
                while True:
                    if row >= plate.n_rows:        # Spalte voll → nächste Assay-Spalte, oben
                        stream += 1
                        row = 0
                    col = base_col + stream * n
                    if col > plate.n_cols:
                        overflow = True
                        break
                    well = f"{plate.rows[row]}{col}"
                    row += 1
                    if well in reserved:           # festes Kontroll-Well → überspringen
                        continue
                    assignments.append(WellAssignment(well, sid, assay, role, src, target))
                    placed = True
                    break
                if not placed:
                    break

    else:  # Zeilen-Modus (um 90° gedreht)
        if occupied and not force_start:
            start_row = max(_row_idx(w) for w in occupied) + 1
            start_cidx = 0
        else:
            start_row = _row_idx(start_well)
            start_cidx = plate.cols.index(_col_num(start_well)) if _col_num(start_well) in plate.cols else 0

        for j, assay in enumerate(active_assays):
            seq = _build_sequence(assay, samples, include_front=assay.id not in fdone)
            base_row = start_row + j
            stream = 0
            cidx = start_cidx
            for sid, role, src, target in seq:
                placed = False
                while True:
                    if cidx >= plate.n_cols:       # Zeile voll → nächste Assay-Zeile, links
                        stream += 1
                        cidx = 0
                    row = base_row + stream * n
                    if row >= plate.n_rows:
                        overflow = True
                        break
                    col = plate.cols[cidx]
                    cidx += 1
                    well = f"{plate.rows[row]}{col}"
                    if well in reserved:           # festes Kontroll-Well → überspringen
                        continue
                    assignments.append(WellAssignment(well, sid, assay, role, src, target))
                    placed = True
                    break
                if not placed:
                    break

    collisions = sorted(a.well for a in assignments if a.well in occupied)

    # Erzwungener Start: die Belegung MUSS exakt bei start_well beginnen.
    # Geht das nicht (kein Platz oder belegte Wells im Weg) → nichts belegen + Fehler.
    if force_start:
        if overflow:
            return [], [tr(
                "Belegung ab {well} nicht möglich: ab hier ist nicht genügend Platz "
                "auf der Platte. Bitte ein weiter oben/links liegendes Start-Well wählen.",
                well=start_well)]
        if collisions:
            preview = ", ".join(collisions[:6]) + (" …" if len(collisions) > 6 else "")
            return [], [tr(
                "Belegung ab {well} nicht möglich: bereits belegte Wells im Weg "
                "({preview}). Bitte ein freies Start-Well mit genügend Platz wählen.",
                well=start_well, preview=preview)]
        return fixed_assignments + assignments, warnings

    # Anschließen-Modus: kollidierende Wells still entfernen, Überlauf nur als Hinweis.
    assignments = [a for a in assignments if a.well not in occupied]
    if overflow:
        warnings.append(tr(
            "PCR-Platte voll — nicht alle Proben passen. "
            "Bitte Proben aufteilen oder früheren Startpunkt wählen."
        ))
    return fixed_assignments + assignments, warnings


def calculate_layout(
    active_assays: list[Assay],
    template_samples: list,
    start_well: str = "A1",
    column_wise: bool = True,
    plate: PlateSize = PLATE_96,
) -> tuple[list[WellAssignment], list[str]]:
    """Einzelne Belegung ohne Vorbelegung (occupied leer)."""
    return calculate_transfer(
        active_assays, template_samples,
        occupied_wells=set(), start_well=start_well,
        column_wise=column_wise, plate=plate,
    )


def apply_transfer(
    existing: list[WellAssignment],
    active_assays: list[Assay],
    template_samples: list,
    start_well: str = "A1",
    column_wise: bool = True,
    force_start: bool = False,
    plate: PlateSize = PLATE_96,
) -> tuple[list[WellAssignment], list[WellAssignment], list[str]]:
    """Fügt EINEN Transfer zu ``existing`` hinzu und hält je Assay GENAU eine
    vordere und eine hintere Kontrolle ein (über alle Transfers hinweg):

      - vordere Kontrolle: wird NUR gesetzt, wenn der Assay noch keine hat → sie
        bleibt vorn an erster Stelle und kommt nie doppelt vor.
      - hintere Kontrolle: die bisherige(n) der aktiven Assays werden ENTFERNT
        und am neuen Ende neu gesetzt → sie „wandert" ans Ende und kommt nie
        doppelt vor.
      - feste Kontrollen (Layout 'fixed'): bleiben unverändert an ihren Wells
        (werden nur einmal gesetzt, wandern nicht) und der Probenfluss umgeht sie.
      - Anschließen (kein expliziter Startpunkt): die Belegung macht GENAU dort
        weiter, wo die bisherige hintere Kontrolle saß → lückenlos.

    Liefert ``(added, removed, warnings)``:
      added   = neu belegte Wells (Proben + ggf. vordere/feste Kontrollen + neue hintere),
      removed = entfernte alte hintere Kontrollen (für Undo/erneutes Setzen).
    Bei Misserfolg (z.B. force_start nicht möglich) → ``([], [], warnings)``.
    """
    active_by_id = {a.id: a for a in active_assays}

    front_done: set = set()       # Assay-IDs mit bereits gesetzter vorderer Kontrolle
    removed: list[WellAssignment] = []   # hintere (wandernde) Kontrollen aktiver Assays
    reserved: set[str] = set()    # feste Kontroll-Wells aktiver Assays (bleiben)
    occupied: set[str] = set()    # Fluss-Wells + alles von inaktiven Assays

    for x in existing:
        a = active_by_id.get(x.assay.id)
        if a is None:
            occupied.add(x.well)                      # inaktiver Assay → Well blockiert
            continue
        if a.control_layout == LAYOUT_FIXED and is_control(x.role):
            reserved.add(x.well)                      # feste Kontrolle bleibt
        elif x.role in _front_roles(a):
            front_done.add(a.id)
            occupied.add(x.well)                      # vordere Kontrolle bleibt im Fluss
        elif x.role in _end_roles(a):
            removed.append(x)                         # hintere Kontrolle wandert → Zelle frei
        else:
            occupied.add(x.well)                      # Probe

    # Wiederaufnahme: beim Anschließen (kein expliziter Start) genau dort weiter,
    # wo die bisherige hintere Kontrolle des ERSTEN aktiven Assays saß → keine Lücke.
    resume_well = None
    if not force_start and removed and active_assays:
        first_id = active_assays[0].id
        ends0 = [x for x in removed if x.assay.id == first_id]
        if ends0:
            if column_wise:
                pos = lambda x: (_col_num(x.well), _row_idx(x.well))
            else:
                pos = lambda x: (_row_idx(x.well), _col_num(x.well))
            resume_well = min(ends0, key=pos).well

    def _run(sw, fs):
        return calculate_transfer(
            active_assays, template_samples,
            occupied_wells=occupied, start_well=sw,
            column_wise=column_wise, plate=plate,
            force_start=fs, front_done=front_done, reserved_wells=reserved,
        )

    if resume_well is not None:
        added, warnings = _run(resume_well, True)      # exakt ab der frei gewordenen Zelle
        if not added:                                  # kein Platz ab dort?
            added, warnings = _run(start_well, False)  # Fallback: nächste Spalte/Zeile
    else:
        added, warnings = _run(start_well, force_start)

    if not added:
        return [], [], warnings        # nichts platziert → auch nichts entfernen
    return added, removed, warnings
