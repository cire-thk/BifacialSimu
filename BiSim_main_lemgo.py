# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 11:39:16 2021
@author:        
    CIRE TH Cologne
    Felix Schemann
    Frederik Klag
    Sebastian Nows

name:
    BiSim - main

overview:
    Import of needed modules and paths.
    Input of variables and settings for the bifacial simulation of PV-Modules 
    with View Factors and/or Ray Tracing method. 
    Command to run the simulation
    
last changes:
    07.06.21 created

"""
    
# Start-Befehl für Simulation

# Später: Aufruf der GUI

# -*- coding: utf-8 -*-

# Import modules
import sys, os
import math

# Importieren der nötigen Module und Pfade
# Path handling
rootPath = os.path.realpath(".")
print(rootPath)
# Include paths
sys.path.append(rootPath + "/BiSim/Controller")
sys.path.append(rootPath + "/BiSim/Handler")

# Include modules
import BiSim_simulationController


# Eingabe von Simulationsvariablen und Einstellungen für die Simulationsmethode
    # Als Klasse oder Funktion oder Bibiliothek oder einfach nur so?
"""
        Sets the mode for simulation: str
        mode 1 : front simulation with PVfactors, back simulation with Raytracing
        mode 2 : front and back simulation with Viewfactors
        mode 3 : front and back simulation with Raytracing
        mode 4 : only front simulation with Viewfactors
        mode 5 : only back simulation with Raytracing
"""

# simulation parameters and variables
SimulationDict = {
'simulationName' : 'Lemgo_with_TRY_weatherdata_wholeYear',
'simulationMode' : 3, 
'localFile' : True, # Decide wether you want to use a  weather file or try to download one for the coordinates
'weatherFile' : (rootPath +'/WeatherData/Lemgo_germany/Lemgo_TMY.csv'), #weather file in TMY format 
'cumulativeSky' : False, # Mode for RayTracing: CumulativeSky or hourly
'startHour' : (2019, 1, 1, 1),  # Only for hourly simulation, yy, mm, dd, hh
'endHour' : (2019, 12, 1, 31),  # Only for hourly simulation, yy, mm, dd, hh
'utcOffset': 1,  
'tilt' : 25, #tilt of the PV surface [deg]
'singleAxisTracking' : True, # singleAxisTracking or not
'ElectricalMode_simple': True, # simple electrical Simulation after PVSyst, use if rear module parameters are missing
'limitAngle' : 60, # limit Angle for singleAxisTracking
'hub_height' : 0.8, #height of the PV rows, measured at the bottom [m]
'azimuth' : 180, #azimuth of the PV surface [deg] 90°: East, 135° : South-East, 180°:South
'nModsx' : 14, #number of modules in x-axis
'nModsy' : 2, #number of modules in y-axis
'nRows' : 11, #number of rows
'sensorsy' : 5, #number of sensors
'moduley' : 2.018 ,#length of modules in y-axis
'modulex' : 0.992, #length of modules in x-axis                       
'albedo' : 0.25, # Measured Albedo average value
'frontReflect' : 0.03, #front surface reflectivity of PV rows
'BackReflect' : 0.05, #back surface reflectivity of PV rows
'longitude' : 8.901289, 
'latitude' : 52.028067,
'gcr' : 0.453, #ground coverage ratio (module area / land use)
'module_type' : 'Lemgo-Modules', #Name of Module
}

# Calculate the height of the PV rows, measured at the bottom edge for the use in Viewfactors, PV*Sol and PVSyst
SimulationDict['clearance_height']  = (SimulationDict['hub_height'] - (math.sin(SimulationDict['tilt'])*SimulationDict['moduley']/2)) #height of the PV rows, measured at their center [m]

'''ModuleDict = {
    'I_sc_f': 9.34, #Short-circuit current measured for front side illumination of the module at STC [A]
    'I_sc_r': 6.54, #Short-circuit current measured for rear side illumination of the module at STC [A]
    'V_oc_f': 46.57, #Open-circuit voltage measured for front side illumination of module at STC [V]
    'V_oc_r': 45.77, #Open-circuit voltage measured for rear side illumination of module at STC [V]
    'V_mpp_f': 37.77, #Front Maximum Power Point Voltage [V]
    'V_mpp_r': 38.27, #Rear Maximum Power Point Voltage [V]
    'I_mpp_f': 8.87, #Front Maximum Power Point Current [A]
    'I_mpp_r': 6.19, #Rear Maximum Power Point Current [A]
    'P_mpp': 335, # Power at maximum power Point [W]
    'T_koeff_P': -0.0039, #Temperature Coeffizient for P_max [1/°C] #SG
    'T_amb': 25, #Ambient Temperature for measuring the Temperature Coefficient [°C] #SG
    'T_koeff_I': 0.0005, #Temperaturkoeffizient for I_sc [1/°C] #SG
    'T_koeff_V': 0.0005, #Temperaturkoeffizient for U_oc [1/°C] #SG
    'zeta': 0.06 #Bestrahlungskoeffizient für Leerlaufspannung [-]
    

    
    #'inverter': pvlib.pvsystem.retrieve_sam('cecinverter')['ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_'],
    #'module': pvlib.pvsystem.retrieve_sam('SandiaMod')['Canadian_Solar_CS5P_220M___2009_'],
    #'P_sys': 360, #system nominal power [KWp]
}'''


    #Lemgo Module Parameters
SimulationDict['clearance_height_mid'] = (SimulationDict['clearance_height'] + (math.sin(SimulationDict['tilt'])*SimulationDict['moduley']/2)) #height of the PV rows, measured at their center [m]

ModuleDict = {
'bi_factor': 0.75, #bifaciality factor
'n_front': 0.19, #module efficiency
'I_sc_f': 9.99, #Short-circuit current measured for front side illumination of the module at STC [A]
'I_sc_r': 9.99, #Short-circuit current measured for rear side illumination of the module at STC [A]
'V_oc_f': 47.9, #Open-circuit voltage measured for front side illumination of module at STC [V]
'V_oc_r': 47.9, #Open-circuit voltage measured for rear side illumination of module at STC [V]
'V_mpp_f': 40.1, #Front Maximum Power Point Voltage [V]
'V_mpp_r': 40.1, #Rear Maximum Power Point Voltage [V]
'I_mpp_f': 9.48, #Front Maximum Power Point Current [A]
'I_mpp_r': 9.48, #Rear Maximum Power Point Current [A]
'P_mpp': 380.2, # Power at maximum power Point [W]
'T_koeff_P': -0.0038, #Temperature Coeffizient for P_max [1/°C] #SG
'T_amb': 25, #Ambient Temperature for measuring the Temperature Coefficient [°C] #SG
'T_koeff_I': 0.0006, #Temperaturkoeffizient for I_sc [1/°C] #SG
'T_koeff_V': 0.0034, #Temperaturkoeffizient for U_oc [1/°C] #SG
'zeta': 0.06 #Bestrahlungskoeffizient für Leerlaufspannung [-]
}

# start simulation
BiSim_simulationController.startSimulation(SimulationDict, ModuleDict)
