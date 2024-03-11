import numpy as np
import pandas as pd
import re # regex
import cmath
import math
import os
import glob
from lmfit import Parameters, minimize
import matplotlib.pyplot as plt
from scipy.interpolate import interp1d


def make_plots(df_B_sweep, is_show_plots, is_save_plots, outputs_path):
    # To plot in tex
    # plt.rcParams['text.usetex'] = True
    B_values = df_B_sweep['B'].values
    turning_point_idx = np.argmax(B_values)
    ramp_up = np.arange(turning_point_idx+1)
    B_values = df_B_sweep['B'].values
    ramp_down = np.arange(turning_point_idx+1,len(B_values))

    # Unit conversion
    df_B_sweep['res_fit'] = df_B_sweep['res_fit']/1e9
    B_values = B_values/1e4
    df_B_sweep['R_S'] = 1e3*df_B_sweep['R_S']
    df_B_sweep['X_S'] = 1e3*df_B_sweep['X_S']

    plt.figure()  
    plt.xlabel('B (T)')
    plt.plot(B_values[ramp_up],  df_B_sweep['res_fit'].values[ramp_up], 
             B_values[ramp_down],  df_B_sweep['res_fit'].values[ramp_down],
             )
    plt.legend(['ramp-up', 'ramp-up'])
    plt.ylabel('$f_{res}$ (GHz)')
    if is_save_plots:
        plt.savefig(os.path.join(outputs_path, "f(B).png"))

    plt.figure()  
    plt.xlabel('B (T)')
    plt.plot(B_values[ramp_up],  df_B_sweep['Q_l_fit'].values[ramp_up], 
             B_values[ramp_up],  df_B_sweep['Q_u_fit'].values[ramp_up],
             B_values[ramp_down],  df_B_sweep['Q_l_fit'].values[ramp_down],
             B_values[ramp_down],  df_B_sweep['Q_u_fit'].values[ramp_down]
             )
    plt.legend(['$Q_l$ ramp-up', '$Q_u$ ramp-up', '$Q_u$ ramp-down', '$Q_u$ ramp-down'])
    plt.ylabel('Q')
    if is_save_plots:
        plt.savefig(os.path.join(outputs_path, "Q(B).png"))

    plt.figure()  
    plt.xlabel('B (T)')
    plt.plot(B_values[ramp_up], df_B_sweep['R_S'].values[ramp_up],
             B_values[ramp_down], df_B_sweep['R_S'].values[ramp_down]
             )
    plt.legend(['ramp-up', 'ramp-down'])
    plt.ylabel(r'$R_S$ ($m\Omega$)')
    if is_save_plots:
        plt.savefig(os.path.join(outputs_path, "R_s(B).png"))

    plt.figure()  
    plt.xlabel('B (T)')
    plt.plot(B_values[ramp_up], df_B_sweep['X_S'].values[ramp_up],
             B_values[ramp_down], df_B_sweep['X_S'].values[ramp_down]
             )
    plt.legend(['ramp-up', 'ramp-down'])
    plt.ylabel(r'$X_S$ ($m\Omega$)')
    if is_save_plots:
        plt.savefig(os.path.join(outputs_path, "X_s(B).png"))
    
    if is_show_plots:
        plt.show()
    else:
        plt.close('all')


def run(inputs_path, outputs_path, DR_params_path, mode, T, data_format, is_polar, is_multimode, is_show_fitting, is_save_fitting):
    # Get run profile from filenames
    df_B_sweep = get_B_sweep(inputs_path, data_format, is_multimode)

    # Calculate quality factors and resonant freqs for each field, and add them to df
    nb_f_sweeps = len(df_B_sweep)
    for idx, i in enumerate(df_B_sweep.index):
        df_f_sweep = get_f_sweep(inputs_path + df_B_sweep.loc[i, 'name'])
        if not is_polar:
            df_f_sweep = format_data(df_f_sweep)
        [Q_l, Q_u, res, beta1, beta2] = DR_calculation(df_f_sweep)
        [Q_l_fit, res_fit] = lorentzian_fitting(df_f_sweep, Q_l, res, is_show_fitting, is_save_fitting, outputs_path, idx)
        Q_u_fit = get_Q_u(Q_l_fit, beta1, beta2)
        df_B_sweep.loc[i, ['Q_l_fit', 'res_fit', 'Q_u_fit']] = Q_l_fit, res_fit, Q_u_fit

        # Print the progress bar
        progress = idx / nb_f_sweeps * 100
        print(f'\rProgress: [{"#" * int(progress / 5):20}] {progress:.1f}%', end='', flush=True)

    # Calculate surface impedance: R_S and X_S for each field, and add them to df
    df_B_sweep = Z_S_calculation(DR_params_path, df_B_sweep, mode, is_multimode, 0.1)
    return df_B_sweep

