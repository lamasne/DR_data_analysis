from functions import *


# Specific parameters
sample_name = "AMC_23_01_01"
DR_type = "single_mode_DR"
T_array = [50]
is_show_plots = 1
is_save_plots = 1
is_show_fitting = 0
is_save_fitting = 0

# General parameters
root_path = "data/" + DR_type + "/"
DR_params_path = root_path + 'DR_params/'
inputs_root_path = root_path + 'measurements/' + sample_name + '/' 
outputs_root_path = root_path + 'plots/' + sample_name + '/' 
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
        [inputs_path, outputs_path] = get_paths(inputs_root_path, outputs_root_path, T, mode)
        df_B_sweep = run(inputs_path, outputs_path, DR_params_path, mode, T, is_multimode, is_show_fitting, is_save_fitting)
        make_plots(df_B_sweep, is_show_plots, is_save_plots, outputs_path)
        print("Finished")