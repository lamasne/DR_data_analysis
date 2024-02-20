from functions import *
import pandas as pd
import numpy as np
import glob
import os

# pd.set_option('display.precision',12)

inputs_root_path = 'inputs/'
outputs_root_path = 'outputs/'

# Parameters (for now single values, in the future loop over all T, and f's)
sample_name = "FF DR001"
T = 50
f_str = '1'

inputs_path = inputs_root_path + str(T) + 'K/freq '+ f_str + '/'
# Get a list of all files matching the pattern
data_files = glob.glob(inputs_path + '*.s2p')

# Building parameters df
filenames = [os.path.basename(file) for file in data_files]
df = pd.DataFrame([[name] + name.split('_')[0:-1] for name in filenames], columns=['name', 'index', 'f', 'syst_T', 'DR_T', 'B'])
df['index'] = df['index'].astype(int)
df['f'] = df['f'].astype(int)
df['syst_T'] = df['syst_T'].astype(np.float64)
df['DR_T'] = df['DR_T'].astype(np.float64)
df['B'] = df['B'].astype(np.float64)
df.sort_values(inplace=True, by='index')
df.set_index('index', inplace=True)
del filenames # to make sure I only get it from ordered dataframe

# Calculate quality factor
for file in df['name']:
    data_df = read_touchstone(inputs_path + file)
    [Qloaded, Qunloaded, resonance, beta1, beta2] = DR_calculation(data_df)
    # break
    


