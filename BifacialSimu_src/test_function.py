# -*- coding: utf-8 -*-
"""
Created on Fri May 12 18:15:38 2023

Function to iteratively test all simulation variations of BifacialSimu with testdata from Brazil and Germany
 
@author: max2k
"""

#%% Import modules

import os
import time

import pandas as pd

from datetime import datetime
#import timeit

import glob

#from BifacialSimu_src import globals
from BifacialSimu import Controller

from multiprocessing import Process
import threading




#%% Simulation and Module Dicts
timestamp = datetime.now().strftime("%Y-%m-%d %H.%M") 
rootPath = os.getcwd().replace(os.sep, '/')
resultspath = Controller.DataHandler().setDirectories()

# simulation parameters and variables
SimulationDict_Heggelbach = {
                'clearance_height': 6, #value was found missing! should be added later!
                'simulationName' : 'test_heggelbach',
                'weatherFile' : rootPath + '/WeatherData/Heggelbach_Germany/Heggelbach_Germany_2022.csv',#'/WeatherData/Golden_USA/SRRLWeatherdata Nov_Dez_2.csv', #'/WeatherData/weatherfile_Hegelbach_2022.csv', #weather file in TMY format 
                'spectralReflectancefile' : rootPath + '/ReflectivityData/interpolated_reflectivity.csv',
                'cumulativeSky' : False, # Mode for RayTracing: CumulativeSky or hourly
                'utcOffset': 2,#2,
                'tilt' : 20, #tilt of the PV surface [deg]
                'singleAxisTracking' : False, # singleAxisTracking or not
                'limitAngle' : 60, # limit Angle for singleAxisTracking
                'hub_height' : 6.8, # Height of the rotation axis of the tracker [m]
                'azimuth' : 232.5, #azimuth of the PV surface [deg] 90°: East, 135° : South-East, 180°:South
                'nModsx' : 6, #number of modules in x-axis
                'nModsy' : 2, #number of modules in y-axis
                'nRows' : 5, #number of rows
                'sensorsy' : 5, #number of sensors
                'moduley' : 1.675,#1.675 ,#length of modules in y-axis
                'modulex' : 1.001,#1.001, #length of modules in x-axis  
                'albedo' : 0.15, # Measured Albedo average value, if hourly isn't available
                'frontReflect' : 0.03, #front surface reflectivity of PV rows
                'BackReflect' : 0.05, #back surface reflectivity of PV rows
                'longitude' : 9.136, 
                'latitude' : 47.853,
                'gcr' : 0.38,#0.35, #ground coverage ratio (module area / land use)
                'module_type' : 'SW-Bisun-270-duo', #Name of Module                    
                }

ModuleDict_Heggelbach = {
            'bi_factor': 0.65, #bifacial factor
            'n_front': 0.161, #module efficiency
            'I_sc_f': 9.28, #Short-circuit current measured for front side illumination of the module at STC [A]
            'I_sc_r': 0,#6.4, #Short-circuit current measured for rear side illumination of the module at STC [A]
            'V_oc_f': 39, #Open-circuit voltage measured for front side illumination of module at STC [V]
            'V_oc_r': 0,#38.4, #Open-circuit voltage measured for rear side illumination of module at STC [V]
            'V_mpp_f': 31.3, #Front Maximum Power Point Voltage [V]
            'V_mpp_r': 0,#31.54, #Rear Maximum Power Point Voltage [V]
            'I_mpp_f': 8.68, #Front Maximum Power Point Current [A]
            'I_mpp_r': 0,#5.98, #Rear Maximum Power Point Current [A]
            'P_mpp': 270, # Power at maximum power Point [W]
            'T_koeff_P': -0.0043, #Temperature Coeffizient [1/°C]
            'T_amb':20, #Ambient Temperature for measuring the Temperature Coeffizient [°C]
            'T_NOCT': 48, #NOCT Temperature for module temp estimation
            'T_koeff_I': 0.00044, #Temperaturkoeffizient for I_sc [1/°C] #SG
            'T_koeff_V': -0.0031, #Temperaturkoeffizient for U_oc [1/°C] #SG
            'zeta': 0.06 #Bestrahlungskoeffizient für Leerlaufspannung [-]
            }