def Z_S_calculation(DR_params_path, df_B_sweep, mode, is_multimode, correction_factor = 0):   
    # the correction factor accounts for the unknown permittivity of rutile
    ref_index = df_B_sweep.index[0]

    # For single mode we have everything as a fun of T
    if not is_multimode:
        column_names = ['DR_T', 'eps_r', 'G_f', 'tau_l']
        df =  pd.read_csv(DR_params_path + 'DR_params.txt', delimiter='\t', header=1, names=column_names)
        df = df.astype(np.float64)
        df.sort_values(inplace=True, by="DR_T")

        # eps_r_fun = interp1d(df['DR_T'], df['eps_r'], kind='cubic')
        G_f_fun = interp1d(df['DR_T'], df['G_f'], kind='cubic')
        tau_l_fun = interp1d(df['DR_T'], df['tau_l'], kind='cubic')
        eps_r_fun = interp1d(df['DR_T'], df['eps_r'], kind='cubic')

        # Reference for X_s computation
        T_ref =  df_B_sweep.loc[ref_index, 'DR_T']
        res_fit_ref = df_B_sweep.loc[ref_index, 'res_fit']
        eps_r_ref = eps_r_fun(T_ref)

        for i in df_B_sweep.index:
            T = df_B_sweep.loc[i, 'DR_T']
            Q_u = df_B_sweep.loc[i, 'Q_u_fit']
            res_fit = df_B_sweep.loc[i, 'res_fit']
            G_f = G_f_fun(T)
            df_B_sweep.loc[i, 'R_S'] = (G_f/2) * ((1/Q_u) - tau_l_fun(T))        
            df_B_sweep.loc[i, 'X_S'] = (-1) * G_f * (((res_fit - res_fit_ref) / res_fit_ref) + (correction_factor * (eps_r_fun(T) - eps_r_ref) / eps_r_ref))

    # For multi-mode, G_f depends on mode and f(T), eps_r on T, tau_l on mode and T
    else:
        df_G_f = pd.read_csv(DR_params_path + 'Surface Geometrical Factor ' + mode +'.txt', delimiter='\t', header=0, names=['f', 'G_f'], dtype=np.float64)
        G_f_fun = interp1d(df_G_f['f'], df_G_f['G_f'], kind='cubic')
        df_tau_l = pd.read_csv(DR_params_path + 'Tangent Loss.txt', delimiter='\t', header=0, dtype=np.float64)
        tau_l_fun = interp1d(df_tau_l['T'], df_tau_l[mode], kind='cubic')
        df_eps_r = pd.read_csv(DR_params_path + 'Relative Permittivity.txt', delimiter='\t', header=0, names=['T', 'eps_r'], dtype=np.float64)
        eps_r_fun = interp1d(df_eps_r['T'], df_eps_r['eps_r'], kind='cubic')
        
        # Reference for X_s computation
        T_ref =  df_B_sweep.loc[ref_index, 'DR_T']
        res_fit_ref = df_B_sweep.loc[ref_index, 'res_fit']
        eps_r_ref = eps_r_fun(T_ref)

        for i in df_B_sweep.index:
            T = df_B_sweep.loc[i, 'DR_T']
            Q_u = df_B_sweep.loc[i, 'Q_u_fit']
            res_fit = df_B_sweep.loc[i, 'res_fit']
            try:
                G_f = G_f_fun(res_fit)
            except ValueError as e:
                print('resonance is not within known values of geometrical factor, G_f put to almost zero')
                G_f = 0.1
            df_B_sweep.loc[i, 'R_S'] = (G_f/2) * ((1/Q_u) - tau_l_fun(T))
            df_B_sweep.loc[i, 'X_S'] = (-1) * G_f * (((res_fit - res_fit_ref) / res_fit_ref) + (correction_factor * (eps_r_fun(T) - eps_r_ref) / eps_r_ref))

    return df_B_sweep

