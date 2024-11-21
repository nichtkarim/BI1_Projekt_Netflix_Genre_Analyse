import pandas as pd  # Importiere pandas für die Arbeit mit Datenframes
import matplotlib.pyplot as plt  # Importiere Matplotlib für Diagrammerstellung
from itertools import combinations, chain  # Importiere Tools zur Arbeit mit Kombinationen
import seaborn as sns  # Importiere Seaborn für erweiterte Visualisierungen
from datetime import datetime  # Importiere datetime für Zeit- und Datumsangaben
import os  # Importiere os zur Arbeit mit Dateisystempfaden

# Konfigurationsvariablen für Dateipfade und Parameter
FILE_PATH = 'Daten/cleaned_data.csv'  # Pfad zur Input-CSV-Datei
BASE_OUTPUT_PATH = 'Daten/Ergebnisse/'  # Basisordner für Ergebnisdateien

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

# Funktion zur Eingabe von Mindest-Support und Mindest-Konfidenz
def eingabe_parameter():
    while True:
        try:
            min_support = float(input("Bitte geben Sie den Mindest-Support ein (in Prozent, z.B. 5 für 5%): ")) / 100
            min_confidence = float(input("Bitte geben Sie die Mindest-Konfidenz ein (in Prozent, z.B. 50 für 50%): ")) / 100
            if 0 < min_support <= 1 and 0 < min_confidence <= 1:
                break
            else:
                print("Bitte geben Sie Werte zwischen 0 und 100 ein.")
        except ValueError:
            print("Ungültige Eingabe. Bitte geben Sie numerische Werte ein.")
    return min_support, min_confidence

# Funktion zur Berechnung von häufigen Itemsets
def berechne_haeufige_itemsets(daten, min_support):
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
    print(f"Generiere Assoziationsregeln mit Mindest-Konfidenz von {min_confidence * 100:.0f}%...")
    regeln = []
    itemset_dict = {tuple(sorted(itemset)): support for itemset, support in itemsets}
    for itemset, support in itemsets:
        if len(itemset) > 1:  # Betrachte nur Itemsets mit mindestens zwei Items
            subsets = list(chain.from_iterable(combinations(itemset, r) for r in range(1, len(itemset))))
            for vorlaeufer in subsets:
                vorlaeufer = tuple(sorted(vorlaeufer))
                konsequenz = tuple(sorted(set(itemset) - set(vorlaeufer)))
                if konsequenz:
                    support_vorlaeufer = itemset_dict.get(vorlaeufer, None)
                    if support_vorlaeufer:
                        konfidenz = support / support_vorlaeufer
                        support_konsequenz = itemset_dict.get(konsequenz, None)
                        if support_konsequenz:
                            lift = konfidenz / (support_konsequenz)
                            if konfidenz >= min_confidence:
                                regeln.append((set(vorlaeufer), set(konsequenz), support * 100, konfidenz * 100, lift))

    print(f"Gefundene Assoziationsregeln: {len(regeln)}")
    # Erstelle ein DataFrame mit den Regeln und deren Metriken
    df = pd.DataFrame(regeln, columns=["Vorläufer", "Konsequenz", "Support (%)", "Konfidenz (%)", "Lift"])
    # Formatierung der Spalten für bessere Lesbarkeit
    df["Vorläufer"] = df["Vorläufer"].apply(lambda x: " UND ".join(sorted(x)))
    df["Konsequenz"] = df["Konsequenz"].apply(lambda x: " UND ".join(sorted(x)))
    return df

