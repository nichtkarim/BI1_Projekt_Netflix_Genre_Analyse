import pandas as pd
import matplotlib.pyplot as plt
from itertools import combinations, chain
from datetime import datetime
import os

# Diese Funktion erstellt einen neuen Ordner, in dem die Ergebnisse des Programms gespeichert werden.
# Ein Zeitstempel wird verwendet, um sicherzustellen, dass der Ordnername eindeutig ist.
# Wenn der Ordner bereits existiert, wird er nicht erneut erstellt.
def erstelle_ausgabe_ordner(base_path):
    datum_zeit = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_path = os.path.join(base_path, f"Ergebnisse_{datum_zeit}/")
    os.makedirs(output_path, exist_ok=True)
    return output_path

# Diese Funktion lädt die Daten aus einer CSV-Datei, entfernt die erste Spalte (z. B. ID-Spalte) und gibt den Rest zurück.
def lade_daten(file_path):
    print("Lade Daten...")
    daten = pd.read_csv(file_path)
    print(f"Daten geladen: {len(daten)} Zeilen, {len(daten.columns)} Spalten.")
    return daten.iloc[:, 1:]

# Diese Funktion ermöglicht die Eingabe von Mindest-Support und Mindest-Konfidenz.
# Beide Werte müssen zwischen 0 und 100 Prozent liegen.
def eingabe_parameter():
    def eingabe(prompt):
        while True:
            try:
                wert = float(input(prompt)) / 100
                if 0 < wert <= 1:
                    return wert
                else:
                    print("Bitte geben Sie einen Wert zwischen 0 und 100 ein.")
            except ValueError:
                print("Ungültige Eingabe. Bitte numerische Werte eingeben.")
    min_support = eingabe("Mindest-Support (%): ")
    min_confidence = eingabe("Mindest-Konfidenz (%): ")
    return min_support, min_confidence

# Diese Funktion berechnet die häufigen Itemsets basierend auf dem angegebenen Mindest-Support.
# Sie erstellt zunächst Einzel-Itemsets und erweitert diese durch Kombinationen höherer Grade.
def berechne_itemsets(daten, min_support):
    print(f"Berechne Itemsets mit Mindest-Support {min_support * 100:.0f}%...")
    einzel_items = daten.iloc[:, 3:].sum(axis=0) / len(daten)
    einzel_items = einzel_items[einzel_items >= min_support]
    itemsets = [(tuple([item]), support) for item, support in einzel_items.items()]

    for size in range(2, len(einzel_items) + 1):
        for itemset in combinations(einzel_items.index, size):
            support = daten[list(itemset)].all(axis=1).sum() / len(daten)
            if support >= min_support:
                itemsets.append((itemset, support))

    df = pd.DataFrame(itemsets, columns=["Itemset", "Support"])
    df["Support"] *= 100
    return df

# Diese Funktion generiert Assoziationsregeln basierend auf den häufigen Itemsets und der Mindest-Konfidenz.
# Jede Regel wird als Vorläufer (Antezedenz) und Konsequenz mit den zugehörigen Metriken ausgegeben.
def generiere_regeln(itemsets, daten, min_confidence):
    print(f"Generiere Regeln mit Mindest-Konfidenz {min_confidence * 100:.0f}%...")
    regeln = []
    itemset_dict = {tuple(sorted(itemset)): support for itemset, support in itemsets}

    for itemset, support in itemsets:
        if len(itemset) > 1:
            subsets = list(chain.from_iterable(combinations(itemset, r) for r in range(1, len(itemset))))
            for vorlaeufer in subsets:
                vorlaeufer = tuple(sorted(vorlaeufer))
                konsequenz = tuple(sorted(set(itemset) - set(vorlaeufer)))
                if konsequenz:
                    support_vorlaeufer = itemset_dict.get(vorlaeufer)
                    if support_vorlaeufer:
                        konfidenz = support / support_vorlaeufer
                        if konfidenz >= min_confidence:
                            regeln.append((vorlaeufer, konsequenz, support * 100, konfidenz * 100))

    df = pd.DataFrame(regeln, columns=["Vorläufer", "Konsequenz", "Support (%)", "Konfidenz (%)"])
    df["Vorläufer"] = df["Vorläufer"].apply(lambda x: " UND ".join(x))
    df["Konsequenz"] = df["Konsequenz"].apply(lambda x: " UND ".join(x))
    return df

