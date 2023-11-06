#  -*- coding: utf-8 -*-
    # -*- coding: utf-8 -*-
"""
Created on Mon Jun  7 11:39:16 2021
@author:        
    Eva-Maria Grommes
    Jan Schmitt

Additional co-authors can be found here:
https://github.com/cire-thk/bifacialSimu    

name:
    Bifacial Simu - GUI
overview:
    Import of needed modules and paths.
    Input of variables and settings for the bifacial simulation of PV-Modules 
    with View Factors and/or Ray Tracing method. 
    Command to run the simulation
    
"""

# Import modules
#import matplotlib
#matplotlib.use("TkAgg")
import sys
import math
#<<<<<<< HEAD
import csv
import os
import webbrowser
from tkinter import *
from math import radians, cos, sin, asin, sqrt
#=======
import os
import webbrowser
from tkinter import *
import time
from datetime import datetime
from timezonefinder import TimezoneFinder as tf
import pytz
#>>>>>>> master

import dateutil.tz
import inspect
# seaborn makes your plots look better
try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog
    from tkinter import messagebox
    from tkinter.messagebox import showinfo        # Import of showinfo to get the event response of tkinter objects (is not used in the program yet)
    
    
except:
    import Tkinter as tk
    import ttk

from configparser import ConfigParser
#import bifacial_radiance
#import warnings
# Import of needed paths
# Get path of this (GUI.py) file. See: https://stackoverflow.com/a/44592299
filename = inspect.getframeinfo(inspect.currentframe()).filename
rootPath = os.path.dirname(os.path.abspath(filename))

# Include path in system path, so that python would find the Modules
sys.path.append(rootPath)

# Path handling
#rootPath = rootPath = os.path.realpath("../../")

#adding rootPath to sysPath
#sys.path.append(rootPath)


from matplotlib import pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as dates
import json
from PIL import ImageTk,Image
import datetime
import csv
import inspect
import numpy as np
import pandas as pd
#import time
#import pickle
import threading #for using multiple threads to make the GUI responsive during simulations
from BifacialSimu_src import globals
from geopy.distance import geodesic as GD # needed to find closest weatherstation to simulation location
import pvlib #needed to read TMY file to get coordinates
import pathlib  # for finding the example dataset
#from datetime import datetime

import matplotlib.pyplot as plt

globals.initialize()

# aliases for Tkinter functions
END = tk.END
W = tk.W
Entry = tk.Entry
Button = tk.Button
Radiobutton = tk.Radiobutton
IntVar = tk.IntVar
PhotoImage = tk.PhotoImage

# Import of needed paths
# Get path of this (GUI.py) file. See: https://stackoverflow.com/a/44592299
filename = inspect.getframeinfo(inspect.currentframe()).filename
rootPath = os.path.dirname(os.path.abspath(filename))

# Include path in system path, so that python would find the Modules
sys.path.append(rootPath)
# Include paths
# sys.path.append(rootPath + "/BifacialSimu/Controller")
# sys.path.append(rootPath + "/BifacialSimu/Handler")

# Include modules
from BifacialSimu import Controller



# Entry of simulation variables and settings for different simulation modes

"""
        Sets the mode for simulation: str
        mode 1 : front simulation with PVfactors, back simulation with Raytracing
        mode 2 : front and back simulation with Viewfactors
        mode 3 : front and back simulation with Raytracing
        mode 4 : only front simulation with Viewfactors
        mode 5 : only back simulation with Raytracing
"""

# simulation parameters and variables
SimulationDict = {
'clearance_height': 0.4, #value was found missing! should be added later!
'simulationName' : 'NREL_best_field_row_2',
'simulationMode' : 1, 
'localFile' : True, # Decide wether you want to use a  weather file or try to download one for the coordinates
'weatherFile' : rootPath +'/WeatherData/Golden_USA/SRRLWeatherdata Nov_Dez_2.csv', #weather file in TMY format 
'spectralReflectancefile' : rootPath + '/ReflectivityData/interpolated_reflectivity.csv',
'cumulativeSky' : False, # Mode for RayTracing: CumulativeSky or hourly
'startHour' : (2019, 11, 1, 0),  # Only for hourly simulation, yy, mm, dd, hh
'endHour' : (2019, 11, 16, 0),  # Only for hourly simulation, yy, mm, dd, hh
'utcOffset': -7,
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
'fixAlbedo': False, # Option to use the fix albedo
'hourlyMeasuredAlbedo' : True, # True if measured albedo values in weather file
'hourlySpectralAlbedo' : True, # Option to calculate a spectral Albedo 
'variableAlbedo': False, # Option to calculate sun position dependend, variable albedo
'albedo' : 0.26, # Measured Albedo average value, if hourly isn't available
'frontReflect' : 0.03, #front surface reflectivity of PV rows
'BackReflect' : 0.05, #back surface reflectivity of PV rows
'longitude' : -105.172, 
'latitude' : 39.739,
'gcr' : 0.35, #ground coverage ratio (module area / land use)
'module_type' : 'NREL row 2', #Name of Module
'fixSoilrate': 0.01, # Soiling rate default value
'variableSoilrate' : [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1],
'days_until_clean' : 15, #Default value for cleaning period of PV moduls
'average_daily_soiling_rate' : False,
'fixed_average_soiling_rate' : False,
'hourlySoilrate' : [], 
'city': "Duala, CM",
#'daily_Soiling_mass' : 0.1, # daily soiling accumulation on the PV-Panels. [g/m³]
}

# is in Function StartSimulation()

ModuleDict = {
    'bi_factor': 0.694, #bifacial factor
    'n_front': 0.19, #module efficiency
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
    'T_NOCT':45, #NOCT Temperature for estimation of module Temperature [°C]
    'T_koeff_I': 0.0005, #Temperaturkoeffizient for I_sc [1/°C] #SG
    'T_koeff_V': 0.0005, #Temperaturkoeffizient for U_oc [1/°C] #SG
    'zeta': 0.06, #Bestrahlungskoeffizient für Leerlaufspannung [-]
    'Ns': 90,  #Number of cells in module; to avoid error by the simulation
    
    
}




class Window(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.geometry("1300x750")
        self.title('BifacialSimu')
        if sys.platform == "linux":
            self.iconbitmap("@" + rootPath + "/Lib/logos/App_icon.xbm")
        else:
            self.iconbitmap(rootPath + "/Lib/logos/App_icon.ico")
        yscroll = tk.Scrollbar(self, orient=tk.VERTICAL)
        xscroll = tk.Scrollbar(self, orient=tk.HORIZONTAL)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        self.canvas = tk.Canvas(self)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas['yscrollcommand'] = yscroll.set
        self.canvas['xscrollcommand'] = xscroll.set
        yscroll['command'] = self.canvas.yview
        xscroll['command'] = self.canvas.xview
        frame=tk.Frame(self.canvas)
class Electrical_simulation:
    """
    Class that simulates the eletrical output from the irradiance simulation
    Currently, electrical simulation works with only Viewfactors and Viewfactors/Raytracing combination 
    
    Methods
    -------
    build_simulationReport: build a final simulation report that contains data from viewfactors and raytracing
    simulate_oneDiode: Applies the one diode model for electrical simulation. Needs module front and rear parameters to work correctly.
    simulate_simpleBifacial: Simple electrical simulation mode that doesn't need rear module parameters. 
                Applies bifaciality factor to calculate rear efficiency and fill factor.
    """
    
    ##### Function to combine radiation reports from Viewfactors and Raytracing if needed
    def build_simulationReport(df_reportVF, df_reportRT, simulationDict, resultsPath):
                      
        if simulationDict['simulationMode'] == 1:
            df_report = pd.concat([df_reportVF, df_reportRT], axis=1)
        if simulationDict['simulationMode'] == 2:
            df_report = df_reportVF
        if simulationDict['simulationMode'] == 3:
            df_report = df_reportRT
        #df_report = df_report.reindex(sorted(df_report.columns), axis=1)
        df_report.to_csv(Path(resultsPath + "radiation_qabs_results.csv"))
        
        frame = tk.Frame(self.canvas)
        self.canvas.create_window(4, 4, window=frame, anchor='nw') # Canvas equivalent of pack()
        frame.bind("<Configure>", self._on_frame_configure)
        
        # Creating Tabs for the Frames
        my_notebook=ttk.Notebook(frame)
        my_notebook.grid(row=1, column=1)
            
            
        #Creating the Frames
        #namecontrol_frame=tk.Frame(frame, width=200, height=60)
        namecontrol_frame=tk.Frame(my_notebook, width=200, height=60) 
        #simulationMode_frame=tk.Frame(frame, width=200, height=60)
        simulationMode_frame=tk.Frame(my_notebook, width=200, height=60,)
        simulationParameter_frame=tk.Frame(frame, padx=50, height=60)
        #ModuleParameter_frame=tk.Frame(frame, width=200, height=60)
        ModuleParameter_frame=tk.Frame(my_notebook, width=200, height=60)
        simulationFunction_frame=tk.Frame(frame, width=200, height=60)
        
        def github_infopage(option_1):
            
            if option_1 == "yes":
                webbrowser.open("https://github.com/cire-thk/BifacialSimu#readme",new=1)
            
            
# =============================================================================
#         Defining the message box commmand functions:
# =============================================================================
        # Main Control tab:
        def button_MC():
            
            pop = Toplevel()
            pop.title("Main Control Info!")
            pop.geometry("1000x400")
            pop.iconbitmap(rootPath+"\Lib\Button_Images\info_logo.ico")
            
            f= open(rootPath+"\Lib\Info_Messages\Main_Control.txt")
            text_MP = f.read()
            f.close()
            # since ° is a unicode character it should be replaced by its character unicode to be read properly from .txt files
            text_MP=text_MP.replace("Â°", "\u00b0")
             
            Info_label = Label(pop, text=text_MP,bg="white", font=("Arial",8),justify="left")
            Info_label.pack(pady=5)
            
            info_frame= Frame(pop, bg="white")
            info_frame.pack(pady=5)
            
            more_info_button = Button(info_frame,text='More Information', command= lambda:github_infopage("yes"))
            more_info_button.grid(row=0,column=0)
                                  
            
            
                                  
        # Simulation Control tab
        def button_SC():
                           
            pop = Toplevel()
            pop.title("Simulation Control Info!")
            pop.geometry("1400x700")
            pop.iconbitmap(rootPath+"\Lib\Button_Images\info_logo.ico")
            
            f= open(rootPath+"\Lib\Info_Messages\Simulation_Control.txt")
            text_MP = f.read()
            f.close()
            # since ° is a unicode character it should be replaced by its character unicode to be read properly from .txt files
            text_MP=text_MP.replace("Â°", "\u00b0")
             
            Info_label = Label(pop, text=text_MP,bg="white", font=("Arial",8),justify="left")
            Info_label.pack(pady=5)
            
            info_frame= Frame(pop, bg="white")
            info_frame.pack(pady=5)
            
            more_info_button = Button(info_frame,text='More Information', command= lambda:github_infopage("yes"))
            more_info_button.grid(row=0,column=0) 
            
        # Module Parameter tab
        def button_MP():
            
             pop= Toplevel()
             pop.title("Module Parameter Info!")
             pop.geometry("1300x760")
             pop.iconbitmap(rootPath+"\Lib\Button_Images\info_logo.ico")
             f= open(rootPath+"\Lib\Info_Messages\Module_Parameter.txt")
             text_MP = f.read()
             f.close()
             # since ° is a unicode character it should be replaced by its character unicode to be read properly from .txt files
             text_MP=text_MP.replace("Â°", "\u00b0")
              
             Info_label = Label(pop, text=text_MP,bg="white", font=("Arial",8),justify="left")
             Info_label.pack(pady=5)
             
             info_frame= Frame(pop, bg="white")
             info_frame.pack(pady=5)
             
             more_info_button = Button(info_frame,text='More Information', command= lambda:github_infopage("yes"))
             more_info_button.grid(row=0,column=0)
             
        # Simulation Parameter tab
        def button_SP():
            # f= open(rootPath+"\Lib\Info_Messages\Simulation_Parameters.txt")
            # text_SP= f.read()
            # f.close()
            # response = messagebox.askokcancel("Functions Info!", text_SP) 
            # if response == 1:
            #     webbrowser.open("https://github.com/cire-thk/BifacialSimu#readme",new=1)
            # global pop_SP
            pop_SP = Toplevel()
            pop_SP.title("Simulatoin Parameter Info!")
            pop_SP.geometry("1400x700")
            pop_SP.iconbitmap(rootPath+"\Lib\Button_Images\info_logo.ico")
            f= open(rootPath+"\Lib\Info_Messages\Simulation_Parameters.txt")
            text_SP= f.read()
            f.close()
            # since ° is a unicode character it should be replaced by its character unicode to be read properly from .txt files
            text_SP=text_SP.replace("Â°", "\u00b0")
             
            SP_Info = Label(pop_SP, text=text_SP,bg="white", font=("Arial",8),justify="left")
            SP_Info.pack(pady=5)
            
            info_frame= Frame(pop_SP, bg="white")
            info_frame.pack(pady=5)
            

            more_info_button = Button(info_frame,text='More Information', command= lambda:github_infopage("yes"))
            more_info_button.grid(row=0,column=0)
# =============================================================================
#         assigning the info Button Icon to a variable
# =============================================================================

        namecontrol_frame.infoButton_MC= PhotoImage(file= rootPath+'/Lib/Button_Images/Button-Info-icon.png')
        Info_image= namecontrol_frame.infoButton_MC
        
# =============================================================================
#         #inserting info buttons in frames: 
# =============================================================================


        # Main Control tab
        Info_MC = Button(namecontrol_frame, image=Info_image,command = button_MC, borderwidth=0)

        Info_MC.grid(row=0,column=1)
        # Simulation Control tab
        Info_SC = Button(simulationMode_frame, image=Info_image,command = button_SC, borderwidth=0)
        Info_SC.grid(row=0,column=1)
        # Module Parameter tab
        Info_MP = Button(ModuleParameter_frame, image=Info_image,command = button_MP, borderwidth=0)
        Info_MP.grid(row=0,column=2)
        # Simulation Parameter tab
        Info_SP = Button(simulationParameter_frame, image=Info_image,command = button_SP, borderwidth=0)
        Info_SP.grid(row=0,column=1)
        
        
        namecontrol_frame.bind("<Configure>", self._on_frame_configure)
        simulationMode_frame.bind("<Configure>", self._on_frame_configure)
        simulationParameter_frame.bind("<Configure>", self._on_frame_configure)
        ModuleParameter_frame.bind("<Configure>", self._on_frame_configure)
        simulationFunction_frame.bind("<Configure>", self._on_frame_configure)
        
        #positioning of the Frames
        namecontrol_frame.grid(row=0, column=0, sticky="NW")
        simulationMode_frame.grid(row=1, column=0, sticky="NW")
        simulationParameter_frame.grid(row=1, column=0, sticky="NW")
        ModuleParameter_frame.grid(row=0, column=0, rowspan=2, sticky="NW")
        simulationFunction_frame.grid(row=2, column=1, rowspan=2, sticky="NW")
        
        #Headlines for the Frames
        namecontrol_label = ttk.Label(namecontrol_frame, text='Main Control', font=("Arial Bold", 15))
        simulationMode_label = ttk.Label(simulationMode_frame, text='Simulation Control', font=("Arial Bold", 15))
        simulationParameter_label = ttk.Label(simulationParameter_frame, text='Simulation Parameter', font=("Arial Bold", 15))
        ModuleParameter_Label = ttk.Label(ModuleParameter_frame, text='Module Parameter', font=("Arial Bold", 15))
        Results_Label=ttk.Label(simulationMode_frame, text='Displaying Results:', font=("Arial Bold",10))
        #simulationFunction_Label = ttk.Label(simulationFunction_frame, background='lavender', text='Simulation Start', font=("Arial Bold", 15))
        
        namecontrol_label.grid(row = 0, column=0,padx=20, sticky="w")
        simulationMode_label.grid(row = 0, column=0,padx=20, sticky="w")
        simulationParameter_label.grid(row =0, column=0,padx=0, sticky=W)
        ModuleParameter_Label.grid(row =0, column=0,padx=20, sticky="w")
        Results_Label.grid(column=0,row=13, sticky="W")
        #simulationFunction_Label.grid(row =0, column=0, sticky="ew")
        
        #Adding empty cells to indent before Plot Buttons
        empty_cell_label_1=ttk.Label(simulationMode_frame,text=" ")
        empty_cell_label_1.grid(column=0, row=10, sticky="W")
        empty_cell_label_2=ttk.Label(simulationMode_frame,text=" ")
        empty_cell_label_2.grid(column=0, row=11, sticky="W")
        empty_cell_label_3=ttk.Label(simulationMode_frame,text=" ")
        empty_cell_label_3.grid(column=0, row=12, sticky="W")
        
        #Adding Frame to Notebook
        my_notebook.add(namecontrol_frame, text="Main Control")
        my_notebook.add(simulationMode_frame, text="Simulation Control")
        my_notebook.add(ModuleParameter_frame, text="Module Parameter")
        
        # Inserting Button for Plotting Mismatch Button
        checkbutton_state=IntVar()
        Mismatch_checkbutton = tk.Checkbutton(simulationMode_frame, text="Plot Mismatch Power Losses", variable= checkbutton_state)
        Mismatch_checkbutton.grid(column=0, row=14, sticky="W")
        
        # Inserting  Button for Plotting Absolute Irradiance 
        plot_AbIr_button=IntVar()
        Absolute_Irradiance_checkbutton = tk.Checkbutton(simulationMode_frame, text="Plot Absolute Irradiance", variable= plot_AbIr_button)
        Absolute_Irradiance_checkbutton.grid(column=1, row=14, sticky="W")
        
        # Inserting  Button for Plotting Irradiance 
        plot_Irr_button=IntVar()
        Irradiance_checkbutton = tk.Checkbutton(simulationMode_frame, text="Plot Irradiance", variable= plot_Irr_button)
        Irradiance_checkbutton.grid(column=0, row=15, sticky="W")
        
        # Inserting  Button for Plotting Bifacial Radiance
        plot_BiRadiance_button=IntVar()
        BifacialRadiance_checkbutton = tk.Checkbutton(simulationMode_frame, text="Plot Bifacial Output Power", variable= plot_BiRadiance_button)
        BifacialRadiance_checkbutton.grid(column=1, row=15, sticky="W")

        
        # Starting the simulation
        def StartSimulation():
           
# =============================================================================
#             Time Parameter
# =============================================================================
            
            if (len(Entry_year_start.get())==0 or len(Entry_month_start.get()) == 0 
                or len(Entry_day_start.get()) == 0 
                or len(Entry_hour_start.get()) == 0 
                or len(Entry_year_end.get()) == 0 
                or len(Entry_month_end.get()) == 0 
                or len(Entry_day_end.get()) == 0 
                or len(Entry_hour_end.get()) == 0) :
                messagebox.showwarning("Simulation Control", "Please insert a Start and End Date \n in the format: [yyyy mm dd hh]!")
                exit
            if int (Entry_month_start.get()) <=0 or int (Entry_month_start.get()) >12:
                messagebox.showwarning("Simulation Control", "Please insert a Start Month between 1 and 12!")
                exit
            if int(Entry_day_start.get()) <1 or int(Entry_day_start.get()) >31:
                messagebox.showwarning("Simulation Control", "Please insert a Start Day between 1 and 31!")
                exit
            if int(Entry_hour_start.get()) <0 or int(Entry_hour_start.get()) >=24:
                messagebox.showwarning("Simulation Control", "Please insert a Start Hour between 0 and 23!")
                exit
            if int (Entry_month_end.get()) <=0 or int (Entry_month_end.get()) >12:
                messagebox.showwarning("Simulation Control", "Please insert a End Month between 1 and 12!")
                exit
                
            if int(Entry_day_end.get()) <1 or int(Entry_day_end.get()) >31:
                messagebox.showwarning("Simulation Control", "Please insert a End Day between 1 and 31!")
                exit
                    
            if int(Entry_hour_end.get()) <0 or int(Entry_hour_end.get()) >=24:
                messagebox.showwarning("Simulation Control", "Please insert a End Hour between 0 and 23!")
                exit
                    
            if (len(Entry_year_start.get()) != 0
                and len(Entry_month_start.get()) != 0 and 1 <= int (Entry_month_start.get()) <= 12
                and len(Entry_day_start.get()) != 0 and 1<= int(Entry_day_start.get()) <=31
                and len(Entry_hour_start.get()) != 0 and 0<= int(Entry_hour_start.get()) <=23
                and len(Entry_year_end.get()) != 0 
                and len(Entry_month_end.get()) != 0 and 1 <= int (Entry_month_end.get()) <= 12
                and len(Entry_day_end.get()) != 0 and 1<= int(Entry_day_end.get()) <=31
                and len(Entry_hour_end.get()) != 0) and 0<= int(Entry_hour_end.get()) <=23:
                
                #start_date = datetime.strptime(Startdate, '%Y %m %d %H')
                #start_date = datetime.strptime(SimulationDict["startHour"], '%Y %m %d %H')
                Startdate = datetime.datetime(int(Entry_year_start.get()), int(Entry_month_start.get()), int(Entry_day_start.get()), int(Entry_hour_start.get())) #defining as Date
                SimulationDict["startHour"] = (Startdate.year, Startdate.month, Startdate.day, Startdate.hour)
                Enddate = datetime.datetime(int(Entry_year_end.get()), int(Entry_month_end.get()), int(Entry_day_end.get()), int(Entry_hour_end.get()))
                SimulationDict["endHour"] = (Enddate.year, Enddate.month, Enddate.day, Enddate.hour)
            
            else:
                messagebox.showwarning("Simulation Control", "Please insert a Start and End Date \n in the format: [yyyy mm dd hh]!")
                exit
                
               
            if len(Entry_utcoffset.get())!=0:
                SimulationDict["utcOffset"]=float(Entry_utcoffset.get())
           

# =============================================================================
#             Simulation Parameter
# =============================================================================

            if len(Entry_Name.get())!=0:
                SimulationDict["simulationName"]=Entry_Name.get()
            
            if len(Entry_Tilt.get()) !=0:
                SimulationDict["tilt"]=float(Entry_Tilt.get())
                
            if len(Entry_LimitAngle.get()) !=0:
                SimulationDict["limitAngle"]=float(Entry_LimitAngle.get())
        
            if len(Entry_ClearanceHeight.get()) !=0:
                SimulationDict["clearance_height"]=float(Entry_ClearanceHeight.get())
                # Calculate the hub height of the PV rows, measured at the bottom edge
                SimulationDict['hub_height']  = (SimulationDict['clearance_height'] + (math.sin(SimulationDict['tilt'])*SimulationDict['moduley']/2))
                
            if len(Entry_Azimuth.get()) !=0:
                SimulationDict["azimuth"]=float(Entry_Azimuth.get()) 

            if len(Entry_nRows.get()) !=0:
                SimulationDict["nRows"]=int(Entry_nRows.get())   
                
            if len(Entry_nModsx.get()) !=0:
                SimulationDict["nModsx"]=int(Entry_nModsx.get()) 
                
            if len(Entry_nModsy.get()) !=0:
                SimulationDict["nModsy"]=int(Entry_nModsy.get())     
                
            if len(Entry_sensors.get()) !=0:
                SimulationDict["sensorsy"]=int(Entry_sensors.get())   
                
            if len(Entry_moduley.get()) !=0:
                SimulationDict["moduley"]=float(Entry_moduley.get())   
            
            if len(Entry_modulex.get()) !=0:
                SimulationDict["modulex"]=float(Entry_modulex.get())
        
            if len(Entry_frontReflect.get()) !=0:
                SimulationDict["frontReflect"]=float(Entry_frontReflect.get())
                
            if len(Entry_backReflect.get()) !=0:
                SimulationDict["BackReflect"]=float(Entry_backReflect.get())
                
            if len(Entry_longitude.get()) !=0:
                SimulationDict["longitude"]=float(Entry_longitude.get())
            
            if len(Entry_latitude.get()) !=0:
                SimulationDict["latitude"]=float(Entry_latitude.get()) 
                
            if len(Entry_gcr.get()) !=0:
                SimulationDict["gcr"]=float(Entry_gcr.get())
                
            if len(Entry_albedo.get()) !=0:
                SimulationDict["albedo"]=float(Entry_albedo.get())
                
            if len(Entry_HubHeight.get()) !=0:
                SimulationDict["hub_height"]=float(Entry_HubHeight.get()) 
                # Calculate the clearance height of the PV rows, measured at the bottom edge
                SimulationDict['clearance_height']  = (SimulationDict['hub_height'] - (math.sin(SimulationDict['tilt'])*SimulationDict['moduley']/2))
                
            if len(Entry_Soilrate.get()) != 0:
                SimulationDict["fixSoilrate"] = float(Entry_Soilrate.get())
            
            if len(Entry_clean.get()) != 0:
                SimulationDict["days_until_clean"] = float(Entry_clean.get())


# =============================================================================
#           Module Parameter
# =============================================================================

            if len(Entry_bi_factor.get()) !=0:
                ModuleDict["bi_factor"]=float(Entry_bi_factor.get())
                
            if len(Entry_nfront.get()) !=0:
                ModuleDict["n_front"]=float(Entry_nfront.get())

            if len(Entry_Iscf.get()) !=0:
                ModuleDict["I_sc_f"]=float(Entry_Iscf.get())
                
            if len(Entry_Iscr.get()) !=0:
                ModuleDict["I_sc_r"]=float(Entry_Iscr.get())
                
            if len(Entry_Vocf.get()) !=0:
                ModuleDict["V_oc_f"]=float(Entry_Vocf.get())
                
            if len(Entry_Vocr.get()) !=0:
                ModuleDict["V_oc_r"]=float(Entry_Vocr.get())
                
            if len(Entry_Vmppf.get()) !=0:
                ModuleDict["V_mpp_f"]=float(Entry_Vmppf.get())
                
            if len(Entry_Vmppr.get()) !=0:
                ModuleDict["V_mpp_r"]=float(Entry_Vmppr.get())
                
            if len(Entry_Imppf.get()) !=0:
                ModuleDict["I_mpp_f"]=float(Entry_Imppf.get())   
                
            if len(Entry_Imppr.get()) !=0:
                ModuleDict["I_mpp_r"]=float(Entry_Imppr.get())  
                
            if len(Entry_Pmpp.get()) !=0:
                ModuleDict["P_mpp"]=float(Entry_Pmpp.get())  
                
            if len(Entry_TkoeffP.get()) !=0:
                ModuleDict["T_koeff_P"]=float(Entry_TkoeffP.get())
                
            if len(Entry_Tamb.get()) !=0:
                ModuleDict["T_amb"]=float(Entry_Tamb.get())    
                
            if len(Entry_TkoeffI.get()) !=0:
                ModuleDict["T_koeff_I"]=float(Entry_TkoeffI.get())
                
            if len(Entry_TkoeffV.get()) !=0:
                ModuleDict["T_koeff_V"]=float(Entry_TkoeffV.get())   
                
            if len(Entry_zeta.get()) !=0:
                ModuleDict["zeta"]=float(Entry_zeta.get())
                
            if len(Entry_Ns.get()) !=0:
                ModuleDict["Ns"]=float(Entry_Ns.get())           
                
            
# =============================================================================
#             Defining the Path for the Results    
# =============================================================================
            
            
            resultsPath = Controller.DataHandler().setDirectories() #WHY IMPORT FROM CONTROLLER AND NOT HANDLER??
            print('created resultsPath at: ' + resultsPath)     
            
            
# =============================================================================
#             Starting the Simulation with the defined Dictionaries
# =============================================================================
            
            Controller.startSimulation(SimulationDict, ModuleDict, resultsPath)


# =============================================================================
#           Functions to make the Plots
# =============================================================================
          
            makePlotAbsIrr(resultsPath,plot_AbIr_button)
            makePlotirradiance(resultsPath,plot_Irr_button)
            makePlotBifacialRadiance(resultsPath,plot_BiRadiance_button) 
            makePlotMismatch(resultsPath,checkbutton_state)

          
# =============================================================================
#           defining the Plots
# =============================================================================
    

        def makePlotAbsIrr(resultsPath, plot_AbIr_button):
            if plot_AbIr_button.get()== 1:
                if SimulationDict["simulationMode"]==1 or SimulationDict["simulationMode"]==2:
                    plt.style.use("seaborn")
                    
                    data=pd.read_csv(resultsPath+"/radiation_qabs_results.csv")
                    date=pd.read_csv(resultsPath + "/Data.csv")
                    timestamp_start=date.timestamp [0]
                   # print (timestamp_start)
                    timestamp_end=len(date.timestamp)       #Counting the amount of timestamps
                   # timestamp_end=
                    idx=pd.date_range(timestamp_start, periods=timestamp_end, freq="1H")    #without periods last timestamp isnt used
                    

                    i=0
                    
                    fig1 = plt.Figure()
                    ax1= fig1.subplots()        
                    x=[]
                    y=[]
                    x2=[]
                    y2=[]
                    while i < int(Entry_nRows.get()):
                        
                        #ids=data['row_'+str(i)+"_qabs_front"]
                        y.append("row_"+str(i)+"_front")
                        x.append(data['row_'+str(i)+"_qabs_front"])
        
                       # y.append(temp_y)
                        ax1.plot(idx, x[i], label=y[i])
        
                        i+=1
                   
                    j=0
                    while j < int(Entry_nRows.get()):

                        
                        x2.append(data['row_'+str(j)+'_qabs_back'])
                        y2.append("row_"+str(j)+"_back")
                       # y.append(temp_y)
                        ax1.plot(idx, x2[j],label=y2[j],linestyle="--")
        
                        j+=1            

                    
                    #ax1.xaxis.set_minor_locator(dates.HourLocator(interval=1))   # every hour
                    #ax1.xaxis.set_minor_formatter(dates.DateFormatter('%H:%M'))  #showing Hour and Minute on X-Axis  
                    ax1.xaxis.set_minor_locator(dates.DayLocator(interval=1))   # every day
                    ax1.xaxis.set_minor_formatter(dates.DateFormatter('%d'))  # day
                    ax1.xaxis.set_major_locator(dates.MonthLocator(interval=1))    # every Month
                    ax1.xaxis.set_major_formatter(dates.DateFormatter('\n%m-%Y'))  #show Month and Year
                    #ax1.legend()
                    ax1.legend(bbox_to_anchor=(0.7,1.02,1,.102),loc=3,ncol=2,borderaxespad=0)   #Place the Legend outside of the graph
                    ax1.set_ylabel('Radiance\n[W/m²]', size=17)
                    ax1.set_xlabel("Time", size=17)
                    ax1.set_title('Absolute Irradiance', size=18)
                    
                    #fig1.grid(True, which="minor")
                    fig1.tight_layout()
                    fig1.savefig("Absolute_Irradiance_front_back_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png")
                    canvas = FigureCanvasTkAgg(fig1, master=tk.Toplevel())
                    canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1.0)
                    canvas.draw()
                    
                    
                if SimulationDict["simulationMode"]==3 or SimulationDict["simulationMode"]==5:
                    plt.style.use("seaborn")
                    
                    data=pd.read_csv(resultsPath+"/radiation_qabs_results.csv")
                    date1=pd.read_csv(resultsPath + "/Dataframe_df.csv")
                    date2=pd.read_csv(resultsPath + "/df_reportRT.csv")
                    timestamp_start=date1.corrected_timestamp [0]
                   # print (timestamp_start)
                    timestamp_end=len(date2.row_2_qinc_front)       #Counting the amount of timestamps
                   # timestamp_end=
                    idx=pd.date_range(timestamp_start, periods=timestamp_end, freq="1H")    #without periods last timestamp isnt used
                    

                    i=0
                    fig1 = plt.Figure()
                    ax1= fig1.subplots()        
                    x=[]
                    y=[]
                    x2=[]
                    y2=[]
                    while i < int(Entry_nRows.get()):
                        
                        #ids=data['row_'+str(i)+"_qabs_front"]
                        y.append("row_"+str(i)+"_front")
                        x.append(data['row_'+str(i)+"_qabs_front"])
        
                       # y.append(temp_y)
                        ax1.plot(idx, x[i], label=y[i])
        
                        i+=1
                   
                    j=0
                    while j < int(Entry_nRows.get()):
                        
                        x2.append(data['row_'+str(j)+'_qabs_back'])
                        y2.append("row_"+str(j)+"_back")
                       # y.append(temp_y)
                        ax1.plot(idx, x2[j],label=y2[j],linestyle="--")
        
                        j+=1            

                    
                    #ax1.xaxis.set_minor_locator(dates.HourLocator(interval=1))   # every hour
                    #ax1.xaxis.set_minor_formatter(dates.DateFormatter('%H:%M'))  #showing Hour and Minute on X-Axis  
                    ax1.xaxis.set_minor_locator(dates.DayLocator(interval=1))   # every day
                    ax1.xaxis.set_minor_formatter(dates.DateFormatter('%d'))  # day
                    ax1.xaxis.set_major_locator(dates.MonthLocator(interval=1))    # every Month
                    ax1.xaxis.set_major_formatter(dates.DateFormatter('\n%m-%Y'))  #show Month and Year
                    ax1.legend()
                    ax1.set_ylabel('Radiance\n[W/m²]', size=17)
                    ax1.set_xlabel("Time", size=17)
                    ax1.set_title('Absolute Irradiance', size=18)
                    
                    #fig1.grid(True, which="minor")
                    fig1.tight_layout()
                    fig1.savefig("Absolute_Irradiance_front_back_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png")
                    ##plt.show()
                
