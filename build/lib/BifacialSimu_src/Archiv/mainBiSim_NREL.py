#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 12:57:54 2019

@author:        Eva-Maria Grommes
Bifacial photovoltaic yield simulation as a function of the albedo


Last change:
    23.02.21 New solarposition calc method, new energy density calc
    09.03.21 Variable Albedo implemented
    12.04.21 New Path Management implemented

"""

# Import
from IPython import get_ipython
get_ipython().magic('reset -sf')

import pandas as pd #pandas = can read .csv as input
import matplotlib.pyplot as plt #display shadows
import numpy as np
import os #to import directories
import warnings
import math
import pvlib #for electrical output simulation
from datetime import datetime
from pvfactors.viewfactors.aoimethods import faoi_fn_from_pvlib_sandia #to calculate AOI reflection losses
from pvfactors.engine import PVEngine
from pvfactors.irradiance import HybridPerezOrdered
from pvfactors.geometry import OrderedPVArray
from pvfactors.viewfactors import VFCalculator
from tqdm import tqdm

# Settings for calculating ViewFactor
get_ipython().run_line_magic('matplotlib', 'inline')
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

#########################################################

# Path to import irradiance data / Quality for plot export
now = datetime.now()
date_time = now.strftime("%Y %m %d_%H_%M") # get current date and time
localDir = os.getcwd()
weatherDir = os.path.join(localDir, 'WeatherData\Golden_USA')
#weatherDir = os.path.join(localDir, 'WeatherData\Ghana_Africa')
weatherData = os.path.join(weatherDir, 'SRRL Weatherdata 3.csv') # get path to weather data
#weatherData = os.path.join(weatherDir, 'Ghana_Reference.csv') # get path to weather data
outputPath = os.path.join(localDir, 'Outputs')
resultsPath = os.path.join(outputPath, date_time + '_results/' ) 
dpi = 150 #Quality for plot export

if not os.path.exists(resultsPath):
    os.makedirs(resultsPath)        # create path to output
#########################################################
    
# Dictionary for Input Parameters
simulationParameter = {
    'n_pvrows': 3, #number of PV rows
    'number_of_segments': 5, #number of segments for each PVrow
    'pvrow_height': 1.50, #height of the PV rows, measured at their center [m]
    'pvrow_width': 2.0, #width of the PV panel in row, considered 2D plane [m]
    'pvmodule_width': 0.992, #length of the PV panel in row, considered 2D plane [m]
    'surface_azimuth': 180, #azimuth of the PV surface [deg] 90°= East, 135° = South-East, 180°=South
    'surface_tilt': 30, #tilt of the PV surface [deg]
    #'albedo': 0.259597496, # Measured Albedo average value
    'a0': 0.259597496, # Measured Albedo under direct illumination with a solar zenith angle of approx. 60°
    'adiff': 0.22, # Measured Albedo under 100% diffuse illumination
    'C': 0.4, #Solar angle dependency factor    
    #'index_observed_pvrow': 1, #index of the PV row, whose incident irradiance will be returned
    'rho_front_pvrow' : 0.03, #front surface reflectivity of PV rows
    'rho_back_pvrow' : 0.05, #back surface reflectivity of PV rows
    'horizon_band_angle' : 6.5, #elevation angle of the sky dome's diffuse horizon band [deg]   
    'L_Position': -105.1727827, #Longitude of measurement position [deg]
    'L_Area': -105.1727827, #Longitude of timezone area [deg]
    'Latitude_Position': 39.7398341, #Latitude of measurement position [deg]
    'axis_azimuth': 0.0, #Axis Azimuth angle [deg]
    'gcr': 0.35, #ground coverage ratio (module area / land use)
}

irradiance_model = HybridPerezOrdered(rho_front=simulationParameter['rho_front_pvrow'], rho_back=simulationParameter['rho_back_pvrow']) #choose an irradiance model

# Dictionary for Module Parameters

#GCL P6 72GD
print("\n NREL Row 2:") 
moduleParameter = {
    'I_sc_f': 9.5, #Short-circuit current measured for front side illumination of the module at STC [A]
    'I_sc_r': 6.56, #Short-circuit current measured for rear side illumination of the module at STC [A]
    'V_oc_f': 48, #Open-circuit voltage measured for front side illumination of module at STC [V]
    'V_oc_r': 47.3, #Open-circuit voltage measured for rear side illumination of module at STC [V]
    'V_mpp_f': 39.2, #Front Maximum Power Point Voltage [V]
    'V_mpp_r': 39.5, #Rear Maximum Power Point Voltage [V]
    'I_mpp_f': 9.00, #Front Maximum Power Point Current [A]
    'I_mpp_r': 6.2, #Rear Maximum Power Point Current [A]
    'P_mpp': 354, # Power at maximum power Point [W]
    'T_koeff_P': -0.0036, #Temperature Coeffizient [1/°C]
    'T_amb':20, #Ambient Temperature for measuring the Temperature Coeffizient [°C]
    'T_koeff_I': 0.0005, #Temperaturkoeffizient for I_sc [1/°C] #SG
    'T_koeff_V': 0.0005, #Temperaturkoeffizient for U_oc [1/°C] #SG
    'zeta': 0.06 #Bestrahlungskoeffizient für Leerlaufspannung [-]
    
    #'inverter': pvlib.pvsystem.retrieve_sam('cecinverter')['ABB__MICRO_0_25_I_OUTD_US_208_208V__CEC_2014_'],
    #'module': pvlib.pvsystem.retrieve_sam('SandiaMod')['Canadian_Solar_CS5P_220M___2009_'],
    #'P_sys': 360, #system nominal power [KWp]
}

# Add dictionary for discretization 
rowSegments = {}

for i in range(0, simulationParameter['n_pvrows']):
    rowSegments[i] = {'back': simulationParameter['number_of_segments']}

discretization = {'cut':rowSegments}
simulationParameter.update(discretization)

#########################################################

# Define timezone and table specifications
def export_data(fp):
    #tz = tz_localize('Africa/Accra')
    df = pd.read_csv(fp, header = 0)
    
    # Define, which columns to drop, if none, comment out
    #columnsToDrop = [df.columns[1]] 
    #columnsToDrop = [df.columns[5], df.columns[6], df.columns[7], df.columns[8]] 
    #for column in columnsToDrop:
    #    df = df.drop(column, axis = 1)
        
    # Rename columns for calculation
    df = df.rename(columns = {'Date': 'timestamps'})
    df = df.rename(columns = {'Avg Global Horizontal [W/m^2]': 'ghi'})
    df = df.rename(columns = {'Diffuse horizontal irradiance (W/m2)': 'dhi'})
    df = df.rename(columns = {'Direct (beam) normal Irradiance (W/m2)': 'dni'})
    df = df.rename(columns = {'Dry bulb temperature (deg. C)': 'temperature'})
    df = df.rename(columns = {'Windspeed (m/s)': 'windspeed'})
    df = df.rename(columns = {'Air pressure (Pa)': 'airpressure'})
 
    df = df.set_index('timestamps') # Define index for dataframe
    df['datetime'] = pd.date_range(start='2019/10/01 00:00', end= '2020/05/01 00:00', freq='H')
    #df.index=pd.to_datetime(df.index) #Configure x-axis label
    df= df.set_index('datetime')
    
    return df

df = export_data(weatherData)
#print(df)

#########################################################

# Measured Albedo average value
#albedo = simulationParameter['albedo']

#########################################################
#Calculation of sun parameters
"""
def calcB(n):
    return math.radians((n - 1) * (360/365))

