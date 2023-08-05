# -*- coding: utf-8 -*-
"""
Created on Wed Apr 12 00:09:28 2023

@author: Arsene Siewe Towoua

"""

# This string extracts specifiqued PM2.5 and PM10 particle and wind speed data in a CSV table containing several data sets. 
#3 tables are then created for PM2.5, PM10 and wind speed respectively.
#data from 2021-12-27 to 2023-03-22
#the data is arranged chronologically. 

import csv
import pandas as pd
import os

# Open the CSV file in read mode
with open('wetter.csv', encoding='utf-8') as csvfile:
    
    # Create a csv.reader object
    reader = csv.reader(csvfile)
    
    # Read the first line to obtain the column names
    headers = next(reader)   
#    print(headers)
    
    # Find the index for the "Specie" column
    specie_index = headers.index('Specie')
    
    # Create a list to store filtered lines
    filtered_rows = []
    
    for row in reader:
        if 'pm10' in row[specie_index] or 'wind-speed' in row[specie_index] or 'pm25' in row[specie_index] or 'precipitation' in row[specie_index] or 'humidity' in row[specie_index]:
            filtered_rows.append(row)
            
      # Print filtered lines
    #for row in filtered_rows:
    #    print(row)        
        
# Open the new CSV file in write mode
    with open('filtered_rows.csv', 'w', newline='', encoding='utf-8') as f:
        # Create a csv.write object
        csv_writer = csv.writer(f)
        
        # Write the header to the new file
        csv_writer.writerow(headers)
        
        # Write the filtered lines to the new file
        for row in filtered_rows:
            csv_writer.writerow(row)        
        #print(row)
   
 # Open the CSV file in read mode
    with open('filtered_rows.csv', mode='r', newline='', encoding='utf-8') as file:
    
        # Read the CSV file using the CSV reader
        new_file = csv.reader(file)
    
        # Read the first line to obtain the column headers
        headers  = next(new_file)
    
        # Create a dictionary to store the grouped data
        grouped_data = {}

        # Browse each line of the CSV file
        for row in new_file:
            
            # Get the index for the "Spicie" column
            spicie_index = headers.index("Specie")
        
            
            # Check whether the value in the "Specie" column is "pm10", "wind-speed", "pm25", "humidity" or "precipitation".
            if row[spicie_index] in ["pm10", "wind-speed", "pm25", "precipitation", "humidity" ]:
                
                # Get the date of the line
                date = row[headers.index("Date")]
    
                # Add the line to the corresponding list in the dictionary
                if date not in grouped_data:
                    grouped_data[date] = []
                    
                    # Check if the date is between 1 January 2022 and 31 December 2022
                    #if '2022-01-01' <= date <= '2022-12-31':
                        
                grouped_data[date].append(row)
                
                            
        # Sort data
        sorted_data = []
        for date in sorted(grouped_data.keys()):
            sorted_data.extend(grouped_data[date])   
        
        # Sorting data by Spicie and Country columns
            sorted_data = sorted(sorted_data, key=lambda row: row[headers.index("Specie")])

        # Sort data by date
            #sorted_data = sorted(new_file, key=lambda row: row[headers.index("Date")])
        
        # Open a new CSV file in write mode
        with open('filtered_wetter_data.csv', mode='w', newline='', encoding='utf-8') as file_out:
        
            # Write column headers in the output file
            writer = csv.writer(file_out)
            writer.writerow(headers)
        
            # Write each sorted line to the output file
            for row in sorted_data:
                writer.writerow(row)   
#            print(row)
            
##################################################################################################
#data 2022 filtered

file_path = "filtered_wetter_data.csv"
df = pd.read_csv(file_path, encoding='utf-8')
df['Date'] = pd.to_datetime(df['Date'])
start_date = '2022-01-01'  # Replace this with your desired start date
end_date = '2022-12-31'    # Replace this with your desired end date

filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]
output_file_path = "filtered_wetter_data_2022.csv"
filtered_df.to_csv(output_file_path, index=False)
            
##########################################################################################
    #humidity-Daten
        
