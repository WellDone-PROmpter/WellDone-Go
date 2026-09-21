# WellDone! Go

**DE** · Browser-Variante von **WellDone!** – die **Plattenbelegung**, kompatibel mit
LightCycler® PRO, direkt im Browser: Proben eintragen (oder vom MagNA Pure 96
importieren / aus Excel einfügen), Assays wählen, Platte belegen und als
**Pipettierschema-PDF** und **LC-PRO-CSV** herunterladen. Kein Installieren, keine
Anmeldung. Alles bleibt auf deinem Rechner – **nichts wird hochgeladen** (die
Berechnung läuft clientseitig in [Pyodide](https://pyodide.org/)).

**Ohne Fremd-Server:** Die Pyodide-Laufzeit (0.26.4) und alle benötigten Python-Pakete
(reportlab, Pillow, charset-normalizer) liegen unverändert im Ordner `pyodide/` dieses Repos und werden nur von hier
geladen – kein CDN, kein PyPI. Versionen, Quellen und Lizenzen:
[`pyodide/THIRD_PARTY_NOTICES.md`](pyodide/THIRD_PARTY_NOTICES.md).

> Kostenloses, **nicht validiertes** Hilfswerkzeug; wertet keine Messergebnisse aus. Nicht als
> **Medizinprodukt oder In-vitro-Diagnostikum in Verkehr gebracht**, keine CE-Kennzeichnung,
> regulatorisch nicht formal geprüft. Vor dem Routineeinsatz im Qualitätsmanagement des Labors
> prüfen und freigeben; Belegung, Kontrollen und Mengen vor jedem Lauf prüfen. Die Haftung
> richtet sich nach den gesetzlichen Vorschriften. „Roche“, „LightCycler“ und „MagNA Pure“ sind
> Marken der jeweiligen Inhaber; dieses Projekt ist unabhängig und privat, nicht von Roche
> geprüft oder verantwortet.

Das volle Windows-Programm (384-Wells, Standards, feste Kontroll-Positionen,
LC480-/LC96-Export u. v. m.): **[WellDone! herunterladen](https://welldone-prompter.github.io/WellDone/)** ·
Schwester-App **[PROmpter Go](https://welldone-prompter.github.io/PROmpter-Go/)** (Ergebnis-Übersicht *nach* dem Lauf).

---

**EN** · Browser edition of **WellDone!** – the **plate setup**, compatible with the
LightCycler® PRO, right in the browser: enter samples (or import from the MagNA Pure 96
/ paste from Excel), pick assays, lay out the plate and download it as a **pipetting
scheme PDF** and an **LC-PRO CSV**. No install, no sign-in. Everything stays on your
computer – **nothing is uploaded** (processing runs client-side in
[Pyodide](https://pyodide.org/)).

**No third-party servers:** the Pyodide runtime (0.26.4) and all required Python
packages (reportlab, Pillow, charset-normalizer) are shipped unmodified in this repo's `pyodide/` folder and are loaded
only from here – no CDN, no PyPI. Versions, sources and licences:
[`pyodide/THIRD_PARTY_NOTICES.md`](pyodide/THIRD_PARTY_NOTICES.md).

> Free, **non-validated** helper tool; it does not evaluate any measurement results. **Not placed
> on the market as a medical device or in vitro diagnostic device**, no CE marking, no formal
> regulatory assessment. Before routine use, the laboratory must check and release it within its
> quality management; check the layout, controls and volumes before every run. Liability is
> governed by the statutory provisions. “Roche”, “LightCycler” and “MagNA Pure” are trademarks
> of their respective owners; this is an independent, private project, neither reviewed by nor
> the responsibility of Roche.

The full Windows program (384 wells, standards, fixed control positions, LC480/LC96
export and more): **[Download WellDone!](https://welldone-prompter.github.io/WellDone/)** ·
sister app **[PROmpter Go](https://welldone-prompter.github.io/PROmpter-Go/)** (results overview *after* the run).
