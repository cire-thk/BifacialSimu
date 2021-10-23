# -*- coding: utf-8 -*-
"""
Created on Tue Oct  5 18:55:49 2021

@author: sarah


Converting minute values of GHI, DNI and DHI into houly values
"""

import pandas as pd
import numpy as np
import datetime

#------------------------------------------------------------------------------
'Input parameters'
Dictionary = {
'startHour' : (2021, 9, 23, 0),                     # yy, mm, dd, hh
'number_of_days' : 16,                              # number of days to calculate hourly data for
'input_file' : 'Measurement_Albedo.csv',            # inset name of input file (utf8 file is needed)
}
#------------------------------------------------------------------------------


df1 = pd.read_csv(Dictionary['input_file'], sep=';', header=6)  
print(df1)
loop_number = Dictionary['number_of_days'] * 24      # 24 hours per day 

A_hourly = []     # array to hold hourly Albedo values
cd = []           # array to hold hourly datetime

for i in range(loop_number):
    
    A_minute = []    # array to hold minute Albedo values
    
    k = i*60
    
    currentDate = datetime.datetime(Dictionary['startHour'][0], Dictionary['startHour'][1], Dictionary['startHour'][2], Dictionary['startHour'][3]) + pd.to_timedelta(i, unit='H') 
    
    for j in range(60):
        
        A = df1.iloc[k]['Albedo'] 
        
        A_minute.append(A)
        

        k = k + 1
        
    A_h = np.mean(A_minute)     # mean value of 60 Albedo minute values
       
    A_hourly.append(A_h)        # append the hourly Albedo value to Albedo array
    cd.append(currentDate)      # append the currentDate to cd array

    
# create pandas dataframe to save the four arrays and give them headers
df2 = pd.DataFrame({'datetime':cd, 'Albedo':A_hourly})
print(df2)

# save pandas dataframe into a csv file
df2.to_csv('hourly_Albedo.csv', sep=';', index=False)
        
        