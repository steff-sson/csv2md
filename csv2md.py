#!/usr/bin/env python3
"""csv2md - CSV to Markdown converter."""

import argparse
import csv
import io
import logging
import ssl
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.request


logger = logging.getLogger(__name__)

DELIMITER_MAP: dict[str, str | None] = {
    ",": ",",
    ";": ";",
    "\\t": "\t",
    "tab": "\t",
    "auto": None,
}

WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

ONCALENDAR_STUNDLICH = "*-*-* *:00:00"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CSV to Markdown converter. Extrahiert eine CSV-Spalte und exportiert als Markdown."
    )
    parser.add_argument("-i", "--interactive", action="store_true", help="Interaktiver Modus")
    parser.add_argument("-c", "--column", type=str, default=None, help="Spaltenname (non-interaktiv)")
    parser.add_argument("-f", "--force", action="store_true", help="Output überschreiben ohne Nachfrage")
    parser.add_argument("-d", "--delimiter", type=str, default="auto", help="CSV-Trennzeichen: auto, ,, ;, \\\\t, tab")
    parser.add_argument("-e", "--encoding", type=str, default="utf-8", help="Zeichenkodierung (default: utf-8)")
    parser.add_argument("-n", "--no-verify", action="store_true", help="SSL-Zertifikatsprüfung deaktivieren")
    parser.add_argument("input", type=str, help="CSV-Datei (URL oder Dateipfad)")
    parser.add_argument("output", type=str, help="Markdown-Ausgabedatei")
    return parser.parse_args(argv)


def setup_logging(verbose: bool = False) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )


def detect_delimiter(raw: str) -> str:
    try:
        dialect = csv.Sniffer().sniff(raw[:4096])
        return dialect.delimiter
    except csv.Error:
        logger.warning("Delimiter could not be detected, falling back to comma")
        return ","


def read_csv_from_url(url: str, delimiter: str | None, encoding: str, no_verify: bool) -> list[dict[str, str]]:
    ctx = ssl.create_default_context()
    if no_verify:
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
    try:
        resp = urllib.request.urlopen(url, timeout=30, context=ctx)
        raw = resp.read().decode(encoding)
    except urllib.error.URLError as e:
        logger.error("URL not reachable: %s", e)
        sys.exit(3)
    except ValueError as e:
        logger.error("Invalid URL: %s", e)
        sys.exit(3)

    if delimiter is None:
        delimiter = detect_delimiter(raw)

    reader = csv.DictReader(io.StringIO(raw), delimiter=delimiter)
    rows = list(reader)

    if len(rows) == 0:
        logger.error("CSV is empty")
        sys.exit(5)

    return rows


def read_csv_from_path(path: Path, delimiter: str | None, encoding: str) -> list[dict[str, str]]:
    if not path.exists():
        logger.error("File not found: %s", path)
        sys.exit(1)

    try:
        raw = path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        logger.error("Cannot decode file with encoding %s: %s", encoding, path)
        sys.exit(1)

    if delimiter is None:
        delimiter = detect_delimiter(raw)

    reader = csv.DictReader(io.StringIO(raw), delimiter=delimiter)
    rows = list(reader)

    if len(rows) == 0:
        logger.error("CSV is empty")
        sys.exit(5)

    return rows


def load_csv(input_str: str, delimiter: str | None, encoding: str, no_verify: bool) -> list[dict[str, str]]:
    if input_str.startswith(("https://", "http://")):
        return read_csv_from_url(input_str, delimiter, encoding, no_verify)
    return read_csv_from_path(Path(input_str), delimiter, encoding)


def convert_to_markdown(rows: list[dict[str, str]], column: str) -> str:
    seen = set()
    items: list[str] = []
    for row in rows:
        val = row.get(column)
        if val is None:
            logger.error("Column '%s' not found in CSV header", column)
            logger.error("Available columns: %s", ", ".join(rows[0].keys()))
            sys.exit(2)
        stripped = val.strip()
        if stripped and stripped not in seen:
            seen.add(stripped)
            items.append(stripped)

    header = f"# {column}\n"
    body = "\n".join(f"* {item}" for item in items)
    return f"{header}\n{body}\n"


def ask_choice(prompt: str, options: list[str]) -> int:
    print(prompt)
    for i, opt in enumerate(options, 1):
        print(f"  {i}) {opt}")
    while True:
        try:
            choice = int(input("> ").strip())
            if 1 <= choice <= len(options):
                return choice
            print(f"Bitte eine Zahl zwischen 1 und {len(options)} eingeben.")
        except ValueError:
            print("Bitte eine gültige Zahl eingeben.")


