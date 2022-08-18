import os
rootPath = os.path.realpath("../")

import unittest
import csv
import pandas as pd
from BifacialSimu.Handler.BifacialSimu_radiationHandler import ViewFactors, RayTrace
from BifacialSimu.Handler.BifacialSimu_dataHandler import DataHandler

simulationDict={
    'clearance_height': 0.4, #value was found missing! should be added later!
    'simulationName' : 'NREL_best_field_row_2',
    'simulationMode' : 1, 
    'localFile' : True, # Decide wether you want to use a  weather file or try to download one for the coordinates
    'weatherFile' : (rootPath +'/WeatherData/Golden_USA/SRRLWeatherdata Nov_Dez_2.csv'), #weather file in TMY format 
    'spectralReflectancefile' : (rootPath + '/ReflectivityData/interpolated_reflectivity.csv'),
    'cumulativeSky' : False, # Mode for RayTracing: CumulativeSky or hourly
    'startHour' : (2019, 11, 1, 0),  # Only for hourly simulation, yy, mm, dd, hh
    'endHour' : (2019, 11, 16, 0),  # Only for hourly simulation, yy, mm, dd, hh
    'utcOffset': -7,
    'tilt' : 25, #tilt of the PV surface [deg]
    'singleAxisTracking' : False, # singleAxisTracking or not
    'backTracking' : False, # Solar backtracking is a tracking control program that aims to minimize PV panel-on-panel shading 
    'ElectricalMode_simple': 1, # simple electrical Simulation after PVSyst, use if rear module parameters are missing
    'limitAngle' : 60, # limit Angle for singleAxisTracking
    'hub_height' : 1.3, # Height of the rotation axis of the tracker [m]
    'azimuth' : 180, #azimuth of the PV surface [deg] 90°: East, 135° : South-East, 180°:South
    'nModsx' : 5, #number of modules in x-axis
    'nModsy' : 1, #number of modules in y-axis
    'nRows' : 3, #number of rows
    'sensorsy' : 5, #number of sensors
    'moduley' : 1.98 ,#length of modules in y-axis
    'modulex' : 0.992, #length of modules in x-axis  
    'fixAlbedo': True, # Option to use the fix albedo
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

df_reportRT = pd.DataFrame()
df_reportVF = pd.DataFrame()
df_report = pd.DataFrame()
dataFrame = pd.DataFrame()

'Importing known results. To be used later in unittest output comparison'
df_csv= pd.read_csv(rootPath + "/Tests/Data.csv", index_col=('timestamp'))
df_csv=df_csv.reset_index(drop=True)
report_VF = pd.read_csv(rootPath + "/Tests/radiation_qabs_results.csv")
report_VF= report_VF.reset_index(drop=True)
VF_csv = pd.read_csv(rootPath + "/Tests/view_factors_4_12.csv")
VF_csv = VF_csv.reset_index(drop=True)


'The 4 lines below were used to manually compare results in unittest. Results are still giving illogical results.'
'Compare results are sometimes giving False values even though the compared values are identically equal!'
# df = DataHandler().passEPWtoDF(metdata, simulationDict, resultsPath)
# df_reportVF, df = ViewFactors.simulateViewFactors(simulationDict, demo, metdata,  df, resultsPath, onlyFrontscan)
# compare = df_csv==df #Compare values are appearing illogically False
# result= df.equals(df_csv) #why False??


class TestSimulationMethodes (unittest.TestCase):
    
    def test_SimulateViewFactors (self):
        df = DataHandler().passEPWtoDF(metdata, simulationDict, resultsPath)
        simulationDict['simulationMode'] = 2
        df_reportVF, df, view_factors_results= ViewFactors.simulateViewFactors(simulationDict, demo, metdata,  df, resultsPath, onlyFrontscan)
        
        #Must drop Index to avoid the Error:
            #ValueError: Can only compare identically-labeled DataFrame objects
        df_reportVF= df_reportVF.reset_index(drop=True)
        df=df.reset_index(drop=True)
        view_factors_results=view_factors_results.reset_index(drop=True)
        
        result1= df.equals(df_csv)
        result2= report_VF.equals(df_reportVF)
        result3= view_factors_results.equals(VF_csv)
        
        self.assertEqual(result1, True)
        self.assertEqual(result2, True)
        self.assertEqual(result3, True)
        



if __name__ == '__main__':
    unittest.main()
        