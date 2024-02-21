from functions import *
import pandas as pd
import numpy as np
import glob
import os
import matplotlib.pyplot as plt

### Left to do:
# check code outputs vs old
# Q_u calc
# Mix DR calc with fitting
# X_S correction
# ploting
# loop over T

inputs_root_path = "inputs/"
outputs_root_path = "outputs/"
sample_name = "FF DR001"
is_multimode = True

# Run parameters (for now single values, in the future loop over all T, and f's)
T = 50
# f_str = "old"
f_str = 'freq 2'
inputs_path = inputs_root_path + str(T) + "K/" + f_str + "/"

# Get run profile from filenames
df_B_sweep = get_B_sweep(inputs_path, T, f_str, is_multimode)

# Calculate quality factor, R_s and X_s
for file in df_B_sweep["name"]:
    df_sweep = get_f_sweep(inputs_path + file)
    [df_sweep_ext, Q_l, Q_u, res, beta1, beta2] = DR_calculation(df_sweep, is_multimode)
    [Q_l_fit, res_fit] = lorentzian_fitting(df_sweep_ext, Q_l, res, is_multimode)
    print(f'Quality factor is: {Q_l_fit}, Resonance is: {res_fit}')
    # Q_u missing
    # X_S correction missing
    break

# Ploting
# plt.plot(df_B_sweep['B'].values, df_B_sweep_ext['res_fit'])
