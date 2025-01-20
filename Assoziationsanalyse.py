import pandas as pd  # Importiere pandas für die Arbeit mit Datenframes
import matplotlib.pyplot as plt  # Importiere Matplotlib für Diagrammerstellung
from itertools import combinations, chain  # Importiere Tools zur Arbeit mit Kombinationen
from datetime import datetime  # Importiere datetime für Zeit- und Datumsangaben
import os  # Importiere os zur Arbeit mit Dateisystempfaden

# Konfigurationsvariablen für Dateipfade und Parameter
FILE_PATH = 'Daten/cleaned_data.csv'  # Pfad zur Input-CSV-Datei
BASE_OUTPUT_PATH = 'Daten/Ergebnisse/'  # Basisordner für Ergebnisdateien

# Generiere einen Zeitstempel für den Ergebnisordner
DATUM_ZEIT = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
OUTPUT_PATH = os.path.join(BASE_OUTPUT_PATH, f"Ergebnisse_{DATUM_ZEIT}/")  # Kombiniere Basisordner und Zeitstempel

# Erstelle den Ergebnisordner, falls er nicht existiert
os.makedirs(OUTPUT_PATH, exist_ok=True)  # Überprüft, ob der Ordner existiert, und erstellt ihn falls nicht

# Funktion zum Laden und Vorbereiten der Daten aus der CSV-Datei
def lade_und_bereite_daten_vor(file_path):
    print("Lade Daten...")  # Ausgabe, dass die Daten geladen werden
    daten = pd.read_csv(file_path)  # CSV-Datei wird eingelesen
    print(f"Daten erfolgreich geladen. Anzahl der Zeilen: {len(daten)}, Anzahl der Spalten: {len(daten.columns)}")  # Datenübersicht
    return daten.iloc[:, 1:]  # Entferne die erste Spalte (z. B. ID-Spalte)

# Funktion zur Eingabe von Mindest-Support und Mindest-Konfidenz
def eingabe_parameter():
    while True:
        try:
            # Mindest-Support eingeben und in Prozent umrechnen
            min_support = float(input("Bitte geben Sie den Mindest-Support ein (in Prozent, z.B. 5 für 5%): ")) / 100
            # Mindest-Konfidenz eingeben und in Prozent umrechnen
            min_confidence = float(input("Bitte geben Sie die Mindest-Konfidenz ein (in Prozent, z.B. 50 für 50%): ")) / 100
            # Werte validieren
            if 0 < min_support <= 1 and 0 < min_confidence <= 1:
                break  # Werte sind gültig, Schleife verlassen
            else:
                print("Bitte geben Sie Werte zwischen 0 und 100 ein.")  # Fehlerhinweis
        except ValueError:
            print("Ungültige Eingabe. Bitte geben Sie numerische Werte ein.")  # Hinweis bei fehlerhafter Eingabe
    return min_support, min_confidence  # Rückgabe der Eingabewerte

# Funktion zur Berechnung von häufigen Itemsets
def berechne_haeufige_itemsets(daten, min_support):
    print(f"Berechne häufige Itemsets mit Mindest-Support von {min_support * 100:.0f}%...")  # Ausgabe des Prozesses
    # Berechne den Support jedes Einzelitems
    einzel_items = daten.iloc[:, 3:].sum(axis=0) / len(daten)
    # Filtere Items basierend auf dem Mindest-Support
    einzel_items = einzel_items[einzel_items >= min_support]
    # Konvertiere Einzelitems in Itemsets
    itemsets = [(tuple([item]), support) for item, support in einzel_items.items()]

    # Iteriere über Kombinationen höherer Grade
    for itemset_size in range(2, len(einzel_items) + 1):
        for itemset in combinations(einzel_items.index, itemset_size):
            # Berechne den Support für das Itemset
            support = daten[list(itemset)].all(axis=1).sum() / len(daten)
            if support >= min_support:  # Überprüfe, ob der Support ausreichend ist
                itemsets.append((itemset, support))

    print(f"Gefundene häufige Itemsets: {len(itemsets)}")  # Anzahl gefundener Itemsets
    # Erstelle DataFrame für die Itemsets
    df = pd.DataFrame(itemsets, columns=["Itemset", "Support"])
    df["Support"] = df["Support"] * 100  # Konvertiere Support in Prozent
    return df  # Rückgabe des DataFrames

