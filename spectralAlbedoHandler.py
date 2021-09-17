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


import BiSim_dataHandler
import BiSim_radiationHandler

def getReflectanceData(simulationDict):
    '''
    Read the spectral Reflectance data of the material (sand); R(lamda)

    Returns
    -------
    None.

    '''
    # If-Abfrage, ob Werte gleich -1.23e+34 sind, da Werte dann ungültig
    # Eingelesene Werte müssen geschnitten werden, da diese im wissenschaftlichen Format notiert sind
    
    R_lamda=numpy.loadtxt(simulationDict['spectralReflectancefile']) 
    
def modelingSpectralIrradiance(simulationDict):
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

    The figure shows modeled spectra at hourly intervals across a single morning.
    
    Parameters
    ----------
    simulationDict: simulation Dictionary, which can be found in BiSimu_main_spectralAlbedo.py

    Returns
    -------
    None.

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
    
    times = pd.date_range('2021-09-22 12:00', freq='h', periods=1, tz='Etc/GMT+' + simulationDict('utcOffset')) # posibility to calculate several spectras for diffrent times, when period >1 
    solpos = solarposition.get_solarposition(times, lat, lon, pressure = pressure) #pressure selber hinzugefügt
    aoi = irradiance.aoi(tilt, azimuth, solpos.apparent_zenith, solpos.azimuth)

    # The technical report uses the 'kasten1966' airmass model, but later versions of SPECTRL2 use 'kastenyoung1989'.
    relative_airmass = atmosphere.get_relative_airmass(solpos.apparent_zenith, model='kastenyoung1989')

    # model spectral irradiance using `pvlib.spectrum.spectrl2`
    # Returns: A dict of arrays with wavelength; dni_extra; dhi; dni; poa_sky_diffuse; poa_ground_diffuse; poa_direct; poa_global
    # The poa_global array represents the total spectral irradiance on the ground surface
    # Note: because calculating the spectra for more than one set of conditions, 2-D arrays is given back (one dimension for wavelength, one for time).

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
   
    # plot: poa_global against wavelength (like Figure 5-1A from the SPECTRL2 NREL Technical Report)
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
    
    
def CalculateR():
    '''
    Calculates R value

    Returns
    -------
    None.

    '''
    
def CalculateH():
    '''
    Calculates H value for every hour in the time period between startHour and endHour

    Returns
    -------
    None.

    '''
    
def CalculateAlbedo():
    '''
    Parameters
    ----------
    H
    R
    Viewfactors

    Returns
    -------
    None.

    '''