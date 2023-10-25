# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 23:02:21 2023

@author: Arsene Siewe Towoua
"""

#with this code the precipitation values from https://www.renewables.ninja/ can be added to the previously saved city tables. 
#This should be repeated for each city as required.


import os
import pandas as pd


# Step 1: Load and edit the file "precipitation_Accra, GH".
precipitation_data = pd.read_csv("precipitation_Budapest, HU.csv")
precipitation_data['time'] = pd.to_datetime(precipitation_data['time']).dt.date

grouped_data = precipitation_data.groupby('time')['prectotland'].mean().reset_index()
grouped_data.rename(columns={'time': 'Time', 'prectotland': 'daily_prectotland'}, inplace=True)

# Create the precipitation_data folder if it doesn't exist
output_folder_precip = "precipitation_data"
if not os.path.exists(output_folder_precip):
    os.makedirs(output_folder_precip)

# Save the new table "precipitation_Accra, GH" in the "precipitation_data" folder
output_path_precip = os.path.join(output_folder_precip, "precipitation_Budapest, HU.csv")
grouped_data.to_csv(output_path_precip, index=False)

# Save the file in the same directory as the code
script_directory = os.path.dirname(os.path.abspath(__file__))
output_path_script = os.path.join(script_directory, "precipitation_Budapest, HU.csv")
grouped_data.to_csv(output_path_script, index=False)

# Step 1: Load the "precipitation_Accra, GH" file
precipitation_data = pd.read_csv("precipitation_Budapest, HU.csv")

# Step 2: Load the "City, Country" file
city_data = pd.read_csv("Budapest, HU.csv")

# Step 3: Merge data and replace values
city_data['precipitation'] = precipitation_data['daily_prectotland']

# Step 4: Create the city_data_2 folder if it doesn't exist
output_folder = "city_data_2"
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Save the new table "City, Country" in the "city_data_2" folder
output_path = os.path.join(output_folder, "Budapest, HU.csv")
city_data.to_csv(output_path, index=False)

print("Manipulations completed and data saved.")

