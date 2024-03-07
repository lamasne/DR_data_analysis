from functions import *


# Specific params
# sample_name = "FF_23_12_01"
# DR_type = "multi_mode_5mm_DR"
sample_name = "AMC_23_01_01" # old one
DR_type = "single_mode_DR"
T_array = [50]
is_show_S21 = 1
is_show_fitting = 1

# General params
root_path = "inputs/" + DR_type + "/"
DR_params_path = root_path + 'DR_params/'
inputs_root_path = root_path + 'measurements/' + sample_name + '/' 
outputs_root_path = "outputs/"
DR_to_modes = {
    "single_mode_DR": ['TE011'], 
    "multi_mode_5mm_DR": ['TE011', 'TE012', 'TE013'], 
    "multi_mode_3mm_DR": ['TE011', 'TE021']
}

is_multimode = True if len(DR_to_modes[DR_type])>1 else False

df_ls = {}
for T in T_array:
    for mode in DR_to_modes[DR_type]:
        print(f'Started computation for T = {T}K and mode = {mode}')
        df_B_sweep = run(inputs_root_path, DR_params_path, mode, T, is_multimode, is_show_S21, is_show_fitting)
        show_plots(df_B_sweep)
        # df_ls[(T, mode)] = df_B_sweep
        print("Finished")