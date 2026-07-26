from dataclasses import dataclass, field

# Platzierungs-Modi der Kontrollen auf der PCR-Platte
LAYOUT_POS_SAMPLES_NEG = "pos_samples_neg"   # Positiv -> Proben -> Negativ (Standard)
LAYOUT_NEG_SAMPLES_POS = "neg_samples_pos"   # Negativ -> Proben -> Positiv
LAYOUT_SAMPLES_POS_NEG = "samples_pos_neg"   # Proben -> Positiv -> Negativ (Kontrollen ans Ende)
LAYOUT_SAMPLES_NEG_POS = "samples_neg_pos"   # Proben -> Negativ -> Positiv
LAYOUT_FIXED = "fixed"                        # Kontrollen an festen Wells, Proben fliessen drumherum
CONTROL_LAYOUTS = (LAYOUT_POS_SAMPLES_NEG, LAYOUT_NEG_SAMPLES_POS,
                   LAYOUT_SAMPLES_POS_NEG, LAYOUT_SAMPLES_NEG_POS, LAYOUT_FIXED)

LAYOUT_LABELS = {
    LAYOUT_POS_SAMPLES_NEG: "Positiv → Proben → Negativ",
    LAYOUT_NEG_SAMPLES_POS: "Negativ → Proben → Positiv",
    LAYOUT_SAMPLES_POS_NEG: "Proben → Positiv → Negativ",
    LAYOUT_SAMPLES_NEG_POS: "Proben → Negativ → Positiv",
    LAYOUT_FIXED: "Feste Positionen",
}

# Plattenformat eines Assays (LCAPs für 96 und 384 sind verschieden)
FORMAT_96 = "96"
FORMAT_384 = "384"
PLATE_FORMATS = (FORMAT_96, FORMAT_384)

# Standard-Rollen im Plate-Setup (zusätzlich zu Kontrollen). Bei externen
# Standardkurven reicht ein Referenzstandard (RS) bzw. Schmelzstandard (MS) je
# Target – jeweils ein kontroll-ähnliches Well, das einen Targetnamen trägt.
STD_RS = "RS"   # Referenzstandard (absolute/relative Quantifizierung, Kalibrierung)
STD_MS = "MS"   # Schmelzstandard (MCGT)
STANDARD_ROLES = (STD_RS, STD_MS)
STANDARD_ROLE_LABELS = {STD_RS: "RS – Referenzstandard", STD_MS: "MS – Schmelzstandard"}

# Kontrolltypen (der LightCycler PRO kennt genau diese vier; DSW-Handbuch S. 316).
# Je Kontrolltyp ist EINE Kontrolle pro Target erlaubt → ein Assay kann mehrere
# Kontrollen desselben Typs führen (z. B. „PTC-Mix I" + „PTC Mix II").
POSITIVE_CONTROL_TYPES = ("PTC", "PPC")   # Reihenfolge: PTC vor PPC
NEGATIVE_CONTROL_TYPES = ("NPC", "NTC")   # Reihenfolge: NPC vor NTC
CONTROL_TYPES = ("PTC", "PPC", "NPC", "NTC")


