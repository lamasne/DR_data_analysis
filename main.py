from functions import *
import pandas as pd
import numpy as np
import glob
import os

# pd.set_option('display.precision',12)

inputs_root_path = "inputs/"
outputs_root_path = "outputs/"
sample_name = "FF DR001"

# Run parameters (for now single values, in the future loop over all T, and f's)
T = 50
f_str = "1"
inputs_path = inputs_root_path + str(T) + "K/freq " + f_str + "/"
df = get_run_profile(inputs_path, T, f_str)
# print(df)

# Calculate quality factor
for file in df["name"]:
    data_df = get_VNA_scan(inputs_path + file)
    [df_extended, Qloaded, Qunloaded, resonance, beta1, beta2] = DR_calculation(data_df)
    lorentzian_fitting(df_extended, Qloaded, resonance)
    break
