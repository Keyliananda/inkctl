# inkctl

`inkctl` ist eine Python-CLI für Inkscape-Workflows. Das Tool kombiniert direkte SVG-Bearbeitung mit `lxml` und den Aufruf der Inkscape-Kommandozeile, damit sich SVG-Dateien skriptbar erstellen, ändern und exportieren lassen.

Das Projekt ist sinnvoll, wenn du:

- SVGs automatisiert bearbeiten willst
- Inkscape-Funktionen aus Skripten oder anderen Tools ansteuern willst
- wiederkehrende Design- oder Produktionsschritte reproduzierbar machen willst
- SVG-Elemente gezielt per ID manipulieren oder entfernen willst

## Features

`inkctl` unterstützt aktuell unter anderem:

- SVG-Dateien analysieren
- neue SVG-Dateien erzeugen
- Rechtecke, Kreise und Ellipsen hinzufügen
- Text hinzufügen
- Ebenen anlegen und auflisten
- Füll- und Konturfarben ändern
- SVG-Elemente per ID entfernen
- Elemente in Inkscape per ID auswählen
- aktuell ausgewählte Element-IDs aus Inkscape auslesen
- inkctl-Extension für den Selektionsexport installieren
- maschinenlesbare CLI-Capabilities als JSON ausgeben
- JSON-Hilfe für einzelne Commands ausgeben
- rohe Inkscape-Actions ausführen
- SVG-Dateien nach PNG oder PDF exportieren

## Voraussetzungen

Für die Nutzung brauchst du:

- Inkscape 1.4 oder neuer
- Python 3.10 oder neuer
- ein System, auf dem der `inkscape`-Befehl verfügbar ist

Wichtig:

- SVG-Manipulationen wie `remove-elements`, `change-fill` oder `create-rect` arbeiten direkt auf der SVG-Datei.
- Export- und Action-Befehle nutzen zusätzlich die installierte Inkscape-CLI.

## Installation Für Nutzer

Der einfachste Weg für normale Nutzer ist `pipx`. Damit wird `inkctl` isoliert installiert und danach systemweit als Befehl verfügbar.

### 1. pipx installieren

macOS:

```bash
brew install pipx
pipx ensurepath
```

Linux:

```bash
python3 -m pip install --user pipx
python3 -m pipx ensurepath
```

Danach das Terminal neu starten, falls `pipx` oder später `inkctl` noch nicht gefunden wird.

### 2. Inkscape installieren

Installiere Inkscape separat und prüfe danach:

```bash
inkscape --version
```

Wenn der Befehl nicht gefunden wird, ist Inkscape zwar eventuell installiert, aber noch nicht im `PATH`.

### 3. `inkctl` aus Git installieren

Sobald dein Repository online ist, kann die Installation so aussehen:

```bash
pipx install git+https://github.com/Keyliananda/inkctl.git
```

Wenn sich Owner oder Repository-Name ändern, passe die URL entsprechend an.

### 4. Installation prüfen

```bash
inkctl --help
inkctl version
```

## Installation Für Lokale Entwicklung

Wenn du lokal am Projekt arbeitest:

```bash
git clone https://github.com/Keyliananda/inkctl.git
cd inkctl
./setup.sh
./inkctl --help
```

`./setup.sh` erledigt dabei:

- lokales `venv` anlegen
- `pip` aktualisieren
- das Projekt per `pip install -e .` im Editable-Modus installieren

Der Wrapper `./inkctl` nutzt automatisch das lokale virtuelle Environment.

## Schnellstart

### Hilfe anzeigen

```bash
inkctl --help
```

### Maschinenlesbare Capabilities ausgeben

```bash
inkctl capabilities --json
```

### JSON-Hilfe für einen einzelnen Command

```bash
inkctl get-selection --help --json
```

### SVG-Informationen anzeigen

```bash
inkctl info --file input.svg
```

### Neue SVG-Datei anlegen

```bash
inkctl new --width 210mm --height 297mm --output new.svg
```

### Rechteck erstellen

