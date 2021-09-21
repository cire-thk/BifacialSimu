# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 17:53:38 2021

@author: Sarah Glaubitz

name: BiSim - spectralAlbedoHandler

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

import BiSim_dataHandler
import BiSim_radiationHandler

def getReflectanceData(simulationDict):
    '''
    Read the spectral reflectance data of the material (sand); R(lamda)

    Returns
    -------
    None.

    '''
     
    
    
    R_lamda=numpy.loadtxt(simulationDict['spectralReflectancefile']) 
    
def modelingSpectralIrradiance(simulationDict, currentDate):
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
    simulationDict: simulation Dictionary, which can be found in BiSimu_main_spectralAlbedo.py

    Returns
    -------
    spectra: dict of arrays

    '''
    lat = simulationDict('latitude')    # [deg] latitude of ground surface to calculate spectral albedo
    lon = simulationDict('longitude')   # [deg] longitude of ground surface to calculate spectral albedo
    tilt = 0                            # [deg] always 0, because the ground is never tilted
    azimuth = simulationDict('azimuth') # [deg] same azimuth for ground surface as for PV panel
    pressure = 100498                   # [Pa] air pressure; average of yearly values from 1958 to 2020 for airport Cologne/Bonn, taken from DWD
    water_vapor_content = 1.551         # [cm] Atmospheric water vapor content; data from AERONET for FZ Juelich for Sep 2021; Level 2 Quality
    tau500 = 0.221                      # [-] aerosol optical depth at wavelength 500 nm; data from AERONET for FZ Juelich for Sep 2021; Level 2 Quality
    ozone = 0.314                       # [atm-cm] Atmospheric ozone content; data from WOUDC for Aug 2021 for Hohenpeissenberg
    albedo = simulationDict('albedo')   # [-] fix albedo value
    
    times = pd.date_range(currentDate, freq='h', periods=1, tz='Etc/GMT+' + simulationDict('utcOffset')) # posibility to calculate several spectras for diffrent times, when period >1 
    solpos = solarposition.get_solarposition(times, lat, lon, pressure = pressure) #pressure selber hinzugefügt
    aoi = irradiance.aoi(tilt, azimuth, solpos.apparent_zenith, solpos.azimuth)

    # The technical report uses the 'kasten1966' airmass model, but later versions of SPECTRL2 use 'kastenyoung1989'.
    relative_airmass = atmosphere.get_relative_airmass(solpos.apparent_zenith, model='kastenyoung1989')

    '''
    model spectral irradiance using `pvlib.spectrum.spectrl2`
    Returns: A dict of arrays with wavelength; dni_extra; dhi; dni; poa_sky_diffuse; poa_ground_diffuse; poa_direct; poa_global
    The poa_global array represents the total spectral irradiance on the ground surface
    Note: because calculating the spectra for more than one set of conditions, 2-D arrays is given back (one dimension for wavelength, one for time).
    '''
    
    spectra = spectrum.spectrl2(
        apparent_zenith=solpos.apparent_zenith,
        aoi=aoi,
        surface_tilt=tilt,
        ground_albedo=albedo,
        surface_pressure=pressure,
        relative_airmass=relative_airmass,
        precipitable_water=water_vapor_content,
        ozone=ozone,
        aerosol_turbidity_500nm=tau500,
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
    
    
def CalculateAlbedo(simulationDict, dataframe):
    '''
    Calculates R value for every hour in the time period between startHour and endHour
    Calculates H value for every hour in the time period between startHour and endHour
    Calculates a value (Albedo) for every hour in the time period between startHour and endHour
        
    Parameters
    ----------
    simulationDict: simulation Dictionary, which can be found in BiSimu_main_spectralAlbedo.py
    TODO: Muss den dataframe 'df' aus der Funktion 'startSimulation' aus simualtionController.pv irgendwie übergeben bekommen.
    TODO: Eventuell über den radiationHandler möglich, da der df an die Funktion simulateRaytrace und simulateViewFactors übergeben wird
    
    Returns
    -------
    None.

    '''
    df = dataFrame
    
    # Translate startHour und endHour in timeindexes
    dtStart = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
    beginning_of_year = datetime.datetime(dtStart.year, 1, 1, tzinfo=dtStart.tzinfo)
    startHour = int((dtStart - beginning_of_year).total_seconds() // 3600) # gives the hour in the year
                
    dtEnd = datetime.datetime(simulationDict['endHour'][0], simulationDict['endHour'][1], simulationDict['endHour'][2], simulationDict['endHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
    beginning_of_year = datetime.datetime(dtEnd.year, 1, 1, tzinfo=dtEnd.tzinfo)
    endHour = int((dtEnd - beginning_of_year).total_seconds() // 3600) # gives the hour in the year
    
    # Intialise arrays
    R_hourly = []     # array to hold R value
    H_hourly = []     # array to hold H value
    a_hourly = []     # array to hold a value
    
    '''
    Loop to calculate R for each hour. Start value is the starthour of the calculation period. 
    End value is the endhour of the calculation period. The start- and endhour for the desired 
    calculation period must match the weather file. The increment is one hour.
    '''
    
    for time in range(startHour, endHour+1):
        
              
        currentDate = time # ? ... hier noch weiter programmieren # yyyy-mm-dd hh:mm
        # TODO: aktuelle Stunde muss wieder in Datumsformat konvertiert werden, damit dieses der 
        # modelingSpectralIrrandiance Funktion übergeben wird
        
        spectrum = modelingSpectralIrradiance(simulationDict, currentDate)
                
        for i in range(112): # 112 loops, because of 112 wavelenghts in spectra, which are used for calculation
            
            # in jeder Zeile müssen Wellenlänge, R und G stehen (aktuell R und G noch in zwei verschiedenen Listen)
            # TODO: R für die aktuelle Wellenlänge ziehen
            # Problem: R Werte sind für andere Wellenlängen als G Werte
            
            G_lamda = spectrum['poa_global'][i] # G for current wavelength lamda [W/m²/nm]
            R_lamda =  # R for current wavelength lamda [-]
            lamda = spectrum ['wavelength'][i]  # current wavelength lamda [nm]
        
            sum_R_G += (G_lamda * R_lamda * lamda) # sum up the Multiplication of R and G for every wavelength [W/m²]
            sum_G += (G_lamda * lamda)  # sum up G for every wavelength [W/m²]
      
        # Calcualte R value
        R = sum_R_G / sum_G
    
        R_hourly.append(R)
        
        # Calculates H value
               
        DNI = df[i, 'dni']          # direct normal irradiation out of weatherfile [W/m²]
        DHI = df[i, 'dhi']          # diffuse horizontal irradation out of weatherfile [W/m²]
        theta = df[i, 'zenith']     # sun zenith angle [deg]
    
        H = (DNI/DHI) * cos(theta)
    
        H_hourly.append(H)
        
        # Calculate Albedo
        # TODO: Viewfactor übergeben
        vf_s_a1 # Viewfactor from surface S (Albedo measurement) to surface A1 (unshaded ground)
        vf_s_a2 # Viewfactor from surface S (Albedo measurement) to surface A2 (shaded ground)
        
        a = R * (vf_s_a1 + (1/(H+1)) * vf_s_a2) # Albedo [-]
        
        a_hourly.append(a)
        
    return a_hourly
    

