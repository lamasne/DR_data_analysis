"""
Algorithm for Resonator Parameter Extraction from Symmetrical and Asymmetrical Transmission Responses
by Patrick Krkotic, Queralt Gallardo, Nikki Tagdulang, Montse Pont and Joan M. O'Callaghan, 2021

Code written by Queralt Gallardo and Patrick Krkotic
arpe-edu@outlook.de

Version 1.0.0
Contributors:

Developed on Python 3.7.7
"""

import numpy as np
import math
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

from scipy.signal import savgol_filter

def fano(f, A, q, f0, g, H, y0):
    # Define the Fano line shape function
    epsilon = (f - f0) / g
    return A * ((epsilon + q)**2) / (1 + epsilon**2) * H + y0

def fano_fitting(X, Y):
    p0 = [1.0, 1.0, 0.5, 0.03, 0.5, 0.01]
    popt = None
    try:
        popt, pcov = curve_fit(fano, X, Y, p0=p0)
    except Exception as e:
        p0 = [1.0, 0., 0.7, 0.2, 1.3, 0.]
        try:
            popt, pcov = curve_fit(fano, X, Y, p0=p0)
        except Exception as e:
            print('Could not perform Fano fitting')
    return popt


# def correct_lin_trend_phase(Y_framed, resol):
#     size = len(Y_framed)//resol
#     popt = None
#     i = 0
#     plt.figure()
#     while popt is None and (i+1)*size < len(Y_framed)//2:
#         Y_framed_cor = Y_framed.copy()
#         # Correct left branch
#         x_cor = np.linspace(0,1,(i+1)*size)
#         coef_lin_left= np.polyfit(x_cor, Y_framed[:(i+1)*size], 1)[0]
#         x_cor_max = np.linspace(0,1.0/(i+1),size)
#         coef_lin_left_max = [np.polyfit(x_cor_max, Y_framed[j*size:(j+1)*size], 1)[0] for j in range(i)]
#         a_lt = coef_lin_left_max.copy()
#         a_lt.append(coef_lin_left)
#         a_l = a_lt[np.argmin(np.abs(a_lt))]       
#         Y_framed_cor[:(i+1)*size] = Y_framed[:(i+1)*size].copy() - a_l*(x_cor-x_cor[-1])
#         # Correct right branch
#         coef_lin_right= np.polyfit(x_cor, Y_framed[len(Y_framed)-(i+1)*size:], 1)[0]
#         coef_lin_right_min = [np.polyfit(x_cor_max, Y_framed[len(Y_framed)-(j+1)*size:len(Y_framed)-j*size], 1)[0] for j in range(i)]
#         a_rt = coef_lin_right_min.copy()
#         a_rt.append(coef_lin_right)
#         a_r =  a_rt[np.argmin(np.abs(a_rt))]
#         Y_framed_cor[len(Y_framed)-(i+1)*size:] = Y_framed[len(Y_framed)-(i+1)*size:].copy() - a_r*x_cor                        
#         # Y_framed[:(i+1)*size] = Y_framed[(i+1)*size+1]
#         # Y_framed[len(Y_framed)-(i+1)*size:] = Y_framed[len(Y_framed)-(i+1)*size-1]
#         plt.plot(np.linspace(0,1,len(Y_framed_cor)), Y_framed_cor, 'b-')
#         plt.show()
#         popt = fano_fitting(x_cor, Y_framed_cor)
#         i+=1
#     if popt is not None:
#         print('it worked!')
#     return popt

# def correct_lin_trend_phase(Y_framed):
#     '''Requires framed Y, works because plot must be symmetrical'''
#     X = np.arange(len(Y_framed))
#     Y_s = savgol_filter(Y_framed, 11, 2)
#     dy_dx = np.gradient(Y_s, X)
#     lin_trend = np.mean(dy_dx)
#     Y_cor = Y_framed.copy() - lin_trend*(X - X[len(Y_framed)//2])                    
#     plt.figure()  
#     plt.title('Correction lin trend')
#     plt.plot(X, Y_framed, 'b-')
#     plt.plot(X, Y_cor, 'r-')
#     plt.show()
#     return Y_cor

