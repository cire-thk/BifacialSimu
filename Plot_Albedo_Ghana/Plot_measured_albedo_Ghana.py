# -*- coding: utf-8 -*-
"""
Created on Thu Dec 16 22:07:44 2021

@author: sarah
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
#from datetime import date, datetime, time, timedelta

df = pd.read_csv('Measured_Albedo_Ghana.csv', sep=';', header=0)
print(df)

plt.rc ('axes', labelsize = 13) # Schriftgröße der x- und y-Beschriftungen
plt.rc ('xtick', labelsize = 11) #Schriftgröße der x-Tick-Labels
plt.rc ('ytick', labelsize = 11) #Schriftgröße der y-Tick-Labels
plt.rc ('legend', fontsize = 11) #Schriftgröße der Legende
f, ax = plt.subplots(figsize=(12, 4), dpi=200)      

x = df['Time']
y1 = df['Kumasi']    
y2 = df['Accra']  
y3 = df['Average'] 
y4 = df['Akwatia']

plt.plot(x,y1, label='Kuwasi')
plt.plot(x,y2, label='Accra')
plt.plot(x,y3, label='Average')
plt.plot(x,y4, label='Akwatia')

ax.set_ylabel('Measured Albedo in Ghana')
ax.set_xlabel('Measurement time')

ind = ['00:00:00', '00:15:00', '00:30:00', '00:45:00', '01:00:00', '01:15:00', '01:30:00', '01:45:00']
#label = ["00:00:00", "00:15:00", "00:30:00", "00:45:00", "01:00:00", "01:15:00", "01:30:00", "01:45:00"]
ax.set_xticks(ind)
#plt.setp(ax.get_xticklabels(), rotation=30)

ax.legend(bbox_to_anchor=(0., 1.02, 1, 0.1), loc='lower left', ncol=4, borderaxespad=0.)
plt.ylim(0,0.4)
plt.xlim(0,1439)
plt.show()