# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 11:39:16 2021
@author:        
    Eva-Maria Grommes

Additional co-authors can be found here:
https://github.com/cire-thk/bifacialSimu    

name:
    BifacialSimu - dataHandler

overview:
    Handles the import and export of data 
    used by the bifacial simulation of PV-Modules

"""

# Import/transformation of needed data
# Import/transformation of Excel sheets
    # function to merge radiation data
    # function to export radiation data
    # function to export graphics and plots
    # function to create reports


import datetime
import pandas as pd
import os #to import directories
import sys
import dateutil
import numpy as np
from pathlib import Path


# Path handling
rootPath = os.path.dirname(os.path.dirname(os.path.realpath(".")))

#adding rootPath to sysPath
sys.path.append(rootPath)

from BifacialSimu_src.BifacialSimu.Handler import BifacialSimu_radiationHandler #"from ." is essential to tell python that the module is found in this file's PATH

class DataHandler:
    def __init__(self):
        self.localDir = rootPath

    
    def setDirectories(self, outputFolder = "Outputs"):
        '''
        outputFolder: str
            Name of output folder (will be created)
        
        '''
  
        # Path to import irradiance data / Quality for plot export
        now = datetime.datetime.now()
        date_time = now.strftime("%Y %m %d_%H_%M") # get current date and time
        outputPath = os.path.join(self.localDir, outputFolder)
        resultsPath = os.path.join(outputPath, date_time + '_results/' ) 
        if not os.path.exists(resultsPath):
            os.makedirs(resultsPath)        # create path to output
        
        return resultsPath
    
    
    def getWeatherData(self, simulationDict, resultsPath):
        """
        Function to create a Radiance Obj with bifacial_radiance and read weather data.
        Can read EPW weather files from input location data or local weather files
        
        Parameters
        ----------
        simulationDict: simulation Dictionary, which can be found in BifacialSimuu_main.py
        resultsPath: output filepath
        """

        starttime =  str(simulationDict['startHour'][1]) +'_'+ str(simulationDict['startHour'][2])+'_'+ str(simulationDict['startHour'][3]) 
        endtime = str(simulationDict['endHour'][1]) +'_'+ str(simulationDict['endHour'][2])+'_'+ str(simulationDict['endHour'][3])
        
        demo = BifacialSimu_radiationHandler.RayTrace.createDemo(simulationDict, resultsPath)
        
        if simulationDict['localFile'] == False:
            
            try:
                longitude = simulationDict['longitude']
                latitude = simulationDict['latitude']
            
                epwfile = demo.getEPW(latitude,longitude) # pull TMY data for any global lat/lon
            except ConnectionError: # no connection to automatically pull data
                pass
            metdata = demo.readEPW(epwfile, starttime= starttime, endtime=endtime, label='center') # read in the EPW weather data from above

        else:            

            metdata = demo.readWeatherFile(weatherFile=simulationDict['weatherFile'], starttime=starttime, endtime=endtime, label='center')

        return metdata, demo
    
    def passEPWtoDF(self, metdata, simulationDict, resultsPath):
        
        """
        Function to pass irradiance data and temperature from metdata Object created by bifacial_radiance to a pandas dataframe.
        The dataframe will be further used in the class ViewFactors.
        Additionally, a timeindex will be set.
        
        Parameters
        ----------
        simulationDict: simulation Dictionary, which can be found in BifacialSimu_main.py
        metdata: Object containing meteorological data and sun parameters        
        resultsPath: output filepath       
        """

        df = metdata.solpos
        print('DF at start of data handler',df)
        try:
            df['ghi'] = metdata.ghi
            df['dhi'] = metdata.dhi
            df['dni'] = metdata.dni
            df['temperature'] = metdata.temp_air
            df['pressure'] = metdata.pressure
            df['albedo'] = metdata.albedo
            
        except:
            df['ghi'] = metdata.ghi
            df['dhi'] = metdata.dhi
            df['dni'] = metdata.dni
            df['temperature'] = metdata.temp_air
            df['albedo'] = metdata.albedo
        
        df['albedo'] = df['albedo'].apply(lambda x: simulationDict['albedo'] if x >= 1 or x <= 0 else x)

        # setting UTC offset from weatherfile
        df = df.reset_index()
        df['corrected_timestamp'] = pd.to_datetime(df['corrected_timestamp'])
        simulationDict['utcOffset'] = int(df['corrected_timestamp'][0].utcoffset().total_seconds()/3600) #set UTC offset from weatherfile

        df['timestamp'] = df['corrected_timestamp']
        df = df.set_index('timestamp')

        df.to_csv(Path(resultsPath + "Dataframe_df.csv"))
        
        return df