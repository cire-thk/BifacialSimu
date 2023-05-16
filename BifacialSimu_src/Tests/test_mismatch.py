import os
import sys
rootPath = os.path.realpath("../")
sys.path.append(rootPath)

import unittest
import csv
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from BifacialSimu.Handler.BifacialSimu_calculationHandler import Electrical_simulation as ES



class TestMistmatch (unittest.TestCase):
    
    def test_calculate_mismatch(self):
        
        a=[0]
        b= 0
        m= ES.calculate_mismatch(a, b)
        self.assertTrue(math.isnan(m)) #testing break of function in case P_mpp was zero
        
    def test_calculate_mismatc(self):    
        a=[100,75,50,25,10,0]
        b=100
        m= ES.calculate_mismatch(a, b)
        self.assertEqual(m[0], 0.0)
        self.assertEqual(m[1], 25.0)
        self.assertEqual(m[2], 50.0)
        self.assertEqual(m[3], 75.0)
        self.assertEqual(m[4], 90.0)
        self.assertEqual(m[5], 100.0)
        
if __name__ == '__main__':
    unittest.main()
        
        