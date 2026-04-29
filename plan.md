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

## Verwendung

```bash
csv2md.py [Optionen] <input> <output>
```

### Optionen

| Flag | Langform | Beschreibung |
|------|----------|--------------|
| `-i` | `--interactive` | Interaktiver Modus (Fragen stellen) |
| `-c` | `--column NAME` | Spaltenname (non-interaktiv) |
| `-f` | `--force` | Output überschreiben ohne Nachfrage |
| `-d` | `--delimiter CHAR` | CSV-Trennzeichen: `,` `;` `\t` `auto` (default: `auto`) |
| `-e` | `--encoding NAME` | Zeichenkodierung (default: `utf-8`) |
| `-n` | `--no-verify` | SSL-Zertifikatsprüfung deaktivieren |
| `-h` | `--help` | Hilfe anzeigen |

### Argumente

- **input**: URL (https://...) oder Dateipfad zur CSV-Datei
- **output**: Dateipfad für die Markdown-Ausgabe

## Modi

### Interaktiver Modus (`-i`)

1. Liest CSV (URL oder Datei)
2. **Fragt nach CSV-Delimiter**: Komma / Semikolon / Tab / Auto-Erkennung
3. Zeigt verfügbare Spalten
4. Fragt nach gewünschter Spalte (nummerierte Auswahl)
5. Fragt nach Überschreiben falls Output existiert
6. Fragt: "Soll systemd aufgesetzt werden?"
   - Falls Ja:
     - Timer-Optionen: stündlich / täglich / wöchentlich
     - Bei täglich: Uhrzeit abfragen (HH:MM)
     - Bei wöchentlich: Wochentag + Uhrzeit abfragen
     - **Fragt: "Nur Dateien erstellen" oder "Sofort installieren"?**
       - "Dateien erstellen": `.service` und `.timer` im aktuellen Verzeichnis
       - "Installieren": Dateien nach `~/.config/systemd/user/` kopieren + Timer aktivieren

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

- Keine Duplikate (automatisch dedupliziert)
- Leere Zellen werden übersprungen
- Items werden in Original-Reihenfolge ausgegeben

## systemd-Integration

### Erstellte Dateien

- `csv2md.service` - Service-Datei zum Starten des Skripts
- `csv2md.timer` - Timer-Datei für regelmäßige Ausführung

### Timer-Optionen

| Option | Beschreibung |
|--------|--------------|
| stündlich | Alle 60 Minuten (OnCalendar=*-*-* *:00:00) |
| täglich | Tägliche Ausführung zur angegebenen Uhrzeit |
| wöchentlich | Wöchentlich am angegebenen Wochentag + Uhrzeit |

### Installation (User-Service)

```bash
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

## CVS-Verarbeitung

### Encoding

- Default: **UTF-8**
- Optionales BOM-Handling für Windows-Kompatibilität

### Delimiter

| Wert | Bedeutung |
|------|-----------|
| `,` | Komma (Standard-CSV) |
| `;` | Semikolon (deutsches CSV) |
| `\t` | Tabstopp (TSV) |
| `auto` | Automatische Erkennung via `csv.Sniffer` |

### Fehlerbehandlung

- CSV nicht gefunden → Fehlermeldung + Exit 1
- Spalte nicht vorhanden → Fehlermeldung + Exit 2
- URL nicht erreichbar → Timeout nach 30s + Exit 3
- SSL-Verifikationsfehler → Hinweis auf `--no-verify` + Exit 4
- Leere CSV → Fehlermeldung + Exit 5

## Netzwerk (URL-Input)

- Default-Timeout: 30 Sekunden
- SSL-Verifikation: standardmäßig aktiviert
- `--no-verify` deaktiviert SSL-Prüfung (für self-signed Zertifikate)
- HTTP Redirects werden gefolgt (max. 5)

## Fallstricke

1. **Interaktivität**: `input()` funktioniert nicht in systemd. Nur `-i` für interaktiven Modus.
2. **Pfade**: Immer absolute Pfade verwenden.
3. **Netzwerk**: systemd Service muss auf Netzwerk-Verfügbarkeit warten.
4. **Logging**: stdout/stderr gehen an systemd journal.
5. **Cross-Platform**: systemd nur unter Linux verfügbar.
6. **Python Version**: Python 3.11+ erforderlich.
7. **venv**: Immer mit aktiviertem venv arbeiten.