def calcDeclination(B): #Declination on North-South axis
    return 0.006918 - 0.399912 * math.cos(B) + 0.070257 * math.sin(B) - 0.006758 * math.cos(2 * B) + 0.000907 * math.sin(2 * B) - 0.002697 * math.cos(3 * B) + 0.00148 * math.sin(3 * B)

def calcE(B): #Equation of time
    return 229.2 * (0.000075 + 0.001868 * math.cos(B) - 0.032077 * math.sin(B) - 0.014615 * math.cos(2 * B) - 0.04089 * math.sin(2 * B))

def calcLT(L_Area, L_Position, E, LET): #local time and longitude
    return (4 * (L_Area - L_Position) + E) / 60 + LET #LET=legal time (GEZ)

def calcHourAngle(LT): #Hour angle
    return math.radians((LT - 12) * 15)

def calcCrownAngle(Declination, Latitude, HourAngle): #Zenit- or Crown Angle
    return math.acos(math.sin(Declination) * math.sin(Latitude) + math.cos(Declination) * math.cos(Latitude) * math.cos(HourAngle))

def calcAzimuthAngle(HourAngle, CrownAngle, Latitude, Declination): #Azimuth Angle
    
    f = 1
    if HourAngle < 0:
        f = -1
    
    return f * abs(math.acos((math.cos(CrownAngle) * math.sin(Latitude) - math.sin(Declination)) / (math.sin(CrownAngle) * math.cos(Latitude))))

