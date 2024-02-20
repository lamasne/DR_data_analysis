from functions import *
import pandas as pd
import numpy as np
import glob
import os


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

# Run parameters (for now single values, in the future loop over all T, and f's)
T = 50
f_str = "1"
inputs_path = inputs_root_path + str(T) + "K/freq " + f_str + "/"

# Get run profile from filenames
df = get_run_profile(inputs_path, T, f_str)

# Calculate quality factor, R_s and X_s
for file in df["name"]:
    data_df = get_f_sweep(inputs_path + file)
    [df_extended, Q_l, Q_u, res, beta1, beta2] = DR_calculation(data_df)
    [Q_l_fit, res_fit] = lorentzian_fitting(df_extended, Q_l, res)
    print(Q_l_fit, res_fit)
    # Q_u missing
    # X_S correction missing
    # ploting missing
    break