def lorentzian_fitting(sweep_df, Q_l_init, res_init, is_show_fitting, is_save_fitting, outputs_path, idx):
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
    plt.figure()
    plt.xlabel('f (Hz)')
    # Logarithmic
    plt.ylabel('S21 magnitude (log)')
    plt.plot(f, (sweep_df["db:S21"]), "x-", linewidth=1.2, label="Data")
    plt.plot(f, (20 * np.log10(abs(S21_formula(result_fitting.params, f)))), "m-", label="Fit")
    # Linear
    # plt.ylabel('S21 magnitude (lin)')
    # plt.plot(f, abs(S21_lin), "x-", linewidth=1.2, label="Data")
    # plt.plot(f, abs(S21_formula(result_fitting.params, f)), "m-", label="Fit")        
    plt.legend(['S21 data', 'S21 fitting'])

    if is_save_fitting:
        os.makedirs(outputs_path + 'S21/', exist_ok=True)
        plt.savefig(os.path.join(outputs_path + 'S21/', f"S21_fitting_{idx:04d}.png"))

    if is_show_fitting:
        plt.show()
    else:
        plt.close()

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
        raise ValueError(" Peak was not high enough to define resonnance freq")

    res = df.loc[idx_res_S21, "freq[Hz]"]
    Q_l = res / (f2 - f1)

    df["magnitudeS11"] = df["db:S11"] - (
        (df["db:S11"].iloc[0] + df["db:S11"].iloc[-1]) * 0.5
    )
    df["magnitudeS22"] = df["db:S22"] - (
        (df["db:S22"].iloc[0] + df["db:S22"].iloc[-1]) * 0.5
    )


    S11_res_lin = 10 ** (df["magnitudeS11"].max() / 20)
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
        if res is None:
            raise ValueError("The data is already in polar representation. Change the is_polar variable to True")
        else:
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


def get_B_sweep(inputs_path, data_format, is_multimode):
    # Get a list of all files VNA files
    data_files = glob.glob(inputs_path + "*.s2p")

    filenames = [os.path.basename(file) for file in data_files]

    format_keys = data_format.keys()
    # Check that the format was well specified
    if len(format_keys) != len(filenames[0].split("_")):
        raise ValueError("The format specified does not match that of the files")

    values_arrays = []
    for name in filenames:
        values_array = {}
        line = name.split("_")
        values_array['name'] = name
        for i, key in enumerate(format_keys):
            valid_range = data_format[key]
            if valid_range[1] == -1:
                values_array[key] = line[i][valid_range[0]:]
            else:
                values_array[key] = line[i][valid_range[0]:valid_range[1]]
        values_arrays.append(values_array)
    df = pd.DataFrame(values_arrays)        

    print(df)
    # if not is_multimode:
    #     values_arrays = []
    #     for index, name in enumerate(filenames):
    #         values_array = [name] + name.split("_")
    #         values_array[1] = values_array[1]
    #         values_array[2] = values_array[2][2:]
    #         values_array[3] = values_array[3][2:]
    #         values_array[4] = values_array[4][1:-4]
    #         values_arrays.append(values_array)
    #     df = pd.DataFrame(
    #         values_arrays,
    #         columns=["name", "index", "syst_T", "DR_T", "B"],
    #     )
    # else:
    #     df = pd.DataFrame(
    #         [[name] + name.split("_")[0:-1] for name in filenames],
    #         columns=["name", "index", "f", "syst_T", "DR_T", "B"],
    #     )

    df["index"] = df["index"].astype(int)
    if is_multimode: df["f"] = df["f"].astype(int)
    df["syst_T"] = df["syst_T"].astype(np.float64)
    df["DR_T"] = df["DR_T"].astype(np.float64)
    df["B"] = df["B"].astype(np.float64)    
    df.sort_values(inplace=True, by="index")
    df.set_index("index", inplace=True)

    return df

def get_paths(inputs_root_path, outputs_root_path, T, mode):
    inputs_path =  inputs_root_path + str(T) + "K/" + mode + '/'
    outputs_path = outputs_root_path + str(T) + "K/" + mode + '/'
    # Create output path if do not exist
    os.makedirs(outputs_path, exist_ok=True)
    return [inputs_path, outputs_path]