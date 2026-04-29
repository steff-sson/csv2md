# agents.md - Anleitung für AI-Agenten

## Projektübersicht

**csv2md** - Ein Python-Skript zur Konvertierung von CSV-Spalten in Markdown-Listen. Unterstützt interaktiven und nicht-interaktiven Modus mit optionaler systemd-Integration.

## Technologie

- **Sprache**: Python 3
- **Abhängigkeiten**: Standardbibliothek (csv, urllib, argparse)
- **Lizenz**: GPL-3.0

## Projektstruktur

```
csv2md/
├── plan.md      # Projektplanung
├── README.md    # Dokumentation (GPL-3.0)
├── agents.md    # Diese Datei
└── csv2md.py    # Hauptskript
```

## Entwicklung

### Coding Standards

- Python-Skripte ohne zusätzliche Abhängigkeiten schreiben
- Standardbibliothek bevorzugen
- Keine unnötigen Kommentare hinzufügen
- PEP 8 Konventionen folgen

### Commits

- Commits erstellen mit: `git add <files> && git commit -m "Nachricht"`
- PRs erstellen mit: `gh pr create --title "Titel" --body "Beschreibung"`

## Testing

- Manuelles Testen mit Beispieldaten
- Interaktiven Modus (`-i`) testen
- systemd-Integration manuell verifizieren

## Tool-Nutzung

- **Bash**: Shell-Befehle ausführen
- **glob**: Dateien finden
- **grep**: In Dateien suchen
- **read**: Dateien lesen
- **write/edit**: Dateien ändern
- **question**: Benutzerfragen stellen
- **todowrite**: Aufgaben verfolgen