# -*- coding: utf-8 -*-
"""
Created on Wed Sep 29 20:03:21 2021

@author: sarah

name:
    InterpolationReflectivityData

overview:
    Import the csv file of the reflectivtiy data of the material for spectral albedo calculation
    Interpolate the reflectivity data for specific wavelength to use it in spectralAlbedoHandler.py
    Save the interpolated reflectivity data and the corresponding wavelength in a csv file

last changes:
    29.09.21 created
"""

import numpy as np
import os
import pandas as pd

rootPath = os.path.realpath(".")
filename = 'brown_to_dark_brown_sand_original'

# array with wavelength for which reflectivity values should be interpolated
'''
x = [310., 315., 320., 325., 330., 335., 340., 345., 350., 360., 370., 380., 390., 400., 410.,
     420., 430., 440., 450., 460., 470., 480., 490., 500., 510., 520., 530., 540., 550., 570., 593., 610.,
     630., 656., 667.6, 690., 710., 718., 724.4, 740., 752.5, 757.5, 762.5, 767.5, 780., 800., 816., 823.7,
     831.5, 840., 860., 880., 905., 915., 925., 930., 937., 948., 965., 980., 993.5, 1040., 1070., 1100.,
     1120., 1130., 1145., 1161., 1170., 1200., 1240., 1270., 1290., 1320., 1350., 1395., 1442.5, 1462.5,
     1477., 1497., 1520., 1539., 1558., 1578., 1592., 1610., 1630., 1646., 1678., 1740., 1800., 1860.,
     1920., 1960., 1985., 2005., 2035., 2065., 2100., 2148., 2198., 2270., 2360., 2450., 2500., 2600.,
     2700., 2800. ]
'''
x = [400., 410.,
     420., 430., 440., 450., 460., 470., 480., 490., 500., 510., 520., 530., 540., 550., 570., 593., 610.,
     630., 656., 667.6, 690., 710., 718., 724.4, 740., 752.5, 757.5, 762.5, 767.5, 780., 800., 816., 823.7,
     831.5, 840., 860., 880., 905., 915., 925., 930., 937., 948., 965., 980., 993.5, 1040., 1070., 1100.,
     1120., 1130., 1145., 1161., 1170., 1200., 1240., 1270., 1290., 1320., 1350., 1395., 1442.5, 1462.5,
     1477., 1497., 1520., 1539., 1558., 1578., 1592., 1610., 1630., 1646., 1678., 1740., 1800., 1860.,
     1920., 1960., 1985., 2005., 2035., 2065., 2100., 2148., 2198., 2270., 2360., 2450., 2500., 2600.,
     2700., 2800.]

# arrray with all wavelength from extern data file
wavelength = np.genfromtxt(rootPath + '/' + filename + '.csv', delimiter=';', skip_header = 1, usecols=(0))
# array with all reflectivity values from extern data file
reflectivity = np.genfromtxt(rootPath + '/' + filename + '.csv', delimiter=';', skip_header = 1, usecols=(1))

# numpy interpolation function
# attention: if maximum value of x is bigger than wavelength array, wrong values are written in the interpol_reflec array for the bigger wavelength values
# has to be considered when using the interpolated values further in spectralAlbedoHandler.py
interpol_reflec = np.interp(x, wavelength, reflectivity)
print(interpol_reflec)

# create pandas dataframe to save both arrays and give them headers
df = pd.DataFrame({'wavelength [nm]':x, 'reflectivity':interpol_reflec})
print(df)
# save pandas dataframe into a csv file
df.to_csv(filename + '_interpolated.csv', sep=';', index=False)
