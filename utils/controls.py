"""Kontroll-Rollen und ihre Kennzeichnung — gemeinsam für Bildschirm & PDF.

Positivkontrollen (PTC, PPC) → Symbol ⊕
Negativkontrollen (NTC, NPC) → Symbol ⊖
Proben (Rolle "Unknown" o.Ä.) → kein Symbol, keine Sondermarkierung.

Im PDF wird ein WinAnsi-sicheres Symbol verwendet ((+)/(–)), weil die
Standard-PDF-Schrift Helvetica die eingekreisten Zeichen ⊕/⊖ nicht enthält.
"""

POSITIVE_CONTROLS = {"PTC", "PPC"}
NEGATIVE_CONTROLS = {"NTC", "NPC"}
CONTROLS = POSITIVE_CONTROLS | NEGATIVE_CONTROLS
STANDARDS = {"RS", "MS"}   # Referenz-/Schmelzstandard (kontroll-ähnlich, mit Targetname)


def is_control(role: str) -> bool:
    return role in CONTROLS


def is_standard(role: str) -> bool:
    return role in STANDARDS


def symbol(role: str) -> str:
    """Symbol für den Bildschirm (Qt kann Unicode)."""
    if role in POSITIVE_CONTROLS:
        return "⊕"
    if role in NEGATIVE_CONTROLS:
        return "⊖"
    return ""


def symbol_ascii(role: str) -> str:
    """Symbol für das PDF (Helvetica/WinAnsi-sicher)."""
    if role in POSITIVE_CONTROLS:
        return "(+)"
    if role in NEGATIVE_CONTROLS:
        return "(–)"   # en-dash (–) ist in WinAnsi enthalten
    return ""


def label(role: str, ascii_symbol: bool = False, name: str | None = None) -> str:
    """Anzuzeigender Text einer Kontrolle, z.B. „⊕ PTC" bzw. „(+) PosK".
    ``name`` (optional) = eigener Kontroll-Name (wie im LCAP); leer → Rollen-Code."""
    sym = symbol_ascii(role) if ascii_symbol else symbol(role)
    return f"{sym} {(name or '').strip() or role}".strip()


# ── Farb-Schattierung der Kontrollen ────────────────────────────────────────
# Positivkontrolle = etwas DUNKLER, Negativkontrolle = etwas HELLER als die
# Assay-Farbe. (Sehr helle/weiße Assays werden dadurch bei der Negativkontrolle
# kaum sichtbar – kommt in der Praxis selten vor, und das Symbol ⊖/(–)
# kennzeichnet sie trotzdem eindeutig.)
DARKEN = 0.35     # Anteil Richtung Schwarz für Positivkontrollen
LIGHTEN = 0.45    # Anteil Richtung Weiß für Negativkontrollen


def _clamp(x: float) -> int:
    return max(0, min(255, int(round(x))))


def _to_rgb(hex_color: str):
    h = (hex_color or "").lstrip("#")
    if len(h) != 6:
        return (255, 255, 255)
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def _to_hex(r, g, b) -> str:
    return f"#{_clamp(r):02X}{_clamp(g):02X}{_clamp(b):02X}"


def darken(hex_color: str, amount: float = DARKEN) -> str:
    r, g, b = _to_rgb(hex_color)
    f = 1.0 - amount
    return _to_hex(r * f, g * f, b * f)


def lighten(hex_color: str, amount: float = LIGHTEN) -> str:
    r, g, b = _to_rgb(hex_color)
    return _to_hex(r + (255 - r) * amount, g + (255 - g) * amount, b + (255 - b) * amount)


def shade(role: str, hex_color: str) -> str:
    """Fill-Farbe eines Wells: Positivkontrolle dunkler, Negativkontrolle heller,
    Proben unverändert. Standards (RS/MS) werden wie Positivkontrollen abgedunkelt."""
    if role in POSITIVE_CONTROLS or role in STANDARDS:
        return darken(hex_color)
    if role in NEGATIVE_CONTROLS:
        return lighten(hex_color)
    return hex_color
