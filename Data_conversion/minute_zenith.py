# -*- coding: utf-8 -*-
"""
Created on Mon Nov  1 11:49:36 2021

@author:        
    Eva-Maria Grommes
    Sarah Glaubitz

Additional co-authors can be found here:
https://github.com/cire-thk/bifacialSimu    

"""
import pandas as pd
from pvlib import solarposition

lat =50.935
lon = 6.992
alitude = 53

times = pd.date_range('2021-09-23 00:00', freq='T', periods=23040, tz='Etc/GMT-2')
solpos = solarposition.get_solarposition(times, lat, lon, alitude)

zenith = solpos.zenith

print(zenith)

zenith.to_csv('minute_zenith.csv', sep=',')