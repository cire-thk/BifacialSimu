# -*- coding: utf-8 -*-
"""
Created on Wed Sep 15 17:53:38 2021

@author: Sarah Glaubitz

name: BiSim - spectralAlbedoHandler

overview:
    Calculation of spectral Albedo
    
last changes:
    15.09.2021 created
"""

import pandas as pd

import BiSim_dataHandler
import BiSim_radiationHandler

def getReflectanceData():
    '''
    Read the spectral Reflectance data of the material (sand)

    Returns
    -------
    None.

    '''
    # If-Abfrage, ob Werte ungleich -1.23e+34 sind, da Werte dann ungültig
    # Eingelesene Werte müssen geschnitten werden, da diese in wissenschaftlichen Format
    
def getGlobalIrradianceData():
    '''
    Read the spectral global irradiance

    Returns
    -------
    None.

    '''
    
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