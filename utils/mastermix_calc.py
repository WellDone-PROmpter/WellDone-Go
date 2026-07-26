"""
MasterMix-Volumenkalkulation für WellDone!

Wichtig:
  - Der vorgemischte MasterMix besteht NUR aus Wasser + Primer/Probes + MasterMix + RT-Enzym.
  - Das Template (die Probe, z.B. 5 µl) wird NICHT vorgemischt, sondern kommt
    pro Well separat dazu.  → reaction_volume = mastermix + template

Reaktionszahl (pro Assay):
  n_reactions = echte Proben + Anzahl Kontrollen + Anzahl Standards + Sicherheitsvolumen
  Das „Sicherheitsvolumen" (Assay-Feld, Standard 1,0) ist die Reserve gegen
  Pipettierverlust und darf eine Nachkommastelle haben (0–10, z.B. 0,5). Bei
  PTC + NTC und Standard-Reserve 1,0 ergibt das Proben + 3 (wie in der Excel-
  Vorlage); mit zusätzlichen Kontrollen (NPC/PPC) wächst die Reaktionszahl mit.
"""
from dataclasses import dataclass
from models.assay import Assay


@dataclass
class MasterMixResult:
    assay: Assay
    n_samples: int      # nur echte Proben (ohne PTC/NTC)
    n_reactions: float  # inkl. Kontrollen + Sicherheitsvolumen (kann .5 sein)
    water_total: float
    primer_total: float
    mastermix_total: float
    rt_enzyme_total: float

    # ── Aufsummierter MasterMix (das, was vorgemischt wird) ──
    @property
    def grand_total(self) -> float:
        return round(self.water_total + self.primer_total
                     + self.mastermix_total + self.rt_enzyme_total, 1)

    @property
    def n_reactions_label(self) -> str:
        """Reaktionszahl als saubere Anzeige: „10" bzw. „9,5" (de) / „9.5" (en)."""
        from utils.i18n import get_language
        n = self.n_reactions
        if float(n).is_integer():
            return str(int(n))
        s = f"{n:g}"
        return s if get_language() == "en" else s.replace(".", ",")

    # ── Werte pro Einzelreaktion (für das Pipettierschema) ──
    @property
    def water_per_reaction(self) -> float:
        return self.assay.water_ul

    @property
    def primer_per_reaction(self) -> float:
        return self.assay.primer_ul

    @property
    def mastermix_per_reaction(self) -> float:
        return self.assay.mastermix_ul

    @property
    def rt_per_reaction(self) -> float:
        return self.assay.rt_enzyme_ul

    @property
    def mastermix_volume_per_well(self) -> float:
        """Vorgemischter MasterMix, der pro Well verteilt wird (ohne Template)."""
        return self.assay.mastermix_volume

    @property
    def template_per_well(self) -> float:
        """Proben-/Template-Volumen, das pro Well separat zugegeben wird."""
        return self.assay.template_ul

    @property
    def reaction_volume(self) -> float:
        """Fertige Reaktion im Well = MasterMix + Template."""
        return self.assay.reaction_volume


def calculate_mastermix(assay: Assay, n_samples: int) -> MasterMixResult:
    """
    Berechnet die benötigten MasterMix-Gesamtvolumina für einen Assay.

    n_samples: Anzahl echte Proben (OHNE Kontrollen)
    """
    safety = getattr(assay, "safety_volume", 1.0)
    n_standards = getattr(assay, "n_standards", 0)
    n_reactions = n_samples + assay.n_controls + n_standards + safety
    return MasterMixResult(
        assay=assay,
        n_samples=n_samples,
        n_reactions=n_reactions,
        water_total=round(n_reactions * assay.water_ul, 1),
        primer_total=round(n_reactions * assay.primer_ul, 1),
        mastermix_total=round(n_reactions * assay.mastermix_ul, 1),
        rt_enzyme_total=round(n_reactions * assay.rt_enzyme_ul, 1),
    )


def summarize_assignments(assignments):
    """Fasst Belegungen je Assay zusammen: Liste von
    ``(assay, n_samples, n_controls, n_standards, mm_result)`` in Reihenfolge des
    ersten Auftretens. Standards (RS/MS) zählen NICHT als Kontrollen (eigene Wells,
    aber über ``assay.n_standards`` im MasterMix berücksichtigt).

    EINZIGE Quelle dieser Zählung — genutzt vom Desktop (``main_window._pcr_summary``)
    UND von der Browser-Variante (``web/webapi.export_pdf``), damit die MasterMix-
    Mengen beider Wege nie auseinanderdriften.
    """
    from utils.controls import is_control, is_standard
    order, data = [], {}
    for a in assignments:
        if a.assay.id not in data:
            data[a.assay.id] = [a.assay, 0, 0, 0]
            order.append(a.assay.id)
        if a.role == "Unknown":
            data[a.assay.id][1] += 1
        elif is_control(a.role):
            data[a.assay.id][2] += 1
        elif is_standard(a.role):
            data[a.assay.id][3] += 1
    out = []
    for aid in order:
        assay, ns, nc, nstd = data[aid]
        out.append((assay, ns, nc, nstd, calculate_mastermix(assay, ns)))
    return out
