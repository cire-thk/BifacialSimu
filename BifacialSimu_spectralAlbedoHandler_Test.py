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
import os
import numpy
import math
import dateutil.tz
import datetime
import numpy as np
import csv
import matplotlib.pyplot as plt
from pvlib import spectrum, irradiance, atmosphere
from pvfactors.geometry import OrderedPVArray
from pvfactors.viewfactors.vfmethods import VFTsMethods
from pvfactors.config import DISTANCE_TOLERANCE

rootPath = os.path.realpath(".")
resultspath = 'C:\Outputs'

simulationDict = {
'simulationName' : 'NREL_best_field_row_2',
'simulationMode' : 1, 
'localFile' : True, # Decide wether you want to use a  weather file or try to download one for the coordinates
'weatherFile' : (rootPath +'/WeatherData/Cologne_Germany/Cologne_Bibdach_50.935_6.992_Measurement_Sept_Okt_2021.csv'), # weather file in TMY format 
'spectralReflectancefile' : (rootPath + '/ReflectivityData/interpolated_reflectivity.csv'),
'cumulativeSky' : False, # Mode for RayTracing: CumulativeSky or hourly
'startHour' : (2021, 9, 23, 0),  # Only for hourly simulation, yy, mm, dd, hh
'endHour' : (2021, 9, 24, 0),  # Only for hourly simulation, yy, mm, dd, hh
'utcOffset': +2,
'tilt' : 25, #tilt of the PV surface [deg]
'singleAxisTracking' : True, # singleAxisTracking or not
'backTracking' : False, # Solar backtracking is a tracking control program that aims to minimize PV panel-on-panel shading 
'ElectricalMode_simple': False, # simple electrical Simulation after PVSyst, use if rear module parameters are missing
'limitAngle' : 60, # limit Angle for singleAxisTracking
'hub_height' : 1.3, # Height of the rotation axis of the tracker [m]
'azimuth' : 180, #azimuth of the PV surface [deg] 90°: East, 135° : South-East, 180°:South
'nModsx' : 1, #number of modules in x-axis
'nModsy' : 1, #number of modules in y-axis
'nRows' : 1, #number of rows
'sensorsy' : 5, #number of sensors
'moduley' : 1 ,#length of modules in y-axis
'modulex' : 1, #length of modules in x-axis  
'hourlyMeasuredAlbedo' : True, # True if measured albedo values in weather file
'spectralAlbedo' : True, # Option to calculate a spectral Albedo 
'albedo' : 0.282, # Measured Albedo average value, if hourly isn't available
'frontReflect' : 0.03, #front surface reflectivity of PV rows
'BackReflect' : 0.05, #back surface reflectivity of PV rows
'longitude' : 6.992, 
'latitude' : 50.935,
'gcr' : 0.45, #ground coverage ratio (module area / land use)
'module_type' : 'NREL row 2', #Name of Module
'clearance_height': 1.5,
}

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
    j: current loop number, which represent the hour after starthour = index of df
    
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

def build_ts_vf_matrix_albedo(pvarray_pv, pvarray_albedo):
    """
    Calculate timeseries view factor matrix for the two given ordered pv arrays
    copied from pvfactors.viewfactors.calculator.VFCalculator.build_ts_vf_matrix with little change
    
    Parameters
    ----------
    pvarray_pv: OrderedPVArray which contains the paramters of PVrows like in radiationHandler
    pvarra_albedo: OrderedPVArray which contains the paramters of an albedometer as horizontal PVrow

    Returns
    -------
    vf_matric: np.ndarray, Timeseries view factor matrix, with 3 dimensions:[n_surfaces, n_surfaces, n_timesteps]
    """
    
    vf_ts_methods = VFTsMethods()
    
    # Initialize matrix
    rotation_vec = pvarray_albedo.rotation_vec
    tilted_to_left = rotation_vec > 0
    n_steps = len(rotation_vec)
    n_ts_surfaces = pvarray_albedo.n_ts_surfaces
    vf_matrix = np.zeros((n_ts_surfaces + 1, n_ts_surfaces + 1, n_steps), dtype=float)  # don't forget to include the sky

    # Get timeseries objects
    ts_ground = pvarray_pv.ts_ground        # ground surfaces like the geometry of PVrows
    ts_pvrows = pvarray_albedo.ts_pvrows    # PVrows surfaces for the albedometer

    # Calculate ts view factors between pvrow and ground surfaces
    vf_ts_methods.vf_pvrow_gnd_surf(ts_pvrows, ts_ground, tilted_to_left, vf_matrix)
    
    # Calculate view factors between pv rows
    vf_ts_methods.vf_pvrow_to_pvrow(ts_pvrows, tilted_to_left, vf_matrix)
    
    # Calculate view factors to sky
    vf_matrix[:-1, -1, :] = 1. - np.sum(vf_matrix[:-1, :-1, :], axis=1)
    # This is not completely accurate yet, we need to set the sky vf to zero when the surfaces have zero length
    for i, ts_surf in enumerate(pvarray_pv.all_ts_surfaces):
        vf_matrix[i, -1, :] = np.where(ts_surf.length > DISTANCE_TOLERANCE, vf_matrix[i, -1, :], 0.)

    return vf_matrix

