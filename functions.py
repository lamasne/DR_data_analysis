import numpy as np
import pandas as pd


def DR_calculation(df):
    idx_reS21_max = df['re:S21'].idxmax()
    reS21_max = df['re:S21'].max()

    f1 = np.interp(-3.01, df['re:S21'].iloc[:idx_reS21_max+1] - reS21_max, df['freq[Hz]'].iloc[:idx_reS21_max+1])
    f2 = np.interp(-3.01, df['re:S21'].iloc[idx_reS21_max+1:] - reS21_max, df['freq[Hz]'].iloc[idx_reS21_max+1:])

    resonance = df.loc[idx_reS21_max, 'freq[Hz]']
    Qloaded = resonance/(f2 - f1)

    df['magnitudeS11'] = df['re:S11'] - ((df['re:S11'].iloc[0]+df['re:S11'].iloc[-1])*0.5)
    df['magnitudeS22'] = df['re:S22'] - ((df['re:S22'].iloc[0]+df['re:S22'].iloc[-1])*0.5)

    # S11resdb = df['magnitudeS11'].min()
    # S21resdb = df['re:S21'].max()
    S22resdb = df.loc[idx_reS21_max, 'magnitudeS22']

    print(df['magnitudeS11'].max())
    print(df['magnitudeS11'].max()/20)

    S11res = 10**(df['magnitudeS11'].max()/20)
    # S21res = 10**(df['re:S21'].max()/20)
    S22res = 10**(S22resdb/20)

    beta1 = (1-S11res)/(S11res+S22res)
    beta2 = (1-S22res)/(S11res+S22res)

    Qunloaded = Qloaded*(1+beta1+beta2)

    return [Qloaded, Qunloaded, resonance, beta1, beta2]


def read_touchstone(filename):
    with open(filename, 'r') as f:
        # Skip header lines and read the last line as column names:
        header_lines = []
        for line in f:
            if line.startswith('#') or line.startswith('!'):
                header_lines.append(line.strip())
            else:
                break
        column_names = header_lines[-1].split()[1:]
        
        # Read data skipping the header lines:
        data = np.loadtxt(filename, skiprows=5)
        
        # Construct DataFrame with column names:
        df = pd.DataFrame(data, columns=column_names)
    return df