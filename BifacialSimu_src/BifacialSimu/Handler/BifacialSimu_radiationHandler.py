# -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 11:39:16 2021

@author:        
    Eva-Maria Grommes

Additional co-authors can be found here:
https://github.com/cire-thk/bifacialSimu    

name:
    BifacialSimu - radiationHandler

overview:
    Manages the calculation of the radiation over the extern modules
    bifacial Radiance and/or PVfactors and delivers the radiation data for the 
    further simulation of BifacialSimu

"""


'Might have to remove IPython functions from this file. IPython should be used in GUI.py only'
from IPython import get_ipython
#get_ipython().magic('reset -sf')
import seaborn as sns
import os
import sys

# Path handling
rootPath = os.path.realpath("../../")

#adding rootPath to sysPath
sys.path.append(rootPath)

from pathlib import Path
import pandas as pd #pandas = can read .csv as input
import matplotlib.pyplot as plt #display shadows
import matplotlib.dates as mdates
import numpy as np
import warnings
import datetime
import numpy
import dateutil.tz
import sys
import math
from tkinter import messagebox
from BifacialSimu_src import globals

#import os #to import directories
#from pvlib.location import Location
#from tqdm import tqdm
#import BifacialSimu_dataHandler
#import math
#import pvlib #for electrical output simulation

# DEPENDENCIES AFTER VENDORING
from BifacialSimu_src.Vendor.bifacial_radiance.main import RadianceObj, AnalysisObj
from BifacialSimu_src.Vendor.pvfactors.viewfactors.aoimethods import faoi_fn_from_pvlib_sandia #to calculate AOI reflection losses
from BifacialSimu_src.Vendor.pvfactors.engine import PVEngine
from BifacialSimu_src.Vendor.pvfactors import irradiance, geometry, viewfactors

import ray
from ray.util.multiprocessing import Pool

ipython = get_ipython()
if ipython is not None:
    ipython.magic('reset -sf')
    
class RayTrace:
    
    """
    Raytracing class that uses the bifacial_radiance library to simulate front and rear irradiance of the PVarray.
    Uses parameters passed into BifacialSimuu.main's simulationDict.
 
    Methods
    -------
    createDemo : create a bifacial_radiance RadianceObj that calculates sun parameters and sky values
    simulateRaytrace: Function to perform raytracing simulation. Uses RadianceObj and simulation parameters 
                      for fixed tilt or single axis tracking simulation.  

    """
    
    def createDemo(simulationDict, resultsPath):
        # Create a RadianceObj 'object'
        simulationName = simulationDict['simulationName']
        demo = RadianceObj(name = simulationName, path = resultsPath) # Create a RadianceObj 'object'
        
        return demo

    def simulateRayTrace(simulationDict,demo,metdata, resultsPath, dataFrame, onlyBackscan):
        """
        Function to calculate singleAxisTracking or fixed tilt with the bifacial_radiance library.
        Uses cumulativeSky or gendayLit functions to calculate the irradiance, depending on input parameters in BifacialSimuu_main.py
        Returns df_reportRT for further use in the calculationHandler.
        
        Note: For cumulativeSky, no report will be created, since a  file containing the relevant data is already created by bifacial_radiance.
        Additionally, a cumulativeSky approach is not compatible with Viewfactors calculation, since it averages the sky over 1 year, while VF uses hourly calculations.
        
        Parameters
        ----------
        simulationDict: simulation Dictionary, which can be found in BifacialSimu_main.py
        demo: Bifacial_Radiance's RadianceObj created in "createDemo" function
        metdata: Object containing meteorological data and sun parameters
        resultsPath: output filepath
        dataFrame: helper DataFrame 
        onlyBackscan: option to only calculate rear side of the modules
        """
        
        ####################################################
        
            # if material=None, then material = metdata.albedo 
            # metdata.albedo (datatype: np.ndarray) is colume of metdata = RadianceObj out of weatherfile with albedo values
            # weatherfile must contain hourly measured albedo, if simulationDict['hourlymeasuredAlbedo'] = True
            # weatherfile contains spectral albedo, if simulationDict['hourlyspectralAlbedo'] = True
            # because spectralAlbedoHandler calcutlate spectral albedo and write the calculated spectral albedo in weatherfile
        
        ####################################################    
        

        # DEFINE a Module type
        moduley = simulationDict['moduley']*simulationDict['nModsy']
     
        # Make the Scene
        sceneDict = {'tilt': simulationDict['tilt'],'gcr': simulationDict['gcr'],'clearance_height':simulationDict['clearance_height'],'hub_height':simulationDict['hub_height'], 'azimuth':simulationDict['azimuth'], 'nModsx': simulationDict['nModsx'], 'nRows': simulationDict['nRows']} 
        
        dtStart = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
        dtEnd = datetime.datetime(simulationDict['endHour'][0], simulationDict['endHour'][1], simulationDict['endHour'][2], simulationDict['endHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
        hours = dtEnd - dtStart 
        hours = int(hours.total_seconds() / 3600) #+1
        
        #################
        #%% Cumulativ Sky
        
        if simulationDict['cumulativeSky'] == True:
            
            demo.makeModule(name=simulationDict['module_type'],x=simulationDict['modulex'], y=moduley)
            
            if simulationDict['fixAlbedo'] ==True:
                # Measured Albedo average fix value
                demo.setGround(simulationDict['albedo'])
                
            else:
                # hourly spectral albedo or hourly measured albedo
                if simulationDict['singleAxisTracking'] == True:
                    demo.setGround(material = None)
                else:
                    #demo.setGround(material = metdata.albedo)
                    sys.exit("The use of hourly Measured Albedo Values is not possible with fixed tilts at the moment")
            
            
            if simulationDict['singleAxisTracking'] == True:
                # get SingleAxisTracking Data
                trackerdict = demo.set1axis(metdata = metdata, limit_angle = simulationDict['limitAngle'], backtrack = simulationDict['backTracking'], 
                            gcr = simulationDict['gcr'], cumulativesky = True)
               
                #demo.genCumSky1axis(demo.epwfile)
                trackerdict = demo.genCumSky1axis()
                
                
                # Make the Scene
                trackerdict = demo.makeScene1axis(trackerdict = trackerdict, moduletype = simulationDict['module_type'], sceneDict = sceneDict) 
                # make the sky
                #trackerdict = demo.genCumSky1axis(trackerdict = trackerdict)
                #demo.genCumSky1axis(demo.epwfile)
                # make oct file
                
                trackerdict = demo.makeOct1axis(trackerdict = trackerdict)
                print('\n trackerdict \n', trackerdict)
                
                trackerdict = demo.analysis1axis(trackerdict)
                results = demo.analysis1axis(trackerdict, onlyBackscan = onlyBackscan)
                print('\n results \n', results)
                
                df_reportRT_sum = pd.DataFrame({
                                            'row_0_qabs_front': [np.mean(results['Wm2Front'])],
                                            'row_0_qabs_back': [np.mean(results['Wm2Back'])]
                                        })
                #demo.exportTrackerDict(trackerdict = demo.trackerdict, savefile = 'results\\test_reindexTrue.csv', reindex = False)
            
            else: # CumSky fixed tilt
                
                scene = demo.makeScene(simulationDict['module_type'],sceneDict)
                demo.genCumSky(demo.epwfile) # entire timeframe
                
                octfile = demo.makeOct(demo.getfilelist())  
                analysis = AnalysisObj(octfile, demo.basename)
                frontscan, backscan = analysis.moduleAnalysis(scene)
                results = analysis.analysis(octfile, demo.basename, frontscan, backscan, onlyBackscan = onlyBackscan)  
 
            
                df_reportRT_sum = pd.DataFrame({
                                            'row_0_qabs_front': [np.mean(results[0]['Wm2'])],
                                            'row_0_qabs_back': [np.mean(results[1]['Wm2'])]
                                        })
            
            df_reportRT = pd.DataFrame(columns=['row_0_qabs_front', 'row_0_qabs_back'])
            df_reportRT_sum /= hours
            
            for hour in range(hours):
                #df_reportRT = df_reportRT.append(df_reportRT_sum, ignore_index=True)
                df_reportRT = pd.concat([df_reportRT, df_reportRT_sum], ignore_index=True)
        #################
        #%% gendayLit
        else:

            ###############
            #Begin raytracing procedure and save data in pd.dataframes
            #df_rtraceFront: Dataframe with raytracing frontdata for all sensors - row-wise
            #df_rtraceBack: Dataframe with raytracing reardata for all sensors - row-wise
            #df_rtrace: All raytracing data for all sensors - row-wise
            #df_reportRT: Dataframe report to be used for electrical simulation, contains mean values for each row
 
            solpos = metdata.solpos
            solpos.reset_index(drop=True, inplace=True)
            

            def raytrace_hour(args):
                """ Ray multiprocessing function; simulates one hour with bifacial radiance"""
            # =============================================================================
            #                     Check Simulation Break Flag
            # =============================================================================
                if globals.thread_break == True:
                   print("Simulation was Stopped!")
                   raise Exception('\nSimulation was stopped by user!\n')
                
                time, SimulationDict = args
                SimulationDict['simulationName']='raytrace_'+str(time)
                
                starttime =  dtStart + datetime.timedelta(hours=time)
                starttime = starttime.strftime('%m_%d_%H')
                #endtime = starttime #+ datetime.timedelta(hours=1)
                #endtime = endtime.strftime('%m_%d_%H')
                
                demo = RayTrace.createDemo(SimulationDict, resultsPath)
                metdata = demo.readWeatherFile(weatherFile=SimulationDict['weatherFile'], starttime=starttime, endtime=starttime, label='center')
                
                if simulationDict['fixAlbedo'] ==True:
                    # Measured Albedo average fix value
                    demo.setGround(simulationDict['albedo'])
                    
                else:
                    # hourly spectral albedo or hourly measured albedo
                    if simulationDict['singleAxisTracking'] == True:
                        demo.setGround(material = None)
                    else:
                        demo.setGround(material = metdata.albedo)
                        #sys.exit("The use of hourly Measured Albedo Values is not possible with fixed tilts at the moment")
                
                if SimulationDict['singleAxisTracking'] == True:
                    
                    trackerdict = demo.set1axis(metdata = metdata, limit_angle = SimulationDict['limitAngle'], backtrack = SimulationDict['backTracking'], gcr = SimulationDict['gcr'], cumulativesky = False)
                    trackerdict = demo.gendaylit1axis()
                    trackerdict = demo.makeScene1axis(trackerdict = trackerdict, moduletype = SimulationDict['module_type'], sceneDict = sceneDict)
                    
                    demo.makeOct1axis()
                    
                    singleindex= dtStart + time*datetime.timedelta(hours=1) 
                    singleindex = singleindex.strftime('%m_%d_%H')
                
                else: #fixed tilt
                    scene = demo.makeScene(SimulationDict['module_type'],sceneDict)    
                    df = dataFrame
                    df_gendaylit= df
                    df_gendaylit = df_gendaylit.reset_index()
                    
                    sunalt = float(solpos.loc[time, 'elevation'])
                    sunaz = float(solpos.loc[time, 'azimuth'])-180
    
                    #get dhi and dni out of dataframe
                    dni = df_gendaylit.loc[time, 'dni']
                    dhi = df_gendaylit.loc[time, 'dhi']
                    
                    #simulate sky with gendaylit
                    demo.gendaylit2manual(dni, dhi, sunalt, sunaz)
                    demo.getfilelist()
                    
                    octfile = demo.makeOct(demo.getfilelist())  
                    analysis = AnalysisObj(octfile, demo.basename)
                
                df_reportRT = pd.DataFrame()
                df_rtrace = pd.DataFrame()
                
                #iterate trough rows and save data into dataframes
                for j in range(SimulationDict['nRows']):
                    # =============================================================================
                    #                     Check Simulation Break Flag
                    # =============================================================================
                    if globals.thread_break == True:
                       print("Simulation was Stopped!")
                       raise Exception('\nSimulation was stopped by user!\n')
                    
                    key_front = "row_" + str(j) + "_qinc_front"
                    key_back = "row_" + str(j) + "_qinc_back"
                    
                    df_rtraceFront  = pd.DataFrame()
                    df_rtraceBack  = pd.DataFrame()
                    
                    rowWanted = j
                    
                    #try if there is data (day) at this time or not (night)
                    try: 
                        # analyse raytracing demo per row and hour
                        if simulationDict['singleAxisTracking'] == True:
                            results_rtrace = demo.analysis1axis(customname="row_" + str(j), rowWanted = rowWanted, sensorsy = simulationDict['sensorsy'], onlyBackscan = onlyBackscan, singleindex = singleindex) 
                        
                        else: # fixed tilt
                            frontscan, backscan = analysis.moduleAnalysis(scene, rowWanted=rowWanted, sensorsy =  SimulationDict['sensorsy'])
                            results_rtrace = analysis.analysis(octfile, "row_" + str(j), frontscan, backscan, onlyBackscan = onlyBackscan)

                        if onlyBackscan == False:
                            if simulationDict['singleAxisTracking'] == True:
                                df_rtraceFront[key_front] = pd.Series(results_rtrace[singleindex]['Wm2Front'])
                                df_rtraceBack[key_back] = pd.Series(results_rtrace[singleindex]['Wm2Back'])
                            else:
                                df_rtraceFront[key_front] = pd.Series(analysis.Wm2Front) 
                                df_rtraceBack[key_back] = pd.Series(analysis.Wm2Back) 

                        else:
                            if simulationDict['singleAxisTracking'] == True:
                                df_rtraceBack[key_back] = pd.Series(results_rtrace[singleindex]['Wm2Back'])  
                            else:
                                df_rtraceBack[key_back] = pd.Series(analysis.Wm2Back)
                        
                    except: # set to NaN if no data available

                            if onlyBackscan == False:
                                df_rtraceFront = pd.DataFrame({key_front: [np.NaN]})
                                df_rtraceBack = pd.DataFrame({key_back: [np.NaN]})

                            else:
                                df_rtraceBack = pd.DataFrame({key_back: [np.NaN]})
 
                    #df_rtrace = df_rtrace.append(pd.concat([df_rtraceFront, df_rtraceBack], axis=1))     
                    df_rtrace = pd.concat([df_rtrace, pd.concat([df_rtraceFront, df_rtraceBack], axis=1)])
                    
                # calculate averages and absolute energy
                for j in range(0, simulationDict['nRows']):
                    
                    # =============================================================================
                    #                     Check Simulation Break Flag
                    # =============================================================================
                    if globals.thread_break == True:
                       print("Simulation was Stopped!")
                       raise Exception('\nSimulation was stopped by user!\n')
                    
                    key_front = "row_" + str(j) + "_qinc_front"
                    key_back = "row_" + str(j) + "_qinc_back"
                    
                    key_front_abs = "row_" + str(j) + "_qabs_front"
                    key_back_abs = "row_" + str(j) + "_qabs_back"
                    
                    
                    if onlyBackscan == False:
                        df_rtrace[key_front] = np.mean(df_rtrace[key_front])       
                        df_rtrace[key_back] = np.mean(df_rtrace[key_back])
                        
                        df_rtrace[key_front_abs] = df_rtrace[key_front] * (1-simulationDict['frontReflect'])   
                        df_rtrace[key_back_abs] = df_rtrace[key_back] * (1-simulationDict['BackReflect'])
                    else:
                        df_rtrace[key_back] = np.mean(df_rtrace[key_back])
                        df_rtrace[key_back_abs] = df_rtrace[key_back] * (1-simulationDict['BackReflect'])

 
                    df_reportRT = pd.concat([df_reportRT, df_rtrace])
                    df_reportRT = df_reportRT.mean().to_frame().T      

                return df_reportRT
            
            #%% start ray multiprocessing pool; limit CPU threads 
            cpu_threads = os.cpu_count()
            if cpu_threads >= 4:
                cpu_threads -= 2
            else:
                cpu_threads = 1
                
            pool = Pool(processes = cpu_threads)

            args_list = [(hour, simulationDict) for hour in range(hours)]
            results = pool.map(raytrace_hour, args_list)
           
            pool.close()
            pool.join() 
            
            # append POOL results to RayTracing report
            df_reportRT = pd.DataFrame()
            for result in results:
                df_reportRT = pd.concat([df_reportRT, result])
                
            # shutdown ray instance
            ray.shutdown()

        # remove .oct files from results folder
        for i in range(hours):
            singleindex= dtStart + i*datetime.timedelta(hours=1) 
            singleindex = singleindex.strftime('%m_%d_%H')
            file_path_oct = resultsPath + 'raytrace_'+ str(i) + '.oct'
            file_path_oct_tracking = '1axis_' + singleindex + '.oct'
            if os.path.isfile(file_path_oct):
                os.remove(file_path_oct)
            if os.path.isfile(file_path_oct_tracking):    
                os.remove(file_path_oct_tracking) 
        
        # Set timeindex for report        
        df_reportRT=df_reportRT.set_index(pd.date_range(start = dtStart, periods=len(df_reportRT), freq='H'))
        df_reportRT['timestamp'] = df_reportRT.index
        df_reportRT.to_csv(Path(resultsPath + "/df_reportRT.csv")  )
        if not 'corrected_timestamp' in df_reportRT.columns:
            df_reportRT['corrected_timestamp'] = pd.to_datetime(df_reportRT.index)

        return df_reportRT



class ViewFactors:
    
    """
    View class that uses the pvfactors library to simulate front and rear irradiance of the PVarray.
    Uses parameters passed into BifacialSimuu.main's simulationDict.
 
    Methods
    -------
    simulateViewFactors: Function to perform view factor simulation. Uses weather data and sun parameters from bifacial_radiance procedure, which are contained in df.

    """        
    def simulateViewFactors(simulationDict, demo, metdata, dataFrame, resultsPath, onlyFrontscan):
        """
        Function to perform hourly view factor simulation. Can simulate single axis tracking and fixed tilt.
        Can simulate only frontscan or both front and backscan. 
        
        Parameters
        ----------
        simulationDict: simulation Dictionary, which can be found in BifacialSimu_main.py
        demo: Bifacial_Radiance's RadianceObj created in "createDemo" function
        metdata: Object containing meteorological data and sun parameters
        dataFrame: DataFrame containing irradiance data and sun parameters
        resultsPath: output filepath
        onylFrontscan: option to only calculate front side of the modules
        """
        
        
        
        df = dataFrame
        print('view_factor dataframe at beginning of radiation handler:')
        print(df)
        moduley = simulationDict['moduley']*simulationDict['nModsy']
        # Pass simulation parameters over, so that pvfactors doesn't cause errors
        simulationParameter = {
        'n_pvrows': simulationDict['nRows'], #number of PV rows
        'number_of_segments': simulationDict['sensorsy'], #number of segments for each PVrow
        'pvrow_height': simulationDict['clearance_height'], #height of the PV rows, measured at their center [m]
        'pvrow_width': simulationDict['moduley'], #width of the PV panel in row, considered 2D plane [m]
        'pvmodule_width': simulationDict['modulex'], #length of the PV panel in row, considered 2D plane [m]
        'surface_azimuth': simulationDict['azimuth'], #azimuth of the PV surface [deg] 90°= East, 135° = South-East, 180°=South
        'surface_tilt': simulationDict['tilt'], #tilt of the PV surface [deg]
        'albedo': simulationDict['albedo'], # Measured Albedo average value
        #'a0': albedo, # Measured Albedo under direct illumination with a solar zenith angle of approx. 60°
        #'adiff': albedo_diff, # Measured Albedo under 100% diffuse illumination
        'C': 0.4, #Solar angle dependency factor    
        #'index_observed_pvrow': 1, #index of the PV row, whose incident irradiance will be returned
        'rho_front_pvrow' : simulationDict['frontReflect'], #front surface reflectivity of PV rows
        'rho_back_pvrow' : simulationDict['BackReflect'], #back surface reflectivity of PV rows
        'horizon_band_angle' : 6.5, #elevation angle of the sky dome's diffuse horizon band [deg]   
        'L_Position': simulationDict['longitude'], #Longitude of measurement position [deg]
        'L_Area': -105.1727827, #Longitude of timezone area [deg]
        'Latitude_Position': simulationDict['latitude'], #Latitude of measurement position [deg]
        'axis_azimuth': 0.0, #Axis Azimuth angle [deg]
        'gcr': simulationDict['gcr'], #ground coverage ratio (module area / land use)
        'x_min': -100,
        'x_max': 100,
        }
        dpi = 150 #Quality for plot export
        
        
        # Settings for calculating ViewFactor
        get_ipython().run_line_magic('matplotlib', 'qt5')
        np.set_printoptions(precision=3, linewidth=300)
        warnings.filterwarnings('ignore')
        
        # seaborn makes your plots look better
        try:
            import seaborn as sns
            sns.set(rc={"figure.figsize": (12, 6)})
            sns.set_style("darkgrid") # Other available styles: whitegrid, dark, white, ticks
            sns.set_context("paper") # Scaling the axes, also available: talk, poster, 
            sns.set_palette("muted") 
            sns.set_color_codes()
        except ImportError:
            print('We suggest you install seaborn using conda or pip and rerun this cell')
        
        irradiance_model = irradiance.HybridPerezOrdered(rho_front=simulationParameter['rho_front_pvrow'], rho_back=simulationParameter['rho_back_pvrow']) #choose an irradiance model
        # Add dictionary for discretization 
        
        rowSegments = {}
        for i in range(0, simulationParameter['n_pvrows']):
             rowSegments[i] = {'back': simulationParameter['number_of_segments']}
            
        discretization = {'cut':rowSegments}
        simulationParameter.update(discretization)

                        
        #Pick a specific day for closer data consideration
        dayUnderConsideration = 1
        
        df_inputs = df.iloc[dayUnderConsideration * 24:(dayUnderConsideration + 1) * 24, :] #rows to look at in .csv
        
        # Plot the data for displaying direct and diffuse irradiance
        print("\n Direct and Diffuse irradiance:")
        f = plt.Figure(figsize=(12, 3))
        ax1 = f.subplots(1)
        df_inputs[['dni', 'dhi']].plot(ax=ax1)
        ax1.locator_params(tight=True, nbins=6)
        ax1.set_ylabel('W/m2')
        f.savefig("Direct_Diffuse_irradiance.png", dpi = dpi)
        #plt.show()
        #not used to show Plot in own Window
        ##plt.show()(sns)
        
        # Calculate tracking angles if single axis tracking is enabled
        if simulationDict['singleAxisTracking'] == True:
            #create Single Axis Tracking dictionary with bifacialRadiance
            trackerdict = demo.set1axis(metdata = metdata, axis_azimuth = simulationDict['azimuth'],
                                        limit_angle = simulationDict['limitAngle'], 
                                        backtrack = simulationDict['backTracking'],
                                        gcr = simulationDict['gcr'], 
                                        cumulativesky = False)

            # convert trackerdict into dataframe
            d = df.from_dict(trackerdict,
                             orient='index',
                             columns=['dhi','ghi','theta','surf_tilt','surf_azm','ground_clearance'])

            d['time'] = d.index
            d.to_csv(resultsPath + 'd.csv') 

            #append variable tilt to data Frame
            df = df.reset_index()           
            df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
            df = df.set_index('time')
            
            df = df.join(d['surf_tilt'])
            
            # set time index
            dtStart = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
            df = df.set_index(pd.date_range(start = dtStart, periods=len(df), freq='H'))
            
            print('view_factor dataframe at radiation handler:')
            print(df)
        
        else:

            df = df.reset_index()
            custom_tz = dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60)
            df['time'] = df['corrected_timestamp'].dt.strftime('%Y_%m_%d_%H')
            df = df.set_index(pd.to_datetime(df['time'], format='%Y_%m_%d_%H').dt.tz_localize(custom_tz))

        ####################################################
        
        # Function to calculate variable albedo according 'PV BIFACIAL YIELD SIMULATION WITH A VARIABLE ALBEDO MODEL' from Matthieu Chiodetti et.al.
        
        def variableAlbedo(df, resultspath):
            
            # Set model parameters
            a0 = 0.22       # Measured Albedo under direct illumination with a solar zenith angle of approx. 60°
            C = 0.4            # Solar angle dependency factor  
            adiff = 0.19896735     # Measured Albedo under 100% diffuse illumination
            
            # Calculate albedo for every hour
            for index, row in df.iterrows(): 
    
                if row['ghi'] == 0: #Avoid division by 0
                    df.loc[index,'albedo'] = 0
                else:
                    df.loc[index,'albedo'] = (1 - row['dhi'] / row['ghi']) * a0 * ((1 + C)  / (1 + 2 * C * math.cos(math.radians(row['zenith'])))) + (row['dhi']  / row['ghi'] * adiff)
      
            if df.loc[index,'albedo'] < 0: #change values below 0 for yield calculation
                df.loc[index,'albedo'] = 0
        
        
            variableAlbedo = pd.DataFrame({'datetime':df.index, 'variable_Albedo': df['albedo']})
            variableAlbedo.to_csv(Path(resultspath + '/variable_Albedo.csv'), sep=';', index=False)
            
            # Plot variable albedo
            plt.rc ('axes', labelsize = 13) # Schriftgröße der x- und y-Beschriftungen
            plt.rc ('xtick', labelsize = 11) #Schriftgröße der x-Tick-Labels
            plt.rc ('ytick', labelsize = 11) #Schriftgröße der y-Tick-Labels
            plt.rc ('legend', fontsize = 11) #Schriftgröße der Legende
            f, ax = plt.subplots(figsize=(12, 4), dpi=200)
            
            variableAlbedo[['variable_Albedo']].plot(ax=ax)
            ax.set_ylabel('Variable albedo')
            ax.legend(bbox_to_anchor=(0., 1.02, 1, 0.1), loc='lower left', ncol=2, borderaxespad=0.)
            plt.ylim(0,0.4)
            #plt.show()()
        
        ####################################################
        
        # set Albedo calculation mode
        if simulationDict['fixAlbedo'] == True :
            # Measured Albedo average value, fix value
            albedo = simulationParameter['albedo']
            print("fix albedo", albedo)
       
        elif simulationDict['variableAlbedo'] == True :
            # calculated variable albedo
            variableAlbedo(df, resultsPath)
            albedo = df['albedo']  
            print("variable albedo", albedo)
        else:
            # hourly measured albedo or hourly spectral albedo
            albedo = df['albedo']  
            print("spectral albedo", albedo)
            # weatherfile must contain hourly measured albedo, if simulationDict['hourlymeasuredAlbedo'] = True
            # weatherfile contains spectral albedo, if simulationDict['hourlyspectralAlbedo'] = True
            # because spectralAlbedoHandler calculate spectral albedo and write the calculated spectral albedo in weatherfile
            # weatherfile is read in again in simulationController as df, spectralAlbedo is in df
        ####################################################
        
        #set sun parameters
        
        surface_azimuth = simulationParameter['surface_azimuth']
        
        df['zenith'] =  np.deg2rad(df.zenith)
        df['azimuth'] =  np.deg2rad(df.azimuth)
        
        if simulationDict['singleAxisTracking'] == True:
            df['surface_tilt'] = df['surf_tilt']
        else:
            df['surface_tilt'] = simulationParameter['surface_tilt']

        df['surface_azimuth'] = surface_azimuth
        
        
        #df = df.rename(columns = {'corrected timestamps': 'time'})
        
        df.to_csv(Path(resultsPath +"/Data.csv"))
        ####################################################
        
        # Run full bifacial simulation
        
        # Create ordered PV array and fit engine
        pvarray = geometry.OrderedPVArray.init_from_dict(simulationParameter)
        engine = PVEngine(pvarray)

        engine.fit(df.index, df.dni, df.dhi,
                   df.azimuth, df.zenith,
                   df.surface_tilt, df.surface_azimuth,
                   albedo)
        
              
        
        # Devide PV array into segments
        number_of_segments = {} # create empty list
        
        # Create loop for defining the number of segments
        for i in range(0, simulationParameter['n_pvrows']):
            number_of_segments[i] = len(pvarray.ts_pvrows[i].back.list_segments)
        """
        # Print Plot including Segments
        #print("\n Segment Division:")    
        f, ax = plt.subplots(figsize = (12,4))
        pvarray.plot_at_idx(1,ax,with_surface_index = True)
        ax.set_xlim(-3,20)
        #f.savefig(resultsPath +"/Segment_Division" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
        f.savefig("Segment_Division.png", dpi = dpi)
        #plt.show()(sns)
        """
        ####################################################
        #AOI reflection losses
        
        module_name = 'SunPower_128_Cell_Module___2009_'
        
        # Create an faoi function
        faoi_function = faoi_fn_from_pvlib_sandia(module_name)
        
        
        # Helper functions for plotting and simulation with reflection losses
        def plot_irradiance(df_reportVF):
        
            # Plot irradiance
            f = plt.Figure(figsize=(12, 4))
            ax = f.subplots(nrows=1, ncols=2)
            
            # Plot back surface irradiance
            df_reportVF[['qinc_back', 'qabs_back']].plot(ax=ax[0])
            ax[0].set_title('Back surface irradiance')
            ax[0].set_ylabel('W/m2')
            
            # Plot front surface irradiance
            df_reportVF[['qinc_front', 'qabs_front']].plot(ax=ax[1])
            ax[1].set_title('Front surface irradiance')
            ax[1].set_ylabel('W/m2')
            #plt.show()()
            
            
        ##### Without backscan #####   
        def plot_irradiance_front(df_reportVF):
            
                
            # Plot irradiance
            f = plt.Figure(figsize=(12, 4))
            ax = f.subplots()
                    
            # Plot front surface irradiance
            df_reportVF[['qinc_front', 'qabs_front']].plot(ax=ax)
            ax.set_title('Front surface irradiance')
            ax.set_ylabel('W/m2')
            #plt.show()()
        
        
        def plot_aoi_losses(df_reportVF):
                # plotting AOI losses
                f = plt.Figure(figsize=(5.5, 4))
                ax = f.subplots()
                df_reportVF[['aoi_losses_back_%']].plot(ax=ax)
                df_reportVF[['aoi_losses_front_%']].plot(ax=ax)
                
                # Adjust axes
                ax.set_ylabel('%')
                ax.legend(['AOI losses back PV row', 'AOI losses front PV row'])
                ax.set_title('AOI losses')
                #plt.show()()
        
        
        ##### Without backscan #####
        def plot_aoi_losses_front(df_reportVF):
            
            # plotting AOI losses
            f = plt.Figure(figsize=(5.5, 4))
            ax = f.subplots()
            df_reportVF[['aoi_losses_front_%']].plot(ax=ax)
            
            # Adjust axes
            ax.set_ylabel('%')
            ax.legend(['AOI losses front PV row'])
            ax.set_title('AOI losses')
            #plt.show()()
            
           
            
        # Create a function that will build a simulation report      
        def fn_report(pvarray):
            if simulationDict['nRows']==1:
                n = 0
            else:
                n = 1        
            reportAOI = {'qinc_back': pvarray.ts_pvrows[n].back.get_param_weighted('qinc'),
                      'qabs_back': pvarray.ts_pvrows[n].back.get_param_weighted('qabs'),
                      'qinc_front': pvarray.ts_pvrows[n].front.get_param_weighted('qinc'),
                      'qabs_front': pvarray.ts_pvrows[n].front.get_param_weighted('qabs')}
            
            # Calculate AOI losses
            reportAOI['aoi_losses_back_%'] = (reportAOI['qinc_back'] - reportAOI['qabs_back']) / reportAOI['qinc_back'] * 100.
            reportAOI['aoi_losses_front_%'] = (reportAOI['qinc_front'] - reportAOI['qabs_front']) / reportAOI['qinc_front'] * 100.
            # Return report
            return reportAOI
            
        ##### Without backscan #####
        def fn_report_front(pvarray):
            # Get irradiance values
            if simulationDict['nRows']==1:
                n = 0
            else:
                n = 1
            reportAOI = {
                      'qinc_front': pvarray.ts_pvrows[n].front.get_param_weighted('qinc'),
                      'qabs_front': pvarray.ts_pvrows[n].front.get_param_weighted('qabs')}
            
            # Calculate AOI losses
            
            reportAOI['aoi_losses_front_%'] = (reportAOI['qinc_front'] - reportAOI['qabs_front']) / reportAOI['qinc_front'] * 100.
            
            
            # Return report
            return reportAOI
        
        # Run full mode simulation
            
        if onlyFrontscan == False:
            reportAOI = engine.run_full_mode(fn_build_report=fn_report)
            df_report_AOI = pd.DataFrame(reportAOI, index=df.index)
            plot_irradiance(df_report_AOI)
            
            
        else:
            reportAOI = engine.run_full_mode(fn_build_report=fn_report_front)
            df_report_AOI = pd.DataFrame(reportAOI, index=df.index)
            plot_irradiance_front(df_report_AOI)
        
        
        
        
        ####################################################
        # Define Function calculating the total incident irradiance for the front and back side and the different segments of the backside
        
        # qinc = total incident irradiance on a surface, and it does not account for reflection losses [W/m2]
        # qabs = total absorbed irradiance by a surface [W/m2]
        
        #ts=timeseries 
        
        
              
        def Segments_report(pvarray):
            result = dict()
            
            rowsum_qabs_front = 0
            rowsum_qabs_back = 0
            rowsum_qinc_front = 0
            rowsum_qinc_back = 0
            
            for i in range(0, len(pvarray.ts_pvrows)):
                
                row = pvarray.ts_pvrows[i]
                
                #result["row_" + str(i) + "_reflection_front"] = row.front.get_param_weighted('reflection') #avg reflection for every row front
                #result["row_" + str(i) + "_reflection_back"] = row.back.get_param_weighted('reflection') #avg reflection for every row back
                result["row_" + str(i) + "_qinc_front"] = row.front.get_param_weighted('qinc') #avg qinc for every row front
                result["row_" + str(i) + "_qinc_back"] = row.back.get_param_weighted('qinc') #avg qinc for every row back
                result["row_" + str(i) + "_qabs_front"] = row.front.get_param_weighted('qabs') #avg qabs for every row front
                result["row_" + str(i) + "_qabs_back"] = row.back.get_param_weighted('qabs') #avg qabs for every row back
                #result["row_" + str(i) + "_q0_front"] = row.front.get_param_weighted('q0') #avg reflection for every row front
                #result["row_" + str(i) + "_q0_back"] = row.back.get_param_weighted('q0') #avg reflection for every row back
                #result["row_" + str(i) + "_isotropic_front"] = row.front.get_param_weighted('isotropic') #avg reflection for every row front
                #result["row_" + str(i) + "_isotropic_back"] = row.back.get_param_weighted('isotropic') #avg reflection for every row back              
                
                for ts_surface in row.front.all_ts_surfaces:
                    key = "qabs_segment_" + str(ts_surface.index)  # updated
                    result[key] = ts_surface.get_param('qabs')
                 
                for ts_surface in row.back.all_ts_surfaces:
                    key = "qabs_segment_" + str(ts_surface.index)  # updated
                    result[key] = ts_surface.get_param('qabs')
                    
                for ts_surface in row.front.all_ts_surfaces:
                    key = "qinc_segment_" + str(ts_surface.index)  # updated
                    result[key] = ts_surface.get_param('qinc')
                  
                for ts_surface in row.back.all_ts_surfaces:
                    key = "qinc_segment_" + str(ts_surface.index)  # udpated
                    result[key] = ts_surface.get_param('qinc')
                
                rowsum_qabs_front += row.front.get_param_weighted('qabs')
                rowsum_qabs_back += row.back.get_param_weighted('qabs')
                rowsum_qinc_front += row.front.get_param_weighted('qinc')
                rowsum_qinc_back += row.back.get_param_weighted('qinc')
                
            result["row_avg_qabs_front"] = rowsum_qabs_front / simulationDict['nRows']
            result["row_avg_qabs_back"] = rowsum_qabs_back / simulationDict['nRows']
            result["row_avg_qinc_front"] = rowsum_qinc_front / simulationDict['nRows']
            result["row_avg_qinc_back"] = rowsum_qinc_back / simulationDict['nRows']
            
            return result
               
        def Segments_report_front(pvarray):
            result = dict()
            
            for i in range(0, len(pvarray.ts_pvrows)):
                
                row = pvarray.ts_pvrows[i]
                
                result["row_" + str(i) + "_qabs_front"] = row.front.get_param_weighted('qabs') #avg qabs for every row front
                result["row_" + str(i) + "_qinc_front"] = row.front.get_param_weighted('qinc') #avg qinc for every row front
                
                
                for ts_surface in row.front.all_ts_surfaces:
                    key = "qabs_segment_" + str(ts_surface.index)  # updated
                    result[key] = ts_surface.get_param('qabs')
                 
                            
                for ts_surface in row.front.all_ts_surfaces:
                    key = "qinc_segment_" + str(ts_surface.index)  # updated
                    result[key] = ts_surface.get_param('qinc')
                  
                                   
        # Display length of every segment
                #for ts_surface in row.front.all_ts_surfaces:
                 #   key = "segment_" + str(ts_surface.index) + "length" # all shaded timeseries surfaces on the front side of the PV row have length zero.
                  #  result[key] = ts_surface.length.tolist()
                    
                #for ts_surface in row.back.all_ts_surfaces:
                 #   key = "segment_" + str(ts_surface.index) + "length"
                  #  result[key] = ts_surface.length.tolist()
                    
        # Display if segments are shaded or not            
        #        for ts_surface in row.front.all_ts_surfaces:
        #            key = "segment_" + str(ts_surface.index) + "shaded"
        #            result[key] = ts_surface.shaded.tolist()
                    
        #        for ts_surface in row.back.all_ts_surfaces:
        #            key = "segment_" + str(ts_surface.index) + "shaded"
        #            result[key] = ts_surface.shaded.tolist()    
            
            return result
        
        ####################################################
        
        # function to average the hourly front and back irradiances of the pv rows to daily values
        # only possible, when the starthour and endhour is 0 o'clock, so whole days are simulated
        # otherwise, the loop has to be programmed, that it checks, if there are less than 24 hour for a day and reduces the loops the the acutal hours in the first or last day
        
        def daily_mean_irradiance(df_reportVF):
            df1 = df_reportVF  

            Avg_front_daily = []     # array to hold daily row average qabs front values
            Avg_back_daily = []      # array to hold daily row average qabs back values
            Row_0_front_daily = []   # array to hold daily qabs front values of row 0
            Row_1_front_daily = []   # array to hold daily qabs front values of row 1
            Row_2_front_daily = []   # array to hold daily qabs front values of row 2
            Row_0_back_daily = []   # array to hold daily qabs back values of row 0
            Row_1_back_daily = []   # array to hold daily qabs back values of row 1
            Row_2_back_daily = []   # array to hold daily qabs back values of row 2
            cd = []             # array to hold hourly datetime

            
            dtStart = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
            dtEnd = datetime.datetime(simulationDict['endHour'][0], simulationDict['endHour'][1], simulationDict['endHour'][2], simulationDict['endHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))#- datetime.timedelta(minutes=60)
            
            delta_days= dtEnd - dtStart

            for i in range(delta_days.days):
                
                Avg_front_hourly = []     # array to hold hourly row average qabs front values
                Avg_back_hourly = []     # array to hold hourly row average qabs front values
                Row_0_front_hourly = []   # array to hold hourly qabs front values of row 0
                Row_1_front_hourly = []   # array to hold hourly qabs front values of row 1
                Row_2_front_hourly = []   # array to hold hourly qabs front values of row 2
                Row_0_back_hourly = []   # array to hold hourly qabs back values of row 0
                Row_1_back_hourly = []   # array to hold hourly qabs back values of row 1
                Row_2_back_hourly = []   # array to hold hourly qabs back values of row 2
                
                currentDate = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))+ pd.to_timedelta(i, unit='D')
                
                for j in range(24):
                    
                    k = i*24 + j
                    
                    Avg_front = df1.iloc[k]['row_avg_qabs_front']    
                    Avg_back = df1.iloc[k]['row_avg_qabs_back'] 
                    Row_0_front = df1.iloc[k]['row_0_qabs_front'] 
                    Row_1_front = df1.iloc[k]['row_1_qabs_front'] 
                    Row_2_front = df1.iloc[k]['row_2_qabs_front'] 
                    if simulationDict['simulationMode'] ==4:
                        Row_0_back = 0
                        Row_1_back = 0
                        Row_2_back = 0    
                    else:
                        Row_0_back = df1.iloc[k]['row_0_qabs_back'] 
                        Row_1_back = df1.iloc[k]['row_1_qabs_back'] 
                        Row_2_back = df1.iloc[k]['row_2_qabs_back']
                               
                    if Avg_front == 0:
                        Avg_front = np.nan
                    if Avg_back == 0:
                        Avg_back = np.nan
                    if Row_0_front == 0:
                        Row_0_front = np.nan
                    if Row_1_front == 0:
                        Row_1_front = np.nan
                    if Row_2_front == 0:
                        Row_2_front = np.nan
                    if Row_0_back == 0:
                        Row_0_back = np.nan
                    if Row_1_back == 0:
                        Row_1_back = np.nan
                    if Row_2_back == 0:
                        Row_2_back = np.nan
                        
                    Avg_front_hourly.append(Avg_front)
                    Avg_back_hourly.append(Avg_back)
                    Row_0_front_hourly.append(Row_0_front)
                    Row_1_front_hourly.append(Row_1_front)
                    Row_2_front_hourly.append(Row_2_front)
                    Row_0_back_hourly.append(Row_0_back)
                    Row_1_back_hourly.append(Row_1_back)
                    Row_2_back_hourly.append(Row_2_back)
                    

                Avg_front_mean = np.nanmean(Avg_front_hourly)      # mean value of 24 hourly values without nan values
                Avg_back_mean = np.nanmean(Avg_back_hourly)        # mean value of 24 hourly values without nan values
                Row_0_front_mean = np.nanmean(Row_0_front_hourly)  # mean value of 24 hourly values without nan values         
                Row_1_front_mean = np.nanmean(Row_1_front_hourly)  # mean value of 24 hourly values without nan values         
                Row_2_front_mean = np.nanmean(Row_2_front_hourly)  # mean value of 24 hourly values without nan values         
                Row_0_back_mean = np.nanmean(Row_0_back_hourly)    # mean value of 24 hourly values without nan values         
                Row_1_back_mean = np.nanmean(Row_1_back_hourly)    # mean value of 24 hourly values without nan values         
                Row_2_back_mean = np.nanmean(Row_2_back_hourly)    # mean value of 24 hourly values without nan values         
                
                Avg_front_daily.append(Avg_front_mean)
                Avg_back_daily.append(Avg_back_mean)
                Row_0_front_daily.append(Row_0_front_mean)
                Row_1_front_daily.append(Row_1_front_mean)
                Row_2_front_daily.append(Row_2_front_mean) 
                Row_0_back_daily.append(Row_0_back_mean)
                Row_1_back_daily.append(Row_1_back_mean)
                Row_2_back_daily.append(Row_2_back_mean)
                
                cd.append(currentDate)          # append the currentDate to cd array
            
            # create pandas dataframe to save the four arrays and give them headers
            df2 = pd.DataFrame({'datetime':cd, 'Average front surface irradiance': Avg_front_daily, 'Average rear surface irradiance': Avg_back_daily, 'Front surface irradiance row 1':Row_0_front_daily, 'Front surface irradiance row 2':Row_1_front_daily,'Front surface irradiance row 3':Row_2_front_daily,'Rear surface irradiance row 1':Row_0_back_daily, 'Rear surface irradiance row 2':Row_1_back_daily, 'Rear surface irradiance row 3':Row_2_back_daily})
            df2.set_index('datetime')
            return df2
        
        def plot_irradiance1(df2):
            # Plot average surface irradiance (qabs)
            
            plt.rc ('axes', labelsize = 13) # Schriftgröße der x- und y-Beschriftungen
            plt.rc ('xtick', labelsize = 11) #Schriftgröße der x-Tick-Labels
            plt.rc ('ytick', labelsize = 11) #Schriftgröße der y-Tick-Labels
            plt.rc ('legend', fontsize = 11) #Schriftgröße der Legende
            fig = plt.Figure(figsize=(12, 4), dpi=200)
            ax = fig.subplots()
            width = 1
                       
            y1 = df2['Average front surface irradiance']
            y2 = df2['Average rear surface irradiance']
            ind = range(len(y1))
            ax.bar(ind, y1, width, label='Average front surface irradiance', linewidth=0)
            ax.bar(ind, y2, width, bottom=y1, label='Average rear surface irradiance', linewidth=0)
            
            ax.set_ylabel('Average surface irradiance in $\mathregular{W/m^2}$')
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax.legend(bbox_to_anchor=(0., 1.02, 1, 0.1), loc='lower left', ncol=2, borderaxespad=0.)
            #plt.xlim(0,len(y1)-1)
            
            
            #plt.show()()
            
            
        def plot_irradiance2(df2):
            # Plot surface irradiance for every row
            fig = plt.Figure(figsize=(12, 4), dpi=200)
            ax = fig.subplots()
            
            width = 1
                       
            y1 = df2['Rear surface irradiance row 1']
            y2 = df2['Rear surface irradiance row 2']
            y3 = df2['Rear surface irradiance row 3']
            ind = range(len(y1))
            ax.bar(ind, y1, width, label='Rear surface irradiance row 1', linewidth=0)
            ax.bar(ind, y2, width, label='Rear surface irradiance row 2', linewidth=0)
            ax.bar(ind, y3, width, label='Rear surface irradiance row 3', linewidth=0)
            
            ax.xaxis.set_major_locator(mdates.MonthLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b'))
            ax.legend(bbox_to_anchor=(0., 1.02, 1, 0.1), loc='lower left', ncol=3, borderaxespad=0.)
            ax.set_ylabel('Rear surface irradiance in $\mathregular{W/m^2}$')
            #plt.xlim(0,len(y1)-1)
            #plt.show()()
        
        
        # Run full simulation
            
        if onlyFrontscan == False:
            report = engine.run_full_mode(fn_build_report=Segments_report)
            df_reportVF = pd.DataFrame(report, index=df.index)
            df2 = daily_mean_irradiance(df_reportVF)  # erzeugt dataframe mit gemittelten täglichen irradiances
            plot_irradiance1(df2)    # Plot mit der durschnittlichen front und back irradiance aller Reihen für jeden Tag
            plot_irradiance2(df2)    # Plot mit der front und back irradiance für jede Reihen für jeden Tag
            
            # Print results as .csv in directory
            df_reportVF.to_csv(Path(resultsPath + "radiation_qabs_results.csv"))
            """
            # Plot total qinc front and back for every row
            f, ax = plt.subplots(3, figsize=(10, 6))
            ax.locator_params(tight=True, nbins=5)
            df_reportVF[['row_0_qinc_front', 'row_0_qinc_back']].plot(ax=ax[0])
            df_reportVF[['row_1_qinc_front', 'row_1_qinc_back']].plot(ax=ax[1])
            df_reportVF[['row_2_qinc_front', 'row_2_qinc_back']].plot(ax=ax[2])
            ax[0].set_ylabel('W/m2')
            ax[1].set_ylabel('W/m2')
            ax[2].set_ylabel('W/m2')
            #f.savefig("row0-3_qinc.png", dpi = dpi)
            #plt.show()(sns)
            """
            
            
        else:
            report = engine.run_full_mode(fn_build_report=Segments_report_front)
            
            # Print results as .csv in directory
            df_reportVF = pd.DataFrame(report, index=df.index)
            df_reportVF.to_csv("radiation_qabs_results.csv")
            
            """
            # Plot total qinc front and back for every row
            f, ax = plt.subplots(3, figsize=(10, 6))
            ax.locator_params(tight=True, nbins=5)
            df_reportVF[['row_0_qinc_front']].plot(ax=ax[0])
            df_reportVF[['row_1_qinc_front']].plot(ax=ax[1])
            df_reportVF[['row_2_qinc_front']].plot(ax=ax[2])
            ax[0].set_ylabel('W/m2')
            ax[1].set_ylabel('W/m2')
            ax[2].set_ylabel('W/m2')
            f.savefig("row0-3_qinc.png", dpi = dpi)
            #plt.show()(sns)
            """
        
        dtStart = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
        

        df = df.set_index(pd.date_range(start = dtStart, periods=len(df), freq='H'))
        df_reportVF = df_reportVF.set_index(pd.date_range(start = dtStart, periods=len(df), freq='H'))

        if 'timestamp' not in df_reportVF.columns:
            df_reportVF['timestamp'] = df_reportVF.index
        if 'corrected_timestamp' not in df_reportVF.columns:
            df_reportVF['corrected_timestamp'] = df_reportVF.index
        
        
        print("df_reportVF at end of RadiationHandler: ")
        print(df_reportVF)

        #df_reportVF.to_csv(resultsPath + "/radiation_qabs_results_" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
        
        #f.savefig(resultsPath +"/row0-3_qinc" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
                
        ####################################################
        # Calculate ViewFactors for Day of Consideration
        
        # Instantiate calculator
        vf_calculator = viewfactors.VFCalculator()
        
        # Calculate view factor matrix of the pv array
        vf_matrix = vf_calculator.build_ts_vf_matrix(pvarray)
               
        # Create ViewFactor matrix 
        def save_view_factor(i, j, vf_matrix, timestamps):
            
            vf = vf_matrix[i, j, :]
            matrix = np.around(vf, decimals=2)
            
            result = pd.DataFrame()
            
            # Print table with timestamps and ViewFactors
            result["timestamps"] = timestamps
            result["view_factors"] = matrix.tolist()
            
            result = result.set_index('timestamps')
            
            #result.to_csv(resultsPath + "/view_factors_" + str(i) + "_" + str(j) + "_" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv") # Print ViewFactors to directory
            result.to_csv("view_factors_" + str(i) + "_" + str(j) + ".csv")
            #print("\n View Factors:")
            #print('View factor from surface {} to surface {}: {}'.format(i, j, np.around(vf, decimals=2))) # in case the matrix should be printed in the console
            return result
        
        view_factors_results = save_view_factor(4, 12, vf_matrix, df.index)
        
        
        #f = plt.Figure(figsize=(10, 3))
        #ax = f.subplots()
        #pvarray.plot_at_idx(0, ax, with_surface_index=True)
        #plt.show()()
        
        return df_reportVF, df, view_factors_results