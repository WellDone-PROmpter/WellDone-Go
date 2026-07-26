"""Kleine, eigene Mehrsprachigkeit (Deutsch/Englisch) für WellDone!.

Gleiche Mechanik wie bei PROmpter (Schwester-Programm): ein schlankes Wörterbuch,
KEIN Qt-Linguist/.ts/.qm.

* **Schlüssel = die deutsche Quell-Zeichenkette** (wie ``gettext``-msgid). Fehlt
  eine Übersetzung, bleibt sicher Deutsch stehen (Fallback, kein Absturz).
* Funktion heißt ``tr`` (nicht ``t``), weil ``t`` an vielen Stellen schon als
  lokale Variable/Lambda-Parameter dient. Erster Parameter ``_src`` (nicht
  ``text``), damit ein Platzhalter ``{text}`` gefahrlos als kwarg geht.

Die Sprache wird beim Programmstart EINMAL gesetzt (``set_language`` in main.py,
vor dem Aufbau der Oberfläche); ein Wechsel greift nach einem Neustart.
"""

from __future__ import annotations

_LANG = "de"


def set_language(lang: str) -> None:
    """Setzt die aktive Sprache (alles außer 'en…' gilt als Deutsch)."""
    global _LANG
    _LANG = "en" if str(lang or "").lower().startswith("en") else "de"


def get_language() -> str:
    """Aktive Sprache: 'de' oder 'en'."""
    return _LANG


def tr(_src: str, **kwargs) -> str:
    """Übersetzt die deutsche Quell-Zeichenkette in die aktive Sprache.

    Fehlt eine Übersetzung, bleibt der deutsche Text stehen. ``{platzhalter}``
    werden – falls kwargs übergeben werden – per ``str.format`` eingesetzt."""
    s = _EN.get(_src, _src) if _LANG == "en" else _src
    return s.format(**kwargs) if kwargs else s


