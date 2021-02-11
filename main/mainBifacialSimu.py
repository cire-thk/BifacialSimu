 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 12:57:54 2019

@author:        Eva-Maria Grommes
Master thesis:  Impact of dust and red soil on the annual yield of Bifacial PV-modules in Ghana

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
from pvlib.location import Location

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


LOCAL_DIR = os.getcwd()
DATA_DIR = os.path.join(LOCAL_DIR, 'C:/Users/Sebastian Nows/OneDrive - th-koeln.de/Masterprojekt/50_Python Simulation/NREL/SRRL Weather Data')
#DATA_DIR = os.path.join(LOCAL_DIR, 'C:/Users/Sebastian Nows/OneDrive - th-koeln.de/Masterprojekt/50_Python Simulation')

#DATA_DIR = os.path.join(LOCAL_DIR, 'C:/Users/fredk/th-koeln.de/Masterprojekt Bifacial Simulation - Dokumente/50_Python Simulation')
#DATA_DIR = os.path.join(LOCAL_DIR, 'C:/Users/fredk/th-koeln.de/Masterprojekt Bifacial Simulation - Dokumente/50_Python Simulation/NREL/SRRL Weather Data')

#DATA_DIR = os.path.join(LOCAL_DIR, 'C:/Users/Felix/th-koeln.de/Masterprojekt Bifacial Simulation - Documents/50_Python Simulation/NREL/SRRL Weather Data')


#filepath = os.path.join(DATA_DIR, 'Ghana_Reference.csv')
filepath = os.path.join(DATA_DIR, 'SRRL Weatherdata 3.csv')

# Create directories
     
measurementsPath = DATA_DIR + "/" + "Berechnungen"
                
if not os.path.exists(measurementsPath):
    os.mkdir(measurementsPath)

dpi = 150 #Quality for plot export

#########################################################
    
# Dictionary for Input Parameters
simulationParameter = {
    'n_pvrows': 3, #number of PV rows
    'number_of_segments': 5, #number of segments for each PVrow
    'pvrow_height': 1.50, #mounting height of the PV rows, measured at their center [m]
    'pvrow_width': 2.0, #width of the PV panel in row, (but width doesn't mean width, actually it means length) considered 2D plane [m]
    'surface_azimuth': 180, #azimuth of the PV surface [deg] 90°= East, 135° = South-East, 180°=South
    'surface_tilt': 35, #tilt of the PV surface [deg]
    'albedo': 0.26, # Measured Albedo average value
    #'index_observed_pvrow': 1, #index of the PV row, whose incident irradiance will be returned
    'rho_front_pvrow' : 0.03, #front surface reflectivity of PV rows
    'rho_back_pvrow' : 0.05, #back surface reflectivity of PV rows
    'horizon_band_angle' : 6.5, #elevation angle of the sky dome's diffuse horizon band [deg]   
    

    'UTC_Time_Zone': 'US/Mountain', # https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
    'City':'Golden',
    'Longitude_Position': -105, #Longitude of measurement position [deg]
    'Longitude_Area': -105, #Longitude of timezone area [deg]
    'Latitude_Position': 39.7, #Latitude of measurement position [deg]

    
# =============================================================================
#     'UTC_Time_Zone': 'US/Arizona', # https://en.wikipedia.org/wiki/List_of_tz_database_time_zones
#     'City':'Golden',
#     'Longitude_Position': -111, #Longitude of measurement position [deg]
#     'Longitude_Area': -111, #Longitude of timezone area [deg]
#     'Latitude_Position': 32.2, #Latitude of measurement position [deg]
# =============================================================================
    
    'axis_azimuth': 0.0, #Axis Azimuth angle [deg]
    'gcr': 0.35, #ground coverage ratio (module area / land use)
}

position = Location(simulationParameter["Latitude_Position"], simulationParameter['Longitude_Position'], simulationParameter['UTC_Time_Zone'], 700, simulationParameter['City'])
print(position)
   
    
irradiance_model = HybridPerezOrdered(rho_front=simulationParameter['rho_front_pvrow'], rho_back=simulationParameter['rho_back_pvrow']) #choose an irradiance model

# Dictionary for Module Parameters

#NREL Row 2
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
    'T_koeff': -0.0036, #Temperature Coeffizient [1/°C]
    'T_amb':20, #Ambient Temperature for measuring the Temperature Coeffizient [°C]
    
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
    df = df.rename(columns = {'date2': 'timestamps'})
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

df = export_data(filepath) #print(df)

#########################################################

#Pick a specific day for closer data consideration
dayUnderConsideration = 1

df_inputs = df.iloc[dayUnderConsideration * 24:(dayUnderConsideration + 1) * 24, :] #rows to look at in .csv

# Plot the data for displaying direct and diffuse irradiance
#print("\n Direct and Diffuse irradiance:") 

