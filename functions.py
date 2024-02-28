import numpy as np
import pandas as pd
import re # regex
import cmath
import math
import os
import glob
from lmfit import Parameters, Model, minimize
import matplotlib.pyplot as plt


def lorentzian_fitting(sweep_df, Q_l_init, res_init):
    S21_lin = 10 ** (sweep_df["db:S21"].values / 20)
    S21_res_lin = S21_lin.max()
    f = sweep_df["freq[Hz]"].values

    params = Parameters()
    params.add("a", value=S21_res_lin, min=S21_res_lin - 0.1, max=S21_res_lin + 0.1)
    params.add("Q_l", value=Q_l_init, min=0, max=Q_l_init * (1.01))
    params.add("res", value=res_init, min=res_init - 1e8, max=res_init + 1e8)
    params.add("d", value=0, min=-10, max=10)
    params.add("e", value=0, min=-10, max=10)

    # Define fitting function
    def S21_formula(params, f):
        a = params['a']
        Q_l = params['Q_l']
        res = params['res']
        d = params['d']
        e = params['e']
        return abs(a / (1 + 2 * 1j * Q_l * ((f - res) / res)) + d + 1j * e)
    
    def residual(params, f, S21_meas):
        return S21_meas - S21_formula(params, f)
    
    result_fitting = minimize(residual, params, args=(f, S21_lin), method="leastsq")
    
    ## Plot data points and the fitted curve
    
    # Linear
    # plt.plot(f, abs(S21_lin), "x-", linewidth=1.2, label="Data")
    # plt.plot(f, abs(S21_formula(result_fitting.params, f)), "m-", label="Fit")
    
    # Logarithmic
    # plt.plot(f, (sweep_df["db:S21"]), "x-", linewidth=1.2, label="Data")
    # plt.plot(f, (20 * np.log10(abs(S21_formula(result_fitting.params, f)))), "m-", label="Fit")
    
    # plt.show()

    # CONSIDERS IT BOTH UNLOADED AND LOADED IN MATLAB file
    Q_l_fit = result_fitting.params["Q_l"].value
    res_fit = result_fitting.params["res"].value

    return [Q_l_fit, res_fit]

def get_Q_u(Q_l, beta1, beta2):
    return Q_l * (1 + beta1 + beta2)

def DR_calculation(df):
    idx_res_S21 = df["db:S21"].idxmax()
    res_S21 = df["db:S21"].max()

    f1 = np.interp(
        -3.01,
        df["db:S21"].iloc[: idx_res_S21 + 1] - res_S21,
        df["freq[Hz]"].iloc[: idx_res_S21 + 1],
    )
    # right branch of S21 needs to be read from finish to start for interp to work
    f2 = np.interp(
        -3.01,
        list(reversed(df["db:S21"].iloc[idx_res_S21 + 1 :].values - res_S21)),
        list(reversed(df["freq[Hz]"].iloc[idx_res_S21 + 1 :].values)),
    )

    if f1 == df["freq[Hz]"].iloc[0] or f2 ==df["freq[Hz]"].iloc[-1]:
        print('IMPORTANT: Peak was not high enough to define resonnance freq')

    res = df.loc[idx_res_S21, "freq[Hz]"]
    Q_l = res / (f2 - f1)

    df["magnitudeS11"] = df["db:S11"] - (
        (df["db:S11"].iloc[0] + df["db:S11"].iloc[-1]) * 0.5
    )
    df["magnitudeS22"] = df["db:S22"] - (
        (df["db:S22"].iloc[0] + df["db:S22"].iloc[-1]) * 0.5
    )


    S11_res_lin = 10 ** (df["magnitudeS11"].max() / 20)
    # S21_res_lin = 10 ** (df["db:S21"].max() / 20)

    S22_res_lin = 10 ** (df.loc[idx_res_S21, "magnitudeS22"] / 20)

    beta1 = (1 - S11_res_lin) / (S11_res_lin + S22_res_lin)
    beta2 = (1 - S22_res_lin) / (S11_res_lin + S22_res_lin)

    Q_u = get_Q_u(Q_l, beta1, beta2)

    return [Q_l, Q_u, res, beta1, beta2]

def format_data(df):
    # convert to polar
    params = []
    for col in df.columns:
        res = re.search('^re:(.*)', col)
        if res is not None:
            params.append(res.group(1))
    
    nb_freq = len(df['freq[Hz]'])
    df_new = pd.DataFrame({'freq[Hz]': df['freq[Hz]']})
    for param in params: 
        reals = df['re:' + param].values
        imags = df['im:' + param].values
        magnitude_lin = np.zeros(nb_freq)
        magnitude_db = np.zeros(nb_freq)
        argument_rad = np.zeros(nb_freq)
        argument_deg = np.zeros(nb_freq)

        for i in range(nb_freq):
            [magnitude_lin[i], argument_rad[i]] = cmath.polar(complex(reals[i], imags[i]))
            magnitude_db[i] = 20 * math.log10(magnitude_lin[i])
            argument_deg[i] = math.degrees(argument_rad[i])

        df_new['db:' + param] = magnitude_db
        df_new['ang:' + param] = argument_deg

    return df_new

def get_f_sweep(filename):
    with open(filename, "r") as f:
        # Skip header lines and read the last line as column names:
        header_lines = []
        for line in f:
            if line.startswith("#") or line.startswith("!"):
                header_lines.append(line.strip())
            else:
                break
        column_names = header_lines[-1].split()[1:]

        # Read data skipping the header lines:
        data = np.loadtxt(filename, skiprows=5)

        # Construct DataFrame with column names:
        df = pd.DataFrame(data, columns=column_names)
    return df


def get_B_sweep(inputs_path, is_multimode):
    # Get a list of all files VNA files
    data_files = glob.glob(inputs_path + "*.s2p")

    filenames = [os.path.basename(file) for file in data_files]

    # # Detect if old or new format
    # if len(filenames[1].split("_")) == 4:
    #     is_old_format = True

    if not is_multimode:
        values_arrays = []
        for index, name in enumerate(filenames):
            values_array = [name] + name.split("_")
            values_array[1] = values_array[1]
            values_array[2] = values_array[2][2:]
            values_array[3] = values_array[3][2:]
            values_array[4] = values_array[4][1:-4]
            values_arrays.append(values_array)
        df = pd.DataFrame(
            values_arrays,
            columns=["name", "index", "syst_T", "DR_T", "B"],
        )
    else:
        df = pd.DataFrame(
            [[name] + name.split("_")[0:-1] for name in filenames],
            columns=["name", "index", "f", "syst_T", "DR_T", "B"],
        )
    df["index"] = df["index"].astype(int)
    if is_multimode: df["f"] = df["f"].astype(int)
    df["syst_T"] = df["syst_T"].astype(np.float64)
    df["DR_T"] = df["DR_T"].astype(np.float64)
    df["B"] = df["B"].astype(np.float64)
    df.sort_values(inplace=True, by="index")
    df.set_index("index", inplace=True)

    return df

def get_inputs_path(inputs_root_path, sample_name, is_multimode):
    if is_multimode:
        f_str = 'multi-mode/freq_1/'
    else:
        f_str = 'single-mode/'
    return  inputs_root_path + sample_name + '/' + str(T) + "K/" + f_str
