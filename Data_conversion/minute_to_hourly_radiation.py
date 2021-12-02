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
'input_file' : 'Measurement_GHI_DHI_DNI.csv',       # inset name of input file (utf8 file is needed)
}
#------------------------------------------------------------------------------


df1 = pd.read_csv(Dictionary['input_file'], sep=';', header=6)  
print(df1)
loop_number = Dictionary['number_of_days'] * 24      # 24 hours per day 

GHI_hourly = []     # array to hold hourly GHI values
DHI_hourly = []     # array to hold hourly DHI values
DNI_hourly = []     # array to hold hourly DNI values
cd = []             # array to hold hourly datetime

for i in range(loop_number):
    
    GHI_minute = []    # array to hold minute GHI values
    DHI_minute = []    # array to hold minute DHI values
    DNI_minute = []    # array to hold minute DNI values
    
    
    currentDate = datetime.datetime(Dictionary['startHour'][0], Dictionary['startHour'][1], Dictionary['startHour'][2], Dictionary['startHour'][3]) + pd.to_timedelta(i, unit='H') 
    
    for j in range(60):
        
        k = i*60 + j
        
        GHI = df1.iloc[k]['GHI'] 
        DHI = df1.iloc[k]['DHI'] 
        DNI = df1.iloc[k]['DNI'] 
        
        GHI_minute.append(GHI)
        DHI_minute.append(DHI)
        DNI_minute.append(DNI)
        
        
    GHI_h = np.mean(GHI_minute)     # mean value of 60 GHI minute values
    DHI_h = np.mean(DHI_minute)     # mean value of 60 DHI minute values
    DNI_h = np.mean(DNI_minute)     # mean value of 60 DNI minute values
    
    GHI_hourly.append(GHI_h)        # append the hourly GHI value to GHI array
    DHI_hourly.append(DHI_h)        # append the hourly DHI value to GHI array
    DNI_hourly.append(DNI_h)        # append the hourly DNI value to GHI array
    cd.append(currentDate)          # append the currentDate to cd array

    
# create pandas dataframe to save the four arrays and give them headers
df2 = pd.DataFrame({'datetime':cd, 'GHI':GHI_hourly, 'DHI':DHI_hourly, 'DNI':DNI_hourly})
print(df2)

# save pandas dataframe into a csv file
df2.to_csv('hourly_GHI_DHI_DNI.csv', sep=';', index=False)
        
        