# ========================For these simulation a Timestamp has to be implemented in the csv. It needs a key for the variable=====================================================
#             if SimulationDict["simulationMode"]==5:
#                 plt.style.use("seaborn")
#                 
#                 data=pd.read_csv(resultsPath+"/df_reportRT.csv")
#                # date=pd.read_csv(resultsPath + "/Data.csv")
#                # timestamp_start=date.timestamp [0]
#                # print (timestamp_start)
#                 timestamp_end=len(date.timestamp)       #Durch len wird gezählt wieviele Zeitdaten Vorliegen somit kann mit Periods bis zum letzten Zeitpunkt kalkuliert werden
#                # timestamp_end=
#                 idx=pd.date_range(timestamp_start, periods=timestamp_end, freq="1H")    #Es wird periods benutzt da beim Enddatum der Enddatum Zeitpunkt nicht betrachtet wird
#                 
#                 x2=[]
#                 y2=[]
#                 j=0
#                 while j < int(Entry_nRows.get()):
#                     
#                     x2.append(data['row_'+str(j)+'_qabs_back'])
#                     y2.append("row_"+str(j)+"_absolute_irradiance_back")
#                    # y.append(temp_y)
#                     ax1.plot(idx, x2[j],label=y2[j],linestyle="--")
#     
#                     j+=1            
# 
#     
#                 ax1.xaxis.set_minor_locator(dates.HourLocator(interval=1))   # every hour
#                 ax1.xaxis.set_minor_formatter(dates.DateFormatter('%H:%M'))  # hours and minutes
#                 ax1.xaxis.set_major_locator(dates.DayLocator(interval=1))    # every day
#                 ax1.xaxis.set_major_formatter(dates.DateFormatter('\n%m-%Y'))  
#                 ax1.legend()
#                 ax1.set_ylabel('Radiance\n[W/m²]')
#                 ax1.set_xlabel("Time")
#                 ax1.set_title('Absolute_Irradiance')
#                 
#                 plt.grid(True, which="major")
#                 plt.tight_layout()
#                 fig1.savefig("Absolute_Irradiance_front_back" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png")
#                 ##plt.show()
#                 
# =============================================================================
# Simulation Mode 4 needs to get debugged       
# =============================================================================
 
        def makePlotMismatch(resultsPath,checkbutton_state):
            if checkbutton_state.get()== 1 :
                plt.style.use("seaborn")
                
                data=pd.read_csv(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
                date=pd.read_csv(resultsPath + "/Data.csv")
                
                
                timestamp_end= len(date.timestamp)
                timestamp_start= date.timestamp[0]
                idx=pd.date_range(timestamp_start, periods=timestamp_end, freq="1H")
                
                mismatch=data["Mismatch"]
                
                fig3 = plt.Figure()
                ax3= fig3.subplots()
                
                ax3.plot(idx,mismatch, label="Mismatch")
                
                ax3.xaxis.set_minor_locator(dates.DayLocator(interval=1))   # every Day
                ax3.xaxis.set_minor_formatter(dates.DateFormatter('%d'))  # day and hours
                ax3.xaxis.set_major_locator(dates.MonthLocator(interval=1))    # every Month
                ax3.xaxis.set_major_formatter(dates.DateFormatter('\n%m-%Y'))             
                ax3.legend()
                ax3.set_ylabel('Mismatch\n[%]', size=17)
                ax3.set_xlabel("Time", size=17)
                ax3.set_title('Mismatch Power Losses', size=18)
                
                # saving resluts to .png file
                fig3.tight_layout()
                fig3.savefig("Bifacial_output_Power_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png")
                
                # showing results in a window
                canvas = FigureCanvasTkAgg(fig3, master=tk.Toplevel())
                canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1.0)
                canvas.draw()
                
            else:
                return
            
        def makePlotirradiance(resultsPath,plot_Irr_button):
            if plot_Irr_button.get()== 1:
                
                if SimulationDict["simulationMode"]==1 or SimulationDict["simulationMode"]==2:
                    plt.style.use("seaborn")
                    
                    
                    data=pd.read_csv(resultsPath + "/Data.csv")
        
                    timestamp_start=data.timestamp [0]
                   # print (timestamp_start)
                    timestamp_end=len(data.timestamp)
                   # timestamp_end=
                    idx=pd.date_range(timestamp_start, periods=timestamp_end, freq="1H")
                    ghi=data["ghi"]
                    dhi=data["dhi"]
                    dni=data["dni"]
                   
                    fig2 = plt.Figure()
                    ax2= fig2.subplots()
                    
                    ax2.plot(idx,ghi, label="GHI")
                    ax2.plot(idx,dhi, label="DHI")
                    ax2.plot(idx,dni, label="DNI")
                     
                    ax2.xaxis.set_minor_locator(dates.DayLocator(interval=1))   # every hour
                    ax2.xaxis.set_minor_formatter(dates.DateFormatter('%d'))  # hours and minutes
                    ax2.xaxis.set_major_locator(dates.MonthLocator(interval=1))    # every day
                    ax2.xaxis.set_major_formatter(dates.DateFormatter('\n%m-%Y')) 
                    ax2.legend()
                    ax2.set_ylabel('Radiance\n[W/m²]', size=17)
                    ax2.set_xlabel("Time", size=17)
                    ax2.set_title('Irradiance', size=18)
                    
                    #fig2.grid(True, which="minor")
                    fig2.tight_layout()
                    fig2.savefig("Irradiance_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png")
                    ###plt.show()
            
