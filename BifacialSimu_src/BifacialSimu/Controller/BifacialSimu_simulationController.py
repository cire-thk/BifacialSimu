# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 11:39:16 2021
@author:        
    Eva-Maria Grommes

Additional co-authors can be found here:
https://github.com/cire-thk/bifacialSimu    

name:
    BifacialSimu - SimulationController

overview:
    Read the input data and settings from the main script, calls the functions 
    of the handlers to perform the bifacial simulation of PV-Modules with
    View Factors and/or Ray Tracing method


"""

'''import os
import sys
# Path handling
rootPath = os.path.dirname(os.path.dirname(os.path.realpath(".")))
print(rootPath)
# Include paths
sys.path.append(rootPath)
sys.path.append(rootPath + "/BifacialSimu/Handler")'''

import pandas as pd
import sys
from BifacialSimu.Handler import * #much easier handling Directories using __init__.py files (avoids import errors)

# Overarching procedure to perform bifacial irrdiance and electrical simulations  
def startSimulation(simulationDict, moduleDict, resultsPath):

    #the path is implemented in GUI.py
    # resultsPath = BifacialSimu_dataHandler.DataHandler().setDirectories()
    # print('created resultsPath at: ' + resultsPath)

    
    #get weatherFile
    metdata, demo = BifacialSimu_dataHandler.DataHandler().getWeatherData(simulationDict, resultsPath)

    print('succsessfully created metdata and demo')
    
    # pass weatherfile to df
    df = BifacialSimu_dataHandler.DataHandler().passEPWtoDF(metdata, simulationDict, resultsPath)
    df_reportRT = pd.DataFrame()
    df_reportVF = pd.DataFrame()
    df_report = pd.DataFrame()
    
    ####################################################
    
    # optional spectralAlbedo calculation
    if simulationDict['hourlySpectralAlbedo'] == True:
        # spectralAlbedoHandler calculate the spectral albedo and write it in the weatherfile in colume 'albedo'
        #BifacialSimu_spectralAlbedoHandler_1_row.calculateAlbedo(simulationDict, df, resultsPath)
        BifacialSimu_spectralAlbedoHandler.calculateAlbedo(simulationDict, df, resultsPath)
        # weatherfile is read in again with updated albedo values as metdata
        metdata, demo = BifacialSimu_dataHandler.DataHandler().getWeatherData(simulationDict, resultsPath) 
    
        # metdata is converted to df
        df = BifacialSimu_dataHandler.DataHandler().passEPWtoDF(metdata, simulationDict, resultsPath)
        print('succsessfully updated metdata, demo and df with spectral albedo')
    
    ####################################################
    
    # choose simulation mode and perform raytracing, viewfactor and electrical simulation
    
    if simulationDict['simulationMode'] == 3:
        print('Front and back simulation with RayTrace')
        df_reportRT = BifacialSimu_radiationHandler.RayTrace.simulateRayTrace(simulationDict, demo, metdata, resultsPath, df, onlyBackscan = False)
        
        if simulationDict['ElectricalMode_simple'] == 0:      
            BifacialSimu_calculationHandler.Electrical_simulation.simulate_simpleBifacial(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
        if simulationDict['ElectricalMode_simple'] == 1:
            BifacialSimu_calculationHandler.Electrical_simulation.simulate_oneDiode(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
        if simulationDict['ElectricalMode_simple'] == 2:      
            BifacialSimu_calculationHandler.Electrical_simulation.simulate_doubleDiode(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
        if simulationDict['ElectricalMode_simple'] == 3:
            BifacialSimu_calculationHandler.Electrical_simulation.simulate_doubleDiodeBi(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
        
    if simulationDict['simulationMode'] == 5 or simulationDict['simulationMode'] == 1:
        print('Back simulation with RayTrace')
        df_reportRT =  BifacialSimu_radiationHandler.RayTrace.simulateRayTrace(simulationDict, demo, metdata, resultsPath, df, onlyBackscan = True)
        
        
    if simulationDict['simulationMode'] == 2:
        print('Front and back simulation with ViewFactors')
        df_reportVF, df = BifacialSimu_radiationHandler.ViewFactors.simulateViewFactors(simulationDict, demo, metdata,  df, resultsPath, onlyFrontscan = False)
        
        if simulationDict['ElectricalMode_simple'] == 0:      
            BifacialSimu_calculationHandler.Electrical_simulation.simulate_simpleBifacial(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
        if simulationDict['ElectricalMode_simple'] == 1:
            BifacialSimu_calculationHandler.Electrical_simulation.simulate_oneDiode(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
        if simulationDict['ElectricalMode_simple'] == 2:      
            BifacialSimu_calculationHandler.Electrical_simulation.simulate_doubleDiode(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
        if simulationDict['ElectricalMode_simple'] == 3:
            BifacialSimu_calculationHandler.Electrical_simulation.simulate_doubleDiodeBi(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
    
    
    if simulationDict['simulationMode'] == 4 or simulationDict['simulationMode'] == 1:
        print('Front simulation with ViewFactors')
        df_reportVF, df = BifacialSimu_radiationHandler.ViewFactors.simulateViewFactors(simulationDict, demo, metdata,  df, resultsPath, onlyFrontscan = True)
        
        if simulationDict['ElectricalMode_simple'] == 0:      
            BifacialSimu_calculationHandler.Electrical_simulation.simulate_simpleBifacial(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
        if simulationDict['ElectricalMode_simple'] == 1:
            BifacialSimu_calculationHandler.Electrical_simulation.simulate_oneDiode(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
        if simulationDict['ElectricalMode_simple'] == 2:      
            BifacialSimu_calculationHandler.Electrical_simulation.simulate_doubleDiode(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
        if simulationDict['ElectricalMode_simple'] == 3:
            BifacialSimu_calculationHandler.Electrical_simulation.simulate_doubleDiodeBi(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
