# csv2md - CSV zu Markdown Konverter

## Übersicht

Skript zur Extraktion einer CSV-Spalte und Export als Markdown-Datei. Unterstützt interaktiven und nicht-interaktiven Modus. Optionale systemd-Integration für regelmäßige Ausführung.

## Voraussetzungen

- **Python 3.11+** (aktuelle LTS für maximale Konsistenz)
- **venv** für Abhängigkeits-Isolation
- **systemd** (Linux, optional für Timer-Integration)

### Venv einrichten

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

## Coding-Richtlinien

### Grundregeln

| Regel | Vorgabe |
|-------|---------|
| **Shebang** | `#!/usr/bin/env python3` |
| **main()-Guard** | Immer `if __name__ == "__main__"` |
| **Imports** | Nur Standardbibliothek (csv, urllib, argparse, pathlib, sys, logging) |
| **Type Hints** | Alle Funktionen typisieren |
| **Strings** | f-strings bevorzugen, kein `%` oder `.format()` |
| **Pfade** | `pathlib.Path`, nicht `os.path` |
| **Logging** | `logging`-Modul statt `print()` — für systemd-Journal-Kompatibilität |
| **Encoding** | `encoding="utf-8"` bei allen `open()`-Aufrufen |
| **Rückgabewerte** | `sys.exit(0)` Erfolg, `sys.exit(n)` Fehler (Exit-Codes siehe unten) |
| **Fehlerbehandlung** | Spezifische Exceptions (`FileNotFoundError`, `ValueError`), kein bare `except` |
| **Kommentare** | Keine (außer Docstrings) |
| **Docstrings** | Nur für komplexe Funktionen, kurz |

### Code-Struktur

```python
#!/usr/bin/env python3
"""csv2md - CSV to Markdown converter."""

import argparse
import csv
import logging
from pathlib import Path
import sys
import urllib.request
import urllib.error

logger = logging.getLogger(__name__)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    ...


def read_csv(...) -> list[dict[str, str]]:
    ...


def convert(...) -> str:
    ...


def setup_systemd(...) -> None:
    ...


def main() -> int:
    ...


if __name__ == "__main__":
    sys.exit(main())
```

## Verwendung

```bash
csv2md.py [Optionen] [input] [output]
```

### Optionen

| Flag | Langform | Beschreibung |
|------|----------|--------------|
| `-i` | `--interactive` | Interaktiver Modus (Fragen stellen) |
| `-c` | `--column NAME` | Spaltenname (non-interaktiv, **erforderlich** wenn `-i` fehlt) |
| `-f` | `--force` | Output überschreiben ohne Nachfrage |
| `-d` | `--delimiter CHAR` | CSV-Trennzeichen: `,` `;` `\t` `auto` (default: `auto`) |
| `-e` | `--encoding NAME` | Zeichenkodierung (default: `utf-8`) |
| `-n` | `--no-verify` | SSL-Zertifikatsprüfung deaktivieren |
| `-h` | `--help` | Hilfe anzeigen |

**Regel:** `-i` und `-c` schließen sich gegenseitig aus. Fehler + Exit 6 wenn beide gesetzt.

### Argumente

- **input** (optional): URL (`https://...`) oder Dateipfad zur CSV-Datei
  - Erkennung: `input_str.startswith(("https://", "http://"))` → URL, sonst Pfad
  - Im interaktiven Modus (`-i`) wird input bei Bedarf erfragt
  - Im nicht-interaktiven Modus (`-c`) ist input **erforderlich**
- **output** (optional): Dateipfad für die Markdown-Ausgabe
  - Output-Verzeichnis muss existieren, sonst Fehler + Exit 7
  - Im interaktiven Modus (`-i`) wird output bei Bedarf erfragt
  - Im nicht-interaktiven Modus (`-c`) ist output **erforderlich**

### Exit-Codes

| Code | Bedeutung |
|------|-----------|
| 0 | Erfolg |
| 1 | CSV nicht gefunden / nicht lesbar |
| 2 | Spalte nicht vorhanden |
| 3 | URL nicht erreichbar (Timeout 30s) |
| 4 | SSL-Verifikationsfehler |
| 5 | Leere CSV |
| 6 | `-i` + `-c` gleichzeitig, oder ungültiges Trennzeichen |
| 7 | Output-Verzeichnis existiert nicht |
| 8 | input/output fehlt im nicht-interaktiven Modus |

## Modi

### Interaktiver Modus (`-i`)

**Präziser Flow (Reihenfolge wichtig):**

1. **Input-Quelle erfragen** — "CSV-Quelle (Dateipfad oder URL):"
   - Wenn input als CLI-Argument übergeben wurde → überspringen
   - Erkennung: startet mit `https://` oder `http://` → URL, sonst Dateipfad
2. **Delimiter abfragen** — Komma / Semikolon / Tab / Auto-Erkennung
   - Wenn delimiter als CLI-Argument übergeben wurde → überspringen
   - Bei `auto`: Rohdaten laden, `csv.Sniffer` versuchen, bei Fehlschlag Fallback auf Komma
3. **CSV laden** — URL oder Datei öffnen, mit gewähltem Delimiter parsen
   - URL: `urllib.request.urlopen()` mit 30s Timeout, SSL-Verify (es sei denn `--no-verify`)
4. **Spaltenüberschriften anzeigen** — nummerierte Liste (1, 2, 3, ...)
5. **Spalte auswählen** — Nummer eingeben
6. **Output-Pfad erfragen** — "Ausgabe-Dateipfad:"
   - Wenn output als CLI-Argument übergeben wurde → überspringen