# =============================================================================
        def makePlotBifacialRadiance(resultsPath,plot_BiRadiance_button):
            if plot_BiRadiance_button.get()==1:
                
                if SimulationDict["simulationMode"]==1 or SimulationDict["simulationMode"]==2: 
                  plt.style.use("seaborn")
                  
                  
                  data=pd.read_csv(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
                  date=pd.read_csv(resultsPath + "/Data.csv")
                  timestamp_start=date.timestamp [0]
                 # print (timestamp_start)
                  timestamp_end=len(date.timestamp)
                 # timestamp_end=
                  idx=pd.date_range(timestamp_start, periods=timestamp_end, freq="1H")
                  
                  P_bi=data["P_bi "]
                  
                 
                  fig3 = plt.Figure()
                  ax3= fig3.subplots()
                  
                  ax3.plot(idx,P_bi, label="P_bi ")
                  
                  ax3.xaxis.set_minor_locator(dates.DayLocator(interval=1))   # every Day
                  ax3.xaxis.set_minor_formatter(dates.DateFormatter('%d'))  # day and hours
                  ax3.xaxis.set_major_locator(dates.MonthLocator(interval=1))    # every Month
                  ax3.xaxis.set_major_formatter(dates.DateFormatter('\n%m-%Y'))             
                  ax3.legend()
                  ax3.set_ylabel('Power Output\n[W/m²]', size=17)
                  ax3.set_xlabel("Time", size=17)
                  ax3.set_title('Bifacial Output Power', size=18)
                  
                  #fig3.grid(True, which="minor")
                  fig3.tight_layout()
                  fig3.savefig("Bifacial_output_Power_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png")
                  #os.rename(resultsPath + "/electrical_simulation.csv", resultsPath + "electrical_simulation_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
                  
                  canvas = FigureCanvasTkAgg(fig3, master=tk.Toplevel())
                  canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1.0)
                  canvas.draw()
                      
                if SimulationDict["simulationMode"]==3  or SimulationDict["simulationMode"]==5:
                  plt.style.use("seaborn")
                  
                  
                  data=pd.read_csv(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
                  date1=pd.read_csv(resultsPath + "/Dataframe_df.csv")
                  date2=pd.read_csv(resultsPath + "/df_reportRT.csv")
                  timestamp_start=date1.corrected_timestamp [0]
                 # print (timestamp_start)
                  timestamp_end=len(date2.row_2_qinc_front)       #
           
                  idx=pd.date_range(timestamp_start, periods=timestamp_end, freq="1H")
                  
                  P_bi=data["P_bi "]
                  
                 
                  fig3 = plt.Figure()
                  ax3= fig3.subplots()
                  
                  ax3.plot(idx,P_bi, label="P_bi ")
                  
                  ax3.xaxis.set_minor_locator(dates.DayLocator(interval=1))   # every Day
                  ax3.xaxis.set_minor_formatter(dates.DateFormatter('%d'))  # day and hours
                  ax3.xaxis.set_major_locator(dates.MonthLocator(interval=1))    # every Month
                  ax3.xaxis.set_major_formatter(dates.DateFormatter('\n%m-%Y'))             
                  ax3.legend()
                  ax3.set_ylabel('Power Output\n[W/m²]', size=17)
                  ax3.set_xlabel("Time", size=17)
                  ax3.set_title('Bifacial Output Power', size=17)
                  
                  #fig3.grid(True, which="minor")
                  fig3.tight_layout()
                  fig3.savefig("Bifacial_output_Power_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png")
                  #os.rename(resultsPath + "/electrical_simulation.csv", resultsPath + "electrical_simulation_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv") 

#                 
# =============================================================================
# Entries for default settings
            
        def setdefault():
            Entry_Tilt.config(state="normal")
            Entry_ClearanceHeight.config(state="normal")
            clearall()
            Combo_Module.current(0)
            Combo_Albedo.current(0)
            Combo_Soilrate.current(0)
            rad1_Soiling.invoke()
            rad1_weatherfile.invoke()
            rad2_simulationMode.invoke()
            rad1_rb_SingleAxisTracking.invoke()
            rad1_Albedo.invoke()
            rad1_ElectricalMode.invoke()
            rad1_BacktrackingMode.invoke()
            Entry_Name.insert(0, simulationName_configfile)
            Entry_weatherfile.insert(0, weatherFile_configfile) #zu überarbeiten
            Entry_reflectivityfile.insert(0, reflectivityFile_configfile)
            Entry_Tilt.insert(0, tilt_configfile)
            Entry_LimitAngle.insert(0, limitAngle_configfile)
            Entry_ClearanceHeight.insert(0, ClearanceHeight_configfile)
            Entry_Azimuth.insert(0, azimuth_configfile)
            Entry_nModsx.insert(0, nModsx_configfile)
            Entry_nModsy.insert(0, nModsy_configfile)
            Entry_nRows.insert(0, nRows_configfile)
            Entry_sensors.insert(0, sensorsy_configfile)
            Entry_year_start.insert(0, Start_Year_configfile)
            Entry_month_start.insert(0, Start_Month_configfile)
            Entry_day_start.insert(0, Start_Day_configfile)
            Entry_hour_start.insert(0, Start_Hour_configfile)
            Entry_year_end.insert(0, End_Year_configfile)
            Entry_month_end.insert(0, End_Month_configfile)
            Entry_day_end.insert(0, End_Day_configfile)
            Entry_hour_end.insert(0, End_Hour_configfile)
         #   Entry_moduley.insert(0, moduley_configfile)
          #  Entry_modulex.insert(0, modulex_configfile)
            Entry_frontReflect.insert(0, frontReflect_configfile)
            Entry_backReflect.insert(0, backReflect_configfile)
            Entry_longitude.insert(0, longitude_configfile)
            Entry_latitude.insert(0, latitude_configfile)
            Entry_gcr.insert(0, gcr_configfile)
            Entry_utcoffset.insert(0, utcoffset_configfile)

            key = entry_modulename_value.get()
            d = self.jsondata[key]
            self.module_type = key
            SimulationDict["module_type"]=self.module_type
            Entry_bi_factor.insert(0,str(d['bi_factor']))
            Entry_nfront.insert(0,str(d['n_front']))
            Entry_Iscf.insert(0,str(d['I_sc_f']))
            Entry_Iscr.insert(0,str(d['I_sc_r']))
            Entry_Vocf.insert(0,str(d['V_oc_f']))
            Entry_Vocr.insert(0,str(d['V_oc_r']))
            Entry_Vmppf.insert(0,str(d['V_mpp_f']))
            Entry_Vmppr.insert(0,str(d['V_mpp_r']))
            Entry_Imppf.insert(0,str(d['I_mpp_f']))              
            Entry_Imppr.insert(0,str(d['I_mpp_r']))
            Entry_Pmpp.insert(0,str(d['P_mpp']))
            Entry_TkoeffP.insert(0,str(d['T_koeff_P']))
            Entry_Tamb.insert(0,str(d['T_amb']))
            Entry_TkoeffI.insert(0,str(d['T_koeff_I']))
            Entry_TkoeffV.insert(0,str(d['T_koeff_V']))
            Entry_zeta.insert(0,str(d['zeta']))
            Entry_modulex.insert(0,str(d['modulex']))
            Entry_moduley.insert(0,str(d['moduley'])) 
            Entry_Ns.insert(0,str(ModuleDict["Ns"]))
            
            
            key1=entry_albedo_value.get()
            a = self.jsondata_albedo[key1]
            self.albedo = key1
            Entry_albedo.delete(0,END)
            Entry_albedo.insert(0,str(a['Albedo']))
            
            key2 = entry_soilrate_value.get()             
            b = self.jsondata_soiling[key2]             
            self.soilrate = key2
            Entry_Soilrate.delete(0, END)
            Entry_Soilrate.insert(0, str(b['soilrate']))
            
            Entry_clean.insert(0, 15) # set default cleaning period [d]
        
# Entry for delete button
            
        def clearall():
            Entry_Name.delete(0, END)
            Entry_weatherfile.delete(0, END) 
            Entry_Tilt.delete(0, END)
            Entry_LimitAngle.delete(0, END)
            Entry_ClearanceHeight.delete(0, END)
            Entry_Azimuth.delete(0, END)
            Entry_nModsx.delete(0, END)
            Entry_nModsy.delete(0, END)
            Entry_nRows.delete(0, END)
            Entry_sensors.delete(0, END)
            Entry_year_start.delete(0, END)
            Entry_month_start.delete(0, END)
            Entry_day_start.delete(0, END)
            Entry_hour_start.delete(0, END)
            Entry_year_end.delete(0, END)
            Entry_month_end.delete(0, END)
            Entry_day_end.delete(0, END)
            Entry_hour_end.delete(0, END)
            Entry_moduley.delete(0, END)
            Entry_modulex.delete(0, END)
            Entry_frontReflect.delete(0, END)
            Entry_backReflect.delete(0, END)
            Entry_longitude.delete(0, END)
            Entry_latitude.delete(0, END)
            Entry_gcr.delete(0, END)
            Entry_bi_factor.delete(0,END)
            Entry_nfront.delete(0,END)
            Entry_Iscf.delete(0,END)
            Entry_Iscr.delete(0,END)
            Entry_Vocf.delete(0,END)
            Entry_Vocr.delete(0,END)
            Entry_Vmppf.delete(0,END)
            Entry_Vmppr.delete(0,END)
            Entry_Imppf.delete(0,END)
            Entry_Imppr.delete(0,END)
            Entry_Pmpp.delete(0,END)
            Entry_TkoeffP.delete(0,END)
            Entry_Tamb.delete(0,END)
            Entry_TkoeffI.delete(0,END)
            Entry_TkoeffV.delete(0,END)
            Entry_zeta.delete(0,END)
            Entry_albedo.delete(0,END)
            Entry_utcoffset.delete(0,END)
            Entry_Soilrate.delete(0, END) 
            Entry_clean.delete (0, END)

            
           # Combo_Module.delete(0,END)
       
         
        #Changing the Name of the Simulation
        Entry_Name=ttk.Entry(namecontrol_frame, width=20, background="white")
        Entry_Name.grid(row=1, column=1, sticky=W)
        Label_Name=ttk.Label(namecontrol_frame,text="Insert Simulation Name:", width=20)
        Label_Name.grid(row=1,column=0, sticky=W)

        # commands for the Weatherfile
        def Weatherfile():
           
            if (rb_weatherfile.get()==0):
                 SimulationDict["localFile"]=True
                 Lab_weatherfile.config(state="normal")
                 Entry_weatherfile.config(state="normal")
                 Button_weatherfile.config(state="normal")
                 Label_longitude.config(state="disabled")
                 Entry_longitude.config(state="disabled")
                 Label_latitude.config(state="disabled")
                 Entry_latitude.config(state="disabled")
                 
            else:
                SimulationDict["localFile"]=False
                Entry_weatherfile.config(state="disabled")
                Button_weatherfile.config(state="disabled")
                Lab_weatherfile.config(state="disabled")
                Label_longitude.config(state="normal")
                Entry_longitude.config(state="normal")
                Label_latitude.config(state="normal")
                Entry_latitude.config(state="normal")
                 
            
        #Deciding to download or use ur own weatherfile       
        rb_weatherfile=IntVar()
        rb_weatherfile.set("0")
        rad1_weatherfile= Radiobutton(namecontrol_frame, variable=rb_weatherfile, width=15, text="Local   File!", value=0, command=lambda:Weatherfile())
        rad2_weatherfile= Radiobutton(namecontrol_frame, variable=rb_weatherfile,  width=20, text="Download weather File!", value=1, command=lambda:Weatherfile())
        rad1_weatherfile.grid(column=0,row=3, sticky=W)
        rad2_weatherfile.grid(column=1,row=3, sticky=W)
        
        

        
        def InsertWeatherfile():    
            
            """ select local weatherfile
            """
          
            filename = tk.filedialog.askopenfilename(title="Select EPW or TMY .csv file", filetypes = (("TMY .csv files", "*.csv"),
                                                              ("EPW files", "*.epw"),
                                                             ("EPW and TMY files", "*.epw;*.csv")))

            Entry_weatherfile.delete(0, END)
            Entry_weatherfile.insert(0, filename)   
            SimulationDict["weatherFile"] = Entry_weatherfile.get()
        
        def InsertReflectivityfile():    
            
            """ select local reflectivityfile
            """
          
            filename = tk.filedialog.askopenfilename(title="Select .csv file", filetypes = (("TMY .csv files", "*.csv"),))

            Entry_reflectivityfile.delete(0, END)
            Entry_reflectivityfile.insert(0, filename)   
            SimulationDict["spectralReflectancefile"]=Entry_reflectivityfile.get()
            

        def Set_UTC_offset():
            """ This function takes the coordinates entered by the user in the GUI, and returns as a result the resulting UTC timezone offset of the given location.
                The coordinates should be entered according to the following format:
                Longitudes: +/- 00.000000, where '+' represents East and '-' represents West
                Latitudes:  +/- 00.000000, where '+' represents North and '-' represents South"""
                
            #User Longitude and Latitude entries    
            Longitude= float(Entry_longitude.get())
            Latitude= float(Entry_latitude.get())
            
            #this part gets time zone name only
            tz_GMT = tf().timezone_at(lng=0, lat=0)             #GMT is required to calculate the difference and obtain the UTC
            tz= tf().timezone_at(lng=Longitude, lat=Latitude)   #This is the coordinates entered by the user
            
            #create a timezone object here:
            timezone_GMT= pytz.timezone(tz_GMT)
            timezone= pytz.timezone(tz)

            #Getting actual time in each time zone 
            GMT_time= datetime.datetime.now(timezone_GMT)
            tested_time= datetime.datetime.now(timezone)

            #Subtracting both times to obtain the difference in hours, which is the UTC offset required
            UTC_offset= tested_time.hour- GMT_time.hour
         
            Entry_utcoffset.delete(0,END)
#<<<<<<< HEAD
            Entry_utcoffset.insert(0, int(offset_result))
            
# Function to set 'longitude' and 'latitude' in SimulationDict. Needed for getSoilingWeatherdata()             
        def Set_lat_lng():
            
            # Get 'longitude' and 'latitude' from entryboxes, when trying to download weatherfile            
            if len(Entry_longitude.get()) != 0 and len(Entry_longitude.get()) != 0 and rb_weatherfile.get() == 1: 
                SimulationDict["longitude"] = float(Entry_longitude.get())                                                                                      
                SimulationDict["latitude"] = float(Entry_latitude.get())  
            # When local file is used, try to get 'longitude' and 'latitude' from TMY files with help of pvlib.iotools                          
            elif len(Entry_weatherfile.get()) != 0 and rb_weatherfile.get() == 0:
                tmydata, tmymetadata = pvlib.iotools.read_tmy3(Entry_weatherfile.get())
                SimulationDict["longitude"] = tmymetadata['longitude']
                SimulationDict["latitude"] = tmymetadata['latitude']                 
                     
                    
#                try:
#                    SimulationDict["longitude"] = float(Entry_longitude.get())                                                                                      
#                    SimulationDict["latitude"] = float(Entry_latitude.get())      
#                except:                     
#                    messagebox.showwarning("Main Control", "Please enter coordinates according to following following exampe (lat, lon): 50.9, 7.0 ")                    
#                pass
            
            # When local file is used, try to get 'longitude' and 'latitude' from TMY files with help of pvlib.iotools                          
#            elif len(Entry_weatherfile.get()) != 0 and rb_weatherfile.get() == 0:                
#                try:
#                    tmydata, tmymetadata = pvlib.iotools.read_tmy3(Entry_weatherfile.get())
#                    SimulationDict["longitude"] = tmymetadata['longitude']
#                    SimulationDict["latitude"] = tmymetadata['latitude']                 
#                except:
#                    messagebox.showwarning(
#                         "Main Control", "PLease enter a weather file in TMY format")                     
            # If both options did not work, show warning messagebox             
#            else:
#                messagebox.showwarning(
#                    "Main Control", "Please insert a TMY weather file or enter coordinates of the simulation location")         
#            Soiling() #Update Soilingrates for new Weatherdata or Location 
            
            # Show message to user, when PV-Module tilt is over 85°             
#            if (float(Entry_Tilt.get()) > 84.0):                 
#                messagebox.showwarning(
#                    "Main Control", "Note that the soiling rate is significantly reduced if modules are nearly vertical!") 
                   
#=======
            #Entry_utcoffset.insert(0, int(UTC_offset))
                     
#>>>>>>> master
        #Changing the weatherfile
        Lab_weatherfile=ttk.Label(namecontrol_frame, text="Add Path of weatherfile:")
        Lab_weatherfile.grid(row=4, column=0, sticky=W)
        Entry_weatherfile=ttk.Entry(namecontrol_frame, background="white", width=25)
        Entry_weatherfile.grid(row=4, column=1)
        Button_weatherfile=ttk.Button(namecontrol_frame, text="Insert Weatherfile!", command=InsertWeatherfile)
        Button_weatherfile.grid(row=4, column=2,sticky = W)
        
        #Changing the reflectivityfile
        Lab_reflectivityfile=ttk.Label(namecontrol_frame, text="Add Path of reflectivityfile:")
        Lab_reflectivityfile.grid(row=5, column=0, sticky=W)
        Entry_reflectivityfile=ttk.Entry(namecontrol_frame, background="white", width=25)
        Entry_reflectivityfile.grid(row=5, column=1)
        Button_reflectivityfile=ttk.Button(namecontrol_frame, text="Insert Reflectivityfile!", command=InsertReflectivityfile)
        Button_reflectivityfile.grid(row=5, column=2)
        
        #Change Longitude and Latitude
        Label_longitude=ttk.Label(namecontrol_frame, text="Enter Longitude:")
        Label_latitude=ttk.Label(namecontrol_frame, text="Enter Latitude:")
        Label_longitude.grid(column=0, row=6, sticky=W)
        Label_latitude.grid(column=0, row=7, sticky=W)
        Entry_longitude=ttk.Entry(namecontrol_frame,background="white", width=10)
        Entry_latitude=ttk.Entry(namecontrol_frame, background="white", width=10)
        Entry_longitude.grid(column=1, row=6, sticky=W)
        Entry_latitude.grid(column=1, row=7, sticky=W)        
        
        #Setting UTC offset of Longitude and Latitude coordinates
        Calculate_UTC= ttk.Button(namecontrol_frame,text= "Set UTC offset", command=lambda: Set_UTC_offset())
        Calculate_UTC.grid(column=2, row=6,sticky=W)
        
        # Confirm Main Control inputs to update soiling rate with Set_lat_lng()         
        Confirm_main_control = ttk.Button(namecontrol_frame, text="Confirm Main Control inputs", command=lambda: Set_lat_lng())                              
        Confirm_main_control.grid(column=1, row=8, sticky=W)            
        

  
# =============================================================================
#     Parameter of the Simulation Parameter Frame
# =============================================================================
   
     #Create the different simulationModes 1 to 5
        
        def simMode():
            if r.get()==0:
                SimulationDict["simulationMode"]=1
            
            if r.get()==1:
                SimulationDict["simulationMode"]=2
            
            if r.get()==2:
                SimulationDict["simulationMode"]=3
            
            if r.get()==3:
                SimulationDict["simulationMode"]=4
            
            if r.get()==4:
                SimulationDict["simulationMode"]=5
                    
        
        #Changing the Simulation Mode 1 to 5
        
        self.r=IntVar()
        r=self.r
        r.set("0")
        rad1_simulationMode = Radiobutton(simulationMode_frame, variable=r, indicatoron = 0, width = 55, text='front simulation with Viewfactors, back simulation with Raytracing', value=0, command=lambda:simMode())
        rad2_simulationMode = Radiobutton(simulationMode_frame, variable=r, indicatoron = 0, width = 55,  text='front and back simulation with Viewfactors', value=1, command=lambda:simMode())
        rad3_simulationMode = Radiobutton(simulationMode_frame, variable=r, indicatoron = 0, width = 55,  text='front and back simulation with Raytracing', value=2, command=lambda:simMode()) #text='Fixed, Hourly by Timestamps'
        rad4_simulationMode = Radiobutton(simulationMode_frame, variable=r, indicatoron = 0, width = 55,  text='only front simulation with Viewfactors', value=3, command=lambda:simMode())
        rad5_simulationMode = Radiobutton(simulationMode_frame, variable=r, indicatoron = 0, width = 55,  text='only back simulation with Raytracing', value=4, command=lambda:simMode())
        rad1_simulationMode.grid(column=0, row=2, columnspan=5)
        rad2_simulationMode.grid(column=0, row=3, columnspan=5)
        rad3_simulationMode.grid(column=0, row=4, columnspan=5)
        rad4_simulationMode.grid(column=0, row=5, columnspan=5)
        rad5_simulationMode.grid(column=0, row=6, columnspan=5)
        rad1_simulationMode.invoke()
    
                
        
        
        #Inserting Time Data
        Label_startdate=ttk.Label(simulationMode_frame, text="Startdate (yy, mm, dd, hh):")
        Label_enddate=ttk.Label(simulationMode_frame, text="Enddate (yy, mm, dd, hh):")
        Label_utcoffset=ttk.Label(simulationMode_frame, text="UTC offset:")
        Label_startdate.grid(column=0,row=7, sticky="W")
        Label_enddate.grid(column=0,row=8, sticky="W")
        Label_utcoffset.grid(column=0,row=9, sticky="W")
        
               

        Entry_year_start=ttk.Entry(simulationMode_frame, background="white", width=16)
        Entry_month_start=ttk.Entry(simulationMode_frame, background="white", width=4)
        Entry_day_start=ttk.Entry(simulationMode_frame, background="white", width=4)
        Entry_hour_start=ttk.Entry(simulationMode_frame, background="white", width=4)
        Entry_year_start.grid(column=1,row=7)
        Entry_month_start.grid(column=2,row=7)
        Entry_day_start.grid(column=3,row=7)
        Entry_hour_start.grid(column=4,row=7)
        
        Entry_year_end=ttk.Entry(simulationMode_frame, background="white", width=16)
        Entry_month_end=ttk.Entry(simulationMode_frame, background="white", width=4)
        Entry_day_end=ttk.Entry(simulationMode_frame, background="white", width=4)
        Entry_hour_end=ttk.Entry(simulationMode_frame, background="white", width=4)
        Entry_year_end.grid(column=1,row=8)
        Entry_month_end.grid(column=2,row=8)
        Entry_day_end.grid(column=3,row=8)
        Entry_hour_end.grid(column=4,row=8)
        
        Entry_utcoffset=ttk.Entry(simulationMode_frame, background="white", width=16)
        Entry_utcoffset.grid(column=1,row=9)


        def Singleaxis():
            #disabling and enabling for singleaxis
            if (rb_SingleAxisTracking.get()==0):
                SimulationDict["singleAxisTracking"]=False
                Label_Tilt.config(state="normal")
                Label_TiltPar.config(state="normal")
                Entry_Tilt.config(state="normal")
                Label_LimitAngle.config(state="disabled")
                Entry_LimitAngle.config(state="disabled")
                Label_LimitAnglePar.config(state="disabled")
                Label_HubHeight.config(state="disabled")
                Entry_HubHeight.config(state="disabled")
                Label_HubHeightPar.config(state="disabled")
                Label_ClearanceHeight.config(state="normal")
                Entry_ClearanceHeight.config(state="normal")
                Label_ClearanceHeightPar.config(state="normal")
                 
                 
            else:
                SimulationDict["singleAxisTracking"]=True
                Label_Tilt.config(state="disabled")
                Label_TiltPar.config(state="disabled")
                Entry_Tilt.config(state="disabled")
                Label_LimitAngle.config(state="normal")
                Entry_LimitAngle.config(state="normal")
                Label_LimitAnglePar.config(state="normal")
                Label_HubHeight.config(state="disabled")
                Entry_HubHeight.config(state="disabled")
                Label_HubHeightPar.config(state="disabled")
                Label_ClearanceHeight.config(state="normal")
                Entry_ClearanceHeight.config(state="normal")
                Label_ClearanceHeightPar.config(state="normal")
                
                
                
        # Radiobuttons for single axis tracking
        rb_SingleAxisTracking=IntVar()
        rb_SingleAxisTracking.set("0")
        rad1_rb_SingleAxisTracking= Radiobutton(simulationParameter_frame, variable=rb_SingleAxisTracking, width=25, text="Without Single Axis Tracking!", value=0, command=lambda:Singleaxis())
        rad2_rb_SingleAxisTracking= Radiobutton(simulationParameter_frame, variable=rb_SingleAxisTracking,  width=20, text="With Single Axis Tracking!", value=1, command=lambda:Singleaxis())
        rad1_rb_SingleAxisTracking.grid(column=0,row=1, sticky=W)
        rad2_rb_SingleAxisTracking.grid(column=1,row=1, columnspan=2, sticky=W)
        
        # Choosing between hourly and average and spectral albedo
        def Measuredalbedo():
            if rb_Albedo.get()==0:
                SimulationDict["hourlyMeasuredAlbedo"]=False
                SimulationDict["hourlySpectralAlbedo"]=False
                SimulationDict["fixAlbedo"]=True
                SimulationDict["variableAlbedo"]=False
                Label_albedo.config(state="normal")
                Entry_albedo.config(state="normal")
                Combo_Albedo.config(state="normal")
                Entry_reflectivityfile.config(state="disabled")
                Button_reflectivityfile.config(state="disabled")
                Lab_reflectivityfile.config(state="disabled")

            elif rb_Albedo.get()==2:
                SimulationDict["hourlyMeasuredAlbedo"]=False
                SimulationDict["hourlySpectralAlbedo"]=True
                SimulationDict["fixAlbedo"]=False
                SimulationDict["variableAlbedo"]=False
                Label_albedo.config(state="normal")
                Entry_albedo.config(state="normal")
                Combo_Albedo.config(state="normal")
                Entry_reflectivityfile.config(state="normal")
                Button_reflectivityfile.config(state="normal")
                Lab_reflectivityfile.config(state="normal")
            
            elif rb_Albedo.get()==3:
                SimulationDict["hourlyMeasuredAlbedo"]=False
                SimulationDict["hourlySpectralAlbedo"]=False
                SimulationDict["fixAlbedo"]=False
                SimulationDict["variableAlbedo"]=True
                Label_albedo.config(state="disabled")
                Entry_albedo.config(state="disabled")
                Combo_Albedo.config(state="disabled")
                Entry_reflectivityfile.config(state="disabled")
                Button_reflectivityfile.config(state="disabled")
                Lab_reflectivityfile.config(state="disabled")

                
            else:
                SimulationDict["hourlyMeasuredAlbedo"]=True
                SimulationDict["hourlySpectralAlbedo"]=False
                SimulationDict["fixAlbedo"]=False
                SimulationDict["variableAlbedo"]=False
                Label_albedo.config(state="disabled")
                Entry_albedo.config(state="disabled")
                Combo_Albedo.config(state="disabled")
                Entry_reflectivityfile.config(state="disabled")
                Button_reflectivityfile.config(state="disabled")
                Lab_reflectivityfile.config(state="disabled")
                
        #Radiobuttons Albedo
        rb_Albedo=IntVar()
        rb_Albedo.set("0")
        rad1_Albedo= Radiobutton(simulationParameter_frame, variable=rb_Albedo, width=23, text="Average measured Albedo!", value=0, command=lambda:Measuredalbedo())
        rad2_Albedo= Radiobutton(simulationParameter_frame, variable=rb_Albedo,  width=23, text="Hourly measured Albedo!", value=1, command=lambda:Measuredalbedo())
        rad3_Albedo= Radiobutton(simulationParameter_frame, variable=rb_Albedo,  width=20, text="Hourly spectral Albedo!", value=2, command=lambda:Measuredalbedo())
        rad4_Albedo= Radiobutton(simulationParameter_frame, variable=rb_Albedo,  width=20, text="Hourly variable Albedo!", value=3, command=lambda:Measuredalbedo())
        rad1_Albedo.grid(column=0,row=17, sticky=W)
        rad2_Albedo.grid(column=1,row=17, columnspan=2, sticky=W)
        rad3_Albedo.grid(column=0,row=18, sticky=W)
        rad4_Albedo.grid(column=1,row=18, columnspan=2, sticky=W)    
        
        # Get Soiling Rate Value from Json file         
        def getSoilingJSONlist():
                # Load Json file from folder             
                with open(rootPath + '\Lib\input_soiling\Soiling.json') as file:                 
                    jsondata_soiling = json.load(file)
                    systemtuple = ('',) # Needed to enable selection of module
                for key in jsondata_soiling.keys():  # um auf die Modul Keys zurückgreifen zu können
                # build the tuple of strings                 
                    systemtuple = systemtuple + (str(key),)
                Combo_Soilrate['values'] = systemtuple[1:]
            
            # Set Combobox on first module
                Combo_Soilrate.current(0)
                self.jsondata_soiling = jsondata_soiling    
                
        def Soiling():            
            Entry_Soilrate.config(state="normal")
            Combo_Soilrate.config(state="normal")
            Label_distance.config(state="normal")
            Label_weatherstation.config(state="normal")
            Entry_distance.config(state="normal")             
            Entry_weatherstation.config(state="normal")
            getSoilingWeatherdata() # Insures that soiling rate is updated with getSoilingWeatherdata() when Weatherdata has changed
            
            if rb_Soiling.get() == 0:
               SimulationDict["average_daily_soiling_rate"] = False
               SimulationDict["fixed_average_soiling_rate"] = False
               Entry_Soilrate.config(state="normal")
               Combo_Soilrate.config(state="disabled")
               Label_distance.config(state="disabled")
               Label_weatherstation.config(state="disabled")
               Entry_distance.config(state="disabled")                                   
               Entry_weatherstation.config(state="disabled")  
               Entry_clean.config(state="normal")
               Label_clean.config(state="normal")
           
            elif (rb_Soiling.get() == 2):
               SimulationDict["average_daily_soiling_rate"] = False
               SimulationDict["fixed_average_soiling_rate"] = True
               Entry_Soilrate.config(state="disabled")
               Combo_Soilrate.config(state="disabled")
               Label_distance.config(state="normal")
               Label_weatherstation.config(state="normal")
               Entry_distance.config(state="normal")                 
               Entry_weatherstation.config(state="normal")                 
               Entry_clean.config(state="normal")
               Label_clean.config(state="normal")
               #messagebox.showwarning("Main Control", "Confirm Main Control inputs when done!")# Input has to be confirmed with Button to update soiling rate
               
            elif (rb_Soiling.get() == 3):
              SimulationDict["average_daily_soiling_rate"] = True 
              SimulationDict["fixed_average_soiling_rate"] = False
              Entry_Soilrate.config(state="disabled")
              Combo_Soilrate.config(state="disabled")
              Label_distance.config(state="normal")
              Label_weatherstation.config(state="normal")
              Entry_distance.config(state="normal")                 
              Entry_weatherstation.config(state="normal")                 
              Entry_clean.config(state="disabled")
              Label_clean.config(state="disabled")
              #messagebox.showwarning("Main Control", "Confirm Main Control inputs when done!")# Input has to be confirmed with Button to update soiling rate
           
            else:
               SimulationDict["average_daily_soiling_rate"] = False
               SimulationDict["fixed_average_soiling_rate"] = False
               Entry_Soilrate.config(state="normal")
               Combo_Soilrate.config(state="normal")
               Label_distance.config(state="disabled")
               Label_weatherstation.config(state="disabled")
               Entry_distance.config(state="disabled")                 
               Entry_weatherstation.config(state="disabled")                    
               Entry_clean.config(state="normal")
               Label_clean.config(state="normal")
                
        # Radiobuttons Soiling         
        rb_Soiling = IntVar()         
        rb_Soiling.set("0")
        
        rad1_Soiling = Radiobutton(simulationParameter_frame, variable=rb_Soiling, width=23, text="Average daily Soiling Rate! [%/d]", value=0, command=lambda: Soiling())  
        rad2_Soiling = Radiobutton(simulationParameter_frame, variable=rb_Soiling, width=35, text="Soiling rate according to geographical area! [%/d]", value=1, command=lambda: Soiling())        
        rad3_Soiling = Radiobutton(simulationParameter_frame, variable=rb_Soiling, width=47, text="Fixed average soiling rate based on meteorological data! [%/d]", value=2, command=lambda: Soiling()) 
        rad4_Soiling = Radiobutton(simulationParameter_frame, variable=rb_Soiling, width=47, text="Average daily soiling rate based on meteorological data! [%/h]", value=3, command=lambda: Soiling()) 
        
        rad1_Soiling.grid(column=0, row=22, sticky=W) 
        rad2_Soiling.grid(column=0, row=23, sticky=W)        
        rad3_Soiling.grid(column=0, row=24, sticky=W)
        rad4_Soiling.grid(column=0, row=25, sticky=W)

        # Radiobuttons Soiling
        Entry_Soilrate = ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_Soilrate.grid(column=2, row=22, sticky=W)
        
        Entry_weatherstation = ttk.Entry(simulationParameter_frame, background="white", width=35)
        Entry_weatherstation.grid(column=2, row=27, sticky=W)
        
        Entry_distance = ttk.Entry(simulationParameter_frame, background="white", width=35)
        Entry_distance.grid(column=2, row=28, sticky="W")
        
        Entry_clean = ttk.Entry(simulationParameter_frame, background="white", width=35)
        Entry_clean.grid(column=2, row=30, sticky="W")
    
    
    
        # Labels Soiling
        Label_weatherstation = ttk.Label(simulationParameter_frame, text="Weatherstation:")
        Label_weatherstation.grid(column=0, row=27, sticky=W)
        
        Label_distance = ttk.Label(simulationParameter_frame, text="Distance from Station [km]:")
        Label_distance.grid(column=0, row=28, sticky="W")
        
        Label_clean = ttk.Label(simulationParameter_frame, text="Raining / Cleaning period of PV surface [d]:")
        Label_clean.grid(column=0, row=30, sticky="W")
    
        # Zuweisen von Werten für Verschmutzungsrate aus hinterlegten Json-Datei bei Benutzung von Dropdown-liste.       
        def comboclick_soilrate(event):
            key2 = entry_soilrate_value.get()  # what is the value selected?
            if key2 != '':  # '' not a dict key
              b = self.jsondata_soiling[key2]                
              self.soilrate = key2
              # clear module entries loaded from json
              Entry_Soilrate.delete(0, END)
              # set module entries loaded from json
              Entry_Soilrate.insert(0, str(b['soilrate']))
              
        # Combobox Soiling
        entry_soilrate_value = tk.StringVar()
        Combo_Soilrate = ttk.Combobox(simulationParameter_frame, textvariable=entry_soilrate_value)
        Combo_Soilrate.grid(column=2, row=23, ipadx=50)
        getSoilingJSONlist()  # set the module name values
        Combo_Soilrate.bind("<<ComboboxSelected>>", comboclick_soilrate)              
    
        # Calculate nearest location from data set with locations to given coordinates 'v'         
        def closest (data, v):
            return min(data, key=lambda p: GD(v, p).km)    

        # Find nearest location from data set 'new_soilingrate_coordinates_data_2022.csv' and set soiling rate accordingly
        def getSoilingWeatherdata():
            #import Soiling data for the mathematical simulation
            new_soilingrate = pd.read_csv(rootPath + '\Lib\input_soiling\soiling_data.csv', encoding ='latin-1' )            
            new_soilingrate = pd.DataFrame(new_soilingrate)
            #print(new_soilingrate)
            
            cities = [] # Array to collect pairs of latitude and longitude for each location
            new_soilingrate = new_soilingrate.reset_index() # Create index with range of numbers starting with '0'
            #print(new_soilingrate)
                
            # Collcect all pairs of coordinates from soiling_Weatherdata in cities[]
            # for count in new_soilingrate.index:
            count = 0    
            while count < len(new_soilingrate['City, Country']):
                coord = (new_soilingrate["lat"][count], new_soilingrate["lng"][count])
                #print(coord)
                cities.append(coord)
                #print(cities)
                count = count + 1
                
            # Find nearest location to given latitude and longitude from SimulationDict
            nearest_location = closest(cities, (SimulationDict["latitude"],SimulationDict["longitude"]))
            indexout = cities.index(nearest_location)
            #print('Lat and long', nearest_location)
            #print('Index city in the excelsheet:', indexout) 
            
            # clear weatherstation and distance entries         
            Entry_weatherstation.delete(0, END)
            Entry_distance.delete(0, END)
                      
            # set weatherstation entry with nearest location from new_soilingrate
            Entry_weatherstation.insert(0, new_soilingrate['City, Country'].values[indexout])
                
            # set distance entry with distance from simulation location to nearest weatherstation from given data with geodesic      
            Entry_distance.insert(0, round(GD((SimulationDict["latitude"],SimulationDict["longitude"]),cities[indexout]).km, 2))
            new_soilingrate = new_soilingrate.set_index('City, Country')
            
            city_name = Entry_weatherstation.get()  # get the city, country name from 'Entry_weatherstation' 
            SimulationDict["city"] = city_name
            #print (SimulationDict["city"])
            
            # When radiobutton 'Soiling Rate from theorical Model' active, set new soilingrate
            if (rb_Soiling.get() == 3):
                Entry_Soilrate.delete(0, END)
                SimulationDict["average_daily_soiling_rate"] = True

                city_data_directory = (rootPath + '\Lib\input_soiling\city_data_2')
                file_path = os.path.join(city_data_directory, f"{city_name}.csv")
                if os.path.exists(file_path):
                    # The CSV file for the specified city exists, so we can import it as a DataFrame
                    df_city = pd.read_csv(file_path)
                    # Perform any further operations with the DataFrame as needed
                else:
                    # The CSV file for the specified city does not exist in the "city_data" folder
                    # Handle the case where the city data is not available
                    messagebox.showinfo("Error", f"Data for {city_name} are not yet in the database; please choose the Soiling mode 3 (Soiling Rate from weather data) to simulate for this city.")

                # Assuming you have already imported the CSV file and the DataFrame is named 'df_city'
                # Calculate the soilingrate for each row
                t = 86400 #time in s (daily)
                a = SimulationDict["tilt"] #tilt angle of th pv-moduls
                
                #Function to calculate the soiling_accumulation
                def calculate_soiling_accumulation(row):
                    if row['precipitation'] >= 0.3:  #row['humidity'] >= 75 or
                        return 0
                    else:
                        return round(((SimulationDict["nModsx"] * SimulationDict["nModsy"]) * (SimulationDict["moduley"] * SimulationDict["modulex"])) 
                                     * (((row['pm25'] + row['pm10']) * (10 **-9)) * row['wind-speed'] * t * math.cos(math.radians(a))), 6)

                df_city['soiling_accumulation'] = df_city.apply(calculate_soiling_accumulation, axis=1)

                # Display the new DataFrame with the 'soiling_accumulation' column
                #print(df_city)

                # Initialize the cumulative soiling_accumulation rate column with NaN values
                df_city['cum_soiling_accumulation'] = np.nan
                df_city['soilingrate'] = np.nan
                
                # Initialize variables
                values_soiling_accumulation = []
                values_soilingrate_hegazy = []
                
                # Calculate the cumulative soiling rate
                cumulative_soiling_accumulation = 0
                for index, row in df_city.iterrows():
                    if row['soiling_accumulation'] == 0:
                        cumulative_soiling_accumulation = 0
                    else:
                        cumulative_soiling_accumulation += row['soiling_accumulation']
                    df_city.at[index, 'cum_soiling_accumulation'] = cumulative_soiling_accumulation
                    
                    # add the value of cumulative_soiling_accumulation to the list of values_soiling_accumulation
                    values_soiling_accumulation.append(cumulative_soiling_accumulation)
                    
                    #calculate the soilingrate_value for the location using the hegazy model
                    rs_hegazy = ((34.37 * math.erf(0.17*(cumulative_soiling_accumulation**0.8473))) / 100) #hegazy
                    #rs_hegazy_neu = 1 - rs_hegazy
                    # add the value of Soiling to the list of values_soilingrate_hegazy
                    values_soilingrate_hegazy.append(rs_hegazy)
                    
                    df_city.at[index, 'soilingrate'] = rs_hegazy
                    
                # Print the new DataFrame with the "cum_soiling_accumulation" column
                #print(df_city)

                # Extract the first 10 rows of the DataFrame
                #first_10_days = df.head(20)

                # Print the values of "soiling_accumulation" for the first 10 days
                #print(first_10_days['soiling_accumulation'])
                #print(first_10_days['cum_soiling_accumulation'])
                
                SimulationDict["hourlySoilrate"] = values_soilingrate_hegazy

                #save the new Table in the "city_data_soiling_accumulation" folder.
                # Create the directory "city_data_soiling_accumulation" if it doesn't exist
                output_directory = (rootPath + '\BifacialSimu\Handler\city_data_soiling_accumulation') 
                if not os.path.exists(output_directory):
                    os.makedirs(output_directory)

                # Save the DataFrame as a CSV file
                file_path = os.path.join(output_directory, f"{city_name}.csv")
                df_city.to_csv(file_path, index=False)

                #print(f"DataFrame saved as '{Entry_weatherstation}.csv' in the 'city_data_soiling_accumulation' folder.")
                
                Soilingrate_hegazy_new = round((sum(values_soilingrate_hegazy) / len (values_soilingrate_hegazy)), 6)
                print('average of daily Soilingrate for the location indicated:',Soilingrate_hegazy_new, "%/d")
                SimulationDict["fixSoilrate"] = Soilingrate_hegazy_new
                
                #reset value in the Entry_Soilrate
                Entry_Soilrate.delete(0, END)
                Entry_Soilrate.insert(0, SimulationDict["fixSoilrate"])
                
                #  plot the soiling_accumulation graph
                #plt.plot(values_soiling_accumulation, marker = 'o')
                #plt.xlabel('Day [d]')
                #plt.xlabel('Hours [h]')
                #plt.ylabel('Soiling Accumulation [g]')
                #plt.title('Evolution of the Soiling Accumulation over the year')
                #plt.show()
                
                
                #  plot the soiling_hegazy graph
                #plt.plot(values_soilingrate_hegazy, marker = 'o')
                #plt.xlabel('Day [d]')
                #plt.xlabel('Hours [h]')
                #plt.ylabel('Soilingrate')
                #plt.title("Evolution of the Soiling rate over the year")
                #plt.show()
                ######################################################################################################################
            # When radiobutton 'soilingrate from weatherdata' active, set new soilingrate
            if (rb_Soiling.get() == 2):
                
                Entry_Soilrate.delete(0, END)
                SimulationDict["fixed_average_soiling_rate"] = True
                
                #value needed to calculate the dirt accumullation  value for the location found
                PM2_5 = new_soilingrate['PM2_5'].iloc[indexout]
                PM10 = new_soilingrate['PM10'].iloc[indexout]
                wind_speed = new_soilingrate['wind_speed'].iloc[indexout]
                
                #print('pm2.5:', PM2_5)
                #print('pm10:', PM10)
                #print('wind_speed:', wind_speed)
                
                #to calculate the Duration of the simulation 
                Startdate = datetime.datetime(int(Entry_year_start.get()), int(Entry_month_start.get()), int(Entry_day_start.get()), int(Entry_hour_start.get())) #defining as Date
                Enddate = datetime.datetime(int(Entry_year_end.get()), int(Entry_month_end.get()), int(Entry_day_end.get()), int(Entry_hour_end.get()))
                
                # Duration of the simulation (in months)
                simulation_duration = (Enddate - Startdate)  #total in days an hours
                seconds = (simulation_duration.total_seconds()) + 86400  #in seconds
                day = seconds / 86400 #accumulation per day
                #hours = seconds / 3600 #accumulation per hour
                
                #print('Start of The simulation:', Startdate)
                #print('End of The simulation:', Enddate)
                #print('simulation_duration:', simulation_duration)
                #print('simulation_duration in seconds:', seconds, 's')
                #print("simulation_duration in hours:", hours, 'h')
                #print("simulation_duration per day:", day, 'd')

                # Define day_until_clean_second as the time until the next cleaning (in seconds)
                day_until_clean = float(Entry_clean.get()) #cleaning occurs every 15 days
                day_until_clean_second = 86400 * day_until_clean  # in seconds; Assume cleaning occurs every 15 days
#               print("cleaning every:", day_until_clean, 'days')
                #print("cleaning every:", day_until_clean_second, 'seconds')
                
                
                ########calculate the dirt accumullation  value for the location found#######
                # Initialize variables
                delta_t = 0 #timessteps
                soiling_accumulation = 0 #soiling_accumulation
                times = []
                values_soiling_accumulation = []
                values_soilingrate_hegazy = [] 
#               values_soiling_you_saiz = []
#               values_soiling_conceicao = []
                
                angle = SimulationDict["tilt"] # tilt angle
                
                #simulation loop
                #for t in range(int(hours)):
                for t in range(int(day)):
                    
#                   if the period day_until_clean_second is reached, reset soiling_accumulation and delta_t
                    if delta_t == day_until_clean_second:
                        soiling_accumulation = 0
                        delta_t = 0 
                        
                    # Calculate new value of soiling_accumulation
                    soiling_accumulation = (((SimulationDict["nModsx"] * SimulationDict["nModsy"]) * (SimulationDict["moduley"] * SimulationDict["modulex"]))*(((PM2_5 + PM10)*(10**(-9))) * wind_speed * delta_t * math.cos(math.radians(angle)))) # Coello 
                    #soiling_accumulation = (((PM2_5 + PM10)*(10**(-9))) * wind_speed * math.cos(math.radians(angle)))  # Coello 
                    # add the value of soiling_accumulation to the list of values_soiling_accumulation
                    values_soiling_accumulation.append(soiling_accumulation)
                    
                    
                    #calculate the soilingvvalue for the location using the hegazy model
                    rs_hegazy = ((34.37 * math.erf(0.17*(soiling_accumulation**0.8473))) / 100) #hegazy
                    #rs_hegazy_neu = 1 - rs_hegazy
                    #add the value of Soiling to the list of values_soilingrate_hegazy
                    values_soilingrate_hegazy.append(rs_hegazy)
                    
                    
                    #You_Saiz model
#                   rs_you_saiz = ((0.0385 * soiling_accumulation)) #“You/Saiz”.
                    #rs_you_saiz_neu = 1 - (rs_you_saiz)                    
                    # add the value of Soiling_rs_you_saiz to the list of values_soiling_you_saiz
#                   values_soiling_you_saiz.append(rs_you_saiz)
                    
                    #conceicao model
#                   rs_conceicao = ((0.2545 * soiling_accumulation^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^    	^^^^^^^^^^^^^^                     
                    # add the value of Soiling_rs_conceicao to the list of values_soiling_conceicao
#                   values_soiling_conceicao.append(rs_conceicao)
                    
                    # add the current hour to the time list in hours
                    times.append(t)
                    
                   #Print current values of soiling_accumulation and delta_t
                    #print('Index_location:', indexout)
                    #print("delta_t:", delta_t)
                    #print('S:', soiling_accumulation, 'g/m²')
                    #print('rs_hegazy:', rs_hegazy, '%/d')
                    #print('rs_hegazy_neu:', rs_hegazy_neu)
                    #print('rs_you_saiz:', rs_you_saiz)
                    #print('rs_you_saiz_neu:', rs_you_saiz_neu)
                    #print('rs_conceicao:', rs_conceicao)

                    #increment the  hourly / daily time interval
                    #delta_t += 3600 #hourly
                    delta_t += 86400 #daily

                #print(values_soilingrate_hegazy)
                #print('time', times)
                
                # Creating the csv table with Soiling data of the Location with the Index(indexout)
                with open('Soiling{}.csv'.format(indexout), mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(['Hours', 'soiling_accumulation', 'rs_hegazy'])  # Column headings #, 'rs_you_saiz', 'rs_conceicao' 
                    for i in range(len(times)):
                        writer.writerow([times[i], values_soiling_accumulation[i], values_soilingrate_hegazy[i]])  # Adding data to the table #, values_soiling_you_saiz[i], values_soiling_conceicao[i]
               
                #plot the soiling_accumulation graph
                #plt.plot(times, values_soiling_accumulation)
                #plt.xlabel('Day [d]')
                #plt.xlabel('Hours [h]')
                #plt.ylabel('Soiling Accumulation [g]')
                #plt.title('Evolution of the Soiling Accumulation over the Simulation interval')
                #plt.show()

                #  plot the soiling_hegazy graph
                #plt.plot(times, values_soilingrate_hegazy)
                #plt.xlabel('Day [d]')
                #plt.xlabel('Hours [h]')
                #plt.ylabel('Soilingrate')
                #plt.title("Evolution of the Soiling rate over the Simulation interval")
                #plt.show()
                
                #for experimental Soiling   
                # When radiobutton 'Soiling Rate from theorical Model' active, set new soilingrate
                #insert the new soiling value to the variable in simulation dictionary. 
                
                #SimulationDict["hourlySoilrate"] = values_soilingrate_hegazy
                #print("Soiling rate hegazy:", SimulationDict["hourlySoilrate"])
                
                Soilingrate_hegazy_new = round((sum(values_soilingrate_hegazy) / len (values_soilingrate_hegazy)), 6)
                #print('average for the location indicated as a function of the length of the simulation:',Soilingrate_hegazy_new)
                SimulationDict["fixSoilrate"] = Soilingrate_hegazy_new
                
                #reset value in the Entry_Soilrate
                Entry_Soilrate.delete(0, END)
                Entry_Soilrate.insert(0, SimulationDict["fixSoilrate"])
                
                if Soilingrate_hegazy_new == 0:
                    # Load csv file with soiling rates from over 500 locations  and convert to pandas dataframe
                    soilingrate_Weatherdata = pd.read_csv(rootPath + '\Lib\input_soiling\soilingrate_coordinates_monthly_2022.csv',  encoding ='latin-1')
                    soilingrate_Weatherdata = pd.DataFrame(soilingrate_Weatherdata)
                    #print(soilingrate_Weatherdata)
                    
                    cities = [] # Array to collect pairs of latitude and longitude for each location
                    soilingrate_Weatherdata = soilingrate_Weatherdata.reset_index() # Create index with range of numbers starting with '0'
                    #print(soilingrate_Weatherdata)
                   
                    # Collcect all pairs of coordinates from soiling_Weatherdata in cities[]
                    # for count in soilingrate_Weatherdata.index:

                    count = 0    
                    while count < len(soilingrate_Weatherdata['City, Country']):
                        coord = (soilingrate_Weatherdata["lat"][count], soilingrate_Weatherdata["lng"][count])
                    #print(coord)
                        cities.append(coord)
                    #print(cities)
                        count = count + 12
                    
                    # Find nearest location to given latitude and longitude from SimulationDict
                    nearest_location = closest(cities, (SimulationDict["latitude"],SimulationDict["longitude"]))
                    indexout = cities.index(nearest_location)
#                   print('Lat and long', nearest_location)
#                   print('Index city in the excelsheet:', indexout) 
                    
                    
                    # clear weatherstation and distance entries         
                    Entry_weatherstation.delete(0, END)
                    Entry_distance.delete(0, END)
                              
                    # set weatherstation entry with nearest location from soilingrate_Weatherdata
                    Entry_weatherstation.insert(0, soilingrate_Weatherdata['City, Country'].values[indexout*12])
                        
                    # set distance entry with distance from simulation location to nearest weatherstation from given data with geodesic      
                    Entry_distance.insert(0, round(GD((SimulationDict["latitude"],SimulationDict["longitude"]),cities[indexout]).km, 2))
                    soilingrate_Weatherdata = soilingrate_Weatherdata.set_index('City, Country')
                    
                    SimulationDict["variableSoilrate"] = soilingrate_Weatherdata['Soiling_Rate'].iloc[indexout*12:(indexout*12 + 12)].values.tolist()
                    #SimulationDict["fixSoilrate"] = SimulationDict["variableSoilrate"]
                    
                    #print("Monthly Soiling Rates:", SimulationDict["variableSoilrate"])
                    
                    
                    #to calculate the Duration of the simulation 
#                   Startdate = datetime.datetime(int(Entry_year_start.get()), int(Entry_month_start.get()), int(Entry_day_start.get()), int(Entry_hour_start.get())) #defining as Date
#                   Enddate = datetime.datetime(int(Entry_year_end.get()), int(Entry_month_end.get()), int(Entry_day_end.get()), int(Entry_hour_end.get()))
                    
                    # Duration of the simulation (in months)
#                   simulation_duration = Enddate - Startdate
#                   
#                   print('Startdate:', Startdate)
#                   print('Enddate:', Enddate)
#                   print('simulation_duration:', simulation_duration)
#                   
                    
                    #reset value in the Entry_Soilrate
                    average_Soiling = round((sum(SimulationDict["variableSoilrate"]) / len (SimulationDict["variableSoilrate"])), 6)
                    print('average for the location indicated as a function of the length of the simulation:', average_Soiling)
                    SimulationDict["fixSoilrate"] = average_Soiling
                    
                    #reset value in the Entry_Soilrate
                    Entry_Soilrate.delete(0, END)
                    Entry_Soilrate.insert(0, SimulationDict["fixSoilrate"])

        # Defining the electrical Mode with or without Values of rear side
        def Electricalmode():
           if rb_ElectricalMode.get()==0:
               SimulationDict["ElectricalMode_simple"]= 1 #One diode front and back
           if rb_ElectricalMode.get()==1:
               SimulationDict["ElectricalMode_simple"]= 0 #One diode front and Bi factor
           if rb_ElectricalMode.get()==2:
               SimulationDict["ElectricalMode_simple"]= 2 #Two Diode front and back
           if rb_ElectricalMode.get()==3:
               SimulationDict["ElectricalMode_simple"]= 3 #Two Diode front and Bi factor
               
          # else:
         #      SimulationDict["ElectricalMode_simple"]=True
               
   
        #Radiobuttons for the two-diode-Methodes
   
        rb_ElectricalMode=IntVar()
        rb_ElectricalMode.set("0")
   
        rad1_ElectricalMode= Radiobutton(ModuleParameter_frame, variable=rb_ElectricalMode, width=22, text="OneDiode front and back", value=0, command=lambda:Electricalmode())
        rad2_ElectricalMode= Radiobutton(ModuleParameter_frame, variable=rb_ElectricalMode, width=21, text="OneDiode with BiFactor", value=1, command=lambda:Electricalmode())
        #rad3_ElectricalMode= Radiobutton(ModuleParameter_frame, variable=rb_ElectricalMode, width=22, text="TwoDiode front and back", value=2, command=lambda:Electricalmode())
        rad4_ElectricalMode= Radiobutton(ModuleParameter_frame, variable=rb_ElectricalMode, width=21, text="TwoDiode with BiFactor", value=3, command=lambda:Electricalmode())
        rad1_ElectricalMode.grid(column=0,row=3, sticky=W)
        rad2_ElectricalMode.grid(column=1,row=3, columnspan=1, sticky=W)
        #rad3_ElectricalMode.grid(column=0,row=4, sticky=W)
        rad4_ElectricalMode.grid(column=1,row=4, columnspan=1, sticky=W)
  
    
  
        #Radiobutton Choice Rear values
        #rb_ElectricalMode=IntVar()
        #rb_ElectricalMode.set("0")
        #rad1_ElectricalMode= Radiobutton(ModuleParameter_frame, variable=rb_ElectricalMode, width=15, text="With rear values!", value=0, command=lambda:Electricalmode())
        #rad2_ElectricalMode= Radiobutton(ModuleParameter_frame, variable=rb_ElectricalMode,  width=18, text="Without rear values!", value=1, command=lambda:Electricalmode())
        #rad1_ElectricalMode.grid(column=0,row=2, sticky=W)
        #rad2_ElectricalMode.grid(column=1,row=2, columnspan=1, sticky=W)
        
        
        # Defining Backtracking
        def Backtracking():
            if rb_Backtracking.get()==0:
                SimulationDict["backTracking"]=False
                
            else:
                SimulationDict["backTracking"]=True
        
        
        
        rb_Backtracking=IntVar()
        rb_Backtracking.set("0")
        rad1_BacktrackingMode= Radiobutton(simulationParameter_frame, variable=rb_Backtracking, width=19, text="Without Backtracking!", value=0, command=lambda:Backtracking())
        rad2_BacktrackingMode= Radiobutton(simulationParameter_frame, variable=rb_Backtracking,  width=15, text="With Backtracking!", value=1, command=lambda:Backtracking())
        rad1_BacktrackingMode.grid(column=0,row=4, sticky=W)
        rad2_BacktrackingMode.grid(column=1,row=4, columnspan=2, sticky=W)        
        
        
        
    def simulate_oneDiode(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath):
        """
        Applies the one diode model for bifacial electrical simulation. Needs module front and rear parameters to work correctly.
        Calculates bifacial gain through a seperate monofacial electrical simulation.

        Parameters
        ----------
        moduleDict: module Dictionary containing module data
        simulationDict: simulation Dictionary, which can be found in BifacialSimuu_main.py
        df_reportVF: Viewfactor simulation report
        df_reportRT: Raytracing simulation report
        df_report: Final simulation report, containing VF and RT data
        resultsPath: output filepath
        df: helper DataFrame containing temperature for electrical simulation
        """
        
        
        
        # Build a final simutlation report
        df_report = Electrical_simulation.build_simulationReport(df_reportVF, df_reportRT, simulationDict, resultsPath)
        
        ####################################################
        # Variables required for electrical simulation
        
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
        V_mpp_f0 = moduleDict['V_mpp_f']
        V_mpp_r0 = moduleDict['V_mpp_r']
        
        I_mpp_f0 = moduleDict['I_mpp_f']
        I_mpp_r0 = moduleDict['I_mpp_r']
        
        I_sc_r0 = moduleDict['I_sc_r']
        I_sc_f0 = moduleDict['I_sc_f']
        
        V_oc_r0 = moduleDict['V_oc_r']
        V_oc_f0 = moduleDict['V_oc_f']
        
        soilrate = simulationDict['fixSoilrate']
        days_until_clean = simulationDict['days_until_clean']
        
        #module = moduleParameter['module']
        #inverter = moduleParameter['inverter']
        
        P_mpp0 = moduleDict['P_mpp']
        V_mpp0 = V_mpp_f0
        
        T_koeff_P = moduleDict['T_koeff_P'] 
        T_koeff_I = moduleDict['T_koeff_I'] 
        T_koeff_V = moduleDict['T_koeff_V'] 
        T_amb = moduleDict['T_amb']
        
        q_stc_front = 1000  # [W/m^2] 
        q_stc_rear = 1000   # [W/m^2] 
        
        # Calculation of fill factor for STC conditions
        FF_f0 = (I_mpp_f0 * V_mpp_f0)/(I_sc_f0 * V_oc_f0) 
        FF_r0 = (I_mpp_r0 * V_mpp_r0)/(I_sc_r0 * V_oc_r0) 
        
        
        dpi = 300 #Quality for plot export
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
        P_m_hourly_arrays = []
        
        df_report['timestamp'] = df_report.index
        df_report = df_report.reset_index()
        df_report['corrected_timestamp'] = pd.to_datetime(df_report['timestamp'])
        df_report['time'] = df_report['corrected_timestamp'].dt.strftime('%m_%d_%H')
        df_report = df_report.set_index('time')
        
        #################################################################################
        #soilingrate from theorical model
        city_name = simulationDict["city"]  # get the city, country name from 'Entry_weatherstation' 
        #print (str(city_name))
        #new_soilingrate = pd.read_csv(rootPath + '\Lib\input_soiling\soiling_data.csv', encoding ='latin-1' ) 
        df_city = pd.read_csv(rootPath + f'\city_data_soiling_accumulation\{city_name}.csv')
        #file_path = os.path.join(city_data_directory, f"{city_name}.csv")
        #df_city = pd.read_csv(file_path)
        # Convert the 'Date' column into date format for both DataFrames
        df_city['Date'] = pd.to_datetime(df_city['Date'], dayfirst=True)
        df_report['corrected_timestamp'] = pd.to_datetime(df_report['corrected_timestamp'], dayfirst=True)

        # Create an empty list to store the corresponding soilingrate values
        sr_value = []

        # Browse rows in DataFrame "df_report
        for index, row in df_report.iterrows():
            # Extract the date (day and month) of the current row from the "df_report" DataFrame
            date_df_report = row['corrected_timestamp'].replace(year=2023)  # Replace year with appropriate year
            
            # Filter the "City, Country" DataFrame to obtain rows with the same date (day and month)
            df_filtered = df_city[(df_city['Date'].dt.day == date_df_report.day) & (df_city['Date'].dt.month == date_df_report.month)]
            
            # Check whether rows have been found in the filtered DataFrame
            if not df_filtered.empty:
                # Retrieve the soilingrate value from the first corresponding line
                soilingrate_value = df_filtered.iloc[0]['soilingrate']
                
                # Add the soilingrate value to the "sr_value" list
                sr_value.append(soilingrate_value)
            else:
                # Add a default value (for example, 0) if no corresponding soilingrate value has been found
                sr_value.append(0)
        simulationDict["hourlySoilrate"] = sr_value
        #print('AAA', len(simulationDict["hourlySoilrate"]))
        #print('VBBB', len(sr_value))
        #print('XXXXXXX', len(df_report))
        #df_reportVF
        # Display the list containing the corresponding soilingrate values for each identical day and month
        #print(len(sr_value))
        #print(sr_value)
        ############################################################################################################################################################
        
        #Soilingrate from weather data
        df_time_soiling = pd.DataFrame(df_report['corrected_timestamp'])
        df_time_soiling['month'] = df_report['corrected_timestamp'].dt.strftime('%m') # Needed to choose wright soiling rate from SimulationDict
        df_time_soiling['day'] = df_report['corrected_timestamp'].dt.strftime('%d') # Needed to choose wright soiling rate from 
        df_time_soiling['year'] = df_report['corrected_timestamp'].dt.strftime('%y') # Needed to choose wright soiling rate from SimulationDict 
        df_time_soiling = df_time_soiling.reset_index(drop = True)
        
        
        if simulationDict['simulationMode'] == 3:
            df = df.reset_index()
            
            df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
            df = df.set_index('time')
            df['timestamp'] = df['corrected_timestamp'].dt.strftime('%m-%d %H:%M%')
            df['timestamp'] = pd.to_datetime(df['timestamp'])  
            #df['timestamp'] = df['timestamp'].dt.tz_localize(None)
            df = df.set_index('timestamp')
            
            dtStart = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
        
        
            dtEnd = datetime.datetime(simulationDict['endHour'][0], simulationDict['endHour'][1], simulationDict['endHour'][2], simulationDict['endHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
            mask = (df.index >= dtStart) & (df.index <= dtEnd) 
            df = df.loc[mask]
        
        df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
        df = df.set_index('time')
        
        
        # Loop to calculate the Bifacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front = "row_" + str(i) + "_qabs_front"
            key_back = "row_" + str(i) + "_qabs_back"
        
            P_bi_hourly = []
            
            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
            y = 0

            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                if temp == days_until_clean*24:
                    temp = 0
                else:
                    temp = temp +1

                if simulationDict["average_daily_soiling_rate"] == True:
                    soilrate = simulationDict["hourlySoilrate"]
                    
                    if simulationDict['simulationMode'] == 1 or simulationDict['simulationMode'] == 2 or simulationDict['simulationMode'] == 3:
                        # calculate front row power output including the soiling rate determined in GUI                               
                        row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate[y]/100))
                        # calculate back row power output including the decreased soiling for backside of PV module                                 
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate[y]/(100*10.581)))
                        
                    if simulationDict['simulationMode'] == 5:
                        row_qabs_front = 0
                    else:
                        row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate[y]/100))