def calculateViewFactor(simulationDict, dataFrame, j):
    '''
    Calculates timeseries view factors with pvfactors between albedometer and ground
        
    Parameters
    ----------
    simulationDict: simulation Dictionary, which can be found in GUI.py
    dataFrame: pandas dataframe, which contains the weather data
    j: current loop number, which represent the hour after starthour = index of df
      
    Returns
    -------
    vf_matrix: Timeseries view factor matrix, with 3 dimensions: [n_surfaces, n_surfaces, n_timesteps]
                n_timesteps = 1
    
    '''
    df = dataFrame
        
    # parameters of pvarrray, which contains the albedometer as a horizontal PVrow
    pvarray_parameters = {
    'n_pvrows': 1,                                  # number of pv rows, 1 because albedometer has only 1 surface
    'pvrow_height': 1,                              # height of pvrows (measured at center / torque tube)
    'pvrow_width': 0.05,                            # width of glasdome of albedometer
    'axis_azimuth': 0.,                             # azimuth angle of rotation axis
    'gcr': 0.5,                                     # ground coverage ratio, irrelevant because only 1 row
    'surface_tilt': 0.,                             # tilt of albedometer, 0 = horizintal
    'surface_azimuth': simulationDict['azimuth'],   # azimuth of same to azimuth of pv rows front surface
    'solar_zenith': df.iloc[j]['apparent_zenith'],  # solar zenith as dataframe
    'solar_azimuth': df.iloc[j]['azimuth'],         # solar azimuth as dataframe
    }
    
    # creat an OrderedPVArray with pvarray_parameters for albedometer
    pvarray_albedo = OrderedPVArray.fit_from_dict_of_scalars(pvarray_parameters)
        
    
    # parameters of pvarrray, which contains parameters like in radiationHandler
    simulationParameter = {
    'n_pvrows': simulationDict['nRows'],            # number of pv rows, 1 because albedometer has only 1 surface
    'pvrow_height': simulationDict['clearance_height'],   # height of pvrows (measured at center / torque tube)
    'pvrow_width': simulationDict['moduley'],       # width of glasdome of albedometer
    'axis_azimuth': 0.,                             # azimuth angle of rotation axis
    'gcr': simulationDict['gcr'],                   # ground coverage ratio, irrelevant because only 1 row
    'surface_tilt': simulationDict['tilt'],         # tilt of albedometer, 0 = horizontal
    'surface_azimuth': simulationDict['azimuth'],   # azimuth of same to azimuth of pv rows front surface
    'solar_zenith': df.iloc[j]['apparent_zenith'],  # solar zenith as dataframe
    'solar_azimuth': df.iloc[j]['azimuth'],         # solar azimuth as dataframe
    }
    
    # creat an OrderedPVArray with simulationParemeters for the PVrowy like in radiationHandler
    pvarray_pv = OrderedPVArray.fit_from_dict_of_scalars(simulationParameter)
    
    '''
    # Plot pvarray shapely geometries at timestep 0
    f, ax = plt.subplots(figsize=(10, 3))
    pvarray_albedo.plot_at_idx(0, ax, with_surface_index=True)
    plt.show()
    
    # Plot pvarray shapely geometries at timestep 0
    f, ax = plt.subplots(figsize=(10, 3))
    pvarray_pv.plot_at_idx(0, ax, with_surface_index=True)
    plt.show()
    
    # List some indices
    pvrow_center = pvarray_albedo.ts_pvrows[0]
    pv_ground = pvarray_albedo.ts_ground
    pv_ground2 = pvarray_pv.ts_ground
    
    ts_surface_list = pvrow_center.front.all_ts_surfaces
    print("Indices of surfaces on front side of center PV row")
    for ts_surface in ts_surface_list:
        index = ts_surface.index
        print("... surface index: {}".format(index))

    ts_surface_list2 = pvrow_center.back.all_ts_surfaces
    print("Indices of surfaces on back side of center PV row")
    for ts_surface in ts_surface_list2:
        index = ts_surface.index
        print("... surface index: {}".format(index))
    
    ts_surface_ground = pv_ground.all_ts_surfaces
    print("Indices of surfaces of ground of pvarray_albedo")
    for ts_surface in ts_surface_ground:
        index = ts_surface.index
        print("... surface index: {}".format(index))
        
    ts_surface_ground2 = pv_ground2.all_ts_surfaces
    print("Indices of surfaces of ground pf pvarray_pv")
    for ts_surface in ts_surface_ground2:
        index = ts_surface.index
        print("... surface index: {}".format(index))
    
    for ts_surface in ts_surface_list:
        index = ts_surface.index
        shaded = ts_surface.shaded
        length = ts_surface.length
        print("Surface with index: '{}' has shading status '{}' and length {} m".format(index, shaded, length))
    
    for ts_surface in ts_surface_ground:
        index = ts_surface.index
        shaded = ts_surface.shaded
        length = ts_surface.length
        print("Albedo: Surface with index: '{}' has shading status '{}' and length {} m".format(index, shaded, length))
        
    for ts_surface in ts_surface_ground2:
        index = ts_surface.index
        shaded = ts_surface.shaded
        length = ts_surface.length
        print("PV: Surface with index: '{}' has shading status '{}' and length {} m".format(index, shaded, length))
    '''
    
    # create vf_matrix out of pvarray_albedo and pv_array_pv with selfmade function
    vf_matrix = build_ts_vf_matrix_albedo(pvarray_pv, pvarray_albedo)
    
    '''
    vf_calculator = VFCalculator()
    vf_matrix_albedo = vf_calculator.build_ts_vf_matrix(pvarray_albedo)
    vf_matrix_pv = vf_calculator.build_ts_vf_matrix(pvarray_pv)
    
    print("Number of dimensions: {}".format(vf_matrix.ndim))
    print("Shape of vf matrix: {}".format(vf_matrix.shape))
    
    print(vf_matrix[8, 0, :])
    print(vf_matrix[8, 4, :])
    
    print("Number of dimensions albedo: {}".format(vf_matrix_albedo.ndim))
    print("Shape of vf matrix albedo: {}".format(vf_matrix_albedo.shape))
    
    print("albedo", vf_matrix_albedo[8, 0, :])
    print(vf_matrix_albedo[8, 4, :])
        
    print("Number of dimensions pv: {}".format(vf_matrix_pv.ndim))
    print("Shape of vf matrix pv: {}".format(vf_matrix_pv.shape))
    
    print("pv", vf_matrix_pv[8, 0, :])
    print(vf_matrix_pv[8, 4, :])
    '''   
    
    return vf_matrix
    
