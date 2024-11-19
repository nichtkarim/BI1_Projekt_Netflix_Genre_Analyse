import pandas as pd  # Importiere pandas für die Arbeit mit Datenframes
import matplotlib.pyplot as plt  # Importiere Matplotlib für Diagrammerstellung
import networkx as nx  # Importiere NetworkX zur Erstellung von Netzwerken
from itertools import combinations, chain  # Importiere Tools zur Arbeit mit Kombinationen
import seaborn as sns  # Importiere Seaborn für erweiterte Visualisierungen
from datetime import datetime  # Importiere datetime für Zeit- und Datumsangaben
import os  # Importiere os zur Arbeit mit Dateisystempfaden

# Konfigurationsvariablen für Dateipfade und Parameter
FILE_PATH = 'Daten/Netflix_Bereinigt.csv'  # Pfad zur Input-CSV-Datei
BASE_OUTPUT_PATH = 'Daten/Ergebnisse/'  # Basisordner für Ergebnisdateien
MIN_SUPPORT = 0.05  # Mindest-Support für Itemset-Berechnung (als Anteil)
MIN_CONFIDENCE = 0.5  # Mindest-Konfidenz für Assoziationsregeln (als Anteil)

# Generiere einen Zeitstempel für den Ergebnisordner
DATUM_ZEIT = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
OUTPUT_PATH = os.path.join(BASE_OUTPUT_PATH, f"Ergebnisse_{DATUM_ZEIT}/")  # Kombiniere Basisordner und Zeitstempel

# Erstelle den Ergebnisordner, falls er nicht existiert
os.makedirs(OUTPUT_PATH, exist_ok=True)

# Funktion zum Laden und Vorbereiten der Daten aus der CSV-Datei
def lade_und_bereite_daten_vor(file_path):
    print("Lade Daten...")
    daten = pd.read_csv(file_path)  # Lese die CSV-Datei ein
    print(f"Daten erfolgreich geladen. Anzahl der Zeilen: {len(daten)}, Anzahl der Spalten: {len(daten.columns)}")
    return daten.iloc[:, 1:]  # Entferne die erste Spalte (falls ID-Spalte vorhanden)

# Funktion zur Berechnung von häufigen Itemsets
def berechne_haeufige_itemsets(daten, min_support):
    """
    Berechnet häufige Itemsets basierend auf dem Mindest-Support, inklusive einzelner Items.
    """
    print(f"Berechne häufige Itemsets mit Mindest-Support von {min_support * 100:.0f}%...")
    # Berechne den Support einzelner Items
    einzel_items = daten.iloc[:, 3:].sum(axis=0) / len(daten)
    einzel_items = einzel_items[einzel_items >= min_support]  # Filtere Items basierend auf Mindest-Support
    itemsets = [(tuple([item]), support) for item, support in einzel_items.items()]  # Erstelle Itemsets für Einzelitems

    # Berechnung von Kombinationen höherer Grade
    for itemset_size in range(2, len(einzel_items) + 1):
        for itemset in combinations(einzel_items.index, itemset_size):  # Iteriere über alle Kombinationen
            support = daten[list(itemset)].all(axis=1).sum() / len(daten)  # Berechne den Support
            if support >= min_support:  # Nur Itemsets mit ausreichendem Support hinzufügen
                itemsets.append((itemset, support))

    print(f"Gefundene häufige Itemsets: {len(itemsets)}")
    # Erstelle ein DataFrame mit Itemsets und deren Support
    df = pd.DataFrame(itemsets, columns=["Itemset", "Support"])
    df["Support"] = df["Support"] * 100  # Konvertiere Support-Werte in Prozent
    return df

