# -*- coding: utf-8 -*-
"""
Created on Mon Apr 24 23:55:45 2023

@author: Arsene Siewe Towoua
"""
import pandas as pd
import numpy as np
from math import radians, cos, sin, asin, sqrt
import math
import datetime
from datetime import datetime
import matplotlib.pyplot as plt
import csv

#39.73845291,-104.98485565 - Denver, US

#Dust accumulation effects on efficiency of solar PV modules for off grid
#27.71201706,85.31295013 - Kathmandu, NP (gut)

#Cordero et.al, „Efects of soiling on photovoltaic (PV) modules in the Atacama Desert,“ Nature Science Reports, 2018.
#-33.43777466,-70.65045166 - Santiago, CL
#-22.4623909,-68.92721558 - Calama, CL

# Coordonnées du lieu donné
X = 39.73845291 #lat
Y = -104.98485565 #lng

angle = 22 # tilt angle

#delta_t = 2 # nombre de mois
#delta_t_sec = delta_t * 30 * 24 * 60 * 60 # en secondes

# Importer le fichier CSV et ajouter une colonne index
data = pd.read_csv('soiling_data.csv', encoding ='utf-8')
data.insert(0, 'index', range(0, len(data)))

# Fonction pour calculer la distance entre deux coordonnées
def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

# Trouver le lieu le plus proche des coordonnées X et Y données
distances = []
for i, row in data.iterrows():
    dist = haversine(Y, X, row['lng'], row['lat'])
    distances.append(dist)
Index_location = np.argmin(distances)

# Calculer la valeur de la salissure pour le lieu trouvé
PM2_5 = data.loc[Index_location, 'PM2_5']
PM10 = data.loc[Index_location, 'PM10']
wind_speed = data.loc[Index_location, 'wind_speed']

Startdate = '2022 01 01 00'
Enddate = '2022 01 10 00'
start_date = datetime.strptime(Startdate, '%Y %m %d %H')
end_date = datetime.strptime(Enddate, '%Y %m %d %H')
print(start_date)
print(end_date)

delta = end_date - start_date
#print(delta)
seconds = delta.total_seconds()
#day = seconds / 86400 #per day
hours = seconds / 3600 #per hour
print("Number of seconds between the two dates:", seconds, 's')
#print("Number of day between the two dates:", day, 'd')
print("Number of hours between the two dates:", hours, 'd')
# Define day_until_clean_second as the time until the next cleaning (in seconds)
day_until_clean = 5 #cleaning occurs every 15 days
day_until_clean_second = 86400 * day_until_clean  # in seconds; Assume cleaning occurs every 15 days

# Initialize variables
delta_t = 0 #timessteps
S = 0 #soiling_accumulation
times = []
values_soiling_accumulation = []
values_soiling_hegazy = []
values_soiling_you_saiz = []
values_soiling_conceicao = []

#loop to determine the soiling value per hour
 
for t in range(int(hours)):
#for t in range(int(day)):
    
    # if the period day_until_clean_second is reached, reset S and delta_t
    if delta_t == day_until_clean_second:
        S = 0
        delta_t = 0 
        
    # Calculate new value of Soiling_accumulation
    S = round ((((PM2_5 + PM10)*(10**(-9))) * wind_speed * delta_t * cos(radians(angle))), 8)   # Coello.
    
    rs_hegazy = round ((((34.37 * math.erf(0.17*(S**0.8473))) / 100)), 6) #hegazy
    #rs_hegazy_neu = 1 - rs_hegazy

    rs_you_saiz = ( (0.0385 * S)) #“You/Saiz”.
    #rs_you_saiz_neu = 1 - (rs_you_saiz)

    rs_conceicao = ((0.2545 * S)* 10**(-1)) # *10**(-1) Arsene

    # add the value of S to the list of values_soiling_accumulation
    values_soiling_accumulation.append(S)
    
    # add the value of Soiling to the list of values_soiling_hegazy
    values_soiling_hegazy.append(rs_hegazy)
    
    # add the value of Soiling_rs_you_saiz to the list of values_soiling_you_saiz
    values_soiling_you_saiz.append(rs_you_saiz)
    
    # add the value of Soiling_rs_conceicao to the list of values_soiling_conceicao
    values_soiling_conceicao.append(rs_conceicao)
    
    # add the current hour/Day to the time list in hours
    times.append(t)
    
    # Print current values of A and delta_t
    print('Index_location:', Index_location)
    print('S:', S, 'g/m²')
    print('rs_hegazy:', rs_hegazy)
    #print('rs_hegazy_neu:', rs_hegazy_neu)
    print('rs_you_saiz:', rs_you_saiz)
    #print('rs_you_saiz_neu:', rs_you_saiz_neu)
    print('rs_conceicao:', rs_conceicao)
    
    print("delta_t:", delta_t)
    
    #increment the daily time interval
    #delta_t += 86400
    #increment the hourly time interval
    delta_t += 3600

#print(values_soiling_accumulation)
print(values_soiling_hegazy)
#print (times)

Soiling_hegazy_new = round((sum(values_soiling_hegazy) / len (values_soiling_hegazy)), 6)
print('average for the location indicated as a function of the length of the simulation:',Soiling_hegazy_new)


# Creating the csv table with Soiling data of the Location with the Index(Index_location)
with open('soiling_data{}.csv'.format(Index_location), mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Hours', 'Soiling_accumulation', 'rs_hegazy', 'rs_you_saiz', 'rs_conceicao' ])  # Column headings
    for i in range(len(times)):
        writer.writerow([times[i], values_soiling_accumulation[i], values_soiling_hegazy[i], values_soiling_you_saiz[i], values_soiling_conceicao[i] ])  # Adding data to the table

#  plot the soiling_accumulation graph
#plt.plot(times, values_soiling_accumulation)
#plt.xlabel('Day [d]')
#plt.xlabel('Hours [h]')
#plt.ylabel('Soiling Accumulation [g/m²]')
#plt.title('Evolution of the Soiling Accumulation during la simulation')
#plt.show()

#  plot the soiling_hegazy graph
plt.plot(times, values_soiling_hegazy)
plt.xlabel('Hours [h]')
plt.ylabel('Soiling')
plt.title('Evolution of the values_soiling_hegazy during la simulation')
plt.show()

#  plot the values_soiling_you_saiz graph
plt.plot(times, values_soiling_you_saiz)
plt.xlabel('Hours [h]')
plt.ylabel('Soiling')
plt.title('Evolution of the values_soiling_you_saiz during la simulation')
plt.show()

#  plot the values_soiling_conceicao graph
plt.plot(times, values_soiling_conceicao)
plt.xlabel('Hours [h]')
plt.ylabel('Soiling')
plt.title('Evolution of the values_soiling_conceicao during la simulation')
plt.show()

print(delta)
