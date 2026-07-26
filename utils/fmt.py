"""Kleine Formatierungs-Helfer für WellDone! (sprachabhängiges Zahlenformat)."""

from utils.i18n import get_language


def de(x: float, decimals: int = 1) -> str:
    """Zahl sprachabhängig formatieren: Deutsch = Dezimal-Komma, Englisch = Punkt.

    Name aus historischen Gründen ``de``; z.B. 9.4 -> „9,4" (de) bzw. „9.4" (en)."""
    s = f"{x:.{decimals}f}"
    return s if get_language() == "en" else s.replace(".", ",")