SimulationDict_Brazil_fixed = {
                'clearance_height': 0.8, #value was found missing! should be added later!
                'simulationName' : 'test_brazil_fixed',
                'weatherFile' : rootPath + '/WeatherData/Brazil/Brazil_2021_grey_gravel.csv',#'/WeatherData/Golden_USA/SRRLWeatherdata Nov_Dez_2.csv', #'/WeatherData/weatherfile_Hegelbach_2022.csv', #weather file in TMY format 
                'spectralReflectancefile' : rootPath + '/ReflectivityData/interpolated_reflectivity.csv',
                'cumulativeSky' : False, # Mode for RayTracing: CumulativeSky or hourly
                'utcOffset': -3,
                'tilt' : 30, #tilt of the PV surface [deg]
                'limitAngle' : 0, # limit Angle for singleAxisTracking
                'hub_height' : 1.42, # Height of the rotation axis of the tracker [m]
                'azimuth' : 30, #azimuth of the PV surface [deg] 90°: East, 135° : South-East, 180°:South
                'nModsx' : 6, #number of modules in x-axis
                'nModsy' : 2, #number of modules in y-axis
                'nRows' : 3, #number of rows
                'sensorsy' : 5, #number of sensors
                'moduley' : 2.384,#1.675 ,#length of modules in y-axis
                'modulex' : 1.303,#1.001, #length of modules in x-axis  
                'albedo' : 0.145, # Measured Albedo average value, if hourly isn't available
                'frontReflect' : 0.03, #front surface reflectivity of PV rows
                'BackReflect' : 0.05, #back surface reflectivity of PV rows
                'longitude' : -48.440694, 
                'latitude' : -27.430972,
                'gcr' : 0.5, #ground coverage ratio (module area / land use)
                'module_type' : 'Canadian Solar CS7N-MB', #Name of Module                    
                }

SimulationDict_Brazil_tracked = {
                'clearance_height': 0.6, #value was found missing! should be added later!
                'simulationName' : 'test_brazil_tracked',
                'weatherFile' : rootPath + '/WeatherData/Brazil/Brazil_2021_grey_gravel.csv',#'/WeatherData/Golden_USA/SRRLWeatherdata Nov_Dez_2.csv', #'/WeatherData/weatherfile_Hegelbach_2022.csv', #weather file in TMY format 
                'spectralReflectancefile' : rootPath + '/ReflectivityData/interpolated_reflectivity.csv',
                'cumulativeSky' : False, # Mode for RayTracing: CumulativeSky or hourly
                'utcOffset': -3,
                'tilt' : 20, #tilt of the PV surface [deg]
                'limitAngle' : 58, # limit Angle for singleAxisTracking
                'hub_height' : 1.42, # Height of the rotation axis of the tracker [m]
                'azimuth' : 90, #azimuth of the PV surface [deg] 90°: East, 135° : South-East, 180°:South
                'nModsx' : 7, #number of modules in x-axis
                'nModsy' : 1, #number of modules in y-axis
                'nRows' : 5, #number of rows
                'sensorsy' : 5, #number of sensors
                'moduley' : 2.384,#1.675 ,#length of modules in y-axis
                'modulex' : 1.303,#1.001, #length of modules in x-axis  
                'albedo' : 0.25, # Measured Albedo average value, if hourly isn't available
                'frontReflect' : 0.03, #front surface reflectivity of PV rows
                'BackReflect' : 0.05, #back surface reflectivity of PV rows
                'longitude' : -48.440694, 
                'latitude' : -27.430972,
                'gcr' : 0.45, #ground coverage ratio (module area / land use)
                'module_type' : 'Canadian Solar CS7N-MB', #Name of Module                    
                }


ModuleDict_Brazil = {
            'bi_factor': 0.7, #bifacial factor
            'n_front': 0.206, #module efficiency
            'I_sc_f': 18.35, #Short-circuit current measured for front side illumination of the module at STC [A]
            'I_sc_r': 0, #Short-circuit current measured for rear side illumination of the module at STC [A]
            'V_oc_f': 44.8, #Open-circuit voltage measured for front side illumination of module at STC [V]
            'V_oc_r': 0, #Open-circuit voltage measured for rear side illumination of module at STC [V]
            'V_mpp_f': 37.7, #Front Maximum Power Point Voltage [V]
            'V_mpp_r': 0, #Rear Maximum Power Point Voltage [V]
            'I_mpp_f': 17.11, #Front Maximum Power Point Current [A]
            'I_mpp_r': 0, #Rear Maximum Power Point Current [A]
            'P_mpp': 645, # Power at maximum power Point [W]
            'T_koeff_P': -0.0034, #Temperature Coeffizient [1/°C]
            'T_amb':20, #Ambient Temperature for measuring the Temperature Coeffizient [°C]
            'T_NOCT': 41, #NOCT Temperature for module temp estimation
            'T_koeff_I': 0.0005, #Temperaturkoeffizient for I_sc [1/°C] #SG
            'T_koeff_V': -0.0026, #Temperaturkoeffizient for U_oc [1/°C] #SG
            'zeta': 0.06 #Bestrahlungskoeffizient für Leerlaufspannung [-]
            }



