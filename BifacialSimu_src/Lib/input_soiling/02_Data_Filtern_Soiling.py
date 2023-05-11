# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 11:11:52 2023

@author: Arsene Siewe Towoua
"""

import pandas as pd


#################################################
#PM25-Values
#Daten aus der Datei "pm25_filtered_rows" in einen DataFrame laden
df_pm25_filtered_rows = pd.read_csv('pm25_filtered_rows.csv', encoding='latin-1')

# Korrigierte falsch kodierte Zeichen in der Spalte "Stadt".
df_pm25_filtered_rows['City'] = df_pm25_filtered_rows['City'].apply(lambda x: x.encode('latin-1').decode('utf-8'))

# Lösche die Spalten "date" und "count".
df_pm25_filtered_rows.drop(['Date', 'count'], axis=1, inplace=True)

# Erstellen eines neuen DataFrame zum Speichern der Durchschnittswerte
df_pm25_filtered_rows_means = pd.DataFrame(columns=['Country', 'City', 'min', 'max', 'median', 'variance'])

# Für jede Kombination aus Land und Stadt berechnen Sie die Mittelwerte
for (country, city), group in df_pm25_filtered_rows.groupby(['Country', 'City']):
    minimum = group['min'].mean()
    maximum = group['max'].mean()
    median = group['median'].mean()
    variance = group['variance'].mean()
    df_pm25_filtered_rows_means = df_pm25_filtered_rows_means.append({'Country': country, 'City': city, 'min': minimum, 'max': maximum, 'median': median, 'variance': variance}, ignore_index=True)

# Verschmelze die Spalten "City" und "Country" zu einer neuen Spalte mit dem Namen "City, Country".
df_pm25_filtered_rows_means['City, Country'] = df_pm25_filtered_rows_means["City"] + ", " + df_pm25_filtered_rows_means["Country"]

# Supprimer les colonnes "City" et "Country"
df_pm25_filtered_rows_means.drop(columns=["City", "Country"], inplace=True)

# Ändere die Position der Spalten "Country" und "City".
df_pm25_filtered_rows_means = df_pm25_filtered_rows_means[['City, Country', 'min', 'max', 'median', 'variance']]

# Speichert den neuen DataFrame als CSV-Datei in einem Ordner "output".
df_pm25_filtered_rows_means.to_csv('pm25_means.csv', index=False)

# Anzeige des DataFrame mit den Durchschnittswerten
print(df_pm25_filtered_rows_means)

#################################################
#PM10-Values

#Daten aus der Datei "pm10_filtered_rows" in einen DataFrame laden
df_pm10_filtered_rows = pd.read_csv('pm10_filtered_rows.csv', encoding='latin-1')

# Korrigierte falsch kodierte Zeichen in der Spalte "Stadt".
df_pm10_filtered_rows['City'] = df_pm10_filtered_rows['City'].apply(lambda x: x.encode('latin-1').decode('utf-8'))

# Lösche die Spalten "date" und "count".
df_pm10_filtered_rows.drop(['Date', 'count'], axis=1, inplace=True)

# Erstellen eines neuen DataFrame zum Speichern der Durchschnittswerte
df_pm10_filtered_rows_means = pd.DataFrame(columns=['Country', 'City', 'min', 'max', 'median', 'variance'])

# Für jede Kombination aus Land und Stadt berechnen Sie die Mittelwerte
for (country, city), group in df_pm10_filtered_rows.groupby(['Country', 'City']):
    minimum = group['min'].mean()
    maximum = group['max'].mean()
    median = group['median'].mean()
    variance = group['variance'].mean()
    df_pm10_filtered_rows_means = df_pm10_filtered_rows_means.append({'Country': country, 'City': city, 'min': minimum, 'max': maximum, 'median': median, 'variance': variance}, ignore_index=True)

# Verschmelze die Spalten "City" und "Country" zu einer neuen Spalte mit dem Namen "City, Country".
df_pm10_filtered_rows_means['City, Country'] = df_pm10_filtered_rows_means["City"] + ", " + df_pm10_filtered_rows_means["Country"]

# Supprimer les colonnes "City" et "Country"
df_pm10_filtered_rows_means.drop(columns=["City", "Country"], inplace=True)

# Ändere die Position der Spalten "Country" und "City".
df_pm10_filtered_rows_means = df_pm10_filtered_rows_means[['City, Country', 'min', 'max', 'median', 'variance']]


# Speichert den neuen DataFrame als CSV-Datei in einem Ordner "output".
df_pm10_filtered_rows_means.to_csv('pm10_means.csv', index=False)

# Anzeige des DataFrame mit den Durchschnittswerten
print(df_pm10_filtered_rows_means)


##########################################################
#Windgeschwindigkeit-Values

#Daten aus der Datei "wind_speed_filtered_rows" in einen DataFrame laden
df_wind_speed_filtered_rows = pd.read_csv('pm25_filtered_rows.csv', encoding='latin-1')

# Korrigierte falsch kodierte Zeichen in der Spalte "Stadt".
df_wind_speed_filtered_rows['City'] = df_wind_speed_filtered_rows['City'].apply(lambda x: x.encode('latin-1').decode('utf-8'))

# Lösche die Spalten "date" und "count".
df_wind_speed_filtered_rows.drop(['Date', 'count'], axis=1, inplace=True)

# Erstellen eines neuen DataFrame zum Speichern der Durchschnittswerte
df_wind_speed_filtered_rows_means = pd.DataFrame(columns=['Country', 'City', 'min', 'max', 'median', 'variance'])

# Für jede Kombination aus Land und Stadt berechnen Sie die Mittelwerte
for (country, city), group in df_wind_speed_filtered_rows.groupby(['Country', 'City']):
    minimum = group['min'].mean()
    maximum = group['max'].mean()
    median = group['median'].mean()
    variance = group['variance'].mean()
    df_wind_speed_filtered_rows_means = df_wind_speed_filtered_rows_means.append({'Country': country, 'City': city, 'min': minimum, 'max': maximum, 'median': median, 'variance': variance}, ignore_index=True)

# Verschmelze die Spalten "City" und "Country" zu einer neuen Spalte mit dem Namen "City, Country".
df_wind_speed_filtered_rows_means['City, Country'] = df_wind_speed_filtered_rows_means["City"] + ", " + df_wind_speed_filtered_rows_means["Country"]

# Supprimer les colonnes "City" et "Country"
df_wind_speed_filtered_rows_means.drop(columns=["City", "Country"], inplace=True)

# Ändere die Position der Spalten "Country" und "City".
df_wind_speed_filtered_rows_means = df_wind_speed_filtered_rows_means[['City, Country', 'min', 'max', 'median', 'variance']]

# Speichert den neuen DataFrame als CSV-Datei in einem Ordner "output".
df_wind_speed_filtered_rows_means.to_csv('wind_speed_means.csv', index=False)

# Anzeige des DataFrame mit den Durchschnittswerten
print(df_wind_speed_filtered_rows_means)









