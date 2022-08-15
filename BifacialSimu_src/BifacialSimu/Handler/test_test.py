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
from BifacialSimu.Handler import BifacialSimu_radiationHandler
from BifacialSimu.Handler import BifacialSimu_dataHandler
from BifacialSimu.Handler.BifacialSimu_dataHandler import DataHandler
from Vendor.bifacial_radiance.main import RadianceObj
from bifacial_radiance import *
from Vendor.pvfactors.engine import PVEngine
from Vendor.pvfactors import geometry


simulationDict={
    'clearance_height': 0.4, #value was found missing! should be added later!
    'simulationName' : 'NREL_best_field_row_2',
    'simulationMode' : 2, 
    'localFile' : True, # Decide wether you want to use a  weather file or try to download one for the coordinates
    'weatherFile' : (rootPath +'/WeatherData/Golden_USA/SRRLWeatherdata Nov_Dez_2.csv'), #weather file in TMY format 
    'spectralReflectancefile' : (rootPath + '/ReflectivityData/interpolated_reflectivity.csv'),
    'cumulativeSky' : False, # Mode for RayTracing: CumulativeSky or hourly
    'startHour' : (2019, 11, 1, 0),  # Only for hourly simulation, yy, mm, dd, hh
    'endHour' : (2019, 11, 16, 0),  # Only for hourly simulation, yy, mm, dd, hh
    'utcOffset': -7,
    'tilt' : 25, #tilt of the PV surface [deg]
    'singleAxisTracking' : True, # singleAxisTracking or not
    'backTracking' : False, # Solar backtracking is a tracking control program that aims to minimize PV panel-on-panel shading 
    'ElectricalMode_simple': 0, # simple electrical Simulation after PVSyst, use if rear module parameters are missing
    'limitAngle' : 60, # limit Angle for singleAxisTracking
    'hub_height' : 1.3, # Height of the rotation axis of the tracker [m]
    'azimuth' : 180, #azimuth of the PV surface [deg] 90°: East, 135° : South-East, 180°:South
    'nModsx' : 5, #number of modules in x-axis
    'nModsy' : 1, #number of modules in y-axis
    'nRows' : 3, #number of rows
    'sensorsy' : 5, #number of sensors
    'moduley' : 1.98 ,#length of modules in y-axis
    'modulex' : 0.992, #length of modules in x-axis  
    'fixAlbedo': False, # Option to use the fix albedo
    'hourlyMeasuredAlbedo' : True, # True if measured albedo values in weather file
    'hourlySpectralAlbedo' : True, # Option to calculate a spectral Albedo 
    'variableAlbedo': False, # Option to calculate sun position dependend, variable albedo
    'albedo' : 0.247, # Measured Albedo average value, if hourly isn't available
    'frontReflect' : 0.03, #front surface reflectivity of PV rows
    'BackReflect' : 0.05, #back surface reflectivity of PV rows
    'longitude' : -105.172, 
    'latitude' : 39.739,
    'gcr' : 0.45, #ground coverage ratio (module area / land use)
    'module_type' : 'NREL row 2', #Name of Module
    }

simulationName = simulationDict['simulationName']
onlyFrontscan=False
onlyBackscan=True


resultsPath = DataHandler().setDirectories()

metdata, demo = DataHandler().getWeatherData(simulationDict, resultsPath)

df = BifacialSimu_dataHandler.DataHandler().passEPWtoDF(metdata, simulationDict, resultsPath)
df_reportRT = pd.DataFrame()
df_reportVF = pd.DataFrame()
df_report = pd.DataFrame()
dataFrame = pd.DataFrame()

df_reportVF, df= BifacialSimu_radiationHandler.ViewFactors.simulateViewFactors(simulationDict, demo, metdata,  df, resultsPath, onlyFrontscan)
# df_report = Electrical_simulation.build_simulationReport(df_reportVF, df_reportRT, simulationDict, resultsPath)

# df_reportVF=ViewFactors.simulateViewFactors(simulationDict, demo, metdata, dataFrame, resultsPath, onlyFrontscan)
# df_reportRT = RayTrace.simulateRayTrace(simulationDict,demo, metdata, resultsPath, dataFrame, onlyBackscan)

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
   
    
result_1= Electrical_simulation.simulate_simpleBifacial(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)

class TestStringMethods(unittest.TestCase):
    
    def test_simulate_simpleBifacial(self):
        self.assertEqual(result_1, 5.599072940263201)

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