# Open the CSV file "filtered_wetter_data" in read mode
with open('filtered_wetter_data_2022.csv', mode='r', newline='', encoding='utf-8') as humidity_file:
    
    # Create a csv.reader object
    humidity = csv.reader(humidity_file)
    
    # Read the first line to obtain the column names
    headers = next(humidity)   
#    print(headers)
    
    # Find the index for the "Specie" column
    specie_index = headers.index('Specie')
   # date_index = headers.index('Date')
    
    #headers.pop(date_index)
    # Create a list to store filtered lines
    humidity_filtered_rows = []
 
    for row in humidity:
        #row.pop(date_index)
       #  del row[date_index]
        if 'humidity' in row[specie_index]: #or 'wind-speed' in row[specie_index] or 'pm25' in row[specie_index]:
            humidity_filtered_rows.append(row)
            
      # Print filtered lines
    #for row in humidity_filtered_rows:
        #print(row)        

    # Open the new CSV file in write mode
    with open('humidity_filtered_rows.csv', 'w', newline='', encoding='utf-8') as humidity_f:
            # Create a csv.writer object
        csv_writer = csv.writer(humidity_f)
            
            # Écrire l'en-tête dans le nouveau fichier
        csv_writer.writerow(headers)
            
            # Write the filtered lines to the new file
        for row in humidity_filtered_rows:
            csv_writer.writerow(row)        
            #print(row)

##########################################################################################
    #PM2.5-Daten
        
# Open the CSV file "filtered_wetter_data" in read mode
with open('filtered_wetter_data_2022.csv', mode='r', newline='', encoding='utf-8') as pm25_file:
    
    # Create a csv.reader object
    pm25 = csv.reader(pm25_file)
    
    # Read the first line to obtain the column names
    headers = next(pm25)   
#    print(headers)
    
    # Find the index for the "Specie" column
    specie_index = headers.index('Specie')
   # date_index = headers.index('Date')
    
    #headers.pop(date_index)
    # Create a list to store filtered lines
    pm25_filtered_rows = []
 
    for row in pm25:
        #row.pop(date_index)
       #  del row[date_index]
        if 'pm25' in row[specie_index]: #or 'wind-speed' in row[specie_index] or 'pm25' in row[specie_index]:
            pm25_filtered_rows.append(row)
            
      # Print filtered lines
    #for row in pm25_filtered_rows:
        #print(row)        

    # Open the new CSV file in write mode
    with open('pm25_filtered_rows.csv', 'w', newline='', encoding='utf-8') as pm25_f:
            # Create a csv.writer object
        csv_writer = csv.writer(pm25_f)
            
            # Écrire l'en-tête dans le nouveau fichier
        csv_writer.writerow(headers)
            
            # Write the filtered lines to the new file
        for row in pm25_filtered_rows:
            csv_writer.writerow(row)        
            #print(row)

################################################################################################    
     #PM10-Daten
# Open the CSV file "filtered_wetter_data" in read mode
with open('filtered_wetter_data_2022.csv', mode='r', newline='', encoding='utf-8') as pm10_file:
    
    # Create a csv.reader object
    pm10 = csv.reader(pm10_file)
    
    # Read the first line to obtain the column names
    headers = next(pm10)   
#    print(headers)
    
    # Find the index for the "Specie" column
    specie_index = headers.index('Specie')
    
    # Create a list to store filtered lines
    pm10_filtered_rows = []
      
    for row in pm10:
        if 'pm10' in row[specie_index]: #or 'wind-speed' in row[specie_index] or 'pm25' in row[specie_index]:
            pm10_filtered_rows.append(row)
            
      # Print filtered lines
    #for row in pm10_filtered_rows:
        #print(row)        

    # Open the new CSV file in write mode
    with open('pm10_filtered_rows.csv', 'w', newline='', encoding='utf-8') as pm10_f:
    # Create a csv.writer object
       csv_writer = csv.writer(pm10_f)
            
          # Write the header to the new file
       csv_writer.writerow(headers)
            
            # Write the filtered lines to the new file
       for row in pm10_filtered_rows:
           csv_writer.writerow(row)        
            #print(row)
            
            
