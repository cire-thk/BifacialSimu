# -*- coding: utf-8 -*-
"""
Created on Thu Jun  8 10:42:31 2023

@author: Arsene Siewe Towoua
"""

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

# from IPython import get_ipython
# get_ipython().magic('reset -sf')
from pathlib import Path
import sys
import pandas as pd #pandas = can read .csv as input
import matplotlib.pyplot as plt #display shadows
import numpy as np
import os #to import directories
from bifacial_radiance import *
import datetime
from tqdm import tqdm
import math
import dateutil.tz

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
rootPath = rootPath = os.path.realpath("../../")

#adding rootPath to sysPath
sys.path.append(rootPath)


from BifacialSimu_src import GUI
from BifacialSimu_src.BifacialSimu.Handler import BifacialSimu_radiationHandler 
from BifacialSimu_src import globals




# electric-calculation Klasse
    
    # Functions for One-Diode Model

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
        df_report.to_csv(Path(resultsPath + "radiation_qabs_results.csv"))
        
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
        
        soilrate = simulationDict['fixSoilrate']
        days_until_clean = simulationDict['days_until_clean']
        
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
        
        df_time_soiling = pd.DataFrame(df_report['corrected_timestamp'])
        df_time_soiling['month'] = df_report['corrected_timestamp'].dt.strftime('%m') # Needed to choose wright soiling rate from SimulationDict                                            
        df_time_soiling = df_time_soiling.reset_index(drop = True)
        
        
        
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
            
            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
            x = 0 #counting variable in loop to get current month from df_time_soiling
                        
            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                if temp == days_until_clean*24:
                    temp = 0
                else:
                    temp = temp +1

                if simulationDict["mathematicalSoilingrate"] == True:
                    soilrate = simulationDict["hourlySoilrate"]

                    for i in range(len(soilrate)):

                        
                        row_qabs_front = df_report.loc[index,key_front] * (1 - soilrate[i])
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate[i]/(8.8)))
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
                    
                #
                elif simulationDict["monthlySoilingrate"] == True:
                          
                    soilrate = simulationDict["variableSoilrate"][int(df_time_soiling['month'][x])]
                    
                x = x+1
                
                # calculate front row power output including the soiling rate determined in GUI                               
                row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate*(temp)/(24)))   
                # calculate back row power output including the decreased soiling for backside of PV module                                 
                row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate*(temp)/(24*8.8)))
                
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
        
       
# =============================================================================
#        at this point we have an hourly average of P_bi for every row in every hour
# =============================================================================
        
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
      
        
        f = plt.Figure(figsize=(12, 3))
        ax1 = f.subplots(1)
        ax1.locator_params(tight=True, nbins=6)
        ax1.plot(P_bi_hourly)
        ax1.set_title('Bifacial output Power hourly')
        ax1.set_xlabel('Hour')
        ax1.set_ylabel('W')
        f.savefig("P_bi_hourly" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
        #plt.show()()
        #sns wird entfernt da die Plots in der GUI ansonsten nicht richtig angezeigt werden können außerhalb der Konsole
        ##plt.show()(sns)
        
        
        ####################################################
        # Monofacial performance Calculation
        
        # Set Energy to Zero       
        sum_energy_m = 0
        sum_power_m = 0
        
        # Loop to calculate the Monofacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front_mono = "row_" + str(i) + "_qabs_front"
            P_m_hourly = []
            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
            x = 0 #counting variable in loop to get current month from df_time_soiling
            #
            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                if temp == days_until_clean*24:
                    temp = 0
                else:
                    temp = temp +1

                if simulationDict["mathematicalSoilingrate"] == True:
                    soilrate = simulationDict["hourlySoilrate"]

                    for i in range(len(soilrate)):
                        #                        
                        #SG
                        row_qabs_front = df_report.loc[index,key_front_mono] * (1 - soilrate[i])
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
                #
                #
                elif simulationDict["monthlySoilingrate"] == True:
                    soilrate = simulationDict["variableSoilrate"][int(df_time_soiling['month'][x])]
                x = x+1

                row_qabs_front = df_report.loc[index,key_front_mono] * (1 - ((soilrate*(temp))/(24)))
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
        #   

        P_m_hourly_average = []
        
        for i in tqdm(range(0, len(P_m_hourly_arrays[0]))):
            sum = 0
          
            for j in range(0, len(P_m_hourly_arrays)):
                sum += P_m_hourly_arrays[j][i]
                
            average_m = sum / float(len(P_m_hourly_arrays))
            
            P_m_hourly_average.append(average_m)
                 #else:
                    #print("Power: 0.0")
             
                    
        mismatch_array = Electrical_simulation.calculate_mismatch(P_m_hourly_average, P_mpp0)

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
        # print("Bifacial Gain: " + str(Bifacial_gain*100) + " %")
        
                
        # Create dataframe with data
        p_bi_df = pd.DataFrame({"timestamps":df_report.index, "P_bi ": P_bi_hourly_average, "P_m ": P_m_hourly_average, "Mismatch":mismatch_array})
        p_bi_df.set_index("timestamps")
        p_bi_df.to_csv(Path(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv"))
        
        #Plot for Bifacial Power Output + Bifacial Gain
        # GUI.Window.makePlotBifacialRadiance(resultsPath,Bifacial_gain)
        # GUI.Window.makePlotMismatch(resultsPath,checkbutton_state)
        
        return Bifacial_gain*100
    
    def calculate_mismatch(P_array, P_cell):
        
        mismatch=[]
        m=0       
        
        if P_cell==0:
            print('ERROR: Please enter the Module MPP in GUI (P_mpp value is 0)')
            mismatch=float('nan')
            return mismatch
        
        else:
            for i in range(len(P_array)):  
            
                m= (1-(P_array[i])/P_cell)*100
                mismatch.append(m)
                
            return mismatch 


    
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
        
        bi_factor = moduleDict['bi_factor']
        
        soilrate = simulationDict['fixSoilrate']
        days_until_clean = simulationDict['days_until_clean']
        
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
        
        #n_back = (moduleDict['bi_factor']*moduleDict['n_front'])
        
        #FF_fr = (n_back*q_stc_rear*(simulationDict['moduley'])*(simulationDict['modulex']))/(I_sc_f0 * V_oc_f0)
                       
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
        
        #df_time_soiling = pd.DataFrame(df['corrected_timestamp'])
        #df_time_soiling['month'] = df['corrected_timestamp'].dt.strftime('%m') # Needed to choose wright soiling rate from SimulationDict                                            
        df_time_soiling = df_time_soiling.reset_index(drop = True)
        
        df_time_soiling = pd.DataFrame(df_report['corrected_timestamp'])
        df_time_soiling['month'] = df_report['corrected_timestamp'].dt.strftime('%m') # Needed to choose wright soiling rate from SimulationDict                                            
        df_time_soiling = df_time_soiling.reset_index(drop = True)
        
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

        # Loop to calculate the Bifacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front = "row_" + str(i) + "_qabs_front"
            key_back = "row_" + str(i) + "_qabs_back"
        
            P_bi_hourly = []
            
            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
            x = 0 #counting variable in loop to get current month from df_time_soiling
            
            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                if temp == days_until_clean*24:
                    temp = 0
                else:
                    temp = temp +1

                if simulationDict["mathematicalSoilingrate"] == True:
                    soilrate = simulationDict["hourlySoilrate"]

                    for i in range(len(soilrate)):
                        
                        #row_qabs_front = row[key_front]
                        #row_qabs_back = row[key_back]
                        
                        row_qabs_front = df_report.loc[index,key_front] * (1 - soilrate[i])
                        row_qabs_back = df_report.loc[index,key_back] (1 - (soilrate[i]/(8.8)))
                        row_qabs_combined = row_qabs_front + (row_qabs_back*bi_factor)
                        T_Current = df.loc[index,'temperature']
                        
                        
                        # calculation of frontside power output
                        if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                            row_qabs_front = 0
                            P_bi = 0     

                        # calculation of backside power output
                        elif math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                            row_qabs_back = 0
                            P_bi = 0
                       
                        else:
                            V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_combined / q_stc_front))
                            I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_combined / q_stc_front)
                            P_bi = FF_f0 * V_oc_f * I_sc_f
                        

                        sum_energy_b += P_bi # Sum up the energy of every row in every hour

                        P_bi_hourly.append(P_bi)
                        
                    # Append P_bi_hourly array to arrays
                    P_bi_hourly_arrays.append(P_bi_hourly)

                    print(sum_energy_b)
                        
            #            
                elif simulationDict["monthlySoilingrate"] == True:
                    
                    soilrate = simulationDict["variableSoilrate"][int(df_time_soiling['month'][x])]
                x = x+1
                
                row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate*(temp)/(24)))
                row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate*(temp)/(24*8.8)))
                row_qabs_combined = row_qabs_front + (row_qabs_back*bi_factor)
                
                T_Current = df.loc[index,'temperature']
                
                
                # calculation of frontside power output
                if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                    row_qabs_front = 0
                    P_bi = 0     

                # calculation of backside power output
                elif math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                    row_qabs_back = 0
                    P_bi = 0
               
                else:
                    V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_combined / q_stc_front))
                    I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_combined / q_stc_front)
                    P_bi = FF_f0 * V_oc_f * I_sc_f
                

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
        '''print("Yearly bifacial output power per module: " + str(annual_power_per_module_b) + " W/module")
        print("Yearly bifacial output energy per module: " + str(annual_power_per_module_b/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
        print ("\n")'''
        
        annual_power_per_peak_b = (sum_energy_b/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual bifacial output power per module peak power
        '''print("Yearly bifacial output power per module peak power: " + str(annual_power_per_peak_b) + " W/Wp")
        print("Yearly bifacial output energy per module peak power: " + str(annual_power_per_peak_b) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        module_area = (simulationDict['moduley'] * simulationDict['nModsy'] * simulationDict['modulex'])
        
        annual_power_per_area_b = (annual_power_per_module_b / module_area)    #[W/m^2] annual bifacial poutput power per module area
        '''print("Yearly bifacial output power per module area: " + str(annual_power_per_area_b) + " W/m^2")
        print("Yearly bifacial output energy per module area: " + str(annual_power_per_area_b/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        # Plot total qinc front and back for every row
        f = plt.Figure(figsize=(12, 3))
        ax1 = f.subplots(1)
        ax1.locator_params(tight=True, nbins=6)
        #f.plot(P_bi_hourly)
        ax1.set_title('Bifacial output Power hourly')
        ax1.set_xlabel('Hour')
        ax1.set_ylabel('W')
        f.savefig("P_bi_hourly" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
        #plt.show()()
        ##plt.show()(sns)
         
        ####################################################
        # Monofacial performance Calculation
        
        # Set Energy to Zero       
        sum_energy_m = 0
        sum_power_m = 0
        
        # Loop to calculate the Monofacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front_mono = "row_" + str(i) + "_qabs_front"
            
            P_m_hourly = []
            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
            x = 0 #counting variable in loop to get current month from df_time_soiling
            
            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                if temp == days_until_clean*24:
                    temp = 0
                else:
                    temp = temp +1

                if simulationDict["mathematicalSoilingrate"] == True:
                    soilrate = simulationDict["hourlySoilrate"]

                    for i in range(len(soilrate)):

                        #SG
                        row_qabs_front = df_report.loc[index,key_front_mono] * (1 - soilrate[i])
                        T_Current = df.loc[index,'temperature']
                        
                        # calculation of frontside power output
                        if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                            row_qabs_front = 0
                            P_m = 0 
                            
                        else:
                            V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
                            I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
                            P_m = FF_f0 * V_oc_f * I_sc_f
                       
                        sum_energy_m += P_m # Sum up the energy of every row in every hour
            #
                elif simulationDict["monthlySoilingrate"] == True:
                    
                    soilrate = simulationDict["variableSoilrate"][int(df_time_soiling['month'][x])]
                x = x+1
                
                #SG
                row_qabs_front = df_report.loc[index,key_front_mono] * (1 - ((soilrate*(temp))/(24)))
                T_Current = df.loc[index,'temperature']
                
                # calculation of frontside power output
                if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                    row_qabs_front = 0
                    P_m = 0 
                    
                else:
                    V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
                    I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
                    P_m = FF_f0 * V_oc_f * I_sc_f
               
                sum_energy_m += P_m # Sum up the energy of every row in every hour

            #
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
        
        #Plot for Bifacial Power Output + Bifacial Gain
        GUI.Window.makePlotBifacialRadiance(resultsPath,Bifacial_gain)     
        
        return Bifacial_gain*100
        
        
    def simulate_doubleDiode(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath):
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
        
        Ns = moduleDict['Ns']      #Number of cells in module
        soilrate = simulationDict['fixSoilrate'] #Michailow
        days_until_clean = simulationDict['days_until_clean']
        
        #module = moduleParameter['module']
        #inverter = moduleParameter['inverter']
        
        P_mpp0 = moduleDict['P_mpp']
        V_mpp0 = V_mpp_f0
        
        T_koeff_P = moduleDict['T_koeff_P'] 
        T_koeff_I = moduleDict['T_koeff_I'] 
        T_koeff_V = moduleDict['T_koeff_V'] 
        T_amb = moduleDict['T_amb']
                
        k = 1.3806503 * 10**(-23)       #Boltzmann constant [J/K]
        q_ec = 1.60217646 * 10**(-19)   #electron charge [C]
        
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
        
        #df_time_soiling = pd.DataFrame(df['corrected_timestamp'])
        #df_time_soiling['month'] = df['corrected_timestamp'].dt.strftime('%m') # Needed to choose wright soiling rate from SimulationDict
        #df_time_soiling = df_time_soiling.reset_index(drop = True)
        
        df_time_soiling = pd.DataFrame(df_report['corrected_timestamp'])
        df_time_soiling['month'] = df_report['corrected_timestamp'].dt.strftime('%m') # Needed to choose wright soiling rate from SimulationDict                                            
        df_time_soiling = df_time_soiling.reset_index(drop = True)
        
        
        #Diode ideality factors. a1 has to be 1 while a2 is flexible but it has to be above 1.2
        a1 = 1      
        a2 = 1.3
        
        #Tolerances for current and power in Mpp calculation algorythm
        tol_I = 0.001 
        tol_P = 0.002
        
        #Calculation of Parameters that do not change in the loop
        P_mpp_f0 = V_mpp_f0 * I_mpp_f0                      #P_mpp is calculated from Mpp Voltage and Current
        Vt = (Ns * k * (25+273.15)) / q_ec                  #Thermal voltage at STC                                     
        I_0_f0 = (I_sc_f0) / (np.exp((V_oc_f0) / (Vt))-1)   #Calculation of saturation current. It is assumed that its the same for both diodes

        #Starting values fpr Rs and Rp
        Rs_f0 = 0
        Rp_min = (V_mpp_f0 / (I_sc_f0 - I_mpp_f0)) - ((V_oc_f0 - V_mpp_f0) / I_mpp_f0)
        Rp_f0 = Rp_min
        
        #Starting parameters for Current, Voltage, and Power
        I = 0
        V = 0
        P = 0
        P1 = 0
        P_mpp_fs0 = 0
        
        #Definition of lists for the I-V P-V plots
        Vfplt = []
        Ifplt = []
        Pfplt = []
               
        #Rs and Rp calculation for the front side. They are calculated at STC. The algorythm tries to match the Mpp of the Module parameters
        #by adjusting Rs and calculating Rp based on Rs.
        for xf in range (1000000):
           
            
           #If the calculation takes too many iterations, an error message will show up.
           if xf == 999999:                     
                print ('Error: The calculation of the front resistances exeeded one million iterations. Please check your parameters.')
                     
           #'Calculation' of the photo current. At STC the I_sc is the photo current.        
           I_ph_f0 = I_sc_f0                                             
       
           #Newtons method to find the current that solves the equation f_I  
           f_I = I_ph_f0 - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt) + np.exp((V + I * Rs_f0) / (Vt * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
           f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt) * np.exp((V + I * Rs_f0) / Vt) - ((I_0_f0 * Rs_f0) / (Vt * a2)) * np.exp((V+ I * Rs_f0) / (Vt * a2)) - (Rs_f0 / Rp_f0) - 1
       
           I2 = I - (f_I/f_dI)
              
           #Check if the new value of I2 is close enough (in tolerance) to the old value I
           if I + tol_I >= I2 and I2 >= I - tol_I:
               P2 = V * I2          #If the current was calculated correctly the power will be calculated
               
               Vfplt.append(V)      #The values of current, voltage and power are added to their designated lists
               Ifplt.append(I2)
               Pfplt.append(P2)
               
               if P2 > P1:          #Check if the new power value is greater than the last. If yes it becomes the new reference power value.
                   P1 = P2
               
               else:
                   P_mpp_fs0 = P1   #If the power does not increase however, the Mpp of this P-V curve is found
                   
                   
                           
               if V >= V_oc_f0:     # When V reaches V_oc the P-V curve is complete and it has to be checked if Mpp converged with the Module parameters
               
                   #If the calculated Mpp is within the tolerance the script tells the user the Values of Rs and Rp aswell as the amount of iterations
                   #it took to calculate them                   
                   if P_mpp_f0 + tol_P >= P_mpp_fs0 and P_mpp_fs0 >= P_mpp_f0 - tol_P:
                       print ('Front resistance calculation completed in ',xf,' iterations.', 'Rs_f0 =', Rs_f0, 'Rp_f0 =', Rp_f0)
                       
                       
                       #The P-V and I-V curve is plotted with the values since the last Rs, Rp adjustment
                       f = plt.Figure(figsize=(6, 6))
                       ax1 = f.subplots(1)
                       ax1.locator_params(tight=True, nbins=6)
                       ax1.plot(Vfplt[-round(V_oc_f0 * 10):], Ifplt[-round(V_oc_f0 * 10):], color = "red")
                       ax1.set_title('P-V I-V Curve front side', fontsize=14)
                       ax1.set_xlabel('Voltage [V]', fontsize=14)
                       ax1.set_ylabel('Current [I]', fontsize=14, color = 'red')
                       ax2=ax1.twinx()
                       ax2.plot(Vfplt[-round(V_oc_f0 * 10):], Pfplt[-round(V_oc_f0 * 10):], color = "blue")
                       ax2.set_ylabel('Power [W]', fontsize=14, color = 'blue')
                       f.savefig("P-V_I-V_Curve_front" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
                       #plt.show()()
 
                       #Rs and Rp have been calculated so the script quits the loop 
                       break
                   
                   #If the calculated Mpp is not within tolerance, the reference power is reset and Rs gets increased by 10 mOhm 
                   else:
                       P1 = 0
                   
                       Rs_f0 = Rs_f0 + 0.01
                   
                       #Calculation of Rp with new Rs. For a better overview it is split into smaller calculations
                       r1 = V_mpp_f0 + I_mpp_f0 * Rs_f0
                       r2 = I_ph_f0
                       r3 = np.exp(r1/Vt)
                       r4 = np.exp(r1/(Vt*a2))
                       r5 = P_mpp_f0/V_mpp_f0
                       r6 = (r3 + r4 + 2)
                       r7 = r6 * I_0_f0

                       Rp_f0 = r1 / (r2 - r7 - r5)
                                     
                   V = -0.1     #V reached its max so it is set to -0.1 so in the first iteration we have I=0 and V=0
               I = 0
               V = V + 0.1
           else:
               I = I2           #If I2 was not close enough to I, I becomes I2 (newtons method)
        

        #After the calculation of Rs and Rp for the front side, the rear side is calculated in the same way, with values from the back side
        P_mpp_r0 = V_mpp_r0 * I_mpp_r0
        Vt = (Ns * k * (25+273.15)) / q_ec
        I_0_r0 = (I_sc_r0) / (np.exp((V_oc_r0) / (Vt))-1)   

        #Starting values fpr Rs and Rp
        Rs_r0 = 0
        Rp_min = (V_mpp_r0 / (I_sc_r0 - I_mpp_r0)) - ((V_oc_r0 - V_mpp_r0) / I_mpp_r0)
        Rp_r0 = Rp_min

        I = 0
        V = 0
        P = 0
        P1 = 0
        P_mpp_rs0 = 0
        
        Vrplt = []
        Irplt = []
        Prplt = []        
        
        #Rs and Rp calculation for the rear side. They are calculated at STC. The algorythm tries to match the Mpp of the Module parameters
        #by adjusting Rs and calculating Rp based on Rs.
        for xr in range (1000000):
       
           if xr == 999999:
                print ('Error: The calculation of the rear resistances exeeded one million iterations. Please check your parameters.')
        
           
           
                  
           #'Calculation' of the photo current. At STC the I_sc is the photo current.        
           I_ph_r0 = I_sc_r0                                             
       
           #Newtons method to find the current that solves the equation f_I  
           f_I = I_ph_r0 - I_0_r0 * (np.exp((V+ I * Rs_r0) / Vt) + np.exp((V + I * Rs_r0) / (Vt * a2)) - 2) - ((V + I * Rs_r0) / Rp_r0) - I
           f_dI = (-1) * ((I_0_r0 * Rs_r0) / Vt) * np.exp((V + I * Rs_r0) / Vt) - ((I_0_r0 * Rs_r0) / (Vt * a2)) * np.exp((V+ I * Rs_r0) / (Vt * a2)) - (Rs_r0 / Rp_r0) - 1
       
           I2 = I - (f_I/f_dI)
              
       
           if I + tol_I >= I2 and I2 >= I - tol_I:
               P2 = V * I2
               Vrplt.append(V)
               Irplt.append(I2)
               Prplt.append(P2)
               
               if P2 > P1:
                   P1 = P2
               
               else:
                   P_mpp_rs0 = P1              
                          
               if V >= V_oc_r0:
                   if P_mpp_r0 + tol_P >= P_mpp_rs0 and P_mpp_rs0 >= P_mpp_r0 - tol_P:
                       print ('Rear resistance calculation completed in ',xr,' iterations.', 'Rs_r0 =', Rs_r0, 'Rp_r0 =', Rp_r0)
                       
                       f, (ax1) = plt.subplots(1, figsize=(6, 6))
                       ax1.locator_params(tight=True, nbins=6)
                       ax1.plot(Vfplt[-round(V_oc_r0 * 10):], Ifplt[-round(V_oc_r0 * 10):], color = "red")
                       ax1.set_title('P-V I-V Curve back side', fontsize=14)
                       ax1.set_xlabel('Voltage [V]', fontsize=14)
                       ax1.set_ylabel('Current [I]', fontsize=14, color = 'red')
                       ax2=ax1.twinx()
                       ax2.plot(Vrplt[-round(V_oc_r0 * 10):], Prplt[-round(V_oc_r0 * 10):], color = "blue")
                       ax2.set_ylabel('Power [W]', fontsize=14, color = 'blue')
                       f.savefig("P-V_I-V_Curve_back" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
                       #plt.show()()                       
                       
                       
                       break
                   else:
                       P1 = 0
                   
                       Rs_r0 = Rs_r0 + 0.01
                   
                       r1 = V_mpp_r0 + I_mpp_r0 * Rs_r0
                       r2 = I_ph_r0
                       r3 = np.exp(r1/Vt)
                       r4 = np.exp(r1/(Vt*a2))
                       r5 = P_mpp_r0/V_mpp_r0
                       r6 = (r3 + r4 + 2)
                       r7 = r6 * I_0_r0

                       Rp_r0 = r1 / (r2 - r7 - r5)
                                     
                   V = -0.1
               I = 0
               V = V + 0.1
           else:
               I = I2        
        

        
        sum_energy_m = 0
        sum_power_m = 0
        
        
        # Loop to calculate the Bifacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front = "row_" + str(i) + "_qabs_front"
            key_back = "row_" + str(i) + "_qabs_back"
            
            P_m_hourly = []
            P_bi_hourly = []
            
            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
            x = 0 #counting variable in loop to get current month from df_time_soiling
            
            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                if temp == days_until_clean*24:
                    temp = 0
                else:
                    temp = temp +1

                if simulationDict["mathematicalSoilingrate"] == True:
                    soilrate = simulationDict["hourlySoilrate"]

                    for i in range(len(soilrate)):

                        #row_qabs_front = row[key_front]
                        #row_qabs_back = row[key_back]
                        
                        row_qabs_front = df_report.loc[index,key_front] * (1 - soilrate[i])
                        row_qabs_back = df_report.loc[index,key_back] (1 - (soilrate[i]/(8.8)))
                        
                        T_Current = df.loc[index,'temperature']
                        
                        #print("front: " + str(row_qabs_front))
                        #print("back: " + str(row_qabs_back))
                        if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                            row_qabs_front = 0
                            
                        if math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                            row_qabs_back = 0

                        
                        if row_qabs_back + row_qabs_front > 0.0:
                            
                            #Now that Rs and Rp are calculated for both sides of the module, the power calculation starts.
                            #Values are now adjusted for temperature and later also irradiation
                            
                            I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb))     
                            I_sc_r = I_sc_r0 * (1 + T_koeff_I * (T_Current - T_amb))
                            
                            V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb))
                            V_oc_r = V_oc_r0 * (1 + T_koeff_V * (T_Current - T_amb))
                            
                            #setting starting parameters for the loop
                            I = 0
                            V = 0
                            P = 0
                            P1 = 0
                            P_mpp_sf = 0
                            
                            
                            #Modified version of the Rs, Rp calculation loop. Since Rs and Rp are now given, the loop needs only a fraction of iterations
                            #to calculate the power from a given irradiance and temperature
                            #The way this works is that the algorythm searches for the Mpp of the module with the given irradiance and temperature
                            #Just like a real PV system would do
                            #It 'draws' the P-V curve and finds the Mpp which is then the power output of the module
                            for yf in range (100000):
                                
                                if row_qabs_front == 0:
                                    P_m = 0
                                    P_mpp_sf = 0
                                    break
                                
                                #Calculation of the photo current + correction for irrandiance and temperature
                                Vt_f = (Ns * k * (T_Current + 273.15)) / q_ec

                                #Calculation of the saturation current
                                I_0_f0 = (I_sc_f) / (np.exp((V_oc_f) / (Vt_f))-1)

                                #adjustment ot the photo current for irradiation
                                I_ph_f0 = I_sc_f                                             
                                I_ph_f = I_ph_f0 * (row_qabs_front / q_stc_front) 
                      
                                #newthons method to find the matching current for a given voltage
                                f_I = I_ph_f - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt_f) + np.exp((V + I * Rs_f0) / (Vt_f * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
                                f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt_f) * np.exp((V + I * Rs_f0) / Vt_f) - ((I_0_f0 * Rs_f0) / (Vt_f * a2)) * np.exp((V+ I * Rs_f0) / (Vt_f * a2)) - (Rs_f0 / Rp_f0) - 1
               
                                I2 = I - (f_I/f_dI)
                      
               
                                if I + tol_I >= I2 and I2 >= I - tol_I:         #Once I is found, the Power check starts just like in xf loop
                                    P2 = V * I2

                                    if P2 > P1:                 #Check if the new power is higher than the last
                                        P1 = P2                 #If this is true, it becomes the new reference value
                       
                                    else:
                                        P_mpp_sf = P1           #The highest calculated power gets added to P_mpp_sf
                                        
                                    if V >= V_oc_f:             # If V reached V_oc, the P-V curve is complete and the Mpp can be searched
                                        P_f = P_mpp_sf          #P_mpp_sf is the calculated Mpp for the Module for the given irradiance and and temperature
                                        P_m = P_f
                                        sum_energy_m += P_m     #The value gets added to a list for Bifacial gain calculation
                                        yf = 0                  #Iterations get reset after successful Mpp calculation
                                        break                   #The Mpp was found, the script quits the loop
                                  
                       
                                    I = 0                       #Since there is only one P-V curve to calculate, V does not have to be reset
                                    V = V + 0.1
                                else:
                                    I = I2
                                
                                    
                            ##################################
                            ###Same procedure for rear side###
                            ##################################
                            I = 0
                            V = 0
                            P = 0
                            P1 = 0
                            
                            
                            
                            for yr in range (100000):
                                
                                if row_qabs_front == 0:
                                    P_mpp_sr = 0
                                    break
                          
                                #Calculation of the photo current + correction for irrandiance and temperature
                                Vt_r = (Ns * k * (T_Current + 273.15)) / q_ec
         
                                I_0_r0 = (I_sc_r) / (np.exp((V_oc_r) / (Vt_r))-1)
               
                                I_ph_r0 = I_sc_r                                             
                                I_ph_r = I_ph_r0 * (row_qabs_back / q_stc_rear) 
                      
                                f_I = I_ph_r - I_0_r0 * (np.exp((V+ I * Rs_r0) / Vt_r) + np.exp((V + I * Rs_r0) / (Vt_r * a2)) - 2) - ((V + I * Rs_r0) / Rp_r0) - I
                                f_dI = (-1) * ((I_0_r0 * Rs_r0) / Vt_r) * np.exp((V + I * Rs_r0) / Vt_r) - ((I_0_r0 * Rs_r0) / (Vt_r * a2)) * np.exp((V+ I * Rs_r0) / (Vt_r * a2)) - (Rs_r0 / Rp_r0) - 1
               
                                I2 = I - (f_I/f_dI)
                      
               
                                if I + tol_I >= I2 and I2 >= I - tol_I:
                                    P2 = V * I2

                                    if P2 > P1:
                                        P1 = P2
                       
                                    else:
                                        P_mpp_sr = P1
                                  
                                    if V >= V_oc_r:
                                        P_r = P_mpp_sr 
                                        yr = 0
                                        break
                                  
                       
                                    I = 0
                                    V = V + 0.1
                                else:
                                    I = I2                    
                            
                        
                            P_bi = P_mpp_sf + P_mpp_sr
                            #print("Power: " + str(P_bi))
                    
                            sum_energy_b += P_bi # Sum up the energy of every row in every hour
                    
                        else:
                            P_m=0
                            P_bi=0
                        
                        P_m_hourly.append(P_m)
                        P_bi_hourly.append(P_bi)
                    
                    # Append P_bi_hourly array to arrays
                    P_m_hourly_arrays.append(P_m_hourly)
                    P_bi_hourly_arrays.append(P_bi_hourly)
            #
                elif simulationDict["monthlySoilingrate"] == True:
                    
                    soilrate = simulationDict["variableSoilrate"][int(df_time_soiling['month'][x])]
                x = x+1
                
                row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate*(temp)/(24)))
                row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate*(temp)/(24*8.8)))
               
                T_Current = df.loc[index,'temperature']
                
                #print("front: " + str(row_qabs_front))
                #print("back: " + str(row_qabs_back))
                if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                    row_qabs_front = 0
                    
                if math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                    row_qabs_back = 0

                
                if row_qabs_back + row_qabs_front > 0.0:
                    
                    #Now that Rs and Rp are calculated for both sides of the module, the power calculation starts.
                    #Values are now adjusted for temperature and later also irradiation
                    
                    I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb))     
                    I_sc_r = I_sc_r0 * (1 + T_koeff_I * (T_Current - T_amb))
                    
                    V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb))
                    V_oc_r = V_oc_r0 * (1 + T_koeff_V * (T_Current - T_amb))
                    
                    #setting starting parameters for the loop
                    I = 0
                    V = 0
                    P = 0
                    P1 = 0
                    P_mpp_sf = 0
                    
                    
                    #Modified version of the Rs, Rp calculation loop. Since Rs and Rp are now given, the loop needs only a fraction of iterations
                    #to calculate the power from a given irradiance and temperature
                    #The way this works is that the algorythm searches for the Mpp of the module with the given irradiance and temperature
                    #Just like a real PV system would do
                    #It 'draws' the P-V curve and finds the Mpp which is then the power output of the module
                    for yf in range (100000):
                        
                        if row_qabs_front == 0:
                            P_m = 0
                            P_mpp_sf = 0
                            break
                        
                        #Calculation of the photo current + correction for irrandiance and temperature
                        Vt_f = (Ns * k * (T_Current + 273.15)) / q_ec

                        #Calculation of the saturation current
                        I_0_f0 = (I_sc_f) / (np.exp((V_oc_f) / (Vt_f))-1)

                        #adjustment ot the photo current for irradiation
                        I_ph_f0 = I_sc_f                                             
                        I_ph_f = I_ph_f0 * (row_qabs_front / q_stc_front) 
              
                        #newthons method to find the matching current for a given voltage
                        f_I = I_ph_f - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt_f) + np.exp((V + I * Rs_f0) / (Vt_f * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
                        f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt_f) * np.exp((V + I * Rs_f0) / Vt_f) - ((I_0_f0 * Rs_f0) / (Vt_f * a2)) * np.exp((V+ I * Rs_f0) / (Vt_f * a2)) - (Rs_f0 / Rp_f0) - 1
       
                        I2 = I - (f_I/f_dI)
              
       
                        if I + tol_I >= I2 and I2 >= I - tol_I:         #Once I is found, the Power check starts just like in xf loop
                            P2 = V * I2

                            if P2 > P1:                 #Check if the new power is higher than the last
                                P1 = P2                 #If this is true, it becomes the new reference value
               
                            else:
                                P_mpp_sf = P1           #The highest calculated power gets added to P_mpp_sf
                                
                            if V >= V_oc_f:             # If V reached V_oc, the P-V curve is complete and the Mpp can be searched
                                P_f = P_mpp_sf          #P_mpp_sf is the calculated Mpp for the Module for the given irradiance and and temperature
                                P_m = P_f
                                sum_energy_m += P_m     #The value gets added to a list for Bifacial gain calculation
                                yf = 0                  #Iterations get reset after successful Mpp calculation
                                break                   #The Mpp was found, the script quits the loop
                          
               
                            I = 0                       #Since there is only one P-V curve to calculate, V does not have to be reset
                            V = V + 0.1
                        else:
                            I = I2
                        
                            
                    ##################################
                    ###Same procedure for rear side###
                    ##################################
                    I = 0
                    V = 0
                    P = 0
                    P1 = 0
                    
                    
                    
                    for yr in range (100000):
                        
                        if row_qabs_front == 0:
                            P_mpp_sr = 0
                            break
                  
                        #Calculation of the photo current + correction for irrandiance and temperature
                        Vt_r = (Ns * k * (T_Current + 273.15)) / q_ec
 
                        I_0_r0 = (I_sc_r) / (np.exp((V_oc_r) / (Vt_r))-1)
       
                        I_ph_r0 = I_sc_r                                             
                        I_ph_r = I_ph_r0 * (row_qabs_back / q_stc_rear) 
              
                        f_I = I_ph_r - I_0_r0 * (np.exp((V+ I * Rs_r0) / Vt_r) + np.exp((V + I * Rs_r0) / (Vt_r * a2)) - 2) - ((V + I * Rs_r0) / Rp_r0) - I
                        f_dI = (-1) * ((I_0_r0 * Rs_r0) / Vt_r) * np.exp((V + I * Rs_r0) / Vt_r) - ((I_0_r0 * Rs_r0) / (Vt_r * a2)) * np.exp((V+ I * Rs_r0) / (Vt_r * a2)) - (Rs_r0 / Rp_r0) - 1
       
                        I2 = I - (f_I/f_dI)
              
       
                        if I + tol_I >= I2 and I2 >= I - tol_I:
                            P2 = V * I2

                            if P2 > P1:
                                P1 = P2
               
                            else:
                                P_mpp_sr = P1
                          
                            if V >= V_oc_r:
                                P_r = P_mpp_sr 
                                yr = 0
                                break
                          
               
                            I = 0
                            V = V + 0.1
                        else:
                            I = I2                    
                    
                
                    P_bi = P_mpp_sf + P_mpp_sr
                    #print("Power: " + str(P_bi))
            
                    sum_energy_b += P_bi # Sum up the energy of every row in every hour
            
                else:
                    P_m=0
                    P_bi=0
                
                P_m_hourly.append(P_m)
                P_bi_hourly.append(P_bi)
            
            # Append P_bi_hourly array to arrays
            P_m_hourly_arrays.append(P_m_hourly)
            P_bi_hourly_arrays.append(P_bi_hourly)

        P_bi_hourly_average = []
        
        for i in tqdm(range(0, len(P_bi_hourly_arrays[0]))):
            sum = 0
          
            for j in range(0, len(P_bi_hourly_arrays)):
                sum += P_bi_hourly_arrays[j][i]
                
            average = sum / float(len(P_bi_hourly_arrays))
            
            P_bi_hourly_average.append(average)
            
       
        
        # The time gets implemented in the GUI
    # p_bi_df.to_csv(resultsPath + "simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
        
        
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
      
        
        f = plt.Figure(figsize=(12, 3))
        ax1 = f.subplots(1)
        ax1.locator_params(tight=True, nbins=6)
        f.plot(P_bi_hourly)
        ax1.set_title('Bifacial output Power hourly')
        ax1.set_xlabel('Hour')
        ax1.set_ylabel('W')
        f.savefig("P_bi_hourly" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
        #plt.show()()
        ##plt.show()(sns)
        
        
        ####################################################
        # Monofacial performance Calculation
        
      # Set Energy to Zero       
        sum_energy_m = 0
        sum_power_m = 0
        
        # Loop to calculate the Monofacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front_mono = "row_" + str(i) + "_qabs_front"
            P_m_hourly = []
            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
            x = 0 #counting variable in loop to get current month from df_time_soiling
            
            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                if temp == days_until_clean*24:
                    temp = 0
                else:
                    temp = temp +1

                if simulationDict["mathematicalSoilingrate"] == True:
                    soilrate = simulationDict["hourlySoilrate"]

                    for i in range(len(soilrate)):
                        #SG
                        row_qabs_front = df_report.loc[index,key_front_mono] * (1 - soilrate[i])
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
            #
                elif simulationDict["monthlySoilingrate"] == True:
                    soilrate = simulationDict["variableSoilrate"][int(df_time_soiling['month'][x])]
                x = x+1
                #SG
                row_qabs_front = df_report.loc[index,key_front_mono] * (1 - ((soilrate*(temp))/(24)))
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
        p_bi_df.to_csv(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
        #p_bi_df.to_csv(resultsPath + "electrical_simulation.csv")
        
        #Plot for Bifacial Power Output + Bifacial Gain
        GUI.Window.makePlotBifacialRadiance(resultsPath,Bifacial_gain)   
    
        return Bifacial_gain*100

    def simulate_doubleDiodeBi(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath):
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
        
        # Note for later!:
        # moduleDict['Ns'] is not defined in moduleDict! (This can gave an error) 
        Ns = moduleDict['Ns']      #Number of cells in module
        
        soilrate = simulationDict['fixSoilrate'] #Michailow
        days_until_clean = simulationDict['days_until_clean']
        
        k = 1.3806503 * 10**(-23)       #Boltzmann constant [J/K]
        q_ec = 1.60217646 * 10**(-19)   #electron charge [C]
        
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
        
        df_time_soiling = pd.DataFrame(df['corrected_timestamp'])
        df_time_soiling['month'] = df['corrected_timestamp'].dt.strftime('%m') # Needed to choose wright soiling rate from SimulationDict
        df_time_soiling = df_time_soiling.reset_index(drop = True)
        
        #Diode ideality factors. a1 has to be 1 while a2 is flexible but it has to be above 1.2
        a1 = 1      
        a2 = 1.3
        
        #Tolerances for current and power in Mpp calculation algorythm
        tol_I = 0.001 
        tol_P = 0.002
        
        #Calculation of Parameters that do not change in the loop
        P_mpp_f0 = V_mpp_f0 * I_mpp_f0                      #P_mpp is calculated from Mpp Voltage and Current
        Vt = (Ns * k * (25+273.15)) / q_ec                  #Thermal voltage at STC                                     
        I_0_f0 = (I_sc_f0) / (np.exp((V_oc_f0) / (Vt))-1)   #Calculation of saturation current. It is assumed that its the same for both diodes

        #Starting values fpr Rs and Rp
        Rs_f0 = 0
        Rp_min = (V_mpp_f0 / (I_sc_f0 - I_mpp_f0)) - ((V_oc_f0 - V_mpp_f0) / I_mpp_f0)
        Rp_f0 = Rp_min
        
        #Starting parameters for Current, Voltage, and Power
        I = 0
        V = 0
        P = 0
        P1 = 0
        P_mpp_fs0 = 0
        
        #Definition of lists for the I-V P-V plots
        Vfplt = []
        Ifplt = []
        Pfplt = []
               
        #Rs and Rp calculation for the front side. They are calculated at STC. The algorythm tries to match the Mpp of the Module parameters
        #by adjusting Rs and calculating Rp based on Rs.
        for xf in range (1000000):
           
            
           #If the calculation takes too many iterations, an error message will show up.
           if xf == 999999:                     
                print ('Error: The calculation of the front resistances exeeded one million iterations. Please check your parameters.')
                     
           #'Calculation' of the photo current. At STC the I_sc is the photo current.        
           I_ph_f0 = I_sc_f0                                             
       
           #Newtons method to find the current that solves the equation f_I  
           f_I = I_ph_f0 - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt) + np.exp((V + I * Rs_f0) / (Vt * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
           f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt) * np.exp((V + I * Rs_f0) / Vt) - ((I_0_f0 * Rs_f0) / (Vt * a2)) * np.exp((V+ I * Rs_f0) / (Vt * a2)) - (Rs_f0 / Rp_f0) - 1
       
           I2 = I - (f_I/f_dI)
              
           #Check if the new value of I2 is close enough (in tolerance) to the old value I
           if I + tol_I >= I2 and I2 >= I - tol_I:
               P2 = V * I2          #If the current was calculated correctly the power will be calculated
               
               Vfplt.append(V)      #The values of current, voltage and power are added to their designated lists
               Ifplt.append(I2)
               Pfplt.append(P2)
               
               if P2 > P1:          #Check if the new power value is greater than the last. If yes it becomes the new reference power value.
                   P1 = P2
               
               else:
                   P_mpp_fs0 = P1   #If the power does not increase however, the Mpp of this P-V curve is found
                   
                   
                           
               if V >= V_oc_f0:     # When V reaches V_oc the P-V curve is complete and it has to be checked if Mpp converged with the Module parameters
               
                   #If the calculated Mpp is within the tolerance the script tells the user the Values of Rs and Rp aswell as the amount of iterations
                   #it took to calculate them                   
                   if P_mpp_f0 + tol_P >= P_mpp_fs0 and P_mpp_fs0 >= P_mpp_f0 - tol_P:
                       print ('Front resistance calculation completed in ',xf,' iterations.', 'Rs_f0 =', Rs_f0, 'Rp_f0 =', Rp_f0)
                       
                       
                       #The P-V and I-V curve is plotted with the values since the last Rs, Rp adjustment
                       f, (ax1) = plt.subplots(1, figsize=(6, 6))
                       ax1.locator_params(tight=True, nbins=6)
                       ax1.plot(Vfplt[-round(V_oc_f0 * 10):], Ifplt[-round(V_oc_f0 * 10):], color = "red")
                       ax1.set_title('P-V I-V Curve front side', fontsize=14)
                       ax1.set_xlabel('Voltage [V]', fontsize=14)
                       ax1.set_ylabel('Current [I]', fontsize=14, color = 'red')
                       ax2=ax1.twinx()
                       ax2.plot(Vfplt[-round(V_oc_f0 * 10):], Pfplt[-round(V_oc_f0 * 10):], color = "blue")
                       ax2.set_ylabel('Power [W]', fontsize=14, color = 'blue')
                       f.savefig("P-V_I-V_Curve_front" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
                       #plt.show()()
 
                       #Rs and Rp have been calculated so the script quits the loop 
                       break
                   
                   #If the calculated Mpp is not within tolerance, the reference power is reset and Rs gets increased by 10 mOhm 
                   else:
                       P1 = 0
                   
                       Rs_f0 = Rs_f0 + 0.01
                   
                       #Calculation of Rp with new Rs. For a better overview it is split into smaller calculations
                       r1 = V_mpp_f0 + I_mpp_f0 * Rs_f0
                       r2 = I_ph_f0
                       r3 = np.exp(r1/Vt)
                       r4 = np.exp(r1/(Vt*a2))
                       r5 = P_mpp_f0/V_mpp_f0
                       r6 = (r3 + r4 + 2)
                       r7 = r6 * I_0_f0

                       Rp_f0 = r1 / (r2 - r7 - r5)
                                     
                   V = -0.1     #V reached its max so it is set to -0.1 so in the first iteration we have I=0 and V=0
               I = 0
               V = V + 0.1
           else:
               I = I2           #If I2 was not close enough to I, I becomes I2 (newtons method)
        

        
        sum_energy_m = 0
        sum_power_m = 0
        
        
        # Loop to calculate the Bifacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front = "row_" + str(i) + "_qabs_front"
            key_back = "row_" + str(i) + "_qabs_back"
            
            P_m_hourly = []
            P_bi_hourly = []
            
            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
            x = 0 #counting variable in loop to get current month from df_time_soiling
            
            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                if temp == days_until_clean*24:
                    temp = 0
                else:
                    temp = temp +1

                if simulationDict["mathematicalSoilingrate"] == True:
                    soilrate = simulationDict["hourlySoilrate"]

                    for i in range(len(soilrate)):
                        
                        #row_qabs_front = row[key_front]
                        #row_qabs_back = row[key_back]
                        
                        row_qabs_front = df_report.loc[index,key_front] * (1 - soilrate[i])
                        row_qabs_back = df_report.loc[index,key_back] (1 - (soilrate[i]/(8.8)))
#                       row_qabs_combined = row_qabs_front + (row_qabs_back*bi_factor)
                        T_Current = df.loc[index,'temperature']
                        #
                        
                        #print("front: " + str(row_qabs_front))
                        #print("back: " + str(row_qabs_back))
                        if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                            row_qabs_front = 0
                            
                        if math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                            row_qabs_back = 0

                        
                        if row_qabs_back + row_qabs_front > 0.0:
                            
                            #Now that Rs and Rp are calculated for both sides of the module, the power calculation starts.
                            #Values are now adjusted for temperature and later also irradiation
                            
                            I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb))     
                            I_sc_r = I_sc_r0 * (1 + T_koeff_I * (T_Current - T_amb))
                            
                            V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb))
                            V_oc_r = V_oc_r0 * (1 + T_koeff_V * (T_Current - T_amb))
                            
                            #setting starting parameters for the loop
                            I = 0
                            V = 0
                            P = 0
                            P1 = 0
                            P_mpp_sf = 0
                            
                            
                            #Modified version of the Rs, Rp calculation loop. Since Rs and Rp are now given, the loop needs only a fraction of iterations
                            #to calculate the power from a given irradiance and temperature
                            #The way this works is that the algorythm searches for the Mpp of the module with the given irradiance and temperature
                            #Just like a real PV system would do
                            #It 'draws' the P-V curve and finds the Mpp which is then the power output of the module
                            for yf in range (100000):
                                
                                if row_qabs_front == 0:
                                    P_m = 0
                                    P_mpp_sf = 0
                                    break
                                
                                #Calculation of the photo current + correction for irrandiance and temperature
                                Vt_f = (Ns * k * (T_Current + 273.15)) / q_ec

                                #Calculation of the saturation current
                                I_0_f0 = (I_sc_f) / (np.exp((V_oc_f) / (Vt_f))-1)

                                #adjustment ot the photo current for irradiation
                                I_ph_f0 = I_sc_f                                             
                                I_ph_f = I_ph_f0 * (row_qabs_front / q_stc_front) 
                      
                                #newthons method to find the matching current for a given voltage
                                f_I = I_ph_f - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt_f) + np.exp((V + I * Rs_f0) / (Vt_f * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
                                f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt_f) * np.exp((V + I * Rs_f0) / Vt_f) - ((I_0_f0 * Rs_f0) / (Vt_f * a2)) * np.exp((V+ I * Rs_f0) / (Vt_f * a2)) - (Rs_f0 / Rp_f0) - 1
               
                                I2 = I - (f_I/f_dI)
                      
               
                                if I + tol_I >= I2 and I2 >= I - tol_I:         #Once I is found, the Power check starts just like in xf loop
                                    P2 = V * I2

                                    if P2 > P1:                 #Check if the new power is higher than the last
                                        P1 = P2                 #If this is true, it becomes the new reference value
                       
                                    else:
                                        P_mpp_sf = P1           #The highest calculated power gets added to P_mpp_sf
                                        
                                    if V >= V_oc_f:             # If V reached V_oc, the P-V curve is complete and the Mpp can be searched
                                        P_f = P_mpp_sf          #P_mpp_sf is the calculated Mpp for the Module for the given irradiance and and temperature
                                        P_m = P_f
                                        sum_energy_m += P_m     #The value gets added to a list for Bifacial gain calculation
                                        yf = 0                  #Iterations get reset after successful Mpp calculation
                                        break                   #The Mpp was found, the script quits the loop
                                  
                       
                                    I = 0                       #Since there is only one P-V curve to calculate, V does not have to be reset
                                    V = V + 0.1
                                else:
                                    I = I2
                                
                                    
                            ##################################
                            ###Same procedure for back side###
                            ##################################
                            I = 0
                            V = 0
                            P = 0
                            P1 = 0
                            
                            
                            
                            for yr in range (100000):
                                
                                if row_qabs_front == 0:
                                    P_mpp_sr = 0
                                    break
                          
                                #Calculation of the photo current + correction for irrandiance and temperature
                                Vt_f = (Ns * k * (T_Current + 273.15)) / q_ec
                                
                                #Calculating the bifacial gain factor
                                BG = row_qabs_back / row_qabs_front
                                
                               

                                
                                #Calculation of the saturation current
                                I_0_f0 = (I_sc_f) / (np.exp((V_oc_f) / (Vt_f))-1)

                       

                                #adjustment ot the photo current for irradiation and bifacial gain factor
                                I_ph_f0 = I_sc_f *BG                                             
                                I_ph_f = I_ph_f0 * (row_qabs_front / q_stc_front) 
                      
                                #newthons method to find the matching current for a given voltage
                                f_I = I_ph_f - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt_f) + np.exp((V + I * Rs_f0) / (Vt_f * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
                                f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt_f) * np.exp((V + I * Rs_f0) / Vt_f) - ((I_0_f0 * Rs_f0) / (Vt_f * a2)) * np.exp((V+ I * Rs_f0) / (Vt_f * a2)) - (Rs_f0 / Rp_f0) - 1
               
                                I2 = I - (f_I/f_dI)
                      
               
                                if I + tol_I >= I2 and I2 >= I - tol_I:         #Once I is found, the Power check starts just like in xf loop
                                    P2 = V * I2

                                    if P2 > P1:                 #Check if the new power is higher than the last
                                        P1 = P2                 #If this is true, it becomes the new reference value
                       
                                    else:
                                        P_mpp_sr = P1           #The highest calculated power gets added to P_mpp_sr
                                        
                                    if V >= V_oc_f:             # If V reached V_oc, the P-V curve is complete and the Mpp can be searched
                                        P_r = P_mpp_sr          #P_mpp_sr is the calculated Mpp for the Module for the given irradiance and and temperature
                                        yr = 0                  #Iterations get reset after successful Mpp calculation
                                        break                   #The Mpp was found, the script quits the loop
                                  
                       
                                    I = 0                       #Since there is only one P-V curve to calculate, V does not have to be reset
                                    V = V + 0.1
                                else:
                                    I = I2
                            
                        
                            P_bi = P_mpp_sf + P_mpp_sr
                            #print("Power: " + str(P_bi))
                    
                            sum_energy_b += P_bi # Sum up the energy of every row in every hour
                    
                        else:
                            P_m=0
                            P_bi=0
                        
                        P_m_hourly.append(P_m)
                        P_bi_hourly.append(P_bi)
                        
                    # Append P_bi_hourly array to arrays
                    P_m_hourly_arrays.append(P_m_hourly)
                    P_bi_hourly_arrays.append(P_bi_hourly)
          
            #
                elif simulationDict["monthlySoilingrate"] == True:

                    soilrate = simulationDict["variableSoilrate"][int(df_time_soiling['month'][x])]
                x = x+1
                    
                row_qabs_front = df_report.loc[index,key_front] * (1 - ((soilrate*(temp)/(24))))
                row_qabs_back = df_report.loc[index,key_back] * (1 - ((soilrate*(temp)/(24*8.8))))
#               row_qabs_combined = row_qabs_front + (row_qabs_back*bi_factor)
                T_Current = df.loc[index,'temperature']
                
                #print("front: " + str(row_qabs_front))
                #print("back: " + str(row_qabs_back))
                if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                    row_qabs_front = 0
                    
                if math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                    row_qabs_back = 0

                
                if row_qabs_back + row_qabs_front > 0.0:
                    
                    #Now that Rs and Rp are calculated for both sides of the module, the power calculation starts.
                    #Values are now adjusted for temperature and later also irradiation
                    
                    I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb))     
                    I_sc_r = I_sc_r0 * (1 + T_koeff_I * (T_Current - T_amb))
                    
                    V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb))
                    V_oc_r = V_oc_r0 * (1 + T_koeff_V * (T_Current - T_amb))
                    
                    #setting starting parameters for the loop
                    I = 0
                    V = 0
                    P = 0
                    P1 = 0
                    P_mpp_sf = 0
                    
                    
                    #Modified version of the Rs, Rp calculation loop. Since Rs and Rp are now given, the loop needs only a fraction of iterations
                    #to calculate the power from a given irradiance and temperature
                    #The way this works is that the algorythm searches for the Mpp of the module with the given irradiance and temperature
                    #Just like a real PV system would do
                    #It 'draws' the P-V curve and finds the Mpp which is then the power output of the module
                    for yf in range (100000):
                        
                        if row_qabs_front == 0:
                            P_m = 0
                            P_mpp_sf = 0
                            break
                        
                        #Calculation of the photo current + correction for irrandiance and temperature
                        Vt_f = (Ns * k * (T_Current + 273.15)) / q_ec

                        #Calculation of the saturation current
                        I_0_f0 = (I_sc_f) / (np.exp((V_oc_f) / (Vt_f))-1)

                        #adjustment ot the photo current for irradiation
                        I_ph_f0 = I_sc_f                                             
                        I_ph_f = I_ph_f0 * (row_qabs_front / q_stc_front) 
              
                        #newthons method to find the matching current for a given voltage
                        f_I = I_ph_f - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt_f) + np.exp((V + I * Rs_f0) / (Vt_f * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
                        f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt_f) * np.exp((V + I * Rs_f0) / Vt_f) - ((I_0_f0 * Rs_f0) / (Vt_f * a2)) * np.exp((V+ I * Rs_f0) / (Vt_f * a2)) - (Rs_f0 / Rp_f0) - 1
       
                        I2 = I - (f_I/f_dI)
              
       
                        if I + tol_I >= I2 and I2 >= I - tol_I:         #Once I is found, the Power check starts just like in xf loop
                            P2 = V * I2

                            if P2 > P1:                 #Check if the new power is higher than the last
                                P1 = P2                 #If this is true, it becomes the new reference value
               
                            else:
                                P_mpp_sf = P1           #The highest calculated power gets added to P_mpp_sf
                                
                            if V >= V_oc_f:             # If V reached V_oc, the P-V curve is complete and the Mpp can be searched
                                P_f = P_mpp_sf          #P_mpp_sf is the calculated Mpp for the Module for the given irradiance and and temperature
                                P_m = P_f
                                sum_energy_m += P_m     #The value gets added to a list for Bifacial gain calculation
                                yf = 0                  #Iterations get reset after successful Mpp calculation
                                break                   #The Mpp was found, the script quits the loop
                          
               
                            I = 0                       #Since there is only one P-V curve to calculate, V does not have to be reset
                            V = V + 0.1
                        else:
                            I = I2
                        
                            
                    ##################################
                    ###Same procedure for back side###
                    ##################################
                    I = 0
                    V = 0
                    P = 0
                    P1 = 0
                    
                    
                    
                    for yr in range (100000):
                        
                        if row_qabs_front == 0:
                            P_mpp_sr = 0
                            break
                  
                        #Calculation of the photo current + correction for irrandiance and temperature
                        Vt_f = (Ns * k * (T_Current + 273.15)) / q_ec
                        
                        #Calculating the bifacial gain factor
                        BG = row_qabs_back / row_qabs_front
                        
                       

                        
                        #Calculation of the saturation current
                        I_0_f0 = (I_sc_f) / (np.exp((V_oc_f) / (Vt_f))-1)

               

                        #adjustment ot the photo current for irradiation and bifacial gain factor
                        I_ph_f0 = I_sc_f *BG                                             
                        I_ph_f = I_ph_f0 * (row_qabs_front / q_stc_front) 
              
                        #newthons method to find the matching current for a given voltage
                        f_I = I_ph_f - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt_f) + np.exp((V + I * Rs_f0) / (Vt_f * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
                        f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt_f) * np.exp((V + I * Rs_f0) / Vt_f) - ((I_0_f0 * Rs_f0) / (Vt_f * a2)) * np.exp((V+ I * Rs_f0) / (Vt_f * a2)) - (Rs_f0 / Rp_f0) - 1
       
                        I2 = I - (f_I/f_dI)
              
       
                        if I + tol_I >= I2 and I2 >= I - tol_I:         #Once I is found, the Power check starts just like in xf loop
                            P2 = V * I2

                            if P2 > P1:                 #Check if the new power is higher than the last
                                P1 = P2                 #If this is true, it becomes the new reference value
               
                            else:
                                P_mpp_sr = P1           #The highest calculated power gets added to P_mpp_sr
                                
                            if V >= V_oc_f:             # If V reached V_oc, the P-V curve is complete and the Mpp can be searched
                                P_r = P_mpp_sr          #P_mpp_sr is the calculated Mpp for the Module for the given irradiance and and temperature
                                yr = 0                  #Iterations get reset after successful Mpp calculation
                                break                   #The Mpp was found, the script quits the loop
                          
               
                            I = 0                       #Since there is only one P-V curve to calculate, V does not have to be reset
                            V = V + 0.1
                        else:
                            I = I2
                    
                
                    P_bi = P_mpp_sf + P_mpp_sr
                    #print("Power: " + str(P_bi))
            
                    sum_energy_b += P_bi # Sum up the energy of every row in every hour
            
                else:
                    P_m=0
                    P_bi=0
                
                P_m_hourly.append(P_m)
                P_bi_hourly.append(P_bi)
                
            # Append P_bi_hourly array to arrays
            P_m_hourly_arrays.append(P_m_hourly)
            P_bi_hourly_arrays.append(P_bi_hourly)
            #
            
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
      
        
        f = plt.Figure(figsize=(12, 3))
        ax1 = f.subplots(1)
        ax1.locator_params(tight=True, nbins=6)
        f.plot(P_bi_hourly)
        ax1.set_title('Bifacial output Power hourly')
        ax1.set_xlabel('Hour')
        ax1.set_ylabel('W')
        f.savefig("P_bi_hourly" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
        #plt.show()()
        #sns wird entfernt da die Plots in der GUI ansonsten nicht richtig angezeigt werden können außerhalb der Konsole
        ##plt.show()(sns)
        
        
        ####################################################
        # Monofacial performance Calculation
        
        # Set Energy to Zero       
        sum_energy_m = 0
        sum_power_m = 0
        
        # Loop to calculate the Monofacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front_mono = "row_" + str(i) + "_qabs_front"
            P_m_hourly = []
            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
            x = 0 #counting variable in loop to get current month from df_time_soiling
            
            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                if temp == days_until_clean*24:
                    temp = 0
                else:
                    temp = temp +1

                if simulationDict["mathematicalSoilingrate"] == True:
                    soilrate = simulationDict["hourlySoilrate"]

                    for i in range(len(soilrate)):
                    
                        #SG
                        row_qabs_front = df_report.loc[index,key_front_mono] * (1 - soilrate[i])
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
            #
                elif simulationDict["monthlySoilingrate"] == True:

                    soilrate = simulationDict["variableSoilrate"][int(df_time_soiling['month'][x])]
                x = x+1
                #SG
                row_qabs_front = df_report.loc[index,key_front_mono] * (1 - ((soilrate*(temp))/(24)))
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
        
        #
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
        p_bi_df.to_csv(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
        #p_bi_df.to_csv(resultsPath + "electrical_simulation.csv")
        
        #Plot for Bifacial Power Output + Bifacial Gain
        GUI.Window.makePlotBifacialRadiance(resultsPath,Bifacial_gain)
        
        def simulate_simpleBifacial_old(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath):
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
            
            soilrate = simulationDict['fixSoilrate'] #Michailow
            days_until_clean = simulationDict['days_until_clean']
            
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
            
            FF_fr = (n_back*q_stc_rear*(simulationDict['moduley'])*(simulationDict['modulex']))/(I_sc_f0 * V_oc_f0)
                           
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
            
            #df_time_soiling = pd.DataFrame(df['corrected_timestamp'])
            #df_time_soiling['month'] = df['corrected_timestamp'].dt.strftime('%m') # Needed to choose wright soiling rate from SimulationDict
            #df_time_soiling = df_time_soiling.reset_index(drop = True)
            
            df_time_soiling = pd.DataFrame(df_report['corrected_timestamp'])
            df_time_soiling['month'] = df_report['corrected_timestamp'].dt.strftime('%m') # Needed to choose wright soiling rate from SimulationDict                                            
            df_time_soiling = df_time_soiling.reset_index(drop = True)
            
            print(df_report)
            
            
            # Loop to calculate the Monofacial Output power for every row in every hour
            for i in tqdm(range(0, simulationDict['nRows'])):
                
                key_front = "row_" + str(i) + "_qabs_front"
                key_back = "row_" + str(i) + "_qabs_back"
            
                P_bi_hourly = []
                
                temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
                x = 0 #counting variable in loop to get current month from df_time_soiling
                
                for index, row in df_report.iterrows():
                    
                    # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                    if temp == days_until_clean*24:
                        temp = 0
                    else:
                        temp = temp +1

                    if simulationDict["mathematicalSoilingrate"] == True:
                        soilrate = simulationDict["hourlySoilrate"]

                        for i in range(len(soilrate)):

                            #row_qabs_front = row[key_front]
                            #row_qabs_back = row[key_back]
                            
                            row_qabs_front = df_report.loc[index,key_front] * (1 - soilrate[i])
                            row_qabs_back = df_report.loc[index,key_back] (1 - (soilrate[i]/(8.8)))
    #                       row_qabs_combined = row_qabs_front + (row_qabs_back*bi_factor)
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
          
                #
                    elif simulationDict["monthlySoilingrate"] == True:
                        
                        soilrate = simulationDict["variableSoilrate"][int(df_time_soiling['month'][x])]
                    x = x+1
                    
                    row_qabs_front = df_report.loc[index,key_front] * (1 - ((soilrate*(temp)/(24))))
                    row_qabs_back = df_report.loc[index,key_back] * (1 - ((soilrate*(temp)/(24*8.8))))
#                   row_qabs_combined = row_qabs_front + (row_qabs_back*bi_factor)
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
            '''print("Yearly bifacial output power per module: " + str(annual_power_per_module_b) + " W/module")
            print("Yearly bifacial output energy per module: " + str(annual_power_per_module_b/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
            print ("\n")'''
            
            annual_power_per_peak_b = (sum_energy_b/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual bifacial output power per module peak power
            '''print("Yearly bifacial output power per module peak power: " + str(annual_power_per_peak_b) + " W/Wp")
            print("Yearly bifacial output energy per module peak power: " + str(annual_power_per_peak_b) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
            print ("\n")'''
            
            module_area = (simulationDict['moduley'] * simulationDict['nModsy'] * simulationDict['modulex'])
            
            annual_power_per_area_b = (annual_power_per_module_b / module_area)    #[W/m^2] annual bifacial poutput power per module area
            '''print("Yearly bifacial output power per module area: " + str(annual_power_per_area_b) + " W/m^2")
            print("Yearly bifacial output energy per module area: " + str(annual_power_per_area_b/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
            print ("\n")'''
            
            # Plot total qinc front and back for every row
          
            
            f = plt.Figure(figsize=(12, 3))
            ax1 = f.subplots(1)
            ax1.locator_params(tight=True, nbins=6)
            f.plot(P_bi_hourly)
            ax1.set_title('Bifacial output Power hourly')
            ax1.set_xlabel('Hour')
            ax1.set_ylabel('W')
            f.savefig("P_bi_hourly" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
            #plt.show()()
            #sns wird entfernt da die Plots in der GUI ansonsten nicht richtig angezeigt werden können außerhalb der Konsole
            ##plt.show()(sns)
             
            ####################################################
            # Monofacial performance Calculation
            
            # Set Energy to Zero
            sum_energy_m = 0
            sum_power_m = 0
            
            # Loop to calculate the Monofacial Output power for every row in every hour
            for i in tqdm(range(0, simulationDict['nRows'])):
                
                key_front_mono = "row_" + str(i) + "_qabs_front"
                P_m_hourly = []
                temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
                x = 0 #counting variable in loop to get current month from df_time_soiling
                
                for index, row in df_report.iterrows():
                    
                    # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                    if temp == days_until_clean*24:
                        temp = 0
                    else:
                        temp = temp +1

                    if simulationDict["mathematicalSoilingrate"] == True:
                        soilrate = simulationDict["hourlySoilrate"]

                        for i in range(len(soilrate)):

                            #SG
                            row_qabs_front = df_report.loc[index,key_front_mono] * (1 - soilrate[i])
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
                #
                    elif simulationDict["monthlySoilingrate"] == True:

                        soilrate = simulationDict["variableSoilrate"][int(df_time_soiling['month'][x])]
                    x = x+1
                    #SG
                    row_qabs_front = df_report.loc[index,key_front_mono] * (1 - ((soilrate*(temp))/(24)))
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
            
            #
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
            
            #Plot for Bifacial Power Output + Bifacial Gain
            GUI.Window.makePlotBifacialRadiance(resultsPath,Bifacial_gain)         
            return Bifacial_gain*100