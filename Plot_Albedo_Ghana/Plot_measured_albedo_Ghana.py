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
      
f, ax = plt.subplots(figsize=(12, 4))

#dt = datetime.combine(date.today(), time(0, 0, 0)) + timedelta(seconds=5)
#print (dt.time())
'''
time = datetime.combine(date.today(), time(0, 0, 0))
print(time.time())
DataFrame_x = [time.time()]
for i in range (1439):
    time += timedelta(seconds=5)
    dt = time.time()
    DataFrame_x.append(dt)
print(DataFrame_x) 
'''
#x = df['Time']

#x = [datetime.datetime(2021, 1, 1, 0, 0, 0) + datetime.timedelta(seconds=5) for i in range(1440)]
#x = DataFrame_x
#x = pd.date_range('2021-01-01 00:00:00', '2021-01-01 01:59:55', freq = '5S')

y1 = df['Kumasi']    
y2 = df['Accra']  
y3 = df['Average'] 
y4 = df['Akwatia']
x = range(len(y1))

plt.plot(x,y1, label='Kuwasi')
plt.plot(x,y2, label='Accra')
plt.plot(x,y3, label='Average')
plt.plot(x,y4, label='Akwatia')

ax.set_ylabel('Measured Albedo in Ghana')
ax.set_xlabel('Time')
'''
#ind = ['00:00:00', '00:15:00', '00:30:00', '00:45:00', '01:00:00', '01:15:00', '01:30:00', '01:45:00']
#ax.set_xticks(ind)
minlocator = mdates.MinuteLocator(interval = 15)
#hourlocator = mdates.HourLocator()

#minlocator.MAXTICKS  = 40000
#hourlocator.MAXTICKS  = 40000

ax.xaxis.set_major_locator(minlocator)
#ax.xaxis.set_major_locator(hourlocator)

#ax.xaxis.set_minor_formatter(mdates.DateFormatter('%H:%M:%S'))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))

#plt.setp(ax.xaxis.get_minorticklabels(), rotation=90)
plt.setp(ax.xaxis.get_majorticklabels(), rotation=90)
'''
ax.legend(bbox_to_anchor=(0., 1.02, 1, 0.1), loc='lower left', ncol=4, borderaxespad=0.)
plt.ylim(0,0.4)
plt.xlim(0,1439)
plt.show()