############################################################################################### 
# Windgeschwindigkeitsdaten
# Open the CSV file "filtered_wetter_data" in read mode
with open('filtered_wetter_data_2022.csv', mode='r', newline='', encoding='utf-8') as wind_speed_file:
    
    # Create a csv.reader object
    wind_speed = csv.reader(wind_speed_file)
    
    # Read the first line to obtain the column names
    headers = next(wind_speed)   
#    print(headers)
    
    # Find the index for the "Specie" column
    specie_index = headers.index('Specie')
    
    # Create a list to store filtered lines
    wind_speed_filtered_rows = []
    
    for row in wind_speed:
        if 'wind-speed' in row[specie_index]: #or 'wind-speed' in row[specie_index] or 'pm25' in row[specie_index]:
            wind_speed_filtered_rows.append(row)
            
     # Print filtered lines
    #for row in wind_speed_filtered_rows:
        #print(row)        

    # Open the new CSV file in write mode
    with open('wind_speed_filtered_rows.csv', 'w', newline='', encoding='utf-8') as wind_speed_f:
            # Create a csv.writer object
        csv_writer = csv.writer(wind_speed_f)
            
            # Write the header to the new file
        csv_writer.writerow(headers)
            
            # Write the filtered lines to the new file
        for row in wind_speed_filtered_rows:
            csv_writer.writerow(row)        
            #print(row)

############################################################################################### 
# precipitation
# Open the CSV file "filtered_wetter_data" in read mode
with open('filtered_wetter_data_2022.csv', mode='r', newline='', encoding='utf-8') as precipitation_file:
    
    # Create a csv.reader object
    precipitation = csv.reader(precipitation_file)
    
    # Read the first line to obtain the column names
    headers = next(precipitation)   
#    print(headers)
    
    # Find the index for the "Specie" column
    specie_index = headers.index('Specie')
    
    # Create a list to store filtered lines
    precipitation_filtered_rows = []
    
    for row in precipitation:
        if 'precipitation' in row[specie_index]:
            precipitation_filtered_rows.append(row)
            
     # Print filtered lines
    #for row in precipitation_filtered_rows:
        #print(row)        

    # Open the new CSV file in write mode
    with open('precipitation_filtered_rows.csv', 'w', newline='', encoding='utf-8') as precipitation_f:
            # Create a csv.writer object
        csv_writer = csv.writer(precipitation_f)
            
            # Write the header to the new file
        csv_writer.writerow(headers)
            
            # Write the filtered lines to the new file
        for row in precipitation_filtered_rows:
            csv_writer.writerow(row)        
            #print(row)    


###########################################################################################################################################################################################
#this part of the code retrieves the previously saved tables and calculates the average value for each identical combination [Country,City]. 
#Finally, a csv table of each data will be saved. 

import pandas as pd

#################################################
#humidity-Values
#Load data from the file "humidity_filtered_rows" into a DataFrame
df_humidity_filtered_rows = pd.read_csv('humidity_filtered_rows.csv', encoding='latin-1')

# Corrected incorrectly coded characters in the "City" column.
df_humidity_filtered_rows['City'] = df_humidity_filtered_rows['City'].apply(lambda x: x.encode('latin-1').decode('utf-8'))

# Delete the columns "date" and "count"
df_humidity_filtered_rows.drop(['Date', 'count'], axis=1, inplace=True)

# Create a new DataFrame to store the average values
df_humidity_filtered_rows_means = pd.DataFrame(columns=['Country', 'City', 'min', 'max', 'median', 'variance'])

# For each combination of country and city calculate the mean values
for (country, city), group in df_humidity_filtered_rows.groupby(['Country', 'City']):
    minimum = group['min'].mean()
    maximum = group['max'].mean()
    median = group['median'].mean()
    variance = group['variance'].mean()
    df_humidity_filtered_rows_means = df_humidity_filtered_rows_means.append({'Country': country, 'City': city, 'min': minimum, 'max': maximum, 'median': median, 'variance': variance}, ignore_index=True)

# Merge the columns "City" and "Country" into a new column with the name "City, Country".
df_humidity_filtered_rows_means['City, Country'] = df_humidity_filtered_rows_means["City"] + ", " + df_humidity_filtered_rows_means["Country"]

