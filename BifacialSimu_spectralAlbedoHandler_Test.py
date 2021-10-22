# -*- coding: utf-8 -*-
'''
!!!!!!!!!!!
Vorm nächsten Ausprobieren alle def Funktionen neu reinkopieren
!!!!!!!!!!!
'''
"""
Created on Wed Sep 15 17:53:38 2021

@author: Sarah Glaubitz

name: BifacialSimu - spectralAlbedoHandler

overview:
    Calculation of spectral Albedo regarding the paper 
    "A Comprehensive Albedo Model for Solar Energy Applications: Geometric Spectral Albedo"
    from Hesan Ziar, Furkan Fatih Sönmez, Olindo Isabella, and Miro Zeman; October 2019
    
last changes:
    15.09.2021 created
"""

import pandas as pd
from pvlib import spectrum, solarposition, irradiance, atmosphere
import os
import numpy
import matplotlib.pyplot as plt
import math
import dateutil.tz
import datetime
import numpy as np

rootPath = os.path.realpath(".")

SimulationDict = {
'simulationName' : 'NREL_best_field_row_2',
'simulationMode' : 1, 
'localFile' : True, # Decide wether you want to use a  weather file or try to download one for the coordinates
'weatherFile' : (rootPath +'/WeatherData/Cologne_Germany/Cologne_Bibdach_50.935_6.992_TMY_2007_2016'), # weather file in TMY format 
'spectralReflectancefile' : (rootPath + '/ReflectivityData/interpolated_reflectivity.csv'),
'cumulativeSky' : False, # Mode for RayTracing: CumulativeSky or hourly
'startHour' : (2009, 1, 1, 0),  # Only for hourly simulation, yy, mm, dd, hh
'endHour' : (2009, 1, 2, 23),  # Only for hourly simulation, yy, mm, dd, hh
'utcOffset': 0,
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
'hourlyMeasuredAlbedo' : True, # True if measured albedo values in weather file
'spectralAlbedo' : True, # Option to calculate a spectral Albedo 
'albedo' : 0.282, # Measured Albedo average value, if hourly isn't available
'frontReflect' : 0.03, #front surface reflectivity of PV rows
'BackReflect' : 0.05, #back surface reflectivity of PV rows
'longitude' : 6.992, 
'latitude' : 50.935,
'gcr' : 0.35, #ground coverage ratio (module area / land use)
'module_type' : 'NREL row 2', #Name of Module
}

def getReflectanceData(simulationDict):
    '''
    Read the spectral reflectance data of the material (sand); R(lamda)
    
    Parameters
    ----------
    simulationDict: simulation Dictionary, which can be found in GUI.py
    
    Returns
    -------
    R_lamda: array of reflectvity values
    '''
    
    # array with reflectivity values, only colume 2 of the csv is read
    R_lamda = numpy.genfromtxt(simulationDict['spectralReflectancefile'], delimiter=';', skip_header = 1, usecols=(1))
   
    return R_lamda
    
