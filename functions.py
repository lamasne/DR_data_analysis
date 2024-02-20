import numpy as np
import pandas as pd
import os
import glob
from lmfit import Parameters, Model
import matplotlib.pyplot as plt


def lorentzian_fitting(df, Q_loaded_init, res_init):
    magnitude = 10 ** (df["re:S21"].values / 20)
    S21res = magnitude.max()

    params = Parameters()
    params.add("a", value=S21res, min=S21res - 0.1, max=S21res + 0.1)
    params.add("b", value=Q_loaded_init, min=0, max=Q_loaded_init * (1.01))
    params.add("c", value=res_init, min=res_init - 1e8, max=res_init + 1e8)
    params.add("d", value=0, min=-10, max=10)
    params.add("e", value=0, min=-10, max=10)

    # Define fitting function
    def fun(x, a, b, c, d, e):
        return abs(a / (1 + 2 * 1j * b * ((x - c) / c)) + d + 1j * e)

    model = Model(fun)

    f = df["freq[Hz]"].values
    result_fitting = model.fit(magnitude, params, x=f, method="leastsq")
    best_fit_values = result_fitting.best_fit

    # Plot data points and the fitted curve
    plt.plot(f, magnitude, "x-", linewidth=1.2, label="Data")
    plt.plot(f, best_fit_values, "m", label="Fit")

    plt.show()

    # CONSIDERS IT BOTH UNLOADED AND LOADED IN MATLAB file
    Q_loaded_fit = result_fitting.params["b"].value
    resonance_fit = result_fitting.params["c"].value

    return [Q_loaded_fit, resonance_fit]


def DR_calculation(df):
    idx_reS21_max = df["re:S21"].idxmax()
    reS21_max = df["re:S21"].max()

    f1 = np.interp(
        -3.01,
        df["re:S21"].iloc[: idx_reS21_max + 1] - reS21_max,
        df["freq[Hz]"].iloc[: idx_reS21_max + 1],
    )
    f2 = np.interp(
        -3.01,
        df["re:S21"].iloc[idx_reS21_max + 1 :] - reS21_max,
        df["freq[Hz]"].iloc[idx_reS21_max + 1 :],
    )

    resonance = df.loc[idx_reS21_max, "freq[Hz]"]
    Qloaded = resonance / (f2 - f1)

    df["magnitudeS11"] = df["re:S11"] - (
        (df["re:S11"].iloc[0] + df["re:S11"].iloc[-1]) * 0.5
    )
    df["magnitudeS22"] = df["re:S22"] - (
        (df["re:S22"].iloc[0] + df["re:S22"].iloc[-1]) * 0.5
    )

    # S11resdb = df['magnitudeS11'].min()
    # S21resdb = df['re:S21'].max()
    S22resdb = df.loc[idx_reS21_max, "magnitudeS22"]

    S11res = 10 ** (df["magnitudeS11"].max() / 20)
    S21res = 10 ** (df["re:S21"].max() / 20)
    print(S21res)

    S22res = 10 ** (S22resdb / 20)

    beta1 = (1 - S11res) / (S11res + S22res)
    beta2 = (1 - S22res) / (S11res + S22res)

    Qunloaded = Qloaded * (1 + beta1 + beta2)

    return [df, Qloaded, Qunloaded, resonance, beta1, beta2]


def get_run_profile(inputs_path, T, f_str):
    # Get a list of all files VNA files
    data_files = glob.glob(inputs_path + "*.s2p")

    filenames = [os.path.basename(file) for file in data_files]
    df = pd.DataFrame(
        [[name] + name.split("_")[0:-1] for name in filenames],
        columns=["name", "index", "f", "syst_T", "DR_T", "B"],
    )
    df["index"] = df["index"].astype(int)
    df["f"] = df["f"].astype(int)
    df["syst_T"] = df["syst_T"].astype(np.float64)
    df["DR_T"] = df["DR_T"].astype(np.float64)
    df["B"] = df["B"].astype(np.float64)
    df.sort_values(inplace=True, by="index")
    df.set_index("index", inplace=True)

    return df


def get_VNA_scan(filename):
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