# Delete the "City" and "Country" columns
df_humidity_filtered_rows_means.drop(columns=["City", "Country"], inplace=True)

# Change the position of the columns "Country" and "City".
df_humidity_filtered_rows_means = df_humidity_filtered_rows_means[['City, Country', 'min', 'max', 'median', 'variance']]

# Saves the new DataFrame as a CSV file.
df_humidity_filtered_rows_means.to_csv('humidity_means.csv', index=False)

# print the DataFrame with the average values
#print(df_humidity_filtered_rows_means)

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
df_wind_speed_filtered_rows = pd.read_csv('wind_speed_filtered_rows.csv', encoding='latin-1')

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


##########################################################
#precipitation-Values

#Load data from the file "precipitation_filtered_rows" into a DataFrame.
df_precipitation_filtered_rows = pd.read_csv('precipitation_filtered_rows.csv', encoding='latin-1')

# Corrected incorrectly coded characters in the "City" column.
df_precipitation_filtered_rows['City'] = df_precipitation_filtered_rows['City'].apply(lambda x: x.encode('latin-1').decode('utf-8'))

# Delete the columns "date" and "count"
df_precipitation_filtered_rows.drop(['Date', 'count'], axis=1, inplace=True)

# Create a new DataFrame to store the average values
df_precipitation_filtered_rows_means = pd.DataFrame(columns=['Country', 'City', 'min', 'max', 'median', 'variance'])

# For each combination of country and city calculate the mean values
for (country, city), group in df_precipitation_filtered_rows.groupby(['Country', 'City']):
    minimum = group['min'].mean()
    maximum = group['max'].mean()
    median = group['median'].mean()
    variance = group['variance'].mean()
    df_precipitation_filtered_rows_means = df_precipitation_filtered_rows_means.append({'Country': country, 'City': city, 'min': minimum, 'max': maximum, 'median': median, 'variance': variance}, ignore_index=True)

# Merge the columns "City" and "Country" into a new column with the name "City, Country".
df_precipitation_filtered_rows_means['City, Country'] = df_precipitation_filtered_rows_means["City"] + ", " + df_precipitation_filtered_rows_means["Country"]

# Delete the "City" and "Country" columns
df_precipitation_filtered_rows_means.drop(columns=["City", "Country"], inplace=True)

# Change the position of the columns "Country" and "City".
df_precipitation_filtered_rows_means = df_precipitation_filtered_rows_means[['City, Country', 'min', 'max', 'median', 'variance']]

# Saves the new DataFrame as a CSV file.
df_precipitation_filtered_rows_means.to_csv('precipitation_means.csv', index=False)

# print the DataFrame with the average values
#print(df_precipitation_filtered_rows_means)



###########################################################################################################################################################################################
#In this part of the Code the PM10, PM2,5, precipitation humidity and wind speed values are inserted in a common file. 
#At the end a Table is obtained with all the values needed to calculate the Soiling according to the location. 

import pandas as pd

# Lecture des fichiers CSV
F1 = pd.read_csv("soilingrate_coordinates_data_2022.csv")
F2 = pd.read_csv("pm10_means.csv")
F3 = pd.read_csv("wind_speed_means.csv")
F4 = pd.read_csv("pm25_means.csv")
F5 = pd.read_csv("precipitation_means.csv")
F6 = pd.read_csv("humidity_means.csv")


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
#new_table_10.to_csv("new_10.csv", index=False)

#humidity
F_humidity = new_table_10
# Merge the two DataFrames using the "City" and "Country" columns
merged_humidity = pd.merge(F_humidity, F6, on=["City, Country"], how="left")

# Replacing missing values with 0 in the "median" column
merged_humidity["median"] = merged_humidity["median"].fillna(0)

# Creation of a new DataFrame with F_humidity columns
new_table_humidity = F_humidity.copy()

# Addition of the "humidity" column with the values from the merged_humidity "median" column
new_table_humidity["humidity"] = merged_humidity["median"].values

# Missing values replaced by 0 in the "humidity" column
new_table_humidity["humidity"] = new_table_humidity["humidity"].fillna(0)

# Save the new DataFrame in CSV format
#new_table_humidity.to_csv("new_humidity.csv", index=False)