@dataclass
class Assay:
    id: int
    display_name: str
    lcap_name: str
    pcr_profile: str
    has_ptc: bool
    has_ntc: bool
    color: str          # Hex-Farbe, z.B. "#3498DB"
    water_ul: float
    primer_ul: float
    mastermix_ul: float
    rt_enzyme_ul: float
    template_ul: float = 5.0   # Proben-/Template-Volumen, kommt separat ins Well
    has_npc: bool = False      # NPC = Negativ-Prozesskontrolle
    has_ppc: bool = False      # PPC = Positiv-Prozesskontrolle
    control_layout: str = LAYOUT_POS_SAMPLES_NEG   # Platzierung der Kontrollen (s. LAYOUT_*)
    fixed_wells: dict = field(default_factory=dict)  # nur bei LAYOUT_FIXED: Rolle -> Well, z.B. {"PTC":"A1","NTC":"H12"}
    safety_volume: float = 1.0   # Reserve-Reaktionen gegen Pipettierverlust (0–10, eine Nachkommastelle)
    plate_format: str = "96"     # Plattenformat des Assays: "96" oder "384" (LCAPs unterscheiden sich)
    standards: list = field(default_factory=list)  # [{role:"RS"|"MS", name, target}] – je 1 Well
    control_names: dict = field(default_factory=dict)  # ALT (nur Migration): {Rolle: Name im LCAP}
    controls: list = field(default_factory=list)  # QUELLE DER WAHRHEIT: [{"type":"PTC"|…, "name": str}], Reihenfolge = Belegung

    def __post_init__(self):
        """``controls`` ist maßgeblich. Alte Assays (has_ptc/… + control_names)
        werden EINMALIG in die Liste migriert; danach werden die has_*-Flags aus
        ``controls`` konsistent abgeleitet (nur noch Lese-Bequemlichkeit)."""
        if not self.controls:
            cs = []
            for t in CONTROL_TYPES:
                if getattr(self, "has_" + t.lower(), False):
                    cs.append({"type": t, "name": ((self.control_names or {}).get(t, "") or "").strip()})
            self.controls = cs
        # nur gültige, mit Typ; leere Namen bleiben leer (= Rollen-Code beim Export)
        self.controls = [{"type": c["type"], "name": (c.get("name") or "").strip()}
                         for c in self.controls if c.get("type") in CONTROL_TYPES]
        types = {c["type"] for c in self.controls}
        self.has_ptc, self.has_ppc = "PTC" in types, "PPC" in types
        self.has_npc, self.has_ntc = "NPC" in types, "NTC" in types

    def enabled_standards(self) -> list[dict]:
        """Gültige Standard-Einträge (Rolle, Name und Target gesetzt). ``note`` ist
        optional (Doku, z.B. Konzentration/Titer) und kommt NICHT in die CSV."""
        out = []
        for s in (self.standards or []):
            role = (s.get("role") or "").strip()
            name = (s.get("name") or "").strip()
            target = (s.get("target") or "").strip()
            note = (s.get("note") or "").strip()
            if role in STANDARD_ROLES and name and target:
                out.append({"role": role, "name": name, "target": target, "note": note})
        return out

    def standard_note(self, role: str, name: str) -> str:
        """Optionale Doku-Notiz eines Standards (für Anzeige/PDF, nicht für die CSV)."""
        for s in self.enabled_standards():
            if s["role"] == role and s["name"] == name:
                return s.get("note", "")
        return ""

    @property
    def n_standards(self) -> int:
        return len(self.enabled_standards())

    @property
    def n_controls(self) -> int:
        """Anzahl der Kontroll-Wells (jede Kontrolle belegt genau ein Well)."""
        return len(self.controls)

    @property
    def enabled_controls(self) -> list[str]:
        """Vorhandene Kontroll-TYPEN in kanonischer Reihenfolge (für Anzeige/Zusammenfassung)."""
        present = {c["type"] for c in self.controls}
        return [t for t in CONTROL_TYPES if t in present]

    @staticmethod
    def control_key(c: dict) -> str:
        """SampleId einer Kontrolle auf der Platte: eigener Name, sonst Rollen-Code."""
        return ((c.get("name") or "").strip()) or c["type"]

    def positive_controls(self) -> list[dict]:
        """Positivkontrollen (PTC, PPC) als Instanzen – PTC vor PPC, sonst Eingabereihenfolge."""
        return [c for t in POSITIVE_CONTROL_TYPES for c in self.controls if c["type"] == t]

    def negative_controls(self) -> list[dict]:
        """Negativkontrollen (NPC, NTC) als Instanzen – NPC vor NTC, sonst Eingabereihenfolge."""
        return [c for t in NEGATIVE_CONTROL_TYPES for c in self.controls if c["type"] == t]

    def control_name(self, role: str) -> str:
        """Name der ERSTEN Kontrolle dieses Typs (Kompatibilität); leer → Rollen-Code."""
        for c in self.controls:
            if c["type"] == role:
                return self.control_key(c)
        return role

    @property
    def uses_fixed_layout(self) -> bool:
        return self.control_layout == LAYOUT_FIXED

    def fixed_control_wells(self) -> list[tuple[str, dict]]:
        """Bei festem Layout: ``[(well, control-instanz)]`` für Kontrollen mit gesetztem
        Well. Schlüssel in ``fixed_wells`` ist die SampleId (``control_key``); alte
        Daten mit Rollen-Schlüssel werden als Fallback mitgelesen."""
        if not self.uses_fixed_layout:
            return []
        fw = self.fixed_wells or {}
        out = []
        for c in self.controls:
            well = fw.get(self.control_key(c)) or fw.get(c["type"], "")
            if well:
                out.append((well, c))
        return out

    @property
    def mastermix_volume(self) -> float:
        """Vorgemischter MasterMix pro Reaktion (OHNE Template)."""
        return self.water_ul + self.primer_ul + self.mastermix_ul + self.rt_enzyme_ul

    # Rückwärtskompatibler Alias: total_ul = MasterMix-Volumen (ohne Template)
    @property
    def total_ul(self) -> float:
        return self.mastermix_volume

    @property
    def reaction_volume(self) -> float:
        """Fertige Reaktion im Well = MasterMix + Template."""
        return self.mastermix_volume + self.template_ul

    def __str__(self) -> str:
        return self.display_name
