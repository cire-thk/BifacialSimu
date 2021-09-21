 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 12:57:54 2019

@author:        Eva-Maria Grommes
Master thesis:  Impact of dust and red soil on the annual yield of Bifacial PV-modules in Ghana

"""

# Import
from IPython import get_ipython
get_ipython().magic('reset -sf')

import pandas as pd #pandas = can read .csv as input
import matplotlib.pyplot as plt #display shadows
import numpy as np
import os #to import directories
import warnings
import math
import pvlib #for electrical output simulation
import bifacial_radiance
from bifacial_radiance import *
from datetime import datetime
from pvfactors.viewfactors.aoimethods import faoi_fn_from_pvlib_sandia #to calculate AOI reflection losses
from pvfactors.engine import PVEngine
from pvfactors.irradiance import HybridPerezOrdered
from pvfactors.geometry import OrderedPVArray
from pvfactors.viewfactors import VFCalculator
from pvlib.location import Location
from tqdm import tqdm



#########################################################






#########################################################
    

   
    


# Dictionary for Module Parameters
"""
#NREL Row 2 
print("\n NREL Row 2:") 
moduleParameter = {
    'I_sc_f': 9.5, #Short-circuit current measured for front side illumination of the module at STC [A]
    'I_sc_r': 6.56, #Short-circuit current measured for rear side illumination of the module at STC [A]
    'V_oc_f': 48, #Open-circuit voltage measured for front side illumination of module at STC [V]
    'V_oc_r': 47.3, #Open-circuit voltage measured for rear side illumination of module at STC [V]
    'V_mpp_f': 39.2, #Front Maximum Power Point Voltage [V]
    'V_mpp_r': 39.5, #Rear Maximum Power Point Voltage [V]
    'I_mpp_f': 9.00, #Front Maximum Power Point Current [A]
    'I_mpp_r': 6.2, #Rear Maximum Power Point Current [A]
    'P_mpp': 354, # Power at maximum power Point [W]
    'T_koeff': -0.0036, #Temperature Coeffizient [1/°C]
    'T_amb':20, #Ambient Temperature for measuring the Temperature Coeffizient [°C]
    
    #'inverter': pvlib.pvsystem.retrieve_sam('cecinverter')['ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_'],
    #'module': pvlib.pvsystem.retrieve_sam('SandiaMod')['Canadian_Solar_CS5P_220M___2009_'],
    #'P_sys': 360, #system nominal power [KWp]
}
"""





#########################################################

'''# Define timezone and table specifications
def export_data(fp):
    #tz = tz_localize('Africa/Accra')
    df = pd.read_csv(fp, header = 0)
    
    # Define, which columns to drop, if none, comment out
    #columnsToDrop = [df.columns[1]] 
    #columnsToDrop = [df.columns[5], df.columns[6], df.columns[7], df.columns[8]] 
    #for column in columnsToDrop:
    #    df = df.drop(column, axis = 1)
        
    # Rename columns for calculation
    df = df.rename(columns = {'date': 'timestamps'})
    df = df.rename(columns = {'Diffuse horizontal irradiance (W/m2)': 'dhi'})
    df = df.rename(columns = {'Direct (beam) normal Irradiance (W/m2)': 'dni'})
    df = df.rename(columns = {'Dry bulb temperature (deg, C)': 'temperature'})
    df = df.rename(columns = {'Windspeed (m/s)': 'windspeed'})
    df = df.rename(columns = {'Air pressure (Pa)': 'airpressure'})
 
    #df = df.set_index('timestamps') # Define index for dataframe
    df['datetime'] = pd.date_range(start='2019/10/01 00:00', end= '2020/05/01 00:00', freq='H')
    #df.index=pd.to_datetime(df.index) #Configure x-axis label
    df= df.set_index('datetime')
    
    return df
    print(df)

#df = export_data(resultsPath) #print(df)'''

#########################################################




#########################################################
#Calculation of sun parameters

"""
    # Begin loop: Calculate for every hour 
for index, row in df.iterrows():
    surface_tilt = simulationParameter['surface_tilt']
    surface_azimuth = simulationParameter['surface_azimuth']
df['surface_tilt'] = surface_tilt
df['surface_azimuth'] = surface_azimuth

times = pd.date_range(start=datetime(2019,10,1), end=datetime(2020,5,1), freq='60Min', ambiguous=True)

#ephem_pos = pvlib.solarposition.get_solarposition(times.tz_localize(position.tz, ambiguous='NaT',nonexistent='NaT'), position.latitude, position.longitude)
ephem_pos = pvlib.solarposition.get_solarposition(pd.date_range(start='2019/10/01 00:00', end= '2020/05/01 00:00', freq='H'), position.latitude, position.longitude)

ephem_pos.to_csv(resultsPath + '/Sonnenstand.csv')
#ephemout = ephem_pos.tz_convert(None)
ephemout = ephem_pos

