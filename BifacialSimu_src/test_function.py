# -*- coding: utf-8 -*-
"""
Created on Fri May 12 18:15:38 2023

Function to iteratively test all simulation variations of BifacialSimu with testdata from Brazil and Germany
 
@author: max2k
"""

#%% Import modules

import os
import time
import glob

from datetime import datetime

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
import seaborn as sns




#from BifacialSimu_src import globals
from BifacialSimu import Controller

from multiprocessing import Process
import threading


system = 'win'
timestamp = datetime.now().strftime("%Y-%m-%d %H.%M") 
rootPath = os.getcwd().replace(os.sep, '/')
resultspath = Controller.DataHandler().setDirectories()

#%% Shutdown timer class
class ShutdownThread(threading.Thread):
    def __init__(self, time_to_abort):
        super().__init__()
        self.time_to_abort = time_to_abort
        self.stop_flag = False

    def run(self):
        i = self.time_to_abort
        while i >= 0:
            if self.stop_flag:
                print('\n!!! Shutdown cancelled !!!')
                return
            minutes, seconds = divmod(i, 60)
            print(f'\n!!!!!! System sleep in: {minutes} minutes {seconds} seconds! Enter anything to abort:')
            if (i)>60:
                time.sleep(60)
                i = i-60
            else:
                time.sleep(5)
                i = i-5
                
        #os.system("shutdown /s /t 1")
        os.system('rundll32.exe powrprof.dll,SetSuspendState 0,1,0')
    def stop(self):
        self.stop_flag = True



#%% Simulation and Module Dicts Heggelbach

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