def calculateAlbedo(simulationDict, dataFrame, resultpath):
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
    VF_S_A1 = []      # array to hold view factors from surface s to surface A1
    VF_S_A2 = []      # array to hold view factors from surface s to surface A2
    a_hourly = []     # array to hold albedo
    cd = []           # array to hold hourly datetime  
    
    #########################################################################
    '''
    Loop to calculate R, H and Albdeo for every hour. 
    Start value is 0, end value is the number of hours between starthour and endhour of the calculation period. 
    The starthour has to be the same as in the dataFrame. The increment is one hour.
    '''
    
    for j in range(timedelta):
                       
        spectrum = modelingSpectralIrradiance(simulationDict, df, j) # 8D array from the function modelingSpectralIrradiance is created
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
        
        # vf_maritx is created with timestep eqaul to current loop number, which represents the hour after starthour
        vf_matrix = calculateViewFactor(simulationDict, df, j)
        
        # Check if GHI is 0, then viewfactors are also 0 because there is no radiation
        if df.iloc[j]['ghi'] == 0:
            VF_s_a1 = 0
            VF_s_a2 = 0
        else:
            VF_s_a1_array = vf_matrix[8, 0, :] # Viewfactor from surface S (Albedo measurement) to surface A1 (unshaded ground)
            VF_s_a1 = VF_s_a1_array[0]         # to convert array into number
            VF_s_a2_array = vf_matrix[8, 4, :] # Viewfactor from surface S (Albedo measurement) to surface A2 (shaded ground)
            VF_s_a2 = VF_s_a2_array[0]         # to convert array into number
            
        a = R * (VF_s_a1 + (1/(H+1)) * VF_s_a2)     # spectral Albedo [-]
        
        VF_S_A1.append(VF_s_a1)
        VF_S_A2.append(VF_s_a2)
        a_hourly.append(a)
        
        #########################################################################
         
        # current date and time
        currentDate = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3]) + pd.to_timedelta(j, unit='H') 
        cd.append(currentDate)      # append the currentDate to cd array
   
    
    #########################################################################
    
    # calculted values are saved to new csv
    albedo_results = pd.DataFrame({'datetime':cd, 'spectral Albedo':a_hourly, 'R': R_hourly, 'H': H_hourly, 'VF_s_a1': VF_S_A1, 'VF_s_a2': VF_S_A2})
    albedo_results.to_csv(resultspath + '/spectral_Albedo.csv', sep=';', index=False)
    
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

    
    return a_hourly
    


  
    
df = pd.read_csv('Dataframe_df_Cologne.csv')
#print (df['ghi'])
#print (df['dhi'])
#print (df['dni'])

test =calculateAlbedo(simulationDict, df, resultspath)
print(test)    

#calculateViewFactor(simulationDict, df)
