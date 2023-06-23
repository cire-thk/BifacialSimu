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

# Open the CSV file in read mode
with open('wetter.csv', encoding='utf-8') as csvfile:
    
    # Create a csv.reader object
    reader = csv.reader(csvfile)
    
    # Read the first line to obtain the column names
    headers = next(reader)   
    print(headers)
    
    # Find the index for the "Specie" column
    specie_index = headers.index('Specie')
    
    # Create a list to store filtered lines
    filtered_rows = []
    
    for row in reader:
        if 'pm10' in row[specie_index] or 'wind-speed' in row[specie_index] or 'pm25' in row[specie_index]:
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
        
            
            # Check whether the value in the "Specie" column is "pm10", "wind-speed" or "pm25".
            if row[spicie_index] in ["pm10", "wind-speed", "pm25"]:
                
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
            print(row)
            
            
##########################################################################################
    #PM2.5-Daten
        
# Open the CSV file "filtered_wetter_data" in read mode
with open('filtered_wetter_data.csv', mode='r', newline='', encoding='utf-8') as pm25_file:
    
    # Create a csv.reader object
    pm25 = csv.reader(pm25_file)
    
    # Read the first line to obtain the column names
    headers = next(pm25)   
    print(headers)
    
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
            # Créer un objet csv.writer
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
with open('filtered_wetter_data.csv', mode='r', newline='', encoding='utf-8') as pm10_file:
    
    # Create a csv.reader object
    pm10 = csv.reader(pm10_file)
    
    # Read the first line to obtain the column names
    headers = next(pm10)   
    print(headers)
    
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
    # Créer un objet csv.writer
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
with open('filtered_wetter_data.csv', mode='r', newline='', encoding='utf-8') as wind_speed_file:
    
    # Create a csv.reader object
    wind_speed = csv.reader(wind_speed_file)
    
    # Read the first line to obtain the column names
    headers = next(wind_speed)   
    print(headers)
    
    # Find the index for the "Specie" column
    specie_index = headers.index('Specie')
    
    # Create a list to store filtered lines
    wind_speed_filtered_rows = []
    
    for row in wind_speed:
        if 'wind-speed' in row[specie_index]: #or 'wind-speed' in row[specie_index] or 'pm25' in row[specie_index]:
            wind_speed_filtered_rows.append(row)
            
     # Imprimer les lignes filtrées
    #for row in wind_speed_filtered_rows:
        #print(row)        

    # Open the new CSV file in write mode
    with open('wind_speed_filtered_rows.csv', 'w', newline='', encoding='utf-8') as wind_speed_f:
            # Créer un objet csv.writer
        csv_writer = csv.writer(wind_speed_f)
            
            # Write the header to the new file
        csv_writer.writerow(headers)
            
            # Write the filtered lines to the new file
        for row in wind_speed_filtered_rows:
            csv_writer.writerow(row)        
            #print(row)
    