#%% Simulation and Module Dicts Brazil
SimulationDict_Brazil_fixed = {
                'clearance_height': 0.8, #value was found missing! should be added later!
                'simulationName' : 'test_brazil_fixed',
                'weatherFile' : rootPath + '/WeatherData/Brazil/Brazil_Aug22-Jul23_grey_gravel_poa.csv',#'/WeatherData/Golden_USA/SRRLWeatherdata Nov_Dez_2.csv', #'/WeatherData/weatherfile_Hegelbach_2022.csv', #weather file in TMY format 
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

def test_function(SimulationDict, ModuleDict, test_name, startHour, endHour, electricalMode, singleAxisTrackingMode,  real_results_path):

    verzeichnis = resultspath+'/Test_result_'+test_name +'/' #rootPath + 'TEST_results/'+timestamp +'-'+test_name +'/'
    
    SimulationDict['startHour'] = startHour
    SimulationDict['endHour'] = endHour
    
    def test_thread(name, timestamp):
        resultsPath = verzeichnis + name + '/'
        
        if not os.path.exists(resultsPath):
            os.makedirs(resultsPath)            
        
        try:
            Controller.startSimulation(SimulationDict, ModuleDict, resultsPath)
            
        except Exception as err:
            with open(resultsPath + 'error_msg.txt', 'a') as file:
                file.write(str(err))   
      
     #%% make results 
    def ergebnisausgabe(name, timer_df):
         
             gesamtergebnis_df = pd.DataFrame() 
             gesamtergebnis_df_d_avg = pd.DataFrame() 
             gesamtergebnis_avg_df = pd.DataFrame() 
             
     #%% Plot functions        
             def plot_boxplots(df, column_names, save_path, title, show, fliers):
                 
                 fig, axs = plt.subplots(1, len(column_names), figsize=(len(column_names)*4, 6))

                 axs = np.array(axs).flatten()

                 for i, col in enumerate(column_names):
                     sns.boxplot(y=col, data=df, ax=axs[i], showfliers=fliers)
                     axs[i].set_title(col)
                     #formatter = FuncFormatter(lambda y, _: '{:.0%}'.format(y))
                     #axs[i].yaxis.set_major_formatter(formatter)

                 fig.suptitle(title)
             
                 plt.savefig(save_path+'/Boxplot-'+title+'.png', format='png')

                 if show ==True:
                     plt.show()
                 else:
                     plt.close()
            
             def plot_data(x, y, x_label, y_label, save_path, title, show):

                 plt.figure(figsize=(10,6))
                 plt.scatter(x, y)
                 plt.xlabel(x_label)
                 plt.ylabel(y_label)
                 plt.title(title)
                 plt.savefig(save_path+'/Scatter-'+title+'.png', format='png')

                 if show ==True:
                     plt.show()
                 else:
                     plt.close()
            
             
             def plot_lines(df, y_column, variant_column, save_path, title, show=True):
                 plt.figure(figsize=(15,9))
             
                 for variant in df[variant_column].unique():
                     temp_df = df[df[variant_column] == variant]
                     plt.plot(temp_df.index, temp_df[y_column], label=variant)
                 plt.plot(temp_df.index, temp_df['E_Wm2'], label='Real-E_m2')    
                 plt.xlabel('Date')
                 plt.ylabel(y_column)
                 plt.title(title)
                 plt.legend()
             
                 plt.savefig(save_path+'/Line-'+title+'.png', format='png')
             
                 if show:
                     plt.show()
                 else:
                     plt.close()
             
             
             def plot_data_line(df, col1, col2, x_label, y_label1, y_label2, save_path, title, show):

                 plt.figure(figsize=(10,6))
                 plt.plot(df.index, df[col1], label=y_label1)
                 plt.plot(df.index, df[col2], label=y_label2)
                 plt.xlabel(x_label)
                 plt.legend()
                 plt.title(title)
                 plt.savefig(save_path+'/Line-'+title+'.png', format='png')
             
                 if show ==True:
                     plt.show()
                 else:
                     plt.close()
     #%% read field test data and cut to timeframe        
             try:
                 real_results = pd.read_csv(real_results_path.replace(os.sep, '/'), index_col=0)
                 real_results['timestamp'] = pd.to_datetime(real_results.index)
                 real_results['datetime'] = real_results['timestamp']
                 real_results = real_results.set_index('datetime')

             except Exception as err:     
                print('Error: ',err)
             
             
             dtStart = datetime(SimulationDict['startHour'][0], SimulationDict['startHour'][1], SimulationDict['startHour'][2], SimulationDict['startHour'][3])
             dtEnd = datetime(SimulationDict['endHour'][0], SimulationDict['endHour'][1], SimulationDict['endHour'][2], SimulationDict['endHour'][3])
             
             mask = (real_results.timestamp >= dtStart) & (real_results.timestamp <= dtEnd) 
             real_results = real_results.loc[mask]

             exclude_columns = ['timestamp', 'index']
             
             for col in real_results.columns:
                 if col not in exclude_columns:
                     real_results[col] = pd.to_numeric(real_results[col], errors='coerce')
             
             
     #%% open resulst from iterating simulations and compare to field test data        
             for variante in os.listdir(verzeichnis):

                 try:
                     unterverzeichnis = verzeichnis +'/'+ variante
                     
                     radiation_simulation_data = pd.DataFrame()   
                     electrical_simulation_data = pd.DataFrame()
                     combined_data = real_results
                     
                     if not glob.glob(unterverzeichnis+'/radiation*.csv'):
                         gesamtergebnis_avg_df.loc[variante, 'Error'] = 'ERROR_Radiation'
                     else:    
                         radiation_simulation_data = pd.read_csv(glob.glob(unterverzeichnis+'/radiation*.csv')[0].replace(os.sep, '/'), index_col=0)
                         radiation_simulation_data.index = pd.to_datetime(radiation_simulation_data.index)
                         radiation_simulation_data.index = radiation_simulation_data.index.tz_localize(None)
                         combined_data = pd.merge(combined_data, radiation_simulation_data, left_index=True, right_index=True, how='inner')
                     
                     
                     if not glob.glob(unterverzeichnis+'/electrical_simulation*.csv'):
                         
                         gesamtergebnis_avg_df.loc[variante, 'Error'] = 'ERROR_Electrical'
                         
                         if glob.glob(unterverzeichnis+'/error_msg*'):
                             with open(unterverzeichnis+'/error_msg.txt', 'r') as file:
                                 electrical_simulation_data['Error']= file.read().replace('\n', ' - ')
                                 gesamtergebnis_avg_df.loc[variante, 'Error'] = file.read().replace('\n', ' - ')
                     
                     else:    
                         electrical_simulation_data = pd.read_csv(glob.glob(unterverzeichnis+'/electrical_simulation*.csv')[0].replace(os.sep, '/'), index_col=0)
                         electrical_simulation_data['timestamps'] = pd.to_datetime(electrical_simulation_data['timestamps'], format="%Y_%m_%d_%H")

                         electrical_simulation_data.set_index('timestamps', inplace=True)
                         
                         gesamtergebnis_avg_df.loc[variante, 'E_kWh/m2'] = electrical_simulation_data['P_bi '].sum() /1000
                         gesamtergebnis_avg_df.loc[variante, 'E_real_kWh/m2'] = real_results.E_Wm2.sum() /1000
                         gesamtergebnis_avg_df.loc[variante, 'delta_E_rel'] = (electrical_simulation_data['P_bi '].sum())/real_results.E_Wm2.sum() - 1
                         gesamtergebnis_avg_df.loc[variante, 'sim_runtime_s'] = timer_df.loc[variante, 'sim_runtime_s']
                         gesamtergebnis_avg_df.loc[variante, 'sim_runtime_m'] = timer_df.loc[variante, 'sim_runtime_s']/60
                     
                         combined_data = pd.merge(combined_data, electrical_simulation_data, left_index=True, right_index=True, how='inner')
                         combined_data['E_Wm2'] = combined_data['E_Wm2'].replace(0, np.nan)
                         combined_data['delta_E_rel'] = combined_data['P_bi '] / combined_data.E_Wm2 - 1
                         combined_data['delta_E_abs'] = combined_data['P_bi '] - combined_data.E_Wm2
                         
                         if 'row_0_qabs_front' in radiation_simulation_data.columns:
                             gesamtergebnis_avg_df.loc[variante, 'Q_abs_front_kWh/m2'] = radiation_simulation_data['row_0_qabs_front'].sum() /1000
                             gesamtergebnis_avg_df.loc[variante, 'Q_abs_front_real__kWh/m2'] = real_results.Q_abs_front.sum() /1000
                             gesamtergebnis_avg_df.loc[variante, 'delta_E_rad_front_rel'] = radiation_simulation_data['row_0_qabs_front'].sum()/real_results.Q_abs_front.sum() - 1
                             combined_data['row_0_qabs_front'] = combined_data['row_0_qabs_front'].replace(0, np.nan)
                             combined_data['delta_Q_front_rel'] = combined_data.row_0_qabs_front / combined_data.Q_abs_front - 1
                             combined_data['delta_Q_front_abs'] = combined_data.row_0_qabs_front - combined_data.Q_abs_front
                         
                         if 'row_0_qabs_back' in radiation_simulation_data.columns:
                             gesamtergebnis_avg_df.loc[variante, 'Q_abs_rear_kWh/m2'] = radiation_simulation_data['row_0_qabs_back'].sum() /1000
                             gesamtergebnis_avg_df.loc[variante, 'Q_abs_rear_real_kWh/m2'] = real_results.Q_abs_rear.sum() /1000
                             gesamtergebnis_avg_df.loc[variante, 'delta_E_rad_rear_rel'] = radiation_simulation_data['row_0_qabs_back'].sum()/real_results.Q_abs_rear.sum() - 1
                             combined_data['row_0_qabs_back'] = combined_data['row_0_qabs_back'].replace(0, np.nan)
                             combined_data['delta_Q_rear_rel'] = combined_data.row_0_qabs_back / combined_data.Q_abs_rear - 1   
                             combined_data['delta_Q_rear_abs'] = combined_data.row_0_qabs_back - combined_data.Q_abs_rear  
         
                         #plot_boxplots(combined_data, ['delta_E_rel', 'delta_Q_front_rel', 'delta_Q_rear_rel'], unterverzeichnis, variante, False, False)
                         plot_boxplots(combined_data, ['delta_E_abs', 'delta_Q_front_abs', 'delta_Q_rear_abs'], unterverzeichnis, variante, False, True)
                         plot_data_line(combined_data, 'P_bi ', 'E_Wm2', 'Date', 'E-sim', 'E-real', unterverzeichnis, variante, False)
                     for i in electrical_simulation_data.iterrows():
                         combined_data['Variante']=variante
                     
                     combined_data_d = combined_data.copy()
                     combined_data_d = combined_data_d.resample('D').mean()
                     
                     gesamtergebnis_df = pd.concat([gesamtergebnis_df, combined_data])         
                     gesamtergebnis_df_d_avg = pd.concat([gesamtergebnis_df_d_avg, combined_data_d])
                 except Exception as err:     
                    print(err)
             
     #%% Plot results        
             plot_lines(gesamtergebnis_df, 'P_bi ', 'Variante', verzeichnis, name+'-all_variants', True)
             
             
             plot_data(gesamtergebnis_df.index, gesamtergebnis_df['delta_E_abs'] ,  ' ', 'Deviation abs', verzeichnis, name, True)
             #plot_data(gesamtergebnis_df_d_avg.index, gesamtergebnis_df_d_avg['delta_E_abs'] ,  ' ', 'Deviation abs', verzeichnis, name+"-day", False)
             #plot_data(gesamtergebnis_df['row_0_qabs_front'], gesamtergebnis_df['delta_E_rel'] ,  'Q Abs front W/m2 ', 'rel Fehler', verzeichnis, name+"Q_abs", True)
             #plot_data(gesamtergebnis_df, 'index', 'delta_E_rel')
             
             #gesamtergebnis_df_filter = gesamtergebnis_df[gesamtergebnis_df['row_0_qabs_front'] > 100]
             #plot_boxplots(gesamtergebnis_df_filter, ['delta_E_rel', 'delta_Q_front_rel', 'delta_Q_rear_rel'], verzeichnis, name+'-filter', True)

             #plot_boxplots(gesamtergebnis_df, ['delta_E_rel', 'delta_Q_front_rel', 'delta_Q_rear_rel'], verzeichnis, name, True, False)
             #plot_boxplots(gesamtergebnis_df, ['delta_E_abs', 'delta_Q_front_abs', 'delta_Q_rear_abs'], verzeichnis, name, True, True)
             plot_boxplots(gesamtergebnis_avg_df, ['delta_E_rel', 'delta_E_rad_front_rel', 'delta_E_rad_rear_rel'], verzeichnis, name+'-avg', True, True)
             
             print(gesamtergebnis_avg_df)     
             
            
             gesamtergebnis_df.to_csv(verzeichnis + '/'+ name + '-results_all_data.csv', index=True, encoding='utf-8-sig', na_rep='0')  
             gesamtergebnis_df_d_avg.to_csv(verzeichnis + '/'+ name + '-results_all_data_d_avg.csv', index=True, encoding='utf-8-sig', na_rep='0')                 
             gesamtergebnis_avg_df.to_csv(verzeichnis + '/'+ name + '-results_sum.csv', index=True, encoding='utf-8-sig', na_rep='0')
      

#%% Test function - function to set albedo mode    
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
            
#%% Test function - Start of iterating processes    
    
    procs = []
    runtime_df = pd.DataFrame()
    
    for simMode in range(1,2):
        
        for backTrackingMode in range(1): #
            
            for albedoMode in range(2): # 
            
                for localFile in range(2):
                        
                    name = 'SM'+ str(simMode+1) + '-EL'+str(electricalMode) + '-BT'+str(backTrackingMode) + '-AL'+str(albedoMode) + '-TR'+str(singleAxisTrackingMode) + '-LF'+str(localFile)
                    
                    SimulationDict["simulationMode"] = simMode+1
                    
                    SimulationDict["localFile"] = bool(localFile)                
                    
                    SimulationDict["ElectricalMode_simple"] = electricalMode
                    
                    SimulationDict["backTrackingMode"] = bool(backTrackingMode)
                    
                    SimulationDict["singleAxisTracking"] = bool(singleAxisTrackingMode)
                    
                    define_albedo(albedoMode)

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
                        
                        start_time = time.time()
                        
                        thread = threading.Thread(target=test_thread, args=(name, timestamp, ))
                        thread.start()
                        thread.join()
                        
                        end_time = time.time() 
                        runtime_df.loc[name, 'sim_runtime_s'] = end_time-start_time

                        time.sleep(0.5)
    
    if system == 'linux':
        for proc in procs:
            proc.join()
        
    time.sleep(2)
    ergebnisausgabe(test_name, runtime_df)
    #thread_return_results = threading.Thread(target=ergebnisausgabe, args=(test_name, runtime_df, ))          
    #thread_return_results.start()
    #thread_return_results = threading.Thread(target=ergebnisausgabe, args=(test_name, runtime_df, SimulationDict, verzeichnis, real_results_path ))          
    #thread_return_results.start()

#%% start test function


print('\nSystem sleep when simulation is completed? [y/n]: ')
system_shutdown = input()
system_shutdown = True if system_shutdown.lower() == 'y' else False

heggelbach_real_path = rootPath + '/WeatherData/Heggelbach_Germany/Heggelbach_Germany_field_test_data.csv'
brazil_fixed_real_path = rootPath + '/WeatherData/Brazil/Brazil_Aug22-Jul23_grey_gravel_fixed_field_test_data.csv'

if __name__ == '__main__':
    
    try:
        """simulate 2 days"""
        #test_function(SimulationDict_Heggelbach, ModuleDict_Heggelbach, 'Heggelbach_2022_8_11', (2022, 8, 11, 5), (2022, 8, 12, 20), 0, 0, heggelbach_real_path)
        test_function(SimulationDict_Brazil_fixed, ModuleDict_Brazil, 'Brazil_fixed_2022_12_12', (2022, 12, 12, 5), (2022, 12, 13, 20), 0, 0, brazil_fixed_real_path)
        
        """simulate 2 weeks"""
        #test_function(SimulationDict_Heggelbach, ModuleDict_Heggelbach, 'Heggelbach_2022_8', (2022, 8, 1, 5), (2022, 8, 14, 20), 0, 0, heggelbach_real_path)
        #test_function(SimulationDict_Brazil_fixed, ModuleDict_Brazil, 'Brazil_fixed_2023_2', (2023, 2, 1, 5), (2023, 2, 14, 20), 0, 0, brazil_fixed_real_path)
        
        
        """simulate whole year"""
        #test_function(SimulationDict_Heggelbach, ModuleDict_Heggelbach, 'Heggelbach_2022', (2022, 1, 1, 5), (2022, 12, 31, 20), 0, 0, heggelbach_real_path)
        #SimulationDict_Heggelbach['weatherFile'] = rootPath + '/WeatherData/Heggelbach_Germany/Heggelbach_Germany_2021.csv'
        #test_function(SimulationDict_Heggelbach, ModuleDict_Heggelbach, 'Heggelbach_2021', (2021, 1, 1, 5), (2021, 12, 31, 20), 0, 0, heggelbach_real_path)
        
        #test_function(SimulationDict_Brazil_fixed, ModuleDict_Brazil, 'Brazil_fixed_2022_poa', (2022, 8, 5, 5), (2022, 12, 31, 20), 0, 0, brazil_fixed_real_path)
        
        #SimulationDict_Brazil_fixed['weatherFile'] = rootPath + '/WeatherData/Brazil/Brazil_Aug22-Jul23_grey_gravel_nrel.csv'
        #test_function(SimulationDict_Brazil_fixed, ModuleDict_Brazil, 'Brazil_fixed_2022_nrel', (2022, 8, 5, 5), (2022, 12, 31, 20), 0, 0, brazil_fixed_real_path)
        
        
        
        """simulate across year boundaries"""
        #SimulationDict_Brazil_fixed['weatherFile'] = rootPath + '/WeatherData/Brazil/Brazil_Aug21-Jul22_grey_gravel.csv'
        #test_function(SimulationDict_Brazil_fixed, ModuleDict_Brazil, 'Brazil_fixed_2021', (2021, 8, 1, 0), (2022, 5, 8, 23), 0, 0, heggelbach_real_path)
        
        #test_function(SimulationDict_Brazil_tracked , ModuleDict_Brazil , 'Brazil_tracked_2022', (2022, 1, 1, 1), (2022, 12, 31, 22), 0, 1)
       
    except Exception as err:     
       print("Error:",err)
 
 
    """Initiate system sleep when simulation is complete""" 
    if system_shutdown == True:    
        
        shutdown_thread = ShutdownThread(300)
        shutdown_thread.start()
    
        try:
            user_input = input()
            if shutdown_thread.is_alive():
                shutdown_thread.stop()
                print("sleep aborted.")
            else:
                print("Too late, sleep in progress...")
        except Exception as e:
            print("Error:", e)