# Funktion zur Generierung von Assoziationsregeln
def generiere_assoziationsregeln(itemsets, daten, min_confidence):
    """
    Generiert Assoziationsregeln basierend auf häufigen Itemsets und Mindest-Konfidenz.
    """
    print(f"Generiere Assoziationsregeln mit Mindest-Konfidenz von {min_confidence * 100:.0f}%...")
    regeln = []
    for itemset, support in itemsets:
        if len(itemset) > 1:  # Betrachte nur Itemsets mit mindestens zwei Items
            subsets = list(chain.from_iterable(combinations(itemset, r) for r in range(1, len(itemset))))
            for vorlaeufer in subsets:
                konsequenz = set(itemset) - set(vorlaeufer)  # Konsequenz ist der Rest des Itemsets
                if konsequenz:
                    # Berechne Konfidenz und Lift
                    support_vorlaeufer = daten[list(vorlaeufer)].all(axis=1).sum() / len(daten)
                    konfidenz = support / support_vorlaeufer
                    support_konsequenz = daten[list(konsequenz)].all(axis=1).sum() / len(daten)
                    lift = konfidenz / support_konsequenz
                    if konfidenz >= min_confidence:
                        regeln.append((set(vorlaeufer), konsequenz, support * 100, konfidenz * 100, lift))

    print(f"Gefundene Assoziationsregeln: {len(regeln)}")
    # Erstelle ein DataFrame mit den Regeln und deren Metriken
    df = pd.DataFrame(regeln, columns=["Vorläufer", "Konsequenz", "Support (%)", "Konfidenz (%)", "Lift"])
    # Formatierung der Spalten für bessere Lesbarkeit
    df["Vorläufer"] = df["Vorläufer"].apply(lambda x: " UND ".join(sorted(x)))
    df["Konsequenz"] = df["Konsequenz"].apply(lambda x: " UND ".join(sorted(x)))
    return df


def visualisiere_itemsets(itemsets_df, output_path):
    # Gibt eine Meldung aus, dass die Visualisierung beginnt
    print("Visualisiere häufige Itemsets...")

    # Sortiere die Itemsets nach Support in absteigender Reihenfolge und wähle die Top 10 aus
    top_itemsets = itemsets_df.sort_values(by="Support", ascending=False).head(10)

    # Erstelle ein horizontales Balkendiagramm
    plt.figure(figsize=(10, 6))  # Definiere die Größe des Diagramms
    plt.barh(
        [" & ".join(i) for i in top_itemsets["Itemset"]],
        # Kombiniere die Items eines Itemsets mit "&" als Trennzeichen
        top_itemsets["Support"],  # Werte für die Höhe der Balken
        color="skyblue"  # Balkenfarbe
    )
    plt.xlabel("Support (%)")  # Beschriftung der x-Achse
    plt.title("Top 10 Häufige Itemsets")  # Titel des Diagramms
    plt.gca().invert_yaxis()  # Drehe die y-Achse um, damit die höchsten Werte oben sind

    # Speichere das Diagramm als Bilddatei
    filename = os.path.join(output_path, 'top_itemsets_balkendiagramm.png')
    plt.savefig(filename)
    print(f"Balkendiagramm gespeichert unter: {filename}")
    plt.show()  # Zeige das Diagramm an


def visualisiere_verteilung_items(daten, output_path):
    # Gibt eine Meldung aus, dass die Visualisierung beginnt
    print("Visualisiere Verteilung von häufig vorkommenden Items...")

    # Berechne die Häufigkeit der Items und wähle die Top 10
    item_counts = daten.iloc[:, 3:].sum(axis=0).sort_values(ascending=False).head(10)

    # Erstelle ein Balkendiagramm der Itemverteilung
    plt.figure(figsize=(10, 6))  # Definiere die Größe des Diagramms
    plt.bar(item_counts.index, item_counts.values, color="skyblue")  # Items und deren Häufigkeiten
    plt.xlabel("Item")  # Beschriftung der x-Achse
    plt.ylabel("Häufigkeit")  # Beschriftung der y-Achse
    plt.title("Verteilung der häufigsten Items")  # Titel des Diagramms
    plt.xticks(rotation=45)  # Drehung der x-Achsen-Beschriftungen für bessere Lesbarkeit

    # Speichere das Diagramm als Bilddatei
    filename = os.path.join(output_path, 'verteilung_items.png')
    plt.savefig(filename)
    print(f"Verteilung gespeichert unter: {filename}")
    plt.show()  # Zeige das Diagramm an


