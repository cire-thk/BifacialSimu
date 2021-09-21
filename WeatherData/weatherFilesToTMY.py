# -*- coding: utf-8 -*-
"""
Created on Tue May 18 10:42:51 2021

@author: Sebastian Nows
"""

import pandas


# Information about weather data file

path ="C:/Users/Sebastian Nows/OneDrive - th-koeln.de/Masterprojekt/50_Wetterdaten/71_Strahlungsdaten DWD/Göttingen/"
name= "Goettingen_Temperatur_Strahlung_stündlich_bearbeitet.csv"

separator = ";"
headline = 0

nrMeasuringStation = '1691'
nameMeasuringStation = 'Goettingen'
longitude = '9.9507'
latitude = '51.5002' 
height = '167'
offset = '-1'
state = 'Germany'
# names of relevant coloumns in weather file, each of them have to be in seperated columns
Date = 'date'
Time = 'time'
GHI = 'ghi'
DHI = 'dhi'
DNI = 'dni'
Drybulb = 'drybulb'
Wspd = 'windspeed'
Pressure = 'Air pressure (Pa)'
Albedo = 'alb'



def csvToTMY3(path, name, separator, headline, nrMeasuringStation, 
              nameMeasuringStation, longitude, latitude, height, offset, Date, 
              Time, GHI, DNI, Drybulb, Wspd, Pressure, Albedo):
    
    df = pandas.read_csv(path+name, sep = separator, header = headline, encoding = "latin1")
    columns= df.columns.values    
    print(df)
    
    # Rename columns for calculation
    #df = df.assign(date2=df[Date].str[3:5]+'/'+df[Date].str[:2]+df[Date].str[5:10])
    #df = df.assign(Alb=Albedo)
    df = df.rename(columns = {Date: 'Date (MM/DD/YYYY)'})
    df = df.rename(columns = {Time: 'Time (HH:MM)'})
    #df = df.rename(columns = {Albedo: 'Alb'})
    df = df.rename(columns = {GHI: 'GHI (W/m^2)'})
    df = df.rename(columns = {DHI: 'DHI (W/m^2)'})
    df = df.rename(columns = {DNI: 'DNI (W/m^2)'})
    df = df.rename(columns = {Drybulb: 'Dry-bulb (C)'})
    #df = df.rename(columns = {Wspd: 'Wspd (m/s)'})
    #df = df.rename(columns = {Pressure: 'Pressure (mbar)'})
    #df = df.drop(Date, axis = 1)
    
    with open(path+'out.csv', 'w') as fp:
        fp.write(nrMeasuringStation+','+nameMeasuringStation+','+state+','+ offset+','+latitude+','+longitude+','+height+'\n'+'\n')
        df.to_csv(fp, index=False)
    print(df)

run = csvToTMY3(path, name, separator, headline, nrMeasuringStation,nameMeasuringStation, longitude, latitude, height, offset, Date, Time, GHI, DNI, Drybulb, Wspd, Pressure, Albedo)