7. **Output existiert?** — Ja → "Überschreiben?" fragen; Nein → weiter
8. **systemd-Abfrage:** "Soll systemd aufgesetzt werden?" (J/N)
   - Falls Ja: Timer-Option (stündlich/täglich/wöchentlich)
     - Bei täglich: Uhrzeit (HH:MM)
     - Bei wöchentlich: Wochentag + Uhrzeit
     - Wochentag-Format: `Mon`, `Tue`, `Wed`, `Thu`, `Fri`, `Sat`, `Sun`
   - **"Nur Dateien erstellen" oder "Sofort installieren"?**
     - Dateien erstellen → `.service`/`.timer` im aktuellen Verzeichnis
     - Installieren → Dateien nach `~/.config/systemd/user/` kopieren + Timer aktivieren
9. **Markdown generieren und schreiben** → Fertig

### Nicht-interaktiver Modus (systemd)

```bash
./csv2md.py --column "Spaltenname" --delimiter "," --force <input> <output>
```

## Markdown-Output

```markdown
# [Spaltenname]

* [Item 1]
* [Item 2]
* [Item 3]
...
```

- Output-Encoding: UTF-8
- Keine Duplikate (automatisch dedupliziert, **case-sensitive**)
- Leere Zellen werden übersprungen
- Items in Original-Reihenfolge

## CSV-Verarbeitung

### Encoding

- Default: **UTF-8**
- BOM-Handling: `utf-8-sig` für Windows-kompatible CSVs
- Default via `--encoding` überschreibbar

### Delimiter

| Wert | Bedeutung |
|------|-----------|
| `,` | Komma (Standard-CSV) |
| `;` | Semikolon (deutsches CSV) |
| `\t` | Tabstopp (TSV) |
| `auto` | `csv.Sniffer().sniff()` — bei Fehlschlag: Fallback auf Komma |

### Fehlerbehandlung

- CSV nicht gefunden → Exit 1
- Spalte nicht vorhanden → Exit 2
- URL nicht erreichbar / Timeout (30s) → Exit 3
- SSL-Verifikationsfehler → Exit 4 + Hinweis auf `--no-verify`
- Leere CSV (0 Zeilen) → Exit 5
- `-i` + `-c` gleichzeitig oder ungültiges Trennzeichen → Exit 6
- Output-Verzeichnis fehlt → Exit 7
- input/output fehlt im nicht-interaktiven Modus → Exit 8
- Delimiter-Erkennung fehlgeschlagen → Fallback auf Komma, kein Fehler

## Netzwerk (URL-Input)

- Default-Timeout: 30 Sekunden
- SSL-Verifikation: standardmäßig aktiviert
- `--no-verify` setzt `ssl._create_unverified_context()` (für self-signed)
- HTTP Redirects: `urllib.request` folgt standardmäßig Redirects

## systemd-Integration

### Service-Template (`csv2md.service`)

```ini
[Unit]
Description=csv2md - CSV to Markdown Converter
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
User=%u
ExecStart=<ABSOLUTER_PFAD_ZUR_PYTHON> <ABSOLUTER_PFAD_ZUM_SKRIPT> --column <SPALTE> --delimiter <DELIMITER> --force <INPUT> <OUTPUT>
WorkingDirectory=<ABSOLUTER_PFAD_ZUM_PROJEKT>

[Install]
WantedBy=default.target
```

**Hinweise:**
- `User=%u` wird von systemd automatisch auf den aktuellen User gesetzt
- `ExecStart` muss den absoluten Pfad zum venv-Python enthalten: `~/.config/systemd/user/` → auflösen zu `/home/user/.config/...`
- `WorkingDirectory` auf das Projektverzeichnis setzen

### Timer-Template (`csv2md.timer`)

```ini
[Unit]
Description=csv2md Timer - regelmäßige CSV-Konvertierung

[Timer]
OnCalendar=<ONCALENDAR_SYNTAX>
Persistent=true

[Install]
WantedBy=default.target
```

**OnCalendar-Syntax nach Timer-Option:**

| Option | OnCalendar |
|--------|------------|
| stündlich | `*-*-* *:00:00` |
| täglich (z.B. 08:30) | `*-*-* 08:30:00` |
| wöchentlich (Mo, 08:30) | `Mon *-*-* 08:30:00` |

Wochentage: `Mon`, `Tue`, `Wed`, `Thu`, `Fri`, `Sat`, `Sun`

### Installation (User-Service)

```bash
# Dateien kopieren
cp csv2md.service csv2md.timer ~/.config/systemd/user/

# systemd neu laden
systemctl --user daemon-reload

# Timer aktivieren und starten
systemctl --user enable csv2md.timer
systemctl --user start csv2md.timer

# Status prüfen
systemctl --user list-timers csv2md.timer

# Logs anzeigen
journalctl --user -u csv2md.service
```

### Wichtige Hinweise

- User-Service wird in `~/.config/systemd/user/` installiert
- Skript muss mit absoluten Pfaden arbeiten
- Für URL-Inputs: `After=network-online.target` im Service
- Timer nutzt `Persistent=true` um verpasste Runs nachzuholen
- `logging`-Modus statt `print()` verwenden, damit Ausgaben im journal landen

## Fallstricke

1. **Interaktivität**: `input()` funktioniert nicht in systemd — systemd-Modus ist immer non-interaktiv
2. **Pfade**: Service-Datei muss absolute Pfade enthalten — Skript ermittelt diese via `Path(__file__).resolve()`
3. **Netzwerk**: systemd Service braucht `After=network-online.target` für URL-Inputs
4. **Logging**: stdout/stderr gehen an systemd journal → `logging`-Modul verwenden
5. **Cross-Platform**: systemd nur unter Linux verfügbar
6. **Python Version**: Python 3.11+ erforderlich
7. **venv**: Immer mit aktiviertem venv arbeiten (`.venv/` in `.gitignore`)