#precipitation
F_precipitation = new_table_humidity
# Merge the two DataFrames using the "City" and "Country" columns
merged_precipitation = pd.merge(F_precipitation, F5, on=["City, Country"], how="left")

# Replacing missing values with 0 in the "median" column
merged_precipitation["median"] = merged_precipitation["median"].fillna(0)

# Creation of a new DataFrame with F_precipitation columns
new_table_precipitation = F_precipitation.copy()

# Addition of the "precipitation" column with the values from the merged_precipitation "median" column
new_table_precipitation["precipitation"] = merged_precipitation["median"].values

# Missing values replaced by 0 in the "precipitation" column
new_table_precipitation["precipitation"] = new_table_precipitation["precipitation"].fillna(0)

# Save the new DataFrame in CSV format
#new_table_precipitation.to_csv("new_precipitation.csv", index=False)

###PM2_5
F_25 = new_table_precipitation
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
new_table_X = new_table_X[['City, Country', 'AQI_PM2_5', 'PM2_5', 'PM10', 'wind_speed', 'humidity', 'precipitation', 'Soiling_Rate', 'lat', 'lng']]

# Save the new DataFrame in CSV format
new_table_X.to_csv("soiling_data.csv", index=False)

#print(new_table_X)


##########################################################################################
#In this part of the code, climate data filtered and sorted by date will be filtered again, 
#and for the rest of the calculations we'll just keep the median value of all the data types, 
#and the data will be saved according to the cities. These cities will be saved in the "city_data_1" folder. 
#Finally, the type of data for each city will be reorganised so that it is usable. These cities will be saved in the "city_data_2" folder.



#Read the CSV file into a pandas DataFrame
file_path = "filtered_wetter_data_2022.csv"
df = pd.read_csv(file_path, encoding='utf-8')

#Convert the "Date" column to datetime format:
df['Date'] = pd.to_datetime(df['Date'])

#Create a new DataFrame to store the data for each city:
city_data_dict = {}

#Group the data by "City" and iterate through each city to 
#create separate DataFrames and save them in the dictionary:
for city, city_data in df.groupby('City'):
    city_country = city_data['Country'].iloc[0]
    new_table = city_data.drop(columns=['count', 'min', 'max', 'variance', 'Country', 'City'])
    new_table = new_table.sort_values(by='Date')
    city_data_dict[f"{city}, {city_country}"] = new_table

#Create a new directory "city_data_1" to store the CSV files for each city:
output_directory = "city_data_1"
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

#Save each city's data as a separate CSV file in the "city_data_1" directory:
for city_name, city_data in city_data_dict.items():
    file_name = f"{output_directory}/{city_name}.csv"
    city_data.to_csv(file_name, index=False)

###############################not necessary##########################################
#Finally, save the new table with cities aggregated together 
#(without the specified columns) as a new CSV file:
#new_table_path = "new_filtered_wetter_data.csv"
#aggregated_df = df.drop(columns=['count', 'min', 'max', 'variance', 'Country'])
#aggregated_df.to_csv(new_table_path, index=False)
##################################################################################

####to create a new table that contains the columns "Date" and 
#the different species, with their corresponding median values:

#Create a list of the species you want in the final table:
desired_species = ["pm25", "pm10", "wind-speed", "humidity", "precipitation"]

#Create a new DataFrame to store the final species data for each city:
city_final_species_dict = {}

#Iterate through each city's data and create a new DataFrame with species as columns, 
#with the final desired species:
for city_name, city_data in city_data_dict.items():
    species_table = pd.pivot_table(city_data, values='median', index='Date', columns='Specie', fill_value=0)
    final_species_table = species_table.reindex(columns=desired_species, fill_value=0)
    city_final_species_dict[city_name] = final_species_table

#Create a new directory "city_data_2" to store the CSV files for each city's final species data:
output_directory_2 = "city_data_2"
if not os.path.exists(output_directory_2):
    os.makedirs(output_directory_2)

#Save each city's final species data as a separate CSV file in the "city_data_2" directory:
for city_name, final_species_data in city_final_species_dict.items():
    file_name = f"{output_directory_2}/{city_name}.csv"
    final_species_data.to_csv(file_name)