df.to_excel(resultsPath + '/Wetterdaten.xlsx')
ephemout.to_excel(resultsPath + '/Sonnenstand.xlsx')
dfSun = df.join(ephemout)
dfSun.index.name = "datetime"
dfSun.to_excel(resultsPath + '/Sonnenstand_gesamt.xlsx')
"""






####################################################
# Variablen, die benötigt werden:

# P_bi: Output power of bifacial module for bifacial illumination (W)
# I_sc_bi: Short-circuit current of bifacial module for bifacial illumination (A)
# V_oc: Open-circuit voltage of bifacial module for bifacial illumination (V)
# FF_bi: Fill factor of bifacial module for bifacial illumination (%)
# G_r: Irradiance on the rear side of the module (W/m2)
# G_f: Irradiance on the front side of the module (W/m2)
# R_isc: Relative current gain (dimensionless)
# I_sc_f: Short-circuit current measured for front side illumination of the module at STC (A)
# x: Irradiance ratio (dimensionless)
# V_oc_f: Open-circuit voltage measured for front side illumina- tion of module at STC (V)
# V_oc_r: Open-circuit voltage measured for rear side illumina- tion of module at STC (V)
# I_sc_r: Short-circuit current measured for rear side illumination of the module at STC (A)
# FF_f: Fill factor measured for front side illumination of the module at STC (%)
# FF_r: Fill factor measured for rear side illumination of the module (%)
# pFF: Pseudo fill factor (FF of the module considering no series resistance effect) (%)

print("Bis hierhin ok3")

####################################################
# Definition of simulation parameter
V_mpp_f0 = moduleParameter['V_mpp_f']
V_mpp_r0 = moduleParameter['V_mpp_r']

I_mpp_f0 = moduleParameter['I_mpp_f']
I_mpp_r0 = moduleParameter['I_mpp_r']

I_sc_r0 = moduleParameter['I_sc_r']
I_sc_f0 = moduleParameter['I_sc_f']

V_oc_r0 = moduleParameter['V_oc_r']
V_oc_f0 = moduleParameter['V_oc_f']

#module = moduleParameter['module']
#inverter = moduleParameter['inverter']

P_mpp0 = moduleParameter['P_mpp']
V_mpp0 = V_mpp_f0

T_koeff_P = moduleParameter['T_koeff_P'] 
T_koeff_I = moduleParameter['T_koeff_I'] 
T_koeff_V = moduleParameter['T_koeff_V'] 
T_amb = moduleParameter['T_amb']

q_stc_front = 1000  # [W/m^2] 
q_stc_rear = 1000   # [W/m^2] 

# Calculation of fill factor for STC conditions
FF_f0 = (I_mpp_f0 * V_mpp_f0)/(I_sc_f0 * V_oc_f0) 
FF_r0 = (I_mpp_r0 * V_mpp_r0)/(I_sc_r0 * V_oc_r0) 

####################################################
# Bifacial performance Calculation

# # Fillfactor Calculation for front and back
# FF_f = (V_mpp_f * I_mpp_f)/(V_oc_f * I_sc_f) # Fill factor measured for front side illumination of the module at STC [%/100]
# print("Fill Factor front: " + str(FF_f))

# FF_r = (V_mpp_r * I_mpp_r)/(V_oc_r * I_sc_r) # Fill factor measured for front back illumination of the module at STC [%/100]
# print("Fill Factor back: " + str(FF_r))
# print ("\n")

# Set Energy to Zero       
sum_energy_b = 0
sum_power_b = 0

# Array to hold other arrays -> average after for loop
P_bi_hourly_arrays = []

# Loop to calculate the Bifacial Output power for every row in every hour
for i in tqdm(range(0, simulationParameter['n_pvrows'])):
    
    key_front = "row_" + str(i) + "_qabs_front"
    key_back = "row_" + str(i) + "_qabs_back"

    P_bi_hourly = []
  

    for index, row in df_report.iterrows():
        
        row_qabs_front = row[key_front]
        row_qabs_back = row[key_back]
        T_Current = df.loc[index,'temperature']
        
        
        #print("front: " + str(row_qabs_front))
        #print("back: " + str(row_qabs_back))
        
        
        if row_qabs_back + row_qabs_front > 0.0:
            
            I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb))     
            I_sc_r = I_sc_r0 * (1 + T_koeff_I * (T_Current - T_amb))
            
            V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb))
            V_oc_r = V_oc_r0 * (1 + T_koeff_V * (T_Current - T_amb))
            
            FF_f = FF_f0 * ((1 + T_koeff_P * (T_Current-T_amb)) / ((1 + T_koeff_I * (T_Current - T_amb)) * (1 + T_koeff_V * (T_Current - T_amb))))
            FF_r = FF_r0 * ((1 + T_koeff_P * (T_Current-T_amb)) / ((1 + T_koeff_I * (T_Current - T_amb)) * (1 + T_koeff_V * (T_Current - T_amb))))
            
            I_sc_b = (row_qabs_front / q_stc_front) * I_sc_f + (row_qabs_back / q_stc_rear) * I_sc_r
            R_I_sc_b = I_sc_b / I_sc_f
            V_oc_b = V_oc_f + ((V_oc_r - V_oc_f) * np.log(R_I_sc_b) / np.log(I_sc_r / I_sc_f))
            
            pFF = ((I_sc_r0/I_sc_f0) * FF_f0 - (FF_r0 * (V_oc_r0 / V_oc_f0))) / ((I_sc_r0/I_sc_f0) - (V_oc_r0 / V_oc_f0))
            FF_b = pFF - (R_I_sc_b * (V_oc_f0 / V_oc_b) * (pFF - FF_f0))
        
            P_bi = FF_b * V_oc_b * I_sc_b
            #print("Power: " + str(P_bi))
    
            sum_energy_b += P_bi # Sum up the energy of every row in every hour
    
        else:
            P_bi=0
        
        P_bi_hourly.append(P_bi)
        
    # Append P_bi_hourly array to arrays
    P_bi_hourly_arrays.append(P_bi_hourly)
        
        
P_bi_hourly_average = []

for i in tqdm(range(0, len(P_bi_hourly_arrays[0]))):
    sum = 0
  
    for j in range(0, len(P_bi_hourly_arrays)):
        sum += P_bi_hourly_arrays[j][i]
        
    average = sum / float(len(P_bi_hourly_arrays))
    
    P_bi_hourly_average.append(average)
    
# Create dataframe with average data
p_bi_df = pd.DataFrame({"timestamps":df_report.index, "P_bi ": P_bi_hourly_average})
p_bi_df.set_index("timestamps")
p_bi_df.to_csv("P_bi_LG" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")


annual_power_per_module_b = (sum_energy_b/simulationParameter['n_pvrows']) #[W] annual bifacial output power per module
print("Yearly bifacial output power per module: " + str(annual_power_per_module_b) + " W/module")
print("Yearly bifacial output energy per module: " + str(annual_power_per_module_b/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
print ("\n")

annual_power_per_peak_b = (sum_energy_b/(P_mpp0 * simulationParameter['n_pvrows']))   #[W/Wp] annual bifacial output power per module peak power
print("Yearly bifacial output power per module peak power: " + str(annual_power_per_peak_b) + " W/Wp")
print("Yearly bifacial output energy per module peak power: " + str(annual_power_per_peak_b) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
print ("\n")

module_area = (simulationParameter['pvrow_width'] * simulationParameter['pvmodule_width'])

annual_power_per_area_b = (annual_power_per_module_b / module_area)    #[W/m^2] annual bifacial poutput power per module area
print("Yearly bifacial output power per module area: " + str(annual_power_per_area_b) + " W/m^2")
print("Yearly bifacial output energy per module area: " + str(annual_power_per_area_b/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
print ("\n")

# Plot total qinc front and back for every row




f, (ax1) = plt.subplots(1, figsize=(12, 3))
ax1.locator_params(tight=True, nbins=6)
plt.plot(P_bi_hourly)
ax1.set_title('Bifacial output Power hourly')
ax1.set_xlabel('Hour')
ax1.set_ylabel('W')
f.savefig("P_bi_hourly" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
plt.show(sns)


####################################################
# Monofacial performance Calculation

# Set Energy to Zero       
sum_energy_m = 0
sum_power_m = 0

# Loop to calculate the Monofacial Output power for every row in every hour
for i in tqdm(range(0, simulationParameter['n_pvrows'])):
    
    key_front_mono = "row_" + str(i) + "_qabs_front"
    
    for index, row in df_report.iterrows():
        
        #SG
        row_qabs_front = row[key_front_mono]
        T_Current = df.loc[index,'temperature']
        
        
        #print("front: " + str(row_qabs_front))
        
        
        if  row_qabs_front > 0.0:
      
            V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleParameter['zeta'] * np.log(row_qabs_front / q_stc_front))
            I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
            P_m = FF_f0 * V_oc_f * I_sc_f
        
            #print("Power: " + str(P_bi))
     
            sum_energy_m += P_m # Sum up the energy of every row in every hour
        
         #else:
            #print("Power: 0.0")

annual_power_per_module_m = (sum_energy_m/simulationParameter['n_pvrows']) #[W] annual monofacial output power per module
print("Yearly monofacial output power per module: " + str(annual_power_per_module_m) + " W/module")
print("Yearly monofacial output energy per module: " + str(annual_power_per_module_m/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
print ("\n")

annual_power_per_peak_m = (sum_energy_m/(P_mpp0 * simulationParameter['n_pvrows']))   #[W/Wp] annual monofacial output power per module peak power
print("Yearly monofacial output power per module peak power: " + str(annual_power_per_peak_m) + " W/Wp")
print("Yearly monofacial output energy per module peak power: " + str(annual_power_per_peak_m) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
print ("\n")

module_area = (simulationParameter['pvrow_width'] * simulationParameter['pvmodule_width'])

annual_power_per_area_m = (annual_power_per_module_m / module_area)    #[W/m^2] annual monofacial poutput power per module area
print("Yearly monofacial output power per module area: " + str(annual_power_per_area_m) + " W/m^2")
print("Yearly monofacial output energy per module area: " + str(annual_power_per_area_m/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
print ("\n")

####################################################

# Bifacial Gain Calculation

Bifacial_gain= (annual_power_per_peak_b - annual_power_per_peak_m) / annual_power_per_peak_m
print("Bifacial Gain: " + str(Bifacial_gain*100) + " %")
