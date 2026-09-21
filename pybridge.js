// pybridge.js — bootet Pyodide, lädt den GETEILTEN WellDone-Kern (dieselben .py wie
// die Desktop-App) ins virtuelle Dateisystem und stellt eine kleine JS-API bereit.
//
// Single-Source: Die Kern-Dateien werden zur Laufzeit per fetch geladen — es gibt
// KEINE zweite Kopie/Übersetzung der Logik. Dieselbe plate_layout.py/csv_export.py,
// die der Desktop ausführt, läuft hier in WebAssembly.
(function (global) {
  "use strict";

  // Pyodide 0.26.4 wird SELBST gehostet: Laufzeit + alle Python-Pakete liegen im Ordner
  // pyodide/ neben index.html (Lizenzen: pyodide/THIRD_PARTY_NOTICES.md). Keine Anfrage
  // an ein CDN oder PyPI — Datenschutz + gesperrte Klinik-Netze. Gegen die Seiten-URL
  // aufgelöst → passt für Dev (/web/pyodide/) und Pages (/pyodide/) gleichermaßen.
  var PYODIDE_URL = new URL("pyodide/", document.baseURI).href;
  // Pakete für loadPackage: Namen aus pyodide-lock.json (Wheel liegt direkt in pyodide/)
  // bzw. lokale Wheels aus pyodide/wheels/ (reine Python-Wheels von PyPI, dort nicht im Lock).
  // reportlab braucht pillow + charset-normalizer (beide im Lock).
  var PY_PACKAGES = ["pillow", "charset-normalizer"];
  var PY_WHEELS = ["reportlab-5.0.1-py3-none-any.whl"];
  // Basis, unter der die Kern-.py liegen. Zwei Layouts, EINE Datei:
  //  • Dev: Projekt-Root wird serviert, die Web-App liegt unter /web/ → "../" trifft /models, /utils, /db.
  //  • Pages (Repo WellDone-Go): index.html + models/ + db/ + utils/ liegen zusammen
  //    in der Wurzel → "" (relativ zur Seite). Anhand des Pfads automatisch wählen.
  var CORE_BASE = (location.pathname.indexOf("/web/") !== -1) ? "../" : "";
  // Absolutes Ziel-Verzeichnis im virtuellen Pyodide-Dateisystem. ABSOLUT, damit
  // mkdirTree und writeFile garantiert denselben Pfad meinen (relative Pfade
  // hängen vom Arbeitsverzeichnis ab → ENOENT).
  var FS_ROOT = "/wd";

  var _pyodide = null;
  var _webapi = null;
  var _ready = null;

  function _loadScript(src) {
    return new Promise(function (resolve, reject) {
      var s = document.createElement("script");
      s.src = src;
      s.onload = resolve;
      s.onerror = function () { reject(new Error("Konnte Skript nicht laden: " + src)); };
      document.head.appendChild(s);
    });
  }

  function _writeFile(path, base) {
    // no-store: nach einem Update immer die frischen Kern-Dateien laden (nicht die
    // vom Browser gecachte alte Version).
    return fetch(base + path, { cache: "no-store" }).then(function (resp) {
      if (!resp.ok) throw new Error("Konnte " + path + " nicht laden (HTTP " + resp.status + ")");
      return resp.text();
    }).then(function (src) {
      var full = FS_ROOT + "/" + path;      // immer absolut
      try {
        var slash = full.lastIndexOf("/");
        _pyodide.FS.mkdirTree(full.substring(0, slash));
        // Als exakte UTF-8-Bytes schreiben — die .py enthalten Umlaute & Sonderzeichen.
        _pyodide.FS.writeFile(full, new TextEncoder().encode(src));
      } catch (err) {
        throw new Error("FS-Fehler bei '" + full + "': " +
          (err && err.message ? err.message : err) + " (errno=" + (err && err.errno) + ")");
      }
    });
  }

  function _boot(onStatus) {
    var status = onStatus || function () {};
    status("Pyodide wird geladen … (einmalig, danach aus dem Browser-Cache)");
    return _loadScript(PYODIDE_URL + "pyodide.js").then(function () {
      return global.loadPyodide({ indexURL: PYODIDE_URL });
    }).then(function (py) {
      _pyodide = py;
      status("WellDone-Kern wird geladen …");
      return fetch("core_manifest.json", { cache: "no-store" }).then(function (r) { return r.json(); });
    }).then(function (manifest) {
      var chain = Promise.resolve();
      manifest.forEach(function (path) {
        chain = chain.then(function () { return _writeFile(path, CORE_BASE); });
      });
      // Die Brücke selbst (liegt neben index.html) landet unter FS_ROOT/webapi.py.
      chain = chain.then(function () { return _writeFile("webapi.py", ""); });
      return chain;
    }).then(function () {
      status("Bibliothek (reportlab) wird geladen …");
      // Alles vom eigenen Server (absolute URLs unter PYODIDE_URL) — für das Pipettierschema-PDF.
      return _pyodide.loadPackage(PY_PACKAGES.concat(PY_WHEELS.map(function (w) {
        return PYODIDE_URL + "wheels/" + w;
      })));
    }).then(function () {
      _pyodide.runPython("import sys; sys.path.insert(0, '" + FS_ROOT + "')");
      _webapi = _pyodide.pyimport("webapi");
      status("bereit");
      return true;
    });
  }

  function init(onStatus) {
    if (!_ready) _ready = _boot(onStatus);
    return _ready;
  }

  function _requireReady() {
    if (!_webapi) throw new Error("Brücke noch nicht bereit — zuerst WellDone.init() abwarten.");
  }

  global.WellDone = {
    init: init,
    isReady: function () { return !!_webapi; },
    // Zugriff auf die rohe Pyodide-Instanz (für Machbarkeits-Tests / spätere PDF-Funktion).
    getPy: function () { return _pyodide; },
    // Sprache setzen (nur Warnmeldungen des Kerns; 'de' Standard).
    setLang: function (lang) { _requireReady(); return _webapi.set_lang(lang); },
    // { assays, samples, start_well, column_wise, plate_format, plate_id, plate_name }
    //   → { assignments, warnings, csv }
    layoutAndCsv: function (payload) {
      _requireReady();
      return JSON.parse(_webapi.layout_and_csv(JSON.stringify(payload || {})));
    },
    // Gleiche Nutzlast wie layoutAndCsv → { ok, pdf:<FS-Pfad>, warnings } bzw. { ok:false, error }.
    exportPdf: function (payload) {
      _requireReady();
      return JSON.parse(_webapi.export_pdf(JSON.stringify(payload || {})));
    },
    // Datei aus dem virtuellen FS als Uint8Array lesen (für den PDF-Download).
    readFile: function (path) {
      _requireReady();
      return _pyodide.FS.readFile(path);
    },
    // Hochgeladene MagNA-Pure-Datei-Bytes ins FS schreiben und parsen lassen →
    // { ok, samples:[[well,name]], warnings } bzw. { ok:false, error }.
    importSamples: function (uint8, ext) {
      _requireReady();
      var path = FS_ROOT + "/_import" + (ext || ".xml");
      _pyodide.FS.writeFile(path, uint8);
      return JSON.parse(_webapi.import_samples(path));
    },
    // Selbsttest der geteilten Serialisierung im Browser.
    echoAssay: function (assay) {
      _requireReady();
      return JSON.parse(_webapi.echo_assay(JSON.stringify(assay || {})));
    }
  };
})(window);
