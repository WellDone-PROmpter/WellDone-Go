"""Kanonische Assay ↔ JSON-Dict-Umwandlung — GETEILTE Quelle für Desktop und Web.

Warum ein eigenes Modul (statt in ``assay_db.py``):
  * Die Desktop-DB-Schicht (SQLite in ``assay_db.py``) bleibt **unangetastet** —
    kein Risiko für die laufende, veröffentlichte App.
  * Die Browser-Variante (Pyodide) speichert Assays als **JSON in IndexedDB**.
    Sie nutzt hier ``assay_from_dict``/``assay_to_dict``, damit ein Assay im Web
    und auf dem Desktop **dieselben Feldbedeutungen** hat und zu **demselben
    ``Assay``-Objekt** zurückführt.

Der eigentliche Korrektheits-Anker ist ``Assay`` → ``calculate_layout`` →
``build_lcpro_csv`` (im Golden-Test byte-genau eingefroren). Solange beide Wege
gleichwertige ``Assay``-Objekte erzeugen, kann die Geräte-CSV nicht driften —
egal ob der Assay aus SQLite (Desktop) oder aus IndexedDB (Web) stammt.

Das Dict verwendet ausschließlich JSON-native Typen (str/float/bool/list/dict),
sodass es sich im Browser direkt mit ``JSON.stringify``/``JSON.parse`` ablegen und
lesen lässt. Verschachtelte Felder (``fixed_wells``, ``standards``, ``controls``)
bleiben echte Listen/Dicts — im Gegensatz zur SQLite-Ablage, die sie als
JSON-Strings in TEXT-Spalten hält.
"""
from models.assay import Assay


def assay_to_dict(a: Assay) -> dict:
    """``Assay`` → JSON-fähiges Dict (für IndexedDB / Export).

    ``controls`` ist die Quelle der Wahrheit; die abgeleiteten ``has_*``-Flags und
    das alte ``control_names`` werden NICHT geschrieben (``__post_init__`` stellt sie
    beim Zurücklesen wieder her)."""
    return {
        "id": a.id,
        "display_name": a.display_name,
        "lcap_name": a.lcap_name,
        "pcr_profile": a.pcr_profile,
        "color": a.color,
        "water_ul": a.water_ul,
        "primer_ul": a.primer_ul,
        "mastermix_ul": a.mastermix_ul,
        "rt_enzyme_ul": a.rt_enzyme_ul,
        "template_ul": a.template_ul,
        "control_layout": a.control_layout,
        "fixed_wells": dict(a.fixed_wells or {}),
        "safety_volume": a.safety_volume,
        "plate_format": a.plate_format,
        "standards": [dict(s) for s in (a.standards or [])],
        "controls": [dict(c) for c in (a.controls or [])],
    }


def assay_from_dict(d: dict) -> Assay:
    """JSON-Dict → ``Assay``. Fehlende Felder werden mit denselben Standardwerten
    belegt wie beim Neuanlegen; ``has_*`` werden bewusst NICHT gesetzt, sondern von
    ``Assay.__post_init__`` aus ``controls`` abgeleitet."""
    d = d or {}
    return Assay(
        id=d.get("id"),
        display_name=(d.get("display_name") or "").strip(),
        lcap_name=(d.get("lcap_name") or "").strip(),
        pcr_profile=(d.get("pcr_profile") or "").strip(),
        has_ptc=False, has_ntc=False,   # → __post_init__ leitet has_* aus controls ab
        color=d.get("color") or "#3498DB",
        water_ul=float(d.get("water_ul") or 0.0),
        primer_ul=float(d.get("primer_ul") or 0.0),
        mastermix_ul=float(d.get("mastermix_ul") or 0.0),
        rt_enzyme_ul=float(d.get("rt_enzyme_ul") or 0.0),
        template_ul=float(d.get("template_ul", 5.0)),
        control_layout=d.get("control_layout") or "pos_samples_neg",
        fixed_wells=dict(d.get("fixed_wells") or {}),
        safety_volume=float(d.get("safety_volume", 1.0)),
        plate_format=d.get("plate_format") or "96",
        standards=[dict(s) for s in (d.get("standards") or [])],
        controls=[dict(c) for c in (d.get("controls") or [])],
    )