def visualisiere_itemsets(itemsets_df, output_path):
    print("Visualisiere häufige Itemsets...")
    top_itemsets = itemsets_df.sort_values(by="Support", ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    plt.barh(
        [" & ".join(i) for i in top_itemsets["Itemset"]],
        top_itemsets["Support"],
        color="skyblue"
    )
    plt.xlabel("Support (%)")
    plt.title("Top 10 Häufige Itemsets")
    plt.gca().invert_yaxis()
    filename = os.path.join(output_path, 'top_itemsets_balkendiagramm.png')
    plt.savefig(filename)
    print(f"Balkendiagramm gespeichert unter: {filename}")
    plt.show()

def visualisiere_verteilung_items(daten, output_path):
    print("Visualisiere Verteilung von häufig vorkommenden Items...")
    item_counts = daten.iloc[:, 3:].sum(axis=0).sort_values(ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    plt.bar(item_counts.index, item_counts.values, color="skyblue")
    plt.xlabel("Item")
    plt.ylabel("Häufigkeit")
    plt.title("Verteilung der häufigsten Items")
    plt.xticks(rotation=45)
    filename = os.path.join(output_path, 'verteilung_items.png')
    plt.savefig(filename)
    print(f"Verteilung gespeichert unter: {filename}")
    plt.show()

def visualisiere_top_regeln(regeln_df, output_path, metriken="Konfidenz (%)"):
    print(f"Visualisiere Top-Regeln nach {metriken}...")
    if metriken not in regeln_df.columns:
        print(f"Spalte '{metriken}' nicht in den Daten verfügbar.")
        return
    top_regeln = regeln_df.sort_values(by=metriken, ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    plt.barh(
        top_regeln["Vorläufer"] + " → " + top_regeln["Konsequenz"],
        top_regeln[metriken],
        color="lightgreen"
    )
    plt.xlabel(metriken)
    plt.title(f"Top 10 Regeln nach {metriken}")
    plt.gca().invert_yaxis()
    filename = os.path.join(output_path, f'top_regeln_{metriken.lower().replace(" ", "_")}.png')
    plt.savefig(filename)
    print(f"Top-Regeln gespeichert unter: {filename}")
    plt.show()

def visualisiere_erweiterte_heatmap(regeln_df, output_path):
    print("Erstelle erweiterte Heatmap für Leverage und Conviction...")
    regeln_df["Leverage"] = (regeln_df["Support (%)"] / 100) - (
        (regeln_df["Vorläufer"].map(regeln_df.groupby("Vorläufer")["Support (%)"].mean()) / 100) *
        (regeln_df["Konsequenz"].map(regeln_df.groupby("Konsequenz")["Support (%)"].mean()) / 100)
    )
    regeln_df["Conviction"] = (1 - (regeln_df["Konsequenz"].map(regeln_df.groupby("Konsequenz")["Support (%)"].mean()) / 100)) / (
        1 - (regeln_df["Konfidenz (%)"] / 100)
    )
    metrics = ["Leverage", "Conviction"]
    for metric in metrics:
        heatmap_data = regeln_df.pivot_table(index="Vorläufer", columns="Konsequenz", values=metric, aggfunc="mean")
        if not heatmap_data.empty:
            plt.figure(figsize=(12, 8))
            sns.heatmap(heatmap_data, annot=True, cmap="coolwarm", fmt=".2f")
            plt.title(f"Heatmap für {metric}")
            plt.xlabel("Konsequenz")
            plt.ylabel("Vorläufer")
            filename = os.path.join(output_path, f'{metric.lower()}_heatmap.png')
            plt.savefig(filename)
            print(f"{metric}-Heatmap gespeichert unter: {filename}")
            plt.show()

def visualisiere_lift_heatmap(regeln_df, output_path):
    print("Erstelle Heatmap der Lift-Werte...")
    heatmap_data = regeln_df.pivot_table(index="Vorläufer", columns="Konsequenz", values="Lift", aggfunc="mean")
    if not heatmap_data.empty:
        plt.figure(figsize=(12, 8))
        sns.heatmap(heatmap_data, annot=True, cmap="YlGnBu", fmt=".2f")
        plt.title("Heatmap der Lift-Werte")
        plt.xlabel("Konsequenz")
        plt.ylabel("Vorläufer")
        filename = os.path.join(output_path, 'lift_heatmap.png')
        plt.savefig(filename)
        print(f"Heatmap gespeichert unter: {filename}")
        plt.show()
    else:
        print("Heatmap konnte nicht erstellt werden, da keine Daten vorhanden sind.")

def visualisiere_scatterplot(regeln_df, output_path, x="Support (%)", y="Konfidenz (%)"):
    print(f"Erstelle Scatterplot für {x} vs. {y}...")
    plt.figure(figsize=(10, 6))
    plt.scatter(
        regeln_df[x], regeln_df[y],
        alpha=0.7, edgecolors="w", linewidth=0.5
    )
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title(f"Scatterplot: {x} vs. {y}")
    filename = os.path.join(output_path,
                            f'scatterplot_{x.lower().replace(" ", "_")}_vs_{y.lower().replace(" ", "_")}.png')
    plt.savefig(filename)
    print(f"Scatterplot gespeichert unter: {filename}")
    plt.show()

def main():
    daten = lade_und_bereite_daten_vor(FILE_PATH)
    min_support, min_confidence = eingabe_parameter()

    # Häufige Itemsets berechnen
    itemsets_df = berechne_haeufige_itemsets(daten, min_support)
    itemsets_filename = os.path.join(OUTPUT_PATH, 'haeufige_itemsets.csv')
    itemsets_df.to_csv(itemsets_filename, index=False)
    print(f"Häufige Itemsets gespeichert unter: {itemsets_filename}")

    # Ausgabe der häufigen Itemsets in der Konsole
    print("\n--- Häufige Itemsets (einschließlich einzelner Items) ---")
    for i, row in itemsets_df.iterrows():
        print(f"{i + 1}. Itemset: {', '.join(row['Itemset'])} - Support: {row['Support']:.2f}%")

    # Assoziationsregeln erstellen
    itemsets = [(tuple(itemset), support / 100) for itemset, support in itemsets_df.values]
    regeln_df = generiere_assoziationsregeln(itemsets, daten, min_confidence)
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
