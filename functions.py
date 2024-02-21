import numpy as np
import pandas as pd
import scipy
import os
import glob
from lmfit import Parameters, Model, minimize
import matplotlib.pyplot as plt


def lorentzian_fitting(sweep_df, Q_l_init, res_init, multimode = False):
    real_dB_name = 're' if multimode else 'db'  

    S21_lin = 10 ** (sweep_df[real_dB_name + ":S21"].values / 20)
    S21_res_lin = S21_lin.max()
    f = sweep_df["freq[Hz]"].values

    # 1
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
    
    # Plot data points and the fitted curve
    plt.plot(f, abs(S21_lin), "x-", linewidth=1.2, label="Data")
    # plt.plot(f, abs(sweep_df[real_dB_name + ":S21"]), "x-", linewidth=1.2, label="Data")
    plt.plot(f, abs(S21_formula(result_fitting.params, f)), "m-", label="Fit")

    plt.show()

    # CONSIDERS IT BOTH UNLOADED AND LOADED IN MATLAB file
    Q_l_fit = result_fitting.params["Q_l"].value
    res_fit = result_fitting.params["res"].value

    return [Q_l_fit, res_fit]


def DR_calculation(df, multimode = False):
    real_dB_name = 're' if multimode else 'db'  
    idx_reS21_max = df[real_dB_name + ":S21"].idxmax()
    reS21_max = df[real_dB_name + ":S21"].max()

    # # Sort x and y based on the values of x
    # sorted_indices = np.argsort(x)
    # sorted_x = x[sorted_indices]
    # sorted_y = y[sorted_indices]

    f1 = np.interp(
        -3.01,
        df[real_dB_name + ":S21"].iloc[: idx_reS21_max + 1] - reS21_max,
        df["freq[Hz]"].iloc[: idx_reS21_max + 1],
    )
    # right branch of S21 needs to be read from finish to start for interp to work
    f2 = np.interp(
        -3.01,
        list(reversed(df[real_dB_name + ":S21"].iloc[idx_reS21_max + 1 :].values - reS21_max)),
        list(reversed(df["freq[Hz]"].iloc[idx_reS21_max + 1 :].values)),
    )

    if f1 == df["freq[Hz]"].iloc[0] or f2 ==df["freq[Hz]"].iloc[-1]:
        print('IMPORTANT: Peak was not high enough to define resonnance freq')

    res = df.loc[idx_reS21_max, "freq[Hz]"]
    Q_l = res / (f2 - f1)

    df["magnitudeS11"] = df[real_dB_name + ":S11"] - (
        (df[real_dB_name + ":S11"].iloc[0] + df[real_dB_name + ":S11"].iloc[-1]) * 0.5
    )
    df["magnitudeS22"] = df[real_dB_name + ":S22"] - (
        (df[real_dB_name + ":S22"].iloc[0] + df[real_dB_name + ":S22"].iloc[-1]) * 0.5
    )

    # S11_res_dB = df['magnitudeS11'].min()
    # S21_res_dB = df['re:S21'].max()
    S22_res_dB = df.loc[idx_reS21_max, "magnitudeS22"]

    S11_res_lin = 10 ** (df["magnitudeS11"].max() / 20)
    S21_res_lin = 10 ** (df[real_dB_name + ":S21"].max() / 20)

    S22_res_lin = 10 ** (S22_res_dB / 20)

    beta1 = (1 - S11_res_lin) / (S11_res_lin + S22_res_lin)
    beta2 = (1 - S22_res_lin) / (S11_res_lin + S22_res_lin)

    Q_u = Q_l * (1 + beta1 + beta2)

    return [df, Q_l, Q_u, res, beta1, beta2]


def get_B_sweep(inputs_path, T, f_str, multimode=False):
    # Get a list of all files VNA files
    data_files = glob.glob(inputs_path + "*.s2p")

    filenames = [os.path.basename(file) for file in data_files]
    if not multimode:
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
    if multimode: df["f"] = df["f"].astype(int)
    df["syst_T"] = df["syst_T"].astype(np.float64)
    df["DR_T"] = df["DR_T"].astype(np.float64)
    df["B"] = df["B"].astype(np.float64)
    df.sort_values(inplace=True, by="index")
    df.set_index("index", inplace=True)

    return df


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