def calcInclinationAngle(CrownAngle, AzimuthAngle, HourAngle, Latitude, Declination): #Inclination (Neigung) Angle

    AzimuthAngle = calcAzimuthAngle(HourAngle, CrownAngle, Latitude, Declination)
    f = 1
    if AzimuthAngle < 0:
        f = -1
    
    ElevationAngle = math.radians(90) - CrownAngle
    
    if ElevationAngle > 0:
        return f * math.atan(math.tan(CrownAngle) * abs(math.cos(math.radians(90) - AzimuthAngle)))
    else:
        return f * math.radians(90)

def calcElevationAngle(CrownAngle): #Elevation Angle (Höhenwinkel)
    return math.radians(90) - CrownAngle
"""
#########################################################
# Calculate sun parameters for every timestamp

# Clear lists/columns
solar_zenith = []
solar_azimuth = []
surface_tilt = []
surface_azimuth = []
albedo = []

ghi = df['ghi']  
dhi = df['dhi']
a0 = simulationParameter['a0']
C = simulationParameter['C']
adiff = simulationParameter['adiff']

# Begin loop: Calculate for every hour 
for index, row in df.iterrows():
    
    dayOfYear = df.index.get_loc(index) / 24    
    Declination = pvlib.solarposition.declination_spencer71(dayOfYear)  #return radiant
    #Declination = pvlib.solarposition.declination_cooper69(dayOfYear) #return radiant
    equationOfTime = pvlib.solarposition.equation_of_time_spencer71 (dayOfYear)   #return minutes
    HourAngle = pvlib.solarposition.hour_angle(pd.date_range(start='2019/10/01 00:00', end= '2020/05/01 00:00', freq='H'), simulationParameter['L_Position'], equationOfTime)    #need longitude in degree, equation of time (in min), return degree
    solar_zenith = pvlib.solarposition.solar_zenith_analytical(np.rad2deg(simulationParameter['Latitude_Position']), np.rad2deg(HourAngle), Declination)    #need latitude in radiant (actuall in degree), hourangle in radiant (actuall in degree), declination in radiant, return radiant
    solar_azimuth = pvlib.solarposition.solar_azimuth_analytical(np.rad2deg(simulationParameter['Latitude_Position']), np.rad2deg(HourAngle), Declination, solar_zenith)    #need latitude in radiant (actuall in degree), hourangle in radiant (actuall in degree), declination in radiant, zenit in radiant, return radiant
    surface_tilt = simulationParameter['surface_tilt']
    surface_azimuth = simulationParameter['surface_azimuth']
    
df['solar_zenith'] = solar_zenith

df['solar_azimuth'] = solar_azimuth

df['surface_tilt'] = surface_tilt

df['surface_azimuth'] = surface_azimuth

# Calculate albedo for every hour
for index, row in df.iterrows(): 
    
    if row['ghi'] == 0: #Avoid division by 0
        df.loc[index,'albedo'] = 0
    else:
        df.loc[index,'albedo'] = (1 - row['dhi'] / row['ghi']) * a0 * ((1 + C)  / (1 + 2 * C * math.cos(row['solar_zenith']))) + (row['dhi']  / row['ghi'] * adiff)
      
    if df.loc[index,'albedo'] < 0: #change values below 0 for yield calculation
       #df.loc[index,'albedo'] = 0
       #df.loc[index,'albedo'] = 0.241020557 #Calculated max albedo 6&7 o'clock
       df.loc[index,'albedo'] = 0.185259524 #Calculated mean albedo 6&7 o'clock
       #df.loc[index,'albedo'] = 0.002447757 #Calculated min albedo 6&7 o'clock
  
#Pick a specific day for closer data consideration
dayUnderConsideration = 224

df_inputs = df.iloc[dayUnderConsideration * 24:(dayUnderConsideration + 1) * 24, :] #rows to look at in .csv
df_inputs2 = df.iloc[dayUnderConsideration * 24:(dayUnderConsideration + 7) * 24, :] #rows to look at in .csv
    
df.to_excel(resultsPath + 'Dataframe.xlsx')

####################################################
       #Plot the albedo values for the whole year
f, (ax1) = plt.subplots(1, figsize=(12, 3))
df.plot(y='albedo')
plt.show()
f.savefig(resultsPath + "Albedo_" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)

#Plot albedo for a specific day
f, (ax1) = plt.subplots(1, figsize=(12, 3))
df_inputs[['albedo']].plot(ax=ax1)
ax1.locator_params(tight=True, nbins=6)
plt.show()
f.savefig(resultsPath + "Albedo_diurnal_development" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)

#Plot albedo for the following week
f, (ax1) = plt.subplots(1, figsize=(12, 3))
df_inputs2[['albedo']].plot(ax=ax1)
ax1.locator_params(tight=True, nbins=6)
plt.show()
f.savefig(resultsPath + "Albedo_weekly_development" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)

# Plot the data for displaying direct and diffuse irradiance
#print("\n Direct and Diffuse irradiance:") 

f, (ax1) = plt.subplots(1, figsize=(12, 3))
df_inputs[['dni', 'dhi']].plot(ax=ax1)
ax1.locator_params(tight=True, nbins=6)
ax1.set_ylabel('W/m2')
f.savefig(resultsPath + "Direct_Diffuse_irradiance:" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
plt.show(sns)


# Run full bifacial simulation

# Create ordered PV array and fit engine
pvarray = OrderedPVArray.init_from_dict(simulationParameter)

engine = PVEngine(pvarray)

engine.fit(df.index, df.dni, df.dhi,
           df.solar_zenith, df.solar_azimuth,
           df.surface_tilt, df.surface_azimuth,
           df.albedo)

# Devide PV array into segments
number_of_segments = {} # create empty list

# Create loop for defining the number of segments
for i in range(0, simulationParameter['n_pvrows']):
    number_of_segments[i] = len(pvarray.ts_pvrows[i].back.list_segments)
    
# Print Plot including Segments
#print("\n Segment Division:")    
f, ax = plt.subplots(figsize = (12,4))
pvarray.plot_at_idx(12,ax,with_surface_index = True)
ax.set_xlim(-3,20)
f.savefig(resultsPath + "Segment_Division" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
plt.show(sns)

####################################################
#AOI reflection losses

module_name = 'SunPower_128_Cell_Module___2009_'

# Create an faoi function
faoi_function = faoi_fn_from_pvlib_sandia(module_name)


# Helper functions for plotting and simulation with reflection losses
def plot_irradiance(df_report):
    # Plot irradiance
    f, ax = plt.subplots(nrows=1, ncols=2, figsize=(12, 4))
    
    # Plot back surface irradiance
    df_report[['qinc_back', 'qabs_back']].plot(ax=ax[0])
    ax[0].set_title('Back surface irradiance')
    ax[0].set_ylabel('W/m2')
    
    # Plot front surface irradiance
    df_report[['qinc_front', 'qabs_front']].plot(ax=ax[1])
    ax[1].set_title('Front surface irradiance')
    ax[1].set_ylabel('W/m2')
    plt.show()

def plot_aoi_losses(df_report):
    # plotting AOI losses
    f, ax = plt.subplots(figsize=(5.5, 4))
    df_report[['aoi_losses_back_%']].plot(ax=ax)
    df_report[['aoi_losses_front_%']].plot(ax=ax)
    
    # Adjust axes
    ax.set_ylabel('%')
    ax.legend(['AOI losses back PV row', 'AOI losses front PV row'])
    ax.set_title('AOI losses')
    plt.show()

# Create a function that will build a simulation report
def fn_report(pvarray):
    # Get irradiance values
    reportAOI = {'qinc_back': pvarray.ts_pvrows[1].back.get_param_weighted('qinc'),
              'qabs_back': pvarray.ts_pvrows[1].back.get_param_weighted('qabs'),
              'qinc_front': pvarray.ts_pvrows[1].front.get_param_weighted('qinc'),
              'qabs_front': pvarray.ts_pvrows[1].front.get_param_weighted('qabs')}
    
    # Calculate AOI losses
    reportAOI['aoi_losses_back_%'] = (reportAOI['qinc_back'] - reportAOI['qabs_back']) / reportAOI['qinc_back'] * 100.
    reportAOI['aoi_losses_front_%'] = (reportAOI['qinc_front'] - reportAOI['qabs_front']) / reportAOI['qinc_front'] * 100.
    # Return report
    return reportAOI

# Run full mode simulation
reportAOI = engine.run_full_mode(fn_build_report=fn_report)
# Turn report into dataframe
df_report_AOI = pd.DataFrame(reportAOI, index=df.index)

plot_irradiance(df_report_AOI)
####################################################
# Define Function calculating the total incident irradiance for the front and back side and the different segments of the backside

# qinc = total incident irradiance on a surface, and it does not account for reflection losses [W/m2]
# qabs = total absorbed irradiance by a surface [W/m2]

def Segments_report(pvarray):
    result = dict()
    
    for i in tqdm(range(0, len(pvarray.ts_pvrows))):
        
        row = pvarray.ts_pvrows[i]
        
        result["row_" + str(i) + "_qabs_front"] = row.front.get_param_weighted('qabs') #total qabs for every row front
        result["row_" + str(i) + "_qabs_back"] = row.back.get_param_weighted('qabs') #total qabs for every row back
        result["row_" + str(i) + "_qinc_front"] = row.front.get_param_weighted('qinc') #total qinc for every row front
        result["row_" + str(i) + "_qinc_back"] = row.back.get_param_weighted('qinc') #total qinc for every row back
        
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

# Run full simulation
report = engine.run_full_mode(fn_build_report=Segments_report)
df_report = pd.DataFrame(report, index=df.index)

# Print results as .csv in directory
df_report.to_excel(resultsPath + "radiation_qabs_results_" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".xlsx")
#df_report.iloc[6:11]

# Plot total qinc front and back for every row
f, ax = plt.subplots(3, figsize=(10, 6))
ax1.locator_params(tight=True, nbins=5)
df_report[['row_0_qinc_front', 'row_0_qinc_back']].plot(ax=ax[0])
df_report[['row_1_qinc_front', 'row_1_qinc_back']].plot(ax=ax[1])
df_report[['row_2_qinc_front', 'row_2_qinc_back']].plot(ax=ax[2])
ax[0].set_ylabel('W/m2')
ax[1].set_ylabel('W/m2')
ax[2].set_ylabel('W/m2')

f.savefig(resultsPath + "row0-3_qinc" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
plt.show(sns)

#print(df_report_AOI['aoi_losses_back_%'])


####################################################
# Calculate ViewFactors for Day of Consideration

# Instantiate calculator
vf_calculator = VFCalculator()

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
    
    result.to_csv(resultsPath + "view_factors_" + str(i) + "_" + str(j) + "_" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv") # Print ViewFactors to directory
    #print("\n View Factors:")
    #print('View factor from surface {} to surface {}: {}'.format(i, j, np.around(vf, decimals=2))) # in case the matrix should be printed in the console

save_view_factor(4, 46, vf_matrix, df.index)


####################################################
# Variablen, die benötigt werden:

# P_bi: Output power of bifacial module for bifacial illumination (W)
# I_sc_bi: Short-circuit current of bifacial module for bifacial illumination (A)
# V_oc: Open-circuit voltage of bifacial module for bifacial illumination (V)
# FF_bi: Fill factor of bifacial module for bifacial illumination (%)
# G_r: Irradiance on the rear side of the module (W/m2)
# G_f: Irradiance on the front side of the module (W/m2)
# R_isc: Relative current gain (dimensionless)
# I_sc_f: Short-circuit current measured for front side illumination of the module at STC (A)
# x: Irradiance ratio (dimensionless)
# V_oc_f: Open-circuit voltage measured for front side illumina- tion of module at STC (V)
# V_oc_r: Open-circuit voltage measured for rear side illumina- tion of module at STC (V)
# I_sc_r: Short-circuit current measured for rear side illumination of the module at STC (A)
# FF_f: Fill factor measured for front side illumination of the module at STC (%)
# FF_r: Fill factor measured for rear side illumination of the module (%)
# pFF: Pseudo fill factor (FF of the module considering no series resistance effect) (%)


####################################################
#SG
# Definition of simulation parameter
V_mpp_f0 = moduleParameter['V_mpp_f']
V_mpp_r0 = moduleParameter['V_mpp_r']

I_mpp_f0 = moduleParameter['I_mpp_f']
I_mpp_r0 = moduleParameter['I_mpp_r']

I_sc_r0 = moduleParameter['I_sc_r']
I_sc_f0 = moduleParameter['I_sc_f']

V_oc_r0 = moduleParameter['V_oc_r']
V_oc_f0 = moduleParameter['V_oc_f']

#module = moduleParameter['module']
#inverter = moduleParameter['inverter']

P_mpp0 = moduleParameter['P_mpp']
V_mpp0 = V_mpp_f0

T_koeff_P = moduleParameter['T_koeff_P'] 
T_koeff_I = moduleParameter['T_koeff_I'] 
T_koeff_V = moduleParameter['T_koeff_V'] 
T_amb = moduleParameter['T_amb']

q_stc_front = 1000  # [W/m^2] 
q_stc_rear = 1000   # [W/m^2] 

# Calculation of fill factor for STC conditions
FF_f0 = (I_mpp_f0 * V_mpp_f0)/(I_sc_f0 * V_oc_f0) 
FF_r0 = (I_mpp_r0 * V_mpp_r0)/(I_sc_r0 * V_oc_r0) 
#SG

####################################################
# Bifacial performance Calculation

# # Fillfactor Calculation for front and back
# FF_f = (V_mpp_f * I_mpp_f)/(V_oc_f * I_sc_f) # Fill factor measured for front side illumination of the module at STC [%/100]
# print("Fill Factor front: " + str(FF_f))

# FF_r = (V_mpp_r * I_mpp_r)/(V_oc_r * I_sc_r) # Fill factor measured for front back illumination of the module at STC [%/100]
# print("Fill Factor back: " + str(FF_r))
# print ("\n")

# Set Energy to Zero       
sum_energy_b = 0
sum_power_b = 0

# Array to hold other arrays -> average after for loop
P_bi_hourly_arrays = []

# Loop to calculate the Bifacial Output power for every row in every hour
for i in tqdm(range(0, simulationParameter['n_pvrows'])):
    
    key_front = "row_" + str(i) + "_qabs_front"
    key_back = "row_" + str(i) + "_qabs_back"

    P_bi_hourly = []

    #SG    

    for index, row in df_report.iterrows():
        
        row_qabs_front = row[key_front]
        row_qabs_back = row[key_back]
        T_Current = df.loc[index,'temperature']
        
        
        #print("front: " + str(row_qabs_front))
        #print("back: " + str(row_qabs_back))
        
        
        if row_qabs_back + row_qabs_front > 0.0:
            
            I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb))     
            I_sc_r = I_sc_r0 * (1 + T_koeff_I * (T_Current - T_amb))
            
            V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb))
            V_oc_r = V_oc_r0 * (1 + T_koeff_V * (T_Current - T_amb))
            
            FF_f = FF_f0 * ((1 + T_koeff_P * (T_Current-T_amb)) / ((1 + T_koeff_I * (T_Current - T_amb)) * (1 + T_koeff_V * (T_Current - T_amb))))
            FF_r = FF_r0 * ((1 + T_koeff_P * (T_Current-T_amb)) / ((1 + T_koeff_I * (T_Current - T_amb)) * (1 + T_koeff_V * (T_Current - T_amb))))
            
            I_sc_b = (row_qabs_front / q_stc_front) * I_sc_f + (row_qabs_back / q_stc_rear) * I_sc_r
            R_I_sc_b = I_sc_b / I_sc_f
            V_oc_b = V_oc_f + ((V_oc_r - V_oc_f) * np.log(R_I_sc_b) / np.log(I_sc_r / I_sc_f))
            
            pFF = ((I_sc_r0/I_sc_f0) * FF_f0 - (FF_r0 * (V_oc_r0 / V_oc_f0))) / ((I_sc_r0/I_sc_f0) - (V_oc_r0 / V_oc_f0))
            FF_b = pFF - (R_I_sc_b * (V_oc_f0 / V_oc_b) * (pFF - FF_f0))
        
            P_bi = FF_b * V_oc_b * I_sc_b
            #print("Power: " + str(P_bi))
    
            sum_energy_b += P_bi # Sum up the energy of every row in every hour
    
        else:
            P_bi=0
        
        P_bi_hourly.append(P_bi)
        
    # Append P_bi_hourly array to arrays
    P_bi_hourly_arrays.append(P_bi_hourly)
        
        
P_bi_hourly_average = []

for i in tqdm(range(0, len(P_bi_hourly_arrays[0]))):
    sum = 0
  
    for j in range(0, len(P_bi_hourly_arrays)):
        sum += P_bi_hourly_arrays[j][i]
        
    average = sum / float(len(P_bi_hourly_arrays))
    
    P_bi_hourly_average.append(average)
    
# Create dataframe with average data
p_bi_df = pd.DataFrame({"timestamps":df_report.index, "P_bi ": P_bi_hourly_average})
p_bi_df.set_index("timestamps")
p_bi_df.to_excel(resultsPath + "P_bi_LG" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".xlsx")


annual_power_per_module_b = (sum_energy_b/simulationParameter['n_pvrows']) #[W] annual bifacial output power per module
print("Yearly bifacial output power per module: " + str(annual_power_per_module_b) + " W/module")
print("Yearly bifacial output energy per module: " + str(annual_power_per_module_b/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
print ("\n")

annual_power_per_peak_b = (sum_energy_b/(P_mpp0 * simulationParameter['n_pvrows']))   #[W/Wp] annual bifacial output power per module peak power
print("Yearly bifacial output power per module peak power: " + str(annual_power_per_peak_b) + " W/Wp")
print("Yearly bifacial output energy per module peak power: " + str(annual_power_per_peak_b) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
print ("\n")

module_area = (simulationParameter['pvrow_width'] * simulationParameter['pvmodule_width'])

annual_power_per_area_b = (annual_power_per_module_b / module_area)    #[W/m^2] annual bifacial poutput power per module area
print("Yearly bifacial output power per module area: " + str(annual_power_per_area_b) + " W/m^2")
print("Yearly bifacial output energy per module area: " + str(annual_power_per_area_b/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
print ("\n")

# Plot total qinc front and back for every row
f, (ax1) = plt.subplots(1, figsize=(12, 3))
ax1.locator_params(tight=True, nbins=6)
plt.plot(df.index, P_bi_hourly)
f.savefig(resultsPath + "P_bi_hourly" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
plt.show(sns)


####################################################
# Monofacial performance Calculation

# Set Energy to Zero       
sum_energy_m = 0
sum_power_m = 0

# Loop to calculate the Monofacial Output power for every row in every hour
for i in tqdm(range(0, simulationParameter['n_pvrows'])):
    
    key_front_mono = "row_" + str(i) + "_qabs_front"
    
    for index, row in df_report.iterrows():
        
        row_qabs_front = row[key_front_mono]
        T_Current = df.loc[index,'temperature']
        
        
        #print("front: " + str(row_qabs_front))
        
        
        if  row_qabs_front > 0.0:
      
            V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleParameter['zeta'] * np.log(row_qabs_front / q_stc_front))
            I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
            P_m = FF_f0 * V_oc_f * I_sc_f
        
            #print("Power: " + str(P_bi))
     
            sum_energy_m += P_m # Sum up the energy of every row in every hour
        
         #else:
            #print("Power: 0.0")

annual_power_per_module_m = (sum_energy_m/simulationParameter['n_pvrows']) #[W] annual monofacial output power per module
print("Yearly monofacial output power per module: " + str(annual_power_per_module_m) + " W/module")
print("Yearly monofacial output energy per module: " + str(annual_power_per_module_m/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
print ("\n")

annual_power_per_peak_m = (sum_energy_m/(P_mpp0 * simulationParameter['n_pvrows']))   #[W/Wp] annual monofacial output power per module peak power
print("Yearly monofacial output power per module peak power: " + str(annual_power_per_peak_m) + " W/Wp")
print("Yearly monofacial output energy per module peak power: " + str(annual_power_per_peak_m) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
print ("\n")

module_area = (simulationParameter['pvrow_width'] * simulationParameter['pvmodule_width'])

annual_power_per_area_m = (annual_power_per_module_m / module_area)    #[W/m^2] annual monofacial poutput power per module area
print("Yearly monofacial output power per module area: " + str(annual_power_per_area_m) + " W/m^2")
print("Yearly monofacial output energy per module area: " + str(annual_power_per_area_m/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
print ("\n")

####################################################

# Bifacial Gain Calculation

Bifacial_gain= (annual_power_per_peak_b - annual_power_per_peak_m) / annual_power_per_peak_m
print("Bifacial Gain: " + str(Bifacial_gain*100) + " %")

