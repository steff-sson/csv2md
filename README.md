# csv2md - CSV zu Markdown Konverter

Skript zur Extraktion einer CSV-Spalte und Export als Markdown-Datei. Unterstützt interaktiven und nicht-interaktiven Modus. Optionale systemd-Integration für regelmäßige Ausführung.

**Voraussetzung:** Python 3.11+, venv

```bash
python3.11 -m venv .venv
source .venv/bin/activate
```

## Lizenz

GNU General Public License v3.0 – siehe [LICENSE](https://www.gnu.org/licenses/gpl-3.0.html).

## Verwendung

```bash
csv2md.py [Optionen] [input] [output]
```

### Optionen

| Flag | Langform | Beschreibung |
|------|----------|--------------|
| `-i` | `--interactive` | Interaktiver Modus (fragt alles ab) |
| `-c` | `--column NAME` | Spaltenname (non-interaktiv, erforderlich ohne `-i`) |
| `-f` | `--force` | Output überschreiben ohne Nachfrage |
| `-d` | `--delimiter CHAR` | Trennzeichen: `auto`, `,`, `;`, `\t`, `tab` (default: `auto`) |
| `-e` | `--encoding NAME` | Zeichenkodierung (default: `utf-8`) |
| `-n` | `--no-verify` | SSL-Zertifikatsprüfung deaktivieren |
| `-h` | `--help` | Hilfe anzeigen |

### Exit-Codes

| Code | Bedeutung |
|------|-----------|
| 0 | Erfolg |
| 1 | CSV nicht gefunden / Output existiert ohne `-f` |
| 2 | Spalte nicht vorhanden |
| 3 | URL nicht erreichbar |
| 4 | SSL-Fehler |
| 5 | Leeres CSV |
| 6 | `-i` + `-c` gleichzeitig oder ungültiges Trennzeichen |
| 7 | Output-Verzeichnis fehlt |
| 8 | input/output fehlt im nicht-interaktiven Modus |

## Modi

### Interaktiv (`-i`) – fragt alles ab

```bash
python csv2md.py -i
```

1. **CSV-Quelle** – Dateipfad oder URL
2. **Trennzeichen** – auto / Komma / Semikolon / Tab
3. CSV laden & parsen
4. **Spalte wählen** – nummerierte Auswahl
5. **Ausgabe-Dateipfad**
6. Überschreiben? (falls existiert)
7. **systemd einrichten?**
   - Timer: stündlich / täglich (Uhrzeit) / wöchentlich (Wochentag + Uhrzeit)
   - **"Nur Dateien erstellen"** – `.service` + `.timer` im aktuellen Verzeichnis
   - **"Installieren"** – nach `~/.config/systemd/user/` kopieren + Timer aktivieren

CLI-Argumente können einzelne Schritte überspringen:

```bash
csv2md.py -i eingabe.csv                  # input vorgegeben, Rest interaktiv
csv2md.py -i -d "; "                      # delimiter vorgegeben
```

### Non-interaktiv (für systemd-Service)

```bash
python csv2md.py --column "Name" --force input.csv output.md
```

Läuft still durch – keine Rückfragen. Perfekt für systemd `ExecStart`.

## Markdown-Output

```markdown
# [Spaltenname]

* [Item 1]
* [Item 2]
* [Item 3]
...
```

- UTF-8 Encoding
- Keine Duplikate (case-sensitive)
- Leere Zellen werden übersprungen
- Original-Reihenfolge

## systemd-Integration

### Timer-Optionen

| Option | OnCalendar |
|--------|------------|
| stündlich | `*-*-* *:00:00` |
| täglich (08:30) | `*-*-* 08:30:00` |
| wöchentlich (Mo, 08:30) | `Mon *-*-* 08:30:00` |

### Installation (User-Service)

```bash
cp csv2md.service csv2md.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable csv2md.timer
systemctl --user start csv2md.timer
systemctl --user list-timers csv2md.timer
journalctl --user -u csv2md.service
```

### Wichtige Hinweise

- User-Service in `~/.config/systemd/user/`
- Service nutzt absolute Pfade
- Für URL-Inputs: `After=network-online.target`
- Timer nutzt `Persistent=true`
- `logging`-Modul statt `print()` im Service-Modus
