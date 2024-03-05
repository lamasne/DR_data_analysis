from functions import *

# Specific params
sample_name = "FF_23_12_01"
# sample_name = "AMC_23_01_01" # old one
T = 50

# General params
inputs_root_path = "inputs/"
DR_params_path = 'inputs/epsilon_all.txt'
outputs_root_path = "outputs/"
list_of_multi_modes = ['FF_23_12_01']
is_multimode = True if sample_name in list_of_multi_modes else False

# Get run profile from filenames
inputs_path = get_inputs_path(inputs_root_path, sample_name, T, is_multimode)
df_B_sweep = get_B_sweep(inputs_path, is_multimode)

# Calculate quality factors and resonant freqs for each field, and add them to df
nb_f_sweeps = len(df_B_sweep)
for loading_bar_var, i in enumerate(df_B_sweep.index):
    df_f_sweep = get_f_sweep(inputs_path + df_B_sweep.loc[i, 'name'])
    if is_multimode:
        df_f_sweep = format_data(df_f_sweep)
    [Q_l, Q_u, res, beta1, beta2] = DR_calculation(df_f_sweep)
    [Q_l_fit, res_fit] = lorentzian_fitting(df_f_sweep, Q_l, res)
    Q_u_fit = get_Q_u(Q_l_fit, beta1, beta2)
    df_B_sweep.loc[i, ['Q_l_fit', 'res_fit', 'Q_u_fit']] = Q_l_fit, res_fit, Q_u_fit

    # Print the progress bar
    progress = loading_bar_var / nb_f_sweeps * 100
    print(f'\rProgress: [{"#" * int(progress / 5):20}] {progress:.1f}%', end='', flush=True)

# Calculate surface impedance: R_S and X_S for each field, and add them to df
df_B_sweep = Z_S_calculation(DR_params_path, df_B_sweep, is_multimode, 0.1)

# Ploting
show_plots(df_B_sweep)
