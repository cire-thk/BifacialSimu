# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 11:39:16 2021
@author:        
    CIRE TH Cologne
    Felix Schemann
    Frederik Klag
    Sebastian Nows

name:
    BiSim - dataHandler

overview:
    Handles the import and export of data 
    used by the bifacial simulation of PV-Modules

last changes:
    07.06.21 created

"""


# Klasse zum Importieren/Umwandeln von benötigten Daten
    
    # Funktion zum einlesen/umwandeln von Exceldateien?    


# Klasse zum Exportieren/Umwandeln von benötigten Daten

    # Funktion zum zusammenführen von Radiaton-Daten
    # Funktion zum Exportieren von Radiation-Daten
    # Funktion zum Exportieren von Grafiken
    # Funktion zum Exportieren eines Berichts?
 

from datetime import datetime   
import os #to import directories
import sys
import bifacial_radiance
from bifacial_radiance import *



# Path handling
rootPath = os.path.dirname(os.path.dirname(os.path.realpath(".")))

import BiSim_radiationHandler

class DataHandler:
    def __init__(self):
        self.localDir = rootPath

    
    def setDirectories(self, outputFolder = "Outputs"):
        '''
        outputFolder: str
            Name of output folder (will be created)
        
        '''
  
        # Path to import irradiance data / Quality for plot export
        now = datetime.now()
        date_time = now.strftime("%Y %m %d_%H_%M") # get current date and time
        outputPath = os.path.join(self.localDir, outputFolder)
        resultsPath = os.path.join(outputPath, date_time + '_results/' ) 
        if not os.path.exists(resultsPath):
            os.makedirs(resultsPath)        # create path to output
        
        return resultsPath
    
    
    def getWeatherData(self, simulationDict, resultsPath):
        
        demo = BiSim_radiationHandler.RayTrace.createDemo(simulationDict, resultsPath)
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
    
    def passEPWtoDF(self, metdata):

        df = metdata.solpos
        
        df['ghi'] = metdata.ghi
        df['dhi'] = metdata.dhi
        df['dni'] = metdata.dni
        df['temperature'] = metdata.temp_air
        print('view_factor dataframe at data handler:')
        print(df)
        #df.index.name = "corrected_timestamp"
        return df