def visualisiere_top_regeln(regeln_df, output_path, metriken="Konfidenz (%)"):
    # Gibt eine Meldung aus, dass die Visualisierung beginnt
    print(f"Visualisiere Top-Regeln nach {metriken}...")

    # Überprüfe, ob die angegebene Metrik in den Daten vorhanden ist
    if metriken not in regeln_df.columns:
        print(f"Spalte '{metriken}' nicht in den Daten verfügbar.")
        return

    # Sortiere die Regeln nach der angegebenen Metrik und wähle die Top 10
    top_regeln = regeln_df.sort_values(by=metriken, ascending=False).head(10)

    # Erstelle ein horizontales Balkendiagramm für die Top-Regeln
    plt.figure(figsize=(10, 6))  # Definiere die Größe des Diagramms
    plt.barh(
        top_regeln["Vorläufer"] + " → " + top_regeln["Konsequenz"],  # Beschriftung der Regeln
        top_regeln[metriken],  # Werte der Metrik
        color="lightgreen"  # Balkenfarbe
    )
    plt.xlabel(metriken)  # Beschriftung der x-Achse
    plt.title(f"Top 10 Regeln nach {metriken}")  # Titel des Diagramms
    plt.gca().invert_yaxis()  # Drehe die y-Achse um

    # Speichere das Diagramm als Bilddatei
    filename = os.path.join(output_path, f'top_regeln_{metriken.lower().replace(" ", "_")}.png')
    plt.savefig(filename)
    print(f"Top-Regeln gespeichert unter: {filename}")
    plt.show()  # Zeige das Diagramm an


def visualisiere_erweiterte_heatmap(regeln_df, output_path):
    # Gibt eine Meldung aus, dass die Erstellung der Heatmap beginnt
    print("Erstelle erweiterte Heatmap für Leverage und Conviction...")

    # Berechne zusätzliche Metriken: Leverage und Conviction
    regeln_df["Leverage"] = regeln_df["Support (%)"] / 100 - (regeln_df["Konfidenz (%)"] / 100) * (regeln_df["Lift"])
    regeln_df["Conviction"] = (1 - regeln_df["Konfidenz (%)"] / 100) / (1 - regeln_df["Lift"])

    # Liste der Metriken für die Erstellung der Heatmaps
    metrics = ["Leverage", "Conviction"]
    for metric in metrics:
        # Erstelle eine Pivot-Tabelle für die Heatmap
        heatmap_data = regeln_df.pivot_table(index="Vorläufer", columns="Konsequenz", values=metric, aggfunc="mean")

        # Überprüfe, ob Daten für die Heatmap verfügbar sind
        if not heatmap_data.empty:
            plt.figure(figsize=(12, 8))  # Definiere die Größe der Heatmap
            sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", fmt=".2f")  # Erstelle die Heatmap
            plt.title(f"Heatmap für {metric}")  # Titel der Heatmap
            plt.xlabel("Konsequenz")  # Beschriftung der x-Achse
            plt.ylabel("Vorläufer")  # Beschriftung der y-Achse

            # Speichere die Heatmap als Bilddatei
            filename = os.path.join(output_path, f'{metric.lower()}_heatmap.png')
            plt.savefig(filename)
            print(f"{metric}-Heatmap gespeichert unter: {filename}")
            plt.show()  # Zeige die Heatmap an


def visualisiere_lift_heatmap(regeln_df, output_path):
    """
    Erstellt eine Heatmap der Lift-Werte.
    """
    print("Erstelle Heatmap der Lift-Werte...")

    # Erstelle eine Pivot-Tabelle für die Lift-Werte
    heatmap_data = regeln_df.pivot_table(index="Vorläufer", columns="Konsequenz", values="Lift", aggfunc="mean")

    # Überprüfe, ob Daten für die Heatmap verfügbar sind
    if not heatmap_data.empty:
        plt.figure(figsize=(12, 8))  # Definiere die Größe der Heatmap
        sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", fmt=".2f")  # Erstelle die Heatmap
        plt.title("Heatmap der Lift-Werte")  # Titel der Heatmap
        plt.xlabel("Konsequenz")  # Beschriftung der x-Achse
        plt.ylabel("Vorläufer")  # Beschriftung der y-Achse

        # Speichere die Heatmap als Bilddatei
        filename = os.path.join(output_path, 'lift_heatmap.png')
        plt.savefig(filename)
        print(f"Heatmap gespeichert unter: {filename}")
        plt.show()  # Zeige die Heatmap an
    else:
        print("Heatmap konnte nicht erstellt werden, da keine Daten vorhanden sind.")


