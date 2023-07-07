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
import matplotlib


#from BifacialSimu_src import globals
from BifacialSimu import Controller

from multiprocessing import Process
import threading



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
        for m in range (self.time_to_abort):
            for s in range(60):
                if self.stop_flag:
                    print('\n!!! Shutdown cancelled !!!')
                    return
                s = 60-s
                minutes  = self.time_to_abort - m
                print(f'\rSystem sleep in: {minutes} minutes {s} seconds! Enter anything to abort: ')
                time.sleep(1)
                #print('\rEnter anything to abort!')
                #time.sleep(0.5)
       
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
                'backTracking' : False,
                'utcOffset': 2,
                'tilt' : 20, #tilt of the PV surface [deg]
                'singleAxisTracking' : False, # singleAxisTracking or not
                'limitAngle' : 30, # limit Angle for singleAxisTracking
                'hub_height' : 6.8, # Height of the rotation axis of the tracker [m]
                'azimuth' : 232.5, #azimuth of the PV surface [deg] 90°: East, 135° : South-East, 180°:South
                'nModsx' : 10, #number of modules in x-axis
                'nModsy' : 2, #number of modules in y-axis
                'nRows' : 10, #number of rows
                'sensorsy' : 5, #number of sensors
                'moduley' : 1.675,#length of modules in y-axis
                'modulex' : 1.001,#length of modules in x-axis  
                'albedo' : 0.252, # Measured Albedo average value, if hourly isn't available
                'frontReflect' : 0.03, #front surface reflectivity of PV rows
                'BackReflect' : 0.05, #back surface reflectivity of PV rows
                'longitude' : 9.136, 
                'latitude' : 47.853,
                'gcr' : 0.38, #ground coverage ratio (module area / land use)
                'module_type' : 'SW-Bisun-270-duo', #Name of Module                    
                }