```bash
inkctl create-rect \
  --x 10 \
  --y 10 \
  --width 100 \
  --height 50 \
  --fill "#4A90D9" \
  --file output.svg
```

### Füllfarbe eines Elements ändern

```bash
inkctl change-fill "#FF0000" --element-id my-rect --file input.svg
```

### Alle Elemente eines Typs ändern

```bash
inkctl change-stroke "#222222" --width 2 --tag rect --file input.svg
```

### Ebenen auflisten

```bash
inkctl list-layers --file input.svg
```

### PNG exportieren

```bash
inkctl export --file input.svg --output output.png --format png
```

## `remove-elements`

Mit `remove-elements` kannst du SVG-Elemente gezielt anhand ihrer IDs entfernen.

### Syntax

```bash
inkctl remove-elements --file <svg-path> --ids id1,id2,id3 [--backup] [--dry-run]
```

### Parameter

- `--file`: Pfad zur SVG-Datei
- `--ids`: kommaseparierte Liste von Element-IDs
- `--backup`: erstellt vor dem Schreiben eine `.bak`-Datei
- `--dry-run`: zeigt nur an, was entfernt würde, ohne die SVG zu ändern

### Beispiel: Vorschau

```bash
inkctl remove-elements \
  --file floorplan.svg \
  --ids ellipse790,circle790,ellipse791 \
  --dry-run
```

### Beispiel: Wirklich entfernen und Backup anlegen

```bash
inkctl remove-elements \
  --file floorplan.svg \
  --ids ellipse790,circle790,ellipse791 \
  --backup
```

### Beispielantwort

```json
{
  "removed": ["ellipse790", "circle790"],
  "not_found": ["missing123"],
  "total_removed": 2,
  "dry_run": false,
  "backup": "/path/to/floorplan.svg.bak"
}
```

## `select-elements`

Mit `select-elements` öffnest du Inkscape mit einer Datei und einer vorausgewählten Menge an Element-IDs.

### Syntax

```bash
inkctl select-elements --file <svg-path> --ids id1,id2,id3
```

### Beispiel

```bash
inkctl select-elements \
  --file floorplan.svg \
  --ids ellipse790,circle790,ellipse791
```

## `install-extension`

Damit `get-selection` funktioniert, muss die inkctl-Inkscape-Extension installiert sein.

### Syntax

```bash
inkctl install-extension
```

Der Befehl kopiert `export_selection.py` und `export_selection.inx` in den systemabhängigen Inkscape-Extensions-Ordner und fordert danach zu einem Neustart von Inkscape auf.

## `get-selection`

`get-selection` liest die zuletzt von der Inkscape-Extension an `inkctl` gesendete Auswahl aus `/tmp/inkscape_selection.json`.

### Syntax

```bash
inkctl get-selection --file <svg-path>
```

### Workflow

1. `inkctl install-extension`
2. Inkscape neu starten
3. In Inkscape Elemente auswählen
4. In Inkscape `Extensions > inkctl > Send Selection to AI` ausführen
5. `inkctl get-selection --file <svg-path>`

### Beispielantwort

```json
{
  "file": "/Users/name/projects/floorplan.svg",
  "selected_ids": ["ellipse790", "circle790"],
  "count": 2
}
```

## `capabilities`

`capabilities` gibt die verfügbaren Commands maschinenlesbar als JSON aus. Das ist speziell für Agenten und andere Tools gedacht, die erst verstehen müssen, welche Befehle `inkctl` unterstützt.

### Syntax

```bash
inkctl capabilities --json
```

### Beispielantwort

```json
{
  "program": "inkctl",
  "description": "Inkscape CLI Addon - SVG-Dateien erstellen und bearbeiten",
  "usage": "usage: inkctl [-h] {...}",
  "commands": [
    {
      "name": "get-selection",
      "summary": "Aktuelle Inkscape-Selektion auslesen",
      "usage": "usage: inkctl get-selection [-h] --file FILE",
      "arguments": [
        {
          "name": "file",
          "kind": "option",
          "option_strings": ["--file"],
          "required": true,
          "type": "string"
        }
      ]
    }
  ]
}
```

