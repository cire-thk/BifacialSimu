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






# Path handling
rootPath = os.path.dirname(os.path.dirname(os.path.realpath(".")))

from BifacialSimu_src import WeatherData
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
        
        demo = BifacialSimu_radiationHandler.RayTrace.createDemo(simulationDict, resultsPath)
        if simulationDict['localFile'] == False:
            try:
                longitude = simulationDict['longitude']
                latitude = simulationDict['latitude']
            
                epwfile = demo.getEPW(latitude,longitude) # pull TMY data for any global lat/lon
            except ConnectionError: # no connection to automatically pull data
                pass
            metdata = demo.readEPW(epwfile) # read in the EPW weather data from above
            
        else:
            metdata = demo.readTMY(simulationDict['weatherFile'])

        
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

        df['ghi'] = metdata.ghi
        df['dhi'] = metdata.dhi
        df['dni'] = metdata.dni

        df['temperature'] = metdata.temp_air
        df['pressure'] = metdata.pressure
        df['albedo'] = metdata.albedo
        
        #define start and end Date for dataframe
        #dtStart = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
        #dtEnd = datetime.datetime(simulationDict['endHour'][0], simulationDict['endHour'][1], simulationDict['endHour'][2], simulationDict['endHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
         
       
        df = df.reset_index()
        
        
        df['corrected_timestamp'] = pd.to_datetime(df['corrected_timestamp'])
        #add 30 minutes, since the calculation of the sunposition has changed the dateformat to -30 minutes 
        df['corrected_timestamp'] = df['corrected_timestamp'] + datetime.timedelta(minutes=30)
        
        #change the days at midnight, because through the shifting it is not right anymore
        if simulationDict['localFile'] == True:
            
            df['corrected_timestamp'] = df['corrected_timestamp'].astype(str)
            df['is_midnight']= df['corrected_timestamp'].str[11:13].apply(lambda x: 'YES' if (x == '00') else 'NO') 
            df['corrected_timestamp'] = pd.to_datetime(df['corrected_timestamp'])
            df['corrected_timestamp'] = np.where(df['is_midnight'] == "YES", df['corrected_timestamp'] + datetime.timedelta(days=-1), df['corrected_timestamp'])
            df.drop(columns=['is_midnight'])
            
        df = df.set_index('corrected_timestamp')
        
        #check if the year of the weatherfile is the same as which the user has entered
        if str(df.index.year[0]) != str(simulationDict['startHour'][0]):
              sys.exit("Please correct the input year to match the year of the weather file: " + str(df.index.year[0]))
            
        
        print('view_factor dataframe at data handler:')
        print(df)

        df.to_csv(resultsPath + "Dataframe_df.csv")
        return df