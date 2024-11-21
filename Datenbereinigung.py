import pandas as pd

# Originaldatei laden
file_path = 'Daten/data.csv'
data = pd.read_csv(file_path)

# Nur relevante Spalten auswählen
data = data[['title', 'type', 'genres', 'releaseYear']]

# Null-Werte entfernen
data = data.dropna(subset=['genres'])

# Genres spalten und in binäres Format umwandeln
genres_split = data['genres'].str.get_dummies(sep=', ')

# Daten zusammenfügen
cleaned_data = pd.concat([data[['title', 'type', 'releaseYear']].reset_index(drop=True), genres_split], axis=1)

# Index hinzufügen und benennen
cleaned_data.reset_index(inplace=True)
cleaned_data.rename(columns={'index': 'ID'}, inplace=True)

# Ergebnis speichern
output_path = 'Daten/cleaned_data.csv'
cleaned_data.to_csv(output_path, index=False)

print(f"Die optimierten bereinigten Daten wurden gespeichert: {output_path}")