#                        T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))

                    if simulationDict['simulationMode'] == 4:
                        row_qabs_back = 0
                    else:
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate[y]/(100*10.581)))
#                        T_Current = df.loc[index,'temperature'] + ((row_qabs_back/800)*(moduleDict['T_NOCT'] - 20))

                    # estimate module temperture with ambient temperature and NOCT temp
                    T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                    if np.isnan(T_Current):
                        T_Current = df.loc[index,'temperature']
                    
                        

                    #print("front: " + str(row_qabs_front))
                    #print("back: " + str(row_qabs_back))
                    
                    if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                        row_qabs_front = 0
                        
                    if math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                        row_qabs_back = 0

                    
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
                    y = y +1

#                    for i in range(len(soilrate)):

                else:
                    soilrate = simulationDict['fixSoilrate']
                    
                    if simulationDict['simulationMode'] == 1 or simulationDict['simulationMode'] == 2 or simulationDict['simulationMode'] == 3:
                        # calculate front row power output including the soiling rate determined in GUI                               
                        row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate*(temp)/(100*24)))
                        # calculate back row power output including the decreased soiling for backside of PV module                                 
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate*(temp)/(100*24*10.581)))
                        
                    if simulationDict['simulationMode'] == 5:
                        row_qabs_front = 0
                    else:
                        row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate*(temp)/(100*24)))
