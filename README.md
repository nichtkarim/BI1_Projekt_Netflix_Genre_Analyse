
# Assoziationsanalyse mit Python

Dieses Projekt führt eine Assoziationsanalyse basierend auf häufigen Itemsets und Assoziationsregeln durch. Es beinhaltet die Berechnung von Support, Konfidenz und Lift sowie die Visualisierung der Ergebnisse.

## Inhaltsverzeichnis
- [Installation](#installation)
- [Voraussetzungen](#voraussetzungen)
- [Dateistruktur](#dateistruktur)
- [Funktionen](#funktionen)
- [Ergebnisse](#ergebnisse)
- [Visualisierungen](#visualisierungen)
- [Kontakt](#kontakt)

## Installation

1. Klone das Repository:
   ```bash
   git clone https://github.com/nichtkarim/BI1_Projekt_Netflix_Genre_Analyse/blob/d2bc9ad1dc587ab1d245758dde559f6589f2c5c1/
   ```
2. Wechsel in das Verzeichnis:
   ```bash
   cd /BI1_Projekt_Netflix_Genre_Analyse
   ```
3. Erstelle und aktiviere eine virtuelle Umgebung(Optional):
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   .venv\Scripts\activate     # Windows
   ```
4. Installiere die Abhängigkeiten:
   ```bash
   pip install -r requirements.txt
   ```

## Voraussetzungen

- Python 3.7 oder höher
- Folgende Python-Bibliotheken:
  - pandas
  - matplotlib
  - seaborn
  - networkx


    
## Dateistruktur

```plaintext
BI1_Projekt_Netflix_Genre_Analyse/
├── .venv/                     # Virtuelle Umgebung (optional)
├── Daten/
│   ├── Ergebnisse/            # Ordner für generierte Ergebnisse
│   └── Netflix_Bereinigt.csv  # Eingabedaten
├── Assoziationsanalyse.py     # Hauptskript
├── README.md                  # Projektbeschreibung
└── requirements.txt           # Abhängigkeiten
```

## Funktionen

### Hauptfunktionen

- **Datenvorbereitung:** 
  Lädt die bereinigten Eingabedaten und entfernt unnötige Spalten.
- **Berechnung von Itemsets:**
  Identifiziert häufige Itemsets basierend auf einem Mindest-Support.
- **Generierung von Assoziationsregeln:**
  Erstellt Regeln mit Mindest-Konfidenz, einschließlich Regeln höheren Grades.
- **Visualisierungen:**
  - Balkendiagramme der häufigsten Itemsets.
  - Visualisierung der Verteilung einzelner Items.
  - Heatmaps für Metriken wie Lift, Leverage und Conviction.
  - Scatterplots für Support, Konfidenz und Lift.

## Eingabedaten

- **Dateiname:** `Netflix_Bereinigt.csv`
- **Format:** CSV mit den folgenden Spalten:
  - `title`: Titel des Films oder der Serie.
  - `type`: Typ, z. B. `movie` oder `series`.
  - `releaseYear`: Veröffentlichungsjahr.
  - Über 35 Spalten, die Genres repräsentieren (binarisiert, 1 = Genre zutreffend, 0 = nicht zutreffend).

### Beispieldaten
1. **Titel:** The Fifth Element
   - Typ: movie
   - Veröffentlichungsjahr: 1997
   - Genres: Action, Adventure, Sci-Fi.

2. **Titel:** Kill Bill: Vol. 1
   - Typ: movie
   - Veröffentlichungsjahr: 2003
   - Genres: Action, Crime, Thriller.

3. **Titel:** Jarhead
   - Typ: movie
   - Veröffentlichungsjahr: 2005
   - Genres: Biography, Drama, War.

4. **Titel:** Unforgiven
   - Typ: movie
   - Veröffentlichungsjahr: 1992
   - Genres: Drama, Western.

5. **Titel:** Eternal Sunshine of the Spotless Mind
   - Typ: movie
   - Veröffentlichungsjahr: 2004
   - Genres: Drama, Romance, Sci-Fi.

## Ergebnisse

- Häufige Itemsets werden in der Datei `haeufige_itemsets.csv` gespeichert.
- Generierte Assoziationsregeln werden in der Datei `assoziationsregeln.csv` gespeichert.
- Visualisierungen werden als PNG-Dateien im Ordner `Daten/Ergebnisse/` gespeichert.

## Visualisierungen

### Beispiele
1. **Balkendiagramm der häufigen Itemsets:**
   - Zeigt die häufigsten Kombinationen von Genres und deren Support.
2. **Heatmap der Lift-Werte:**
   - Visualisiert die Stärke der Assoziationen zwischen Items.
3. **Scatterplots:**
   - Zeigen die Verteilung von Support, Konfidenz und Lift für alle Regeln.

## Ausführung

1. Stelle sicher, dass die Eingabedatei `Netflix_Bereinigt.csv` im Ordner `Daten/` liegt.
2. Starte das Skript:
   ```bash
   python Assoziationsanalyse.py
   ```
3. Ergebnisse werden im Ordner `Daten/Ergebnisse/` gespeichert.

## Kontakt

Bei Fragen oder Vorschlägen:
- **Autor:** Karim
- **E-Mail:** abdul-hadi.karim@fh-swf.de
