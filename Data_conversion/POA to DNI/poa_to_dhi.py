# -*- coding: utf-8 -*-
"""
Created on Sat Jun 24 02:21:19 2023

@author: max2k
"""

import pandas as pd
import numpy as np
import pvlib



df = pd.read_csv('poa_data.csv', parse_dates=['timestamps'], dayfirst=True, index_col='timestamps')
df = df.resample('1H').mean()

latitude, longitude = -27.43, -47.853  # Beispiel für Frankfurt, Deutschland


location = pvlib.location.Location(latitude, longitude)

solar_position = location.get_solarposition(df.index)

surface_tilt = 35
surface_azimuth = 30  

# Schätzung der globalen horizontalen Bestrahlung (GHI)
df['ghi'] = (df['poa_front'] + df['poa_back']) / np.cos(np.radians(surface_tilt))

# Schätzung der direkten normalen Bestrahlung (DNI) mit dem DISC-Modell
disc = pvlib.irradiance.disc(df['ghi'], solar_position['zenith'], df.index)
df['dni'] = disc['dni']

# Berechnung der diffusen horizontalen Bestrahlung (DHI) 
df['dhi'] = df['ghi'] - df['dni'] * np.cos(np.radians(solar_position['zenith']))



df = df.clip(lower=0)


print(df.head())
df.to_csv('dhi.csv', index=True, encoding='utf-8-sig', na_rep='0')