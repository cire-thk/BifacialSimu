# Test for the simulate_doubleDiode function in BifacialSimu_calculationHandler
# Mainly testing the Bifacial Gian end results of the simulations

# from IPython import get_ipython
# get_ipython().magic('reset -sf')
  
import unittest
import pandas as pd #pandas = can read .csv as input
import matplotlib.pyplot as plt #display shadows
import numpy as np
import os #to import directories
import sys

sys.path.append('../')
from bifacial_radiance import *
import datetime
from tqdm import tqdm
import math
import dateutil.tz

from BifacialSimu.Handler import BifacialSimu_radiationHandler 
from BifacialSimu.Handler.BifacialSimu_calculationHandler import Electrical_simulation
    


def test_simulate_doubleDiode():
    
    assert simulate_doubleDiode(M_Dict, S_Dict, df_reportVF, df_reportRT, df_report, df, resultsPath) == 9.4575142278105062
    
print('done with no errors')