ModuleDict_Heggelbach = {
                'bi_factor': 0.65, #bifacial factor
                'n_front': 0.161, #module efficiency
                'I_sc_f': 9.28, #Short-circuit current measured for front side illumination of the module at STC [A]
                'I_sc_r': 0, #Short-circuit current measured for rear side illumination of the module at STC [A]
                'V_oc_f': 39, #Open-circuit voltage measured for front side illumination of module at STC [V]
                'V_oc_r': 0, #Open-circuit voltage measured for rear side illumination of module at STC [V]
                'V_mpp_f': 31.3, #Front Maximum Power Point Voltage [V]
                'V_mpp_r': 0,#Rear Maximum Power Point Voltage [V]
                'I_mpp_f': 8.68, #Front Maximum Power Point Current [A]
                'I_mpp_r': 0, #Rear Maximum Power Point Current [A]
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
                'backTracking' : False,
                'utcOffset': -3,
                'tilt' : 30, #tilt of the PV surface [deg]
                'limitAngle' : 0, # limit Angle for singleAxisTracking
                'hub_height' : 1.42, # Height of the rotation axis of the tracker [m]
                'azimuth' : 30, #azimuth of the PV surface [deg] 90°: East, 135° : South-East, 180°:South
                'nModsx' : 6, #number of modules in x-axis
                'nModsy' : 2, #number of modules in y-axis
                'nRows' : 3, #number of rows
                'sensorsy' : 5, #number of sensors
                'moduley' : 2.384,#length of modules in y-axis
                'modulex' : 1.303, #length of modules in x-axis  
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
                'weatherFile' : rootPath + '/WeatherData/Brazil/Brazil_March23_white_gravel_poa.csv',#'/WeatherData/Golden_USA/SRRLWeatherdata Nov_Dez_2.csv', #'/WeatherData/weatherfile_Hegelbach_2022.csv', #weather file in TMY format 
                'spectralReflectancefile' : rootPath + '/ReflectivityData/interpolated_reflectivity.csv',
                'cumulativeSky' : False, # Mode for RayTracing: CumulativeSky or hourly
                'backTracking' : False,
                'utcOffset': -3,
                'tilt' : 20, #tilt of the PV surface [deg]
                'limitAngle' : 58, # limit Angle for singleAxisTracking
                'hub_height' : 1.42, # Height of the rotation axis of the tracker [m]
                'azimuth' : 120, #azimuth of the PV surface [deg] 90°: East, 135° : South-East, 180°:South
                'nModsx' : 26, #number of modules in x-axis
                'nModsy' : 1, #number of modules in y-axis
                'nRows' : 5, #number of rows
                'sensorsy' : 5, #number of sensors
                'moduley' : 2.384,#length of modules in y-axis
                'modulex' : 1.303, #length of modules in x-axis  
                'albedo' : 0.45, # Measured Albedo average value, if hourly isn't available
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
def plot_lines(df, y_column, label, save_path, title, show=True):
    
    try:
        plt.figure(figsize=(12,6),dpi=300)
            
    
        for variant in df['Variante'].unique():
            #temp_df = df[df['Variante'] == variant]
            #plt.plot(temp_df.index, temp_df[y_column], label=variant)
            temp_df = df[df['Variante'] == variant].sort_index()
            plt.plot(temp_df.index, temp_df[y_column], label=variant)
        
        
        avg_line = df.groupby(df.index)[y_column].mean()  # Durchschnittskurve für alle Varianten
        plt.plot(avg_line.index, avg_line, label='Simulation Average', linestyle='--', linewidth=2, color='darkred')   
        
        plt.plot(temp_df.index, temp_df['E_Wm2'], label='Field test data', linestyle='--', linewidth=2, color='black')    
    
        plt.ylabel(label, fontsize=6)
        plt.title(title, fontsize=8)
        plt.legend(fontsize=6)
        plt.xticks(fontsize=6)
        plt.yticks(fontsize=6) 
    
        plt.savefig(save_path+'/Line-'+title+'.png', format='png')
    
        if show:
            plt.show()
        else:
            plt.close()
    except Exception as err:
        print('Plot Error:',err)        



def plot_boxplots(df, y_columns, y_label, save_path, title, show=True, relative=False):
    
    # Definition of formatter function
    def to_percent(y, position):
        s = "{:.1f}".format(100 * y)
        if matplotlib.rcParams['text.usetex'] is True:
            return s + r'$\%$'
        else:
            return s + '%'
    
    # Formatter
    formatter = FuncFormatter(to_percent)
    
    try:
        n = len(y_columns)
        
        fig, axs = plt.subplots(n, 1, figsize=(15,12*n), dpi=300)
    
        for i, y_column in enumerate(y_columns):
            sns.boxplot(x='Variante', y=y_column, data=df, palette='Set3', ax=axs[i])
            mean = df[y_column].mean()
            axs[i].axhline(mean, color='r', linestyle='--')
            axs[i].set_ylabel(y_label, fontsize=6)
            axs[i].set_xlabel('', fontsize=2)
            axs[i].set_title(f"{title} - {y_column}", fontsize=8)
            
            axs[i].tick_params(axis='x', labelsize=6)
            axs[i].tick_params(axis='y', labelsize=6)
            
            # Set y-axis to be in percentage format if relative is True
            if relative:
                axs[i].yaxis.set_major_formatter(formatter)
    
        plt.tight_layout()
        plt.savefig(save_path + '/Boxplot-' + title.replace('/', '_') + '.png', format='png')
    
        if show:
            plt.show()
        else:
            plt.close()
    except Exception as err:
        print('Plot Error:', err)

def plot_bars(df, y_columns, y_label, save_path, title, show=True, relative=False):
    
    # Definition of formatter function
    def to_percent(y, position):
        s = "{:.1f}".format(100 * y)
        if matplotlib.rcParams['text.usetex'] is True:
            return s + r'$\%$'
        else:
            return s + '%'
    
    # Formatter
    formatter = FuncFormatter(to_percent)
    
    try:
        n = len(y_columns)
        
        fig, axs = plt.subplots(n, 1, figsize=(15,12*n), dpi=300)
    
        for i, y_column in enumerate(y_columns):
            sns.barplot(x='Variante', y=y_column, data=df, palette='Set3', ax=axs[i])
            mean = df[y_column].mean()
            axs[i].axhline(mean, color='r', linestyle='--')
            axs[i].set_ylabel(y_label, fontsize=6)
            axs[i].set_xlabel('', fontsize=2)
            axs[i].set_title(f"{title} - {y_column}", fontsize=8)
            
            axs[i].tick_params(axis='x', labelsize=6)
            axs[i].tick_params(axis='y', labelsize=6)
            
            # Set y-axis to be in percentage format if relative is True
            if relative:
                axs[i].yaxis.set_major_formatter(formatter)
    
        plt.tight_layout()
        plt.savefig(save_path + '/Barchart-' + title.replace('/', '_') + '.png', format='png')
    
        if show:
            plt.show()
        else:
            plt.close()
    except Exception as err:
        print('Plot Error:', err)
     
def test_function(SimulationDict, ModuleDict, test_name, startHour, endHour, singleAxisTrackingMode,  real_results_path):

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
            
             
             def plot_data_line(df, col1, col2, x_label, y_label1, y_label2, save_path, title, show):

                 plt.figure(figsize=(10,6),dpi=300)
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
             try:    
                 for variante in os.listdir(verzeichnis):
    
                     
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
                             try: 
                                 electrical_simulation_data['timestamps'] = pd.to_datetime(electrical_simulation_data['timestamps'], format="%Y_%m_%d_%H")
                             except:
                                 electrical_simulation_data['timestamps'] = pd.to_datetime(electrical_simulation_data['timestamps'])
                                 electrical_simulation_data['timestamps'] = electrical_simulation_data['timestamps'].dt.tz_localize(None)
                             
                             electrical_simulation_data.set_index('timestamps', inplace=True)
                             
                             gesamtergebnis_avg_df.loc[variante, 'E_kWh/m2'] = electrical_simulation_data['P_bi '].sum() /1000
                             gesamtergebnis_avg_df.loc[variante, 'E_real_kWh/m2'] = real_results.E_Wm2.sum() /1000
                             gesamtergebnis_avg_df.loc[variante, 'delta_E_rel'] = (electrical_simulation_data['P_bi '].sum())/real_results.E_Wm2.sum() - 1
                             gesamtergebnis_avg_df.loc[variante, 'sim_runtime_s'] = timer_df.loc[variante, 'sim_runtime_s']
                             gesamtergebnis_avg_df.loc[variante, 'sim_runtime_m'] = timer_df.loc[variante, 'sim_runtime_s']/60
                             gesamtergebnis_avg_df.loc[variante, 'Variante'] =  variante
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
             
                             plot_data_line(combined_data, 'P_bi ', 'E_Wm2', 'Date', 'E-sim', 'E-real', unterverzeichnis, variante, False)
                         for i in electrical_simulation_data.iterrows():
                             combined_data['Variante']=variante
                         
                         combined_data_d = combined_data.copy()
                         combined_data_d_numeric = combined_data_d.select_dtypes(include=[np.number])  # Auswahl der numerischen Spalten
                         combined_data_d_sum = combined_data_d_numeric.resample('D').sum()  # Anwendung der sum()-Funktion auf die numerischen Spalten
                            
                         combined_data_d_text = combined_data_d.select_dtypes(include=[object])  # Auswahl der Textspalte
                         combined_data_d_text = combined_data_d_text.resample('D').first()   
                         combined_data_d = pd.concat([combined_data_d_text, combined_data_d_sum], axis=1)  # Zusammenführen der Textspalte und der summierten Spalten
                            
                                                 
                         gesamtergebnis_df = pd.concat([gesamtergebnis_df, combined_data])         
                         gesamtergebnis_df_d_avg = pd.concat([gesamtergebnis_df_d_avg, combined_data_d])
                         
                 
         #%% Plot results        
                 #plot_lines(gesamtergebnis_df, 'P_bi ', r'Bifacial Power Output [$\mathrm{\frac{Wh}{m^2}}$]',  verzeichnis, name+'-all_variants', False)
                 #plot_boxplots(gesamtergebnis_df, ['delta_E_abs', 'delta_Q_front_abs', 'delta_Q_rear_abs' ], r'Energy per m$^2$  [$\mathrm{\frac{Wh}{m^2*d}}$]', verzeichnis, name+'-avg', False)
             except Exception as err:     
                 print(err)
                 
             print(gesamtergebnis_avg_df)     
             
            
             gesamtergebnis_df.to_csv(verzeichnis + '/'+ name + '-results_all_data.csv', index=True, encoding='utf-8-sig', na_rep='0')  
             gesamtergebnis_df_d_avg.to_csv(verzeichnis + '/'+ name + '-results_all_data_d_avg.csv', index=True, encoding='utf-8-sig', na_rep='0')                 
             gesamtergebnis_avg_df.to_csv(verzeichnis + '/'+ name + '-results_sum.csv', index=True, encoding='utf-8-sig', na_rep='0')
             return gesamtergebnis_df, gesamtergebnis_df_d_avg, gesamtergebnis_avg_df

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
    
    runtime_df = pd.DataFrame()
    
    for simMode in range(3):       
        if singleAxisTrackingMode ==1 and SimulationDict['cumulativeSky'] == True:
            continue
        
        for backTrackingMode in range(1): #
            if backTrackingMode ==1 and singleAxisTrackingMode !=1:
                continue
            
            for albedoMode in range(1): # 
                if albedoMode ==1 and simMode in {0, 2, 4}:
                    continue
                
                for localFile in range(1,2):
                    
                    for electricalMode in range(1):
                        
                        for cumSky in range(2):
                            if cumSky ==1 and simMode not in {2, 5}:
                                continue
                            
                            name = 'SM'+ str(simMode+1) + '-EL'+str(electricalMode) + '-BT'+str(backTrackingMode) + '-AL'+str(albedoMode) + '-TR'+str(singleAxisTrackingMode) + '-LF'+str(localFile)
                            if cumSky ==1:
                                name += '-CS'+str(cumSky)
                            
                            SimulationDict["simulationMode"] = simMode+1
                            SimulationDict["localFile"] = bool(localFile)                     
                            SimulationDict["ElectricalMode_simple"] = electricalMode                    
                            SimulationDict["backTrackingMode"] = bool(backTrackingMode)                   
                            SimulationDict["singleAxisTracking"] = bool(singleAxisTrackingMode)
                            SimulationDict["cumulativeSky"] = bool(cumSky)  
                            define_albedo(albedoMode)
                            
                            if electricalMode == 1:
                                ModuleDict['I_sc_r'] = ModuleDict['I_sc_f'] * ModuleDict['bi_factor']
                                ModuleDict['V_oc_r'] = ModuleDict['V_oc_f'] * ModuleDict['bi_factor']
                                ModuleDict['V_mpp_r'] = ModuleDict['V_mpp_f'] * ModuleDict['bi_factor']
                                ModuleDict['I_mpp_r'] = ModuleDict['I_mpp_f'] * ModuleDict['bi_factor']
                                
                            else:
                                ModuleDict['I_sc_r'] = 0
                                ModuleDict['V_oc_r'] = 0
                                ModuleDict['V_mpp_r'] = 0
                                ModuleDict['I_mpp_r'] = 0
                            
                            start_time = time.time()
    
                            try:
                               test_thread(name, timestamp)
                            except Exception as err:
                               print(err)
                               
                            end_time = time.time() 
                            runtime_df.loc[name, 'sim_runtime_s'] = end_time-start_time
    
                            time.sleep(0.1) 
                                  
        
    results_h, results_d, results_avg = ergebnisausgabe(test_name, runtime_df)
    
    return results_h, results_d, results_avg

#%% start test function


print('\nSystem sleep when simulation is completed? [y]: ')
system_shutdown = input()
if system_shutdown.lower() == 'y':
    system_shutdown = True 
    print('\nSystem is going to sleep after test run!\n')
else:
    system_shutdown = False


heggelbach_real_path = rootPath + '/WeatherData/Heggelbach_Germany/Heggelbach_Germany_field_test_data.csv'
brazil_tracked_real_path = rootPath + '/WeatherData/Brazil/Brazil_Nov22-March23_white_gravel_tracked_field_test_data.csv'


if __name__ == '__main__':
    
    try:
        """simulate 2 days"""
        
        heggelbach_h_22, heggelbach_d_22, heggelbach_avg_22 = test_function(SimulationDict_Heggelbach, ModuleDict_Heggelbach, 'Heggelbach 2022', (2022, 7, 1, 8), (2022, 7, 7, 21), 0, heggelbach_real_path)
        
        """simulate year"""
        #heggelbach_h_22, heggelbach_d_22, heggelbach_avg_22 = test_function(SimulationDict_Heggelbach, ModuleDict_Heggelbach, 'Heggelbach 2022', (2022, 1, 1, 1), (2022, 12, 28, 0), 0, heggelbach_real_path)

        #brazil_fixed_h, brazil_fixed_d = test_function(SimulationDict_Brazil_fixed, ModuleDict_Brazil, 'Brazil-fixed 2023 POA_conversion', (2023, 1, 1, 11), (2023, 1, 1, 13), 0, brazil_fixed_real_path)
        #brazil_tracked_h, brazil_tracked_d, brazil_tracked_avg = test_function(SimulationDict_Brazil_tracked, ModuleDict_Brazil, 'Brazil tracked 2023 POA-conversion', (2023, 1, 1, 7), (2023, 1, 5, 18), 1, brazil_tracked_real_path)        
        
        #SimulationDict_Heggelbach['weatherFile'] = rootPath + '/WeatherData/Heggelbach_Germany/Heggelbach_Germany_2017.csv'
        #heggelbach_h_17, heggelbach_d_17, heggelbach_avg_17 = test_function(SimulationDict_Heggelbach, ModuleDict_Heggelbach, 'Heggelbach 2017', (2017, 1, 1, 1), (2017, 1, 5, 0), 0, heggelbach_real_path)
        #SimulationDict_Heggelbach['weatherFile'] = rootPath + '/WeatherData/Heggelbach_Germany/Heggelbach_Germany_2018.csv'
        
        #SimulationDict_Heggelbach['weatherFile'] = rootPath + '/WeatherData/Heggelbach_Germany/Heggelbach_Germany_2021.csv'

        """simulate across year boundaries"""
        
    
        """plot and show final results to interact with"""
        #plot_lines(heggelbach_h_17, 'P_bi ', r'Bifacial Power Output [$\mathrm{\frac{W}{m^2}}$]', resultspath, 'Heggelbach 2017 - Hourly Bifacial Power Output', True)
        #plot_lines(heggelbach_h_18, 'P_bi ', r'Bifacial Power Output [$\mathrm{\frac{W}{m^2}}$]', resultspath, 'Heggelbach 2018 - Hourly Bifacial Power Output', True)
        #plot_lines(heggelbach_h_21, 'P_bi ', r'Bifacial Power Output [$\mathrm{\frac{W}{m^2}}$]', resultspath, 'Heggelbach 2021 - Hourly Bifacial Power Output', True)
        plot_lines(heggelbach_h_22, 'P_bi ', r'Bifacial Power Output [$\mathrm{\frac{W}{m^2}}$]', resultspath, 'Heggelbach 2022 - Hourly Bifacial Power Output', True)
        #plot_lines(brazil_tracked_h, 'P_bi ', r'Bifacial Power Output [$\mathrm{\frac{W}{m^2}}$]', resultspath, 'Brazil tracked - Hourly Bifacial Power Output', True)
        
        #plot_boxplots(heggelbach_d_17, ['delta_E_abs', 'delta_Q_front_abs', 'delta_Q_rear_abs' ], r'Energy yield per m$^2$  [$\mathrm{\frac{Wh}{m^2*d}}$]', resultspath, 'Heggelbach 2017 - Absolute Energy Difference - Daily', True)
        #plot_boxplots(heggelbach_d_18, ['delta_E_abs', 'delta_Q_front_abs', 'delta_Q_rear_abs' ], r'Energy yield per m$^2$  [$\mathrm{\frac{Wh}{m^2*d}}$]', resultspath, 'Heggelbach 2018 - Absolute Energy Difference - Daily', True)
        #plot_boxplots(heggelbach_d_21, ['delta_E_abs', 'delta_Q_front_abs', 'delta_Q_rear_abs' ], r'Energy yield per m$^2$  [$\mathrm{\frac{Wh}{m^2*d}}$]', resultspath, 'Heggelbach 2021 - Absolute Energy Difference - Daily', True)
        #plot_boxplots(heggelbach_d_22, ['delta_E_abs', 'delta_Q_front_abs', 'delta_Q_rear_abs' ], r'Energy yield per m$^2$  [$\mathrm{\frac{Wh}{m^2*d}}$]', resultspath, 'Heggelbach 2022 - Absolute Energy Difference - Daily', True)
        #plot_boxplots(heggelbach_avg_22, ['delta_E_rel', 'delta_E_rad_front_rel', 'delta_E_rad_rear_rel' ], r'Energy yield per m$^2$  [$\mathrm{\frac{Wh}{m^2}}$]', resultspath, 'Heggelbach 2022 - Relative Energy Difference - Full timeframe', True, True)
        plot_bars(heggelbach_avg_22, ['delta_E_rel', 'delta_E_rad_front_rel', 'delta_E_rad_rear_rel' ], r'Energy yield per m$^2$  [$\mathrm{\frac{Wh}{m^2}}$]', resultspath, 'Heggelbach 2022 - Relative Energy Difference - Full timeframe', True, True)
        #plot_boxplots(brazil_tracked_d, ['delta_E_abs', 'delta_Q_front_abs', 'delta_Q_rear_abs' ], r'Energy yield per m$^2$  [$\mathrm{\frac{Wh}{m^2*d}}$]', resultspath, 'Brazil tracked - Absolute Energy Difference - Daily', True)
        
    except Exception as err:     
       print("Error:",err)

    
    """Initiate system sleep when simulation is complete""" 
    if system_shutdown == True:    
        
        shutdown_thread = ShutdownThread(10)
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

