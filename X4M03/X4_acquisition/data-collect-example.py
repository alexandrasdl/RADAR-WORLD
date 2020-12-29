""" data-collect-example.py

#Target module: X4M200,X4M300,X4M03

#Firmware: XEP

#Introduction: This code was developed to XeThru modules which support both RF and baseband data output. This example record radar baseband data during 60 seconds and store it into a .txt file. 
	
#How to Use: To run this script three function should be used: start_uwb(), log_uwb() and stop_uwb()

"""

# Import Libraries

from __future__ import print_function, division

import sys
from optparse import OptionParser
from time import sleep
from math import floor

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

import pymoduleconnector
from pymoduleconnector import DataType
import os

import time

# ------------------------------------------------------------------

''' Parameters configuration'''

# COM port from where radar module is connected
device_name = "COM4"
# directory 
dir = "/X4_records"
# time
interval = 60
# Define X4 Parameters 
FPS = 20  # Frames Per Second
area_start, area_end = 0.3, 3 # Area Start and End
fs = 23.328e9 # Sampling Rate
fc = 7.29e9 # Center Frequency
PRF = 15.1875e6 # Pulse Per Frequency
dac_min, dac_max = 950, 1150 # DAC from Threshold Sweep Methods
interations = 64 # Parameter from Threshold Sweep Methods (recommended)
duty_ = 0.95 # Duty Cycle
pulses_per_step = 56 # Parameter from Threshold Sweep Methods (adapter to be optimized for maximum integration on chip)

''' End '''

# other global variables
xep = 0 
# Create Matrix where frames will be stored
save_frames = []

# ------------------------------------------------------------------

def start_uwb():
    """ Set parameters and initialize X4 chip """
    # Reset device to start a new acquisition
    mc = pymoduleconnector.ModuleConnector(device_name)
    xep = mc.get_xep()
    xep.module_reset()
    mc.close()
    sleep(3)

    # Create a new Module Connector
    mc = pymoduleconnector.ModuleConnector(device_name)
    
    save_frames = []
    # Assume an X4M300/X4M200 module and try to enter XEP mode
    app = mc.get_x4m300()
    # Stop running application and set module in manual mode.
    try:
        app.set_sensor_mode(0x13, 0) # Make sure no profile is running.
    except RuntimeError:
        # Profile not running, OK
        pass

    try:
        app.set_sensor_mode(0x12, 0) # Manual mode.
    except RuntimeError:
        # Maybe running XEP firmware only?
        pass

    xep = mc.get_xep()

    # Set X4 Parameters 
    xep.x4driver_set_frame_area_offset(0) 
    xep.x4driver_set_frame_area(area_start,area_end)
    xep.x4driver_set_dac_min(dac_min)
    xep.x4driver_set_dac_max(dac_max)
    xep.x4driver_set_iterations(interations)
    xep.x4driver_set_pulses_per_step(pulses_per_step)

    # Set Baseband Mode
    xep.x4driver_set_downconversion(int(True))
    xep.x4driver_set_fps(FPS)
    
    log_uwb()
    
# ------------------------------------------------------------------
    
def log_uwb():
    """ Read and save complex values coming from X4 """

    def read_frame():
        """Gets frame data from module"""
        d = xep.read_message_data_float()
        frame = np.array(d.data)
         # Convert the resulting frame to a complex array
        n = len(frame)
        frame = frame[:n//2] + 1j*frame[n//2:]
        # save frame
        save_frames.append(frame)
        
    # Start streaming of data
    start = time.time()

    while True:
            # Update the data and check if the data is okay
            if (time.time() - start < interval):     
                read_frame()
            else: 
                stop_uwb()
                
# ------------------------------------------------------------------
                
def stop_uwb():
       """ Finish and save X4 files inside a previous defined directory """
       # Stop acquisition
       xep.x4driver_set_fps(0)
     
       # Find number of files in path and increase value to recorded file
       number_of_files_in_path = len([1 for x in list(os.scandir(dir)) if x.is_file()])
       filename = "/record_"+str(number_of_files_in_path+1)+".txt"
       
       # Write Acquisition parameters in the file
       f = open(dir + filename,"w+")      
       f.write("FPS: " + str(FPS) + "\n")
       f.write("area_start: " + str(area_start) + "\n")
       f.write("area_end: " + str(area_end) + "\n")
       f.write("fs: " + str(fs) + "\n")
       f.write("fc: " + str(fc) + "\n")
       f.write("PRF: " + str(PRF) + "\n")
       f.write("dac_min: " + str(dac_min) + "\n")
       f.write("dac_max: " + str(dac_max) + "\n")
       f.write("interations: " + str(interations) + "\n")
       f.write("duty_: " + str(duty_) + "\n")
       f.write("pulses_per_step: " + str(pulses_per_step) + "\n")
       
       # Write matrix inside file
       for i in range(len(save_frames)):
           for x in np.nditer(save_frames[i]):
               if (save_frames[i].size)>1:
                   f.write(str(x) + " ")
               else:
                   f.write("\n" + str(x) + "\n")
       f.write("\n")
       
       # Close File
       f.close()
       
# -------------------------    MAIN   -----------------------------------------      

# Start Acquisition and stop after 60 seconds             
start_uwb()
print("finish")