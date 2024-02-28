from functions import *
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

### Left to do:
# R_S and X_S calculation


# Specific params
# sample_name = "FF_23_12_01"
sample_name = "AMC_23_01_01" # old one
T = 50

# General params
inputs_root_path = "inputs/"
outputs_root_path = "outputs/"
list_of_multi_modes = ['FF_23_12_01']
is_multimode = True if sample_name in list_of_multi_modes else False

# Get run profile from filenames
inputs_path = get_inputs_path(inputs_root_path, sample_name, is_multimode)
df_B_sweep = get_B_sweep(inputs_path, is_multimode)
print(df_B_sweep)

# Calculate quality factor and resonant freqs -- WHAT ABOUT R_s and X_s ? 
nb_f_sweeps = len(df_B_sweep)
Q_l_fit_array = np.zeros(nb_f_sweeps)
res_fit_array = np.zeros(nb_f_sweeps)
for i, df_idx in enumerate(df_B_sweep.index):
    df_f_sweep = get_f_sweep(inputs_path + df_B_sweep.loc[df_idx, 'name'])
    if is_multimode:
        df_f_sweep = format_data(df_f_sweep)
    [Q_l, Q_u, res, beta1, beta2] = DR_calculation(df_f_sweep)
    [Q_l_fit_array[i], res_fit_array[i]] = lorentzian_fitting(df_f_sweep, Q_l, res)

    # R_s and X_s calculation

# Calculate unloaded quality factor
Q_u_fit_array = np.zeros(nb_f_sweeps)
for i, Q_l_fit in enumerate(Q_l_fit_array):
    Q_u_fit_array[i] = get_Q_u(Q_l_fit, beta1, beta2)


# Ploting
B_values = df_B_sweep['B'].values
plt.plot(B_values, Q_l_fit_array, B_values, Q_u_fit_array)
plt.xlabel('B field - Oe')
plt.legend(['Q_l', 'Q_u'])
plt.show()