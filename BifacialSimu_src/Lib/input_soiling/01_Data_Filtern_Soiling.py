# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 00:09:28 2023

@author: Arsene Siewe Towoua
"""


###Pandas
#import pandas as pd

# Spécifiez l'encodage approprié pour votre fichier CSV
#df = pd.read_csv('wetter.csv', encoding='utf-8',  delimiter=';')


#premiere_ligne = df.iloc[3]
#derniere_ligne = df.tail(1).iloc[0]
#wind_speed_df = df[df['specie'].str.contains('wind-speed')]


#print(premiere_ligne)
#print(derniere_ligne)
#print(wind_speed_df)
#print(df.columns)
#print(df.columns.tolist())





import csv

# Ouvrir le fichier CSV en mode lecture
with open('wetter.csv', encoding='utf-8') as csvfile:
    
    # Créer un objet csv.reader
    reader = csv.reader(csvfile)
    
    # Lire la première ligne pour obtenir les noms de colonnes
    headers = next(reader)   
    print(headers)
    
    # Trouver l'index de la colonne "Specie"
    specie_index = headers.index('Specie')
    
    # Créer une liste pour stocker les lignes filtrées
    filtered_rows = []
    
    for row in reader:
        if 'pm10' in row[specie_index] or 'wind-speed' in row[specie_index] or 'pm25' in row[specie_index]:
            filtered_rows.append(row)
            
      # Imprimer les lignes filtrées
    #for row in filtered_rows:
    #    print(row)        
        
# Ouvrir le nouveau fichier CSV en mode écriture
    with open('filtered_rows.csv', 'w', newline='', encoding='utf-8') as f:
        # Créer un objet csv.writer
        csv_writer = csv.writer(f)
        
        # Écrire l'en-tête dans le nouveau fichier
        csv_writer.writerow(headers)
        
        # Écrire les lignes filtrées dans le nouveau fichier
        for row in filtered_rows:
            csv_writer.writerow(row)        
        #print(row)
   
 # Ouvrir le fichier CSV en mode lecture
    with open('filtered_rows.csv', mode='r', newline='', encoding='utf-8') as file:
    
        # Lire le fichier CSV en utilisant le lecteur CSV
        new_file = csv.reader(file)
    
        # Lire la première ligne pour obtenir les en-têtes de colonne
        headers  = next(new_file)
    
        # Créer un dictionnaire pour stocker les données regroupées
        grouped_data = {}

        # Parcourir chaque ligne du fichier CSV
        for row in new_file:
            
            # Obtenir l'index de la colonne "Spicie"
            spicie_index = headers.index("Specie")
        
            
            # Vérifier si la valeur de la colonne "Specie" est "pm10", "wind-speed" ou "pm25"
            if row[spicie_index] in ["pm10", "wind-speed", "pm25"]:
                
                # Obtenir la date de la ligne
                date = row[headers.index("Date")]
    
                # Ajouter la ligne à la liste correspondante dans le dictionnaire
                if date not in grouped_data:
                    grouped_data[date] = []
                    
                    # Vérifier si la date est comprise entre le 1er janvier 2022 et le 31 décembre 2022
                    #if '2022-01-01' <= date <= '2022-12-31':
                        
                grouped_data[date].append(row)
                
                            
        # Trier les données en fonction des dates
        sorted_data = []
        for date in sorted(grouped_data.keys()):
            sorted_data.extend(grouped_data[date])   
        
        # Tri des données en fonction des colonnes Spicie et Country
            sorted_data = sorted(sorted_data, key=lambda row: row[headers.index("Specie")])

        # Trier les données en fonction des dates
            #sorted_data = sorted(new_file, key=lambda row: row[headers.index("Date")])
        
        # Ouvrir un nouveau fichier CSV en mode écriture
        with open('filtered_wetter_data.csv', mode='w', newline='', encoding='utf-8') as file_out:
        
            # Écrire les en-têtes de colonne dans le fichier de sortie
            writer = csv.writer(file_out)
            writer.writerow(headers)
        
            # Écrire chaque ligne triée dans le fichier de sortie
            for row in sorted_data:
                writer.writerow(row)   
            print(row)
            
            
##########################################################################################
    #PM2.5-Daten
        
# Ouvrir le fichier CSV en mode lecture
with open('filtered_wetter_data.csv', mode='r', newline='', encoding='utf-8') as pm25_file:
    
    # Créer un objet csv.reader
    pm25 = csv.reader(pm25_file)
    
    # Lire la première ligne pour obtenir les noms de colonnes
    headers = next(pm25)   
    print(headers)
    
    # Trouver l'index de la colonne "Specie"
    specie_index = headers.index('Specie')
   # date_index = headers.index('Date')
    
    #headers.pop(date_index)
    # Créer une liste pour stocker les lignes filtrées
    pm25_filtered_rows = []
 
    for row in pm25:
        #row.pop(date_index)
       #  del row[date_index]
        if 'pm25' in row[specie_index]: #or 'wind-speed' in row[specie_index] or 'pm25' in row[specie_index]:
            pm25_filtered_rows.append(row)
            
      # Imprimer les lignes filtrées
    #for row in pm25_filtered_rows:
        #print(row)        

    # Ouvrir le nouveau fichier CSV en mode écriture
    with open('pm25_filtered_rows.csv', 'w', newline='', encoding='utf-8') as pm25_f:
            # Créer un objet csv.writer
        csv_writer = csv.writer(pm25_f)
            
            # Écrire l'en-tête dans le nouveau fichier
        csv_writer.writerow(headers)
            
            # Écrire les lignes filtrées dans le nouveau fichier
        for row in pm25_filtered_rows:
            csv_writer.writerow(row)        
            #print(row)

################################################################################################    
     #PM10-Daten
# Ouvrir le fichier CSV en mode lecture
with open('filtered_wetter_data.csv', mode='r', newline='', encoding='utf-8') as pm10_file:
    
    # Créer un objet csv.reader
    pm10 = csv.reader(pm10_file)
    
    # Lire la première ligne pour obtenir les noms de colonnes
    headers = next(pm10)   
    print(headers)
    
    # Trouver l'index de la colonne "Specie"
    specie_index = headers.index('Specie')
    
    # Créer une liste pour stocker les lignes filtrées
    pm10_filtered_rows = []
      
    for row in pm10:
        if 'pm10' in row[specie_index]: #or 'wind-speed' in row[specie_index] or 'pm25' in row[specie_index]:
            pm10_filtered_rows.append(row)
            
      # Imprimer les lignes filtrées
    #for row in pm10_filtered_rows:
        #print(row)        

    # Ouvrir le nouveau fichier CSV en mode écriture
    with open('pm10_filtered_rows.csv', 'w', newline='', encoding='utf-8') as pm10_f:
    # Créer un objet csv.writer
       csv_writer = csv.writer(pm10_f)
            
          # Écrire l'en-tête dans le nouveau fichier
       csv_writer.writerow(headers)
            
            # Écrire les lignes filtrées dans le nouveau fichier
       for row in pm10_filtered_rows:
           csv_writer.writerow(row)        
            #print(row)
            
            
############################################################################################### 
# Windgeschwindigkeitsdaten
# Ouvrir le fichier CSV en mode lecture
with open('filtered_wetter_data.csv', mode='r', newline='', encoding='utf-8') as wind_speed_file:
    
    # Créer un objet csv.reader
    wind_speed = csv.reader(wind_speed_file)
    
    # Lire la première ligne pour obtenir les noms de colonnes
    headers = next(wind_speed)   
    print(headers)
    
    # Trouver l'index de la colonne "Specie"
    specie_index = headers.index('Specie')
    
    # Créer une liste pour stocker les lignes filtrées
    wind_speed_filtered_rows = []
    
    for row in wind_speed:
        if 'wind-speed' in row[specie_index]: #or 'wind-speed' in row[specie_index] or 'pm25' in row[specie_index]:
            wind_speed_filtered_rows.append(row)
            
     # Imprimer les lignes filtrées
    #for row in wind_speed_filtered_rows:
        #print(row)        

    # Ouvrir le nouveau fichier CSV en mode écriture
    with open('wind_speed_filtered_rows.csv', 'w', newline='', encoding='utf-8') as wind_speed_f:
            # Créer un objet csv.writer
        csv_writer = csv.writer(wind_speed_f)
            
            # Écrire l'en-tête dans le nouveau fichier
        csv_writer.writerow(headers)
            
            # Écrire les lignes filtrées dans le nouveau fichier
        for row in wind_speed_filtered_rows:
            csv_writer.writerow(row)        
            #print(row)
    
