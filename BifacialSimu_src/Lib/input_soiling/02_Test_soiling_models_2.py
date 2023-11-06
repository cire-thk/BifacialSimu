"""
@author: Arsene Siewe Towoua

"""

import pandas as pd

# Importing CSV files into DataFrames
df_accra = pd.read_csv('Accra, GH.csv')
df_data = pd.read_csv('Dataframe_df.csv')

# Convert the 'Date' column into date format for both DataFrames
df_accra['Date'] = pd.to_datetime(df_accra['Date'], dayfirst=True)
df_data['corrected_timestamp'] = pd.to_datetime(df_data['corrected_timestamp'], dayfirst=True)

# Create an empty list to store the corresponding soilingrate values
PAPA = []

# Browse rows in DataFrame "Dataframe_df
for index, row in df_data.iterrows():
    # Extract the date (day and month) from the current row of the "Dataframe_df" DataFrame
    date_data = row['corrected_timestamp'].replace(year=2023)  # Remplacer l'année par l'année appropriée
    
    # Filter the "Accra, GH" DataFrame to obtain rows with the same date (day and month)
    df_filtered = df_accra[(df_accra['Date'].dt.day == date_data.day) & (df_accra['Date'].dt.month == date_data.month)]
    
    # Check whether rows have been found in the filtered DataFrame
    if not df_filtered.empty:
        # Retrieve the soilingrate value from the first corresponding line
        soilingrate_value = df_filtered.iloc[0]['soilingrate']
        
        # Add the soilingrate value to the "PAPA" list
        PAPA.append(soilingrate_value)
    else:
        # Add a default value (for example, 0) if no corresponding soilingrate value has been found
        PAPA.append(0)

# Display the "PAPA" list containing the corresponding soilingrate values for each identical day and month
print(PAPA)
print(len(PAPA))


import os
import pandas as pd

# Define the absolute path of the file
file_path = "C:\\Users\\Arsene Siewe Towoua\\anaconda3\\envs\\soiling2\\Lib\\input_soiling\\city_data_soiling_accumulation\\Denver, US.csv"

# Check if the file exists
if os.path.exists(file_path):
    df_city = pd.read_csv(file_path)
    # Do what you need to do with the df_city DataFrame here
else:
    print(f"Le fichier '{file_path}' n'a pas été trouvé.")
