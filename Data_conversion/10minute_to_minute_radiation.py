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
'input_file' : '10minute_Flughafen.csv',       # inset name of input file (utf8 file is needed)
}
#------------------------------------------------------------------------------


df1 = pd.read_csv(Dictionary['input_file'], sep=';', header=0)  
print(df1)
loop_number = Dictionary['number_of_days'] * 24 *6     # 24 hours per day and 6 10 minutes per hour

GHI_minute = []     # array to hold minute GHI values
DHI_minute = []     # array to hold minute DHI values
cd = []      # array to hold minute datetime

for i in range(loop_number):
     
    for j in range(10):
        
        k = i * 10 + j
        
        GHI = df1.iloc[i]['GHI'] *10 
        DHI = df1.iloc[i]['DHI'] *10
        
        currentDate = datetime.datetime(Dictionary['startHour'][0], Dictionary['startHour'][1], Dictionary['startHour'][2], Dictionary['startHour'][3]) + pd.to_timedelta(k, unit='m') 
        
        GHI_minute.append(GHI)
        DHI_minute.append(DHI)
        cd.append(currentDate)          # append the currentDate to cd array
         

    
# create pandas dataframe to save the four arrays and give them headers
df2 = pd.DataFrame({'datetime':cd, 'GHI':GHI_minute, 'DHI':DHI_minute})
print(df2)

# save pandas dataframe into a csv file
df2.to_csv('minute_GHI_DHI.csv', sep=';', index=False)
        
        