def visualisiere_scatterplot(regeln_df, output_path, x="Support (%)", y="Konfidenz (%)"):
    # Gibt eine Meldung aus, dass die Erstellung des Scatterplots beginnt
    print(f"Erstelle Scatterplot für {x} vs. {y}...")

    # Erstelle den Scatterplot
    plt.figure(figsize=(10, 6))  # Definiere die Größe des Scatterplots
    plt.scatter(
        regeln_df[x], regeln_df[y],  # Achsendaten
        alpha=0.7, edgecolors="w", linewidth=0.5  # Optische Einstellungen
    )
    plt.xlabel(x)  # Beschriftung der x-Achse
    plt.ylabel(y)  # Beschriftung der y-Achse
    plt.title(f"Scatterplot: {x} vs. {y}")  # Titel des Scatterplots

    # Speichere den Scatterplot als Bilddatei
    filename = os.path.join(output_path,
                            f'scatterplot_{x.lower().replace(" ", "_")}_vs_{y.lower().replace(" ", "_")}.png')
    plt.savefig(filename)
    print(f"Scatterplot gespeichert unter: {filename}")
    plt.show()  # Zeige den Scatterplot an


def main():
    daten = lade_und_bereite_daten_vor(FILE_PATH)

    # Häufige Itemsets berechnen
    itemsets_df = berechne_haeufige_itemsets(daten, MIN_SUPPORT)
    itemsets_filename = os.path.join(OUTPUT_PATH, 'haeufige_itemsets.csv')
    itemsets_df.to_csv(itemsets_filename, index=False)
    print(f"Häufige Itemsets gespeichert unter: {itemsets_filename}")

    # Ausgabe der häufigen Itemsets in der Konsole
    print("\n--- Häufige Itemsets (einschließlich einzelner Items) ---")
    for i, row in itemsets_df.iterrows():
        print(f"{i + 1}. Itemset: {', '.join(row['Itemset'])} - Support: {row['Support']:.2f}%")

    # Assoziationsregeln erstellen
    itemsets = [(tuple(itemset), support / 100) for itemset, support in itemsets_df.values]
    regeln_df = generiere_assoziationsregeln(itemsets, daten, MIN_CONFIDENCE)
    regeln_filename = os.path.join(OUTPUT_PATH, 'assoziationsregeln.csv')
    regeln_df.to_csv(regeln_filename, index=False)
    print(f"Assoziationsregeln gespeichert unter: {regeln_filename}")

    # Ausgabe der Assoziationsregeln in der Konsole
    print("\n--- Erweiterte Assoziationsregeln (einschließlich 2. Grades) ---")
    for i, row in regeln_df.iterrows():
        print(f"{i + 1}. Regel: Wenn {row['Vorläufer']} DANN {row['Konsequenz']} "
              f"- Support: {row['Support (%)']:.2f}%, Konfidenz: {row['Konfidenz (%)']:.2f}%, Lift: {row['Lift']:.2f}")

    # Visualisierungen erstellen
    visualisiere_itemsets(itemsets_df, OUTPUT_PATH)
    visualisiere_verteilung_items(daten, OUTPUT_PATH)
    visualisiere_top_regeln(regeln_df, OUTPUT_PATH, metriken="Lift")
    visualisiere_top_regeln(regeln_df, OUTPUT_PATH, metriken="Konfidenz (%)")
    visualisiere_lift_heatmap(regeln_df, OUTPUT_PATH)
    visualisiere_erweiterte_heatmap(regeln_df, OUTPUT_PATH)
    visualisiere_scatterplot(regeln_df, OUTPUT_PATH, x="Support (%)", y="Konfidenz (%)")
    visualisiere_scatterplot(regeln_df, OUTPUT_PATH, x="Lift", y="Konfidenz (%)")




if __name__ == "__main__":
    main()
