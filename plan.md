# csv2md - CSV zu Markdown Konverter

## Übersicht

Skript zur Extraktion einer CSV-Spalte und Export als Markdown-Datei. Unterstützt interaktiven und nicht-interaktiven Modus. Optionale systemd-Integration für regelmäßige Ausführung.

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
| `-h` | `--help` | Hilfe anzeigen |

### Argumente

- **input**: URL (https://...) oder Dateipfad zur CSV-Datei
- **output**: Dateipfad für die Markdown-Ausgabe

## Modi

### Interaktiver Modus (`-i`)

1. Liest CSV (URL oder Datei)
2. Zeigt verfügbare Spalten
3. Fragt nach gewünschter Spalte (nummerierte Auswahl)
4. Fragt nach Überschreiben falls Output existiert
5. Fragt: "Soll systemd aufgesetzt werden?"
   - Falls Ja:
     - Timer-Optionen: stündlich / täglich / wöchentlich
     - Bei täglich: Uhrzeit abfragen (HH:MM)
     - Bei wöchentlich: Wochentag + Uhrzeit abfragen
     - Erstellt `.service` und `.timer` Dateien
     - Gibt Installations-Anleitung aus

### Nicht-interaktiver Modus (systemd)

```bash
./csv2md.py --column "Spaltenname" --force <input> <output>
```

## Markdown-Output

```markdown
# [Spaltenname]

* [Item 1]
* [Item 2]
* [Item 3]
...
```

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

## Fallstricke

1. **Interaktivität**: `input()` funktioniert nicht in systemd. Nur `-i` für interaktiven Modus.
2. **Pfade**: Immer absolute Pfade verwenden.
3. **Netzwerk**: systemd Service muss auf Netzwerk-Verfügbarkeit warten.
4. **Logging**: stdout/stderr gehen an systemd journal.
5. **Timer-Accuracy**: `OnCalendar` ist nicht exakt, Timer können leicht verzögert sein.