# Funktion zur Generierung von Assoziationsregeln
def generiere_assoziationsregeln(itemsets, daten, min_confidence):
    print(f"Generiere Assoziationsregeln mit Mindest-Konfidenz von {min_confidence * 100:.0f}%...")  # Statusmeldung
    regeln = []  # Initialisiere leere Liste für Regeln
    # Erstelle ein Dictionary für schnellen Zugriff auf Support-Werte
    itemset_dict = {tuple(sorted(itemset)): support for itemset, support in itemsets}

    # Iteriere über alle Itemsets
    for itemset, support in itemsets:
        if len(itemset) > 1:  # Betrachte nur Itemsets mit mehr als einem Item
            subsets = list(chain.from_iterable(combinations(itemset, r) for r in range(1, len(itemset))))  # Erstelle Teilmengen
            for vorlaeufer in subsets:
                vorlaeufer = tuple(sorted(vorlaeufer))  # Sortiere den Vorläufer
                konsequenz = tuple(sorted(set(itemset) - set(vorlaeufer)))  # Bestimme Konsequenz
                if konsequenz:  # Überprüfe, ob Konsequenz existiert
                    support_vorlaeufer = itemset_dict.get(vorlaeufer, None)  # Hole Support des Vorläufers
                    if support_vorlaeufer:
                        konfidenz = support / support_vorlaeufer  # Berechne Konfidenz
                        support_konsequenz = itemset_dict.get(konsequenz, None)  # Hole Support der Konsequenz
                        if support_konsequenz:
                            lift = konfidenz / support_konsequenz  # Berechne Lift
                            if konfidenz >= min_confidence:  # Überprüfe Mindest-Konfidenz
                                regeln.append((set(vorlaeufer), set(konsequenz), support * 100, konfidenz * 100, lift))  # Füge Regel hinzu

    print(f"Gefundene Assoziationsregeln: {len(regeln)}")  # Anzahl der Regeln
    # Erstelle DataFrame für Regeln
    df = pd.DataFrame(regeln, columns=["Vorläufer", "Konsequenz", "Support (%)", "Konfidenz (%)", "Lift"])
    df["Vorläufer"] = df["Vorläufer"].apply(lambda x: " UND ".join(sorted(x)))  # Formatierung der Vorläufer
    df["Konsequenz"] = df["Konsequenz"].apply(lambda x: " UND ".join(sorted(x)))  # Formatierung der Konsequenzen
    return df  # Rückgabe des DataFrames

# Funktion zur Visualisierung der häufigen Itemsets
def visualisiere_itemsets(itemsets_df, output_path):
    print("Visualisiere häufige Itemsets...")  # Statusmeldung
    top_itemsets = itemsets_df.sort_values(by="Support", ascending=False).head(10)  # Sortiere und wähle Top 10
    plt.figure(figsize=(10, 6))  # Erstelle Grafik
    plt.barh(
        [" & ".join(i) for i in top_itemsets["Itemset"]],
        top_itemsets["Support"],
        color="skyblue"
    )
    plt.xlabel("Support (%)")  # Achsentitel
    plt.title("Top 10 Häufige Itemsets")  # Diagrammtitel
    plt.gca().invert_yaxis()  # Y-Achse umdrehen
    filename = os.path.join(output_path, 'top_itemsets_balkendiagramm.png')  # Dateiname für Speicherung
    plt.savefig(filename)  # Speichere Diagramm
    print(f"Balkendiagramm gespeichert unter: {filename}")  # Speicherhinweis
    plt.show()  # Zeige Diagramm an

# Funktion zur Visualisierung der Item-Verteilung
def visualisiere_verteilung_items(daten, output_path):
    print("Visualisiere Verteilung von häufig vorkommenden Items...")  # Statusmeldung
    item_counts = daten.iloc[:, 3:].sum(axis=0).sort_values(ascending=False).head(10)  # Zähle Items
    plt.figure(figsize=(10, 6))  # Erstelle Grafik
    plt.bar(item_counts.index, item_counts.values, color="skyblue")  # Balkendiagramm
    plt.xlabel("Item")  # Achsentitel
    plt.ylabel("Häufigkeit")  # Achsentitel
    plt.title("Verteilung der häufigsten Items")  # Diagrammtitel
    plt.xticks(rotation=45)  # Drehe Achsenbeschriftung
    filename = os.path.join(output_path, 'verteilung_items.png')  # Dateiname für Speicherung
    plt.savefig(filename)  # Speichere Diagramm
    print(f"Verteilung gespeichert unter: {filename}")  # Speicherhinweis
    plt.show()  # Zeige Diagramm an