def ask_yes_no(prompt: str) -> bool:
    while True:
        answer = input(f"{prompt} (j/n): ").strip().lower()
        if answer in ("j", "ja", "y", "yes"):
            return True
        if answer in ("n", "nein", "no"):
            return False
        print("Bitte 'j' oder 'n' eingeben.")


def ask_time(prompt: str) -> str:
    while True:
        t = input(f"{prompt} (HH:MM): ").strip()
        try:
            parts = t.split(":")
            hour = int(parts[0])
            minute = int(parts[1])
            if 0 <= hour <= 23 and 0 <= minute <= 59:
                return f"{hour:02d}:{minute:02d}"
            print("Bitte eine gültige Uhrzeit (HH:MM) eingeben.")
        except (ValueError, IndexError):
            print("Bitte das Format HH:MM verwenden.")


def ask_weekday() -> str:
    idx = ask_choice("Wochentag wählen:", WEEKDAYS)
    return WEEKDAYS[idx - 1]


def generate_service_content(
    python_path: str,
    script_path: str,
    working_dir: str,
    column: str,
    delimiter: str,
    input_str: str,
    output_str: str,
) -> str:
    delim_flag = "" if delimiter == "auto" else f"--delimiter {delimiter} "
    exec_start = (
        f"{python_path} {script_path} "
        f"--column \"{column}\" "
        f"{delim_flag}"
        f"--force \"{input_str}\" \"{output_str}\""
    )
    return (
        "[Unit]\n"
        "Description=csv2md - CSV to Markdown Converter\n"
        "After=network-online.target\n"
        "Wants=network-online.target\n"
        "\n"
        "[Service]\n"
        "Type=oneshot\n"
        f"ExecStart={exec_start}\n"
        f"WorkingDirectory={working_dir}\n"
        "\n"
        "[Install]\n"
        "WantedBy=default.target\n"
    )


def generate_timer_content(timer_option: str, time_str: str | None, weekday: str | None) -> str:
    if timer_option == "stündlich":
        oncalendar = ONCALENDAR_STUNDLICH
    elif timer_option == "täglich" and time_str:
        oncalendar = f"*-*-* {time_str}:00"
    elif timer_option == "wöchentlich" and time_str and weekday:
        oncalendar = f"{weekday} *-*-* {time_str}:00"
    else:
        oncalendar = ONCALENDAR_STUNDLICH

    return (
        "[Unit]\n"
        "Description=csv2md Timer - regelmässige CSV-Konvertierung\n"
        "\n"
        "[Timer]\n"
        f"OnCalendar={oncalendar}\n"
        "Persistent=true\n"
        "\n"
        "[Install]\n"
        "WantedBy=default.target\n"
    )


