import pandas as pd
import matplotlib.pyplot as plt
import networkx as nx
from itertools import combinations, chain
import seaborn as sns
from datetime import datetime
import os

# Konfigurationen
FILE_PATH = 'Daten/Netflix_Bereinigt.csv'
BASE_OUTPUT_PATH = 'Daten/Ergebnisse/'
MIN_SUPPORT = 0.03
MIN_CONFIDENCE = 0.4

# Aktuelles Datum und Zeit für den Ordnernamen
DATUM_ZEIT = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
OUTPUT_PATH = os.path.join(BASE_OUTPUT_PATH, f"Ergebnisse_{DATUM_ZEIT}/")

# Erstelle den Ausgabeordner
os.makedirs(OUTPUT_PATH, exist_ok=True)


def lade_und_bereite_daten_vor(file_path):
    print("Lade Daten...")
    daten = pd.read_csv(file_path)
    print(f"Daten erfolgreich geladen. Anzahl der Zeilen: {len(daten)}, Anzahl der Spalten: {len(daten.columns)}")
    return daten.iloc[:, 1:]


def berechne_haeufige_itemsets(daten, min_support):
    """
    Berechnet häufige Itemsets basierend auf dem Mindest-Support, inklusive einzelner Items.
    """
    print(f"Berechne häufige Itemsets mit Mindest-Support von {min_support * 100:.0f}%...")

    # Berechnung des Supports für einzelne Items (1. Grades)
    einzel_items = daten.iloc[:, 3:].sum(axis=0) / len(daten)
    einzel_items = einzel_items[einzel_items >= min_support]
    itemsets = [(tuple([item]), support) for item, support in einzel_items.items()]

    # Berechnung des Supports für Kombinationen (2. Grades und höher)
    for itemset_size in range(2, len(einzel_items) + 1):
        for itemset in combinations(einzel_items.index, itemset_size):
            support = daten[list(itemset)].all(axis=1).sum() / len(daten)
            if support >= min_support:
                itemsets.append((itemset, support))

    print(f"Gefundene häufige Itemsets: {len(itemsets)}")
    df = pd.DataFrame(itemsets, columns=["Itemset", "Support"])
    df["Support"] = df["Support"] * 100  # Konvertiere zu Prozent
    return df



def generiere_assoziationsregeln(itemsets, daten, min_confidence):
    """
    Generiert Assoziationsregeln basierend auf häufigen Itemsets und Mindest-Konfidenz,
    einschließlich Regeln des 2. Grades oder höher.
    """
    print(f"Generiere Assoziationsregeln mit Mindest-Konfidenz von {min_confidence * 100:.0f}%...")
    regeln = []
    for itemset, support in itemsets:
        if len(itemset) > 1:  # Betrachte nur Itemsets mit mindestens zwei Items
            subsets = list(chain.from_iterable(combinations(itemset, r) for r in range(1, len(itemset))))
            for vorlaeufer in subsets:
                konsequenz = set(itemset) - set(vorlaeufer)
                if konsequenz:
                    support_vorlaeufer = daten[list(vorlaeufer)].all(axis=1).sum() / len(daten)
                    konfidenz = support / support_vorlaeufer
                    support_konsequenz = daten[list(konsequenz)].all(axis=1).sum() / len(daten)
                    lift = konfidenz / support_konsequenz
                    if konfidenz >= min_confidence:
                        regeln.append((set(vorlaeufer), konsequenz, support * 100, konfidenz * 100, lift))

    print(f"Gefundene Assoziationsregeln: {len(regeln)}")
    df = pd.DataFrame(regeln, columns=["Vorläufer", "Konsequenz", "Support (%)", "Konfidenz (%)", "Lift"])
    df["Vorläufer"] = df["Vorläufer"].apply(lambda x: " UND ".join(sorted(x)))
    df["Konsequenz"] = df["Konsequenz"].apply(lambda x: " UND ".join(sorted(x)))
    return df




def visualisiere_itemsets(itemsets_df, output_path):
    print("Visualisiere häufige Itemsets...")
    top_itemsets = itemsets_df.sort_values(by="Support", ascending=False).head(10)
    plt.figure(figsize=(10, 6))
    plt.barh([" & ".join(i) for i in top_itemsets["Itemset"]], top_itemsets["Support"], color="skyblue")
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
    plt.barh(top_regeln["Vorläufer"] + " → " + top_regeln["Konsequenz"], top_regeln[metriken], color="lightgreen")
    plt.xlabel(metriken)
    plt.title(f"Top 10 Regeln nach {metriken}")
    plt.gca().invert_yaxis()
    filename = os.path.join(output_path, f'top_regeln_{metriken.lower().replace(" ", "_")}.png')
    plt.savefig(filename)
    print(f"Top-Regeln gespeichert unter: {filename}")
    plt.show()



def visualisiere_erweiterte_heatmap(regeln_df, output_path):
    print("Erstelle erweiterte Heatmap für Leverage und Conviction...")
    regeln_df["Leverage"] = regeln_df["Support (%)"] / 100 - (regeln_df["Konfidenz (%)"] / 100) * (regeln_df["Lift"])
    regeln_df["Conviction"] = (1 - regeln_df["Konfidenz (%)"] / 100) / (1 - regeln_df["Lift"])

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
    """
    Erstellt eine Heatmap der Lift-Werte.
    """
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
    plt.scatter(regeln_df[x], regeln_df[y], alpha=0.7, edgecolors="w", linewidth=0.5)
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
