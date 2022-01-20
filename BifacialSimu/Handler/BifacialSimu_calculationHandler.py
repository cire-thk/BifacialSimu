# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 11:39:16 2021

@author:        
    Eva-Maria Grommes

Additional co-authors can be found here:
https://github.com/cire-thk/bifacialSimu    

name:
    BifacialSimu - calculationHandler

overview:
    Contains all own calculations of BifacialSimu which are needed for 
    the bifacial simulation of PV-Modules


"""

from IPython import get_ipython
get_ipython().magic('reset -sf')

import pandas as pd #pandas = can read .csv as input
import matplotlib.pyplot as plt #display shadows
import numpy as np
import os #to import directories
from bifacial_radiance import *
import datetime
from tqdm import tqdm
import math
import dateutil.tz
import GUI
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

#sys.path.append(rootPath + "/BifacialSimu/Handler")


import BifacialSimu_radiationHandler 


# electric-calculation Klasse
    
    # Funktionen für 1-Dioden-Modell

class Electrical_simulation:
    """
    Class that simulates the eletrical output from the irradiance simulation
    Currently, electrical simulation works with only Viewfactors and Viewfactors/Raytracing combination 
    
    Methods
    -------
    build_simulationReport: build a final simulation report that contains data from viewfactors and raytracing
    simulate_oneDiode: Applies the one diode model for electrical simulation. Needs module front and rear parameters to work correctly.
    simulate_simpleBifacial: Simple electrical simulation mode that doesn't need rear module parameters. 
                Applies bifaciality factor to calculate rear efficiency and fill factor.
    """
    
    ##### Function to combine radiation reports from Viewfactors and Raytracing if needed
    def build_simulationReport(df_reportVF, df_reportRT, simulationDict, resultsPath):
                      
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
        """
        Applies the one diode model for bifacial electrical simulation. Needs module front and rear parameters to work correctly.
        Calculates bifacial gain through a seperate monofacial electrical simulation.

        Parameters
        ----------
        moduleDict: module Dictionary containing module data
        simulationDict: simulation Dictionary, which can be found in BifacialSimuu_main.py
        df_reportVF: Viewfactor simulation report
        df_reportRT: Raytracing simulation report
        df_report: Final simulation report, containing VF and RT data
        resultsPath: output filepath
        df: helper DataFrame containing temperature for electrical simulation
        """
        
        
        
        # Build a final simutlation report
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
        
        
        dpi = 300 #Quality for plot export
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
        P_m_hourly_arrays = []
        
        df_report['timestamp'] = df_report.index
        df_report = df_report.reset_index()
        df_report['corrected_timestamp'] = pd.to_datetime(df_report['timestamp'])
        df_report['time'] = df_report['corrected_timestamp'].dt.strftime('%m_%d_%H')
        df_report = df_report.set_index('time')
        
        
        
        
        if simulationDict['simulationMode'] == 3:
            df = df.reset_index()
            
            df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
            df = df.set_index('time')
            df['timestamp'] = df['corrected_timestamp'].dt.strftime('%m-%d %H:%M%')
            df['timestamp'] = pd.to_datetime(df['timestamp'])  
            #df['timestamp'] = df['timestamp'].dt.tz_localize(None)
            df = df.set_index('timestamp')
            
            dtStart = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
        
        
            dtEnd = datetime.datetime(simulationDict['endHour'][0], simulationDict['endHour'][1], simulationDict['endHour'][2], simulationDict['endHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
            mask = (df.index >= dtStart) & (df.index <= dtEnd) 
            df = df.loc[mask]
        
        df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
        df = df.set_index('time')
        
        
        # Loop to calculate the Bifacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front = "row_" + str(i) + "_qabs_front"
            key_back = "row_" + str(i) + "_qabs_back"
        
            P_bi_hourly = []
          
            for index, row in df_report.iterrows():
                
                row_qabs_front = df_report.loc[index,key_front]
                row_qabs_back = df_report.loc[index,key_back]
                T_Current = df.loc[index,'temperature']
                
                
                #print("front: " + str(row_qabs_front))
                #print("back: " + str(row_qabs_back))
                if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                    row_qabs_front = 0
                    
                if math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                    row_qabs_back = 0

                
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
            
       
        
        # The time gets implemented in the GUI
    # p_bi_df.to_csv(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
        
        
        annual_power_per_module_b = (sum_energy_b/simulationDict['nRows']) #[W] annual bifacial output power per module
        '''print("Yearly bifacial output power per module: " + str(annual_power_per_module_b) + " W/module")
        print("Yearly bifacial output energy per module: " + str(annual_power_per_module_b/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
        print ("\n")'''
        
        annual_power_per_peak_b = (sum_energy_b/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual bifacial output power per module peak power
        '''print("Yearly bifacial output power per module peak power: " + str(annual_power_per_peak_b) + " W/Wp")
        print("Yearly bifacial output energy per module peak power: " + str(annual_power_per_peak_b) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        module_area = (simulationDict['moduley'] *simulationDict['nModsy'] *simulationDict['modulex'])
        
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
        f.savefig("P_bi_hourly" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
        plt.show()
        #sns wird entfernt da die Plots in der GUI ansonsten nicht richtig angezeigt werden können außerhalb der Konsole
        #plt.show(sns)
        
        
        ####################################################
        # Monofacial performance Calculation
        
        # Set Energy to Zero       
        sum_energy_m = 0
        sum_power_m = 0
        
        # Loop to calculate the Monofacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front_mono = "row_" + str(i) + "_qabs_front"
            P_m_hourly = []
            
            for index, row in df_report.iterrows():
                
                #SG
                row_qabs_front = df_report.loc[index,key_front_mono]
                T_Current = df.loc[index,'temperature']

                if math.isnan(row_qabs_front):
                    row_qabs_front = 0 
                
                if  row_qabs_front > 0.0:
              
                    V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
                    I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
                    P_m = FF_f0 * V_oc_f * I_sc_f
                
                    #print("Power: " + str(P_bi))
             
                    sum_energy_m += P_m # Sum up the energy of every row in every hour
                else:
                    P_m = 0
                    
                P_m_hourly.append(P_m)
            
            # Append P_m_hourly array to arrays
            P_m_hourly_arrays.append(P_m_hourly)
        
        
        P_m_hourly_average = []
        
        for i in tqdm(range(0, len(P_m_hourly_arrays[0]))):
            sum = 0
          
            for j in range(0, len(P_m_hourly_arrays)):
                sum += P_m_hourly_arrays[j][i]
                
            average_m = sum / float(len(P_m_hourly_arrays))
            
            P_m_hourly_average.append(average_m)
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
        
        module_area = (simulationDict['moduley'] *simulationDict['nModsy']* simulationDict['modulex'])
        
        annual_power_per_area_m = (annual_power_per_module_m / module_area)    #[W/m^2] annual monofacial poutput power per module area
        '''print("Yearly monofacial output power per module area: " + str(annual_power_per_area_m) + " W/m^2")
        print("Yearly monofacial output energy per module area: " + str(annual_power_per_area_m/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        ####################################################
        
        # Bifacial Gain Calculation
        
        Bifacial_gain= (annual_power_per_peak_b - annual_power_per_peak_m) / annual_power_per_peak_m
        print("Bifacial Gain: " + str(Bifacial_gain*100) + " %")
        
                
        # Create dataframe with data
        p_bi_df = pd.DataFrame({"timestamps":df_report.index, "P_bi ": P_bi_hourly_average, "P_m ": P_m_hourly_average})
        p_bi_df.set_index("timestamps")
        p_bi_df.to_csv(resultsPath + "electrical_simulation.csv")
        
        #Plot for Bifacial Power Output + Bifacial Gain
        GUI.Window.makePlotBifacialRadiance(resultsPath,Bifacial_gain)
        
    def simulate_simpleBifacial(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath):
        """
        Applies a simplified version of the electrical simulation after PVSyst. Uses bifaciality factor to calculate rear efficiency and fill factors.
        Rear open-circuit voltage and short-circuit current are calculated using rear irradiance and temperature. 
        The rear output is then determined through the rear fill factor. Then the bifacial electrical output is calculated by adding front and rear output.
        Calculates bifacial gain through a seperate monofacial electrical simulation.

        Parameters
        ----------
        moduleDict: module Dictionary containing module data
        simulationDict: simulation Dictionary, which can be found in BifacialSimu_main.py
        df_reportVF: Viewfactor simulation report
        df_reportRT: Raytracing simulation report
        df_report: Final simulation report, containing VF and RT data
        resultsPath: output filepath
        df: helper DataFrame containing temperature for electrical simulation
        """
        
        
        # Build a final simulation report
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
        # Definition of simulation parameter if only front parameters are available
        # Procedure after PVSyst
        V_mpp_f0 = moduleDict['V_mpp_f']
            
        I_mpp_f0 = moduleDict['I_mpp_f']
                
        I_sc_f0 = moduleDict['I_sc_f']
        
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
        
        n_back = (moduleDict['bi_factor']*moduleDict['n_front'])
        
        FF_fr = (n_back*q_stc_rear*(moduleDict['moduley'])*(simulationDict['modulex']))/(I_sc_f0 * V_oc_f0)
                       
        dpi = 150 #Quality for plot export
        
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
        
        if simulationDict['simulationMode'] == 3:
            df = df.reset_index()
            
            df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
            df = df.set_index('time')
            df['timestamp'] = df['corrected_timestamp'].dt.strftime('%m-%d %H:%M%')
            df['timestamp'] = pd.to_datetime(df['timestamp'])  
            #df['timestamp'] = df['timestamp'].dt.tz_localize(None)
            df = df.set_index('timestamp')
            
            dtStart = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
        
        
            dtEnd = datetime.datetime(simulationDict['endHour'][0], simulationDict['endHour'][1], simulationDict['endHour'][2], simulationDict['endHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
            mask = (df.index >= dtStart) & (df.index <= dtEnd) 
            df = df.loc[mask]
        
        df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
        df = df.set_index('time')
        print(df_report)
        
        
        
        # Loop to calculate the Monofacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front = "row_" + str(i) + "_qabs_front"
            key_back = "row_" + str(i) + "_qabs_back"
        
            P_bi_hourly = []
          
            for index, row in df_report.iterrows():
                
                #row_qabs_front = row[key_front]
                #row_qabs_back = row[key_back]
                
                row_qabs_front = df_report.loc[index,key_front]
                row_qabs_back = df_report.loc[index,key_back]
                T_Current = df.loc[index,'temperature']
                
                
                # calculation of frontside power output
                if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                    row_qabs_front = 0
                    P_f = 0
                    
                else:
                    V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
                    I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
                    P_f = FF_f0 * V_oc_f * I_sc_f

                # calculation of backside power output
                if math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                    row_qabs_back = 0
                    P_r = 0
                    
                else:
                    V_oc_r = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_back / q_stc_rear))
                    I_sc_r = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_back / q_stc_rear)
                    P_r = FF_fr * V_oc_r * I_sc_r
                    
                
                P_bi = P_f + P_r 
                
        
                
                sum_energy_b += P_bi # Sum up the energy of every row in every hour

                P_bi_hourly.append(P_bi)
                
            # Append P_bi_hourly array to arrays
            P_bi_hourly_arrays.append(P_bi_hourly)

            print(sum_energy_b)
                
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
        p_bi_df.to_csv(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
        
        
        annual_power_per_module_b = (sum_energy_b/simulationDict['nRows']) #[W] annual bifacial output power per module
        print("Yearly bifacial output power per module: " + str(annual_power_per_module_b) + " W/module")
        print("Yearly bifacial output energy per module: " + str(annual_power_per_module_b/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
        print ("\n")
        
        annual_power_per_peak_b = (sum_energy_b/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual bifacial output power per module peak power
        print("Yearly bifacial output power per module peak power: " + str(annual_power_per_peak_b) + " W/Wp")
        print("Yearly bifacial output energy per module peak power: " + str(annual_power_per_peak_b) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")
        
        module_area = (simulationDict['moduley'] * simulationDict['nModsy'] * simulationDict['modulex'])
        
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
        f.savefig("P_bi_hourly" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
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
                #row_qabs_front = row[key_front_mono]
                #T_Current = df.loc[index,'temperature']
                row_qabs_front = df_report.loc[index,key_front_mono]
                T_Current = df.loc[index,'temperature']

                if math.isnan(row_qabs_front):
                    row_qabs_front = 0     
                
                if  row_qabs_front > 0.0:
              
                    V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
                    I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
                    P_m = FF_f0 * V_oc_f * I_sc_f
                
             
                    sum_energy_m += P_m # Sum up the energy of every row in every hour
                

        
        annual_power_per_module_m = (sum_energy_m/simulationDict['nRows']) #[W] annual monofacial output power per module
        print("Yearly monofacial output power per module: " + str(annual_power_per_module_m) + " W/module")
        print("Yearly monofacial output energy per module: " + str(annual_power_per_module_m/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
        print ("\n")
        
        annual_power_per_peak_m = (sum_energy_m/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual monofacial output power per module peak power
        print("Yearly monofacial output power per module peak power: " + str(annual_power_per_peak_m) + " W/Wp")
        print("Yearly monofacial output energy per module peak power: " + str(annual_power_per_peak_m) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")
        
        module_area = (simulationDict['moduley'] *simulationDict['nModsy']* simulationDict['modulex'])
        
        annual_power_per_area_m = (annual_power_per_module_m / module_area)    #[W/m^2] annual monofacial poutput power per module area
        print("Yearly monofacial output power per module area: " + str(annual_power_per_area_m) + " W/m^2")
        print("Yearly monofacial output energy per module area: " + str(annual_power_per_area_m/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")
        
        ####################################################
        
        # Bifacial Gain Calculation
        
        Bifacial_gain= (annual_power_per_peak_b - annual_power_per_peak_m) / annual_power_per_peak_m
        print("Bifacial Gain: " + str(Bifacial_gain*100) + " %")
        
        #Plot for Bifacial Power Output + Bifacial Gain
        GUI.Window.makePlotBifacialRadiance(resultsPath,Bifacial_gain)         