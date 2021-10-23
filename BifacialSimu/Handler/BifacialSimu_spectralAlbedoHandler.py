# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 17:53:38 2021

@author: Sarah Glaubitz

name: BifacialSimu - spectralAlbedoHandler

overview:
    Calculation of spectral Albedo regarding the paper: 
    "A Comprehensive Albedo Model for Solar Energy Applications: Geometric Spectral Albedo"
    from Hesan Ziar, Furkan Fatih Sönmez, Olindo Isabella, and Miro Zeman; October 2019
    
last changes:
    15.09.2021 created
"""

import pandas as pd
from pvlib import spectrum, solarposition, irradiance, atmosphere
import os
import numpy as np
import matplotlib.pyplot as plt
import math
import dateutil.tz
import datetime
import pvfactors
import csv

import BifacialSimu_dataHandler
import BifacialSimu_radiationHandler



def getReflectivityData(simulationDict):
    '''
    Read the spectral reflectance data of the material (sand); R(lamda)
    
    Parameters
    ----------
    simulationDict: simulation Dictionary, which can be found in GUI.py
    
    Returns
    -------
    R_lamda: array of reflectvity values
    '''
    
    # numpy array with reflectivity values, only colume 2 of the csv is read
    R_lamda = np.genfromtxt(simulationDict['spectralReflectancefile'], delimiter=';', skip_header = 1, usecols=(1))
   
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
    dataFrame: pandas dataframe, which contains the weather data
    j: current loop number, which represent the hour after starthour
    
    Returns
    -------
    spectra: dict of arrays with wavelength; dni_extra; dhi; dni; poa_sky_diffuse; poa_ground_diffuse; poa_direct; poa_global
    '''
       
    df = dataFrame
     
    tilt = 0                                # [deg] always 0, because the ground is never tilted
    azimuth = simulationDict['azimuth']     # [deg] same azimuth for ground surface as for PV panel
    pressure = (df.iloc[j]['pressure']*100) # [Pa] air pressure; df value is in mbar so multiplied by 100 to Pa
    water_vapor_content = 1.551             # [cm] Atmospheric water vapor content; data from AERONET for FZ Juelich for Sep 2021; Level 2 Quality
    tau500 = 0.221                          # [-] aerosol optical depth at wavelength 500 nm; data from AERONET for FZ Juelich for Sep 2021; Level 2 Quality
    ozone = 0.314                           # [atm-cm] Atmospheric ozone content; data from WOUDC for Aug 2021 for Hohenpeissenberg
    albedo = simulationDict['albedo']       # [-] fix albedo value
    
    # Attention: sun_zenith is greater than 90 deg for night time
    sun_zenith = df.iloc[j]['apparent_zenith']  # [deg] zenith angle of solar radiation
    sun_azimuth = df.iloc[j]['azimuth'] # [deg] azimith angle of solar radiation

    currentDate = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3]) + pd.to_timedelta(j, unit='H')  # current date and time to calculate spectrum          
    doy = int(currentDate.strftime('%j'))        # getting day of year out of the current date

    aoi = irradiance.aoi(tilt, azimuth, sun_zenith, sun_azimuth) # always equal to sun_zenith, because tilt = 0° 
    
    # The technical report uses the 'kasten1966' airmass model, but later versions of SPECTRL2 use 'kastenyoung1989'.
    # Attention: returns NaN values, if sun_zenith is greater than 90 deg
    relative_airmass = atmosphere.get_relative_airmass(sun_zenith, model='kastenyoung1989')
    
    '''
    modeling spectral irradiance using `pvlib.spectrum.spectrl2`
    The poa_global array represents the total spectral irradiance on the ground surface
    Note: With the exception of wavelength, which has length 122, each array has shape (122, N)
          where N is the length of the input apparent_zenith
    '''
    spectra = spectrum.spectrl2(
        apparent_zenith=sun_zenith,
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
    

def calcuateViewFactor(simulationDict, dataFrame):
    '''
    Calculates timeseries view factors with pvfactors between albedo meter and ground
        
    Parameters
    ----------
    
      
    Returns
    -------
    
    '''
    df = dataFrame
    
    # parameters for PV array, which contains the albedometer as a horizontal PVrow
    pvarray_parameters = {
    'n_pvrows': 1,            # number of pv rows, 1 because albedometer has only 1 surface
    'pvrow_height': 1,        # height of pvrows (measured at center / torque tube)
    'pvrow_width': 0.05,      # width of glasdome of albedometer
    'axis_azimuth': 0.,       # azimuth angle of rotation axis
    'gcr': 0.5,               # ground coverage ratio, irrelevant because only 1 row
    'surface_tilt': 0.,       # tilt of albedometer, 0 = horizintal
    'surface_azimuth': simulationDict['azimuth'],   # azimuth of same to azimuth of pv rows front surface
    'solar_zenith': df.apparent_zenith,    # solar zenith as dataframe
    'solar_azimuth': df.azimuth,           # solar azimuth as dataframe
    }
    
    # creat a OrderedPVArray with pvarray_parameters
    pvarray = OrderedPVArray.init_from_dict(pvarray_parameters)
       
    # fit the zenith and azimuth angles of albedometer and sun to pvarrray as array-like arguments
    pvarray.fit(pvarra_parameters['solar_zenith'], pvarra_parameters['solar_azimuth'], pvarra_parameters['surface_tilt'], pvarra_parameters['surface_azimuth'])
    
    # Plot pvarray shapely geometries at timestep 0
    f, ax = plt.subplots(figsize=(10, 3))
    pvarray.plot_at_idx(0, ax)
    plt.show()
    
    
    
    return 
    
def calculateAlbedo(simulationDict, dataFrame, resultspath):
    '''
    Calculates R value for every hour in the time period between startHour and endHour
    Calculates H value for every hour in the time period between startHour and endHour
    Calculates a value (Albedo) for every hour in the time period between startHour and endHour
        
    Parameters
    ----------
    simulationDict: simulation Dictionary, which can be found in GUI.py
    dataFrame: pandas dataframe, which contains the weather data
    resultspath: output filepath
    
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
    a_hourly = []     # array to hold albedo
    cd = []           # array to hold hourly datetime  
    
    #########################################################################
    '''
    Loop to calculate R, H and Albdeo for every hour. 
    Start value is 0, end value is the number of hours between starthour and endhour of the calculation period. 
    The starthour has to be the same as in the dataFrame. The increment is one hour.
    '''
    
    for j in range(timedelta):
                       
        spectrum = modelingSpectralIrradiance(simulationDict, dataFrame, j) # 8D array from the function modelingSpectralIrradiance is created
        R_lamda_array = getReflectivityData(simulationDict) # 1D array from the function getReflectanceData is created
        
        sum_R_G = 0
        sum_G = 0
                
        for i in range(112): # 112 loops (0<=i<=111), because of 112 wavelenghts in spectra, which are used for calculation (only to 3000 nm, because R values reaches only to 3000 nm)
            
            '''
            Attention: 
            - G_lamda (= 'poa_global' colume of the array 'spectrum') gives NaN values for nigth time instead of 0,
              because the input parameter 'relative_airmass' of 'spectra' in the function 'modelingSpectralIrradiance' 
              is a NaN value for night time, because apperent_zenith is greater than 90 deg
            - sum_R_G and sum_G are NaN values for nighttime, in consequence
            '''
            G_lamda = spectrum['poa_global'][i] # G for current number of wavelength i [W/m²/nm]
            G_lamda2 = G_lamda[0]               # gets G out of the array (which contains only one value)
            R_lamda = R_lamda_array[i]          # R for current number of wavelength i [-]
            lamda = spectrum['wavelength'][i]   # current wavelength i [nm]
                              
            sum_R_G += (G_lamda2 * R_lamda * lamda) # sum up the multiplication of R, G and lamda for every wavelength [W/m²]
            sum_G += (G_lamda2 * lamda)             # sum up multiplication of G and lamda for every wavelength [W/m²]
        
        
        #########################################################################
        # Calculate R value
        
        # Check, if sum_G is 0 or Nan, so that sum_R_G is not divided by 0 or NaN
        if sum_G == 0 or pd.isna(sum_G): # NaN values only for night time (see comment above)
            R = 0       
        else:
            R = sum_R_G / sum_G
    
        R_hourly.append(R)
        
        #########################################################################
        
        # Calculates H value
               
        DNI = df.iloc[j]['dni']                     # direct normal irradiation out of dataframe (which comes from weatherfile) [W/m²]
        DHI = df.iloc[j]['dhi']                     # diffuse horizontal irradation out of dataframe (which comes from weatherfile) [W/m²]
        theta = math.radians(df.iloc[j]['zenith'])  # sun zenith angle out of dataframe[rad]
        
        # Check, if DHI is 0, so that DNI is not divided by 0
        if DHI == 0:
            H = 0
        elif theta > (0.5*math.pi):   # 0.5*pi rad = 90 deg
            H = 0
        else:
            H = (DNI/DHI) * math.cos(theta)
    
        H_hourly.append(H)
        
        #########################################################################
        
        # Calculate Albedo
        # TODO: Viewfactor übergeben
        VF_s_a1 = # Viewfactor from surface S (Albedo measurement) to surface A1 (unshaded ground)
        VF_s_a2 = # Viewfactor from surface S (Albedo measurement) to surface A2 (shaded ground)
        
        a = R * (VF_s_a1 + (1/(H+1)) * VF_s_a2) # Albedo [-]
        
        a_hourly.append(a)
        
        #########################################################################
         
        # current date and time
        currentDate = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3]) + pd.to_timedelta(j, unit='H') 
        cd.append(currentDate)      # append the currentDate to cd array
   
    #########################################################################
    
    # a_hourly is saved to new csv
    albedo_results = pd.DataFrame({'datetime':cd, 'spectral Albedo':a})
    albedo_results.to_csv(resultspath + 'spectral_Albedo.csv', sep=';', index=False)
    
    #########################################################################
     
    # weatherfile gets updated with a_hourly
    
    # read in first and second row separat
    with open(simulationDict['weatherFile'], newline='') as f:
        reader = csv.reader(f)
        row1 = next(reader)  # gets the first line
        row2 = next(reader)  # gets the second line

    # read in weatherfile as pandas dataframe
    weatherfile = pd.read_csv(simulationDict['weatherFile'], sep=',', header = 1)
   
    # weatherfile and a_hourly must have the same length 
    # check, if length of a_hourly is shorten than weatherfile
    # if a_hourly is shorter, nan values gets added, so both list have same length
    length_w= len(weatherfile.index)
    length_a= len(a_hourly)
    
    if length_a < length_w: 
        dif_length = length_w - length_a
        for i in range(dif_length):
            a_hourly.append(math.nan)
    
    # values in column Alb are displaced with values from a_hourly
    weatherfile['Alb'] = a_hourly  # a_hourly must have same length as weatherfile

    # convert pandas dataframe into a list
    weatherfile_list = weatherfile.values.tolist()
    
    # save row 1 and 2 and the weatherfile list into csv
    file = open(simulationDict['weatherFile'], 'w+', newline ='') 
    with file:     
        write = csv.writer(file) 
        write.writerow(row1)
        write.writerow(row2)
        write.writerows(weatherfile_list) 
    
    #########################################################################

    
    # return a_hourly
    

