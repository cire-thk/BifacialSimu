# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 11:39:16 2021
@author:        
    CIRE TH Cologne
    Felix Schemann
    Frederik Klag
    Sebastian Nows

name:
    BiSim - calculationHandler

overview:
    Contains all own calculations of BiSim which are needed for 
    the bifacial simulation of PV-Modules

last changes:
    07.06.21 created

"""

from IPython import get_ipython
get_ipython().magic('reset -sf')

import pandas as pd #pandas = can read .csv as input
import matplotlib.pyplot as plt #display shadows
import numpy as np
import os #to import directories
from bifacial_radiance import *
from datetime import datetime
from tqdm import tqdm

# seaborn makes your plots look better
try:
    import seaborn as sns
    sns.set(rc={"figure.figsize": (12, 6)})
    sns.set_style("darkgrid") # Other available styles: whitegrid, dark, white, ticks
    sns.set_context("paper") # Scaling the axes, also available: talk, poster, 
    sns.set_palette("muted") 
    sns.set_color_codes()
except ImportError:
    print('We suggest you install seaborn using conda or pip and rerun this cell')

# Path handling
#rootPath = os.path.dirname(os.path.dirname(os.path.realpath(".")))

# Include paths

#sys.path.append(rootPath + "/BiSim/Handler")


import BiSim_radiationHandler 


# electric-calculation Klasse
    
    
    # Funktionen für 1-Dioden-Modell

class Electrical_simulation:
    
    
    ##### Function to combine radiation reports from Viewfactors and Raytracing if needed
    def build_simulationReport(df_reportVF, df_reportRT, simulationDict, resultsPath):
                      
        ##########
        # Work in progress
        
        if simulationDict['simulationMode'] == 1:
            df_report = pd.concat([df_reportVF, df_reportRT], axis=1)
        if simulationDict['simulationMode'] == 2:
            df_report = df_reportVF
        if simulationDict['simulationMode'] == 3:
            df_report = df_reportRT
        #df_report = df_report.reindex(sorted(df_report.columns), axis=1)
        df_report.to_csv(resultsPath + "radiation_qabs_results.csv")
        
        return df_report
    
    def simulate_oneDiode(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath):
        
        df_report = Electrical_simulation.build_simulationReport(df_reportVF, df_reportRT, simulationDict, resultsPath)
        
        ####################################################
        # Variables required for electrical simulation
        
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

        ####################################################
        # Definition of simulation parameter
        V_mpp_f0 = moduleDict['V_mpp_f']
        V_mpp_r0 = moduleDict['V_mpp_r']
        
        I_mpp_f0 = moduleDict['I_mpp_f']
        I_mpp_r0 = moduleDict['I_mpp_r']
        
        I_sc_r0 = moduleDict['I_sc_r']
        I_sc_f0 = moduleDict['I_sc_f']
        
        V_oc_r0 = moduleDict['V_oc_r']
        V_oc_f0 = moduleDict['V_oc_f']
        
        #module = moduleParameter['module']
        #inverter = moduleParameter['inverter']
        
        P_mpp0 = moduleDict['P_mpp']
        V_mpp0 = V_mpp_f0
        
        T_koeff_P = moduleDict['T_koeff_P'] 
        T_koeff_I = moduleDict['T_koeff_I'] 
        T_koeff_V = moduleDict['T_koeff_V'] 
        T_amb = moduleDict['T_amb']
        
        q_stc_front = 1000  # [W/m^2] 
        q_stc_rear = 1000   # [W/m^2] 
        
        # Calculation of fill factor for STC conditions
        FF_f0 = (I_mpp_f0 * V_mpp_f0)/(I_sc_f0 * V_oc_f0) 
        FF_r0 = (I_mpp_r0 * V_mpp_r0)/(I_sc_r0 * V_oc_r0) 
        
        
        dpi = 150 #Quality for plot export
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
        
        df_report['timestamp'] = df_report.index
        df_report = df_report.reset_index()
        df_report['corrected_timestamp'] = pd.to_datetime(df_report['timestamp'])
        df_report['time'] = df_report['corrected_timestamp'].dt.strftime('%m_%d_%H')
        df_report = df_report.set_index('time')
        
        df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
        df = df.set_index('time')
        
        print(df_report)
        print('view_factor dataframe at calculation handler:')
        print(df)
        # Loop to calculate the Bifacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
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
        
        
        annual_power_per_module_b = (sum_energy_b/simulationDict['nRows']) #[W] annual bifacial output power per module
        '''print("Yearly bifacial output power per module: " + str(annual_power_per_module_b) + " W/module")
        print("Yearly bifacial output energy per module: " + str(annual_power_per_module_b/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
        print ("\n")'''
        
        annual_power_per_peak_b = (sum_energy_b/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual bifacial output power per module peak power
        '''print("Yearly bifacial output power per module peak power: " + str(annual_power_per_peak_b) + " W/Wp")
        print("Yearly bifacial output energy per module peak power: " + str(annual_power_per_peak_b) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        module_area = (simulationDict['moduley'] * simulationDict['modulex'])
        
        annual_power_per_area_b = (annual_power_per_module_b / module_area)    #[W/m^2] annual bifacial poutput power per module area
        '''print("Yearly bifacial output power per module area: " + str(annual_power_per_area_b) + " W/m^2")
        print("Yearly bifacial output energy per module area: " + str(annual_power_per_area_b/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
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
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front_mono = "row_" + str(i) + "_qabs_front"
            
            for index, row in df_report.iterrows():
                
                #SG
                row_qabs_front = row[key_front_mono]
                T_Current = df.loc[index,'temperature']
                
                
                #print("front: " + str(row_qabs_front))
                
                
                if  row_qabs_front > 0.0:
              
                    V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
                    I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
                    P_m = FF_f0 * V_oc_f * I_sc_f
                
                    #print("Power: " + str(P_bi))
             
                    sum_energy_m += P_m # Sum up the energy of every row in every hour
                
                 #else:
                    #print("Power: 0.0")
        
        annual_power_per_module_m = (sum_energy_m/simulationDict['nRows']) #[W] annual monofacial output power per module
        '''print("Yearly monofacial output power per module: " + str(annual_power_per_module_m) + " W/module")
        print("Yearly monofacial output energy per module: " + str(annual_power_per_module_m/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
        print ("\n")'''
        
        annual_power_per_peak_m = (sum_energy_m/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual monofacial output power per module peak power
        '''print("Yearly monofacial output power per module peak power: " + str(annual_power_per_peak_m) + " W/Wp")
        print("Yearly monofacial output energy per module peak power: " + str(annual_power_per_peak_m) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        module_area = (simulationDict['moduley'] * simulationDict['modulex'])
        
        annual_power_per_area_m = (annual_power_per_module_m / module_area)    #[W/m^2] annual monofacial poutput power per module area
        '''print("Yearly monofacial output power per module area: " + str(annual_power_per_area_m) + " W/m^2")
        print("Yearly monofacial output energy per module area: " + str(annual_power_per_area_m/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        ####################################################
        
        # Bifacial Gain Calculation
        
        Bifacial_gain= (annual_power_per_peak_b - annual_power_per_peak_m) / annual_power_per_peak_m
        print("Bifacial Gain: " + str(Bifacial_gain*100) + " %")
# radiation-calculation Klasse

    # Funktion zur Berechnung von Sonnenstand manuell
    # Funktion zur Berechnung Albedo (einfach spektral)
    # Funktion zur Berechnung Albedo 

    