# Funktion zur Visualisierung der Top-Regeln nach einer Metrik
def visualisiere_top_regeln(regeln_df, output_path, metriken="Konfidenz (%)"):
    print(f"Visualisiere Top-Regeln nach {metriken}...")  # Statusmeldung
    if metriken not in regeln_df.columns:  # Überprüfe, ob Metrik existiert
        print(f"Spalte '{metriken}' nicht in den Daten verfügbar.")  # Fehlermeldung
        return
    top_regeln = regeln_df.sort_values(by=metriken, ascending=False).head(10)  # Sortiere und wähle Top 10
    plt.figure(figsize=(10, 6))  # Erstelle Grafik
    plt.barh(
        top_regeln["Vorläufer"] + " → " + top_regeln["Konsequenz"],
        top_regeln[metriken],
        color="lightgreen"
    )
    plt.xlabel(metriken)  # Achsentitel
    plt.title(f"Top 10 Regeln nach {metriken}")  # Diagrammtitel
    plt.gca().invert_yaxis()  # Y-Achse umdrehen
    filename = os.path.join(output_path, f'top_regeln_{metriken.lower().replace(" ", "_")}.png')  # Dateiname
    plt.savefig(filename)  # Speichere Diagramm
    print(f"Top-Regeln gespeichert unter: {filename}")  # Speicherhinweis
    plt.show()  # Zeige Diagramm an

# Hauptfunktion des Programms
def main():
    daten = lade_und_bereite_daten_vor(FILE_PATH)  # Lade Daten
    min_support, min_confidence = eingabe_parameter()  # Eingabe der Parameter

    itemsets_df = berechne_haeufige_itemsets(daten, min_support)  # Berechnung der Itemsets
    itemsets_filename = os.path.join(OUTPUT_PATH, 'haeufige_itemsets.csv')  # Speicherort
    itemsets_df.to_csv(itemsets_filename, index=False)  # Speichere Itemsets
    print(f"Häufige Itemsets gespeichert unter: {itemsets_filename}")  # Speicherhinweis

    print("\n--- Häufige Itemsets (einschließlich einzelner Items) ---")  # Ausgabe
    for i, row in itemsets_df.iterrows():  # Iteriere über Itemsets
        print(f"{i + 1}. Itemset: {', '.join(row['Itemset'])} - Support: {row['Support']:.2f}%")  # Drucke Itemset

    itemsets = [(tuple(itemset), support / 100) for itemset, support in itemsets_df.values]  # Konvertiere Itemsets
    regeln_df = generiere_assoziationsregeln(itemsets, daten, min_confidence)  # Berechnung der Regeln
    regeln_filename = os.path.join(OUTPUT_PATH, 'assoziationsregeln.csv')  # Speicherort
    regeln_df.to_csv(regeln_filename, index=False)  # Speichere Regeln
    print(f"Assoziationsregeln gespeichert unter: {regeln_filename}")  # Speicherhinweis

    print("\n--- Erweiterte Assoziationsregeln (einschließlich 2. Grades) ---")  # Ausgabe
    for i, row in regeln_df.iterrows():  # Iteriere über Regeln
        print(f"{i + 1}. Regel: Wenn {row['Vorläufer']} DANN {row['Konsequenz']} "
              f"- Support: {row['Support (%)']:.2f}%, Konfidenz: {row['Konfidenz (%)']:.2f}%, Lift: {row['Lift']:.2f}")

    visualisiere_itemsets(itemsets_df, OUTPUT_PATH)  # Visualisierung der Itemsets
    visualisiere_verteilung_items(daten, OUTPUT_PATH)  # Visualisierung der Item-Verteilung
    visualisiere_top_regeln(regeln_df, OUTPUT_PATH, metriken="Konfidenz (%)")  # Visualisierung der Regeln

# Startpunkt des Programms
if __name__ == "__main__":
    main()  # Starte das Programm