#%% Test function

def test_function(SimulationDict, ModuleDict, test_name, startHour, endHour, electricalMode, singleAxisTrackingMode):

    verzeichnis = resultspath+'/Test_result_'+test_name +'/' #rootPath + 'TEST_results/'+timestamp +'-'+test_name +'/'

    def test_thread(name, timestamp):
        resultsPath = verzeichnis + name + '/'
        
        if not os.path.exists(resultsPath):
            os.makedirs(resultsPath)            
        
        try:
            
            Controller.startSimulation(SimulationDict, ModuleDict, resultsPath)
            
        except Exception as err:
            with open(resultsPath + 'error_msg.txt', 'a') as file:
                file.write(str(err))
 
            
    def ergebnisausgabe():
    
        gesamtergebnis_el_df = pd.DataFrame() 
        gesamtergebnis_rad_df = pd.DataFrame()
        
        gesamtergebnis_sum_el_df = pd.DataFrame() 
    
        for variante in os.listdir(verzeichnis):
            
            print(variante)
            
            unterverzeichnis = verzeichnis +'/'+ variante
            
            radiation_simulation_data = pd.DataFrame()   
            electrical_simulation_data = pd.DataFrame()   
            
            if not glob.glob(unterverzeichnis+'/radiation*.csv'):
                radiation_simulation_data.loc[variante, 'Error']='ERROR'
            else:    
                radiation_simulation_data = pd.read_csv(glob.glob(unterverzeichnis+'/radiation*.csv')[0].replace(os.sep, '/'), index_col=0)
            
            for i in radiation_simulation_data.iterrows():
                radiation_simulation_data['Variante']=variante
            
            gesamtergebnis_rad_df = pd.concat([gesamtergebnis_rad_df, radiation_simulation_data]) 
            
            
            if not glob.glob(unterverzeichnis+'/electrical_simulation*.csv'):
                electrical_simulation_data.loc[variante, 'Error']='ERROR'
                if glob.glob(unterverzeichnis+'/error_msg*'):
                    with open(unterverzeichnis+'/error_msg.txt', 'r') as file:
                        electrical_simulation_data['Error_Message']= file.read().replace('\n', ' - ')
            else:    
                electrical_simulation_data = pd.read_csv(glob.glob(unterverzeichnis+'/electrical_simulation*.csv')[0].replace(os.sep, '/'), index_col=0)
                
                gesamtergebnis_sum_el_df.loc[variante, 'E_kWh/m2'] = electrical_simulation_data['P_bi '].sum() /1000
            
            for i in electrical_simulation_data.iterrows():
                electrical_simulation_data['Variante']=variante
                   
            
            gesamtergebnis_el_df = pd.concat([gesamtergebnis_el_df, electrical_simulation_data])         
            
    
        gesamtergebnis_rad_df.to_csv(verzeichnis+'/Gesamtergebnis-Radiation.csv', index=True, encoding='utf-8-sig', na_rep='0')              
        gesamtergebnis_el_df.to_csv(verzeichnis+'/Gesamtergebnis-Elektrisch.csv', index=True, encoding='utf-8-sig', na_rep='0')              
        gesamtergebnis_sum_el_df.to_csv(verzeichnis+'/AVG-Elektrisch.csv', index=True, encoding='utf-8-sig', na_rep='0')   
        
    
    def define_albedo(albedoMode):
        if albedoMode == 0:
            SimulationDict["fixAlbedo"]=True    
            SimulationDict["hourlyMeasuredAlbedo"]=False
            SimulationDict["hourlySpectralAlbedo"]=False
            SimulationDict["variableAlbedo"]=False
        if albedoMode == 1:
            SimulationDict["fixAlbedo"]=False    
            SimulationDict["hourlyMeasuredAlbedo"]=True
            SimulationDict["hourlySpectralAlbedo"]=False
            SimulationDict["variableAlbedo"]=False
        if albedoMode == 2:
            SimulationDict["fixAlbedo"]=False    
            SimulationDict["hourlyMeasuredAlbedo"]=False
            SimulationDict["hourlySpectralAlbedo"]=True
            SimulationDict["variableAlbedo"]=False
        if albedoMode == 3:
            SimulationDict["fixAlbedo"]=False    
            SimulationDict["hourlyMeasuredAlbedo"]=False
            SimulationDict["hourlySpectralAlbedo"]=False
            SimulationDict["variableAlbedo"]=True  
            