def write_systemd_files(
    service_content: str,
    timer_content: str,
    output_dir: Path,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    service_path = output_dir / "csv2md.service"
    timer_path = output_dir / "csv2md.timer"
    service_path.write_text(service_content, encoding="utf-8")
    timer_path.write_text(timer_content, encoding="utf-8")
    print(f"  -> {service_path}")
    print(f"  -> {timer_path}")


def install_systemd(service_content: str, timer_content: str) -> None:
    user_dir = Path.home() / ".config" / "systemd" / "user"
    write_systemd_files(service_content, timer_content, user_dir)
    try:
        subprocess.run(["systemctl", "--user", "daemon-reload"], check=True)
        subprocess.run(["systemctl", "--user", "enable", "csv2md.timer"], check=True)
        subprocess.run(["systemctl", "--user", "start", "csv2md.timer"], check=True)
        print("systemd-Timer wurde installiert und gestartet.")
    except subprocess.CalledProcessError as e:
        logger.error("systemd installation failed: %s", e)
        sys.exit(1)


def handle_systemd_setup(
    args: argparse.Namespace,
    column: str,
    delimiter_val: str,
) -> None:
    print("\n--- systemd Einrichtung ---")

    timer_options = ["stündlich", "täglich", "wöchentlich"]
    timer_idx = ask_choice("Timer-Option wählen:", timer_options)
    timer_option = timer_options[timer_idx - 1]

    time_str: str | None = None
    weekday: str | None = None

    if timer_option == "täglich":
        time_str = ask_time("Uhrzeit für tägliche Ausführung")
    elif timer_option == "wöchentlich":
        weekday = ask_weekday()
        time_str = ask_time(f"Uhrzeit für wöchentliche Ausführung ({weekday})")

    python_path = sys.executable
    script_path = str(Path(__file__).resolve())
    working_dir = str(Path(__file__).resolve().parent)

    service_content = generate_service_content(
        python_path=python_path,
        script_path=script_path,
        working_dir=working_dir,
        column=column,
        delimiter=delimiter_val,
        input_str=str(Path(args.input).resolve()) if not args.input.startswith(("https://", "http://")) else args.input,
        output_str=str(Path(args.output).resolve()),
    )
    timer_content = generate_timer_content(timer_option, time_str, weekday)

    install_mode = ask_yes_no("systemd installieren? (sonst nur Dateien erstellen)")
    if install_mode:
        install_systemd(service_content, timer_content)
    else:
        current_dir = Path.cwd()
        print(f"Erstelle systemd-Dateien in: {current_dir}")
        write_systemd_files(service_content, timer_content, current_dir)
        print("\nZur manuellen Installation:")
        print(f"  cp {current_dir}/csv2md.service {current_dir}/csv2md.timer ~/.config/systemd/user/")
        print("  systemctl --user daemon-reload")
        print("  systemctl --user enable csv2md.timer")
        print("  systemctl --user start csv2md.timer")


def interactive_mode(args: argparse.Namespace) -> int:
    print("=== csv2md - Interaktiver Modus ===\n")

    delimiter_options = ["auto", ",", ";", "tab"]
    delim_idx = ask_choice("CSV-Trennzeichen wählen:", delimiter_options)
    chosen_delimiter = delimiter_options[delim_idx - 1]
    delim_value = DELIMITER_MAP[chosen_delimiter]

    rows = load_csv(args.input, delim_value, args.encoding, args.no_verify)

    if len(rows) == 0:
        logger.error("CSV is empty")
        return 5

    headers = list(rows[0].keys())
    col_idx = ask_choice("Spalte wählen:", headers)
    column = headers[col_idx - 1]

    output_path = Path(args.output)
    if output_path.exists() and not args.force:
        if not ask_yes_no(f"Output existiert bereits. Überschreiben?"):
            print("Abgebrochen.")
            return 0

    markdown = convert_to_markdown(rows, column)
    output_path.write_text(markdown, encoding="utf-8")
    print(f"Markdown geschrieben: {output_path}")

    if ask_yes_no("Soll systemd aufgesetzt werden?"):
        handle_systemd_setup(args, column, chosen_delimiter)

    return 0


def non_interactive_mode(args: argparse.Namespace) -> int:
    if not args.column:
        logger.error("--column ist im nicht-interaktiven Modus erforderlich")
        return 6

    delim_value = DELIMITER_MAP.get(args.delimiter)
    if delim_value is None and args.delimiter != "auto":
        logger.error("Ungültiges Trennzeichen: %s", args.delimiter)
        logger.error("Erlaubt: auto, ,, ;, \\\\t")
        return 6

    rows = load_csv(args.input, delim_value, args.encoding, args.no_verify)

    if len(rows) == 0:
        logger.error("CSV is empty")
        return 5

    if args.column not in rows[0]:
        logger.error("Spalte '%s' nicht gefunden", args.column)
        logger.error("Verfügbare Spalten: %s", ", ".join(rows[0].keys()))
        return 2

    output_path = Path(args.output)
    if output_path.exists() and not args.force:
        logger.error("Output existiert bereits: %s (--force zum Überschreiben)", args.output)
        return 1

    if not output_path.parent.exists():
        logger.error("Output-Verzeichnis existiert nicht: %s", output_path.parent)
        return 7

    markdown = convert_to_markdown(rows, args.column)
    output_path.write_text(markdown, encoding="utf-8")
    logger.info("Markdown geschrieben: %s", output_path)

    return 0


def main() -> int:
    args = parse_args()
    setup_logging(verbose=False)

    output_path = Path(args.output)
    if not output_path.parent.exists():
        logger.error("Output-Verzeichnis existiert nicht: %s", output_path.parent)
        return 7

    if args.interactive and args.column:
        logger.error("-i und -c schliessen sich gegenseitig aus")
        return 6

    if args.delimiter not in DELIMITER_MAP:
        logger.error("Ungültiges Trennzeichen: %s", args.delimiter)
        logger.error("Erlaubt: auto, ,, ;, \\\\t, tab")
        return 6

    if args.interactive:
        return interactive_mode(args)
    return non_interactive_mode(args)


if __name__ == "__main__":
    sys.exit(main())