# Diese Funktion speichert einen DataFrame als CSV-Datei an einem angegebenen Pfad.
def speichere_csv(df, filename):
    df.to_csv(filename, index=False)
    print(f"Datei gespeichert: {filename}")

# Diese Funktion visualisiert die Top 10 häufigen Itemsets als Balkendiagramm und speichert die Grafik.
def visualisiere_itemsets(itemsets_df, output_path):
    print("Visualisiere häufige Itemsets...")
    top_itemsets = itemsets_df.sort_values(by="Support", ascending=False).head(10)
    plt.barh([" & ".join(i) for i in top_itemsets["Itemset"]], top_itemsets["Support"], color="skyblue")
    plt.xlabel("Support (%)")
    plt.title("Top 10 Häufige Itemsets")
    plt.gca().invert_yaxis()
    filename = os.path.join(output_path, 'top_itemsets.png')
    plt.savefig(filename)
    plt.show()

# Diese Funktion visualisiert die Verteilung der häufigsten Items und speichert ein Balkendiagramm.
def visualisiere_verteilung_items(daten, output_path):
    print("Visualisiere Verteilung von Items...")
    item_counts = daten.iloc[:, 3:].sum(axis=0).sort_values(ascending=False).head(10)
    plt.bar(item_counts.index, item_counts.values, color="skyblue")
    plt.xlabel("Item")
    plt.ylabel("Häufigkeit")
    plt.title("Verteilung der häufigsten Items")
    plt.xticks(rotation=45)
    filename = os.path.join(output_path, 'item_verteilung.png')
    plt.savefig(filename)
    plt.show()

# Diese Funktion visualisiert die Top 10 Assoziationsregeln basierend auf einer gewählten Metrik (z. B. Konfidenz).
def visualisiere_top_regeln(regeln_df, output_path, metriken="Konfidenz (%)"):
    print(f"Visualisiere Top-Regeln nach {metriken}...")
    top_regeln = regeln_df.sort_values(by=metriken, ascending=False).head(10)
    plt.barh(top_regeln["Vorläufer"] + " → " + top_regeln["Konsequenz"], top_regeln[metriken], color="lightgreen")
    plt.xlabel(metriken)
    plt.title(f"Top 10 Regeln nach {metriken}")
    plt.gca().invert_yaxis()
    filename = os.path.join(output_path, f'top_regeln_{metriken.lower().replace(" ", "_")}.png')
    plt.savefig(filename)
    plt.show()

# Die Hauptfunktion steuert den Ablauf des Programms: Laden der Daten, Berechnung der Itemsets und Regeln,
# sowie Speichern und Visualisieren der Ergebnisse.
def main():
    file_path = 'Daten/cleaned_data.csv'
    base_output_path = 'Daten/Ergebnisse/'
    output_path = erstelle_ausgabe_ordner(base_output_path)

    daten = lade_daten(file_path)
    min_support, min_confidence = eingabe_parameter()

    itemsets_df = berechne_itemsets(daten, min_support)
    speichere_csv(itemsets_df, os.path.join(output_path, 'itemsets.csv'))

    itemsets = [(tuple(itemset), support / 100) for itemset, support in itemsets_df.values]
    regeln_df = generiere_regeln(itemsets, daten, min_confidence)
    speichere_csv(regeln_df, os.path.join(output_path, 'regeln.csv'))

    visualisiere_itemsets(itemsets_df, output_path)
    visualisiere_verteilung_items(daten, output_path)
    visualisiere_top_regeln(regeln_df, output_path, metriken="Konfidenz (%)")

if __name__ == "__main__":
    main()