f, (ax1) = plt.subplots(1, figsize=(12, 3))
df_inputs[['dni', 'dhi']].plot(ax=ax1)
ax1.locator_params(tight=True, nbins=6)
ax1.set_ylabel('W/m2')
f.savefig("Direct_Diffuse_irradiance:" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
plt.show(sns)

# Measured Albedo average value
albedo = simulationParameter['albedo']


#########################################################
#Calculation of sun parameters

    # Begin loop: Calculate for every hour 
for index, row in df.iterrows():
    surface_tilt = simulationParameter['surface_tilt']
    surface_azimuth = simulationParameter['surface_azimuth']
df['surface_tilt'] = surface_tilt
df['surface_azimuth'] = surface_azimuth

times = pd.date_range(start=datetime(2019,10,1), end=datetime(2020,5,1), freq='60Min', ambiguous=True)

#ephem_pos = pvlib.solarposition.get_solarposition(times.tz_localize(position.tz, ambiguous='NaT',nonexistent='NaT'), position.latitude, position.longitude)
ephem_pos = pvlib.solarposition.get_solarposition(pd.date_range(start='2019/10/01 00:00', end= '2020/05/01 00:00', freq='H'), position.latitude, position.longitude)

ephem_pos.to_csv(measurementsPath + '/Sonnenstand.csv')
#ephemout = ephem_pos.tz_convert(None)
ephemout = ephem_pos

df.to_excel(measurementsPath + '/Wetterdaten.xlsx')
ephemout.to_excel(measurementsPath + '/Sonnenstand.xlsx')
dfSun = df.join(ephemout)
dfSun.index.name = "datetime"
dfSun.to_excel(measurementsPath + '/Sonnenstand_gesamt.xlsx')

####################################################

# Run full bifacial simulation

# Create ordered PV array and fit engine
pvarray = OrderedPVArray.init_from_dict(simulationParameter)

engine = PVEngine(pvarray)

engine.fit(dfSun.index, dfSun.dni, dfSun.dhi,
           dfSun.azimuth, dfSun.zenith,
           dfSun.surface_tilt, dfSun.surface_azimuth,
           albedo)

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
f.savefig("Segment_Division" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
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

#ts=timeseries 

def Segments_report(pvarray):
    result = dict()
    
    for i in range(0, len(pvarray.ts_pvrows)):
        
        row = pvarray.ts_pvrows[i]
        
        result["row_" + str(i) + "_qabs_front"] = row.front.get_param_weighted('qabs') #avg qabs for every row front
        result["row_" + str(i) + "_qabs_back"] = row.back.get_param_weighted('qabs') #avg qabs for every row back
        result["row_" + str(i) + "_qinc_front"] = row.front.get_param_weighted('qinc') #avg qinc for every row front
        result["row_" + str(i) + "_qinc_back"] = row.back.get_param_weighted('qinc') #avg qinc for every row back
        
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
df_report.to_excel("radiation_qabs_results_" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".xlsx")
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

f.savefig("row0-3_qinc" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
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
    
    result.to_csv("view_factors_" + str(i) + "_" + str(j) + "_" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv") # Print ViewFactors to directory
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

# Definition of simulation parameter
V_mpp_f = moduleParameter['V_mpp_f']
V_mpp_r = moduleParameter['V_mpp_r']

I_mpp_f = moduleParameter['I_mpp_f']
I_mpp_r = moduleParameter['I_mpp_r']

I_sc_r = moduleParameter['I_sc_r']
I_sc_f = moduleParameter['I_sc_f']

V_oc_r = moduleParameter['V_oc_r']
V_oc_f = moduleParameter['V_oc_f']

#module = moduleParameter['module']
#inverter = moduleParameter['inverter']

P_mpp = moduleParameter['P_mpp']
V_mpp = V_mpp_f

T_koeff =moduleParameter['T_koeff']
T_amb =moduleParameter['T_amb']

####################################################
# Bifacial performance Calculation

# Fillfactor Calculation for front and back
FF_f = (V_mpp_f * I_mpp_f)/(V_oc_f * I_sc_f) # Fill factor measured for front side illumination of the module at STC [%/100]
print("Fill Factor front: " + str(FF_f))

FF_r = (V_mpp_r * I_mpp_r)/(V_oc_r * I_sc_r) # Fill factor measured for front back illumination of the module at STC [%/100]
print("Fill Factor back: " + str(FF_r))
print ("\n")

# Set Energy to Zero       
sum_energy = 0
sum_power = 0

# Array to hold other arrays -> average after for loop
P_bi_hourly_arrays = []

# Loop to calculate the Bifacial Output power for every row in every hour
for i in range(0, simulationParameter['n_pvrows']):
    
    key_front = "row_" + str(i) + "_qabs_front"
    key_back = "row_" + str(i) + "_qabs_back"

    P_bi_hourly = []

    
    for index, row in df_report.iterrows():
        
        row_qabs_front = row[key_front]
        row_qabs_back = row[key_back]
        Current_Temp = df.loc[index,'temperature']
        
        
        #print("front: " + str(row_qabs_front))
        #print("back: " + str(row_qabs_back))
        
        
        if row_qabs_back + row_qabs_front > 0.0:
            x = row_qabs_back / row_qabs_front # Irradiance ratio (dimensionless)
        
            if math.isnan(x):   # necessary for the night to prevent deviding through Zero
                print("is nan")          
        
            R_isc = 1 + x * (I_sc_r / I_sc_f) # Relative current gain (dimensionless)
            I_sc_bi = I_sc_f * R_isc # Short-circuit current of bifacial module for bifacial illumination [A]
            
            V_oc_bi = V_oc_f + ((V_oc_r-V_oc_f)*np.log(R_isc))/(np.log(I_sc_r/I_sc_f)) # Open-circuit voltage of bifacial module for bifacial illumination [V]
            
            pFF = (((I_sc_r/I_sc_f)*FF_f)-(FF_r*(V_oc_r/V_oc_f)))/((I_sc_r/I_sc_f)-(V_oc_r/V_oc_f)) # Pseudo fill factor (FF of the module considering no series resistance effect) [%]
            FF_bi = pFF - R_isc*(V_oc_f/V_oc_bi)*(pFF-FF_f) #  Fill factor of bifacial module for bifacial illumination [%]
            P_bi = I_sc_bi*V_oc_bi*FF_bi*(1+T_koeff*(Current_Temp-T_amb)) # Output power of bifacial module for bifacial illumination [W]
            #print("Power: " + str(P_bi))
     
            sum_energy += P_bi # Sum up the energy of every row in every hour
   
        else:
            P_bi=0
        
        P_bi_hourly.append(P_bi)
        
    # Append P_bi_hourly array to arrays
    P_bi_hourly_arrays.append(P_bi_hourly)
        
        
P_bi_hourly_average = []

for i in range(0, len(P_bi_hourly_arrays[0])):
    sum = 0
  
    for j in range(0, len(P_bi_hourly_arrays)):
        sum += P_bi_hourly_arrays[j][i]
        
    average = sum / float(len(P_bi_hourly_arrays))
    
    P_bi_hourly_average.append(average)
    
# Create dataframe with average data
p_bi_df = pd.DataFrame({"timestamps":df_report.index, "P_bi ": P_bi_hourly_average})
p_bi_df.set_index("timestamps")
p_bi_df.to_excel("P_bi_LG" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".xlsx")
    

sum_power = (sum_energy/simulationParameter['n_pvrows'])
print("Yearly bifacial module output power: " + str(sum_power) + " Wh/m^2")
print("Yearly bifacial module output energy: " + str(sum_power/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
print ("\n")

# Plot total qinc front and back for every row
f, (ax1) = plt.subplots(1, figsize=(12, 3))
ax1.locator_params(tight=True, nbins=6)
plt.plot(df.index, P_bi_hourly)
f.savefig("P_bi_hourly" + datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
plt.show(sns)


####################################################
# Monofacial performance Calculation

# Set Energy to Zero       
sum_energy_mono = 0
sum_power_mono = 0

# Loop to calculate the Monofacial Output power for every row in every hour
for i in range(0, simulationParameter['n_pvrows']):
    
    key_front_mono = "row_" + str(i) + "_qabs_front"
    
    for index, row in df_report.iterrows():
        
        row_qabs_front = row[key_front_mono]
        Current_Temp = df.loc[index,'temperature']
        
        
        #print("front: " + str(row_qabs_front))
        
        
        if  row_qabs_front > 0.0:
        
            if math.isnan(x):   # necessary for the night to prevent deviding through Zero
                print("is nan")          
        
            R_isc = (I_sc_r / I_sc_f) # Relative current gain (dimensionless)
            I_sc_bi = I_sc_f * R_isc # Short-circuit current of bifacial module for bifacial illumination [A]
            
            V_oc_bi = V_oc_f + ((V_oc_r-V_oc_f)*np.log(R_isc))/(np.log(I_sc_r/I_sc_f)) # Open-circuit voltage of bifacial module for bifacial illumination [V]
            
            pFF = (((I_sc_r/I_sc_f)*FF_f)-(FF_r*(V_oc_r/V_oc_f)))/((I_sc_r/I_sc_f)-(V_oc_r/V_oc_f)) # Pseudo fill factor (FF of the module considering no series resistance effect) [%]
            FF_bi = pFF - R_isc*(V_oc_f/V_oc_bi)*(pFF-FF_f) #  Fill factor of bifacial module for bifacial illumination [%]
            P_bi = I_sc_bi*V_oc_bi*FF_bi*(1+T_koeff*(Current_Temp-T_amb)) # Output power of bifacial module for bifacial illumination [W]
            #print("Power: " + str(P_bi))
     
            sum_energy_mono += P_bi # Sum up the energy of every row in every hour
   
        #else:
            #print("Power: 0.0")

sum_power_mono = (sum_energy_mono/simulationParameter['n_pvrows'])
print("Yearly module monofacial output power: " + str(sum_power_mono) + " Wh/m^2")
print("Yearly module monofacial output energy: " + str(sum_power_mono/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
print ("\n")

####################################################

# Bifacial Gain Calculation

Bifacial_gain= (sum_power-sum_power_mono)/sum_power_mono
print("Bifacial Gain: " + str(Bifacial_gain*100) + " %")