#%% Start of iterating processes    
    
    procs = []
    
    for simMode in range(2):
        
        for backTrackingMode in range(2): #
            
            for albedoMode in range(2): # 
            
                for localFile in range(2):
                        
                    name = 'SM'+ str(simMode+1) + '-EL'+str(electricalMode) + '-BT'+str(backTrackingMode) + '-AL'+str(albedoMode) + '-TR'+str(singleAxisTrackingMode) + '-LF'+str(localFile)
                    
                    SimulationDict["simulationMode"] = simMode+1
                    
                    SimulationDict["localFile"] = bool(localFile)                
                    
                    SimulationDict["ElectricalMode_simple"] = electricalMode
                    
                    SimulationDict["backTrackingMode"] = bool(backTrackingMode)
                    
                    SimulationDict["singleAxisTracking"] = bool(singleAxisTrackingMode)
                    
                    define_albedo(albedoMode)
                    
                    if localFile == 0:
                        startHour_lst = list(startHour)
                        startHour_lst[0] = 2001
                        SimulationDict["startHour"] = tuple(startHour_lst)
                        
                        endHour_lst = list(endHour)
                        endHour_lst[0] = 2001
                        SimulationDict["endHour"] = tuple(endHour_lst)
                    else:
                        SimulationDict["startHour"] = startHour
                        SimulationDict["endHour"] = endHour   
                   
                    if localFile == 0 and albedoMode == 1:
                        continue

                    if system == 'linux':
                        if simMode == 2 or simMode == 4:
                            proc = Process(target=test_thread, args=(name, timestamp, ))
                            proc.start()
                            procs.append(proc)
                        else:
                            proc = Process(target=test_thread, args=(name, timestamp, ))
                            proc.start()
                            proc.join()
                    else:
                        
                        thread = threading.Thread(target=test_thread, args=(name, timestamp, ))
                        thread.start()
                        thread.join()
                        time.sleep(0.5)
    
    if system == 'linux':
        for proc in procs:
            proc.join()
        
    time.sleep(2)
    ergebnisausgabe()              
    

#%% start test function
system = 'win'
    
if __name__ == '__main__':
    
    test_function(SimulationDict_Heggelbach, ModuleDict_Heggelbach, 'Heggelbach_2022', (2022, 7, 1, 4), (2022, 12, 31, 22), 0, 0)
    
    #test_function(SimulationDict_Heggelbach, ModuleDict_Heggelbach, 'Heggelbach_2022', (2022, 1, 1, 0), (2022, 12, 31, 23), 0, 0)
    #SimulationDict_Heggelbach['weatherFile'] = rootPath + '/WeatherData/Heggelbach_Germany/Heggelbach_Germany_2021.csv'
    #test_function(SimulationDict_Heggelbach, ModuleDict_Heggelbach, 'Heggelbach_2021', (2021, 1, 1, 0), (2021, 12, 31, 23), 0, 0)
    
    test_function(SimulationDict_Brazil_fixed, ModuleDict_Brazil, 'Brazil_fixed_2021', (2021, 8, 1, 4), (2021, 12, 31, 22), 0, 0)
    
    #SimulationDict_Brazil_fixed['weatherFile'] = rootPath + '/WeatherData/Brazil/Brazil_Aug21-Jul22_grey_gravel.csv'
    #test_function(SimulationDict_Brazil_fixed, ModuleDict_Brazil, 'Brazil_fixed_2021', (2021, 8, 1, 0), (2022, 5, 8, 23), 0, 0)
    
    #test_function(SimulationDict_Brazil_tracked , ModuleDict_Brazil , 'Brazil_tracked_2022', (2022, 1, 1, 1), (2022, 12, 31, 22), 0, 1)
    print('!!!System shutdown!!!')
    time.sleep(30)
    print('!!!System shutdown!!!')
    time.sleep(30)
    os.system("shutdown /s /t 1")


