// app.js — Oberfläche der Browser-Variante („WellDone! Go"). Die gesamte Fach-Logik
// (Belegung, CSV, PDF) läuft im GETEILTEN Python-Kern über WellDone (pybridge.js);
// hier steht nur Darstellung, Eingabe und das Weiterreichen an die Brücke.
(function (global) {
  "use strict";

  var ROWS = "ABCDEFGH";
  var NCOLS = 12;
  var LS_ASSAYS = "welldone.web.assays.v1";
  var LS_LANG = "welldone.web.lang";

  // ── i18n (nur Oberflächen-Texte; Fachbegriffe/Assay-Daten bleiben unverändert) ──
  var I18N = {
    de: {
      tagline: "Plattenbelegung im Browser – kompatibel mit LightCycler® PRO",
      starting: "Starte …", booting: "Der WellDone-Kern wird im Browser geladen … (beim ersten Mal einige Sekunden)",
      ready: "bereit ✓",
      samplePlate: "1. Proben-Platte", clear: "Leeren", importSamples: "⭳ Proben importieren",
      sampleSub: "Proben eingeben, einscannen, vom MP96 importieren oder aus Excel kopieren",
      importDone: "{n} Proben importiert.", importSkipped: "übersprungen: {w}",
      importErr: "Import fehlgeschlagen – ist es ein MagNA-Pure-96-Export (.xml/.csv)?",
      pcrPlate: "4. PCR-Platte", downloadCsv: "⬇ LC-PRO-CSV", downloadPdf: "⬇ Pipettierschema-PDF",
      pdfErr: "Das Pipettierschema-PDF konnte nicht erstellt werden.",
      assays: "2. Assays", assayHint: "Anhaken, welche Assays auf die Platte sollen (nur ein PCR-Profil je Platte).",
      addAssay: "+ Assay anlegen", fName: "Anzeigename", fLcap: "LCAP-Name (Gerät)", fProfile: "PCR-Profil",
      fColor: "Farbe", fPtc: "Positivkontrolle (PTC)", fNtc: "Negativkontrolle (NTC)",
      fPtcName: "PTC-Name (LCAP, optional)", fNtcName: "NTC-Name (LCAP, optional)", save: "Speichern",
      edit: "Bearbeiten", cancel: "Abbrechen",
      fCtrlOrder: "Kontroll-Reihenfolge", ordPSN: "PTC · Proben · NTC", ordSPN: "Proben · PTC · NTC",
      fVolTitle: "Mengen je Reaktion (µl)",
      fWater: "Wasser", fPrimer: "Primer", fMM: "MasterMix", fRt: "RT-Enzym", fTemplate: "Template",
      run: "3. Belegung", plateName: "Plattenname (erscheint überall)", plateId: "Plate-ID (= Barcode der PCR-Platte)",
      colwise: "spaltenweise", rowwise: "zeilenweise",
      runBtn: "▶ Plattenbelegung ausführen",
      disclaimer: "⚠️ Nicht validiertes Hilfswerkzeug – nicht als Medizinprodukt/IVD in Verkehr gebracht, keine CE-Kennzeichnung. Belegung, Kontrollen und Mengen vor jedem Lauf prüfen; vor dem Routineeinsatz im Labor-QM freigeben.",
      legalImprint: "Impressum", legalPrivacy: "Datenschutz",
      needAssay: "Bitte mindestens einen Assay anhaken.",
      needSamples: "Bitte mindestens eine Probe eintragen.",
      needName: "Anzeigename, LCAP-Name und PCR-Profil sind Pflicht.",
      mixedProfile: "Nur EIN PCR-Profil je Platte – angehakt sind mehrere: ",
      placed: "Belegt: {n} Wells", dlReady: "— Bericht (PDF) & LC-PRO-CSV bereit zum Download.",
      remove: "Assay entfernen",
      exportLib: "⬇ Export", importLib: "⬆ Import",
      libImported: "{n} Assays importiert.",
      libImportErr: "Das ist keine gültige Assay-Bibliothek (JSON-Datei).",
      libReplaceConfirm: "Import ersetzt die aktuelle Assay-Liste. Fortfahren?",
      chkShort: "{n} Probe(n) unter {min} Zeichen (LC PRO braucht ≥ {min}): {list}",
      chkLong: "{n} Probe(n) über {max} Zeichen – werden gekürzt: {list}",
      chkBad: "{n} Probe(n) mit unzulässigen Zeichen: {list}"
    },
    en: {
      tagline: "Plate layout in your browser – compatible with LightCycler® PRO",
      starting: "Starting …", booting: "Loading the WellDone core in the browser … (a few seconds the first time)",
      ready: "ready ✓",
      samplePlate: "1. Sample plate", clear: "Clear", importSamples: "⭳ Import samples",
      sampleSub: "enter, scan, import from the MP96 or copy from Excel",
      importDone: "{n} samples imported.", importSkipped: "skipped: {w}",
      importErr: "Import failed – is it a MagNA Pure 96 export (.xml/.csv)?",
      pcrPlate: "4. PCR plate", downloadCsv: "⬇ LC-PRO CSV", downloadPdf: "⬇ Pipetting scheme PDF",
      pdfErr: "The pipetting scheme PDF could not be created.",
      assays: "2. Assays", assayHint: "Tick which assays go on the plate (only one PCR profile per plate).",
      addAssay: "+ Add assay", fName: "Display name", fLcap: "LCAP name (instrument)", fProfile: "PCR profile",
      fColor: "Colour", fPtc: "Positive control (PTC)", fNtc: "Negative control (NTC)",
      fPtcName: "PTC name (LCAP, optional)", fNtcName: "NTC name (LCAP, optional)", save: "Save",
      edit: "Edit", cancel: "Cancel",
      fCtrlOrder: "Control order", ordPSN: "PTC · samples · NTC", ordSPN: "samples · PTC · NTC",
      fVolTitle: "Volumes per reaction (µl)",
      fWater: "Water", fPrimer: "Primer", fMM: "MasterMix", fRt: "RT enzyme", fTemplate: "Template",
      run: "3. Layout", plateName: "Plate name (appears everywhere)", plateId: "Plate ID (= barcode of the PCR plate)",
      colwise: "column-wise", rowwise: "row-wise",
      runBtn: "▶ Run plate layout",
      disclaimer: "⚠️ Non-validated helper tool – not placed on the market as a medical device/IVD, no CE marking. Check the layout, controls and volumes before every run; release it in your lab's QM before routine use.",
      legalImprint: "Legal notice", legalPrivacy: "Privacy",
      needAssay: "Please tick at least one assay.",
      needSamples: "Please enter at least one sample.",
      needName: "Display name, LCAP name and PCR profile are required.",
      mixedProfile: "Only ONE PCR profile per plate – several are ticked: ",
      placed: "Placed: {n} wells", dlReady: "— report (PDF) & LC-PRO CSV ready to download.",
      remove: "Remove assay",
      exportLib: "⬇ Export", importLib: "⬆ Import",
      libImported: "{n} assays imported.",
      libImportErr: "This is not a valid assay library (JSON file).",
      libReplaceConfirm: "Import replaces the current assay list. Continue?",
      chkShort: "{n} sample(s) under {min} characters (LC PRO needs ≥ {min}): {list}",
      chkLong: "{n} sample(s) over {max} characters – will be trimmed: {list}",
      chkBad: "{n} sample(s) with invalid characters: {list}"
    }
  };

  // Standard-Assays beim ersten Start (wie die Desktop-Startbibliothek).
  var DEFAULT_ASSAYS = [
    { id: 1, display_name: "3 EnteroBocAde2", lcap_name: "3 EnteroBocAde2", pcr_profile: "LMM_7plex_96",
      color: "#E74C3C", water_ul: 9.4, primer_ul: 1.5, mastermix_ul: 4.0, rt_enzyme_ul: 0.1, template_ul: 5.0,
      control_layout: "pos_samples_neg", controls: [{ type: "PTC", name: "" }, { type: "NTC", name: "" }] },
    { id: 2, display_name: "Gastro Bacteria M1", lcap_name: "0101_GastroB96_mPCR1", pcr_profile: "LMM_Gastro_96",
      color: "#2ECC71", water_ul: 9.9, primer_ul: 2.0, mastermix_ul: 8.0, rt_enzyme_ul: 0.1, template_ul: 5.0,
      control_layout: "pos_samples_neg", controls: [{ type: "PTC", name: "" }, { type: "NTC", name: "" }] },
    { id: 3, display_name: "SARS-CoV2 Multiplex", lcap_name: "0601_SARS-CoV2-96_mPCR 1", pcr_profile: "LMM_SARS_96",
      color: "#9B59B6", water_ul: 9.9, primer_ul: 2.0, mastermix_ul: 8.0, rt_enzyme_ul: 0.1, template_ul: 5.0,
      control_layout: "pos_samples_neg", controls: [{ type: "PTC", name: "" }, { type: "NTC", name: "" }] }
  ];

  var _lang = "de";
  var _assays = [];
  var _checked = {};          // assay-id -> bool
  var _lastCsv = null;
  var _lastPayload = null;    // letzte Belegungs-Nutzlast (für den PDF-Knopf)
  var _cells = {};            // well -> <input> (Proben-Platte)
  var _editOpen = null;       // assay-id, dessen Inline-Bearbeiten-Formular offen ist

  function $(id) { return document.getElementById(id); }
  function t(key) { return (I18N[_lang] && I18N[_lang][key]) || key; }
  function _num(v, d) { var n = parseFloat(v); return isFinite(n) ? n : d; }

  // Übersetzt alle [data-i18n]-Blätter innerhalb eines Elements (auch dynamisch gebaute).
  function translateWithin(el) {
    var els = el.querySelectorAll("[data-i18n]");
    for (var i = 0; i < els.length; i++) {
      var k = els[i].getAttribute("data-i18n");
      if (I18N[_lang][k] !== undefined && els[i].children.length === 0) els[i].textContent = I18N[_lang][k];
    }
  }

  // ── Sprache ────────────────────────────────────────────────────────────────
  function applyLang() {
    document.documentElement.setAttribute("data-lang", _lang);
    document.documentElement.setAttribute("lang", _lang);
    translateWithin(document.body);
    $("btn-de").setAttribute("aria-pressed", String(_lang === "de"));
    $("btn-en").setAttribute("aria-pressed", String(_lang === "en"));
    if (global.WellDone && WellDone.isReady()) WellDone.setLang(_lang);
  }
  function setLang(l) {
    _lang = (l === "en") ? "en" : "de";
    try { localStorage.setItem(LS_LANG, _lang); } catch (e) {}
    applyLang();
  }

  // ── Assay-Bibliothek (localStorage) ─────────────────────────────────────────
  function loadAssays() {
    try {
      var raw = localStorage.getItem(LS_ASSAYS);
      if (raw) { _assays = JSON.parse(raw); return; }
    } catch (e) {}
    _assays = JSON.parse(JSON.stringify(DEFAULT_ASSAYS));
    saveAssays();
  }
  function saveAssays() {
    try { localStorage.setItem(LS_ASSAYS, JSON.stringify(_assays)); } catch (e) {}
  }
  function nextId() {
    var m = 0; _assays.forEach(function (a) { if (a.id > m) m = a.id; }); return m + 1;
  }
  function _assign(base, extra) { for (var k in extra) base[k] = extra[k]; return base; }

  // Ein Formular (Anlegen ODER Bearbeiten) – ohne globale IDs, damit mehrere
  // Formulare (Inline je Assay + die „+ Assay anlegen"-Box) kollisionsfrei laufen.
  function buildAssayForm(a, isNew, onSave, onCancel) {
    a = a || {};
    var cs = a.controls || [];
    var pName = (cs.filter(function (c) { return c.type === "PTC"; })[0] || {}).name || "";
    var nName = (cs.filter(function (c) { return c.type === "NTC"; })[0] || {}).name || "";
    var wrap = document.createElement("div");
    wrap.className = "assay-form";
    wrap.innerHTML =
      '<label><span data-i18n="fName"></span><input class="fName" type="text" placeholder="z. B. SARS-CoV2 Multiplex"></label>' +
      '<label><span data-i18n="fLcap"></span><input class="fLcap" type="text" placeholder="z. B. 0601_SARS-CoV2-96_mPCR 1"></label>' +
      '<label><span data-i18n="fProfile"></span><input class="fProfile" type="text" placeholder="z. B. LMM_SARS_96"></label>' +
      '<div class="row2">' +
        '<label class="colorrow"><span data-i18n="fColor"></span><input class="fColor" type="color"></label>' +
        '<label class="grow"><span data-i18n="fCtrlOrder"></span><select class="fLayout">' +
          '<option value="pos_samples_neg" data-i18n="ordPSN"></option>' +
          '<option value="samples_pos_neg" data-i18n="ordSPN"></option>' +
        '</select></label>' +
      '</div>' +
      '<div class="ctrlrow">' +
        '<label class="chk"><input class="fPtc" type="checkbox"> <span data-i18n="fPtc"></span></label>' +
        '<label class="chk"><input class="fNtc" type="checkbox"> <span data-i18n="fNtc"></span></label>' +
      '</div>' +
      '<label><span data-i18n="fPtcName"></span><input class="fPtcName" type="text" placeholder="z. B. PosK"></label>' +
      '<label><span data-i18n="fNtcName"></span><input class="fNtcName" type="text" placeholder="z. B. negK"></label>' +
      '<p class="voltitle" data-i18n="fVolTitle"></p>' +
      '<div class="volgrid">' +
        '<label><span data-i18n="fWater"></span><input class="fWater" type="number" step="0.1" min="0"></label>' +
        '<label><span data-i18n="fPrimer"></span><input class="fPrimer" type="number" step="0.1" min="0"></label>' +
        '<label><span data-i18n="fMM"></span><input class="fMM" type="number" step="0.1" min="0"></label>' +
        '<label><span data-i18n="fRt"></span><input class="fRt" type="number" step="0.1" min="0"></label>' +
        '<label><span data-i18n="fTemplate"></span><input class="fTemplate" type="number" step="0.1" min="0"></label>' +
      '</div>' +
      '<div class="formbtns">' +
        '<button type="button" class="btn save" data-i18n="save"></button>' +
        '<button type="button" class="btn ghost cancel" data-i18n="cancel"></button>' +
      '</div>' +
      '<p class="err" hidden></p>';
    var q = function (sel) { return wrap.querySelector(sel); };
    q(".fName").value = a.display_name || ""; q(".fLcap").value = a.lcap_name || ""; q(".fProfile").value = a.pcr_profile || "";
    q(".fColor").value = /^#[0-9a-fA-F]{6}$/.test(a.color) ? a.color : "#3498DB";
    q(".fLayout").value = (a.control_layout === "samples_pos_neg") ? "samples_pos_neg" : "pos_samples_neg";
    q(".fPtc").checked = cs.some(function (c) { return c.type === "PTC"; });
    q(".fNtc").checked = cs.some(function (c) { return c.type === "NTC"; });
    q(".fPtcName").value = pName; q(".fNtcName").value = nName;
    q(".fWater").value = a.water_ul != null ? a.water_ul : 9.9;
    q(".fPrimer").value = a.primer_ul != null ? a.primer_ul : 2.0;
    q(".fMM").value = a.mastermix_ul != null ? a.mastermix_ul : 8.0;
    q(".fRt").value = a.rt_enzyme_ul != null ? a.rt_enzyme_ul : 0.1;
    q(".fTemplate").value = a.template_ul != null ? a.template_ul : 5.0;
    q(".save").onclick = function () {
      var controls = [];
      if (q(".fPtc").checked) controls.push({ type: "PTC", name: q(".fPtcName").value.trim() });
      if (q(".fNtc").checked) controls.push({ type: "NTC", name: q(".fNtcName").value.trim() });
      var data = {
        display_name: q(".fName").value.trim(), lcap_name: q(".fLcap").value.trim(),
        pcr_profile: q(".fProfile").value.trim(), color: q(".fColor").value || "#3498DB",
        control_layout: q(".fLayout").value || "pos_samples_neg",
        water_ul: _num(q(".fWater").value, 9.9), primer_ul: _num(q(".fPrimer").value, 2.0),
        mastermix_ul: _num(q(".fMM").value, 8.0), rt_enzyme_ul: _num(q(".fRt").value, 0.1),
        template_ul: _num(q(".fTemplate").value, 5.0), controls: controls
      };
      if (!data.display_name || !data.lcap_name || !data.pcr_profile) {
        var e = q(".err"); e.textContent = t("needName"); e.hidden = false; return;
      }
      onSave(data);
    };
    q(".cancel").onclick = onCancel;
    translateWithin(wrap);
    return wrap;
  }

  function renderAssays() {
    var ul = $("assayList"); ul.innerHTML = "";
    _assays.forEach(function (a) {
      if (_checked[a.id] === undefined) _checked[a.id] = false;
      var li = document.createElement("li");
      li.className = "assay-item" + (_editOpen === a.id ? " editing" : "");
      var row = document.createElement("div"); row.className = "assay-row";
      var cb = document.createElement("input");
      cb.type = "checkbox"; cb.checked = !!_checked[a.id];
      cb.onchange = function () { _checked[a.id] = cb.checked; };
      var sw = document.createElement("span"); sw.className = "swatch"; sw.style.background = a.color;
      var txt = document.createElement("span"); txt.className = "assay-text";
      var ctrls = (a.controls || []).map(function (c) { return c.type; }).join("+") || "–";
      txt.innerHTML = "<strong>" + esc(a.display_name) + "</strong><span class='sub'>" +
        esc(a.pcr_profile) + " · " + ctrls + "</span>";
      var ed = document.createElement("button");
      ed.type = "button"; ed.className = "rm"; ed.textContent = "✎"; ed.title = t("edit");
      ed.onclick = function () { _editOpen = (_editOpen === a.id ? null : a.id); renderAssays(); };
      var rm = document.createElement("button");
      rm.type = "button"; rm.className = "rm"; rm.textContent = "✕"; rm.title = t("remove");
      rm.onclick = function () { removeAssay(a.id); };
      var lbl = document.createElement("label"); lbl.className = "assay-lbl";
      lbl.appendChild(cb); lbl.appendChild(sw); lbl.appendChild(txt);
      row.appendChild(lbl); row.appendChild(ed); row.appendChild(rm);
      li.appendChild(row);
      if (_editOpen === a.id) {
        // Bearbeiten klappt DIREKT unter dem jeweiligen Assay auf.
        li.appendChild(buildAssayForm(a, false,
          function (data) {
            _assays = _assays.map(function (x) { return x.id === a.id ? _assign({ id: a.id }, data) : x; });
            _editOpen = null; saveAssays(); renderAssays();
          },
          function () { _editOpen = null; renderAssays(); }
        ));
      }
      ul.appendChild(li);
    });
  }
  function removeAssay(id) {
    _assays = _assays.filter(function (a) { return a.id !== id; });
    delete _checked[id]; if (_editOpen === id) _editOpen = null;
    saveAssays(); renderAssays();
  }
  // „+ Assay anlegen" – eigener, immer sichtbarer Einstieg (getrennt vom Bearbeiten).
  function mountAddForm() {
    var host = $("addFormHost"); if (!host) return;
    host.innerHTML = "";
    host.appendChild(buildAssayForm({}, true,
      function (data) {
        _assays.push(_assign({ id: nextId() }, data));
        saveAssays(); renderAssays();
        $("assayBox").open = false; mountAddForm();
      },
      function () { $("assayBox").open = false; mountAddForm(); }
    ));
  }

  // ── Bibliothek als JSON exportieren / importieren ───────────────────────────
  function libMsg(msg, isErr) {
    var el = $("libMsg");
    if (!msg) { el.hidden = true; el.textContent = ""; el.classList.remove("err"); return; }
    el.hidden = false; el.textContent = msg; el.classList.toggle("err", !!isErr);
  }
  function exportLibrary() {
    var data = { app: "WellDone! Go", kind: "assay-library", version: 1, assays: _assays };
    var blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url; a.download = "welldone_assays_" + stamp() + ".json";
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }
  function normalizeAssay(a, id) {
    a = a || {};
    return {
      id: id,
      display_name: String(a.display_name || a.name || "").trim() || ("Assay " + id),
      lcap_name: String(a.lcap_name || a.display_name || "").trim(),
      pcr_profile: String(a.pcr_profile || "").trim(),
      color: /^#[0-9a-fA-F]{6}$/.test(a.color) ? a.color : "#3498DB",
      control_layout: a.control_layout || "pos_samples_neg",
      water_ul: _num(a.water_ul, 9.9), primer_ul: _num(a.primer_ul, 2.0),
      mastermix_ul: _num(a.mastermix_ul, 8.0), rt_enzyme_ul: _num(a.rt_enzyme_ul, 0.1),
      template_ul: _num(a.template_ul, 5.0),
      controls: (Array.isArray(a.controls) ? a.controls : []).filter(function (c) {
        return c && (c.type === "PTC" || c.type === "NTC");
      }).map(function (c) { return { type: c.type, name: String(c.name || "") }; })
    };
  }
  function importFile(inputEl) {
    var f = inputEl.files && inputEl.files[0];
    inputEl.value = "";                       // erneutes Wählen derselben Datei erlauben
    if (!f) return;
    var reader = new FileReader();
    reader.onload = function () {
      var parsed;
      try { parsed = JSON.parse(reader.result); } catch (e) { libMsg(t("libImportErr"), true); return; }
      var arr = Array.isArray(parsed) ? parsed
              : (parsed && Array.isArray(parsed.assays) ? parsed.assays : null);
      if (!arr || !arr.length) { libMsg(t("libImportErr"), true); return; }
      if (_assays.length && !global.confirm(t("libReplaceConfirm"))) return;
      _assays = arr.map(function (a, i) { return normalizeAssay(a, i + 1); });
      _checked = {}; _editOpen = null; saveAssays(); renderAssays();
      libMsg(t("libImported").replace("{n}", _assays.length), false);
    };
    reader.onerror = function () { libMsg(t("libImportErr"), true); };
    reader.readAsText(f);
  }

  // ── Proben-Platte (Eingabe-Raster) ──────────────────────────────────────────
  function wellName(r, c) { return ROWS[r] + (c + 1); }

  function buildSourcePlate() {
    var g = $("sourcePlate"); g.innerHTML = ""; _cells = {};
    g.appendChild(corner());
    for (var c = 0; c < NCOLS; c++) g.appendChild(header(String(c + 1)));
    for (var r = 0; r < ROWS.length; r++) {
      g.appendChild(header(ROWS[r]));
      for (var c2 = 0; c2 < NCOLS; c2++) {
        var w = wellName(r, c2);
        var inp = document.createElement("input");
        inp.type = "text"; inp.className = "cell in"; inp.dataset.r = r; inp.dataset.c = c2;
        inp.title = w;
        inp.addEventListener("paste", onPaste);
        inp.addEventListener("keydown", onCellKey);
        _cells[w] = inp;
        g.appendChild(inp);
      }
    }
  }
  function corner() { var d = document.createElement("div"); d.className = "hdr corner"; return d; }
  function header(txt) { var d = document.createElement("div"); d.className = "hdr"; d.textContent = txt; return d; }

  function onPaste(ev) {
    var text = (ev.clipboardData || global.clipboardData).getData("text");
    if (text === undefined || text === null) return;
    if (text.indexOf("\t") < 0 && text.indexOf("\n") < 0) return;  // Einzelwert → normal einfügen
    ev.preventDefault();
    var startR = parseInt(ev.target.dataset.r, 10), startC = parseInt(ev.target.dataset.c, 10);
    var rows = text.replace(/\r/g, "").replace(/\n$/, "").split("\n");
    for (var i = 0; i < rows.length; i++) {
      var colsv = rows[i].split("\t");
      for (var j = 0; j < colsv.length; j++) {
        var rr = startR + i, cc = startC + j;
        if (rr < ROWS.length && cc < NCOLS) {
          var cell = _cells[wellName(rr, cc)];
          if (cell) cell.value = colsv[j].trim();
        }
      }
    }
  }
  function onCellKey(ev) {
    // Return springt SPALTENWEISE zur nächsten Zelle (A1→B1→…→H1→A2…),
    // Shift+Return rückwärts — passt zur spaltenweisen Eintrag-/Sammel-Reihenfolge.
    if (ev.key !== "Enter") return;
    ev.preventDefault();
    var r = parseInt(ev.target.dataset.r, 10), c = parseInt(ev.target.dataset.c, 10);
    var total = ROWS.length * NCOLS;
    var idx = c * ROWS.length + r + (ev.shiftKey ? -1 : 1);
    idx = (idx % total + total) % total;                 // umlaufen (H12 → A1)
    var next = _cells[wellName(idx % ROWS.length, Math.floor(idx / ROWS.length))];
    if (next) { next.focus(); next.select(); }
  }
  function clearSamples() {
    Object.keys(_cells).forEach(function (w) { _cells[w].value = ""; });
    importMsg("");   // Kopf-Hinweis wieder auf den Standardtext
  }

  // ── MagNA-Pure-96-Proben-Import ─────────────────────────────────────────────
  // Meldung sitzt in der Kopfzeile rechts neben „1. Proben-Platte" und ersetzt
  // dort den Standard-Hinweis (sampleSub).
  function importMsg(msg, isErr) {
    var el = $("importMsg"); if (!el) return;
    el.textContent = msg || t("sampleSub");
    el.classList.toggle("err", !!isErr);
  }
  function normWell(w) {
    var m = String(w || "").toUpperCase().replace(/\s/g, "").match(/^([A-H])0*([1-9][0-9]?)$/);
    return m ? (m[1] + m[2]) : String(w || "").toUpperCase().replace(/\s/g, "");
  }
  function fillGrid(samples) {
    Object.keys(_cells).forEach(function (w) { _cells[w].value = ""; });
    var filled = 0, skipped = [];
    samples.forEach(function (pair) {
      var cell = _cells[normWell(pair[0])];
      if (cell) { cell.value = String(pair[1]); filled++; }
      else skipped.push(String(pair[0]));
    });
    return { filled: filled, skipped: skipped };
  }
  function importSamplesFile(inputEl) {
    var f = inputEl.files && inputEl.files[0];
    inputEl.value = "";                        // erneutes Wählen derselben Datei erlauben
    if (!f) return;
    var ext = (f.name.toLowerCase().match(/\.(xml|csv|txt)$/) || [".xml"])[0];
    var reader = new FileReader();
    reader.onload = function () {
      var res;
      try { res = WellDone.importSamples(new Uint8Array(reader.result), ext); }
      catch (e) { importMsg(t("importErr") + " (" + (e && e.message ? e.message : e) + ")", true); return; }
      if (!res || !res.ok) { importMsg(t("importErr"), true); return; }
      var r = fillGrid(res.samples || []);
      var msg = t("importDone").replace("{n}", r.filled);
      if (r.skipped.length) msg += " (" + t("importSkipped").replace("{w}", r.skipped.join(", ")) + ")";
      importMsg(msg, false);
    };
    reader.onerror = function () { importMsg(t("importErr"), true); };
    reader.readAsArrayBuffer(f);
  }
  function collectSamples() {
    // spaltenweise einsammeln (A1,B1,…,H1,A2,…) – wie am Desktop eingetragen
    var out = [];
    for (var c = 0; c < NCOLS; c++) {
      for (var r = 0; r < ROWS.length; r++) {
        var w = wellName(r, c), v = _cells[w].value.trim();
        if (v) out.push([w, v]);
      }
    }
    return out;
  }

  // ── PCR-Platte (Ergebnis) ───────────────────────────────────────────────────
  var _pcrCells = {};
  function buildPcrPlate() {
    var g = $("pcrPlate"); g.innerHTML = ""; _pcrCells = {};
    g.appendChild(corner());
    for (var c = 0; c < NCOLS; c++) g.appendChild(header(String(c + 1)));
    for (var r = 0; r < ROWS.length; r++) {
      g.appendChild(header(ROWS[r]));
      for (var c2 = 0; c2 < NCOLS; c2++) {
        var w = wellName(r, c2);
        var d = document.createElement("div");
        d.className = "cell out"; d.dataset.well = w;
        _pcrCells[w] = d;
        g.appendChild(d);
      }
    }
  }
  function paintPcr(assignments) {
    Object.keys(_pcrCells).forEach(function (w) {
      var d = _pcrCells[w]; d.style.background = ""; d.textContent = ""; d.title = w; d.className = "cell out";
    });
    assignments.forEach(function (a) {
      var d = _pcrCells[a.well]; if (!d) return;
      d.style.background = a.fill || a.color;
      var isCtrl = (a.role !== "Unknown");
      d.className = "cell out filled" + (isCtrl ? " ctrl" : "");
      d.textContent = "";
      var label = isCtrl ? a.role : (a.sample_id || "");
      if (label) {
        var sp = document.createElement("span");
        sp.className = "wtext"; sp.textContent = label;   // lange Namen werden per CSS abgeschnitten
        d.appendChild(sp);
      }
      d.title = a.well + ": " + a.sample_id + " (" + a.role + ") – " + a.assay_name;
    });
  }
  function renderLegend(assignments) {
    var seen = {}, order = [];
    assignments.forEach(function (a) {
      if (!seen[a.assay_id]) { seen[a.assay_id] = { name: a.assay_name, color: a.color }; order.push(a.assay_id); }
    });
    var el = $("legend"); el.innerHTML = "";
    order.forEach(function (id) {
      var it = seen[id];
      var span = document.createElement("span"); span.className = "leg";
      var sw = document.createElement("span"); sw.className = "swatch"; sw.style.background = it.color;
      span.appendChild(sw); span.appendChild(document.createTextNode(it.name));
      el.appendChild(span);
    });
  }
  // „Leeren" der PCR-Platte: Ergebnis, Legende, Status und Downloads zurücksetzen.
  function clearResult() {
    Object.keys(_pcrCells).forEach(function (w) {
      var d = _pcrCells[w]; d.style.background = ""; d.textContent = ""; d.title = w; d.className = "cell out";
    });
    $("legend").innerHTML = "";
    _lastCsv = null; _lastPayload = null;
    $("csvBtn").disabled = true; $("pdfBtn").disabled = true;
    runStatus("");
  }

  // ── Belegung ausführen ──────────────────────────────────────────────────────
  function checkedAssays() {
    return _assays.filter(function (a) { return _checked[a.id]; });
  }
  // Statuszeile UNTER dem grünen „Ausführen"-Knopf.
  function runStatus(msg, isErr) {
    var w = $("runStatus"); if (!w) return;
    if (!msg) { w.hidden = true; w.textContent = ""; w.classList.remove("err"); return; }
    w.hidden = false; w.textContent = msg; w.classList.toggle("err", !!isErr);
  }
  function runLayout() {
    var assays = checkedAssays();
    if (!assays.length) { runStatus(t("needAssay"), true); return; }
    var samples = collectSamples();
    if (!samples.length) { runStatus(t("needSamples"), true); return; }

    // Ein-Profil-Sperre (wie am Desktop) – vor dem Rechnen
    var profs = {};
    assays.forEach(function (a) { var p = (a.pcr_profile || "").trim(); if (p) profs[p] = true; });
    var pk = Object.keys(profs);
    if (pk.length > 1) { runStatus(t("mixedProfile") + pk.join(", "), true); return; }

    var payload = {
      assays: assays, samples: samples,
      start_well: "A1",             // Go beginnt immer bei A1 …
      column_wise: ($("direction").value !== "row"),  // … Richtung wählbar in der Belegung-Kopfzeile
      plate_format: "96",
      plate_id: $("plateId").value.trim(),
      plate_name: $("plateName").value.trim()
    };
    _lastPayload = payload;
    var res = WellDone.layoutAndCsv(payload);

    paintPcr(res.assignments);
    renderLegend(res.assignments);
    _lastCsv = res.csv;
    $("csvBtn").disabled = !res.assignments.length;
    $("pdfBtn").disabled = !res.assignments.length;

    var lines = ["✓ " + t("placed").replace("{n}", res.assignments.length) + " " + t("dlReady")];
    (res.warnings || []).forEach(function (w) { lines.push("⚠️ " + w); });
    var c = res.checks || {};
    var fp = function (arr) { return arr.slice(0, 6).map(function (p) { return p[0] + ":" + p[1]; }).join(", ") + (arr.length > 6 ? " …" : ""); };
    var fb = function (arr) { return arr.slice(0, 6).map(function (p) { return p[0] + ":" + p[1] + "→" + p[2]; }).join(", ") + (arr.length > 6 ? " …" : ""); };
    if (c.too_short && c.too_short.length) lines.push("⚠️ " + t("chkShort").replace("{n}", c.too_short.length).replace(/\{min\}/g, c.min).replace("{list}", fp(c.too_short)));
    if (c.too_long && c.too_long.length) lines.push("⚠️ " + t("chkLong").replace("{n}", c.too_long.length).replace("{max}", c.max).replace("{list}", fp(c.too_long)));
    if (c.bad_chars && c.bad_chars.length) lines.push("⚠️ " + t("chkBad").replace("{n}", c.bad_chars.length).replace("{list}", fb(c.bad_chars)));
    runStatus(lines.join("\n"), false);
  }

  function stamp() {
    var d = new Date(), p = function (n) { return (n < 10 ? "0" : "") + n; };
    return "" + d.getFullYear() + p(d.getMonth() + 1) + p(d.getDate()) + "_" + p(d.getHours()) + p(d.getMinutes());
  }
  function downloadCsv() {
    if (!_lastCsv) return;
    var id = $("plateId").value.trim().replace(/[^A-Za-z0-9_-]/g, "") || "platesetup";
    var blob = new Blob([_lastCsv], { type: "text/csv;charset=utf-8" });
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url; a.download = id + "_" + stamp() + ".csv";
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }
  function downloadPdf() {
    if (!_lastPayload) return;
    var res;
    try { res = WellDone.exportPdf(_lastPayload); }
    catch (e) { runStatus(t("pdfErr") + " (" + (e && e.message ? e.message : e) + ")", true); return; }
    if (!res || !res.ok) { runStatus(t("pdfErr"), true); return; }
    var bytes = WellDone.readFile(res.pdf);
    var blob = new Blob([bytes], { type: "application/pdf" });
    var id = $("plateId").value.trim().replace(/[^A-Za-z0-9_-]/g, "") || "pipettierschema";
    var url = URL.createObjectURL(blob);
    var a = document.createElement("a");
    a.href = url; a.download = id + "_Pipettierschema_" + stamp() + ".pdf";
    document.body.appendChild(a); a.click(); document.body.removeChild(a);
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  function esc(s) { return String(s).replace(/[&<>"]/g, function (c) {
    return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]; }); }

  // ── Stiller Anti-Drift-Selbsttest (Konsole) ─────────────────────────────────
  function selfTest() {
    try {
      var EXP =
        "PlateId,PlatesetupName,PlateType,SampleId,WellPosition,AssayName,Targetname,Dilution,MasterMixName,LotNumber,RunProfileName,SampleRole\r\n" +
        "PL01,Testlauf,96,PTC,A1,LCAP_EINS_96,,,,,PROFIL_X,PTC\r\n" +
        "PL01,Testlauf,96,Probe-001,B1,LCAP_EINS_96,,,,,PROFIL_X,Unknown\r\n" +
        "PL01,Testlauf,96,Probe-002,C1,LCAP_EINS_96,,,,,PROFIL_X,Unknown\r\n" +
        "PL01,Testlauf,96,Probe-003,D1,LCAP_EINS_96,,,,,PROFIL_X,Unknown\r\n" +
        "PL01,Testlauf,96,NTC,E1,LCAP_EINS_96,,,,,PROFIL_X,NTC\r\n" +
        "PL01,Testlauf,96,PosK2,A2,LCAP_ZWEI_96,,,,,PROFIL_X,PTC\r\n" +
        "PL01,Testlauf,96,Probe-001,B2,LCAP_ZWEI_96,,,,,PROFIL_X,Unknown\r\n" +
        "PL01,Testlauf,96,Probe-002,C2,LCAP_ZWEI_96,,,,,PROFIL_X,Unknown\r\n" +
        "PL01,Testlauf,96,Probe-003,D2,LCAP_ZWEI_96,,,,,PROFIL_X,Unknown\r\n" +
        "PL01,Testlauf,96,NTC,E2,LCAP_ZWEI_96,,,,,PROFIL_X,NTC\r\n";
      var r = WellDone.layoutAndCsv({
        assays: [
          { id: 1, display_name: "Assay Eins", lcap_name: "LCAP_EINS_96", pcr_profile: "PROFIL_X",
            color: "#3498DB", water_ul: 9.9, primer_ul: 2.0, mastermix_ul: 8.0, rt_enzyme_ul: 0.1, template_ul: 5.0,
            controls: [{ type: "PTC", name: "" }, { type: "NTC", name: "" }] },
          { id: 2, display_name: "Assay Zwei", lcap_name: "LCAP_ZWEI_96", pcr_profile: "PROFIL_X",
            color: "#E74C3C", water_ul: 9.9, primer_ul: 2.0, mastermix_ul: 8.0, rt_enzyme_ul: 0.1, template_ul: 5.0,
            controls: [{ type: "PTC", name: "PosK2" }, { type: "NTC", name: "" }] }
        ],
        samples: [["A1", "Probe-001"], ["B1", "Probe-002"], ["C1", "Probe-003"]],
        start_well: "A1", column_wise: true, plate_format: "96", plate_id: "PL01", plate_name: "Testlauf"
      });
      console.log("[WellDone] Anti-Drift-Selbsttest:", r.csv === EXP ? "OK (CSV byte-genau)" : "FEHLER – CSV weicht ab!");
    } catch (e) { console.warn("[WellDone] Selbsttest übersprungen:", e); }
  }

  // ── Start ───────────────────────────────────────────────────────────────────
  function boot() {
    try { _lang = localStorage.getItem(LS_LANG) === "en" ? "en" : "de"; } catch (e) {}
    buildSourcePlate();
    buildPcrPlate();
    loadAssays();
    renderAssays();
    mountAddForm();
    applyLang();

    WellDone.init(function (s) { $("status").textContent = s; }).then(function () {
      WellDone.setLang(_lang);
      $("status").textContent = t("ready");
      $("boot").hidden = true;
      $("app").hidden = false;
      selfTest();
    }).catch(function (e) {
      $("status").textContent = "Fehler: " + (e && e.message ? e.message : e);
      console.error(e);
    });
  }

  global.WDApp = {
    setLang: setLang, clearSamples: clearSamples, clearResult: clearResult,
    runLayout: runLayout, downloadCsv: downloadCsv, downloadPdf: downloadPdf,
    exportLibrary: exportLibrary, importFile: importFile, importSamplesFile: importSamplesFile
  };

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})(window);