def modelingSpectralIrradiance(simulationDict, dataFrame, j):
    '''
    Model the spectral distribution of irradiance based on atmospheric conditions. 
    The spectral distribution of irradiance is the power content at each wavelength 
    band in the solar spectrum and is affected by various scattering and absorption 
    mechanisms in the atmosphere.
    
    based on SPECTRL2 NREL Technical Report:
    Bird, R, and Riordan, C., 1984, "Simple solar spectral model for direct and 
    diffuse irradiance on horizontal and tilted planes at the earth's surface 
    for cloudless atmospheres", NREL Technical Report TR-215-2436 
    doi:10.2172/5986936.
    
    Parameters
    ----------
    simulationDict: simulation Dictionary, which can be found in GUI.py
    currentDate: date and time in datetime format for solarposition calculation
    dataFrame: pandas dataframe, which contains the weather data
    j: current loop number, which represent the hour after starthour
    
    Returns
    -------
    spectra: dict of arrays with wavelength; dni_extra; dhi; dni; poa_sky_diffuse; poa_ground_diffuse; poa_direct; poa_global
    '''
       
    df = dataFrame
     
    #lat = simulationDict['latitude']       # [deg] latitude of ground surface to calculate spectral albedo
    #lon = simulationDict['longitude']      # [deg] longitude of ground surface to calculate spectral albedo
    tilt = 0                                # [deg] always 0, because the ground is never tilted
    azimuth = simulationDict['azimuth']     # [deg] same azimuth for ground surface as for PV panel
    pressure = (df.iloc[j]['pressure']*100) # [Pa] air pressure; df value is in mbar so multiplied by 100 to Pa
    print('pressure', pressure)
    water_vapor_content = 1.551             # [cm] Atmospheric water vapor content; data from AERONET for FZ Juelich for Sep 2021; Level 2 Quality
    tau500 = 0.221                          # [-] aerosol optical depth at wavelength 500 nm; data from AERONET for FZ Juelich for Sep 2021; Level 2 Quality
    ozone = 0.314                           # [atm-cm] Atmospheric ozone content; data from WOUDC for Aug 2021 for Hohenpeissenberg
    albedo = simulationDict['albedo']       # [-] fix albedo value
    
    # Attention: apparent_zenith is greater than 90 deg for night time
    apparent_zenith = df.iloc[j]['apparent_zenith']  # [deg] zenith angle of solar radiation
    print('zenit', apparent_zenith)
    sun_azimuth = df.iloc[j]['azimuth'] # [deg] azimith angle of solar radiation
    print('azimuth', sun_azimuth)
    currentDate = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3]) + pd.to_timedelta(j, unit='H')  # current date and time to calculate spectrum for           
    print(currentDate)
    doy = int(currentDate.strftime('%j'))        # getting day of year out of the current date

    
    # Attention: Works only with positiv utcOffset values of simulationDict; Workaround: use only positiv utcOffset
    #times = pd.date_range(start=cd, freq='h', periods=1, tz='Etc/GMT+' + str(simulationDict['utcOffset'])) # posibility to calculate several spectras for diffrent times, when period >1
    #print(times)
    # Attention: solpos.apparent_zenith is greater than 90 deg for night time
    #solpos = solarposition.get_solarposition(times, lat, lon)
    #print(solpos.apparent_zenith)
    #print(solpos.elevation)
    
    aoi = irradiance.aoi(tilt, azimuth, apparent_zenith, sun_azimuth) # always equal to solpos_apparent_zenith, because tilt = 0° 
    
    # The technical report uses the 'kasten1966' airmass model, but later versions of SPECTRL2 use 'kastenyoung1989'.
    # Attention: returns NaN values, if apparent_zenith is greater than 90 deg
    relative_airmass = atmosphere.get_relative_airmass(apparent_zenith, model='kastenyoung1989')
    print('airmass', relative_airmass)
    '''
    modeling spectral irradiance using `pvlib.spectrum.spectrl2`
    The poa_global array represents the total spectral irradiance on the ground surface
    Note: With the exception of wavelength, which has length 122, each array has shape (122, N)
          where N is the length of the input apparent_zenith
    '''
    spectra = spectrum.spectrl2(
        apparent_zenith=apparent_zenith,
        aoi=aoi,
        surface_tilt=tilt,
        ground_albedo=albedo,
        surface_pressure=pressure,
        relative_airmass=relative_airmass,
        precipitable_water=water_vapor_content,
        ozone=ozone,
        aerosol_turbidity_500nm=tau500,
        dayofyear=doy,                        # is needed, if apparent_zenith isn't a pandas series
    )
   
    # plot: modeled poa_global against wavelength (like Figure 5-1A from the SPECTRL2 NREL Technical Report)
    #plt.figure()
    #plt.plot(spectra['wavelength'], spectra['poa_global'])
    #plt.xlim(200, 2700)
    #plt.ylim(0, 1.8)
    #plt.title(r"Day 80 1984, $\tau=0.1$, Wv=0.5 cm")
    #plt.ylabel(r"Irradiance ($W m^{-2} nm^{-1}$)")
    #plt.xlabel(r"Wavelength ($nm$)")
    #time_labels = times.strftime("%H:%M %p")
    #labels = [
    #    "AM {:0.02f}, Z{:0.02f}, {}".format(*vals)
    #    for vals in zip(relative_airmass, solpos.apparent_zenith, time_labels)
    #    ]
    #plt.legend(labels)
    #plt.show()
    
    '''
    Note that the airmass and zenith values do not exactly match the values in
    the technical report; this is because airmass is estimated from solar
    position and the solar position calculation in the technical report does not
    exactly match the one used here.  However, the differences are minor enough
    to not materially change the spectra.
    '''
    return spectra
    
    
