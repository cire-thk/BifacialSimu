# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 11:39:16 2021
@author:        
    CIRE TH Cologne
    Felix Schemann
    Frederik Klag
    Sebastian Nows

name:
    BiSim - SimulationController

overview:
    Read the input data and settings from the main script, calls the functions 
    of the handlers to perform the bifacial simulation of PV-Modules with
    View Factors and/or Ray Tracing method

last changes:
    07.06.21 created


"""

'''import os
import sys
# Path handling
rootPath = os.path.dirname(os.path.dirname(os.path.realpath(".")))
print(rootPath)
# Include paths
sys.path.append(rootPath)
sys.path.append(rootPath + "/BiSim/Handler")'''

import pandas as pd
import BiSim_calculationHandler
import BiSim_radiationHandler
import BiSim_dataHandler

# Overarching procedure to perform bifacial irrdiance and electrical simulations  
def startSimulation(simulationDict, moduleDict, resultsPath):

    #the path is implemented in GUI.py
   # resultsPath = BiSim_dataHandler.DataHandler().setDirectories()
   # print('created resultsPath at: ' + resultsPath)
   
    
    #get weatherFile
    metdata, demo = BiSim_dataHandler.DataHandler().getWeatherData(simulationDict, resultsPath)

    print('succsessfully created metdata and demo')
    
    # pass weatherfile to df
    df = BiSim_dataHandler.DataHandler().passEPWtoDF(metdata, simulationDict, resultsPath)
    df_reportRT = pd.DataFrame()
    df_reportVF = pd.DataFrame()
    df_report = pd.DataFrame()
    
    # choose simulation mode and perform raytracing, viewfactor and electrical simulation
    if simulationDict['simulationMode'] == 3:
        print('Front and back simulation with RayTrace')
        df_reportRT = BiSim_radiationHandler.RayTrace.simulateRayTrace(simulationDict, demo, metdata, resultsPath, df, onlyBackscan = False)
        
        if simulationDict['ElectricalMode_simple'] == True:      
            BiSim_calculationHandler.Electrical_simulation.simulate_simpleBifacial(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
        else:
            BiSim_calculationHandler.Electrical_simulation.simulate_oneDiode(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
        
    if simulationDict['simulationMode'] == 5 or simulationDict['simulationMode'] == 1:
        print('Back simulation with RayTrace')
        df_reportRT =  BiSim_radiationHandler.RayTrace.simulateRayTrace(simulationDict, demo, metdata, resultsPath, df, onlyBackscan = True)
        
        
    if simulationDict['simulationMode'] == 2:
        print('Front and back simulation with ViewFactors')
        df_reportVF, df = BiSim_radiationHandler.ViewFactors.simulateViewFactors(simulationDict, demo, metdata,  df, resultsPath, onlyFrontscan = False)
        
        if simulationDict['ElectricalMode_simple'] == True:      
            BiSim_calculationHandler.Electrical_simulation.simulate_simpleBifacial(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
        else:
            BiSim_calculationHandler.Electrical_simulation.simulate_oneDiode(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
    
    if simulationDict['simulationMode'] == 4 or simulationDict['simulationMode'] == 1:
        print('Front simulation with ViewFactors')
        df_reportVF, df = BiSim_radiationHandler.ViewFactors.simulateViewFactors(simulationDict, demo, metdata,  df, resultsPath, onlyFrontscan = True)
        
        if simulationDict['ElectricalMode_simple'] == True:      
            BiSim_calculationHandler.Electrical_simulation.simulate_simpleBifacial(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
        else:
            BiSim_calculationHandler.Electrical_simulation.simulate_oneDiode(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath)
    


