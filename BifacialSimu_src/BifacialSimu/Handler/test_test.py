# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 17:57:09 2022

@author: egrommes
"""

# Test für simulate_simpleBifacial
# import sys
import os
rootPath = os.path.realpath("../../")

# from mypackage.mymodule import as_int
import unittest
import pandas as pd
from BifacialSimu.Handler.BifacialSimu_calculationHandler import Electrical_simulation
from BifacialSimu.Handler.BifacialSimu_radiationHandler import ViewFactors, RayTrace
from BifacialSimu.Handler.BifacialSimu_dataHandler import DataHandler
from bifacial_radiance import *
from Vendor.pvfactors.engine import PVEngine
from Vendor.pvfactors import geometry


simulationDict={
    
    'simulationName' : 'NREL_best_field_row_2',
    'simulationMode' : 1, 
    'localFile' : True, # Decide wether you want to use a  weather file or try to download one for the coordinates
    'weatherFile' : (rootPath +'/WeatherData/Golden_USA/SRRLWeatherdata Nov_Dez_2.csv'), #weather file in TMY format 
    'spectralReflectancefile' : (rootPath + '/ReflectivityData/interpolated_reflectivity.csv'),
    'cumulativeSky' : False, # Mode for RayTracing: CumulativeSky or hourly
    'startHour' : (2019, 11, 1, 0),  # Only for hourly simulation, yy, mm, dd, hh
    'endHour' : (2019, 11, 16, 0),  # Only for hourly simulation, yy, mm, dd, hh
    'utcOffset': -7,
    'tilt' : 10, #tilt of the PV surface [deg]
    'singleAxisTracking' : True, # singleAxisTracking or not
    'backTracking' : False, # Solar backtracking is a tracking control program that aims to minimize PV panel-on-panel shading 
    'ElectricalMode_simple': False, # simple electrical Simulation after PVSyst, use if rear module parameters are missing
    'limitAngle' : 60, # limit Angle for singleAxisTracking
    'hub_height' : 1.3, # Height of the rotation axis of the tracker [m]
    'azimuth' : 180, #azimuth of the PV surface [deg] 90°: East, 135° : South-East, 180°:South
    'nModsx' : 1, #number of modules in x-axis
    'nModsy' : 1, #number of modules in y-axis
    'nRows' : 3, #number of rows
    'sensorsy' : 5, #number of sensors
    'moduley' : 2 ,#length of modules in y-axis
    'modulex' : 1, #length of modules in x-axis  
    'fixAlbedo': False, # Option to use the fix albedo
    'hourlyMeasuredAlbedo' : True, # True if measured albedo values in weather file
    'hourlySpectralAlbedo' : True, # Option to calculate a spectral Albedo 
    'variableAlbedo': False, # Option to calculate sun position dependend, variable albedo
    'albedo' : 0.26, # Measured Albedo average value, if hourly isn't available
    'frontReflect' : 0.03, #front surface reflectivity of PV rows
    'BackReflect' : 0.05, #back surface reflectivity of PV rows
    'longitude' : -105.172, 
    'latitude' : 39.739,
    'gcr' : 0.35, #ground coverage ratio (module area / land use)
    'module_type' : 'NREL row 2', #Name of Module
    }

# simulationParameter = {
# 'n_pvrows': simulationDict['nRows'], #number of PV rows
# 'number_of_segments': simulationDict['sensorsy'], #number of segments for each PVrow
# 'pvrow_height': simulationDict['clearance_height'], #height of the PV rows, measured at their center [m]
# 'pvrow_width': simulationDict['moduley'], #width of the PV panel in row, considered 2D plane [m]
# 'pvmodule_width': simulationDict['modulex'], #length of the PV panel in row, considered 2D plane [m]
# 'surface_azimuth': simulationDict['azimuth'], #azimuth of the PV surface [deg] 90°= East, 135° = South-East, 180°=South
# 'surface_tilt': simulationDict['tilt'], #tilt of the PV surface [deg]
# 'albedo': simulationDict['albedo'], # Measured Albedo average value
# #'a0': albedo, # Measured Albedo under direct illumination with a solar zenith angle of approx. 60°
# #'adiff': albedo_diff, # Measured Albedo under 100% diffuse illumination
# 'C': 0.4, #Solar angle dependency factor    
# #'index_observed_pvrow': 1, #index of the PV row, whose incident irradiance will be returned
# 'rho_front_pvrow' : simulationDict['frontReflect'], #front surface reflectivity of PV rows
# 'rho_back_pvrow' : simulationDict['BackReflect'], #back surface reflectivity of PV rows
# 'horizon_band_angle' : 6.5, #elevation angle of the sky dome's diffuse horizon band [deg]   
# 'L_Position': simulationDict['longitude'], #Longitude of measurement position [deg]
# 'L_Area': -105.1727827, #Longitude of timezone area [deg]
# 'Latitude_Position': simulationDict['latitude'], #Latitude of measurement position [deg]
# 'axis_azimuth': 0.0, #Axis Azimuth angle [deg]
# 'gcr': simulationDict['gcr'], #ground coverage ratio (module area / land use)
# 'x_min': -100,
# 'x_max': 100,
# }

resultsPath = DataHandler().setDirectories()

demo=0
metdata=0
dataFrame={}
onlyFrontscan=False
onlyBackscan=False
VF=ViewFactors

df_reportVF=VF.simulateViewFactors(demo, metdata, dataFrame, resultsPath, onlyFrontscan=False)
df_reportRT = RayTrace.simulateRayTrace(demo, metdata, resultsPath, dataFrame, onlyBackscan)
df_report = Electrical_simulation.build_simulationReport(df_reportVF, df_reportRT, simulationDict, resultsPath)

moduleDict={
		"bi_factor": 0.694,
		"n_front": 0.19,
        "I_sc_f": 9.5,
        "I_sc_r": 6.56,
        "V_oc_f": 48,
        "V_oc_r": 47.3,
        "V_mpp_f": 39.2,
        "V_mpp_r": 39.5,
        "I_mpp_f": 9.0,
        "I_mpp_r": 6.2,
        "P_mpp": 354,
        "T_koeff_P": -0.0036,
        "T_amb": 20,
        "T_koeff_I": 0.0005,
        "T_koeff_V": 0.0005,
        "zeta": 0.06,
		"moduley": 1.98,
		"modulex": 0.992
}
   
    #assertEqual(1,2) #1actual value #2expected
    
    # df_report={}
    # df=pd.DataFrame()
    # resultsPath=""
    

class TestStringMethods(unittest.TestCase):
    
    def test_simulate_simpleBifacial(self):
        result_1= Electrical_simulation.simulate_simpleBifacial(simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
        self.assertEqual(result_1, 9.457514227805062)

    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()