#                        T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                        
                    if simulationDict['simulationMode'] == 4:
                        row_qabs_back = 0
                    else:
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate*(temp)/(100*24*10.581)))
#                        T_Current = df.loc[index,'temperature'] + ((row_qabs_back/800)*(moduleDict['T_NOCT'] - 20))

                    # estimate module temperture with ambient temperature and NOCT temp
                    T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                    if np.isnan(T_Current):
                        T_Current = df.loc[index,'temperature']
                        
                    
                    
                    #print("front: " + str(row_qabs_front))
                    #print("back: " + str(row_qabs_back))
                    
                    if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                        row_qabs_front = 0
                        
                    if math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                        row_qabs_back = 0

                    
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
        
       
# =============================================================================
#    Simulations Parameter Frame
# =============================================================================
    
  
        # Tilt
        Label_Tilt=ttk.Label(simulationParameter_frame, text="Fixed Tilt of the PV surface:")
        Label_Tilt.grid(column=0, row=2, sticky=W)
        Label_TiltPar=ttk.Label(simulationParameter_frame, text="[Deg °]")
        Label_TiltPar.grid(column=2, row=2, sticky=W)
        Entry_Tilt=ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_Tilt.grid(column=1, row=2, sticky=W)

        #Limit Angle
        Label_LimitAngle=ttk.Label(simulationParameter_frame, text="Limit Angle of Tracking System:")
        Label_LimitAngle.grid(column=0, row=3, sticky=W)
        Label_LimitAnglePar=ttk.Label(simulationParameter_frame, text="[Deg°]")
        Label_LimitAnglePar.grid(column=2, row=3, sticky=W)
        Entry_LimitAngle=ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_LimitAngle.grid(column=1, row=3, sticky=W)
        
        #hub_height and Clearance Height
        Label_ClearanceHeight=ttk.Label(simulationParameter_frame, text="Clearence height:")
        Label_HubHeight=ttk.Label(simulationParameter_frame, text="Hub height:")
        Label_ClearanceHeight.grid(column=0, row=5, sticky=W)
        Label_HubHeight.grid(column=0, row=6, sticky=W)
        Label_ClearanceHeightPar=ttk.Label(simulationParameter_frame, text="[m]")
        Label_HubHeightPar=ttk.Label(simulationParameter_frame, text="[m]")
        Label_ClearanceHeightPar.grid(column=2, row=5, sticky=W)
        Label_HubHeightPar.grid(column=2, row=6, sticky=W)
        Entry_ClearanceHeight=ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_HubHeight=ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_ClearanceHeight.grid(column=1, row=5, sticky=W)
        Entry_HubHeight.grid(column=1, row=6, sticky=W)
        
        # The time gets implemented in the GUI
    # p_bi_df.to_csv(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
        
        
        annual_power_per_module_b = (sum_energy_b/simulationDict['nRows']) #[W] annual bifacial output power per module
        '''print("Yearly bifacial output power per module: " + str(annual_power_per_module_b) + " W/module")
        print("Yearly bifacial output energy per module: " + str(annual_power_per_module_b/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
        print ("\n")'''
        
        annual_power_per_peak_b = (sum_energy_b/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual bifacial output power per module peak power
        '''print("Yearly bifacial output power per module peak power: " + str(annual_power_per_peak_b) + " W/Wp")
        print("Yearly bifacial output energy per module peak power: " + str(annual_power_per_peak_b) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        module_area = (simulationDict['moduley'] *simulationDict['nModsy'] *simulationDict['modulex'])
        
        
       
        #Azimuth of the PV surface
        Label_Azimuth=ttk.Label(simulationParameter_frame, text="Azimuth of PV surface:")
        Label_Azimuth.grid(column=0, row=7, sticky=W)
        Label_AzimuthPar=ttk.Label(simulationParameter_frame, text="[Deg°]" +" (90° = East) (180°= South)")
        Label_AzimuthPar.grid(column=2, row=7, sticky=W)
        Entry_Azimuth=ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_Azimuth.grid(column=1, row=7, sticky=W)
        
        #Number of rows and Modules in Rows
        Label_nRows=ttk.Label(simulationParameter_frame, text="Number of Rows:")
        Label_nModsx=ttk.Label(simulationParameter_frame, text="Number of Modules in Row in X Axis:")
        Label_nModsy=ttk.Label(simulationParameter_frame, text="Number of Modules in Row in Y Axis:")
        Label_nRows.grid(column=0, row=8, sticky=W)
        Label_nModsx.grid(column=0, row=9, sticky=W)
        Label_nModsy.grid(column=0, row=10, sticky=W)
        Label_nRowsPar=ttk.Label(simulationParameter_frame, text="[-]")
        Label_nModsxPar=ttk.Label(simulationParameter_frame, text="[-]")
        Label_nModsyPar=ttk.Label(simulationParameter_frame, text="[-]")
        Label_nRowsPar.grid(column=2, row=8, sticky=W)
        Label_nModsxPar.grid(column=2, row=9, sticky=W)
        Label_nModsyPar.grid(column=2, row=10, sticky=W)
        Entry_nRows=ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_nModsx=ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_nModsy=ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_nRows.grid(column=1, row=8, sticky=W)
        Entry_nModsx.grid(column=1, row=9, sticky=W)
        Entry_nModsy.grid(column=1, row=10, sticky=W)

        #sensors
        Label_sensors=ttk.Label(simulationParameter_frame, text="Number of Sensors:")
        Label_sensors.grid(column=0, row=11, sticky=W)
        Label_sensorsPar=ttk.Label(simulationParameter_frame, text="[-]")
        Label_sensorsPar.grid(column=2, row=11, sticky=W)
        Entry_sensors=ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_sensors.grid(column=1, row=11, sticky=W)

        #Lenght of Modules in y and x-axis
        Label_moduley=ttk.Label(simulationParameter_frame, text="Length of modules in y-axis:")
        Label_modulex=ttk.Label(simulationParameter_frame, text="Length of modules in x-axis:")
        Label_moduley.grid(column=0, row=12, sticky=W)
        Label_modulex.grid(column=0, row=13, sticky=W)
        Label_moduleyPar=ttk.Label(simulationParameter_frame, text="[m]")
        Label_modulexPar=ttk.Label(simulationParameter_frame, text="[m]")
        Label_moduleyPar.grid(column=2, row=12, sticky=W)
        Label_modulexPar.grid(column=2, row=13, sticky=W)
        Entry_moduley=ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_modulex=ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_moduley.grid(column=1, row=12, sticky=W)
        Entry_modulex.grid(column=1, row=13, sticky=W)
        

        #front and back reflect of the surface
        Label_frontReflect=ttk.Label(simulationParameter_frame, text="Front surface reflectivity of PV rows:")
        Label_backReflect=ttk.Label(simulationParameter_frame, text="Back surface reflectivity of PV rows:")
        Label_frontReflect.grid(column=0, row=14, sticky=W)
        Label_backReflect.grid(column=0, row=15, sticky=W)
        Label_frontReflectPar=ttk.Label(simulationParameter_frame, text="[-]")
        Label_backReflectPar=ttk.Label(simulationParameter_frame, text="[-]")
        Label_frontReflectPar.grid(column=2, row=14, sticky=W)
        Label_backReflectPar.grid(column=2, row=15, sticky=W)
        Entry_frontReflect=ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_backReflect=ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_frontReflect.grid(column=1, row=14, sticky=W)
        Entry_backReflect.grid(column=1, row=15, sticky=W)
        
        #gcr
        Label_gcr=ttk.Label(simulationParameter_frame, text="Ground coverage ratio:")
        Label_gcr.grid(column=0, row=16, sticky=W)
        Label_gcrPar=ttk.Label(simulationParameter_frame, text="[-] (module area / land use)")
        Label_gcrPar.grid(column=2, row=16, sticky=W)
        Entry_gcr=ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_gcr.grid(column=1, row=16, sticky=W)        
        
        #with or without rear  / Warning        
        #Labela_modulinfo=ttk.Label(ModuleParameter_frame, text="", background = 'white')
        #Labela_modulinfo.grid(column=0, columnspan=3, row=21, sticky=W)
        #Entry_modulinfo=ttk.Entry(ModuleParameter_frame, background="white", width=16)
        #Label_modulinfo=ttk.Label(ModuleParameter_frame, text="If your choice for the module attribute is 'With rear values!' use the modules 1 to 3 in the Combobox.\nIf your choice is 'Without rear values' use the modules 4 to the end of the list.", background = 'red',font=8)
        #Label_modulinfo.grid(column=0, columnspan=3, row=23, sticky=W)
        #Entry_modulinfo=ttk.Entry(ModuleParameter_frame, background="white", width=8)       
            
        
# =============================================================================
#     Configuration for the module dict
# ============================================================================= 
        
        #Bifaciality factor
        Label_bi_factor=ttk.Label(ModuleParameter_frame, text="bi_factor:")
        Label_bi_factor.grid(column=0, row=5, sticky=W)
        Label_bi_factorPar=ttk.Label(ModuleParameter_frame, text="[-]")
        Label_bi_factorPar.grid(column=2, row=5, sticky=W)
        Entry_bi_factor=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_bi_factor.grid(column=1, row=5, sticky=W)   
        
        #Wirkungsgrad Vorderseite
        Label_nfront=ttk.Label(ModuleParameter_frame, text="n_front:")
        Label_nfront.grid(column=0, row=6, sticky=W)
        Label_nfrontPar=ttk.Label(ModuleParameter_frame, text="[-]")
        Label_nfrontPar.grid(column=2, row=6, sticky=W)
        Entry_nfront=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_nfront.grid(column=1, row=6, sticky=W)   

        Label_Iscf=ttk.Label(ModuleParameter_frame, text="I_sc_f:")
        Label_Iscf.grid(column=0, row=7, sticky=W)
        Label_IscfPar=ttk.Label(ModuleParameter_frame, text="[A]")
        Label_IscfPar.grid(column=2, row=7, sticky=W)
        Entry_Iscf=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_Iscf.grid(column=1, row=7, sticky=W)    
        
        Label_Iscr=ttk.Label(ModuleParameter_frame, text="I_sc_r:")
        Label_Iscr.grid(column=0, row=8, sticky=W)
        Label_IscrPar=ttk.Label(ModuleParameter_frame, text="[A]")
        Label_IscrPar.grid(column=2, row=8, sticky=W)
        Entry_Iscr=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_Iscr.grid(column=1, row=8, sticky=W)    
        
        Label_Vocf=ttk.Label(ModuleParameter_frame, text="V_oc_f:")
        Label_Vocf.grid(column=0, row=9, sticky=W)
        Label_VocfPar=ttk.Label(ModuleParameter_frame, text="[V]")
        Label_VocfPar.grid(column=2, row=9, sticky=W)
        Entry_Vocf=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_Vocf.grid(column=1, row=9, sticky=W)  
        
        Label_Vocr=ttk.Label(ModuleParameter_frame, text="V_oc_r:")
        Label_Vocr.grid(column=0, row=10, sticky=W)
        Label_VocrPar=ttk.Label(ModuleParameter_frame, text="[V]")
        Label_VocrPar.grid(column=2, row=10, sticky=W)
        Entry_Vocr=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_Vocr.grid(column=1, row=10, sticky=W)  
        
        Label_Vmppf=ttk.Label(ModuleParameter_frame, text="V_mpp_f:")
        Label_Vmppf.grid(column=0, row=11, sticky=W)
        Label_VmppfPar=ttk.Label(ModuleParameter_frame, text="[V]")
        Label_VmppfPar.grid(column=2, row=11, sticky=W)
        Entry_Vmppf=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_Vmppf.grid(column=1, row=11, sticky=W)  
        
        Label_Vmppr=ttk.Label(ModuleParameter_frame, text="V_mpp_r:")
        Label_Vmppr.grid(column=0, row=12, sticky=W)
        Label_VmpprPar=ttk.Label(ModuleParameter_frame, text="[V]")
        Label_VmpprPar.grid(column=2, row=12, sticky=W)
        Entry_Vmppr=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_Vmppr.grid(column=1, row=12, sticky=W)  
        
        Label_Imppf=ttk.Label(ModuleParameter_frame, text="I_mpp_f:")
        Label_Imppf.grid(column=0, row=13, sticky=W)
        Label_ImppfPar=ttk.Label(ModuleParameter_frame, text="[A]")
        Label_ImppfPar.grid(column=2, row=13, sticky=W)
        Entry_Imppf=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_Imppf.grid(column=1, row=13, sticky=W) 
        
        Label_Imppr=ttk.Label(ModuleParameter_frame, text="I_mpp_r:")
        Label_Imppr.grid(column=0, row=14, sticky=W)
        Label_ImpprPar=ttk.Label(ModuleParameter_frame, text="[A]")
        Label_ImpprPar.grid(column=2, row=14, sticky=W)
        Entry_Imppr=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_Imppr.grid(column=1, row=14, sticky=W) 
        
        Label_Pmpp=ttk.Label(ModuleParameter_frame, text="P_mpp:")
        Label_Pmpp.grid(column=0, row=15, sticky=W)
        Label_PmppPar=ttk.Label(ModuleParameter_frame, text="[W]")
        Label_PmppPar.grid(column=2, row=15, sticky=W)
        Entry_Pmpp=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_Pmpp.grid(column=1, row=15, sticky=W) 
        
        Label_TkoeffP=ttk.Label(ModuleParameter_frame, text="T_koeff_P:")
        Label_TkoeffP.grid(column=0, row=16, sticky=W)
        Label_TkoeffPPar=ttk.Label(ModuleParameter_frame, text="[1 / \u00b0C]")
        Label_TkoeffPPar.grid(column=2, row=16, sticky=W)
        Entry_TkoeffP=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_TkoeffP.grid(column=1, row=16, sticky=W) 
        
        Label_Tamb=ttk.Label(ModuleParameter_frame, text="T_amb:")
        Label_Tamb.grid(column=0, row=17, sticky=W)
        Label_TambPar=ttk.Label(ModuleParameter_frame, text="[\u00b0C]")
        Label_TambPar.grid(column=2, row=17, sticky=W)
        Entry_Tamb=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_Tamb.grid(column=1, row=17, sticky=W) 
        
        Label_TkoeffI=ttk.Label(ModuleParameter_frame, text="T_koeff_I:")
        Label_TkoeffI.grid(column=0, row=18, sticky=W)
        Label_TkoeffIPar=ttk.Label(ModuleParameter_frame, text="[1 / \u00b0C]")
        Label_TkoeffIPar.grid(column=2, row=18, sticky=W)
        Entry_TkoeffI=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_TkoeffI.grid(column=1, row=18, sticky=W) 
        
        Label_TkoeffV=ttk.Label(ModuleParameter_frame, text="T_koeff_V:")
        Label_TkoeffV.grid(column=0, row=19, sticky=W)
        Label_TkoeffVPar=ttk.Label(ModuleParameter_frame, text="[1 / \u00b0C]")
        Label_TkoeffVPar.grid(column=2, row=19, sticky=W)
        Entry_TkoeffV=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_TkoeffV.grid(column=1, row=19, sticky=W) 
        
        Label_zeta=ttk.Label(ModuleParameter_frame, text="zeta:")
        Label_zeta.grid(column=0, row=20, sticky=W)
        Label_zetaPar=ttk.Label(ModuleParameter_frame, text="[-]")
        Label_zetaPar.grid(column=2, row=20, sticky=W)
        Entry_zeta=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_zeta.grid(column=1, row=20, sticky=W) 
        
        Label_Ns=ttk.Label(ModuleParameter_frame, text="Ns:")
        Label_Ns.grid(column=0, row=20, sticky=W)
        Label_NsPar=ttk.Label(ModuleParameter_frame, text="[-]")
        Label_NsPar.grid(column=2, row=20, sticky=W)
        Entry_Ns=ttk.Entry(ModuleParameter_frame, background="white", width=8)
        Entry_Ns.grid(column=1, row=20, sticky=W) 
        

        
# =============================================================================
#          Config file (default.ini) 
# =============================================================================
         
        parser = ConfigParser()
        parser.read(rootPath + '/Lib/default/default.ini')
        simulationName_configfile=parser.get('default', 'simulationName')
       # simulationMode_configfile=parser.get('default', 'simulationMode')
        weatherFile_configfile=parser.get('default', "weatherFile")
        reflectivityFile_configfile=parser.get('default', "reflectivityFile")
        tilt_configfile=parser.get('default', 'tilt')
        limitAngle_configfile=parser.getfloat('default', 'limitAngle')
        ClearanceHeight_configfile=parser.getfloat('default', 'clearance_height')
        azimuth_configfile=parser.getfloat('default', 'azimuth')
        nModsx_configfile=parser.getint('default', 'nModsx')
        nModsy_configfile=parser.getint('default', 'nModsy')
        nRows_configfile=parser.getint('default', 'nRows')
        sensorsy_configfile=parser.getint('default', 'sensorsy')
        Start_Year_configfile=parser.get('default', 'Start_Year')
        Start_Month_configfile=parser.get('default', 'Start_Month')
        Start_Day_configfile=parser.get('default', 'Start_Day')
        Start_Hour_configfile=parser.get('default', 'Start_Hour')
        End_Year_configfile=parser.get('default', 'End_Year')
        End_Month_configfile=parser.get('default', 'End_Month')
        End_Day_configfile=parser.get('default', 'End_Day')
        End_Hour_configfile=parser.get('default', 'End_Hour')
      #  moduley_configfile=parser.get('default', 'moduley')
      #  modulex_configfile=parser.get('default', 'modulex')
        frontReflect_configfile=parser.get('default', 'frontReflect')
        backReflect_configfile=parser.get('default', 'backReflect')
        longitude_configfile=parser.get('default', 'longitude')
        latitude_configfile=parser.get('default', 'latitude')
        gcr_configfile=parser.get('default', 'gcr')
        utcoffset_configfile=parser.get('default', 'utcoffset')
        
        # Plot total qinc front and back for every row
      
        
        f = plt.Figure(figsize=(12, 3))
        ax1 = f.subplots(1)
        ax1.locator_params(tight=True, nbins=6)
        ax1.plot(P_bi_hourly)
        ax1.set_title('Bifacial output Power hourly')
        ax1.set_xlabel('Hour')
        ax1.set_ylabel('W')
        f.savefig("P_bi_hourly" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
        #plt.show()()
        #sns wird entfernt da die Plots in der GUI ansonsten nicht richtig angezeigt werden können außerhalb der Konsole
        ##plt.show()(sns)
        
        
        ####################################################
        # Monofacial performance Calculation
        
        # Set Energy to Zero       
        sum_energy_m = 0
        sum_power_m = 0
        
        # Loop to calculate the Monofacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front_mono = "row_" + str(i) + "_qabs_front"
            P_m_hourly = []
            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
            x = 0 #counting variable in loop to get current month from df_time_soiling
            y = 0
            #
            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                if temp == days_until_clean*24:
                    temp = 0
                else:
                    temp = temp +1

                if simulationDict["average_daily_soiling_rate"] == True:
                    soilrate = simulationDict["hourlySoilrate"]
                    
                    if simulationDict['simulationMode'] == 5:
                        row_qabs_front = 0
                    else:
                        row_qabs_front = df_report.loc[index,key_front_mono] * (1 - (soilrate[y]/100))
                        
                    # estimate module temperture with ambient temperature and NOCT temp
                    T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                    if np.isnan(T_Current):
                        T_Current = df.loc[index,'temperature']

                    if math.isnan(row_qabs_front):
                        row_qabs_front = 0 
                    
                    if  row_qabs_front > 0.0:
                  
                        V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
                        I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
                        P_m = FF_f0 * V_oc_f * I_sc_f
                    
                        #print("Power: " + str(P_bi))
                 
                        sum_energy_m += P_m # Sum up the energy of every row in every hour
                    else:
                        P_m = 0
                        
                    P_m_hourly.append(P_m)
                    y = y +1

                else:
                    soilrate = simulationDict['fixSoilrate']
                    
                    if simulationDict['simulationMode'] == 5:
                        row_qabs_front = 0
                    else:
                        row_qabs_front = df_report.loc[index,key_front_mono] * (1 - (soilrate*(temp)/(100*24)))
                        
                    # estimate module temperture with ambient temperature and NOCT temp
                    T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                    if np.isnan(T_Current):
                        T_Current = df.loc[index,'temperature']

                    if math.isnan(row_qabs_front):
                        row_qabs_front = 0 
                    
                    if  row_qabs_front > 0.0:
                  
                        V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
                        I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
                        P_m = FF_f0 * V_oc_f * I_sc_f
                    
                        #print("Power: " + str(P_bi))
                 
                        sum_energy_m += P_m # Sum up the energy of every row in every hour
                    else:
                        P_m = 0
                        
                    P_m_hourly.append(P_m)
                
                # Append P_m_hourly array to arrays
                P_m_hourly_arrays.append(P_m_hourly)

        P_m_hourly_average = []
        
        for i in tqdm(range(0, len(P_m_hourly_arrays[0]))):
            sum = 0
          
            for j in range(0, len(P_m_hourly_arrays)):
                sum += P_m_hourly_arrays[j][i]
                
            average_m = sum / float(len(P_m_hourly_arrays))
            
            P_m_hourly_average.append(average_m)
                 #else:
                    #print("Power: 0.0")
             
                    
        mismatch_array = Electrical_simulation.calculate_mismatch(P_m_hourly_average, P_mpp0)

        annual_power_per_module_m = (sum_energy_m/simulationDict['nRows']) #[W] annual monofacial output power per module
        '''print("Yearly monofacial output power per module: " + str(annual_power_per_module_m) + " W/module")
        print("Yearly monofacial output energy per module: " + str(annual_power_per_module_m/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
        print ("\n")'''
        
        annual_power_per_peak_m = (sum_energy_m/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual monofacial output power per module peak power
        '''print("Yearly monofacial output power per module peak power: " + str(annual_power_per_peak_m) + " W/Wp")
        print("Yearly monofacial output energy per module peak power: " + str(annual_power_per_peak_m) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        module_area = (simulationDict['moduley'] *simulationDict['nModsy']* simulationDict['modulex'])
        
        annual_power_per_area_m = (annual_power_per_module_m / module_area)    #[W/m^2] annual monofacial poutput power per module area
        '''print("Yearly monofacial output power per module area: " + str(annual_power_per_area_m) + " W/m^2")
        print("Yearly monofacial output energy per module area: " + str(annual_power_per_area_m/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        ####################################################
        
        # Bifacial Gain Calculation
        
        Bifacial_gain= (annual_power_per_peak_b - annual_power_per_peak_m) / annual_power_per_peak_m
        print("Bifacial Gain: " + str(Bifacial_gain*100) + " %")
        
                
        # Create dataframe with data
        p_bi_df = pd.DataFrame({"timestamps":df_report.index, "P_bi ": P_bi_hourly_average, "P_m ": P_m_hourly_average, "Mismatch":mismatch_array})
        p_bi_df.set_index("timestamps")
        p_bi_df.to_csv(Path(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv"))
        
        #Plot for Bifacial Power Output + Bifacial Gain
        GUI.Window.makePlotBifacialRadiance(resultsPath,Bifacial_gain)
#        GUI.Window.makePlotMismatch(resultsPath,checkbutton_state)
        
        return Bifacial_gain*100
    
    def calculate_mismatch(P_array, P_cell):
        
        mismatch=[]  
        m=0       
        
        if P_cell==0:
            print('ERROR: Please enter the Module MPP in GUI (P_mpp value is 0)')
            mismatch=float('nan')
            return mismatch
        
        else:
            for i in range(len(P_array)):  
            
                m= (1-(P_array[i])/P_cell)*100
                mismatch.append(m)
                
            return mismatch 

    
    def simulate_simpleBifacial(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath):
        """
        Applies a simplified version of the electrical simulation after PVSyst. Uses bifaciality factor to calculate rear efficiency and fill factors.
        Rear open-circuit voltage and short-circuit current are calculated using rear irradiance and temperature. 
        The rear output is then determined through the rear fill factor. Then the bifacial electrical output is calculated by adding front and rear output.
        Calculates bifacial gain through a seperate monofacial electrical simulation.

        Parameters
        ----------
        moduleDict: module Dictionary containing module data
        simulationDict: simulation Dictionary, which can be found in BifacialSimu_main.py
        df_reportVF: Viewfactor simulation report
        df_reportRT: Raytracing simulation report
        df_report: Final simulation report, containing VF and RT data
        resultsPath: output filepath
        df: helper DataFrame containing temperature for electrical simulation
        """
        
        
        # Build a final simulation report
        df_report = Electrical_simulation.build_simulationReport(df_reportVF, df_reportRT, simulationDict, resultsPath)
        
        ####################################################
        # Variables required for electrical simulation
        
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
        # Definition of simulation parameter if only front parameters are available
        # Procedure after PVSyst
        V_mpp_f0 = moduleDict['V_mpp_f']
            
        I_mpp_f0 = moduleDict['I_mpp_f']
                
        I_sc_f0 = moduleDict['I_sc_f']
        
        V_oc_f0 = moduleDict['V_oc_f']
        
        bi_factor = moduleDict['bi_factor']
        
        soilrate = simulationDict['fixSoilrate']
        days_until_clean = simulationDict['days_until_clean']
        
        #module = moduleParameter['module']
        #inverter = moduleParameter['inverter']
        
        P_mpp0 = moduleDict['P_mpp']
        V_mpp0 = V_mpp_f0
        
        T_koeff_P = moduleDict['T_koeff_P'] 
        T_koeff_I = moduleDict['T_koeff_I'] 
        T_koeff_V = moduleDict['T_koeff_V'] 
        T_amb = moduleDict['T_amb']
        
        q_stc_front = 1000  # [W/m^2] 
        q_stc_rear = 1000   # [W/m^2] 
        
        # Calculation of fill factor for STC conditions
        FF_f0 = (I_mpp_f0 * V_mpp_f0)/(I_sc_f0 * V_oc_f0)
        
        #n_back = (moduleDict['bi_factor']*moduleDict['n_front'])
        
        #FF_fr = (n_back*q_stc_rear*(simulationDict['moduley'])*(simulationDict['modulex']))/(I_sc_f0 * V_oc_f0)
                       
        dpi = 150 #Quality for plot export
        
        # Set Energy to Zero       
        sum_energy_b = 0
        sum_power_b = 0
        
        # Array to hold other arrays -> average after for loop
        P_bi_hourly_arrays = []
        
        df_report['timestamp'] = df_report.index
        df_report = df_report.reset_index()
        df_report['corrected_timestamp'] = pd.to_datetime(df_report['timestamp'])
        df_report['time'] = df_report['corrected_timestamp'].dt.strftime('%m_%d_%H')
        df_report = df_report.set_index('time')
        
        ###########################################################################################################################################################
        #soilingrate from theorical model
        city_name = simulationDict["city"]  # get the city, country name from 'Entry_weatherstation' 
        #print (str(city_name))
        #new_soilingrate = pd.read_csv(rootPath + '\Lib\input_soiling\soiling_data.csv', encoding ='latin-1' ) 
        df_city = pd.read_csv(rootPath + f'\city_data_soiling_accumulation\{city_name}.csv')
        #file_path = os.path.join(city_data_directory, f"{city_name}.csv")
        #df_city = pd.read_csv(file_path)
        # Convert the 'Date' column into date format for both DataFrames
        df_city['Date'] = pd.to_datetime(df_city['Date'], dayfirst=True)
        df_report['corrected_timestamp'] = pd.to_datetime(df_report['corrected_timestamp'], dayfirst=True)

        # Create an empty list to store the corresponding soilingrate values
        sr_value = []

        # Browse rows in DataFrame "df_report
        for index, row in df_report.iterrows():
            # Extract the date (day and month) of the current row from the "df_report" DataFrame
            date_df_report = row['corrected_timestamp'].replace(year=2023)  # Remplacer l'année par l'année appropriée
            
            # Filter the "City, Country" DataFrame to obtain rows with the same date (day and month)
            df_filtered = df_city[(df_city['Date'].dt.day == date_df_report.day) & (df_city['Date'].dt.month == date_df_report.month)]
            
            # Check whether rows have been found in the filtered DataFrame
            if not df_filtered.empty:
                # Retrieve the soilingrate value from the first corresponding line
                soilingrate_value = df_filtered.iloc[0]['soilingrate']
                
                # Add the soilingrate value to the "sr_value" list
                sr_value.append(soilingrate_value)
            else:
                # Add a default value (for example, 0) if no corresponding soilingrate value has been found
                sr_value.append(0)
        simulationDict["hourlySoilrate"] = sr_value
        #print('AAA', len(simulationDict["hourlySoilrate"]))
        #print('VBBB', len(sr_value))
        #print('XXXXXXX', len(df_report))
        #df_reportVF
        # Display the list containing the corresponding soilingrate values for each identical day and month
        #print(len(sr_value))
        #print(sr_value)
        ###########################################################################################################################################################
        
        if simulationDict['simulationMode'] == 3:
            df = df.reset_index()
            
            df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
            df = df.set_index('time')
            df['timestamp'] = df['corrected_timestamp'].dt.strftime('%m-%d %H:%M%')
            df['timestamp'] = pd.to_datetime(df['timestamp'])  
            #df['timestamp'] = df['timestamp'].dt.tz_localize(None)
            df = df.set_index('timestamp')
            
            dtStart = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
        
        
            dtEnd = datetime.datetime(simulationDict['endHour'][0], simulationDict['endHour'][1], simulationDict['endHour'][2], simulationDict['endHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
            mask = (df.index >= dtStart) & (df.index <= dtEnd) 
            df = df.loc[mask]
        
        df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
        df = df.set_index('time')
        print(df_report)

        # Loop to calculate the Bifacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front = "row_" + str(i) + "_qabs_front"
            key_back = "row_" + str(i) + "_qabs_back"
        
            P_bi_hourly = []
            
            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
            y = 0
            
            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                if temp == days_until_clean*24:
                    temp = 0
                else:
                    temp = temp +1

                if simulationDict["average_daily_soiling_rate"] == True:
                    soilrate = simulationDict["hourlySoilrate"]

                    if simulationDict['simulationMode'] == 1 or simulationDict['simulationMode'] == 2 or simulationDict['simulationMode'] == 3:
                        # calculate front row power output including the soiling rate determined in GUI                               
                        row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate[y]/100))
                        # calculate back row power output including the decreased soiling for backside of PV module                                 
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate[y]/(100*10.581)))

                    if simulationDict['simulationMode'] == 5:
                        row_qabs_front = 0
                    else:
                        row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate[y]/100))
#                        T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))

                    if simulationDict['simulationMode'] == 4:
                        row_qabs_back = 0
                    else:
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate[y]/(100*10.581)))
#                        T_Current = df.loc[index,'temperature'] + ((row_qabs_back/800)*(moduleDict['T_NOCT'] - 20))

                    # estimate module temperture with ambient temperature and NOCT temp
                    T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                    if np.isnan(T_Current):
                        T_Current = df.loc[index,'temperature']
                    
                    row_qabs_combined = row_qabs_front + (row_qabs_back*bi_factor)
                        
                        
                    # calculation of frontside power output
                    if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                        row_qabs_front = 0
                        P_bi = 0     

                    # calculation of backside power output
                    elif math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                        row_qabs_back = 0
                        P_bi = 0
                       
                    else:
                        V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_combined / q_stc_front))
                        I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_combined / q_stc_front)
                        P_bi = FF_f0 * V_oc_f * I_sc_f
                        

                    sum_energy_b += P_bi # Sum up the energy of every row in every hour

                    P_bi_hourly.append(P_bi)
                        
                else:
                    soilrate = soilrate = simulationDict['fixSoilrate']
                    
                    if simulationDict['simulationMode'] == 1 or simulationDict['simulationMode'] == 2 or simulationDict['simulationMode'] == 3:
                        # calculate front row power output including the soiling rate determined in GUI                               
                        row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate*(temp)/(100*24)))   
                        # calculate back row power output including the decreased soiling for backside of PV module                                 
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate*(temp)/(100*24*10.581)))
                        
                    if simulationDict['simulationMode'] == 5:
                        row_qabs_front = 0
                    else:
                        row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate*(temp)/(100*24)))
#                        T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                        
                    if simulationDict['simulationMode'] == 4:
                        row_qabs_back = 0
                    else:
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate*(temp)/(100*24*10.581)))
#                        T_Current = df.loc[index,'temperature'] + ((row_qabs_back/800)*(moduleDict['T_NOCT'] - 20))

                    # estimate module temperture with ambient temperature and NOCT temp
                    T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                    if np.isnan(T_Current):
                        T_Current = df.loc[index,'temperature']
                        
                    row_qabs_combined = row_qabs_front + (row_qabs_back*bi_factor)
                
                    # calculation of frontside power output
                    if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                        row_qabs_front = 0
                        P_bi = 0     

                    # calculation of backside power output
                    elif math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                        row_qabs_back = 0
                        P_bi = 0
               
                    else:
                        V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_combined / q_stc_front))
                        I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_combined / q_stc_front)
                        P_bi = FF_f0 * V_oc_f * I_sc_f
                

                    sum_energy_b += P_bi # Sum up the energy of every row in every hour

                    P_bi_hourly.append(P_bi)
                
            # Append P_bi_hourly array to arrays
            P_bi_hourly_arrays.append(P_bi_hourly)

            print(sum_energy_b)
            
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
        p_bi_df.to_csv(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
        
        
        annual_power_per_module_b = (sum_energy_b/simulationDict['nRows']) #[W] annual bifacial output power per module
        '''print("Yearly bifacial output power per module: " + str(annual_power_per_module_b) + " W/module")
        print("Yearly bifacial output energy per module: " + str(annual_power_per_module_b/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
        print ("\n")'''
        
        annual_power_per_peak_b = (sum_energy_b/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual bifacial output power per module peak power
        '''print("Yearly bifacial output power per module peak power: " + str(annual_power_per_peak_b) + " W/Wp")
        print("Yearly bifacial output energy per module peak power: " + str(annual_power_per_peak_b) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        module_area = (simulationDict['moduley'] * simulationDict['nModsy'] * simulationDict['modulex'])
        
        annual_power_per_area_b = (annual_power_per_module_b / module_area)    #[W/m^2] annual bifacial poutput power per module area
        '''print("Yearly bifacial output power per module area: " + str(annual_power_per_area_b) + " W/m^2")
        print("Yearly bifacial output energy per module area: " + str(annual_power_per_area_b/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        # Plot total qinc front and back for every row
        f = plt.Figure(figsize=(12, 3))
        ax1 = f.subplots(1)
        ax1.locator_params(tight=True, nbins=6)
        #f.plot(P_bi_hourly)
        ax1.set_title('Bifacial output Power hourly')
        ax1.set_xlabel('Hour')
        ax1.set_ylabel('W')
        f.savefig("P_bi_hourly" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
        #plt.show()()
        ##plt.show()(sns)
         
        ####################################################
        # Monofacial performance Calculation
        
        # Set Energy to Zero       
        sum_energy_m = 0
        sum_power_m = 0
        
        # Loop to calculate the Monofacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front_mono = "row_" + str(i) + "_qabs_front"
            
            P_m_hourly = []
            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
            y = 0 #counting variable in loop to get current month from df_time_soiling
            
            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                if temp == days_until_clean*24:
                    temp = 0
                else:
                    temp = temp +1

                if simulationDict["average_daily_soiling_rate"] == True:
                    soilrate = simulationDict["hourlySoilrate"]
                    
                    if simulationDict['simulationMode'] == 5:
                        row_qabs_front = 0
                    else:
                        row_qabs_front = df_report.loc[index,key_front_mono] * (1 - (soilrate[y]/100))
                        
                    # estimate module temperture with ambient temperature and NOCT temp
                    T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                    if np.isnan(T_Current):
                        T_Current = df.loc[index,'temperature']
                        
                    # calculation of frontside power output
                    if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                        row_qabs_front = 0
                        P_m = 0 
                            
                    else:
                        V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
                        I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
                        P_m = FF_f0 * V_oc_f * I_sc_f
                       
                    sum_energy_m += P_m # Sum up the energy of every row in every hour
                
                #
                else:
                    soilrate = simulationDict['fixSoilrate']
                    #SG
                    if simulationDict['simulationMode'] == 5:
                        row_qabs_front = 0
                    else:
                        row_qabs_front = df_report.loc[index,key_front_mono] * (1 - (soilrate*(temp)/(100*24)))
                        
                    # estimate module temperture with ambient temperature and NOCT temp
                    T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                    if np.isnan(T_Current):
                        T_Current = df.loc[index,'temperature']
                        
                    # calculation of frontside power output
                    if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                        row_qabs_front = 0
                        P_m = 0 
                    
                    else:
                        V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
                        I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
                        P_m = FF_f0 * V_oc_f * I_sc_f
               
                    sum_energy_m += P_m # Sum up the energy of every row in every hour

            #
        annual_power_per_module_m = (sum_energy_m/simulationDict['nRows']) #[W] annual monofacial output power per module
        '''print("Yearly monofacial output power per module: " + str(annual_power_per_module_m) + " W/module")
        print("Yearly monofacial output energy per module: " + str(annual_power_per_module_m/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
        print ("\n")'''
        
        annual_power_per_peak_m = (sum_energy_m/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual monofacial output power per module peak power
        '''print("Yearly monofacial output power per module peak power: " + str(annual_power_per_peak_m) + " W/Wp")
        print("Yearly monofacial output energy per module peak power: " + str(annual_power_per_peak_m) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        module_area = (simulationDict['moduley'] *simulationDict['nModsy']* simulationDict['modulex'])
        
        annual_power_per_area_m = (annual_power_per_module_m / module_area)    #[W/m^2] annual monofacial poutput power per module area
        '''print("Yearly monofacial output power per module area: " + str(annual_power_per_area_m) + " W/m^2")
        print("Yearly monofacial output energy per module area: " + str(annual_power_per_area_m/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        ####################################################
        
        # Bifacial Gain Calculation
        
        Bifacial_gain= (annual_power_per_peak_b - annual_power_per_peak_m) / annual_power_per_peak_m
        print("Bifacial Gain: " + str(Bifacial_gain*100) + " %")
        
        #Plot for Bifacial Power Output + Bifacial Gain
        GUI.Window.makePlotBifacialRadiance(resultsPath,Bifacial_gain)     
        
        return Bifacial_gain*100
        
        
    def simulate_doubleDiode(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath):
        """
        Applies the one diode model for bifacial electrical simulation. Needs module front and rear parameters to work correctly.
        Calculates bifacial gain through a seperate monofacial electrical simulation.

        Parameters
        ----------
        moduleDict: module Dictionary containing module data
        simulationDict: simulation Dictionary, which can be found in BifacialSimuu_main.py
        df_reportVF: Viewfactor simulation report
        df_reportRT: Raytracing simulation report
        df_report: Final simulation report, containing VF and RT data
        resultsPath: output filepath
        df: helper DataFrame containing temperature for electrical simulation
        """
        
        
        
        # Build a final simutlation report
        df_report = Electrical_simulation.build_simulationReport(df_reportVF, df_reportRT, simulationDict, resultsPath)
        
        ####################################################
        # Variables required for electrical simulation
        
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
        V_mpp_f0 = moduleDict['V_mpp_f']
        V_mpp_r0 = moduleDict['V_mpp_r']
        
        I_mpp_f0 = moduleDict['I_mpp_f']
        I_mpp_r0 = moduleDict['I_mpp_r']
        
        I_sc_r0 = moduleDict['I_sc_r']
        I_sc_f0 = moduleDict['I_sc_f']
        
        V_oc_r0 = moduleDict['V_oc_r']
        V_oc_f0 = moduleDict['V_oc_f']
        
        Ns = moduleDict['Ns']      #Number of cells in module
        soilrate = simulationDict['fixSoilrate'] #Michailow
        days_until_clean = simulationDict['days_until_clean']
        
        #module = moduleParameter['module']
        #inverter = moduleParameter['inverter']
        
        P_mpp0 = moduleDict['P_mpp']
        V_mpp0 = V_mpp_f0
        
        T_koeff_P = moduleDict['T_koeff_P'] 
        T_koeff_I = moduleDict['T_koeff_I'] 
        T_koeff_V = moduleDict['T_koeff_V'] 
        T_amb = moduleDict['T_amb']
                
        k = 1.3806503 * 10**(-23)       #Boltzmann constant [J/K]
        q_ec = 1.60217646 * 10**(-19)   #electron charge [C]
        
        q_stc_front = 1000  # [W/m^2] 
        q_stc_rear = 1000   # [W/m^2] 
        
        # Calculation of fill factor for STC conditions
        FF_f0 = (I_mpp_f0 * V_mpp_f0)/(I_sc_f0 * V_oc_f0) 
        FF_r0 = (I_mpp_r0 * V_mpp_r0)/(I_sc_r0 * V_oc_r0) 
        
        
        dpi = 150 #Quality for plot export
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
        P_m_hourly_arrays = []
        
        df_report['timestamp'] = df_report.index
        df_report = df_report.reset_index()
        df_report['corrected_timestamp'] = pd.to_datetime(df_report['timestamp'])
        df_report['time'] = df_report['corrected_timestamp'].dt.strftime('%m_%d_%H')
        df_report = df_report.set_index('time')
        
        
        
        
        if simulationDict['simulationMode'] == 3:
            df = df.reset_index()
            
            df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
            df = df.set_index('time')
            df['timestamp'] = df['corrected_timestamp'].dt.strftime('%m-%d %H:%M%')
            df['timestamp'] = pd.to_datetime(df['timestamp'])  
            #df['timestamp'] = df['timestamp'].dt.tz_localize(None)
            df = df.set_index('timestamp')
            
            dtStart = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
        
        
            dtEnd = datetime.datetime(simulationDict['endHour'][0], simulationDict['endHour'][1], simulationDict['endHour'][2], simulationDict['endHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
            mask = (df.index >= dtStart) & (df.index <= dtEnd) 
            df = df.loc[mask]
        
        df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
        df = df.set_index('time')

        #################################################################################
        #soilingrate from theorical model
        city_name = simulationDict["city"]  # get the city, country name from 'Entry_weatherstation' 
        #print (str(city_name))
        #new_soilingrate = pd.read_csv(rootPath + '\Lib\input_soiling\soiling_data.csv', encoding ='latin-1' ) 
        df_city = pd.read_csv(rootPath + f'\city_data_soiling_accumulation\{city_name}.csv')
        #file_path = os.path.join(city_data_directory, f"{city_name}.csv")
        #df_city = pd.read_csv(file_path)
        # Convert the 'Date' column into date format for both DataFrames
        df_city['Date'] = pd.to_datetime(df_city['Date'], dayfirst=True)
        df_report['corrected_timestamp'] = pd.to_datetime(df_report['corrected_timestamp'], dayfirst=True)

        # Create an empty list to store the corresponding soilingrate values
        sr_value = []

        # Browse rows in DataFrame "df_report
        for index, row in df_report.iterrows():
            # Extract the date (day and month) of the current row from the "df_report" DataFrame
            date_df_report = row['corrected_timestamp'].replace(year=2023)  # Remplacer l'année par l'année appropriée
            
            # Filter the "City, Country" DataFrame to obtain rows with the same date (day and month)
            df_filtered = df_city[(df_city['Date'].dt.day == date_df_report.day) & (df_city['Date'].dt.month == date_df_report.month)]
            
            # Check whether rows have been found in the filtered DataFrame
            if not df_filtered.empty:
                # Retrieve the soilingrate value from the first corresponding line
                soilingrate_value = df_filtered.iloc[0]['soilingrate']
                
                # Add the soilingrate value to the "sr_value" list
                sr_value.append(soilingrate_value)
            else:
                # Add a default value (for example, 0) if no corresponding soilingrate value has been found
                sr_value.append(0)
        simulationDict["hourlySoilrate"] = sr_value
        #print('AAA', len(simulationDict["hourlySoilrate"]))
        #print('VBBB', len(sr_value))
        #print('XXXXXXX', len(df_report))
        #df_reportVF
        # Display the list containing the corresponding soilingrate values for each identical day and month
        #print(len(sr_value))
        #print(sr_value)
        ############################################################################################################################################################
        
        #Diode ideality factors. a1 has to be 1 while a2 is flexible but it has to be above 1.2
        a1 = 1      
        a2 = 1.3
        
        #Tolerances for current and power in Mpp calculation algorythm
        tol_I = 0.001 
        tol_P = 0.002
        
        #Calculation of Parameters that do not change in the loop
        P_mpp_f0 = V_mpp_f0 * I_mpp_f0                      #P_mpp is calculated from Mpp Voltage and Current
        Vt = (Ns * k * (25+273.15)) / q_ec                  #Thermal voltage at STC                                     
        I_0_f0 = (I_sc_f0) / (np.exp((V_oc_f0) / (Vt))-1)   #Calculation of saturation current. It is assumed that its the same for both diodes

        #Starting values fpr Rs and Rp
        Rs_f0 = 0
        Rp_min = (V_mpp_f0 / (I_sc_f0 - I_mpp_f0)) - ((V_oc_f0 - V_mpp_f0) / I_mpp_f0)
        Rp_f0 = Rp_min
        
        #Starting parameters for Current, Voltage, and Power
        I = 0
        V = 0
        P = 0
        P1 = 0
        P_mpp_fs0 = 0
        
        #Definition of lists for the I-V P-V plots
        Vfplt = []
        Ifplt = []
        Pfplt = []
               
        #Rs and Rp calculation for the front side. They are calculated at STC. The algorythm tries to match the Mpp of the Module parameters
        #by adjusting Rs and calculating Rp based on Rs.
        for xf in range (1000000):
           
            
           #If the calculation takes too many iterations, an error message will show up.
           if xf == 999999:                     
                print ('Error: The calculation of the front resistances exeeded one million iterations. Please check your parameters.')
                     
           #'Calculation' of the photo current. At STC the I_sc is the photo current.        
           I_ph_f0 = I_sc_f0                                             
       
           #Newtons method to find the current that solves the equation f_I  
           f_I = I_ph_f0 - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt) + np.exp((V + I * Rs_f0) / (Vt * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
           f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt) * np.exp((V + I * Rs_f0) / Vt) - ((I_0_f0 * Rs_f0) / (Vt * a2)) * np.exp((V+ I * Rs_f0) / (Vt * a2)) - (Rs_f0 / Rp_f0) - 1
       
           I2 = I - (f_I/f_dI)
              
           #Check if the new value of I2 is close enough (in tolerance) to the old value I
           if I + tol_I >= I2 and I2 >= I - tol_I:
               P2 = V * I2          #If the current was calculated correctly the power will be calculated
               
               Vfplt.append(V)      #The values of current, voltage and power are added to their designated lists
               Ifplt.append(I2)
               Pfplt.append(P2)
               
               if P2 > P1:          #Check if the new power value is greater than the last. If yes it becomes the new reference power value.
                   P1 = P2
               
               else:
                   P_mpp_fs0 = P1   #If the power does not increase however, the Mpp of this P-V curve is found
                   
                   
                           
               if V >= V_oc_f0:     # When V reaches V_oc the P-V curve is complete and it has to be checked if Mpp converged with the Module parameters
               
                   #If the calculated Mpp is within the tolerance the script tells the user the Values of Rs and Rp aswell as the amount of iterations
                   #it took to calculate them                   
                   if P_mpp_f0 + tol_P >= P_mpp_fs0 and P_mpp_fs0 >= P_mpp_f0 - tol_P:
                       print ('Front resistance calculation completed in ',xf,' iterations.', 'Rs_f0 =', Rs_f0, 'Rp_f0 =', Rp_f0)
                       
                       
                       #The P-V and I-V curve is plotted with the values since the last Rs, Rp adjustment
                       f = plt.Figure(figsize=(6, 6))
                       ax1 = f.subplots(1)
                       ax1.locator_params(tight=True, nbins=6)
                       ax1.plot(Vfplt[-round(V_oc_f0 * 10):], Ifplt[-round(V_oc_f0 * 10):], color = "red")
                       ax1.set_title('P-V I-V Curve front side', fontsize=14)
                       ax1.set_xlabel('Voltage [V]', fontsize=14)
                       ax1.set_ylabel('Current [I]', fontsize=14, color = 'red')
                       ax2=ax1.twinx()
                       ax2.plot(Vfplt[-round(V_oc_f0 * 10):], Pfplt[-round(V_oc_f0 * 10):], color = "blue")
                       ax2.set_ylabel('Power [W]', fontsize=14, color = 'blue')
                       f.savefig("P-V_I-V_Curve_front" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
                       #plt.show()()
 
                       #Rs and Rp have been calculated so the script quits the loop 
                       break
                   
                   #If the calculated Mpp is not within tolerance, the reference power is reset and Rs gets increased by 10 mOhm 
                   else:
                       P1 = 0
                   
                       Rs_f0 = Rs_f0 + 0.01
                   
                       #Calculation of Rp with new Rs. For a better overview it is split into smaller calculations
                       r1 = V_mpp_f0 + I_mpp_f0 * Rs_f0
                       r2 = I_ph_f0
                       r3 = np.exp(r1/Vt)
                       r4 = np.exp(r1/(Vt*a2))
                       r5 = P_mpp_f0/V_mpp_f0
                       r6 = (r3 + r4 + 2)
                       r7 = r6 * I_0_f0

                       Rp_f0 = r1 / (r2 - r7 - r5)
                                     
                   V = -0.1     #V reached its max so it is set to -0.1 so in the first iteration we have I=0 and V=0
               I = 0
               V = V + 0.1
           else:
               I = I2           #If I2 was not close enough to I, I becomes I2 (newtons method)
        

        #After the calculation of Rs and Rp for the front side, the rear side is calculated in the same way, with values from the back side
        P_mpp_r0 = V_mpp_r0 * I_mpp_r0
        Vt = (Ns * k * (25+273.15)) / q_ec
        I_0_r0 = (I_sc_r0) / (np.exp((V_oc_r0) / (Vt))-1)   

        #Starting values fpr Rs and Rp
        Rs_r0 = 0
        Rp_min = (V_mpp_r0 / (I_sc_r0 - I_mpp_r0)) - ((V_oc_r0 - V_mpp_r0) / I_mpp_r0)
        Rp_r0 = Rp_min

        I = 0
        V = 0
        P = 0
        P1 = 0
        P_mpp_rs0 = 0
        
        Vrplt = []
        Irplt = []
        Prplt = []        
        
        #Rs and Rp calculation for the rear side. They are calculated at STC. The algorythm tries to match the Mpp of the Module parameters
        #by adjusting Rs and calculating Rp based on Rs.
        for xr in range (1000000):
       
           if xr == 999999:
                print ('Error: The calculation of the rear resistances exeeded one million iterations. Please check your parameters.')
        
           
           
                  
           #'Calculation' of the photo current. At STC the I_sc is the photo current.        
           I_ph_r0 = I_sc_r0                                             
       
           #Newtons method to find the current that solves the equation f_I  
           f_I = I_ph_r0 - I_0_r0 * (np.exp((V+ I * Rs_r0) / Vt) + np.exp((V + I * Rs_r0) / (Vt * a2)) - 2) - ((V + I * Rs_r0) / Rp_r0) - I
           f_dI = (-1) * ((I_0_r0 * Rs_r0) / Vt) * np.exp((V + I * Rs_r0) / Vt) - ((I_0_r0 * Rs_r0) / (Vt * a2)) * np.exp((V+ I * Rs_r0) / (Vt * a2)) - (Rs_r0 / Rp_r0) - 1
       
           I2 = I - (f_I/f_dI)
              
       
           if I + tol_I >= I2 and I2 >= I - tol_I:
               P2 = V * I2
               Vrplt.append(V)
               Irplt.append(I2)
               Prplt.append(P2)
               
               if P2 > P1:
                   P1 = P2
               
               else:
                   P_mpp_rs0 = P1              
                          
               if V >= V_oc_r0:
                   if P_mpp_r0 + tol_P >= P_mpp_rs0 and P_mpp_rs0 >= P_mpp_r0 - tol_P:
                       print ('Rear resistance calculation completed in ',xr,' iterations.', 'Rs_r0 =', Rs_r0, 'Rp_r0 =', Rp_r0)
                       
                       f, (ax1) = plt.subplots(1, figsize=(6, 6))
                       ax1.locator_params(tight=True, nbins=6)
                       ax1.plot(Vfplt[-round(V_oc_r0 * 10):], Ifplt[-round(V_oc_r0 * 10):], color = "red")
                       ax1.set_title('P-V I-V Curve back side', fontsize=14)
                       ax1.set_xlabel('Voltage [V]', fontsize=14)
                       ax1.set_ylabel('Current [I]', fontsize=14, color = 'red')
                       ax2=ax1.twinx()
                       ax2.plot(Vrplt[-round(V_oc_r0 * 10):], Prplt[-round(V_oc_r0 * 10):], color = "blue")
                       ax2.set_ylabel('Power [W]', fontsize=14, color = 'blue')
                       f.savefig("P-V_I-V_Curve_back" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
                       #plt.show()()                       
                       
                       
                       break
                   else:
                       P1 = 0
                   
                       Rs_r0 = Rs_r0 + 0.01
                   
                       r1 = V_mpp_r0 + I_mpp_r0 * Rs_r0
                       r2 = I_ph_r0
                       r3 = np.exp(r1/Vt)
                       r4 = np.exp(r1/(Vt*a2))
                       r5 = P_mpp_r0/V_mpp_r0
                       r6 = (r3 + r4 + 2)
                       r7 = r6 * I_0_r0

                       Rp_r0 = r1 / (r2 - r7 - r5)
                                     
                   V = -0.1
               I = 0
               V = V + 0.1
           else:
               I = I2        
        

        
        
# =============================================================================
#         defining the input for the Albedo
# =============================================================================
     
        def getAlbedoJSONlist():
            """ Insert Albedo name from Albedo.json from following ressource: User’s Guide for Albedo Data Sets; von Bill Marion
        
        # Loop to calculate the Bifacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front = "row_" + str(i) + "_qabs_front"
            key_back = "row_" + str(i) + "_qabs_back"
            
            P_m_hourly = []
            P_bi_hourly = []
            
            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
            y = 0
            
            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                if temp == days_until_clean*24:
                    temp = 0
                else:
                    temp = temp +1

                if simulationDict["average_daily_soiling_rate"] == True:
                    soilrate = simulationDict["hourlySoilrate"]
                    
                    if simulationDict['simulationMode'] == 1 or simulationDict['simulationMode'] == 2 or simulationDict['simulationMode'] == 3:
                        # calculate front row power output including the soiling rate determined in GUI                               
                        row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate[y]/100))
                        # calculate back row power output including the decreased soiling for backside of PV module                                 
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate[y]/(100*10.581)))

                    if simulationDict['simulationMode'] == 5:
                        row_qabs_front = 0
                    else:
                        row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate[y]/100))
#                        T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))

                    if simulationDict['simulationMode'] == 4:
                        row_qabs_back = 0
                    else:
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate[y]/(100*10.581)))
#                        T_Current = df.loc[index,'temperature'] + ((row_qabs_back/800)*(moduleDict['T_NOCT'] - 20))

                    # estimate module temperture with ambient temperature and NOCT temp
                    T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                    if np.isnan(T_Current):
                        T_Current = df.loc[index,'temperature']
                        
                    #print("front: " + str(row_qabs_front))
                    #print("back: " + str(row_qabs_back))
                    if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                        row_qabs_front = 0
                            
                    if math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                        row_qabs_back = 0
                        
                    if row_qabs_back + row_qabs_front > 0.0:
                            
                        #Now that Rs and Rp are calculated for both sides of the module, the power calculation starts.
                        #Values are now adjusted for temperature and later also irradiation
                            
                        I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb))     
                        I_sc_r = I_sc_r0 * (1 + T_koeff_I * (T_Current - T_amb))
                            
                        V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb))
                        V_oc_r = V_oc_r0 * (1 + T_koeff_V * (T_Current - T_amb))
                            
                        #setting starting parameters for the loop
                        I = 0
                        V = 0
                        P = 0
                        P1 = 0
                        P_mpp_sf = 0
                            
                            
                        #Modified version of the Rs, Rp calculation loop. Since Rs and Rp are now given, the loop needs only a fraction of iterations
                        #to calculate the power from a given irradiance and temperature
                        #The way this works is that the algorythm searches for the Mpp of the module with the given irradiance and temperature
                        #Just like a real PV system would do
                        #It 'draws' the P-V curve and finds the Mpp which is then the power output of the module
                        for yf in range (100000):
                            
                            if row_qabs_front == 0:
                                P_m = 0
                                P_mpp_sf = 0
                                break
                                
                            #Calculation of the photo current + correction for irrandiance and temperature
                            Vt_f = (Ns * k * (T_Current + 273.15)) / q_ec

                            #Calculation of the saturation current
                            I_0_f0 = (I_sc_f) / (np.exp((V_oc_f) / (Vt_f))-1)

                            #adjustment ot the photo current for irradiation
                            I_ph_f0 = I_sc_f                                             
                            I_ph_f = I_ph_f0 * (row_qabs_front / q_stc_front) 
                      
                            #newthons method to find the matching current for a given voltage
                            f_I = I_ph_f - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt_f) + np.exp((V + I * Rs_f0) / (Vt_f * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
                            f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt_f) * np.exp((V + I * Rs_f0) / Vt_f) - ((I_0_f0 * Rs_f0) / (Vt_f * a2)) * np.exp((V+ I * Rs_f0) / (Vt_f * a2)) - (Rs_f0 / Rp_f0) - 1
               
                            I2 = I - (f_I/f_dI)
                            
                            if I + tol_I >= I2 and I2 >= I - tol_I:         #Once I is found, the Power check starts just like in xf loop
                                P2 = V * I2

                                if P2 > P1:                 #Check if the new power is higher than the last
                                    P1 = P2                 #If this is true, it becomes the new reference value
                       
                                else:
                                    P_mpp_sf = P1           #The highest calculated power gets added to P_mpp_sf
                                        
                                if V >= V_oc_f:             # If V reached V_oc, the P-V curve is complete and the Mpp can be searched
                                    P_f = P_mpp_sf          #P_mpp_sf is the calculated Mpp for the Module for the given irradiance and and temperature
                                    P_m = P_f
                                    sum_energy_m += P_m     #The value gets added to a list for Bifacial gain calculation
                                    yf = 0                  #Iterations get reset after successful Mpp calculation
                                    break                   #The Mpp was found, the script quits the loop
                                    
                                I = 0                       #Since there is only one P-V curve to calculate, V does not have to be reset
                                V = V + 0.1
                            else:
                                I = I2
                                
                                    
                            ##################################
                            ###Same procedure for rear side###
                            ##################################
                        I = 0
                        V = 0
                        P = 0
                        P1 = 0
                            
                            
                            
                        for yr in range (100000):
                                
                            if row_qabs_front == 0:
                                P_mpp_sr = 0
                                break
                          
                            #Calculation of the photo current + correction for irrandiance and temperature
                            Vt_r = (Ns * k * (T_Current + 273.15)) / q_ec
         
                            I_0_r0 = (I_sc_r) / (np.exp((V_oc_r) / (Vt_r))-1)
               
                            I_ph_r0 = I_sc_r                                             
                            I_ph_r = I_ph_r0 * (row_qabs_back / q_stc_rear) 
                      
                            f_I = I_ph_r - I_0_r0 * (np.exp((V+ I * Rs_r0) / Vt_r) + np.exp((V + I * Rs_r0) / (Vt_r * a2)) - 2) - ((V + I * Rs_r0) / Rp_r0) - I
                            f_dI = (-1) * ((I_0_r0 * Rs_r0) / Vt_r) * np.exp((V + I * Rs_r0) / Vt_r) - ((I_0_r0 * Rs_r0) / (Vt_r * a2)) * np.exp((V+ I * Rs_r0) / (Vt_r * a2)) - (Rs_r0 / Rp_r0) - 1
               
                            I2 = I - (f_I/f_dI)
                            
                            if I + tol_I >= I2 and I2 >= I - tol_I:
                                P2 = V * I2

                                if P2 > P1:
                                    P1 = P2
                       
                                else:
                                    P_mpp_sr = P1
                                  
                                if V >= V_oc_r:
                                    P_r = P_mpp_sr 
                                    yr = 0
                                    break
                                  
                       
                                I = 0
                                V = V + 0.1
                                
                            else:
                                I = I2                    
                            
                        
                        P_bi = P_mpp_sf + P_mpp_sr
                        #print("Power: " + str(P_bi))
                    
                        sum_energy_b += P_bi # Sum up the energy of every row in every hour
                    
                    else:
                        P_m=0
                        P_bi=0
                        
                    P_m_hourly.append(P_m)
                    P_bi_hourly.append(P_bi)
                #
                else:
                    soilrate = simulationDict['fixSoilrate']
                    if simulationDict['simulationMode'] == 1 or simulationDict['simulationMode'] == 2 or simulationDict['simulationMode'] == 3:
                        # calculate front row power output including the soiling rate determined in GUI                               
                        row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate*(temp)/(100*24)))   
                        # calculate back row power output including the decreased soiling for backside of PV module                                 
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate*(temp)/(100*24*10.581)))
                        
                    if simulationDict['simulationMode'] == 5:
                        row_qabs_front = 0
                    else:
                        row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate*(temp)/(100*24)))
#                        T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                        
                    if simulationDict['simulationMode'] == 4:
                        row_qabs_back = 0
                    else:
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate*(temp)/(100*24*10.581)))
#                        T_Current = df.loc[index,'temperature'] + ((row_qabs_back/800)*(moduleDict['T_NOCT'] - 20))

                    # estimate module temperture with ambient temperature and NOCT temp
                    T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                    if np.isnan(T_Current):
                        T_Current = df.loc[index,'temperature']

                    #print("front: " + str(row_qabs_front))
                    #print("back: " + str(row_qabs_back))
                    if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                        row_qabs_front = 0
                    
                    if math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                        row_qabs_back = 0

                
                    if row_qabs_back + row_qabs_front > 0.0:
                    
                    #Now that Rs and Rp are calculated for both sides of the module, the power calculation starts.
                    #Values are now adjusted for temperature and later also irradiation
                    
                        I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb))     
                        I_sc_r = I_sc_r0 * (1 + T_koeff_I * (T_Current - T_amb))
                    
                        V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb))
                        V_oc_r = V_oc_r0 * (1 + T_koeff_V * (T_Current - T_amb))
                    
                        #setting starting parameters for the loop
                        I = 0
                        V = 0
                        P = 0
                        P1 = 0
                        P_mpp_sf = 0
                    
                    
                    #Modified version of the Rs, Rp calculation loop. Since Rs and Rp are now given, the loop needs only a fraction of iterations
                    #to calculate the power from a given irradiance and temperature
                    #The way this works is that the algorythm searches for the Mpp of the module with the given irradiance and temperature
                    #Just like a real PV system would do
                    #It 'draws' the P-V curve and finds the Mpp which is then the power output of the module
                        for yf in range (100000):
                        
                            if row_qabs_front == 0:
                                P_m = 0
                                P_mpp_sf = 0
                                break
                        
                            #Calculation of the photo current + correction for irrandiance and temperature
                            Vt_f = (Ns * k * (T_Current + 273.15)) / q_ec

                            #Calculation of the saturation current
                            I_0_f0 = (I_sc_f) / (np.exp((V_oc_f) / (Vt_f))-1)

                            #adjustment ot the photo current for irradiation
                            I_ph_f0 = I_sc_f                                             
                            I_ph_f = I_ph_f0 * (row_qabs_front / q_stc_front) 
              
                            #newthons method to find the matching current for a given voltage
                            f_I = I_ph_f - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt_f) + np.exp((V + I * Rs_f0) / (Vt_f * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
                            f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt_f) * np.exp((V + I * Rs_f0) / Vt_f) - ((I_0_f0 * Rs_f0) / (Vt_f * a2)) * np.exp((V+ I * Rs_f0) / (Vt_f * a2)) - (Rs_f0 / Rp_f0) - 1
       
                            I2 = I - (f_I/f_dI)
              
       
                            if I + tol_I >= I2 and I2 >= I - tol_I:         #Once I is found, the Power check starts just like in xf loop
                                P2 = V * I2

                                if P2 > P1:                 #Check if the new power is higher than the last
                                    P1 = P2                 #If this is true, it becomes the new reference value
               
                                else:
                                    P_mpp_sf = P1           #The highest calculated power gets added to P_mpp_sf
                                
                                if V >= V_oc_f:             # If V reached V_oc, the P-V curve is complete and the Mpp can be searched
                                    P_f = P_mpp_sf          #P_mpp_sf is the calculated Mpp for the Module for the given irradiance and and temperature
                                    P_m = P_f
                                    sum_energy_m += P_m     #The value gets added to a list for Bifacial gain calculation
                                    yf = 0                  #Iterations get reset after successful Mpp calculation
                                    break                   #The Mpp was found, the script quits the loop
                          
               
                                I = 0                       #Since there is only one P-V curve to calculate, V does not have to be reset
                                V = V + 0.1
                            else:
                                I = I2
                        
                            
                    ##################################
                    ###Same procedure for rear side###
                    ##################################
                        I = 0
                        V = 0
                        P = 0
                        P1 = 0
                    
                    
                    
                        for yr in range (100000):
                        
                            if row_qabs_front == 0:
                                P_mpp_sr = 0
                                break
                  
                            #Calculation of the photo current + correction for irrandiance and temperature
                            Vt_r = (Ns * k * (T_Current + 273.15)) / q_ec
 
                            I_0_r0 = (I_sc_r) / (np.exp((V_oc_r) / (Vt_r))-1)
       
                            I_ph_r0 = I_sc_r                                             
                            I_ph_r = I_ph_r0 * (row_qabs_back / q_stc_rear) 
              
                            f_I = I_ph_r - I_0_r0 * (np.exp((V+ I * Rs_r0) / Vt_r) + np.exp((V + I * Rs_r0) / (Vt_r * a2)) - 2) - ((V + I * Rs_r0) / Rp_r0) - I
                            f_dI = (-1) * ((I_0_r0 * Rs_r0) / Vt_r) * np.exp((V + I * Rs_r0) / Vt_r) - ((I_0_r0 * Rs_r0) / (Vt_r * a2)) * np.exp((V+ I * Rs_r0) / (Vt_r * a2)) - (Rs_r0 / Rp_r0) - 1
       
                            I2 = I - (f_I/f_dI)
              
       
                            if I + tol_I >= I2 and I2 >= I - tol_I:
                                P2 = V * I2

                                if P2 > P1:
                                    P1 = P2
               
                                else:
                                    P_mpp_sr = P1
                          
                                if V >= V_oc_r:
                                    P_r = P_mpp_sr 
                                    yr = 0
                                    break
                          
               
                                I = 0
                                V = V + 0.1
                            else:
                                I = I2                    
                    
                
                        P_bi = P_mpp_sf + P_mpp_sr
                        #print("Power: " + str(P_bi))
            
                        sum_energy_b += P_bi # Sum up the energy of every row in every hour
            
                    else:
                        P_m=0
                        P_bi=0
                
                P_m_hourly.append(P_m)
                P_bi_hourly.append(P_bi)
            
                # Append P_bi_hourly array to arrays
            P_m_hourly_arrays.append(P_m_hourly)
            P_bi_hourly_arrays.append(P_bi_hourly)

        P_bi_hourly_average = []
        
        for i in tqdm(range(0, len(P_bi_hourly_arrays[0]))):
            sum = 0
          
            for j in range(0, len(P_bi_hourly_arrays)):
                sum += P_bi_hourly_arrays[j][i]
                
            average = sum / float(len(P_bi_hourly_arrays))
            
            P_bi_hourly_average.append(average)
            
       
        
        # The time gets implemented in the GUI
    # p_bi_df.to_csv(resultsPath + "simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
        
        
        annual_power_per_module_b = (sum_energy_b/simulationDict['nRows']) #[W] annual bifacial output power per module
        '''print("Yearly bifacial output power per module: " + str(annual_power_per_module_b) + " W/module")
        print("Yearly bifacial output energy per module: " + str(annual_power_per_module_b/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
        print ("\n")'''
        
        annual_power_per_peak_b = (sum_energy_b/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual bifacial output power per module peak power
        '''print("Yearly bifacial output power per module peak power: " + str(annual_power_per_peak_b) + " W/Wp")
        print("Yearly bifacial output energy per module peak power: " + str(annual_power_per_peak_b) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        module_area = (simulationDict['moduley'] *simulationDict['nModsy'] *simulationDict['modulex'])
        
        annual_power_per_area_b = (annual_power_per_module_b / module_area)    #[W/m^2] annual bifacial poutput power per module area
        '''print("Yearly bifacial output power per module area: " + str(annual_power_per_area_b) + " W/m^2")
        print("Yearly bifacial output energy per module area: " + str(annual_power_per_area_b/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        # Plot total qinc front and back for every row
      
        
        f = plt.Figure(figsize=(12, 3))
        ax1 = f.subplots(1)
        ax1.locator_params(tight=True, nbins=6)
        f.plot(P_bi_hourly)
        ax1.set_title('Bifacial output Power hourly')
        ax1.set_xlabel('Hour')
        ax1.set_ylabel('W')
        f.savefig("P_bi_hourly" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
        #plt.show()()
        ##plt.show()(sns)
        
        
        ####################################################
        # Monofacial performance Calculation
        
      # Set Energy to Zero       
#        sum_energy_m = 0
#        sum_power_m = 0
        
        # Loop to calculate the Monofacial Output power for every row in every hour
#        for i in tqdm(range(0, simulationDict['nRows'])):
            
#            key_front_mono = "row_" + str(i) + "_qabs_front"
#            P_m_hourly = []
#            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
#            y = 0 index for hourly soiling rate value
            
#            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0
#                if temp == days_until_clean*24:
#                    temp = 0
#                else:
#                    temp = temp +1

#                if simulationDict["average_daily_soiling_rate"] == True:
#                    soilrate = simulationDict["hourlySoilrate"]
#                    if simulationDict['simulationMode'] == 5:
#                        row_qabs_front = 0
#                    else:
#                        row_qabs_front = df_report.loc[index,key_front_mono] * (1 - (soilrate[y]/100))
                        
                    # estimate module temperture with ambient temperature and NOCT temp
#                    T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
#                    if np.isnan(T_Current):
#                        T_Current = df.loc[index,'temperature']

#                    if math.isnan(row_qabs_front):
#                        row_qabs_front = 0 
                        
#                    if  row_qabs_front > 0.0:
                      
#                        V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
#                        I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
#                        P_m = FF_f0 * V_oc_f * I_sc_f
                        
                        #print("Power: " + str(P_bi))
                     
#                        sum_energy_m += P_m # Sum up the energy of every row in every hour
#                    else:
#                        P_m = 0
                        
#                    P_m_hourly.append(P_m)
                    
#                else:
#                    soilrate = simulationDict['fixSoilrate']
#                    if simulationDict['simulationMode'] == 5:
#                        row_qabs_front = 0
#                    else:
#                        row_qabs_front = df_report.loc[index,key_front_mono] * (1 - (soilrate*(temp)/(100*24)))
                        
                    # estimate module temperture with ambient temperature and NOCT temp
#                    T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
#                    if np.isnan(T_Current):
#                        T_Current = df.loc[index,'temperature']

#                    if math.isnan(row_qabs_front):
#                        row_qabs_front = 0 
                
#                    if  row_qabs_front > 0.0:
              
#                        V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
#                        I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
#                        P_m = FF_f0 * V_oc_f * I_sc_f
                
                        #print("Power: " + str(P_bi))
             
#                        sum_energy_m += P_m # Sum up the energy of every row in every hour
#                    else:
#                        P_m = 0
                    
#                    P_m_hourly.append(P_m)
            
                # Append P_m_hourly array to arrays
#                P_m_hourly_arrays.append(P_m_hourly)
        
        P_m_hourly_average = []
        
        for i in tqdm(range(0, len(P_m_hourly_arrays[0]))):
            sum = 0
          
            for j in range(0, len(P_m_hourly_arrays)):
                sum += P_m_hourly_arrays[j][i]
                
            average_m = sum / float(len(P_m_hourly_arrays))
            
            P_m_hourly_average.append(average_m)
                 #else:
                    #print("Power: 0.0")
        
        annual_power_per_module_m = (sum_energy_m/simulationDict['nRows']) #[W] annual monofacial output power per module
        '''print("Yearly monofacial output power per module: " + str(annual_power_per_module_m) + " W/module")
        print("Yearly monofacial output energy per module: " + str(annual_power_per_module_m/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
        print ("\n")'''
        
        annual_power_per_peak_m = (sum_energy_m/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual monofacial output power per module peak power
        '''print("Yearly monofacial output power per module peak power: " + str(annual_power_per_peak_m) + " W/Wp")
        print("Yearly monofacial output energy per module peak power: " + str(annual_power_per_peak_m) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        module_area = (simulationDict['moduley'] *simulationDict['nModsy']* simulationDict['modulex'])
        
        annual_power_per_area_m = (annual_power_per_module_m / module_area)    #[W/m^2] annual monofacial poutput power per module area
        '''print("Yearly monofacial output power per module area: " + str(annual_power_per_area_m) + " W/m^2")
        print("Yearly monofacial output energy per module area: " + str(annual_power_per_area_m/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        ####################################################
        
        # Bifacial Gain Calculation
        
        Bifacial_gain= (annual_power_per_peak_b - annual_power_per_peak_m) / annual_power_per_peak_m
        print("Bifacial Gain: " + str(Bifacial_gain*100) + " %")
        
                
        # Create dataframe with data
        p_bi_df = pd.DataFrame({"timestamps":df_report.index, "P_bi ": P_bi_hourly_average, "P_m ": P_m_hourly_average})
        p_bi_df.set_index("timestamps")
        p_bi_df.to_csv(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
        #p_bi_df.to_csv(resultsPath + "electrical_simulation.csv")
        
        #Plot for Bifacial Power Output + Bifacial Gain
        GUI.Window.makePlotBifacialRadiance(resultsPath,Bifacial_gain)   
    
        return Bifacial_gain*100

    def simulate_doubleDiodeBi(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath):
        """
        Applies the one diode model for bifacial electrical simulation. Needs module front and rear parameters to work correctly.
        Calculates bifacial gain through a seperate monofacial electrical simulation.

        Parameters
        ----------
        moduleDict: module Dictionary containing module data
        simulationDict: simulation Dictionary, which can be found in BifacialSimuu_main.py
        df_reportVF: Viewfactor simulation report
        df_reportRT: Raytracing simulation report
        df_report: Final simulation report, containing VF and RT data
        resultsPath: output filepath
        df: helper DataFrame containing temperature for electrical simulation
        """
        
        
        
        # Build a final simutlation report
        df_report = Electrical_simulation.build_simulationReport(df_reportVF, df_reportRT, simulationDict, resultsPath)
        
        ####################################################
        # Variables required for electrical simulation
        
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
        V_mpp_f0 = moduleDict['V_mpp_f']
        V_mpp_r0 = moduleDict['V_mpp_r']
        
        I_mpp_f0 = moduleDict['I_mpp_f']
        I_mpp_r0 = moduleDict['I_mpp_r']
        
        I_sc_r0 = moduleDict['I_sc_r']
        I_sc_f0 = moduleDict['I_sc_f']
        
        V_oc_r0 = moduleDict['V_oc_r']
        V_oc_f0 = moduleDict['V_oc_f']
        
        #module = moduleParameter['module']
        #inverter = moduleParameter['inverter']
        
        P_mpp0 = moduleDict['P_mpp']
        V_mpp0 = V_mpp_f0
        
        T_koeff_P = moduleDict['T_koeff_P'] 
        T_koeff_I = moduleDict['T_koeff_I'] 
        T_koeff_V = moduleDict['T_koeff_V'] 
        T_amb = moduleDict['T_amb']
        
        # Note for later!:
        # moduleDict['Ns'] is not defined in moduleDict! (This can gave an error) 
        Ns = moduleDict['Ns']      #Number of cells in module
        
        soilrate = simulationDict['fixSoilrate'] #Michailow
        days_until_clean = simulationDict['days_until_clean']
        
        k = 1.3806503 * 10**(-23)       #Boltzmann constant [J/K]
        q_ec = 1.60217646 * 10**(-19)   #electron charge [C]
        
        q_stc_front = 1000  # [W/m^2] 
        q_stc_rear = 1000   # [W/m^2] 
        
        # Calculation of fill factor for STC conditions
        FF_f0 = (I_mpp_f0 * V_mpp_f0)/(I_sc_f0 * V_oc_f0) 
        FF_r0 = (I_mpp_r0 * V_mpp_r0)/(I_sc_r0 * V_oc_r0) 
        
        
        dpi = 150 #Quality for plot export
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
        P_m_hourly_arrays = []
        
        df_report['timestamp'] = df_report.index
        df_report = df_report.reset_index()
        df_report['corrected_timestamp'] = pd.to_datetime(df_report['timestamp'])
        df_report['time'] = df_report['corrected_timestamp'].dt.strftime('%m_%d_%H')
        df_report = df_report.set_index('time')
        
        
        
        
        if simulationDict['simulationMode'] == 3:
            df = df.reset_index()
            
            df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
            df = df.set_index('time')
            df['timestamp'] = df['corrected_timestamp'].dt.strftime('%m-%d %H:%M%')
            df['timestamp'] = pd.to_datetime(df['timestamp'])  
            #df['timestamp'] = df['timestamp'].dt.tz_localize(None)
            df = df.set_index('timestamp')
            
            dtStart = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
        
        
            dtEnd = datetime.datetime(simulationDict['endHour'][0], simulationDict['endHour'][1], simulationDict['endHour'][2], simulationDict['endHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
            mask = (df.index >= dtStart) & (df.index <= dtEnd) 
            df = df.loc[mask]
        
        df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
        df = df.set_index('time')
        
        #################################################################################
        #soilingrate from theorical model
        city_name = simulationDict["city"]  # get the city, country name from 'Entry_weatherstation' 
        #print (str(city_name))
        #new_soilingrate = pd.read_csv(rootPath + '\Lib\input_soiling\soiling_data.csv', encoding ='latin-1' ) 
        df_city = pd.read_csv(rootPath + f'\city_data_soiling_accumulation\{city_name}.csv')
        #file_path = os.path.join(city_data_directory, f"{city_name}.csv")
        #df_city = pd.read_csv(file_path)
        # Convert the 'Date' column into date format for both DataFrames
        df_city['Date'] = pd.to_datetime(df_city['Date'], dayfirst=True)
        df_report['corrected_timestamp'] = pd.to_datetime(df_report['corrected_timestamp'], dayfirst=True)

        # Create an empty list to store the corresponding soilingrate values
        sr_value = []

        # Browse rows in DataFrame "df_report
        for index, row in df_report.iterrows():
            # Extract the date (day and month) of the current row from the "df_report" DataFrame
            date_df_report = row['corrected_timestamp'].replace(year=2023)  # Remplacer l'année par l'année appropriée
           
            # Filter the "City, Country" DataFrame to obtain rows with the same date (day and month)
            df_filtered = df_city[(df_city['Date'].dt.day == date_df_report.day) & (df_city['Date'].dt.month == date_df_report.month)]
           
            # Check whether rows have been found in the filtered DataFrame
            if not df_filtered.empty:
                # Retrieve the soilingrate value from the first corresponding line
                soilingrate_value = df_filtered.iloc[0]['soilingrate']
               
               # Add the soilingrate value to the "sr_value" list
                sr_value.append(soilingrate_value)
            else:
                # Add a default value (for example, 0) if no corresponding soilingrate value has been found
                sr_value.append(0)
        simulationDict["hourlySoilrate"] = sr_value
        #print('AAA', len(simulationDict["hourlySoilrate"]))
        #print('VBBB', len(sr_value))
        #print('XXXXXXX', len(df_report))
        #df_reportVF
        # Display the list containing the corresponding soilingrate values for each identical day and month
        #print(len(sr_value))
        #print(sr_value)
        ############################################################################################################################################################
       
       
        #Diode ideality factors. a1 has to be 1 while a2 is flexible but it has to be above 1.2
        a1 = 1      
        a2 = 1.3
        
        #Tolerances for current and power in Mpp calculation algorythm
        tol_I = 0.001 
        tol_P = 0.002
        
        #Calculation of Parameters that do not change in the loop
        P_mpp_f0 = V_mpp_f0 * I_mpp_f0                      #P_mpp is calculated from Mpp Voltage and Current
        Vt = (Ns * k * (25+273.15)) / q_ec                  #Thermal voltage at STC                                     
        I_0_f0 = (I_sc_f0) / (np.exp((V_oc_f0) / (Vt))-1)   #Calculation of saturation current. It is assumed that its the same for both diodes

        #Starting values fpr Rs and Rp
        Rs_f0 = 0
        Rp_min = (V_mpp_f0 / (I_sc_f0 - I_mpp_f0)) - ((V_oc_f0 - V_mpp_f0) / I_mpp_f0)
        Rp_f0 = Rp_min
        
        #Starting parameters for Current, Voltage, and Power
        I = 0
        V = 0
        P = 0
        P1 = 0
        P_mpp_fs0 = 0
        
        #Definition of lists for the I-V P-V plots
        Vfplt = []
        Ifplt = []
        Pfplt = []
               
        #Rs and Rp calculation for the front side. They are calculated at STC. The algorythm tries to match the Mpp of the Module parameters
        #by adjusting Rs and calculating Rp based on Rs.
        for xf in range (1000000):
           
            
           #If the calculation takes too many iterations, an error message will show up.
           if xf == 999999:                     
                print ('Error: The calculation of the front resistances exeeded one million iterations. Please check your parameters.')
                     
           #'Calculation' of the photo current. At STC the I_sc is the photo current.        
           I_ph_f0 = I_sc_f0                                             
       
           #Newtons method to find the current that solves the equation f_I  
           f_I = I_ph_f0 - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt) + np.exp((V + I * Rs_f0) / (Vt * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
           f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt) * np.exp((V + I * Rs_f0) / Vt) - ((I_0_f0 * Rs_f0) / (Vt * a2)) * np.exp((V+ I * Rs_f0) / (Vt * a2)) - (Rs_f0 / Rp_f0) - 1
       
           I2 = I - (f_I/f_dI)
              
           #Check if the new value of I2 is close enough (in tolerance) to the old value I
           if I + tol_I >= I2 and I2 >= I - tol_I:
               P2 = V * I2          #If the current was calculated correctly the power will be calculated
               
               Vfplt.append(V)      #The values of current, voltage and power are added to their designated lists
               Ifplt.append(I2)
               Pfplt.append(P2)
               
               if P2 > P1:          #Check if the new power value is greater than the last. If yes it becomes the new reference power value.
                   P1 = P2
               
               else:
                   P_mpp_fs0 = P1   #If the power does not increase however, the Mpp of this P-V curve is found
                   
                   
                           
               if V >= V_oc_f0:     # When V reaches V_oc the P-V curve is complete and it has to be checked if Mpp converged with the Module parameters
               
                   #If the calculated Mpp is within the tolerance the script tells the user the Values of Rs and Rp aswell as the amount of iterations
                   #it took to calculate them                   
                   if P_mpp_f0 + tol_P >= P_mpp_fs0 and P_mpp_fs0 >= P_mpp_f0 - tol_P:
                       print ('Front resistance calculation completed in ',xf,' iterations.', 'Rs_f0 =', Rs_f0, 'Rp_f0 =', Rp_f0)
                       
                       
                       #The P-V and I-V curve is plotted with the values since the last Rs, Rp adjustment
                       f, (ax1) = plt.subplots(1, figsize=(6, 6))
                       ax1.locator_params(tight=True, nbins=6)
                       ax1.plot(Vfplt[-round(V_oc_f0 * 10):], Ifplt[-round(V_oc_f0 * 10):], color = "red")
                       ax1.set_title('P-V I-V Curve front side', fontsize=14)
                       ax1.set_xlabel('Voltage [V]', fontsize=14)
                       ax1.set_ylabel('Current [I]', fontsize=14, color = 'red')
                       ax2=ax1.twinx()
                       ax2.plot(Vfplt[-round(V_oc_f0 * 10):], Pfplt[-round(V_oc_f0 * 10):], color = "blue")
                       ax2.set_ylabel('Power [W]', fontsize=14, color = 'blue')
                       f.savefig("P-V_I-V_Curve_front" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
                       #plt.show()()
 
                       #Rs and Rp have been calculated so the script quits the loop 
                       break
                   
                   #If the calculated Mpp is not within tolerance, the reference power is reset and Rs gets increased by 10 mOhm 
                   else:
                       P1 = 0
                   
                       Rs_f0 = Rs_f0 + 0.01
                   
                       #Calculation of Rp with new Rs. For a better overview it is split into smaller calculations
                       r1 = V_mpp_f0 + I_mpp_f0 * Rs_f0
                       r2 = I_ph_f0
                       r3 = np.exp(r1/Vt)
                       r4 = np.exp(r1/(Vt*a2))
                       r5 = P_mpp_f0/V_mpp_f0
                       r6 = (r3 + r4 + 2)
                       r7 = r6 * I_0_f0

                       Rp_f0 = r1 / (r2 - r7 - r5)
                                     
                   V = -0.1     #V reached its max so it is set to -0.1 so in the first iteration we have I=0 and V=0
               I = 0
               V = V + 0.1
           else:
               I = I2           #If I2 was not close enough to I, I becomes I2 (newtons method)
        

        
        sum_energy_m = 0
        sum_power_m = 0
        
        
        # Loop to calculate the Bifacial Output power for every row in every hour
        for i in tqdm(range(0, simulationDict['nRows'])):
            
            key_front = "row_" + str(i) + "_qabs_front"
            key_back = "row_" + str(i) + "_qabs_back"
            
            P_m_hourly = []
            P_bi_hourly = []
            
            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
            y = 0 #index for hourly soiling rate value
            
            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                if temp == days_until_clean*24:
                    temp = 0
                else:
                    temp = temp +1

                if simulationDict["average_daily_soiling_rate"] == True:
                    soilrate = simulationDict["hourlySoilrate"]
                    
                    if simulationDict['simulationMode'] == 1 or simulationDict['simulationMode'] == 2 or simulationDict['simulationMode'] == 3:
                        # calculate front row power output including the soiling rate determined in GUI                               
                        row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate[y]/100))
                        # calculate back row power output including the decreased soiling for backside of PV module                                 
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate[y]/(100*10.581)))
                    
                    if simulationDict['simulationMode'] == 5:
                        row_qabs_front = 0
                        T_Current = df.loc[index,'temperature'] + ((df_report.loc[index,key_back]/800)*(moduleDict['T_NOCT'] - 20))
                    else:
                        row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate[y]/100))
                        T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                    if simulationDict['simulationMode'] == 4:
                        row_qabs_back = 0
                    else:
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate[y]/(100*10.581)))

                    # estimate module temperture with ambient temperature and NOCT temp

                    if np.isnan(T_Current):
                        T_Current = df.loc[index,'temperature']

                    #print("front: " + str(row_qabs_front))
                    #print("back: " + str(row_qabs_back))
                    if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                        row_qabs_front = 0
                            
                    if math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                        row_qabs_back = 0

                    if row_qabs_back + row_qabs_front > 0.0:
                            
                        #Now that Rs and Rp are calculated for both sides of the module, the power calculation starts.
                        #Values are now adjusted for temperature and later also irradiation
                            
                        I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb))     
                        I_sc_r = I_sc_r0 * (1 + T_koeff_I * (T_Current - T_amb))
                            
                        V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb))
                        V_oc_r = V_oc_r0 * (1 + T_koeff_V * (T_Current - T_amb))
                            
                        #setting starting parameters for the loop
                        I = 0
                        V = 0
                        P = 0
                        P1 = 0
                        P_mpp_sf = 0
                            
                            
                        #Modified version of the Rs, Rp calculation loop. Since Rs and Rp are now given, the loop needs only a fraction of iterations
                        #to calculate the power from a given irradiance and temperature
                        #The way this works is that the algorythm searches for the Mpp of the module with the given irradiance and temperature
                        #Just like a real PV system would do
                        #It 'draws' the P-V curve and finds the Mpp which is then the power output of the module
                        for yf in range (100000):
                                
                            if row_qabs_front == 0:
                                P_m = 0
                                P_mpp_sf = 0
                                break
                                
                            #Calculation of the photo current + correction for irrandiance and temperature
                            Vt_f = (Ns * k * (T_Current + 273.15)) / q_ec

                            #Calculation of the saturation current
                            I_0_f0 = (I_sc_f) / (np.exp((V_oc_f) / (Vt_f))-1)

                            #adjustment ot the photo current for irradiation
                            I_ph_f0 = I_sc_f                                             
                            I_ph_f = I_ph_f0 * (row_qabs_front / q_stc_front) 
                      
                            #newthons method to find the matching current for a given voltage
                            f_I = I_ph_f - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt_f) + np.exp((V + I * Rs_f0) / (Vt_f * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
                            f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt_f) * np.exp((V + I * Rs_f0) / Vt_f) - ((I_0_f0 * Rs_f0) / (Vt_f * a2)) * np.exp((V+ I * Rs_f0) / (Vt_f * a2)) - (Rs_f0 / Rp_f0) - 1
               
                            I2 = I - (f_I/f_dI)
                      
               
                            if I + tol_I >= I2 and I2 >= I - tol_I:         #Once I is found, the Power check starts just like in xf loop
                                P2 = V * I2

                                if P2 > P1:                 #Check if the new power is higher than the last
                                    P1 = P2                 #If this is true, it becomes the new reference value
                       
                                else:
                                    P_mpp_sf = P1           #The highest calculated power gets added to P_mpp_sf
                                        
                                if V >= V_oc_f:             # If V reached V_oc, the P-V curve is complete and the Mpp can be searched
                                    P_f = P_mpp_sf          #P_mpp_sf is the calculated Mpp for the Module for the given irradiance and and temperature
                                    P_m = P_f
                                    sum_energy_m += P_m     #The value gets added to a list for Bifacial gain calculation
                                    yf = 0                  #Iterations get reset after successful Mpp calculation
                                    break                   #The Mpp was found, the script quits the loop
                                  
                       
                                I = 0                       #Since there is only one P-V curve to calculate, V does not have to be reset
                                V = V + 0.1
                            else:
                                I = I2
                                
                                    
                            ##################################
                            ###Same procedure for back side###
                            ##################################
                        I = 0
                        V = 0
                        P = 0
                        P1 = 0
                            
                            
                            
                        for yr in range (100000):
                                
                            if row_qabs_front == 0:
                                P_mpp_sr = 0
                                break
                          
                            #Calculation of the photo current + correction for irrandiance and temperature
                            Vt_f = (Ns * k * (T_Current + 273.15)) / q_ec
                                
                            #Calculating the bifacial gain factor
                            BG = row_qabs_back / row_qabs_front
                                
                            #Calculation of the saturation current
                            I_0_f0 = (I_sc_f) / (np.exp((V_oc_f) / (Vt_f))-1)

                            #adjustment ot the photo current for irradiation and bifacial gain factor
                            I_ph_f0 = I_sc_f *BG                                             
                            I_ph_f = I_ph_f0 * (row_qabs_front / q_stc_front) 
                      
                            #newthons method to find the matching current for a given voltage
                            f_I = I_ph_f - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt_f) + np.exp((V + I * Rs_f0) / (Vt_f * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
                            f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt_f) * np.exp((V + I * Rs_f0) / Vt_f) - ((I_0_f0 * Rs_f0) / (Vt_f * a2)) * np.exp((V+ I * Rs_f0) / (Vt_f * a2)) - (Rs_f0 / Rp_f0) - 1
               
                            I2 = I - (f_I/f_dI)
                      
               
                            if I + tol_I >= I2 and I2 >= I - tol_I:         #Once I is found, the Power check starts just like in xf loop
                                P2 = V * I2

                                if P2 > P1:                 #Check if the new power is higher than the last
                                    P1 = P2                 #If this is true, it becomes the new reference value
                       
                                else:
                                    P_mpp_sr = P1           #The highest calculated power gets added to P_mpp_sr
                                        
                                if V >= V_oc_f:             # If V reached V_oc, the P-V curve is complete and the Mpp can be searched
                                    P_r = P_mpp_sr          #P_mpp_sr is the calculated Mpp for the Module for the given irradiance and and temperature
                                    yr = 0                  #Iterations get reset after successful Mpp calculation
                                    break                   #The Mpp was found, the script quits the loop

                                I = 0                       #Since there is only one P-V curve to calculate, V does not have to be reset
                                V = V + 0.1
                            else:
                                I = I2
                            
                        
                        P_bi = P_mpp_sf + P_mpp_sr
                        #print("Power: " + str(P_bi))
                    
                        sum_energy_b += P_bi # Sum up the energy of every row in every hour
                    
                    else:
                        P_m=0
                        P_bi=0
                        
                    P_m_hourly.append(P_m)
                    P_bi_hourly.append(P_bi)

                else:
                    soilrate = simulationDict['fixSoilrate']
                    
                    if simulationDict['simulationMode'] == 1 or simulationDict['simulationMode'] == 2 or simulationDict['simulationMode'] == 3:
                        # calculate front row power output including the soiling rate determined in GUI                               
                        row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate*(temp)/(100*24)))   
                        # calculate back row power output including the decreased soiling for backside of PV module                                 
                        row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate*(temp)/(100*24*10.581)))
                    
                    if simulationDict['simulationMode'] == 5:
                        row_qabs_front = 0
                        T_Current = df.loc[index,'temperature'] + ((df_report.loc[index,key_back]/800)*(moduleDict['T_NOCT'] - 20))
                    else:
                        row_qabs_front = df_report.loc[index,key_front] * (1 - ((soilrate*(temp)/(100*24))))
                        T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                    if simulationDict['simulationMode'] == 4:
                        row_qabs_back = 0
                    else:
                        row_qabs_back = df_report.loc[index,key_back] * (1 - ((soilrate*(temp)/(100*24*10.581))))

                    # estimate module temperture with ambient temperature and NOCT temp

                    if np.isnan(T_Current):
                        T_Current = df.loc[index,'temperature']
                        
                    #print("front: " + str(row_qabs_front))
                    #print("back: " + str(row_qabs_back))
                    if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                        row_qabs_front = 0
                    
                    if math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                        row_qabs_back = 0

                
                    if row_qabs_back + row_qabs_front > 0.0:
                    
                    #Now that Rs and Rp are calculated for both sides of the module, the power calculation starts.
                    #Values are now adjusted for temperature and later also irradiation
                    
                        I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb))     
                        I_sc_r = I_sc_r0 * (1 + T_koeff_I * (T_Current - T_amb))
                    
                        V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb))
                        V_oc_r = V_oc_r0 * (1 + T_koeff_V * (T_Current - T_amb))
                    
                        #setting starting parameters for the loop
                        I = 0
                        V = 0
                        P = 0
                        P1 = 0
                        P_mpp_sf = 0
                    
                    
                    #Modified version of the Rs, Rp calculation loop. Since Rs and Rp are now given, the loop needs only a fraction of iterations
                    #to calculate the power from a given irradiance and temperature
                    #The way this works is that the algorythm searches for the Mpp of the module with the given irradiance and temperature
                    #Just like a real PV system would do
                    #It 'draws' the P-V curve and finds the Mpp which is then the power output of the module
                        for yf in range (100000):
                        
                            if row_qabs_front == 0:
                                P_m = 0
                                P_mpp_sf = 0
                                break
                        
                        #Calculation of the photo current + correction for irrandiance and temperature
                            Vt_f = (Ns * k * (T_Current + 273.15)) / q_ec

                        #Calculation of the saturation current
                            I_0_f0 = (I_sc_f) / (np.exp((V_oc_f) / (Vt_f))-1)

                        #adjustment ot the photo current for irradiation
                            I_ph_f0 = I_sc_f                                             
                            I_ph_f = I_ph_f0 * (row_qabs_front / q_stc_front) 
              
                        #newthons method to find the matching current for a given voltage
                            f_I = I_ph_f - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt_f) + np.exp((V + I * Rs_f0) / (Vt_f * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
                            f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt_f) * np.exp((V + I * Rs_f0) / Vt_f) - ((I_0_f0 * Rs_f0) / (Vt_f * a2)) * np.exp((V+ I * Rs_f0) / (Vt_f * a2)) - (Rs_f0 / Rp_f0) - 1
       
                            I2 = I - (f_I/f_dI)
              
       
                            if I + tol_I >= I2 and I2 >= I - tol_I:         #Once I is found, the Power check starts just like in xf loop
                                P2 = V * I2

                                if P2 > P1:                 #Check if the new power is higher than the last
                                    P1 = P2                 #If this is true, it becomes the new reference value
               
                                else:
                                    P_mpp_sf = P1           #The highest calculated power gets added to P_mpp_sf
                                
                                if V >= V_oc_f:             # If V reached V_oc, the P-V curve is complete and the Mpp can be searched
                                    P_f = P_mpp_sf          #P_mpp_sf is the calculated Mpp for the Module for the given irradiance and and temperature
                                    P_m = P_f
                                    sum_energy_m += P_m     #The value gets added to a list for Bifacial gain calculation
                                    yf = 0                  #Iterations get reset after successful Mpp calculation
                                    break                   #The Mpp was found, the script quits the loop
                          
               
                                I = 0                       #Since there is only one P-V curve to calculate, V does not have to be reset
                                V = V + 0.1
                            else:
                                I = I2
                        
                            
                    ##################################
                    ###Same procedure for back side###
                    ##################################
                        I = 0
                        V = 0
                        P = 0
                        P1 = 0
                    
                    
                    
                        for yr in range (100000):
                        
                            if row_qabs_front == 0:
                                P_mpp_sr = 0
                                break
                  
                            #Calculation of the photo current + correction for irrandiance and temperature
                            Vt_f = (Ns * k * (T_Current + 273.15)) / q_ec
                        
                            #Calculating the bifacial gain factor
                            BG = row_qabs_back / row_qabs_front
                        
                       

                        
                            #Calculation of the saturation current
                            I_0_f0 = (I_sc_f) / (np.exp((V_oc_f) / (Vt_f))-1)

               

                            #adjustment ot the photo current for irradiation and bifacial gain factor
                            I_ph_f0 = I_sc_f *BG                                             
                            I_ph_f = I_ph_f0 * (row_qabs_front / q_stc_front) 
              
                            #newthons method to find the matching current for a given voltage
                            f_I = I_ph_f - I_0_f0 * (np.exp((V+ I * Rs_f0) / Vt_f) + np.exp((V + I * Rs_f0) / (Vt_f * a2)) - 2) - ((V + I * Rs_f0) / Rp_f0) - I
                            f_dI = (-1) * ((I_0_f0 * Rs_f0) / Vt_f) * np.exp((V + I * Rs_f0) / Vt_f) - ((I_0_f0 * Rs_f0) / (Vt_f * a2)) * np.exp((V+ I * Rs_f0) / (Vt_f * a2)) - (Rs_f0 / Rp_f0) - 1
       
                            I2 = I - (f_I/f_dI)
              
       
                            if I + tol_I >= I2 and I2 >= I - tol_I:         #Once I is found, the Power check starts just like in xf loop
                                P2 = V * I2

                                if P2 > P1:                 #Check if the new power is higher than the last
                                    P1 = P2                 #If this is true, it becomes the new reference value
               
                                else:
                                    P_mpp_sr = P1           #The highest calculated power gets added to P_mpp_sr
                                
                                if V >= V_oc_f:             # If V reached V_oc, the P-V curve is complete and the Mpp can be searched
                                    P_r = P_mpp_sr          #P_mpp_sr is the calculated Mpp for the Module for the given irradiance and and temperature
                                    yr = 0                  #Iterations get reset after successful Mpp calculation
                                    break                   #The Mpp was found, the script quits the loop
                          
               
                                I = 0                       #Since there is only one P-V curve to calculate, V does not have to be reset
                                V = V + 0.1
                            else:
                                I = I2
                    
                
                        P_bi = P_mpp_sf + P_mpp_sr
                        #print("Power: " + str(P_bi))
            
                        sum_energy_b += P_bi # Sum up the energy of every row in every hour
            
                    else:
                        P_m=0
                        P_bi=0
                
                    P_m_hourly.append(P_m)
                    P_bi_hourly.append(P_bi)
                
                # Append P_bi_hourly array to arrays
                P_m_hourly_arrays.append(P_m_hourly)
                P_bi_hourly_arrays.append(P_bi_hourly)
                #
            
        P_bi_hourly_average = []
        
        for i in tqdm(range(0, len(P_bi_hourly_arrays[0]))):
            sum = 0
          
            for j in range(0, len(P_bi_hourly_arrays)):
                sum += P_bi_hourly_arrays[j][i]
                
            average = sum / float(len(P_bi_hourly_arrays))
            
            P_bi_hourly_average.append(average)
            
       
        
        # The time gets implemented in the GUI
    # p_bi_df.to_csv(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
        
        
        annual_power_per_module_b = (sum_energy_b/simulationDict['nRows']) #[W] annual bifacial output power per module
        '''print("Yearly bifacial output power per module: " + str(annual_power_per_module_b) + " W/module")
        print("Yearly bifacial output energy per module: " + str(annual_power_per_module_b/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
        print ("\n")'''
        
        annual_power_per_peak_b = (sum_energy_b/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual bifacial output power per module peak power
        '''print("Yearly bifacial output power per module peak power: " + str(annual_power_per_peak_b) + " W/Wp")
        print("Yearly bifacial output energy per module peak power: " + str(annual_power_per_peak_b) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        module_area = (simulationDict['moduley'] *simulationDict['nModsy'] *simulationDict['modulex'])
        
        annual_power_per_area_b = (annual_power_per_module_b / module_area)    #[W/m^2] annual bifacial poutput power per module area
        '''print("Yearly bifacial output power per module area: " + str(annual_power_per_area_b) + " W/m^2")
        print("Yearly bifacial output energy per module area: " + str(annual_power_per_area_b/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        # Plot total qinc front and back for every row
      
        
        f = plt.Figure(figsize=(12, 3))
        ax1 = f.subplots(1)
        ax1.locator_params(tight=True, nbins=6)
        f.plot(P_bi_hourly)
        ax1.set_title('Bifacial output Power hourly')
        ax1.set_xlabel('Hour')
        ax1.set_ylabel('W')
        f.savefig("P_bi_hourly" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
        #plt.show()()
        #sns wird entfernt da die Plots in der GUI ansonsten nicht richtig angezeigt werden können außerhalb der Konsole
        ##plt.show()(sns)
        
        
        ####################################################
        # Monofacial performance Calculation
        
        # Set Energy to Zero       
#        sum_energy_m = 0
#        sum_power_m = 0
        
        # Loop to calculate the Monofacial Output power for every row in every hour
#        for i in tqdm(range(0, simulationDict['nRows'])):
            
#            key_front_mono = "row_" + str(i) + "_qabs_front"
#            P_m_hourly = []
#            temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
#            y = 0 #index for hourly soiling rate value
            
#            for index, row in df_report.iterrows():
                
                # count number of iterations until 'days_until_clean' is reached. Then start from 0  
#                if temp == days_until_clean*24:
#                    temp = 0
#                else:
#                    temp = temp +1

#                if simulationDict["average_daily_soiling_rate"] == True:
#                    soilrate = simulationDict["hourlySoilrate"]

#                    if simulationDict['simulationMode'] == 5:
#                        row_qabs_front = 0
#                    else:
#                        row_qabs_front = df_report.loc[index,key_front_mono] * (1 - (soilrate[y]/100))
                        
                    # estimate module temperture with ambient temperature and NOCT temp
#                    T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
#                    if np.isnan(T_Current):
#                        T_Current = df.loc[index,'temperature']

#                    if math.isnan(row_qabs_front):
#                        row_qabs_front = 0 
                        
#                    if  row_qabs_front > 0.0:
                      
#                        V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
#                        I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
#                        P_m = FF_f0 * V_oc_f * I_sc_f
                        
                        #print("Power: " + str(P_bi))
                     
#                        sum_energy_m += P_m # Sum up the energy of every row in every hour
#                    else:
#                        P_m = 0
                            
#                    P_m_hourly.append(P_m)
                #
                #
#                else:
#                    soilrate = simulationDict['fixSoilrate']
                        
#                    if simulationDict['simulationMode'] == 5:
#                        row_qabs_front = 0
#                    else:
#                        row_qabs_front = df_report.loc[index,key_front_mono] * (1 - (soilrate*(temp)/100*24)))
                        
                    # estimate module temperture with ambient temperature and NOCT temp
#                    T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
#                    if np.isnan(T_Current):
#                        T_Current = df.loc[index,'temperature']

#                    if math.isnan(row_qabs_front):
#                        row_qabs_front = 0 
                    
#                    if  row_qabs_front > 0.0:
              
#                        V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
#                        I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
#                        P_m = FF_f0 * V_oc_f * I_sc_f
                
                        #print("Power: " + str(P_bi))
             
#                        sum_energy_m += P_m # Sum up the energy of every row in every hour
#                    else:
#                        P_m = 0
                    
#                    P_m_hourly.append(P_m)
            
                # Append P_m_hourly array to arrays
#                P_m_hourly_arrays.append(P_m_hourly)
                
        P_m_hourly_average = []
        
        for i in tqdm(range(0, len(P_m_hourly_arrays[0]))):
            sum = 0
          
            for j in range(0, len(P_m_hourly_arrays)):
                sum += P_m_hourly_arrays[j][i]
                
            average_m = sum / float(len(P_m_hourly_arrays))
            
            P_m_hourly_average.append(average_m)
                 #else:
                    #print("Power: 0.0")
        
        annual_power_per_module_m = (sum_energy_m/simulationDict['nRows']) #[W] annual monofacial output power per module
        '''print("Yearly monofacial output power per module: " + str(annual_power_per_module_m) + " W/module")
        print("Yearly monofacial output energy per module: " + str(annual_power_per_module_m/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
        print ("\n")'''
        
        annual_power_per_peak_m = (sum_energy_m/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual monofacial output power per module peak power
        '''print("Yearly monofacial output power per module peak power: " + str(annual_power_per_peak_m) + " W/Wp")
        print("Yearly monofacial output energy per module peak power: " + str(annual_power_per_peak_m) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        module_area = (simulationDict['moduley'] *simulationDict['nModsy']* simulationDict['modulex'])
        
        annual_power_per_area_m = (annual_power_per_module_m / module_area)    #[W/m^2] annual monofacial poutput power per module area
        '''print("Yearly monofacial output power per module area: " + str(annual_power_per_area_m) + " W/m^2")
        print("Yearly monofacial output energy per module area: " + str(annual_power_per_area_m/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
        print ("\n")'''
        
        ####################################################
        
        # Bifacial Gain Calculation
        
        Bifacial_gain= (annual_power_per_peak_b - annual_power_per_peak_m) / annual_power_per_peak_m
        print("Bifacial Gain: " + str(Bifacial_gain*100) + " %")
        
                
        # Create dataframe with data
        p_bi_df = pd.DataFrame({"timestamps":df_report.index, "P_bi ": P_bi_hourly_average, "P_m ": P_m_hourly_average})
        p_bi_df.set_index("timestamps")
        p_bi_df.to_csv(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
        #p_bi_df.to_csv(resultsPath + "electrical_simulation.csv")
        
        #Plot for Bifacial Power Output + Bifacial Gain
        GUI.Window.makePlotBifacialRadiance(resultsPath,Bifacial_gain)
        
        def simulate_simpleBifacial_old(moduleDict, simulationDict, df_reportVF, df_reportRT, df_report, df, resultsPath):
            """
            Applies a simplified version of the electrical simulation after PVSyst. Uses bifaciality factor to calculate rear efficiency and fill factors.
            Rear open-circuit voltage and short-circuit current are calculated using rear irradiance and temperature. 
            The rear output is then determined through the rear fill factor. Then the bifacial electrical output is calculated by adding front and rear output.
            Calculates bifacial gain through a seperate monofacial electrical simulation.

            Parameters
            ----------
            moduleDict: module Dictionary containing module data
            simulationDict: simulation Dictionary, which can be found in BifacialSimu_main.py
            df_reportVF: Viewfactor simulation report
            df_reportRT: Raytracing simulation report
            df_report: Final simulation report, containing VF and RT data
            resultsPath: output filepath
            df: helper DataFrame containing temperature for electrical simulation
            """
            
           # jsonfile = ('module2.json')
            with open(rootPath + '/Lib/input_albedo/Albedo.json') as file:          #Laden des Json FIle aus dem Ordner
                jsondata_albedo = json.load(file)
            
            systemtuple = ('',)                     #Ohne können die Module nicht ausgewählt werden
            for key in jsondata_albedo.keys():                     #um auf die Modul Keys zurückgreifen zu können
                systemtuple = systemtuple + (str(key),)   #build the tuple of strings
            Combo_Albedo['values'] = systemtuple[1:]
            Combo_Albedo.current(0)                         # Combobox auf das erste Modul setzen
            self.jsondata_albedo = jsondata_albedo
       
        def comboclick_albedo(event):
            """ Insert Albedo value from Combobox
            """
            
          
            
            key1 = entry_albedo_value.get() # what is the value selected?
            #print(key + ' selected')
            if key1 != '':  # '' not a dict key
                
                a = self.jsondata_albedo[key1]
                self.albedo = key1
                         
                
                # clear module entries loaded from json
                Entry_albedo.delete(0,END)

 
               # set module entries loaded from json
                Entry_albedo.insert(0,str(a['Albedo']))
       
     
        
     
        
        Label_albedo=ttk.Label(simulationParameter_frame, text= "Albedo:")
        Label_albedo.grid(column=0, row=19, sticky="w")
        Entry_albedo=ttk.Entry(simulationParameter_frame, background="white", width=10)
        Entry_albedo.grid(column=1, row=19, sticky="w")
        entry_albedo_value = tk.StringVar()
        Combo_Albedo=ttk.Combobox(simulationParameter_frame, textvariable=entry_albedo_value)
        
        Combo_Albedo.grid(column=2, row=19, ipadx=50)
        getAlbedoJSONlist()                                     #set the module name values
        Combo_Albedo.bind("<<ComboboxSelected>>", comboclick_albedo)


# =============================================================================
#        Defining the Combobox for the modules
# =============================================================================


        def getModuleJSONlist():
            """ populate entry_modulename with module names from module.json
            """
            ####################################################
            # Variables required for electrical simulation
            
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
            # Definition of simulation parameter if only front parameters are available
            # Procedure after PVSyst
            V_mpp_f0 = moduleDict['V_mpp_f']
                
            I_mpp_f0 = moduleDict['I_mpp_f']
                    
            I_sc_f0 = moduleDict['I_sc_f']
            
            V_oc_f0 = moduleDict['V_oc_f']
            
            soilrate = simulationDict['fixSoilrate'] #Michailow
            days_until_clean = simulationDict['days_until_clean']
            
            #module = moduleParameter['module']
            #inverter = moduleParameter['inverter']
            
            P_mpp0 = moduleDict['P_mpp']
            V_mpp0 = V_mpp_f0
            
            T_koeff_P = moduleDict['T_koeff_P'] 
            T_koeff_I = moduleDict['T_koeff_I'] 
            T_koeff_V = moduleDict['T_koeff_V'] 
            T_amb = moduleDict['T_amb']
            
            q_stc_front = 1000  # [W/m^2] 
            q_stc_rear = 1000   # [W/m^2] 
            
            # Calculation of fill factor for STC conditions
            FF_f0 = (I_mpp_f0 * V_mpp_f0)/(I_sc_f0 * V_oc_f0)
            
            n_back = (moduleDict['bi_factor']*moduleDict['n_front'])
            
            FF_fr = (n_back*q_stc_rear*(simulationDict['moduley'])*(simulationDict['modulex']))/(I_sc_f0 * V_oc_f0)
                           
            dpi = 150 #Quality for plot export
            
            # Set Energy to Zero       
            sum_energy_b = 0
            sum_power_b = 0
            
            # Array to hold other arrays -> average after for loop
            P_bi_hourly_arrays = []
            
            df_report['timestamp'] = df_report.index
            df_report = df_report.reset_index()
            df_report['corrected_timestamp'] = pd.to_datetime(df_report['timestamp'])
            df_report['time'] = df_report['corrected_timestamp'].dt.strftime('%m_%d_%H')
            df_report = df_report.set_index('time')
            
            if simulationDict['simulationMode'] == 3:
                df = df.reset_index()
                
                df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
                df = df.set_index('time')
                df['timestamp'] = df['corrected_timestamp'].dt.strftime('%m-%d %H:%M%')
                df['timestamp'] = pd.to_datetime(df['timestamp'])  
                #df['timestamp'] = df['timestamp'].dt.tz_localize(None)
                df = df.set_index('timestamp')
                
                dtStart = datetime.datetime(simulationDict['startHour'][0], simulationDict['startHour'][1], simulationDict['startHour'][2], simulationDict['startHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
            
            
                dtEnd = datetime.datetime(simulationDict['endHour'][0], simulationDict['endHour'][1], simulationDict['endHour'][2], simulationDict['endHour'][3], tzinfo=dateutil.tz.tzoffset(None, simulationDict['utcOffset']*60*60))
                mask = (df.index >= dtStart) & (df.index <= dtEnd) 
                df = df.loc[mask]
            
            df['time'] = df['corrected_timestamp'].dt.strftime('%m_%d_%H')
            df = df.set_index('time')
            
            #################################################################################
            #soilingrate from theorical model
            city_name = simulationDict["city"]  # get the city, country name from 'Entry_weatherstation' 
            #print (str(city_name))
            #new_soilingrate = pd.read_csv(rootPath + '\Lib\input_soiling\soiling_data.csv', encoding ='latin-1' ) 
            df_city = pd.read_csv(rootPath + f'\city_data_soiling_accumulation\{city_name}.csv')
            #file_path = os.path.join(city_data_directory, f"{city_name}.csv")
            #df_city = pd.read_csv(file_path)
            # Convert the 'Date' column into date format for both DataFrames
            df_city['Date'] = pd.to_datetime(df_city['Date'], dayfirst=True)
            df_report['corrected_timestamp'] = pd.to_datetime(df_report['corrected_timestamp'], dayfirst=True)

            # Create an empty list to store the corresponding soilingrate values
            sr_value = []

            # Browse rows in DataFrame "df_report
            for index, row in df_report.iterrows():
                # Extract the date (day and month) of the current row from the "df_report" DataFrame
                date_df_report = row['corrected_timestamp'].replace(year=2023)  # Remplacer l'année par l'année appropriée
                
                # Filter the "City, Country" DataFrame to obtain rows with the same date (day and month)
                df_filtered = df_city[(df_city['Date'].dt.day == date_df_report.day) & (df_city['Date'].dt.month == date_df_report.month)]
                
                # Check whether rows have been found in the filtered DataFrame
                if not df_filtered.empty:
                    # Retrieve the soilingrate value from the first corresponding line
                    soilingrate_value = df_filtered.iloc[0]['soilingrate']
                    
                    # Add the soilingrate value to the "sr_value" list
                    sr_value.append(soilingrate_value)
                else:
                    # Add a default value (for example, 0) if no corresponding soilingrate value has been found
                    sr_value.append(0)
            simulationDict["hourlySoilrate"] = sr_value
            #print('AAA', len(simulationDict["hourlySoilrate"]))
            #print('VBBB', len(sr_value))
            #print('XXXXXXX', len(df_report))
            #df_reportVF
            # Display the list containing the corresponding soilingrate values for each identical day and month
            #print(len(sr_value))
            #print(sr_value)
            ############################################################################################################################################################

            df_time_soiling = pd.DataFrame(df_report['corrected_timestamp'])
            df_time_soiling['month'] = df_report['corrected_timestamp'].dt.strftime('%m') # Needed to choose wright soiling rate from SimulationDict                                            
            df_time_soiling = df_time_soiling.reset_index(drop = True)
            
            print(df_report)
            
            
            # Loop to calculate the Monofacial Output power for every row in every hour
            for i in tqdm(range(0, simulationDict['nRows'])):
                
                key_front = "row_" + str(i) + "_qabs_front"
                key_back = "row_" + str(i) + "_qabs_back"
            
                P_bi_hourly = []
                
                temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
                y = 0 #index for hourly soiling rate value
                
                for index, row in df_report.iterrows():
                    
                    # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                    if temp == days_until_clean*24:
                        temp = 0
                    else:
                        temp = temp +1

                    if simulationDict["average_daily_soiling_rate"] == True:
                        soilrate = simulationDict["hourlySoilrate"]
                        
                        if simulationDict['simulationMode'] == 1 or simulationDict['simulationMode'] == 2 or simulationDict['simulationMode'] == 3:
                            # calculate front row power output including the soiling rate determined in GUI                               
                            row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate[y]/100))
                            # calculate back row power output including the decreased soiling for backside of PV module                                 
                            row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate[y]/(100*10.581)))

                        if simulationDict['simulationMode'] == 5:
                            row_qabs_front = 0
                        else:
                            row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate[y]/100))
    #                        T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))

                        if simulationDict['simulationMode'] == 4:
                            row_qabs_back = 0
                        else:
                            row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate[y]/(100*10.581)))
    #                        T_Current = df.loc[index,'temperature'] + ((row_qabs_back/800)*(moduleDict['T_NOCT'] - 20))

                        # estimate module temperture with ambient temperature and NOCT temp
                        T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                        if np.isnan(T_Current):
                            T_Current = df.loc[index,'temperature']
                        
                        row_qabs_combined = row_qabs_front + (row_qabs_back*bi_factor)

                        # calculation of frontside power output
                        if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                            row_qabs_front = 0
                            P_f = 0
                                
                        else:
                            V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
                            I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
                            P_f = FF_f0 * V_oc_f * I_sc_f

                        # calculation of backside power output
                        if math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                            row_qabs_back = 0
                            P_r = 0
                                
                        else:
                            V_oc_r = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_back / q_stc_rear))
                            I_sc_r = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_back / q_stc_rear)
                            P_r = FF_fr * V_oc_r * I_sc_r
                                
                            
                        P_bi = P_f + P_r 
                            
                    
                            
                        sum_energy_b += P_bi # Sum up the energy of every row in every hour

                        P_bi_hourly.append(P_bi)


                    else:
                        soilrate = simulationDict['fixSoilrate']
                        
                        if simulationDict['simulationMode'] == 1 or simulationDict['simulationMode'] == 2 or simulationDict['simulationMode'] == 3:
                            # calculate front row power output including the soiling rate determined in GUI                               
                            row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate*(temp)/(100*24)))   
                            # calculate back row power output including the decreased soiling for backside of PV module                                 
                            row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate*(temp)/(100*24*10.581)))
                            
                        if simulationDict['simulationMode'] == 5:
                            row_qabs_front = 0
                        else:
                            row_qabs_front = df_report.loc[index,key_front] * (1 - (soilrate*(temp)/(100*24)))
    #                        T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                            
                        if simulationDict['simulationMode'] == 4:
                            row_qabs_back = 0
                        else:
                            row_qabs_back = df_report.loc[index,key_back] * (1 - (soilrate*(temp)/(100*24*10.581)))
    #                        T_Current = df.loc[index,'temperature'] + ((row_qabs_back/800)*(moduleDict['T_NOCT'] - 20))

                        # estimate module temperture with ambient temperature and NOCT temp
                        T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                        if np.isnan(T_Current):
                            T_Current = df.loc[index,'temperature']
                            
                        row_qabs_combined = row_qabs_front + (row_qabs_back*bi_factor)
                    
                        # calculation of frontside power output
                        if math.isnan(row_qabs_front) or row_qabs_front < 0.0:
                            row_qabs_front = 0
                            P_f = 0
                        
                        else:
                            V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
                            I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
                            P_f = FF_f0 * V_oc_f * I_sc_f

                        # calculation of backside power output
                        if math.isnan(row_qabs_back) or row_qabs_back < 0.0:
                            row_qabs_back = 0
                            P_r = 0
                        
                        else:
                            V_oc_r = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_back / q_stc_rear))
                            I_sc_r = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_back / q_stc_rear)
                            P_r = FF_fr * V_oc_r * I_sc_r
                        
                    
                        P_bi = P_f + P_r 
                    
            
                    
                        sum_energy_b += P_bi # Sum up the energy of every row in every hour

                        P_bi_hourly.append(P_bi)
                    
                    # Append P_bi_hourly array to arrays
                    P_bi_hourly_arrays.append(P_bi_hourly)

                    #print(sum_energy_b)
                             
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
            p_bi_df.to_csv(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
            
            
            annual_power_per_module_b = (sum_energy_b/simulationDict['nRows']) #[W] annual bifacial output power per module
            '''print("Yearly bifacial output power per module: " + str(annual_power_per_module_b) + " W/module")
            print("Yearly bifacial output energy per module: " + str(annual_power_per_module_b/1000) + " kWh/module") # Because the input data is per hour, the Energy is equivalent to the performance
            print ("\n")'''
            
            annual_power_per_peak_b = (sum_energy_b/(P_mpp0 * simulationDict['nRows']))   #[W/Wp] annual bifacial output power per module peak power
            '''print("Yearly bifacial output power per module peak power: " + str(annual_power_per_peak_b) + " W/Wp")
            print("Yearly bifacial output energy per module peak power: " + str(annual_power_per_peak_b) + " kWh/kWp") # Because the input data is per hour, the Energy is equivalent to the performance 
            print ("\n")'''
            
            module_area = (simulationDict['moduley'] * simulationDict['nModsy'] * simulationDict['modulex'])
            
            annual_power_per_area_b = (annual_power_per_module_b / module_area)    #[W/m^2] annual bifacial poutput power per module area
            '''print("Yearly bifacial output power per module area: " + str(annual_power_per_area_b) + " W/m^2")
            print("Yearly bifacial output energy per module area: " + str(annual_power_per_area_b/1000) + " kWh/m^2") # Because the input data is per hour, the Energy is equivalent to the performance 
            print ("\n")'''
            
            # Plot total qinc front and back for every row
          
            
            f = plt.Figure(figsize=(12, 3))
            ax1 = f.subplots(1)
            ax1.locator_params(tight=True, nbins=6)
            f.plot(P_bi_hourly)
            ax1.set_title('Bifacial output Power hourly')
            ax1.set_xlabel('Hour')
            ax1.set_ylabel('W')
            f.savefig("P_bi_hourly" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png", dpi = dpi)
            #plt.show()()
            #sns wird entfernt da die Plots in der GUI ansonsten nicht richtig angezeigt werden können außerhalb der Konsole
            ##plt.show()(sns)
             
            ####################################################
            # Monofacial performance Calculation
            
            # Set Energy to Zero
            sum_energy_m = 0
            sum_power_m = 0
            
            # Loop to calculate the Monofacial Output power for every row in every hour
            for i in tqdm(range(0, simulationDict['nRows'])):
                
                key_front_mono = "row_" + str(i) + "_qabs_front"
                P_m_hourly = []
                temp = 0  #couting variable in loop to calculate soilrate for consecutive hours
                y = 0 #index for hourly soiling rate value
                
                for index, row in df_report.iterrows():
                    
                    # count number of iterations until 'days_until_clean' is reached. Then start from 0  
                    if temp == days_until_clean*24:
                        temp = 0
                    else:
                        temp = temp +1

                    if simulationDict["average_daily_soiling_rate"] == True:
                        soilrate = simulationDict["hourlySoilrate"]
                        if simulationDict['simulationMode'] == 5:
                            row_qabs_front = 0
                        else:
                            row_qabs_front = df_report.loc[index,key_front_mono] * (1 - (soilrate[y]/100))
                            
                        # estimate module temperture with ambient temperature and NOCT temp
                        T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                        if np.isnan(T_Current):
                            T_Current = df.loc[index,'temperature']
                            

                        if math.isnan(row_qabs_front):
                            row_qabs_front = 0 
                            
                        if  row_qabs_front > 0.0:
                          
                            V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
                            I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
                            P_m = FF_f0 * V_oc_f * I_sc_f
                            
                            #print("Power: " + str(P_bi))
                         
                            sum_energy_m += P_m # Sum up the energy of every row in every hour
                        else:
                            P_m = 0
                                
                        P_m_hourly.append(P_m)

                    else:
                        soilrate = simulationDict['fixSoilrate']
                                                
                        if simulationDict['simulationMode'] == 5:
                            row_qabs_front = 0
                        else:
                            row_qabs_front = df_report.loc[index,key_front_mono] * (1 - (soilrate*(temp)/(100*24)))
                        
                        # estimate module temperture with ambient temperature and NOCT temp
                        T_Current = df.loc[index,'temperature'] + ((row_qabs_front/800)*(moduleDict['T_NOCT'] - 20))
                        if np.isnan(T_Current):
                            T_Current = df.loc[index,'temperature']

                        if math.isnan(row_qabs_front):
                            row_qabs_front = 0 
                    
                        if  row_qabs_front > 0.0:
                  
                            V_oc_f = V_oc_f0 * (1 + T_koeff_V * (T_Current - T_amb) + moduleDict['zeta'] * np.log(row_qabs_front / q_stc_front))
                            I_sc_f = I_sc_f0 * (1 + T_koeff_I * (T_Current - T_amb)) * (row_qabs_front / q_stc_front)
                            P_m = FF_f0 * V_oc_f * I_sc_f
                    
                            #print("Power: " + str(P_bi))
                 
                            sum_energy_m += P_m # Sum up the energy of every row in every hour
                        else:
                            P_m = 0
                        
                        P_m_hourly.append(P_m)
                
                    # Append P_m_hourly array to arrays
                    P_m_hourly_arrays.append(P_m_hourly)
            #
            P_m_hourly_average = []
            
            for i in tqdm(range(0, len(P_m_hourly_arrays[0]))):
                sum = 0
              
                for j in range(0, len(P_m_hourly_arrays)):
                    sum += P_m_hourly_arrays[j][i]
                    
                average_m = sum / float(len(P_m_hourly_arrays))
                
                P_m_hourly_average.append(average_m)
                     #else:
                        #print("Power: 0.0")
            
           # jsonfile = ('module.json')
            with open(rootPath + '/Lib/input_module/module.json') as file:          #Laden des Json FIle aus dem Ordner
                jsondata = json.load(file)
            
            systemtuple = ('',)                     
            for key in jsondata.keys():                     #getting the keys
                systemtuple = systemtuple + (str(key),)   #build the tuple of strings
            Combo_Module['values'] = systemtuple[1:]
            Combo_Module.current(0)                         # Combobox on first key
            self.jsondata = jsondata
       
        def comboclick_Module(event):
            """ load specific module data from module.json after new module selected
            """
            
          
            
            key = entry_modulename_value.get() # what is the value selected?
            #print(key + ' selected')
            if key != '':  # '' not a dict key
                
                d = self.jsondata[key]
                self.module_type = key
                SimulationDict["module_type"]=self.module_type            
                
                # clear module entries loaded from json
                Entry_bi_factor.delete(0,END)
                Entry_nfront.delete(0,END)
                Entry_Iscf.delete(0,END)
                Entry_Iscr.delete(0,END)
                Entry_Vocf.delete(0,END)
                Entry_Vocr.delete(0,END)
                Entry_Vmppf.delete(0,END)
                Entry_Vmppr.delete(0,END)
                Entry_Imppf.delete(0,END)
                Entry_Imppr.delete(0,END)
                Entry_Pmpp.delete(0,END)
                Entry_TkoeffP.delete(0,END)
                Entry_Tamb.delete(0,END)
                Entry_TkoeffI.delete(0,END)
                Entry_TkoeffV.delete(0,END)
                Entry_zeta.delete(0,END)
                Entry_modulex.delete(0,END)
                Entry_moduley.delete(0,END)
 
               # set module entries loaded from json
               
                if rb_ElectricalMode.get()==0:                  #If the rb "Without rear values!" is activated it is possible to just pick the A-Modules
     #A-Modules: Number 1 to 3 in the list of the Combobox
     #B-Modules: Number 4 to the end in the list of the Combobox                
                    
                    
                    Entry_bi_factor.insert(0,str(d['bi_factor']))
                    Entry_nfront.insert(0,str(d['n_front']))
                    Entry_Iscf.insert(0,str(d['I_sc_f']))
                    Entry_Iscr.insert(0,str(d['I_sc_r']))
                    Entry_Vocf.insert(0,str(d['V_oc_f']))
                    Entry_Vocr.insert(0,str(d['V_oc_r']))
                    Entry_Vmppf.insert(0,str(d['V_mpp_f']))
                    Entry_Vmppr.insert(0,str(d['V_mpp_r']))
                    Entry_Imppf.insert(0,str(d['I_mpp_f']))              
                    Entry_Imppr.insert(0,str(d['I_mpp_r']))
                    Entry_Pmpp.insert(0,str(d['P_mpp']))
                    Entry_TkoeffP.insert(0,str(d['T_koeff_P']))
                    Entry_Tamb.insert(0,str(d['T_amb']))
                    Entry_TkoeffI.insert(0,str(d['T_koeff_I']))
                    Entry_TkoeffV.insert(0,str(d['T_koeff_V']))
                    Entry_zeta.insert(0,str(d['zeta']))
                    Entry_modulex.insert(0,str(d['modulex']))
                    Entry_moduley.insert(0,str(d['moduley']))   
                
                else:                                               #If the rb "Without rear values!" is activated it is possible to just pick the B-Modules
 
    # 0 means "nicht verfügbar" or not avaiable in this Radiobutton mode                  
                    Entry_bi_factor.insert(0,str(d['bi_factor']))
                    Entry_nfront.insert(0,str(d['n_front']))
                    Entry_Iscf.insert(0,str(d['I_sc_f']))
                    Entry_Iscr.insert(0, "0")
                    Entry_Vocf.insert(0,str(d['V_oc_f']))
                    Entry_Vocr.insert(0,"0")
                    Entry_Vmppf.insert(0,str(d['V_mpp_f']))
                    Entry_Vmppr.insert(0,"0")
                    Entry_Imppf.insert(0,str(d['I_mpp_f']))              
                    Entry_Imppr.insert(0,"0")
                    Entry_Pmpp.insert(0,str(d['P_mpp']))
                    Entry_TkoeffP.insert(0,str(d['T_koeff_P']))
                    Entry_Tamb.insert(0,str(d['T_amb']))
                    Entry_TkoeffI.insert(0,str(d['T_koeff_I']))
                    Entry_TkoeffV.insert(0,str(d['T_koeff_V']))
                    Entry_zeta.insert(0,str(d['zeta']))
                    Entry_modulex.insert(0,str(d['modulex']))
                    Entry_moduley.insert(0,str(d['moduley']))    
                

        # Combobox Module
        
        entry_modulename_value = tk.StringVar()
        Combo_Module=ttk.Combobox(ModuleParameter_frame, textvariable=entry_modulename_value)
        
        Combo_Module.grid(column=1, row=0)
        getModuleJSONlist()                                     #set the module name values
        Combo_Module.bind("<<ComboboxSelected>>", comboclick_Module)





                # If you get the Error Pyimage X isnt existing restart the Console

        #Loading the image in the program
        def logo():
            self.logo = Image.open(rootPath+'/Lib/logos/logo_BifacialSimu_transparentresized.png')
            logo=self.logo
            #resizing the image
            self.resized=logo.resize((100, 100), Image.ANTIALIAS)
            self.logo1 = ImageTk.PhotoImage(self.resized)


            #pack the image in the frame
            Label_logo=ttk.Label(simulationParameter_frame, image=self.logo1)
            Label_logo.image=logo
            Label_logo.grid(row=0,column=2)
        
        logo()

        #Loading the second image in the program
        def logo2():
            self.logo2 = Image.open(rootPath+'/Lib/default/Example_Config.png')
            logo2=self.logo2
            #resizing the image
            self.resized2=logo2.resize((400, 350), Image.ANTIALIAS)
            self.logo2 = ImageTk.PhotoImage(self.resized2)


            #pack the image in the frame
            Label2_logo=ttk.Label(namecontrol_frame, image=self.logo2)
            Label2_logo.image=logo2
            Label2_logo.grid(row=9,column=0, columnspan=3)
        
        logo2()
        
        


        # activates the first Radiobuttons to disable ttk.Entry fields and write in the Dict
                
        Weatherfile()
        simMode()
        Singleaxis()
        Measuredalbedo()
        Electricalmode()
        Backtracking()
        
# =============================================================================
#         Control Buttons for the Simulation    
# =============================================================================
        
        #start Simulation in Thread
        def generate_thread():
            
            #breaking flag must be rest before starting a new Simulation, otherwise it won't function if someone pressed the stop button before.
            globals.thread_break = False 
            
            threading.Thread(target=StartSimulation).start()
       
        #break Simulation in Thread
        def Break_Simulation():
            
            #messagebox to ask users if they are sure they want to terminate process.          
            answer = messagebox.askyesno("Stopping Simulation", "Are you sure you want to stop the simulation?", )
            
            if answer == 1:
                #breaking flag switches to True to trigger the simulation break
                globals.thread_break = True
                
        Button_startSimulation=ttk.Button(simulationFunction_frame, text="Start Simulation!", command=generate_thread)
        Button_startSimulation.grid(column=2,row=1)
        Button_setDefault=ttk.Button(simulationFunction_frame, text="set default!", command=setdefault)
        Button_setDefault.grid(column=0,row=1)
        Button_clear=ttk.Button(simulationFunction_frame, text="clear!", command=clearall)
        Button_clear.grid(column=1,row=1)
        Button_stopSimulation=ttk.Button(simulationFunction_frame, text="Stop Simulation!", command=Break_Simulation)
        Button_stopSimulation.grid(column=3,row=1)
        
        

    def _on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    
    def makePlotBifacialRadiance(resultsPath, Bifacial_gain):
        
        if SimulationDict["simulationMode"]==1 or SimulationDict["simulationMode"]==2: 
            plt.style.use("seaborn")
            
            
            data=pd.read_csv(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
            date=pd.read_csv(resultsPath + "/Data.csv")
            timestamp_start=date.timestamp [0]
           # print (timestamp_start)
            timestamp_end=len(date.timestamp)
           # timestamp_end=
            idx=pd.date_range(timestamp_start, periods=timestamp_end, freq="1H")
            
            P_bi=data["P_bi "]
            
           
            fig3 = plt.Figure()
            ax3= fig3.subplots()
            
            ax3.plot(idx,P_bi, label="P_bi ")
            
            ax3.xaxis.set_minor_locator(dates.DayLocator(interval=1))   # every Day
            ax3.xaxis.set_minor_formatter(dates.DateFormatter('%d'))  # day and hours
            ax3.xaxis.set_major_locator(dates.MonthLocator(interval=1))    # every Month
            ax3.xaxis.set_major_formatter(dates.DateFormatter('\n%m-%Y'))             
            ax3.legend()
            ax3.set_ylabel('Power Output\n[W/m²]', size=17)
            ax3.set_xlabel("Time", size=17)
            ax3.set_title('Bifacial Output Power\Bifacial Gain: '+ str(Bifacial_gain*100) + " %", size=18)
            
            #fig3.grid(True, which="minor")
            fig3.tight_layout()
            fig3.savefig("Bifacial_output_Power_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png")
            #os.rename(resultsPath + "/electrical_simulation.csv", resultsPath + "electrical_simulation_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
            
            canvas = FigureCanvasTkAgg(fig3, master=tk.Toplevel())
            canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1.0)
            canvas.draw()
                
        if SimulationDict["simulationMode"]==3  or SimulationDict["simulationMode"]==5:
            plt.style.use("seaborn")
            
            
            data=pd.read_csv(resultsPath + "electrical_simulation" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv")
            date1=pd.read_csv(resultsPath + "/Dataframe_df.csv")
            date2=pd.read_csv(resultsPath + "/df_reportRT.csv")
            timestamp_start=date1.corrected_timestamp [0]
           # print (timestamp_start)
            timestamp_end=len(date2.row_2_qinc_front)       #
     
            idx=pd.date_range(timestamp_start, periods=timestamp_end, freq="1H")
            
            P_bi=data["P_bi "]
            
           
            fig3 = plt.Figure()
            ax3= fig3.subplots()
            
            ax3.plot(idx,P_bi, label="P_bi ")
            
            ax3.xaxis.set_minor_locator(dates.DayLocator(interval=1))   # every Day
            ax3.xaxis.set_minor_formatter(dates.DateFormatter('%d'))  # day and hours
            ax3.xaxis.set_major_locator(dates.MonthLocator(interval=1))    # every Month
            ax3.xaxis.set_major_formatter(dates.DateFormatter('\n%m-%Y'))             
            ax3.legend()
            ax3.set_ylabel('Power Output\n[W/m²]', size=17)
            ax3.set_xlabel("Time", size=17)
            ax3.set_title('Bifacial Output Power\nBifacial Gain: '+ str(Bifacial_gain*100) + " %", size=17)
            
            #fig3.grid(True, which="minor")
            fig3.tight_layout()
            fig3.savefig("Bifacial_output_Power_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".png")
            #os.rename(resultsPath + "/electrical_simulation.csv", resultsPath + "electrical_simulation_" + datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + ".csv") 




def gui():    
    root = Window()
    # bring window into focus

    root.lift()
    root.attributes('-topmost',True)
    root.after_idle(root.attributes,'-topmost',False)
    # run mainloop 
    root.mainloop()
    print("\nNow leaving GUI")


# If the script is run as a file, it needs to call gui().    
if __name__ == '__main__':
    gui()  

# Showing parameter after closing the GUI
print (SimulationDict)
print (ModuleDict)