## JSON-Hilfe pro Command

Mit `--help --json` lässt sich die Hilfe eines einzelnen Commands in strukturierter Form ausgeben.

### Syntax

```bash
inkctl <command> --help --json
```

### Beispiel

```bash
inkctl get-selection --help --json
```

## Befehlsübersicht

Aktuell verfügbare Kommandos:

- `info`
- `new`
- `export`
- `version`
- `actions`
- `create-rect`
- `create-circle`
- `create-ellipse`
- `add-text`
- `add-layer`
- `list-layers`
- `change-fill`
- `change-stroke`
- `remove-elements`
- `select-elements`
- `get-selection`
- `install-extension`
- `capabilities`

Hilfe zu einem einzelnen Befehl bekommst du jeweils mit:

```bash
inkctl <command> --help
```

Zum Beispiel:

```bash
inkctl remove-elements --help
```

## Typische Workflows

### 1. SVG prüfen, bearbeiten und exportieren

```bash
inkctl info --file plan.svg
inkctl remove-elements --file plan.svg --ids debug1,debug2 --backup
inkctl export --file plan.svg --output plan.png --format png
```

### 2. SVG programmatisch aufbauen

```bash
inkctl new --width 800px --height 600px --output canvas.svg
inkctl create-rect --x 20 --y 20 --width 200 --height 100 --file canvas.svg
inkctl create-circle --cx 300 --cy 120 --r 40 --file canvas.svg
```

### 3. Rohe Inkscape-Actions ausführen

```bash
inkctl actions "export-filename:out.png; export-do" --file input.svg
```

## Projektstruktur

```text
.
├── commands/          CLI-Kommandos
├── inkscape_cli/      SVG-Logik und Inkscape-Integration
├── inkctl.py          Python-Einstiegspunkt für den CLI-Befehl
├── inkctl             lokaler Wrapper für das Projekt-venv
├── pyproject.toml     Paketdefinition und Console-Script
├── requirements.txt   minimale Abhängigkeiten
└── setup.sh           lokales Bootstrap-Script
```

## Entwicklung

Wenn du lokal weiterentwickeln willst:

```bash
source venv/bin/activate
python -m py_compile inkctl.py commands/*.py inkscape_cli/*.py
```

Da das Projekt editable installiert wird, sind Änderungen im Code sofort über `inkctl` beziehungsweise `./inkctl` verfügbar.

## Troubleshooting

### `inkctl: command not found`

Wahrscheinlich ist `pipx` nicht im `PATH` oder das Terminal wurde nach `pipx ensurepath` noch nicht neu gestartet.

Prüfe:

```bash
pipx list
```

### `inkscape` wird nicht gefunden

Prüfe:

```bash
inkscape --version
```

Falls das fehlschlägt, ist Inkscape nicht installiert oder nicht im `PATH`.

### `ModuleNotFoundError: No module named 'lxml'`

Dann wurde vermutlich `python inkctl.py ...` mit einer falschen Python-Umgebung gestartet.

Nutze stattdessen:

```bash
inkctl --help
```

oder lokal im Projekt:

```bash
./inkctl --help
```

### `--dry-run` erstellt trotzdem ein Backup

Das ist beabsichtigt, wenn `--backup` gesetzt ist. So kannst du den geplanten Lauf inklusive Sicherungsdatei testen.

## Namensvorschlag Für Das Repository

Für GitHub ist `inkctl` der beste Name:

- kurz
- merkbar
- gut als CLI-Befehl wiedererkennbar

Wenn `inkctl` später doch unpassend wird, sind gute Alternativen:

- `inkctl-for-inkscape`
- `inkscape-inkctl`

`cli-for-inkscape` würde ich nicht empfehlen, weil der Name sehr generisch ist.

## Lizenz

Empfehlung für dieses Projekt: `MIT`.

Lege dafür im Repository-Root eine Datei `LICENSE` an oder wähle beim Erstellen des GitHub-Repositories direkt `MIT License` aus.
