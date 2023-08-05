"""
@author: Arsene Siewe Towoua

"""

import pandas as pd

# Importer les fichiers CSV dans des DataFrames
df_accra = pd.read_csv('Accra, GH.csv')
df_data = pd.read_csv('Dataframe_df.csv')

# Convertir la colonne 'Date' en format de date pour les deux DataFrames
df_accra['Date'] = pd.to_datetime(df_accra['Date'], dayfirst=True)
df_data['corrected_timestamp'] = pd.to_datetime(df_data['corrected_timestamp'], dayfirst=True)

# Créer une liste vide pour stocker les valeurs de soilingrate correspondantes
PAPA = []

# Parcourir les lignes du DataFrame "Dataframe_df"
for index, row in df_data.iterrows():
    # Extraire la date (jour et mois) de la ligne en cours du DataFrame "Dataframe_df"
    date_data = row['corrected_timestamp'].replace(year=2023)  # Remplacer l'année par l'année appropriée
    
    # Filtrer le DataFrame "Accra, GH" pour obtenir les lignes ayant la même date (jour et mois)
    df_filtered = df_accra[(df_accra['Date'].dt.day == date_data.day) & (df_accra['Date'].dt.month == date_data.month)]
    
    # Vérifier si des lignes ont été trouvées dans le DataFrame filtré
    if not df_filtered.empty:
        # Récupérer la valeur de soilingrate de la première ligne correspondante
        soilingrate_value = df_filtered.iloc[0]['soilingrate']
        
        # Ajouter la valeur de soilingrate à la liste "PAPA"
        PAPA.append(soilingrate_value)
    else:
        # Ajouter une valeur par défaut (par exemple, 0) si aucune valeur de soilingrate correspondante n'a été trouvée
        PAPA.append(0)

# Afficher la liste "PAPA" contenant les valeurs de soilingrate correspondantes pour chaque jour et mois identiques
print(PAPA)
print(len(PAPA))


import os
import pandas as pd

# Définir le chemin absolu du fichier
file_path = "C:\\Users\\Arsene Siewe Towoua\\anaconda3\\envs\\soiling2\\Lib\\input_soiling\\city_data_soiling_accumulation\\Denver, US.csv"

# Vérifier si le fichier existe
if os.path.exists(file_path):
    df_city = pd.read_csv(file_path)
    # Faites ce que vous devez faire avec le DataFrame df_city ici
else:
    print(f"Le fichier '{file_path}' n'a pas été trouvé.")
