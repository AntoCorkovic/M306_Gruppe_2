# Energieagentur Bünzli

## Beschreibung
Dieses Projekt bietet eine Softwarelösung zur Analyse und Visualisierung von Energieverbrauchsdaten. Es ermöglicht das Einlesen von SDAT- und ESL-Dateien, die Umrechnung von Verbrauchswerten in Zählerstände und die Darstellung der Daten in verschiedenen Formaten.

## Voraussetzungen
- Python 3.7 oder höher
- pip (Python Package Installer)

## Installation
1. Navigieren Sie in das Projektverzeichnis:
   ```
   cd M306_Gruppe_2-main
   ```
2. Installieren Sie die erforderlichen Pakete:
   ```
   pip install -r requirements.txt
   ```

## Verwendung
1. Starten Sie die Anwendung:
   ```
   python app.py
   ```
2. Öffnen Sie einen Webbrowser und navigieren Sie zu:
   ```
   http://127.0.0.1:5000/chart
   ```

## Funktionen
- Einlesen von SDAT-Dateien
- Einlesen von ESL-Dateien
- Umrechnung von Verbrauchswerten in Zählerstände
- Visualisierung der Daten in einem Verbrauchsdiagramm
- Visualisierung der Daten in einem Zählerstanddiagramm
- Export der Daten als CSV und JSON
- Übermittlung der Daten via HTTP POST-Request an einen Server

## Zusätzliche Features (experimentell)
- Drag-and-Drop-Funktion zum Hochladen weiterer Daten
- Diagramm mit täglichem Durchschnittsverbrauch und -einspeisung über den ausgewählten Zeitraum


## Entwicklung

### Tests ausführen

Um die Tests für dieses Projekt auszuführen, folgen Sie bitte diesen Schritten:

1. Stellen Sie sicher, dass Sie sich im Hauptverzeichnis des Projekts befinden.

2. Führen Sie den folgenden Befehl aus, um alle Tests zu starten:
   ```
   pytest tests/
   ```

#### Wichtiger Hinweis zu Importpfaden:

- Für den GitHub Workflow wurden die Importpfade in den Testdateien angepasst, indem das Präfix `src.` entfernt wurde.
- Wenn Sie die Tests lokal ausführen möchten, müssen Sie möglicherweise das `src.`-Präfix in den Importanweisungen der Testdateien wieder hinzufügen.

Beispiel für eine lokale Testdatei:
```python
from src.models.counterstands import Counterstands, TimePeriod, ValueRow
from src.parser import Parser
```

Beispiel für die GitHub Workflow-Version:
```python
from models.counterstands import Counterstands, TimePeriod, ValueRow
from parser import Parser
```

Stellen Sie sicher, dass Sie die Importpfade entsprechend anpassen, bevor Sie die Tests in Ihrer lokalen Umgebung ausführen.
