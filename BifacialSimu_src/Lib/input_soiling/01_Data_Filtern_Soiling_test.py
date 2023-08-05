"""
@author: Arsene Siewe Towoua

"""

#this code is used to filter climate data on rainfall. 
#After downloading the data from "https://www.renewables.ninja/", 
#open the csv file and delete the first three columns. 
#Then rename (precipitation_City, Country) the file in the ideal way so that the data can be filtered. 

#example for Abidjan, CI 

import pandas as pd

# Load the CSV file into a DataFrame
file_path = "precipitation_Denver, US.csv"
df = pd.read_csv(file_path)

# Delete the 'time' column
df.drop(columns=['time'], inplace=True)

# Convert 'local_time' column to datetime type
df['local_time'] = pd.to_datetime(df['local_time'])

# Group by day and calculate average rainfall
df_grouped = df.groupby(df['local_time'].dt.date)['prectotland'].mean()

# Save path for new CSV file
new_file_path = "precipitation_data/precipitation_Denver, US.csv"

# Save the DataFrame as a new CSV file
df_grouped.to_csv(new_file_path)

###########################################
#ad the new precipitaion data to the city, country csv file. 


# CSV file path
input_file_path = r"C:\Users\Arsene Siewe Towoua\anaconda3\envs\soiling2\Lib\site-packages\BifacialSimu_src\Lib\input_soiling\city_data_2\Denver, US.csv"
precipitation_file_path = r"C:\Users\Arsene Siewe Towoua\anaconda3\envs\soiling2\Lib\site-packages\BifacialSimu_src\Lib\input_soiling\precipitation_data\precipitation_Denver, US.csv"

# Loading CSV files into DataFrames
df_input = pd.read_csv(input_file_path)
df_precipitation = pd.read_csv(precipitation_file_path)

# Add the 'precipitation' column to the input DataFrame
df_input['precipitation'] = df_precipitation['prectotland']

# Delete the first column of the input DataFrame
#df_input = df_input.iloc[:, 1:]

# Save path for new CSV file
precipitation_file_path = "city_data_2\Denver, US.csv"

# Save the DataFrame as a new CSV file
df_input.to_csv(precipitation_file_path)

# Display the resulting DataFrame
print(df_input)
