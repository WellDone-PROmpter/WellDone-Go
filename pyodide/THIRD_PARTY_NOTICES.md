# Third-Party Notices — WellDone! Go

**DE:** WellDone! Go führt Python im Browser über Pyodide (WebAssembly) aus. Die Pyodide-Laufzeit und alle benötigten Python-Pakete liegen unverändert in diesem Ordner `pyodide/` und werden ausschließlich vom eigenen Server geladen — kein CDN, kein PyPI zur Laufzeit. Die Dateien stammen aus den unten genannten offiziellen Quellen; die SHA-256-Prüfsummen wurden gegen `pyodide-lock.json` bzw. die PyPI-Angaben geprüft. Die Lizenztexte liegen im Unterordner `licenses/`.

**EN:** WellDone! Go runs Python in the browser via Pyodide (WebAssembly). The Pyodide runtime and all required Python packages are shipped unmodified in this folder `pyodide/` and are loaded only from this site's own server — no CDN, no PyPI at runtime. The files were taken from the official sources listed below; their SHA-256 checksums were verified against `pyodide-lock.json` or the PyPI metadata. The licence texts are in the subfolder `licenses/`.

| Komponente / Component | Version | Quelle / Source | Lizenz / Licence | Lizenztext / Licence text |
|---|---|---|---|---|
| Pyodide (Laufzeit / runtime: `pyodide.js`, `pyodide.asm.js`, `pyodide.asm.wasm`, `python_stdlib.zip`, `pyodide-lock.json`) | 0.26.4 | https://cdn.jsdelivr.net/pyodide/v0.26.4/full/ | MPL-2.0 | `licenses/pyodide-LICENSE.txt` |
| CPython (in Pyodide enthalten / bundled with Pyodide) | 3.12.1 | https://www.python.org/ | PSF-2.0 | `licenses/cpython-LICENSE.txt` |
| Pillow (`pillow-10.2.0-cp312-cp312-pyodide_2024_0_wasm32.whl`) | 10.2.0 | https://cdn.jsdelivr.net/pyodide/v0.26.4/full/pillow-10.2.0-cp312-cp312-pyodide_2024_0_wasm32.whl | HPND | `licenses/pillow-LICENSE.txt` |
| charset-normalizer (`charset_normalizer-3.3.2-py3-none-any.whl`) | 3.3.2 | https://cdn.jsdelivr.net/pyodide/v0.26.4/full/charset_normalizer-3.3.2-py3-none-any.whl | MIT | `licenses/charset_normalizer-LICENSE.txt` |
| ReportLab (`wheels/reportlab-5.0.1-py3-none-any.whl`) | 5.0.1 | https://files.pythonhosted.org/packages/db/cb/dacbc268cb68d0428ea2cbd85266195a9ab3e677449589ddae59bd7542ac/reportlab-5.0.1-py3-none-any.whl | BSD-3-Clause | `licenses/reportlab-LICENSE.txt` |

## SHA-256

```
c0069107621d5b942a659e737a12e774cc0451feaa2256f475d72e071d844ec7  pyodide.js
919560652ed3dad3707cb3a394785da1e046fb13dc0defa162058ff230cb7eed  pyodide.asm.js
b7e66a19427a55010ac3367c1b6c64b893f9826f783412945fdf0c3337f3bc94  pyodide.asm.wasm
72894522b791858b9d613ac786b951d8b5094035dcf376313ea24a466810f336  python_stdlib.zip
cd50b49de944c579045e122fe8628b31f9ce446379f032f36c05e273d38766e0  pyodide-lock.json
9f3ae58c481ade2a88f794a5aa130b9514d315ef549f254e474f9593a73428cf  pillow-10.2.0-cp312-cp312-pyodide_2024_0_wasm32.whl
28b5d11a85eee727ea45c95f87ce285a53233a043f228cd88b5079fb090f102e  charset_normalizer-3.3.2-py3-none-any.whl
1c36e6bb0e71780c72331eba60da7f602e8d4389a8723825af71342e49d791e8  wheels/reportlab-5.0.1-py3-none-any.whl
```

**DE:** Pyodide ist unter der Mozilla Public License 2.0 lizenziert; der Quelltext ist unter https://github.com/pyodide/pyodide (Tag `0.26.4`) erhältlich. Die Laufzeit enthält CPython sowie weitere mitkompilierte Bibliotheken unter deren jeweiligen Lizenzen (siehe Pyodide-Repository).

**EN:** Pyodide is licensed under the Mozilla Public License 2.0; its source code is available at https://github.com/pyodide/pyodide (tag `0.26.4`). The runtime contains CPython and further compiled-in libraries under their respective licences (see the Pyodide repository).
