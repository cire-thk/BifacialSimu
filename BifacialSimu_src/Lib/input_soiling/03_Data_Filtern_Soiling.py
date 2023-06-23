# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 23:55:45 2023

@author: Arsene Siewe Towoua
"""
#In this Code the PM10, PM2,5 and wind speed values are inserted in a common file. 
#At the end a Table is obtained with all the values needed to calculate the Soiling according to the location. 

import pandas as pd

# Lecture des fichiers CSV
F1 = pd.read_csv("soilingrate_coordinates_data_2022.csv")
F2 = pd.read_csv("pm10_means.csv")
F3 = pd.read_csv("wind_speed_means.csv")
F4 = pd.read_csv("pm25_means.csv")

###PM10

# Merge the two DataFrames using the "City" and "Country" columns
merged = pd.merge(F1, F2, on=["City, Country"], how="left")

# Replacing missing values with 0 in the "median" column
merged["median"] = merged["median"].fillna(0)

# Creation of a new DataFrame with F_1 columns
new_table_10 = F1.copy()

# Addition of the "PM10" column with the values from the merged "median" column
new_table_10["PM10"] = merged["median"].values

# Missing values replaced by 0 in the "PM10" column
new_table_10["PM10"] = new_table_10["PM10"].fillna(0)

# Save the new DataFrame in CSV format
new_table_10.to_csv("new_10.csv", index=False)


###PM2_5
F_25 = new_table_10
# Merge the two DataFrames using the "City" and "Country" columns
merged_25 = pd.merge(F_25, F4, on=["City, Country"], how="left")

# Replacing missing values with 0 in the "median" column
merged_25["median"] = merged_25["median"].fillna(0)

# Creation of a new DataFrame with F_25 columns
new_table_25 = F_25.copy()

# Addition of the "PM_25" column with the values from the merged_25 "median" column
new_table_25["PM2_5"] = merged_25["median"].values

# Missing values replaced by 0 in the "PM2_5" column
new_table_25["PM2_5"] = new_table_25["PM2_5"].fillna(0)

# Save the new DataFrame in CSV format
#new_table_25.to_csv("new_25.csv", index=False)


###Windgeschwindigkeit

F_X = new_table_25
#print(F_X)

# Merge the two DataFrames using the "City" and "Country" columns
merged_X = pd.merge(F_X, F3, on=["City, Country"], how="left")

# Replacing missing values with 0 in the "median" column
merged_X["median"] = merged_X["median"].fillna(0)

# Creation of a new DataFrame with F_X columns
new_table_X = F_X.copy()

# Addition of the "wind_speed" column with the values from the "median" column in merged_X
new_table_X["wind_speed"] = merged_X["median"].values

# Replacing missing values with 0 in the "wind_speed" column
new_table_X["wind_speed"] = new_table_X["wind_speed"].fillna(0)

# Change the position of the columns
new_table_X = new_table_X[['City, Country', 'AQI_PM2_5', 'PM2_5', 'PM10', 'wind_speed', 'Soiling_Rate', 'lat', 'lng']]

# Save the new DataFrame in CSV format
new_table_X.to_csv("soiling_data.csv", index=False)

#print(new_table_X)

