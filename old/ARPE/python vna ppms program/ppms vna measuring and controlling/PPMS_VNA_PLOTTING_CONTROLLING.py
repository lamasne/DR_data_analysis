
"""
Created on Mon Oct 16 10:45:05 2023

@author: joan cucurull
"""
#--------- COMMENTS ---------------------
'''
It is recommendable to run the VNA_PLOTTING_MULTIMODE.py before running this to check the vna is working properly

The chamber must be purged and sealed manually with the PPMS software

You need the PPMS_VNA_AUXILIAR_SCRIPT.py and QDPPMSComms (folder) in the same folder as this script

!!!!!!!!!!!!!!!!!!!!!!The He level must be checked !!!!!!!!!!!!!!!!!!!!!! (don't run this program until this is done!)

The variables of the measurement can be changed below 
'''

import sys
import os
import time
import numpy as np

from QDPPMSComms.QDPPMSComms import QDPPMS

import threading

from PPMS_VNA_AUXILIAR_SCRIPT import vna_multimode


#----------- VARIABLES PPMS ------------------

ratioT = 5            #(K/min)
ratioB = 100          #(0e/second)
max_time_T = 2        #maximum time to stabilize the temperature (s)
waiting_time_T = 0        #time to wait after the temperature stabilisation (s)
temperatures = [48.20]    #list of temperatures at which we will measure (K)
steps_B = [90000]    #list of steps in the magnetic field sweep (just in case we want to do measurements at some specific magnetic fields).
                     #Units: 0e
'''
If we want to do a continuous magnetic field sweep with no steps: steps_B = [max_field] 

If we want to stop the sweep in some steps we have to write the steps in the list steps_B, 
and the sweep will finish at 0 0e after the last step. 
Example: steps_B = [10000, 20000, 30000, 20000, 10000] stops at 1, 2 and 3 tesla in the way up and down.
'''
#----------- VARIABLES VNA ------------------

freq1 = 7.9 #GHz (1st mode frequency)
ratio21=1.626 #freq2/freq1 measured at any temperature and field
ratio41= 1.714 #freq4/freq1 measured at any temperature and field

#---------- STARTING THE CONTROL OF THE PPMS ---------
qd = QDPPMS('pcd020e',3333)

#---------- CHANGING AND STABILISING TEMPERATURE ----------------------

for temp in temperatures:
    '''
    qd.setTemperature(temp, ratioT, qd.TEMP_FASTSETTLE)
    print(f'Setting {temp} K and 0 Oe \n Waiting...')
    start = time.time()
    qd.waitForStable(qd.STATUSTEMP, waiting_time_T, max_time_T)
    end = time.time()
    user_temperature, system_temperature = qd.getTemperature()
    field = qd.getField()
    print(f'User temperature = {user_temperature} K (Sample temperature = {system_temperature} K)')
    print(f'Field = {field} 0e')
    print(f'The ramp took {end - start:.3f} sec\n')
    '''

    ##############################################################################
    #################### VNA working #########################################
    # ----------- STARTING VNA ------------------------------
    print('Setting up the VNA')
    ## create an event to eventually stop the VNA
    event = threading.Event()
    ## create and configure a new thread
    thread = threading.Thread(target=vna_multimode, args=(freq1, ratio21, ratio41, event))

    ## start the VNA
    thread.start()
    time.sleep(16) #wating for the vna to be configurated

    #----------- MAGNETIC FIELD SWEEP ------------------------------

    print('Starting field sweep')
    for B in steps_B:
        qd.setField(B, ratioB, qd.FIELD_LINEAR, qd.FIELD_DRIVEN)
        #time.sleep(5)
        qd.waitForStable(qd.STATUSFIELD, 0, 3600)

    qd.setField(0, ratioB, qd.FIELD_LINEAR, qd.FIELD_PERSIST)
    qd.waitForStable(qd.STATUSFIELD, 0, 3600)

    # ----------- STOPPING VNA ------------------------------
    print('Stopping VNA thread...')
    event.set()
    # wait for the new thread to finish
    thread.join()
    print('VNA thread stopped')

    ##############################################################################
    #################### VNA not working ###########################################


    #---------- DEMAGNETIZATION -------------------------------
    print('starting demagnetisation')
    qd.setField(-10000, ratioB, qd.FIELD_LINEAR, qd.FIELD_DRIVEN)
    time.sleep(10000/ratioB)
    print('starting oscillation mode')
    qd.setField(0, ratioB, qd.FIELD_OSCILLATE, qd.FIELD_PERSIST)
    print('waiting for the field to be stable at 0 Oe')
    qd.waitForStable(qd.STATUSFIELD,0,300)
    