# ───────────────────────────────────────────────────────────────────────────
# Deutsch → Englisch. Schlüssel müssen EXAKT der deutschen Quelle entsprechen.
# Einträge mit Deutsch == Englisch sind weggelassen (Fallback liefert dasselbe).
# ───────────────────────────────────────────────────────────────────────────
_EN: dict[str, str] = {
    # ── Über/App (utils/resources.py, about_dialog) ───────────────────────
    "Plattenbelegung für den Roche LightCycler PRO":
        "Plate setup for the Roche LightCycler PRO",
    "Über {name} / Hilfe": "About {name} / Help",
    "Version {v} · {b}": "Version {v} · {b}",
    "Deine Version: {v}": "Your version: {v}",
    "⬇  Neue Version herunterladen": "⬇  Download new version",
    "Erfasst Proben, belegt die PCR-Platte automatisch und erzeugt das "
    "Pipettierschema (PDF) sowie das Plate-Setup (CSV) für den Roche "
    "LightCycler PRO.":
        "Records samples, sets up the PCR plate automatically and creates the "
        "pipetting scheme (PDF) and the plate setup (CSV) for the Roche LightCycler PRO.",
    "Hinweis: Hilfswerkzeug, nicht validiert – bitte Belegung, Kontrollen "
    "und MasterMix-Mengen vor jedem Lauf prüfen.":
        "Note: helper tool, not validated – please check setup, controls and "
        "MasterMix volumes before every run.",
    "📖  Handbuch öffnen (PDF)": "📖  Open manual (PDF)",
    '🌐 <a href="{url}">Download- &amp; Infoseite (GitHub)</a>':
        '🌐 <a href="{url}">Downloads &amp; info page (GitHub)</a>',
    '🧪 Schwester-App: <a href="{url}">PROmpter</a> — bereitet die '
    'Ergebnisse des LightCycler PRO <b>nach</b> dem Lauf zu PDF-Bericht '
    '&amp; Excel-Tabelle auf. (WellDone = Vorbereitung, PROmpter = Auswertung.)':
        '🧪 Sister app: <a href="{url}">PROmpter</a> — turns the LightCycler PRO '
        'results <b>after</b> the run into a PDF report &amp; Excel table. '
        '(WellDone = preparation, PROmpter = analysis.)',
    "Feedback & Verbesserungsvorschläge": "Feedback & suggestions",
    "Open-Source-Bibliotheken: ": "Open-source libraries: ",
    "Schließen": "Close",
    "Abbrechen": "Cancel",
    "Speichern": "Save",
    "Ja": "Yes",
    "Nein": "No",
    "Handbuch": "Manual",
    "Bitte öffnen Sie das Handbuch manuell:\n{path}":
        "Please open the manual manually:\n{path}",
    "Das Handbuch-PDF wurde nicht gefunden.": "The manual PDF was not found.",
    "Download": "Download",
    "Es ist noch kein Download-Link hinterlegt. "
    "Bitte den Ersteller der App kontaktieren.":
        "No download link has been set yet. Please contact the app's author.",
    "Deine Version: {v}  ·  prüfe auf Updates …":
        "Your version: {v}  ·  checking for updates …",
    "⚠  Neue Version verfügbar: {latest}  (du hast {have})":
        "⚠  New version available: {latest}  (you have {have})",
    "✓  Du hast die aktuelle Version ({v}).":
        "✓  You have the current version ({v}).",
    "Deine Version: {v}  ·  aktuelle Version konnte nicht geprüft werden (offline?).":
        "Your version: {v}  ·  current version could not be checked (offline?).",

    # ── Hauptfenster (ui/main_window.py) ───────────────────────────────────
    "WellDone! — Plattenbelegung für den Roche LightCycler PRO":
        "WellDone! — Plate setup for the Roche LightCycler PRO",
    "PROBEN-PLATTE": "SAMPLE PLATE",
    "PCR-PLATTE": "PCR PLATE",
    "Richtung, in der der Cursor/Scanner durch die Wells springt":
        "Direction the cursor/scanner jumps through the wells",
    "Quellplatte-ID": "Source plate ID",
    "= Barcode der Eluat-Platte": "= barcode of the eluate plate",
    "Barcode der Eluat-/Output-Platte (MP96) – beim XML-Import automatisch.":
        "Barcode of the eluate/output plate (MP96) – automatic on XML import.",
    "Plattenbezeichnung": "Plate label",
    "z. B. Auftrag (MP96)": "e.g. order (MP96)",
    "📥  Vorlage": "📥  Template",
    "📥 Vorlage": "📥 Template",
    "CSV-Vorlage für die Proben-Platte speichern (Format wie MagNA Pure 96)":
        "Save a CSV template for the sample plate (format like MagNA Pure 96)",
    "💾  PDF": "💾  PDF",
    "Proben-Platte (96er-Raster) + alle MP96-Details als PDF speichern":
        "Save the sample plate (96 grid) + all MP96 details as PDF",
    "📂  Import": "📂  Import",
    "MagNA Pure 96 Export einlesen (XML mit Barcodes – oder CSV)":
        "Read a MagNA Pure 96 export (XML with barcodes – or CSV)",
    "MagNA Pure 96/24 Export einlesen (XML mit Barcodes – oder CSV)":
        "Read a MagNA Pure 96/24 export (XML with barcodes – or CSV)",
    "MagNA-Pure-Export importieren": "Import MagNA Pure export",
    "↶  Zurück": "↶  Undo",
    "Letzte große Aktion (Importieren / Einfügen / Leeren) zurücknehmen":
        "Undo the last big action (import / paste / clear)",
    "🗑  Proben leeren": "🗑  Clear samples",
    "Alle Proben aus der Platte entfernen": "Remove all samples from the plate",
    "Auswahl: keine → alle Proben werden verwendet":
        "Selection: none → all samples are used",
    "Auswahl: {count} Well(s) → nur diese werden verwendet":
        "Selection: {count} well(s) → only these are used",
    "⬇  Plattenbelegung ausführen": "⬇  Run plate setup",
    "Startwell: A1   (leeres PCR-Well klicken)":
        "Start well: A1   (click an empty PCR well)",
    "Startwell: {well} ✓   (Belegung beginnt genau hier)":
        "Start well: {well} ✓   (setup starts exactly here)",
    "schließt an belegte Wells an   ·   leeres PCR-Well = genauer Start":
        "continues after the filled wells   ·   empty PCR well = exact start",
    "Startwell: {well}   (leeres PCR-Well klicken)":
        "Start well: {well}   (click an empty PCR well)",
    "Letzte Plattenbelegung rückgängig machen": "Undo the last plate setup",
    "🗑  PCR leeren": "🗑  Clear PCR",
    "Nur 384: Quadrant AN = 4×96-Stempel (96-Kanal-Pipette); AUS = fortlaufend A1…P24":
        "384 only: quadrant ON = 4×96 stamp (96-channel pipette); OFF = continuous A1…P24",
    "Reihenfolge der vier Quadranten: im / gegen den Uhrzeigersinn":
        "Order of the four quadrants: clockwise / counter-clockwise",
    "Anordnung auf der PCR-Platte (spalten-/zeilenweise)":
        "Arrangement on the PCR plate (by column / by row)",
    "spaltenweise ↓ (A1→B1)": "by column ↓ (A1→B1)",
    "zeilenweise → (A1→A2)": "by row → (A1→A2)",
    "Eingabe-Richtung: {d}": "Input direction: {d}",
    "spaltenweise ↓": "by column ↓",
    "zeilenweise →": "by row →",
    "Anordnung auf der PCR-Platte (Klick schaltet um):\n"
    "spaltenweise ↓ = A1→B1→C1 …   ·   zeilenweise → = A1→A2→A3 …":
        "Arrangement on the PCR plate (click toggles):\n"
        "by column ↓ = A1→B1→C1 …   ·   by row → = A1→A2→A3 …",
    "Quadrant: AN": "Quadrant: ON",
    "Quadrant: AUS": "Quadrant: OFF",
    "⟳ im Uhrzeiger": "⟳ clockwise",
    "⟲ gegen Uhrzeiger": "⟲ counter-clockwise",
    "🖨  Drucken": "🖨  Print",
    "Pipettierschema öffnen und drucken": "Open and print the pipetting scheme",
    "Pipettierschema als PDF speichern": "Save the pipetting scheme as PDF",
    "📤  Setup PRO": "📤  Setup PRO",
    "Plate-Setup-CSV für den LightCycler PRO speichern":
        "Save the plate-setup CSV for the LightCycler PRO",
    "📤  Setup": "📤  Setup",
    "Plate-Setup für das Zielgerät exportieren (LightCycler PRO oder 480)":
        "Export the plate setup for the target cycler (LightCycler PRO or 480)",
    "📤  Setup LC": "📤  Setup LC",
    "Plattenbelegung fürs Zielgerät exportieren – Dateityp im Speichern-Dialog wählen (LightCycler PRO, 480 oder 96)":
        "Export the plate setup for the target cycler – choose the file type in the save dialog (LightCycler PRO, 480 or 96)",
    "Plattenbelegung exportieren": "Export plate setup",
    "Plate-Setup für LightCycler PRO (*.csv)": "Plate setup for LightCycler PRO (*.csv)",
    "Plattenbelegung für LightCycler 480 (*.txt)": "Plate setup for LightCycler 480 (*.txt)",
    "Plattenbelegung für LightCycler 480 mit Assay-Suffix (*.txt)":
        "Plate setup for LightCycler 480 with assay suffix (*.txt)",
    "LightCycler PRO  (Plate-Setup-CSV)": "LightCycler PRO  (plate-setup CSV)",
    "LightCycler 480  (Sample Editor, Tab-Text)":
        "LightCycler 480  (Sample Editor, tab-text)",
    "Sample-Editor-Datei (LightCycler 480) speichern":
        "Save Sample Editor file (LightCycler 480)",
    "Textdateien (*.txt)": "Text files (*.txt)",
    "Die LightCycler-480-Datei konnte nicht gespeichert werden. Bitte einen "
    "beschreibbaren Ordner wählen (z. B. Dokumente/Desktop) und die Datei "
    "ggf. zuerst schließen.":
        "The LightCycler 480 file could not be saved. Please choose a writable "
        "folder (e.g. Documents/Desktop) and close the file first if necessary.",
    "LightCycler-480-Datei gespeichert:\n{path}":
        "LightCycler 480 file saved:\n{path}",
    "Plattenbelegung für LightCycler 96 (*.txt)": "Plate setup for LightCycler 96 (*.txt)",
    "Die LightCycler-96-Datei konnte nicht gespeichert werden. Bitte einen "
    "beschreibbaren Ordner wählen (z. B. Dokumente/Desktop) und die Datei "
    "ggf. zuerst schließen.":
        "The LightCycler 96 file could not be saved. Please choose a writable "
        "folder (e.g. Documents/Desktop) and close the file first if necessary.",
    "LightCycler-96-Datei gespeichert:\n{path}":
        "LightCycler 96 file saved:\n{path}",
    "Nur 96-Well": "96-well only",
    "Der LightCycler 96 ist ein 96-Well-Gerät. Für den Export zum "
    "LightCycler 96 bitte eine 96er-Platte verwenden (LightCycler PRO "
    "und 480 unterstützen auch 384).":
        "The LightCycler 96 is a 96-well instrument. To export for the "
        "LightCycler 96 please use a 96-well plate (LightCycler PRO and 480 "
        "also support 384).",
    # ── Kontroll-Namen (LCAP) + Assay-Import aus LC-PRO-Lauf ──
    "Name:": "Name:",
    "keine": "none",
    "Assay wählen": "Choose assay",
    "Kein Assay gefunden": "No assay found",
    "Import fehlgeschlagen": "Import failed",
    "Ungültiger Kontroll-Name": "Invalid control name",
    "Falsches Plattenformat": "Wrong plate format",
    "Dieser Lauf ist ein {run}-Well-Lauf, der Assay ist aber im "
    "{cur}-Well-Format. LCAPs sind format-spezifisch (96 ≠ 384). Bitte "
    "einen {cur}-Well-Lauf wählen – oder den Assay im {run}-Well-Reiter "
    "neu anlegen.":
        "This run is a {run}-well run, but the assay is in {cur}-well format. "
        "LCAPs are format-specific (96 ≠ 384). Please choose a {cur}-well run – "
        "or create the assay in the {run}-well tab.",
    "Alle Dateien (*)": "All files (*)",
    "LC-PRO Customer Export (*.zip *.xml)": "LC-PRO Customer Export (*.zip *.xml)",
    "LightCycler-PRO-Lauf wählen": "Choose LightCycler PRO run",
    "📥 Aus LightCycler-PRO-Lauf einlesen…": "📥 Read from LightCycler PRO run…",
    "Targets im Lauf: {t}": "Targets in the run: {t}",
    "{role} = „{name}“": "{role} = “{name}”",
    "Die Datei konnte nicht gelesen werden:\n{e}": "The file could not be read:\n{e}",
    "Dieser Lauf enthält mehrere Assays – welchen übernehmen?":
        "This run contains several assays – which one to import?",
    "In dieser Datei wurde keine Assay-Definition gefunden. Bitte einen "
    "LightCycler-PRO-Lauf (Customer Export) wählen.":
        "No assay definition was found in this file. Please choose a "
        "LightCycler PRO run (Customer Export).",
    "Der Kontroll-Name „{name}“ ({role}) enthält unzulässige Zeichen: {chars}":
        "The control name “{name}” ({role}) contains invalid characters: {chars}",
    "Welche Kontrollen der Assay mitführt. Der Kontroll-Name rechts muss dem "
    "Analysis Package (LCAP) auf dem LightCycler PRO 100 % entsprechen (z. B. "
    "„PosK“) – sonst erkennt der PRO die Kontrolle nicht. Leer = Rollen-Code.":
        "Which controls the assay carries. The control name on the right must match "
        "the Analysis Package (LCAP) on the LightCycler PRO 100 % (e.g. “PosK”) – "
        "otherwise the PRO won't recognise the control. Empty = role code.",
    "Name dieser Kontrolle EXAKT wie im LCAP auf dem LightCycler PRO "
    "(z. B. „PosK“). Leer = Rollen-Code „{role}“.":
        "Name of this control EXACTLY as in the LCAP on the LightCycler PRO "
        "(e.g. “PosK”). Empty = role code “{role}”.",
    "Assay-Name und Kontroll-Namen aus einem echten LightCycler-PRO-Lauf "
    "(Customer Export, ZIP oder XML) übernehmen – exakt so, wie sie im LCAP "
    "definiert sind. Danach nur noch Volumina und Farbe ergänzen.":
        "Take the assay name and control names from a real LightCycler PRO run "
        "(Customer Export, ZIP or XML) – exactly as defined in the LCAP. Then just "
        "add volumes and colour.",
    "Assay „{name}“ übernommen.\nKontrollen: {ctrls}\nPCR-Profil: {prof}{tinfo}"
    "\n\nBitte noch Volumina und Farbe prüfen/ergänzen, dann speichern.":
        "Assay “{name}” imported.\nControls: {ctrls}\nPCR profile: {prof}{tinfo}"
        "\n\nPlease still check/complete volumes and colour, then save.",
    # ── Kontroll-Editor (mehrere Kontrollen je Typ) ──
    "Kontrollen des Assays. Name = controlName im LCAP (z. B. „PosK“); je "
    "Kontrolltyp ist eine pro Target erlaubt (mehrere gleichen Typs möglich). "
    "Leerer Name = Rollen-Code. Well nur bei „Feste Positionen“.":
        "Controls of the assay. Name = controlName in the LCAP (e.g. “PosK”); one "
        "per control type per target is allowed (several of the same type possible). "
        "Empty name = role code. Well only for “Fixed positions”.",
    "Name wie im LCAP (z. B. PosK)": "Name as in the LCAP (e.g. PosK)",
    "PTC/PPC = Positiv-, NTC/NPC = Negativkontrolle.":
        "PTC/PPC = positive, NTC/NPC = negative control.",
    "Name dieser Kontrolle EXAKT wie im LCAP auf dem LightCycler PRO "
    "(z. B. „PosK“). Leer = Rollen-Code.":
        "Name of this control EXACTLY as in the LCAP on the LightCycler PRO "
        "(e.g. “PosK”). Empty = role code.",
    "Well": "Well",
    "Nur bei „Feste Positionen“: Well dieser Kontrolle (z. B. A1).":
        "Only for “Fixed positions”: well of this control (e.g. A1).",
    "Für feste Positionen mindestens eine Kontrolle anlegen.":
        "At least one control is required for fixed positions.",
    # ── Ein Profil je Platte (LightCycler PRO: eine Platte = ein Thermoprofil) ──
    "Verschiedene PCR-Profile": "Different PCR profiles",
    "Auf eine Platte gehört nur EIN PCR-Profil (eine Platte = ein "
    "Thermoprofil). Hier träfen mehrere zusammen: {profiles}. Bitte nur "
    "Assays mit demselben PCR-Profil gemeinsam belegen.":
        "A plate may carry only ONE PCR profile (one plate = one thermal "
        "profile). Several would meet here: {profiles}. Please only place "
        "assays with the same PCR profile together.",
    # Dialoge / Meldungen Hauptfenster
    "Belegung verwerfen?": "Discard setup?",
    "Beim Wechsel wird die aktuelle PCR-Belegung geleert. Fortfahren?":
        "Switching clears the current PCR setup. Continue?",
    "Ziel:\n{path}\n\n": "Target:\n{path}\n\n",
    "Grund:\n{name}: {err}": "Reason:\n{name}: {err}",
    "Teilweise eingefügt": "Partly pasted",
    "{count} Probe(n) eingefügt. {overflow} Wert(e) passten nicht mehr auf "
    "die 96er-Platte und wurden ignoriert.":
        "{count} sample(s) pasted. {overflow} value(s) no longer fit on the 96 plate "
        "and were ignored.",
    "leeres Feld – als Startpunkt gewählt": "empty field – chosen as start point",
    "Probe": "Sample",
    "Assay": "Assay",
    "Rolle": "Role",
    "Proben-Well": "Sample well",
    "Feld gelöscht": "Field deleted",
    "Kein Assay": "No assay",
    "Bitte links mindestens einen Assay anhaken, bevor Sie die Plattenbelegung ausführen.":
        "Please tick at least one assay on the left before running the plate setup.",
    "Platte voll": "Plate full",
    "Alle vier Quadranten sind belegt. Bitte „PCR leeren“ oder eine neue Sitzung.":
        "All four quadrants are occupied. Please “Clear PCR” or start a new session.",
    "Zu viele Assays": "Too many assays",
    "Es sind noch {free} Quadrant(en) frei, aber {n} Assays aktiv. "
    "Bitte Assays reduzieren oder eine neue Platte beginnen.":
        "{free} quadrant(s) still free, but {n} assays active. "
        "Please reduce assays or start a new plate.",
    "Nichts zu belegen": "Nothing to set up",
    "Keine Proben ausgewählt. Bitte Proben markieren oder die Auswahl aufheben.":
        "No samples selected. Please select samples or clear the selection.",
    "Keine Proben": "No samples",
    "Bitte zuerst Proben in die Probenplatte eintragen.":
        "Please enter samples in the sample plate first.",
    "Probennamen zu kurz": "Sample names too short",
    "   •  Probenplatte {w}: „{n}“   (1 Zeichen)":
        "   •  sample plate {w}: “{n}”   (1 character)",
    "Der LightCycler PRO benötigt je Probe mindestens {min} Zeichen. "
    "Folgende Proben sind zu kurz und würden vom Gerät nicht übernommen:\n\n{shown}\n\n"
    "Trotzdem fortfahren?":
        "The LightCycler PRO requires at least {min} characters per sample. "
        "The following samples are too short and would be rejected by the device:\n\n{shown}\n\n"
        "Continue anyway?",
    "   •  Probenplatte {w}: „{n}“   → {bad}":
        "   •  sample plate {w}: “{n}”   → {bad}",
    "Unzulässige Zeichen im Probennamen": "Invalid characters in sample name",
    "Der LightCycler PRO akzeptiert bestimmte Zeichen nicht "
    "(^ ~ \\ & | \" , ;). Folgende Proben sind betroffen:\n\n"
    "{shown}\n\nTrotzdem fortfahren?":
        "The LightCycler PRO does not accept certain characters "
        "(^ ~ \\ & | \" , ;). The following samples are affected:\n\n"
        "{shown}\n\nContinue anyway?",
    "Belegung nicht möglich": "Setup not possible",
    "Es konnten keine Wells belegt werden.": "No wells could be filled.",
    "{n} Well(s) waren bereits belegt und wurden übersprungen.":
        "{n} well(s) were already occupied and were skipped.",
    "Belegung mit Hinweisen": "Setup with notes",
    "Nichts rückgängig": "Nothing to undo",
    "Es wurde noch keine Belegung ausgeführt.": "No setup has been run yet.",
    "PCR-Platte leeren?": "Clear PCR plate?",
    "Alle Belegungen verwerfen und die PCR-Platte komplett leeren?":
        "Discard all setups and clear the PCR plate completely?",
    "Vorlage": "Template",
    "Die Vorlagedatei wurde nicht gefunden.": "The template file was not found.",
    "Probenplatte-Vorlage speichern": "Save sample-plate template",
    "CSV-Dateien (*.csv)": "CSV files (*.csv)",
    "Fehler": "Error",
    "Vorlage konnte nicht gespeichert werden:\n{e}":
        "Template could not be saved:\n{e}",
    "Vorlage gespeichert": "Template saved",
    "Die Vorlage wurde gespeichert:\n{path}\n\n"
    "Spalten ausfüllen und anschließend über „Importieren…“ einlesen.":
        "The template was saved:\n{path}\n\n"
        "Fill in the columns and then read it back via “Import…”.",
    "MP96-Export importieren": "Import MP96 export",
    "MP96-Export (*.xml *.csv);;XML mit Barcodes (*.xml);;CSV (*.csv)":
        "MP96 export (*.xml *.csv);;XML with barcodes (*.xml);;CSV (*.csv)",
    "Import-Fehler": "Import error",
    "Import": "Import",
    "Keine Proben gefunden.": "No samples found.",
    "{n} Proben importiert.": "{n} samples imported.",
    "\nQuellplatte-ID: {sid} · Bezeichnung: {oid}":
        "\nSource plate ID: {sid} · label: {oid}",
    "\n\nHinweise:\n{w}": "\n\nNotes:\n{w}",
    "Proben-Platte leer": "Sample plate empty",
    "Bitte zuerst Proben laden oder eintragen.":
        "Please load or enter samples first.",
    "Proben-Platte als PDF": "Sample plate as PDF",
    "PDF-Dateien (*.pdf)": "PDF files (*.pdf)",
    "Speichern fehlgeschlagen": "Save failed",
    "Das Proben-Platte-PDF konnte nicht gespeichert werden. Bitte einen "
    "beschreibbaren Ordner wählen (z. B. Dokumente/Desktop) und die Datei "
    "ggf. zuerst schließen.":
        "The sample-plate PDF could not be saved. Please choose a writable folder "
        "(e.g. Documents/Desktop) and close the file first if necessary.",
    "Exportiert": "Exported",
    "Proben-Platte gespeichert:\n{path}": "Sample plate saved:\n{path}",
    "Auswahl leeren?": "Clear selection?",
    "Nur die {n} markierten Wells leeren?": "Clear only the {n} selected wells?",
    "Proben-Platte leeren?": "Clear sample plate?",
    "Alle Proben auf der Proben-Platte löschen?":
        "Delete all samples on the sample plate?",
    "Keine Proben-Platte-Aktion zum Zurücknehmen (Importieren / Einfügen / Leeren).":
        "No sample-plate action to undo (import / paste / clear).",
    "Kein Inhalt": "Nothing to export",
    "Die PCR-Platte ist leer. Bitte zuerst die Belegung ausführen.":
        "The PCR plate is empty. Please run the setup first.",
    "Probennamen werden gekürzt": "Sample names will be truncated",
    "   •  {loc}{n}   ({len} Zeichen)": "   •  {loc}{n}   ({len} characters)",
    "Probenplatte {sw}: ": "sample plate {sw}: ",
    "Der LightCycler PRO kann je Probe höchstens {max} Zeichen "
    "speichern. Für den Export der folgenden Proben werden nur die ersten "
    "{max} Zeichen verwendet:\n\n{shown}\n\nExport trotzdem fortsetzen?":
        "The LightCycler PRO can store at most {max} characters per sample. "
        "For the export of the following samples only the first {max} characters "
        "are used:\n\n{shown}\n\nContinue the export anyway?",
    "Plate-ID „{id}“  →  {bad}": "Plate ID “{id}”  →  {bad}",
    "Plattenname „{name}“  →  {bad}": "Plate name “{name}”  →  {bad}",
    "Unzulässige Zeichen": "Invalid characters",
    "Folgende Felder enthalten Zeichen, die der LightCycler PRO nicht "
    "akzeptiert:\n\n   •  {problems}\n\nExport trotzdem fortsetzen?":
        "The following fields contain characters the LightCycler PRO does not "
        "accept:\n\n   •  {problems}\n\nContinue the export anyway?",
    "Plate-Setup LC PRO speichern": "Save plate setup (LC PRO)",
    "Das Plate-Setup (CSV) konnte nicht gespeichert werden.\n\n"
    "Bitte einen Ordner wählen, in den Sie schreiben dürfen (z.B. "
    "„Dokumente“ oder „Desktop“). Falls die Datei bereits geöffnet "
    "ist, bitte zuerst schließen.":
        "The plate setup (CSV) could not be saved.\n\n"
        "Please choose a folder you can write to (e.g. “Documents” or “Desktop”). "
        "If the file is already open, please close it first.",
    "Plate-Setup gespeichert:\n{path}": "Plate setup saved:\n{path}",
    "Pipettierschema speichern": "Save pipetting scheme",
    "Das Pipettierschema-PDF konnte nicht gespeichert werden.\n\n"
    "Bitte einen Ordner wählen, in den Sie schreiben dürfen (z.B. "
    "„Dokumente“ oder „Desktop“) – nicht „Programme“ oder ein "
    "schreibgeschütztes Laufwerk. Falls die PDF-Datei bereits "
    "geöffnet ist, bitte zuerst schließen.":
        "The pipetting-scheme PDF could not be saved.\n\n"
        "Please choose a folder you can write to (e.g. “Documents” or “Desktop”) – "
        "not “Program Files” or a read-only drive. If the PDF is already open, "
        "please close it first.",
    "Pipettierschema gespeichert:\n{path}": "Pipetting scheme saved:\n{path}",
    "Fehler beim Erstellen": "Error while creating",
    "Das Pipettierschema-PDF konnte nicht erstellt werden.":
        "The pipetting-scheme PDF could not be created.",
    "Öffnen nicht möglich": "Cannot open",
    "Das PDF wurde erstellt, konnte aber nicht automatisch "
    "geöffnet/gedruckt werden (evtl. ist kein PDF-Betrachter "
    "installiert). Sie können es manuell öffnen:":
        "The PDF was created but could not be opened/printed automatically "
        "(perhaps no PDF viewer is installed). You can open it manually:",
    "Neue Plattenbelegung?": "New plate setup?",
    "Alle aktuellen Eingaben (Proben, Assays, PCR-Platte) verwerfen?":
        "Discard all current input (samples, assays, PCR plate)?",
    "Plattenbelegung speichern": "Save plate setup",
    "WellDone-Dateien (*.wds);;Alle Dateien (*)":
        "WellDone files (*.wds);;All files (*)",
    "Gespeichert": "Saved",
    "Plattenbelegung gespeichert:\n{path}": "Plate setup saved:\n{path}",
    "Plattenbelegung laden": "Load plate setup",
    "Ladefehler": "Load error",
    "Plattenbelegung geladen:\n{path}": "Plate setup loaded:\n{path}",
    "\n\nHinweis: Einige Assays existieren nicht mehr und wurden übersprungen.":
        "\n\nNote: some assays no longer exist and were skipped.",
    "Geladen": "Loaded",

    # ── Plattenbelegung-Panel (ui/plate_info_panel.py) ─────────────────────
    "PLATTENBELEGUNG": "PLATE SETUP",
    "Hilfe · Über · Feedback · Handbuch": "Help · About · Feedback · Manual",
    "Plattenname / Session": "Plate name / session",
    "autom.: JJMMTT_Assays": "auto: YYMMDD_Assays",
    "Plate-ID (optional)": "Plate ID (optional)",
    "= Barcode der PCR-Platte": "= barcode of the PCR plate",
    "Optional. Entspricht dem Barcode der PCR-Platte (z. B. B654321).":
        "Optional. Matches the barcode of the PCR plate (e.g. B654321).",
    "Kommentar": "Comment",
    "Bearbeiter, Lot-MasterMix, …": "Operator, MasterMix lot, …",
    "WORKFLOW": "WORKFLOW",
    "1. Proben eingeben / importieren": "1. Enter / import samples",
    "2. Assays auswählen": "2. Select assays",
    "3. Plattenbelegung ausführen": "3. Run plate setup",
    "4. Pipettierschema gespeichert/gedruckt": "4. Pipetting scheme saved/printed",
    "5. Plate-Setup (LC PRO) exportiert": "5. Plate setup (LC PRO) exported",
    "6. Plattenbelegung/Session speichern": "6. Save plate setup/session",
    "✔ WellDone!": "✔ WellDone!",
    "✨ Neu": "✨ New",
    "📂 Laden": "📂 Load",
    "💾 Speichern": "💾 Save",
    "Unzulässige Zeichen: {chars} — vom LightCycler PRO nicht akzeptiert.":
        "Invalid characters: {chars} — not accepted by the LightCycler PRO.",

    # ── Essays-Übersicht (ui/summary_panel.py) ─────────────────────────────
    "ASSAYS AUF PCR-PLATTE": "ASSAYS ON PCR PLATE",
    "— PCR-Platte leer —": "— PCR plate empty —",
    "{n} Proben": "{n} samples",
    "{n} Kontrollen": "{n} controls",
    "Standard": "Standard",                 # qPCR-Fachbegriff – im Englischen identisch
    "Standards": "Standards",
    "MasterMix": "MasterMix",               # Reagenz-/Produktname – bleibt gleich
    ",<br>{vol} µl MasterMix": ",<br>{vol} µl MasterMix",
    "Kontrolle:": "Controls:",

    # ── Feld-Detail (ui/detail_panel.py) ───────────────────────────────────
    "Feld-Detail (Probe)": "Field detail (sample)",
    "Feld-Detail (PCR)": "Field detail (PCR)",
    "Feld-Detail": "Field detail",
    "leeres Feld": "empty field",
    "Umschalt+Enter = neue Zeile": "Shift+Enter = new line",
    "Name": "Name",
    "Note": "Note",
    "Sample-ID": "Sample ID",
    "⚠ Name zu kurz – mindestens {min} Zeichen":
        "⚠ Name too short – at least {min} characters",
    "⚠ Unzulässige Zeichen: {chars}": "⚠ Invalid characters: {chars}",
    "Status: {state}": "Status: {state}",
    "bereits belegt": "already used",
    "verfügbar": "available",
    "Prep-Notes": "Prep notes",
    "🗑  Dieses Feld löschen": "🗑  Delete this field",

    # ── Assay-Panel (ui/assay_panel.py) ────────────────────────────────────
    "ASSAYS": "ASSAYS",
    "96-Well": "96-well",
    "384-Well": "384-well",
    "Zentrale Assay-Bibliothek: aus Netzwerk-Vorlage laden oder lokale "
    "Bibliothek als Vorlage speichern":
        "Central assay library: load from a network template or save the local "
        "library as a template",
    "Reihenfolge: ausgewählten Assay nach oben": "Order: move selected assay up",
    "Reihenfolge: ausgewählten Assay nach unten": "Order: move selected assay down",
    "⧉ Kopieren": "⧉ Copy",
    "Den ausgewählten Assay duplizieren": "Duplicate the selected assay",
    "+ Neu": "+ New",
    "✕ Löschen": "✕ Delete",
    "✏ Bearbeiten": "✏ Edit",
    "Kontrollen:  {ctrl}{suffix}": "Controls:  {ctrl}{suffix}",
    "  (feste Pos.)": "  (fixed pos.)",
    "  (Neg→Pos)": "  (neg→pos)",
    "MasterMix {mm} µl + Template {tmpl} µl":
        "MasterMix {mm} µl + template {tmpl} µl",
    "Hinweis": "Note",
    "Bitte zuerst einen Assay anklicken.": "Please click an assay first.",
    "Inkompatibles PCR-Profil": "Incompatible PCR profile",
    'Assay "{name}" verwendet Profil "{profile}".\n'
    'Aktuell aktive Assays verwenden Profil "{ref}".\n\n'
    "Nur Assays mit demselben PCR-Profil können gleichzeitig laufen.":
        'Assay "{name}" uses profile "{profile}".\n'
        'Currently active assays use profile "{ref}".\n\n'
        "Only assays with the same PCR profile can run at the same time.",
    "Unterschiedliche Kontroll-Platzierung": "Different control placement",
    'Assay "{name}" nutzt die Kontroll-Platzierung „{layout}".\n'
    'Aktuell aktive Assays nutzen „{ref}".\n\n'
    "Gleichzeitig aktive Assays müssen dieselbe Kontroll-Platzierung verwenden.":
        'Assay "{name}" uses control placement “{layout}”.\n'
        'Currently active assays use “{ref}”.\n\n'
        "Assays active at the same time must use the same control placement.",
    "Feste Positionen kollidieren": "Fixed positions collide",
    'Assay "{name}" nutzt feste Kontroll-Well(s) {wells}, die bereits von '
    'einem aktiven Assay belegt sind.\n\n'
    "Feste Kontroll-Positionen müssen sich zwischen gleichzeitig aktiven "
    "Assays unterscheiden.":
        'Assay "{name}" uses fixed control well(s) {wells} that are already used '
        'by an active assay.\n\n'
        "Fixed control positions must differ between assays active at the same time.",
    "Bibliothek aktualisiert": "Library updated",
    "Die Assay-Bibliothek wurde aus der Vorlage übernommen. Die aktive "
    "Auswahl wurde zurückgesetzt — bitte die Assays für den Lauf neu wählen.":
        "The assay library was loaded from the template. The active selection was "
        "reset — please choose the assays for the run again.",
    "Löschen bestätigen": "Confirm deletion",
    'Assay "{name}" wirklich löschen?': 'Really delete assay "{name}"?',

    # ── Layout-Optionen (models/assay.py LAYOUT_LABELS + Dialog-Combo) ─────
    "Positiv → Proben → Negativ": "Positive → samples → negative",
    "Negativ → Proben → Positiv": "Negative → samples → positive",
    "Proben → Positiv → Negativ": "Samples → positive → negative",
    "Proben → Negativ → Positiv": "Samples → negative → positive",
    "Feste Positionen": "Fixed positions",
    "Positiv → Proben → Negativ (Standard)": "Positive → samples → negative (default)",
    "Feste Positionen (Kontrollen am Rand)": "Fixed positions (controls at the edge)",

    # ── Assay-Dialog (ui/assay_dialog.py) ──────────────────────────────────
    "Farbe wählen…": "Choose colour…",
    "Farbe wählen": "Choose colour",
    "Assay bearbeiten": "Edit assay",
    "Neuen Assay hinzufügen": "Add new assay",
    "{fmt}-Well": "{fmt}-well",
    "Plattenformat dieses Assays (LCAPs sind für 96 und 384 verschieden). "
    "Wird über den Reiter in der Assay-Liste festgelegt.":
        "Plate format of this assay (LCAPs differ for 96 and 384). "
        "Set via the tab in the assay list.",
    "Format:": "Format:",
    "z.B. 3 EnteroBocAde2": "e.g. 3 EnteroBocAde2",
    "Max. {n} Zeichen — so bleibt das PCR-Profil in der Liste sichtbar.":
        "Max. {n} characters — keeps the PCR profile visible in the list.",
    "Anzeigename:*": "Display name:*",
    "Der Assay-/AP-Name, wie er auf dem LightCycler PRO installiert ist "
    "(Analysis Package / .lcap). Muss exakt übereinstimmen — Zeichen, "
    "Leerzeichen und Bindestriche identisch (Groß-/Kleinschreibung egal).":
        "The assay/AP name as installed on the LightCycler PRO (Analysis Package "
        "/ .lcap). Must match exactly — characters, spaces and hyphens identical "
        "(case-insensitive).",
    "LCAP-Name (Import):*": "LCAP name (import):*",
    "z.B. LMM_7plex_96": "e.g. LMM_7plex_96",
    "Das Run-Profil, wie es auf dem LightCycler PRO hinterlegt ist. "
    "Muss 100 % identisch eingegeben werden — inkl. Groß-/Kleinschreibung "
    "und Leerzeichen.":
        "The run profile as stored on the LightCycler PRO. Must be entered 100% "
        "identically — including case and spaces.",
    "\n\nAktive Profile: {profiles}": "\n\nActive profiles: {profiles}",
    "PCR-Profil:*": "PCR profile:*",
    "Farbe:": "Colour:",
    "Welche Kontrollen der Assay mitführt. Die Kontroll-Namen (PTC/NTC/PPC/NPC) "
    "müssen im Analysis Package auf dem LightCycler PRO definiert sein und "
    "dort 100 % identisch heißen.":
        "Which controls the assay carries. The control names (PTC/NTC/PPC/NPC) must "
        "be defined in the Analysis Package on the LightCycler PRO and named 100% "
        "identically there.",
    "PTC (Positiv-Kontrolle)": "PTC (positive control)",
    "NTC (Negativ-Kontrolle)": "NTC (negative control)",
    "PPC (Positiv-Prozesskontrolle)": "PPC (positive process control)",
    "NPC (Negativ-Prozesskontrolle)": "NPC (negative process control)",
    "Kontrollen:": "Controls:",
    "Wie die Kontrollen auf der Platte liegen:\n"
    "• Positiv/Negativ → Proben → …: Kontrollen vorn und hinten.\n"
    "• Proben → Positiv → Negativ: erst die Proben, Kontrollen ans Ende "
    "(z. B. fürs Quadranten-Stempeln auf 384).\n"
    "• Feste Positionen: jede Kontrolle in einem festen Well.":
        "How the controls sit on the plate:\n"
        "• Positive/Negative → samples → …: controls at front and back.\n"
        "• Samples → Positive → Negative: samples first, controls at the end "
        "(e.g. for quadrant stamping on 384).\n"
        "• Fixed positions: each control in a fixed well.",
    "Kontroll-Platzierung:": "Control placement:",
    "Well je aktiver Kontrolle eintragen (z. B. A1, H12 – bei 384 bis P24):":
        "Enter a well for each active control (e.g. A1, H12 – up to P24 on 384):",
    "z. B. A1": "e.g. A1",
    "Optional – nur bei abs. Quantifizierung / MCGT mit externer Standardkurve: "
    "Referenzstandard (RS) bzw. Schmelzstandard (MS) je Target. Name = Standard-/"
    "Genotypname genau wie im LCAP. Jeder Standard belegt ein Well.":
        "Optional – only for absolute quantification / MCGT with an external "
        "standard curve: reference standard (RS) or melting standard (MS) per "
        "target. Name = standard/genotype name exactly as in the LCAP. Each "
        "standard takes one well.",
    "+ Standard": "+ Standard",
    "Standards:": "Standards:",
    "RS = Referenzstandard (Quantifizierung), MS = Schmelzstandard (MCGT)":
        "RS = reference standard (quantification), MS = melting standard (MCGT)",
    "Name (wie im LCAP)": "Name (as in the LCAP)",
    "Target (z. B. EGFR)": "Target (e.g. EGFR)",
    "Notiz (z. B. 1e5 cp/mL)": "Note (e.g. 1e5 cp/mL)",
    "Nur zur Doku auf dem Pipettierschema – kommt NICHT in die CSV.":
        "For documentation on the pipetting scheme only – does NOT go into the CSV.",
    "— Reaktionszusammensetzung (µl pro Reaktion) —":
        "— Reaction composition (µl per reaction) —",
    "Wasser (µl):": "Water (µl):",
    "Primer/Probes (µl):": "Primer/probes (µl):",
    "MasterMix (µl):": "MasterMix (µl):",
    "RT-Enzym (µl):": "RT enzyme (µl):",
    "Template/Probe (µl):": "Template/sample (µl):",
    "Reserve gegen Pipettierverlust (Standard 1,0; 0–10, Schritte 0,1).\n"
    "Erhöht NUR die berechneten Gesamtvolumina (Wasser, MasterMix …):\n"
    "Gesamt = Menge je Reaktion × (Proben + Kontrollen + Sicherheitsvolumen).":
        "Reserve against pipetting loss (default 1.0; 0–10, steps of 0.1).\n"
        "Increases ONLY the calculated total volumes (water, MasterMix …):\n"
        "Total = amount per reaction × (samples + controls + safety volume).",
    "Sicherheitsvolumen (Reserve-Rkt.):": "Safety volume (reserve rxns):",
    "Volumen:": "Volume:",
    "MasterMix <b>{mm} µl</b>  +  Template <b>{tmpl} µl</b>  =  Reaktion <b>{rxn} µl</b>":
        "MasterMix <b>{mm} µl</b>  +  template <b>{tmpl} µl</b>  =  reaction <b>{rxn} µl</b>",
    "Standard unvollständig": "Standard incomplete",
    "Jeder Standard braucht einen Namen UND einen Targetnamen "
    "(oder die Zeile ganz leer lassen).":
        "Each standard needs a name AND a target name (or leave the row empty).",
    "Pflichtfelder": "Required fields",
    "Bitte Anzeigename, LCAP-Name und PCR-Profil ausfüllen.":
        "Please fill in display name, LCAP name and PCR profile.",
    "Feste Positionen": "Fixed positions",
    "Für feste Positionen mindestens eine Kontrolle aktivieren.":
        "For fixed positions, enable at least one control.",
    "Bitte für {role} ein Well eintragen (z. B. A1).":
        "Please enter a well for {role} (e.g. A1).",
    "Ungültiges Well": "Invalid well",
    "{role}: „{w}“ ist kein gültiges Well für das {fmt}-Format (A1 … {last}).":
        "{role}: “{w}” is not a valid well for the {fmt} format (A1 … {last}).",
    "Jede Kontrolle braucht ein eigenes Well.": "Each control needs its own well.",

    # ── Einstellungen (ui/settings_dialog.py) ──────────────────────────────
    "Einstellungen": "Settings",
    "Template-Eingabe: Barcode-Scanner / Tastatur":
        "Template input: barcode scanner / keyboard",
    "Spaltenweise  (A1 → B1 → C1 → … → H1 → A2 …)":
        "By column  (A1 → B1 → C1 → … → H1 → A2 …)",
    "Zeilenweise   (A1 → A2 → A3 → … → A12 → B1 …)":
        "By row   (A1 → A2 → A3 → … → A12 → B1 …)",
    "Cursor springt:": "Cursor jumps:",
    "Mit 'Enter' (oder Scanner-Enter) springt der Cursor zum nächsten Well.":
        "With 'Enter' (or scanner Enter) the cursor jumps to the next well.",
    "PCR-Platte: Aufbau-Richtung": "PCR plate: layout direction",
    "Assay = Spalte  (PTC oben, Proben abwärts, NTC unten)":
        "Assay = column  (PTC top, samples down, NTC bottom)",
    "Assay = Zeile   (PTC links, Proben nach rechts, NTC rechts)":
        "Assay = row   (PTC left, samples to the right, NTC right)",
    "Belegung:": "Setup:",
    "Bestimmt, wie jeder Assay-Block auf der PCR-Platte angeordnet wird.":
        "Determines how each assay block is arranged on the PCR plate.",
    # Sprachauswahl (neu)
    "Sprache / Language": "Language",
    "Sprache:": "Language:",
    "Deutsch": "Deutsch",
    "Wird nach Neustart übernommen": "Applied after restart",

    # ── Template-Bibliothek (ui/template_library_dialog.py) ────────────────
    "Zentrale Assay-Bibliothek": "Central assay library",
    "Die lokale Assay-Bibliothek ist die Arbeitskopie. Über eine zentrale "
    "Vorlage auf einer Netzfreigabe lassen sich alle Rechner auf denselben "
    "Stand bringen.":
        "The local assay library is the working copy. A central template on a "
        "network share lets you bring all computers to the same state.",
    "Netzwerk-Vorlage": "Network template",
    "📥  Aus Netzwerk-Vorlage laden …": "📥  Load from network template …",
    "Die lokale Bibliothek durch die Vorlage ERSETZEN "
    "(vorher wird automatisch ein Backup angelegt).":
        "REPLACE the local library with the template (a backup is created first).",
    "💾  Lokale Bibliothek als Vorlage speichern …":
        "💾  Save local library as template …",
    "Die lokale Bibliothek an den Netz-Pfad schreiben "
    "(veröffentlicht den Master für die anderen Rechner).":
        "Write the local library to the network path (publishes the master for the "
        "other computers).",
    "Hinweis: „Laden“ ersetzt die lokale Bibliothek vollständig; rein lokale "
    "Assays gehen dabei verloren (liegen aber im automatischen Backup).":
        "Note: “Load” fully replaces the local library; purely local assays are "
        "lost (but kept in the automatic backup).",
    "Zuletzt verwendete Vorlage:\n{path}": "Last used template:\n{path}",
    "Noch keine Vorlage verwendet.": "No template used yet.",
    "Netzwerk-Vorlage wählen": "Choose network template",
    "Ungültige Vorlage": "Invalid template",
    "Die gewählte Datei ist keine gültige WellDone-Assay-Datenbank.":
        "The selected file is not a valid WellDone assay database.",
    "Bibliothek ersetzen?": "Replace library?",
    "Die lokale Assay-Bibliothek wird vollständig durch die Vorlage ersetzt.\n"
    "Vorher wird automatisch ein Backup angelegt.\n\nFortfahren?":
        "The local assay library will be fully replaced by the template.\n"
        "A backup is created first.\n\nContinue?",
    "Laden fehlgeschlagen:\n{e}": "Load failed:\n{e}",
    "Die Assay-Bibliothek wurde aus der Vorlage übernommen.":
        "The assay library was loaded from the template.",
    "\n\nBackup der vorherigen Bibliothek:\n{backup}":
        "\n\nBackup of the previous library:\n{backup}",
    "Übernommen": "Applied",
    "Als Netzwerk-Vorlage speichern": "Save as network template",
    "Als Vorlage speichern?": "Save as template?",
    "Die lokale Assay-Bibliothek wird als Vorlage gespeichert:\n{path}\n\nFortfahren?":
        "The local assay library will be saved as a template:\n{path}\n\nContinue?",
    "Speichern fehlgeschlagen:\n{e}": "Save failed:\n{e}",
    "Die lokale Bibliothek wurde als Netzwerk-Vorlage gespeichert.":
        "The local library was saved as a network template.",
    "Assay-Datenbank (*.db);;Alle Dateien (*.*)":
        "Assay database (*.db);;All files (*.*)",

    # ── Plattenraster-Widget (ui/plate_widget.py) ──────────────────────────
    "Ausschneiden": "Cut",
    "Kopieren": "Copy",
    "Einfügen": "Paste",
    "Alles auswählen": "Select all",
    "„{name}“ – Name zu kurz: mindestens {min} Zeichen nötig":
        "“{name}” – name too short: at least {min} characters required",
    "„{name}“ – unzulässige Zeichen: {chars}":
        "“{name}” – invalid characters: {chars}",
    "\nTemplate-Well: {well}": "\nTemplate well: {well}",
    "\nTarget: {target}": "\nTarget: {target}",
    "\nNotiz: {note}": "\nNote: {note}",
    "Well: {well}\nProbe: {sample}\nAssay: {assay}\nRolle: {role}{extra}":
        "Well: {well}\nSample: {sample}\nAssay: {assay}\nRole: {role}{extra}",

    # ── Belegungs-Logik (models/plate_layout.py) ───────────────────────────
    "Keine Assays ausgewählt.": "No assays selected.",
    "Keine Proben im Template eingetragen.": "No samples entered in the template.",
    "Belegung ab {well} nicht möglich: ab hier ist nicht genügend Platz "
    "auf der Platte. Bitte ein weiter oben/links liegendes Start-Well wählen.":
        "Setup from {well} not possible: there is not enough room on the plate "
        "from here. Please choose a start well further up/left.",
    "Belegung ab {well} nicht möglich: bereits belegte Wells im Weg "
    "({preview}). Bitte ein freies Start-Well mit genügend Platz wählen.":
        "Setup from {well} not possible: occupied wells in the way ({preview}). "
        "Please choose a free start well with enough room.",
    "PCR-Platte voll — nicht alle Proben passen. "
    "Bitte Proben aufteilen oder früheren Startpunkt wählen.":
        "PCR plate full — not all samples fit. Please split the samples or choose "
        "an earlier start point.",

    # ── Pipettierschema-PDF (utils/pdf_export.py) ──────────────────────────
    "Keine Assays auf der Platte.": "No assays on the plate.",
    "WellDone! — Pipettierschema": "WellDone! — Pipetting scheme",
    "Seite {p} von {total}": "Page {p} of {total}",
    "   |   Plate-ID: {id}": "   |   Plate ID: {id}",
    "Erstellt: {when}": "Created: {when}",
    "Quellplatte: {sp}": "Source plate: {sp}",
    "1. MasterMix ansetzen und je Well verteilen":
        "1. Prepare MasterMix and distribute to each well",
    "2. Proben verteilen (Quell-Koordinate je Well)":
        "2. Distribute samples (source coordinate per well)",
    "2. Proben verteilen (Template je Well separat zugeben)":
        "2. Distribute samples (add template separately to each well)",
    "Standards (RS/MS)": "Standards (RS/MS)",
    "3. Quellplatte (96) — Probenname je Well":
        "3. Source plate (96) — sample name per well",
    "Position auf der MP96-/Eluat-Platte = Quell-Well der Probe.":
        "Position on the MP96/eluate plate = source well of the sample.",
    "Komponente (µl)": "Component (µl)",
    "je 1 Rkt": "per 1 rxn",
    "gesamt ({n}×)": "total ({n}×)",
    "Wasser": "Water",
    "Primer/Probes": "Primer/probes",
    "RT-Enzym": "RT enzyme",
    "Summe MasterMix": "MasterMix sum",
    "+ Template/Probe": "+ template/sample",
    "= Reaktion gesamt": "= reaction total",
    "pro Well": "per well",
    " · Target: {target}": " · Target: {target}",
    "WellDone! — Proben-Platte (MP96)": "WellDone! — Sample plate (MP96)",
    "Proben (Position = Quell-Well der MP96-/Eluat-Platte)":
        "Samples (position = source well of the MP96/eluate plate)",
    "Lauf-Details": "Run details",
    "Auftrag (OrderID)": "Order (OrderID)",
    "Eluat-Platte (Output)": "Eluate plate (output)",
    "Quell-/Eingangsplatte": "Source/input plate",
    "Bearbeiter": "Operator",
    "Batch-ID": "Batch ID",
    "Status": "Status",
    "Gerät (SN)": "Instrument (SN)",
    "Kit": "Kit",
    "Protokoll": "Protocol",
    "Probenvolumen": "Sample volume",
    "Elutionsvolumen": "Elution volume",
    "Start": "Start",
    "Ende": "End",
    "Kommentar (Auftrag)": "Comment (order)",
    "Reagenz-/Lot-Barcodes": "Reagent/lot barcodes",
    "Flags": "Flags",
    "WellDone! — Proben-Platte": "WellDone! — Sample plate",

    # ── Import-Warnungen (utils/csv_import.py, xml_import.py) ───────────────
    "XML konnte nicht gelesen werden: {e}": "XML could not be read: {e}",
    "Well {well} kommt mehrfach vor — nur der erste Eintrag wird genutzt.":
        "Well {well} occurs more than once — only the first entry is used.",
    "CSV nicht erkannt. Es werden Spalten für Well/Position und "
    "Sample/Name benötigt.\nGefundene Spalten: {fields}":
        "CSV not recognised. Columns for well/position and sample/name are "
        "required.\nColumns found: {fields}",
    "Keine Proben in der Datei gefunden.": "No samples found in the file.",
    "Keine Proben (SampleData) in der XML-Datei gefunden.":
        "No samples (SampleData) found in the XML file.",
    "{n} Probe(n) mit weniger als {min} Zeichen — der "
    "LightCycler PRO benötigt mindestens {min} Zeichen: {sample}":
        "{n} sample(s) with fewer than {min} characters — the LightCycler PRO "
        "requires at least {min} characters: {sample}",
    "{n} Probe(n) mit weniger als {min} Zeichen: {sample}":
        "{n} sample(s) with fewer than {min} characters: {sample}",
    "{n} Probe(n) mit unzulässigen Zeichen — der LightCycler PRO "
    "akzeptiert keine der Zeichen ^ ~ \\ & | \" , ; : {sample}":
        "{n} sample(s) with invalid characters — the LightCycler PRO accepts "
        "none of the characters ^ ~ \\ & | \" , ; : {sample}",
    "{n} Probe(n) mit unzulässigen Zeichen: {sample}":
        "{n} sample(s) with invalid characters: {sample}",

    # ── MP96-Auftrag (ui/mp96_order_dialog.py + Knopf im Hauptfenster) ─────
    "📋  MP96-Auftrag…": "📋  MP96 order…",
    "Auftrag (XML) für den MagNA Pure 96 erstellen":
        "Create an order (XML) for the MagNA Pure 96",
    "MP96-Auftrag erstellen": "Create MP96 order",
    "Vorlage: (keine geladen)": "Template: (none loaded)",
    "📂  TemplateData.xml laden…": "📂  Load TemplateData.xml…",
    "Den Katalog (Kits, Tests, Volumina, Platten) aus der MP96-TemplateData.xml laden.":
        "Load the catalog (kits, tests, volumes, plates) from the MP96 TemplateData.xml.",
    "Kit:": "Kit:",
    "Test / Protokoll:": "Test / protocol:",
    "Probenvolumen (µl):": "Sample volume (µl):",
    "Elutionsvolumen (µl):": "Elution volume (µl):",
    "Interne Kontrolle:": "Internal control:",
    "Eingangsplatte:": "Input plate:",
    "Füllvolumen Eingangsplatte (µl):": "Input plate fill volume (µl):",
    "Zielplatte:": "Output plate:",
    "Auftragsname:": "Order name:",
    "Quellplatte-ID:": "Source plate ID:",
    "Kommentar:": "Comment:",
    "Bearbeiter:": "Operator:",
    "{n} Proben aus der Proben-Platte werden übernommen.":
        "{n} samples from the sample plate will be included.",
    "Auftrag erstellen…": "Create order…",
    "TemplateData.xml wählen": "Choose TemplateData.xml",
    "TemplateData-Dateien (*.xml)": "TemplateData files (*.xml)",
    "Vorlage konnte nicht gelesen werden:\n{e}": "Template could not be read:\n{e}",
    "Vorlage: {name}": "Template: {name}",
    "(geladen)": "(loaded)",
    "(keine)": "(none)",
    "Bitte zuerst eine TemplateData.xml laden.": "Please load a TemplateData.xml first.",
    "Bitte Kit und Test wählen.": "Please choose kit and test.",
    "MP96-Order speichern": "Save MP96 order",
    "XML-Dateien (*.xml)": "XML files (*.xml)",
    "Der MP96-Auftrag konnte nicht gespeichert werden:\n{e}":
        "The MP96 order could not be saved:\n{e}",
    "MP96-Auftrag gespeichert:\n{path}": "MP96 order saved:\n{path}",
    "Voreinstellung:": "Preset:",
    "— keine —": "— none —",
    "Speichern…": "Save…",
    "Löschen": "Delete",
    "Aktuelle Einstellungen als Voreinstellung speichern":
        "Save the current settings as a preset",
    "Gewählte Voreinstellung löschen": "Delete the selected preset",
    "Voreinstellung speichern": "Save preset",
    "Name der Voreinstellung:": "Preset name:",
    "Voreinstellung löschen": "Delete preset",
    "Voreinstellung „{name}“ wirklich löschen?": "Really delete preset “{name}”?",
    "📋  MP96 Order": "📋  MP96 order",
    "TemplateData.xml am MP96 exportieren und hier importieren.":
        "Export the TemplateData.xml at the MP96 and import it here.",
    "Kit:*": "Kit:*",
    "Test / Protokoll:*": "Test / protocol:*",
    "Probenvolumen (µl):*": "Sample volume (µl):*",
    "Elutionsvolumen (µl):*": "Elution volume (µl):*",
    "Eingangsplatte:*": "Input plate:*",
    "Zielplatte:*": "Output plate:*",
    "Auftragsname:*": "Order name:*",
    "Der Auftragsname darf diese Zeichen nicht enthalten "
    "(er wird als Dateiname verwendet):\n\n{chars}":
        "The order name must not contain these characters "
        "(it is used as a file name):\n\n{chars}",
    "Proben-Belegung prüfen": "Check sample layout",
    "Die Proben liegen nicht lückenlos ab A1 (spaltenweise). Der MagNA Pure 96 "
    "verlangt eine lückenlose Belegung — sonst lässt sich der Lauf nicht starten.":
        "The samples are not placed without gaps from A1 (by column). The MagNA Pure 96 "
        "requires a gap-free layout — otherwise the run cannot be started.",
    "{n} Proben sind kein Vielfaches von 8: der MP96 verarbeitet immer ganze "
    "8er-Spalten und füllt {pad} Well(s) mit Systemflüssigkeit auf.":
        "{n} samples are not a multiple of 8: the MP96 always processes whole columns "
        "of 8 and fills up {pad} well(s) with system fluid.",
    "Zusammenrücken & weiter": "Compact & continue",
    "Fortfahren": "Continue",
    "Proben zusammenrücken (ab A1, lückenlos)": "Compact samples (from A1, no gaps)",

    # ── DB (db/assay_db.py – seltene Fehler) ───────────────────────────────
    "Die Vorlage ist keine gültige WellDone-Assay-Datenbank.":
        "The template is not a valid WellDone assay database.",
    "Es gibt noch keine lokale Assay-Datenbank zum Speichern.":
        "There is no local assay database to save yet.",
    "Kein Ziel-Pfad für die Vorlage angegeben.":
        "No target path given for the template.",
}
