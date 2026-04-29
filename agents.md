# agents.md - Anleitung für AI-Agenten

## Projektübersicht

**csv2md** - Ein Python-Skript zur Konvertierung von CSV-Spalten in Markdown-Listen. Unterstützt interaktiven und nicht-interaktiven Modus mit optionaler systemd-Integration.

## Technologie

- **Sprache**: Python 3.11+
- **Abhängigkeiten**: Nur Standardbibliothek (csv, urllib, argparse, pathlib, logging, ssl, subprocess)
- **Lizenz**: GPL-3.0

## Projektstruktur

```
csv2md/
├── plan.md      # Projektplanung & Coding-Richtlinien
├── README.md    # Dokumentation (GPL-3.0)
├── agents.md    # Diese Datei
├── csv2md.py    # Hauptskript
└── .gitignore   # .venv/, __pycache__/, *.pyc
```

## Entwicklung

### Venv einrichten

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

### Coding Standards (siehe plan.md)

- Shebang: `#!/usr/bin/env python3`
- main()-Guard: `if __name__ == "__main__":`
- Alle Funktionen typisieren (Type Hints)
- f-strings, pathlib, logging
- UTF-8 encoding bei allen Dateioperationen
- Keine Kommentare (außer kurze Docstrings)
- `sys.exit(n)` für Exit-Codes

### Exit-Codes

| Code | Bedeutung |
|------|-----------|
| 0 | Erfolg |
| 1 | CSV nicht gefunden / nicht lesbar / Output existiert ohne `-f` |
| 2 | Spalte nicht vorhanden |
| 3 | URL nicht erreichbar |
| 4 | SSL-Verifikationsfehler |
| 5 | Leeres CSV |
| 6 | Gleichzeitig `-i` + `-c` oder ungültiges Trennzeichen |
| 7 | Output-Verzeichnis existiert nicht |
| 8 | input/output fehlt im nicht-interaktiven Modus |

## Testing

```bash
# Tests mit .tmp/ Verzeichnis
python3 csv2md.py -c "Name" -f .tmp/test.csv .tmp/output.md
python3 csv2md.py -i < .tmp/input.txt
python3 csv2md.py -h
```

## Tool-Nutzung

- **Bash**: Shell-Befehle ausführen
- **glob**: Dateien finden
- **grep**: In Dateien suchen
- **read**: Dateien lesen
- **write/edit**: Dateien ändern
- **question**: Benutzerfragen stellen
- **todowrite**: Aufgaben verfolgen

## Wichtige Regeln

- Vor Code-Änderungen: **immer plan.md lesen**
- Coding-Richtlinien aus plan.md befolgen
- Funktionen testen bevor committen
- `.tmp/` für Testdaten verwenden
