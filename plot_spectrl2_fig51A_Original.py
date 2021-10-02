"""
Modeling Spectral Irradiance
============================

Recreating Figure 5-1A from the SPECTRL2 NREL Technical Report.
"""

# %%
# This example shows how to model the spectral distribution of irradiance
# based on atmospheric conditions. The spectral distribution of irradiance is
# the power content at each wavelength band in the solar spectrum and is
# affected by various scattering and absorption mechanisms in the atmosphere.
# This example recreates an example figure from the SPECTRL2 NREL Technical
# Report [1]_. The figure shows modeled spectra at hourly intervals across
# a single morning.
#
# References
# ----------
# .. [1] Bird, R, and Riordan, C., 1984, "Simple solar spectral model for
#    direct and diffuse irradiance on horizontal and tilted planes at the
#    earth's surface for cloudless atmospheres", NREL Technical Report
#    TR-215-2436 doi:10.2172/5986936.

# %%
# The SPECTRL2 model has several inputs; some can be calculated with pvlib,
# but other must come from a weather dataset. In this case, these weather
# parameters are example assumptions taken from the technical report.

from pvlib import spectrum, solarposition, irradiance, atmosphere
import pandas as pd
import matplotlib.pyplot as plt

simulationDict = {
'simulationName' : 'NREL_best_field_row_2',
'simulationMode' : 1, 
'localFile' : True, # Decide wether you want to use a  weather file or try to download one for the coordinates
#'weatherFile' : (rootPath +'/WeatherData/Golden_USA/SRRLWeatherdata Nov_Dez.csv'), #weather file in TMY format 
#'spectralReflectancefile' : (rootPath + '/ReflectivityData/interpolated_reflectivity.csv'),
'cumulativeSky' : False, # Mode for RayTracing: CumulativeSky or hourly
'startHour' : (2019, 11, 1, 2),  # Only for hourly simulation, yy, mm, dd, hh
'endHour' : (2019, 11, 1, 3),  # Only for hourly simulation, yy, mm, dd, hh
'utcOffset': +2,
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
'spectralAlbedo' : True, #Option to calculate a spectral Albedo 
'albedo' : 0.26, # Measured Albedo average value, if hourly isn't available
'frontReflect' : 0.03, #front surface reflectivity of PV rows
'BackReflect' : 0.05, #back surface reflectivity of PV rows
'longitude' : 6.992, 
'latitude' : 50.935,
'gcr' : 0.35, #ground coverage ratio (module area / land use)
'module_type' : 'NREL row 2', #Name of Module
}

# assumptions from the technical report:
lat = simulationDict['latitude']    # [deg] latitude of ground surface to calculate spectral albedo
lon = simulationDict['longitude']   # [deg] longitude of ground surface to calculate spectral albedo
tilt = 0                            # [deg] always 0, because the ground is never tilted
azimuth = simulationDict['azimuth'] # [deg] same azimuth for ground surface as for PV panel
pressure = 100498                   # [Pa] air pressure; average of yearly values from 1958 to 2020 for airport Cologne/Bonn, taken from DWD
water_vapor_content = 1.551         # [cm] Atmospheric water vapor content; data from AERONET for FZ Juelich for Sep 2021; Level 2 Quality
tau500 = 0.221                      # [-] aerosol optical depth at wavelength 500 nm; data from AERONET for FZ Juelich for Sep 2021; Level 2 Quality
ozone = 0.314                       # [atm-cm] Atmospheric ozone content; data from WOUDC for Aug 2021 for Hohenpeissenberg
albedo = simulationDict['albedo']   # [-] fix albedo value
'''
cd= '2019-11-01 12:00'
if int(simulationDict['utcOffset']) >= 0:
    times = pd.date_range(start=cd, freq='h', periods=1, tz='Etc/GMT+' + str(simulationDict['utcOffset'])) # posibility to calculate several spectras for diffrent times, when period >1
else:
    times = pd.date_range(start=cd, freq='h', periods=1, tz='Etc/GMT' + str(simulationDict['utcOffset'])) # posibility to calculate several spectras for diffrent times, when period >1

'''
cd= '2019-11-01 12:00'
times = pd.date_range(cd, freq='h', periods=1, tz='Etc/GMT+'+ str(simulationDict['utcOffset']))
print(times)
solpos = solarposition.get_solarposition(times, lat, lon)
print(solpos.apparent_zenith)
print(solpos.zenith)
print(solpos.apparent_elevation)
print(solpos.elevation)
aoi = irradiance.aoi(tilt, azimuth, solpos.apparent_zenith, solpos.azimuth)
print(aoi)

# The technical report uses the 'kasten1966' airmass model, but later
# versions of SPECTRL2 use 'kastenyoung1989'.  Here we use 'kasten1966'
# for consistency with the technical report.
relative_airmass = atmosphere.get_relative_airmass(solpos.apparent_zenith,
                                                   model='kasten1966')
print(relative_airmass)
# %%
# With all the necessary inputs in hand we can model spectral irradiance using
# :py:func:`pvlib.spectrum.spectrl2`.  Note that because we are calculating
# the spectra for more than one set of conditions, we will get back 2-D
# arrays (one dimension for wavelength, one for time).

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

# %%
# The ``poa_global`` array represents the total spectral irradiance on our
# hypothetical solar panel. Let's plot it against wavelength to recreate
# Figure 5-1A:
'''
plt.figure()
plt.plot(spectra['wavelength'], spectra['poa_global'])
plt.xlim(200, 2700)
plt.ylim(0, 1.8)
plt.title(r"Day 80 1984, $\tau=0.1$, Wv=0.5 cm")
plt.ylabel(r"Irradiance ($W m^{-2} nm^{-1}$)")
plt.xlabel(r"Wavelength ($nm$)")
time_labels = times.strftime("%H:%M %p")
labels = [
    "AM {:0.02f}, Z{:0.02f}, {}".format(*vals)
    for vals in zip(relative_airmass, solpos.apparent_zenith, time_labels)
]
plt.legend(labels)
plt.show()
'''
# %%
# Note that the airmass and zenith values do not exactly match the values in
# the technical report; this is because airmass is estimated from solar
# position and the solar position calculation in the technical report does not
# exactly match the one used here.  However, the differences are minor enough
# to not materially change the spectra.
