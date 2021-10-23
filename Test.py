# -*- coding: utf-8 -*-
"""
Created on Thu Oct 21 22:20:54 2021

@author: sarah
"""
import os
import pandas as pd
import csv 
import math

rootPath = os.path.realpath(".")

simulationDict = {
'simulationName' : 'NREL_best_field_row_2',
'simulationMode' : 1, 
'localFile' : True, # Decide wether you want to use a  weather file or try to download one for the coordinates
'weatherFile' : (rootPath +'/WeatherData/Cologne_Germany/Cologne_Bibdach_50.935_6.992_Measurement_Sept_Okt_2021_Test.csv'), # weather file in TMY format 
'spectralReflectancefile' : (rootPath + '/ReflectivityData/interpolated_reflectivity.csv'),
'cumulativeSky' : False, # Mode for RayTracing: CumulativeSky or hourly
'startHour' : (2021, 9, 23, 0),  # Only for hourly simulation, yy, mm, dd, hh
'endHour' : (2021, 9, 24, 0),  # Only for hourly simulation, yy, mm, dd, hh
'utcOffset': +2,
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
'hourlyMeasuredAlbedo' : False, # True if measured albedo values in weather file
'spectralAlbedo' : True, # Option to calculate a spectral Albedo 
'albedo' : 0.2384, # Measured Albedo average value, if hourly isn't available
'frontReflect' : 0.03, #front surface reflectivity of PV rows
'BackReflect' : 0.05, #back surface reflectivity of PV rows
'longitude' : 6.992, 
'latitude' : 50.935,
'gcr' : 0.35, #ground coverage ratio (module area / land use)
'module_type' : 'NREL row 2', #Name of Module
}

a_hourly = []
for i in range(380):
    a_hourly.append(i)


with open(rootPath +'/WeatherData/Cologne_Germany/Cologne_Bibdach_50.935_6.992_Measurement_Sept_Okt_2021.csv', newline='') as f:
  reader = csv.reader(f)
  row1 = next(reader)  # gets the first line
  row2 = next(reader)  # gets the second line

weatherfile = pd.read_csv(rootPath +'/WeatherData/Cologne_Germany/Cologne_Bibdach_50.935_6.992_Measurement_Sept_Okt_2021.csv', sep=',', header = 1)

length_w= len(weatherfile.index)
print(len(weatherfile.index))
length_a= len(a_hourly)
print(len(a_hourly))

if length_a < length_w: 
    dif_length = length_w - length_a
    for i in range(dif_length):
        a_hourly.append(math.nan)

weatherfile['Alb'] = a_hourly
print(weatherfile)

weatherfile_list = weatherfile.values.tolist()

file = open(simulationDict['weatherFile'], 'w+', newline ='') 
with file:     
    write = csv.writer(file) 
    write.writerow(row1)
    write.writerow(row2)
    write.writerows(weatherfile_list) 