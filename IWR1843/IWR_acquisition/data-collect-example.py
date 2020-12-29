""" data-collect-example.py

#Target module: IWRxxx or 

#Firmware: profile_VitalSigns for xwr1642

#Introduction: This code was developed and adapter to IWR1843 using the firmware developed for IWR1642. In this examples complex fft data is saved during 60 seconds and store it into a .txt file. 
	
#How to Use: To run this script three function should be used: start_fmcw(), log_fmcw() and stop_fmcw()

"""

# Import Libraries

import serial
import time
import numpy as np
import matplotlib.pyplot as plt
import winsound
import os

''' Parameters configuration'''

# Change the configuration file name
configFileName = "profile_VitalSigns_20fps"
# Change Port: please take care with each respective baud rate defined at serialConfig()
CLIport_ = "COM8"
Dataport_ = "COM6"

# other global variables
CLIport = {}
Dataport = {}
byteBuffer = []
byteBufferLength = 0;

# ------------------------------------------------------------------

def start_fmcw():
    """ Set serial ports, send confiugration file to radar and initialize IWR chip """
    
    global CLIport
    global Dataport
    # Open the serial ports for the configuration and the data ports
    
    # Windows
    CLIport = serial.Serial(CLIport_, 115200)
    Dataport = serial.Serial(Dataport_, 921600)

    # Read the configuration file and send it to the board
    config = [line.rstrip('\r\n') for line in open(configFileName)]
    for i in config:
        CLIport.write((i+'\n').encode())
        time.sleep(0.01)
        
    log_fmcw()

# ------------------------------------------------------------------

def log_fmcw():
    """ Read and save complex values coming from IWR """
    
    def readAndParseData18xx(Dataport):
        """Gets frame data from module"""
        global byteBuffer, byteBufferLength
    
        readBuffer = Dataport.read(Dataport.in_waiting)
        byteVec = np.frombuffer(readBuffer, dtype = 'int8')
        byteBuffer.append(np.array(time.time()))
        byteBuffer.append(np.array(byteVec))
        print("---")
        
        # Start streaming of data
        start = time.time()

    while True:
            # Update the data and check if the data is okay
            if (time.time() - start < interval):     
                readAndParseData18xx(Dataport)
                time.sleep(0.01) # Sampling frequency of 30 Hz
            else: 
                stop_uwb()
                
# ------------------------------------------------------------------

def stop_uwb():
       """ Finish and save IWR files inside a previous defined directory """
       # Stop acquisition and close open doors
       CLIport.write(('sensorStop\n').encode())
       CLIport.close()
       Dataport.close()
     
       # Find number of files in path and increase value to recorded file
       number_of_files_in_path = len([1 for x in list(os.scandir(dir)) if x.is_file()])
       filename = "/record_"+str(number_of_files_in_path+1)+".txt"
       
       # Open directory and start writiing inside .txt. file
       # Write matrix inside file
        f = open(dir + filename,"w+")      
        
        for i in range(len(byteBuffer)-1):

             if byteBuffer[i+1].size == 0 or byteBuffer[i].size == 0:
                  print("is empty")
             else:
                 for x in np.nditer(byteBuffer[i]):
                     if (byteBuffer[i].size)>1:
                         f.write(str(x) + " ")
                     else:
                         f.write("\n" + str(x) + "\n")
        f.write("\n")
        f.close()
       
       # Close File
       f.close()
       
       while True:
          pass

# -------------------------    MAIN   -----------------------------------------  

start_fmcw()
print("finish")