def new_correct_lin_trend_phase(Y, tol=1.5):
    # softener = 0.5
    softener = 1
    X = np.arange(len(Y))
    Y_s = savgol_filter(Y, 25, 2)
    dy_dx = np.gradient(Y_s, X)
    dy_dx = savgol_filter(dy_dx, 31, 2)
    idx_l_end = 6
    while abs(dy_dx[idx_l_end]/np.mean(dy_dx[:5])) < tol:
        idx_l_end += 1
    x_l = np.arange(idx_l_end)
    coeff_l = np.polyfit(
        x_l,
        Y_s[:idx_l_end],
        1
    )
    idx_r_end = len(Y)-6
    while abs(dy_dx[idx_r_end]/np.mean(dy_dx[-5:])) < tol:
        idx_r_end -= 1
    x_r = np.arange(idx_r_end, len(Y_s))
    coeff_r = np.polyfit(
        x_r,
        Y_s[idx_r_end:],
        1
    )
    plt.figure()  
    plt.title('Finding the edges')
    plt.plot(X, Y, 'b-')
    plt.plot(x_l, Y_s[:idx_l_end], 'r-')
    plt.plot(x_r, Y_s[idx_r_end:], 'r-')
    lin_trend = softener*(coeff_l[0] + coeff_r[0])/2.0
    Y_cor = Y.copy() - lin_trend*(X - X[len(Y)//2])                    
    plt.figure()  
    plt.title('Correction linear trend')
    plt.plot(X, Y, 'b-')
    plt.plot(X, Y_cor, 'r-')
    plt.show()
    return Y_cor

# def new_correct_lin_trend_phase(Y, tol=2e-3):
#     X = np.arange(len(Y))
#     # Find ends size
#     peaks_idxs = obtain_peaks_idxs(Y)
#     Y_s = savgol_filter(Y, 25, 2)
#     dy_dx = np.gradient(np.gradient(Y_s, X), X)
#     dy_dx = savgol_filter(dy_dx, 31, 2)
#     norm_tol = abs(tol*max(dy_dx))
#     idx_l_end = min(peaks_idxs)
#     while abs(dy_dx[0] - dy_dx[idx_l_end]) > norm_tol:
#         idx_l_end -= 1
#     x_l = np.arange(idx_l_end)
#     coeff_l = np.polyfit(
#         x_l,
#         Y_s[:idx_l_end],
#         1
#     )
#     idx_r_end = max(peaks_idxs)
#     while abs(dy_dx[-1] - dy_dx[idx_r_end]) > norm_tol:
#         idx_r_end += 1
#     x_r = np.arange(idx_r_end, len(Y_s))
#     coeff_r = np.polyfit(
#         x_r,
#         Y_s[idx_r_end:],
#         1
#     )
#     plt.figure()  
#     plt.title('Finding the edges')
#     plt.plot(X, Y, 'b-')
#     plt.plot(x_l, Y_s[:idx_l_end], 'r-')
#     plt.plot(x_r, Y_s[idx_r_end:], 'r-')
#     lin_trend = (coeff_l[0] + coeff_r[0])/2.0
#     Y_cor = Y.copy() - lin_trend*(X - X[len(Y)//2])                    
#     plt.figure()  
#     plt.title('Correction linear trend')
#     plt.plot(X, Y, 'b-')
#     plt.plot(X, Y_cor, 'r-')
#     plt.show()
#     return Y_cor

# def OLD_correct_lin_trend_phase(Y, resol):
#     '''Requires framed Y, works because plot must be symmetrical'''
#     X = np.arange(len(Y))
#     chunk_size = len(Y)//resol 
#     ends_size = len(Y)//3//chunk_size
#     coef_lin_left_by_chunk = [np.polyfit(np.linspace(j*chunk_size,(j+1)*chunk_size,chunk_size), Y[j*chunk_size:(j+1)*chunk_size], 1)[0] for j in range(ends_size)]
#     coef_lin_right_by_chunk = [np.polyfit(np.linspace(len(Y)-(j+1)*chunk_size, len(Y)-j*chunk_size,chunk_size), Y[len(Y)-(j+1)*chunk_size:len(Y)-j*chunk_size], 1)[0] for j in range(ends_size)]
#     a = coef_lin_left_by_chunk.copy() + coef_lin_right_by_chunk.copy() 
#     lin_trend = np.mean(a)
#     Y_cor = Y.copy() - lin_trend*(X - X[len(Y)//2])                    
#     plt.figure()  
#     plt.title('Correction linear trend')
#     plt.plot(X, Y, 'b-')
#     plt.plot(X, Y_cor, 'r-')
#     plt.show()
#     return Y_cor

def frame_S_param_phase(Y, tol = 0.1):
    # Get the center x - works for curve with one and 2 symetrical peaks
    X = np.arange(len(Y))
    peaks_idxs = obtain_peaks_idxs(Y, tol)
    idx_Y_mid = int(np.mean(peaks_idxs))
    nb_pts_end_curve = min([idx_Y_mid, len(Y)-idx_Y_mid])
    Y_framed = Y[idx_Y_mid-nb_pts_end_curve:idx_Y_mid+nb_pts_end_curve].copy()
    # plt.figure()
    # plt.title('Framing of phase')
    # plt.plot(Y)
    # plt.plot(np.linspace(idx_Y_mid-nb_pts_end_curve, idx_Y_mid+nb_pts_end_curve, len(Y_framed)), Y_framed)
    # plt.show()
    return Y_framed

def obtain_peaks_idxs(Y, tol=0.1):
    X = np.arange(len(Y))
    Y_s = savgol_filter(Y, 25, 2)
    dy_dx = np.gradient(Y_s, X)
    dy_dx = savgol_filter(dy_dx, 31, 2)
    d2y_dx2 = np.gradient(dy_dx, X)
    d2y_dx2 = savgol_filter(d2y_dx2, 31, 2)
    peaks_idxs = [np.argmax(abs(d2y_dx2))]
    peak_2_candidates = np.array([[i, elem] for i, elem in enumerate (d2y_dx2) if abs(d2y_dx2[peaks_idxs[0]]/abs(elem) < tol)])
    if len(peak_2_candidates) > 0:
        best_can = peak_2_candidates[0].copy()
        for cand in peak_2_candidates:
            if cand[1] > best_can[1]:
                best_can = cand.copy()
        peaks_idxs.append(int(best_can[0]))
    # fig, ax1 = plt.subplots()
    # plt.title('Phase smoothing + Peak detection')
    # ax1.plot(Y, 'b*', label='Y')
    # ax1.plot(Y_s, 'r-', label='Y_s')
    # ax1.set_ylabel('norm. Y and Y_s')
    # ax2 = ax1.twinx()
    # ax2.set_ylabel('norm. dy/dx and d2y/dx2')
    # ax2.plot(d2y_dx2/abs(max(d2y_dx2)), 'g--', label='d2y/dx2')
    # ax2.plot(peaks_idxs, [d2y_dx2[i]/abs(max(d2y_dx2)) for i in peaks_idxs], 'b*')
    # ax2.plot(dy_dx/abs(max(dy_dx)), 'k--', label='dy/dx')
    # # Combine the legends from all axes
    # lines = ax1.get_lines() + ax2.get_lines()
    # labels = [line.get_label() for line in lines]
    # plt.legend(lines, labels)
    # plt.show()
    return peaks_idxs

# def OLD_frame_S_param_phase(Y, size, tol):
#     res = None
#     for y_zero in np.linspace(0.3, 0.7, 100): 
#         zeros = get_zeros(Y, y_zero, size, tol)
#         if len(zeros) == 3:
#             if res is None:
#                 res = [y_zero, zeros]           
#             elif (zeros[2]-zeros[1]) * (zeros[1]-zeros[0]) < left_dist_to_mid * right_dist_to_mid:   
#             # elif abs((zeros[2]-zeros[1]) - (zeros[1]-zeros[0])) < abs(left_dist_to_mid - right_dist_to_mid):   
#                     res = [y_zero, zeros]             
#             left_dist_to_mid = res[1][2]-res[1][1]
#             right_dist_to_mid = res[1][1]-res[1][0]    

#     try:
#         idx_Y_mid = res[1][1]
#     except Exception as e:
#         plt.figure('Failed to center')
#         plt.plot(Y)
#         plt.show()
#         # raise Exception('What kind of S-param phase curve is that?')
            
#     nb_pts_end_curve = min([idx_Y_mid, len(Y)-idx_Y_mid])
#     Y_framed = Y[idx_Y_mid-nb_pts_end_curve:idx_Y_mid+nb_pts_end_curve].copy()
#     plt.figure('Framing of phase')
#     plt.plot(Y)
#     plt.plot(np.linspace(idx_Y_mid-nb_pts_end_curve, idx_Y_mid+nb_pts_end_curve, len(Y_framed)), Y_framed)
#     plt.show()
#     return Y_framed

# def get_zeros(Y, y_zero, size, tol):
#     zeros = []
#     i = 0
#     while i < len(Y):
#         if abs(Y[i] - y_zero) < tol:
#             candidates = []
#             j = i
#             for y in Y[i:(i+size)]:
#                 if abs(y - y_zero) < tol:
#                     candidates.append([y,j])
#                 j+=1
#             # # transpose the matrix
#             # candidates = [list(row) for row in zip(*candidates)]
#             min_res_Y = abs(candidates[0][0] - y_zero)
#             idx_min_res_Y = candidates[0][1]
#             for candidate in candidates:
#                 if abs(candidate[0] - y_zero) < min_res_Y:
#                     min_res_Y, idx_min_res_Y = candidate
#             zeros.append(idx_min_res_Y)
#             # keep looking for zeros from last candidate 
#             i = candidates[-1][1]
#         i += 1
#     return zeros    

def PhaseUnwrappingCorrection(ring_slot,df):

    S11phase = []
    S21phase = []
    S12phase = []
    S22phase = []

#################################################
#### Define the Right Touchstone Columns
##################################################

    """
    s11 = ring_slot.s[:,0,0] # S11 values from the S-Parameter Matrix in .s2p file
    s21 = ring_slot.s[:,1,0] # S21 values from the S-Parameter Matrix in .s2p file
    s12 = ring_slot.s[:,0,1]
    s22 = ring_slot.s[:,1,1] # S22 values from the S-Parameter Matrix in .s2p file
    """

#################################################
#### Phase Unwrapping
##################################################

    f = df['s_db 21'].index

    for p in range(2):
        for k in range(2):
            ######## leads to 0 0, 0 1, 1 0 , 1 1 --> S11, S12, S21, S22

            sparamter = ring_slot.s[:,p,k] # S21 values from the S-Parameter Matrix in .s2p file
            phase = ring_slot.s_deg[:,p,k] # Phase data of S21
            phase_unw = np.zeros(len(phase))
            j = 0

            # Unwrap routine
            for i in range(len(phase_unw)):
                phase_unw[i] = math.radians(phase_unw[i]) # Degrees to radians
            for i in range(len(phase)):
                phase[i] = math.radians(phase[i]) # Degrees to radians

            disc= False
            for i in range(len(phase)-1):
                if abs(phase[i+1] - phase[i]) >= ((3*np.pi)/2): # search for phase discontinuity
                    disc= True
                    if phase[i] < phase[i+1]: # if it is a positive discontinuity
                        j = i
                        for j in range(i, len(phase)-1):
                            phase_unw[j+1] = phase[j+1] - (2*np.pi)
                    else:
                        for j in range(i, len(phase)-1):
                            phase_unw[j+1] = phase[j+1]
                elif disc==False:
                    if i ==0:
                        phase_unw[i] = phase[i]
                        phase_unw[i + 1] = phase[i + 1]
                    else:
                        phase_unw[i+1] = phase[i+1]

            # New ploting
            if disc:
                plt.figure()
                plt.title('Phase discontinuity correction')            
                plt.subplot(1, 2, 1)
                X = np.linspace(0,1,len(phase))
                plt.plot(X, phase)
                plt.subplot(1, 2, 2)
                plt.plot(X, phase_unw)
                plt.show()

            # plt.figure()
            # plt.subplot(1, 2, 1)
            # plt.xlabel('ang S21')
            # plt.ylabel('magnitude S21')            
            # plt.plot(X, abs(sparamter), 'bo')     
            # # plt.plot(X, phase_unw, 'bo')             
            # plt.subplot(1, 2, 2)
            # plt.plot(sparamter.real, sparamter.imag, 'bo')
            # plt.plot(0, 0, 'bo')
            # plt.xlabel('Re[S21]')
            # plt.ylabel('Im[S21]')
            # plt.title('Make it a circle')         
            # plt.gca().set_aspect('equal', adjustable='box')  # Set aspect ratio to be equal   
            # plt.show()

#################################################
#### Phase Correction
##################################################


            # Normalize phase plot
            Y = (phase_unw  - min(phase_unw))/(max(phase_unw)-min(phase_unw))

            Y_framed = frame_S_param_phase(Y)                   
            Y_cor_framed = new_correct_lin_trend_phase(Y_framed)
            X_cor_framed = np.linspace(0,1,len(Y_cor_framed))
            popt = fano_fitting(X_cor_framed,Y_cor_framed)

            X = np.linspace(0,1,len(f))
            if popt is None:
                plt.figure()
                plt.title('Could not fit the S-parameter phase with Fano curve')
                plt.plot(X, Y, 'b-')
                plt.plot(X_cor_framed, Y_cor_framed, 'g--')
                plt.show()
                raise Exception('Could not fit the S-parameter phase with Fano curve')
            
            else: 
                [A, q, f0, g, H, y0] = popt
                plt.figure()
                plt.plot(X, Y, 'b.', label='Data')
                plt.plot(X_cor_framed, Y_cor_framed, 'g--')
                plt.plot(X, fano(X, *popt), 'r-', label=f'Fitted curve: q={q:.2f}, f0={f0:.2f}, g={g:.2f}, H={H:.2f}, y0={y0:.2f}')
                plt.legend()    
                plt.show()

            # phase_max = np.max(phase_unw)
            # phase_max_idx  = np.argmax(phase_unw)
            
            # nb_pts_end_curve = min([phase_max_idx, len(phase_unw)-phase_max_idx])
            # left_branch = np.zeros(nb_pts_end_curve)
            # right_branch = np.zeros(nb_pts_end_curve)
            # # until we reach one end of the curve
            # for i in range(nb_pts_end_curve):
            #     left_branch[i] = phase_unw[phase_max_idx-i]
            #     right_branch[i] = phase_unw[phase_max_idx+i]

            # # reverse array
            # left_branch = left_branch[::-1]

            # plt.figure()
            # X = np.arange(len(phase_unw))
            # plt.plot(X, phase_unw)
            # plt.plot(X[phase_max_idx-nb_pts_end_curve:phase_max_idx], left_branch, 'bo')
            # plt.plot(X[phase_max_idx:phase_max_idx+nb_pts_end_curve], right_branch, 'ro')
            # plt.show()

            n = round(0.1 * len(df))
            ph_ini = phase_unw[:n].copy() # initial 10%
            ph_fin = phase_unw[-n:].copy() # final 10%

            # Linear regression initial part
            coef_lin_ini = np.polyfit(f[:n], ph_ini[:n], 1)

            # Linear regression final part
            coef_lin_fin = np.polyfit(f[-n:], ph_fin[-n:], 1)


            # Option 3
            phase_r = np.zeros(len(f))
            for i in range(len(f)):
                phase_r[i] = phase_unw[i] - (coef_lin_ini[0]-coef_lin_fin[0])/2 * (f[i]-f[0])
            
            sparamter_r = np.zeros(len(f), dtype=complex)
            for i in range(len(f)):
                # print(np.cos(phase_r[i]))
                # print(np.sin(phase_r[i]))
                sparamter_r[i] = abs(sparamter[i]) * (np.cos(phase_r[i]) + 1j * np.sin(phase_r[i]))

            # plt.figure()
            # X = np.linspace(0,1,len(phase))
            # plt.plot(X, phase_unw, 'r-')
            # plt.plot(X, [0]*len(phase))
            # plt.plot(X, phase_r, 'b-')
            # plt.plot(X[:n], phase_unw[:n])
            # plt.plot(X[-n:], phase_unw[-n:])

            # plt.figure()
            # plt.plot(sparamter.real, sparamter.imag, 'bo')
            # plt.plot(sparamter_r.real, sparamter_r.imag, 'ro')
            # # plt.plot(0, 0, 'gx')
            # plt.xlabel('Re[S21]')
            # plt.ylabel('Im[S21]')
            # plt.title('Correction perfect circle')         
            # plt.gca().set_aspect('equal', adjustable='box')  # Set aspect ratio to be equal   
            # plt.show()

            if p == 0:
                if k == 0:
                    S11phase.append(sparamter_r)
                else:
                    S12phase.append(sparamter_r)
            else:
                if k == 0:
                    S21phase.append(sparamter_r)
                else:
                    S22phase.append(sparamter_r)

    return S11phase,S21phase,S12phase,S22phase,None