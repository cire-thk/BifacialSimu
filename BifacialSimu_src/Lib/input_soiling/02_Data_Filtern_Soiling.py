# -*- coding: utf-8 -*-
"""
Created on Sun Apr 23 11:11:52 2023

@author: Arsene Siewe Towoua
"""

#this code retrieves the previously saved tables and calculates the average value for each identical combination [Country,City]. 
#Finally, a csv table of each data will be saved. 

import pandas as pd


#################################################
#PM25-Values
#Load data from the file "pm25_filtered_rows" into a DataFrame
df_pm25_filtered_rows = pd.read_csv('pm25_filtered_rows.csv', encoding='latin-1')

# Corrected incorrectly coded characters in the "City" column.
df_pm25_filtered_rows['City'] = df_pm25_filtered_rows['City'].apply(lambda x: x.encode('latin-1').decode('utf-8'))

# Delete the columns "date" and "count"
df_pm25_filtered_rows.drop(['Date', 'count'], axis=1, inplace=True)

# Create a new DataFrame to store the average values
df_pm25_filtered_rows_means = pd.DataFrame(columns=['Country', 'City', 'min', 'max', 'median', 'variance'])

# For each combination of country and city calculate the mean values
for (country, city), group in df_pm25_filtered_rows.groupby(['Country', 'City']):
    minimum = group['min'].mean()
    maximum = group['max'].mean()
    median = group['median'].mean()
    variance = group['variance'].mean()
    df_pm25_filtered_rows_means = df_pm25_filtered_rows_means.append({'Country': country, 'City': city, 'min': minimum, 'max': maximum, 'median': median, 'variance': variance}, ignore_index=True)

# Merge the columns "City" and "Country" into a new column with the name "City, Country".
df_pm25_filtered_rows_means['City, Country'] = df_pm25_filtered_rows_means["City"] + ", " + df_pm25_filtered_rows_means["Country"]

# Delete the "City" and "Country" columns
df_pm25_filtered_rows_means.drop(columns=["City", "Country"], inplace=True)

# Change the position of the columns "Country" and "City".
df_pm25_filtered_rows_means = df_pm25_filtered_rows_means[['City, Country', 'min', 'max', 'median', 'variance']]

# Saves the new DataFrame as a CSV file.
df_pm25_filtered_rows_means.to_csv('pm25_means.csv', index=False)

# print the DataFrame with the average values
#print(df_pm25_filtered_rows_means)

#################################################
#PM10-Values

#Load data from the file "pm10_filtered_rows" into a DataFrame
df_pm10_filtered_rows = pd.read_csv('pm10_filtered_rows.csv', encoding='latin-1')

# Corrected incorrectly coded characters in the "City" column.
df_pm10_filtered_rows['City'] = df_pm10_filtered_rows['City'].apply(lambda x: x.encode('latin-1').decode('utf-8'))

# Delete the columns "date" and "count"
df_pm10_filtered_rows.drop(['Date', 'count'], axis=1, inplace=True)

# Create a new DataFrame to store the average values
df_pm10_filtered_rows_means = pd.DataFrame(columns=['Country', 'City', 'min', 'max', 'median', 'variance'])

# For each combination of country and city calculate the mean values
for (country, city), group in df_pm10_filtered_rows.groupby(['Country', 'City']):
    minimum = group['min'].mean()
    maximum = group['max'].mean()
    median = group['median'].mean()
    variance = group['variance'].mean()
    df_pm10_filtered_rows_means = df_pm10_filtered_rows_means.append({'Country': country, 'City': city, 'min': minimum, 'max': maximum, 'median': median, 'variance': variance}, ignore_index=True)

# Merge the columns "City" and "Country" into a new column with the name "City, Country".
df_pm10_filtered_rows_means['City, Country'] = df_pm10_filtered_rows_means["City"] + ", " + df_pm10_filtered_rows_means["Country"]

# Delete the "City" and "Country" columns
df_pm10_filtered_rows_means.drop(columns=["City", "Country"], inplace=True)

# Change the position of the columns "Country" and "City".
df_pm10_filtered_rows_means = df_pm10_filtered_rows_means[['City, Country', 'min', 'max', 'median', 'variance']]


# Saves the new DataFrame as a CSV file.
df_pm10_filtered_rows_means.to_csv('pm10_means.csv', index=False)

# print the DataFrame with the average values
#print(df_pm10_filtered_rows_means)


##########################################################
#Windgeschwindigkeit-Values

#Load data from the file "wind_speed_filtered_rows" into a DataFrame.
df_wind_speed_filtered_rows = pd.read_csv('pm25_filtered_rows.csv', encoding='latin-1')

# Corrected incorrectly coded characters in the "City" column.
df_wind_speed_filtered_rows['City'] = df_wind_speed_filtered_rows['City'].apply(lambda x: x.encode('latin-1').decode('utf-8'))

# Delete the columns "date" and "count"
df_wind_speed_filtered_rows.drop(['Date', 'count'], axis=1, inplace=True)

# Create a new DataFrame to store the average values
df_wind_speed_filtered_rows_means = pd.DataFrame(columns=['Country', 'City', 'min', 'max', 'median', 'variance'])

# For each combination of country and city calculate the mean values
for (country, city), group in df_wind_speed_filtered_rows.groupby(['Country', 'City']):
    minimum = group['min'].mean()
    maximum = group['max'].mean()
    median = group['median'].mean()
    variance = group['variance'].mean()
    df_wind_speed_filtered_rows_means = df_wind_speed_filtered_rows_means.append({'Country': country, 'City': city, 'min': minimum, 'max': maximum, 'median': median, 'variance': variance}, ignore_index=True)

# Merge the columns "City" and "Country" into a new column with the name "City, Country".
df_wind_speed_filtered_rows_means['City, Country'] = df_wind_speed_filtered_rows_means["City"] + ", " + df_wind_speed_filtered_rows_means["Country"]

# Delete the "City" and "Country" columns
df_wind_speed_filtered_rows_means.drop(columns=["City", "Country"], inplace=True)

# Change the position of the columns "Country" and "City".
df_wind_speed_filtered_rows_means = df_wind_speed_filtered_rows_means[['City, Country', 'min', 'max', 'median', 'variance']]

# Saves the new DataFrame as a CSV file.
df_wind_speed_filtered_rows_means.to_csv('wind_speed_means.csv', index=False)

# print the DataFrame with the average values
#print(df_wind_speed_filtered_rows_means)