def calculateAlbedo(simulationDict, dataFrame):
    '''
    Calculates R value for every hour in the time period between startHour and endHour
    Calculates H value for every hour in the time period between startHour and endHour
    Calculates a value (Albedo) for every hour in the time period between startHour and endHour
        
    Parameters
    ----------
    simulationDict: simulation Dictionary, which can be found in GUI.py
    dataFrame: pandas dataframe, which contains the weather data
    
    TODO: Ich muss den dataframe 'df' aus der Funktion 'startSimulation' aus simualtionController.py irgendwie übergeben bekommen.
    TODO: Eventuell über den radiationHandler möglich, da der df an die Funktion simulateRaytrace und simulateViewFactors übergeben wird
    
    Returns
    -------
    a_hourly: array with Albedo value for every hour in the time period between startHour and endHour
    '''
    df = dataFrame
        
    # Translate startHour und endHour in timeindexes
    dtStart = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
    #beginning_of_year = datetime.datetime(dtStart.year, 1, 1, tzinfo=dtStart.tzinfo)
    #startHour = int((dtStart - beginning_of_year).total_seconds() // 3600) # gives the hour in the year
                
    dtEnd = datetime.datetime(simulationDict['endHour'][0], simulationDict['endHour'][1], simulationDict['endHour'][2], simulationDict['endHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
    #beginning_of_year = datetime.datetime(dtEnd.year, 1, 1, tzinfo=dtEnd.tzinfo)
    #endHour = int((dtEnd - beginning_of_year).total_seconds() // 3600) # gives the hour in the year
    
    timedelta = int((dtEnd - dtStart).total_seconds() //3600) + 1       # +1, so that endHour also runs through the loop
    
    # Intialise arrays
    R_hourly = []     # array to hold R value
    H_hourly = []     # array to hold H value
    a_hourly = np.array()     # array to hold albedo
    print('a_hourly',a_hourly)
    '''
    Loop to calculate R, H and Albdeo for every hour. 
    Start value is 0, end value is the number of hours between starthour and endhour of the calculation period. 
    The starthour has to be the same as in the dataFrame. The increment is one hour.
    '''
    
    for j in range(timedelta):
                        
        spectrum = modelingSpectralIrradiance(simulationDict, dataFrame, j) # 8D array from the function modelingSpectralIrradiance is created
        R_lamda_array = getReflectanceData(simulationDict) # 1D array from the function getReflectanceData is created
        
        sum_R_G = 0
        sum_G = 0
                
        for i in range(112): # 112 loops (0<=i<=111), because of 112 wavelenghts in spectra, which are used for calculation (only to 3000 nm, because R values reaches only to 3000 nm)
            
            '''
            Attention: 
            - G_lamda is an array (no problem, but not nice)
            - G_lamda (= 'poa_global' colume of the array 'spectrum') gives NaN values for nigth time instead of 0,
              because the input parameter 'relative_airmass' of 'spectra' in the function 'modelingSpectralIrradiance' 
              is a NaN value for night time, because apperent_zenith is greater than 90 deg
            '''
            G_lamda = spectrum['poa_global'][i] # G for current number of wavelength i [W/m²/nm]  
            G_lamda2 = G_lamda[0]               # gets G out of the array (with contains only one value)
            R_lamda = R_lamda_array[i]          # R for current number of wavelength i [-]
            lamda = spectrum['wavelength'][i]   # current wavelength i [nm]
                              
            sum_R_G += (G_lamda2 * R_lamda * lamda) # sum up the multiplication of R, G and lamda for every wavelength [W/m²]
            sum_G += (G_lamda2 * lamda)             # sum up multiplication of G and lamda for every wavelength [W/m²]
        
        
        # Calcualte R value
        
        # Check, if sum_G is 0 or Nan, so that sum_R_G is not divided by 0 or NaN
        if sum_G == 0 or pd.isna(sum_G): # NaN values only for night time (see comment above)
            R = 0       
        else:
            R = sum_R_G / sum_G
        print('R', R)
        R_hourly.append(R)
        
        
        # Calculates H value
               
        DNI = df.iloc[j]['dni']                     # direct normal irradiation out of dataframe (which comes from weatherfile) [W/m²]
        print('DNI', DNI)
        DHI = df.iloc[j]['dhi']                     # diffuse horizontal irradation out of dataframe (which comes from weatherfile) [W/m²]
        print('DHI', DHI)
        theta = math.radians(df.iloc[j]['zenith'])  # sun zenith angle out of dataframe[rad]
        print('theta', theta)
        # Check, if DHI is 0, so that DNI is not divided by 0
        if DHI == 0:
            H = 0
        elif theta > (0.5*math.pi):   # 0.5*pi rad = 90 deg
            H = 0
        else:
            H = (DNI/DHI) * math.cos(theta)
        print('H', H)
        H_hourly.append(H)
        
        '''
        # Calculate Albedo
        # TODO: Viewfactor übergeben
        VF_s_a1 # Viewfactor from surface S (Albedo measurement) to surface A1 (unshaded ground)
        VF_s_a2 # Viewfactor from surface S (Albedo measurement) to surface A2 (shaded ground)
        
        a = R * (VF_s_a1 + (1/(H+1)) * VF_s_a2) # Albedo [-]
        
        a_hourly.append(a)
        '''
    print(R_hourly)
    print(H_hourly)
  
    
df = pd.read_csv('Dataframe_df_Cologne.csv')
#print (df['ghi'])
#print (df['dhi'])
#print (df['dni'])

calculateAlbedo(SimulationDict, df)
#print(test)    

