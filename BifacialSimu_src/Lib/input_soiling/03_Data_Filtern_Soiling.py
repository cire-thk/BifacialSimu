import pandas as pd

# Lecture des fichiers CSV
F1 = pd.read_csv("soilingrate_coordinates_data_2022.csv")
F2 = pd.read_csv("pm10_means.csv")
F3 = pd.read_csv("wind_speed_means.csv")

###PM10

# Fusion des deux DataFrames en utilisant la colonne "City" et "Country"
merged = pd.merge(F1, F2, on=["City, Country"], how="left")

# Remplacement des valeurs manquantes par 0 dans la colonne "median"
merged["median"] = merged["median"].fillna(0)

# Création d'un nouveau DataFrame avec les colonnes de F1
new_table = F1.copy()

# Ajout de la colonne "PM10" avec les valeurs de la colonne "median" de merged
new_table["PM10"] = merged["median"].values

# Remplacement des valeurs manquantes par 0 dans la colonne "PM10"
new_table["PM10"] = new_table["PM10"].fillna(0)

# Enregistrer le nouveau DataFrame en format CSV
new_table.to_csv("new.csv", index=False)

###Windgeschwindigkeit

F_X = new_table
#print(F_X)

# Fusion des deux DataFrames en utilisant la colonne "City" et "Country"
merged_X = pd.merge(F_X, F3, on=["City, Country"], how="left")

# Remplacement des valeurs manquantes par 0 dans la colonne "median"
merged_X["median"] = merged_X["median"].fillna(0)

# Création d'un nouveau DataFrame avec les colonnes de F_X
new_table_X = F_X.copy()

# Ajout de la colonne "wind_speed" avec les valeurs de la colonne "median" de merged_X
new_table_X["wind_speed"] = merged_X["median"].values

# Remplacement des valeurs manquantes par 0 dans la colonne "wind_speed"
new_table_X["wind_speed"] = new_table_X["wind_speed"].fillna(0)

# Ändere die Position der Spalten
new_table_X = new_table_X[['City, Country', 'AQI_PM2_5', 'PM2_5', 'PM10', 'wind_speed', 'Soiling_Rate', 'lat', 'lng']]

# Enregistrer le nouveau DataFrame en format CSV
new_table_X.to_csv("new_soilingrate_coordinates_data_2022.csv", index=False)

print(new_table_X)


#import pandas as pd

#F1 = pd.read_csv("soilingrate_coordinates_data_2022.csv")
#F2 = pd.read_csv("pm10_means.csv")
#F3 = pd.read_csv("wind_speed_means.csv")

#Filtrer les lignes de F2 et F3 pour ne garder que les combinaisons de "City, Country" présentes dans F1.
#F2 = F2[F2["City, Country"].isin(F1["City, Country"])]
#F3 = F3[F3["City, Country"].isin(F1["City, Country"])]

#Fusionner les trois DataFrames en un seul en utilisant la méthode merge de pandas. Pour cela, vous devez spécifier la colonne de jointure qui est "City, Country".
#new_table = pd.merge(F1, F2, on="City, Country")
#new_table = pd.merge(new_table, F3, on="City, Country")

#Créer une nouvelle colonne "PM10" dans le nouveau DataFrame et y ajouter les valeurs 
#de la colonne "median" du fichier 2, et une nouvelle colonne "wind_speed" et y ajouter les valeurs 
#de la colonne "median" du fichier 3 correspondant aux combinaisons de "City, Country" présentes dans F1.
#new_table["PM10"] = F2[F2["City, Country"].isin(new_table["City, Country"])]["median"].values
#new_table["wind_speed"] = F3[F3["City, Country"].isin(new_table["City, Country"])]["median"].values

#Pour chaque combinaison "City, country" inexistante dans F1, ajouter une ligne 
#au nouveau tableau et attribuer la valeur 0 dans la colonne "PM10" et "wind_speed".
#for index, row in F1.iterrows():
#    if not new_table.loc[new_table["City, Country"] == row["City, Country"]].empty:
#        continue
#    new_row = pd.Series(row)
#    new_row["PM10"] = 0
#    new_row["wind_speed"] = 0
#    new_table = new_table.append(new_row, ignore_index=True)

#Enfin, sauvegarder le nouveau DataFrame sous forme de fichier CSV avec le nom "new".
#new_table.to_csv("new.csv", index=False)

#print(new_table)



#import pandas as pd

# Ouvrir les fichiers
#F1 = pd.read_csv('soilingrate_coordinates_data_2022.csv')
#F2 = pd.read_csv('pm10_means.csv')
#F3 = pd.read_csv('wind_speed_means.csv')

# Fusionner les données de F2 et F3 en utilisant la colonne "City, Country" comme clé de jointure
#F23 = pd.merge(F2, F3, on='City, Country', how='outer')

# Fusionner les données de F1 et F23 en utilisant la colonne "City, Country" comme clé de jointure
#new = pd.merge(F1, F23, on='City, Country', how='outer')

# Ajouter une nouvelle colonne "PM10" avec les valeurs de la colonne "median" de F2
#new['PM10'] = new['City, Country'].map(F2.set_index('City, Country')['median'])
#new['PM10'].fillna(0, inplace=True)

# Ajouter une nouvelle colonne "wind_speed" avec les valeurs de la colonne "median" de F3
#new['wind_speed'] = new['City, Country'].map(F3.set_index('City, Country')['median'])
#new['wind_speed'].fillna(0, inplace=True)

# Sauvegarder le nouveau tableau sous forme de fichier csv avec le nom "new"
#new.to_csv('new.csv', index=False)
