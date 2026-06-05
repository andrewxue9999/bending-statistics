#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 30 19:26:39 2023

@author: carolingold

Routine to plot AFM data - based on 
etelford38/Asylum_Data_Plotting: 
https://github.com/etelford38/Asylum_Data_Plotting/blob/main/Asylum_CAFM.py

- Part 2 - manipulate Data
"""

import numpy as np
import cv2


# ==============================================================================
# LineCorrect Data (partially taken from stmpy)
# ==============================================================================

def Polyfit_subtract_1D(data, n):
    x = np.linspace(0,1,len(data))
    popt = np.polyfit(x, data, n)
    # print(popt)
    return data - np.polyval(popt, x)

def Polyfit_subtract_2d(data,n):
    fit_data=[]
    for i, line in enumerate(data):
        linefit=Polyfit_subtract_1D(line,n)
        fit_data.append(linefit)
    return np.array(fit_data)

# ==============================================================================
# Manipulate data : FFT
# ==============================================================================

def oneFFT(data):
    f = np.fft.fft2(data)
    fshift = np.fft.fftshift(f)
    absFFT = np.abs(fshift)  # + 1e-10
    magnitude_spectrum = np.log(absFFT)
    magnitude_spectrum = magnitude_spectrum - np.mean(magnitude_spectrum)

    # Remove the zero-peak and the vertical/horizontal noise lines
    magnitude_spectrum_size = magnitude_spectrum.shape[0]
    magnitude_spectrum[int(magnitude_spectrum_size//2),
                       :] = 0  # np.std(magnitude_spectrum)
    # np.std(magnitude_spectrum)
    magnitude_spectrum[:, int(magnitude_spectrum_size//2)] = 0

    magnitude_spectrum_norm = magnitude_spectrum - np.min(magnitude_spectrum)
    magnitude_spectrum_norm = (
        magnitude_spectrum_norm / np.max(magnitude_spectrum_norm)*255).astype(np.uint8)

    magnitude_spectrum_norm = cv2.medianBlur(magnitude_spectrum_norm, 1)

    test = magnitude_spectrum_norm.copy()

    return test


def pad_with(vector, pad_width, iaxis, kwargs):
    pad_value = kwargs.get('padder', 0)
    vector[:pad_width[0]] = pad_value
    vector[-pad_width[1]:] = pad_value


def FFT_data_nm(data_dict, data, zoomFactor=1, padding=None):

    # data_max=np.max(data)
    x_real = float(data_dict['xrange'])
    y_real = float(data_dict['yrange'])
    x_lines = float(data_dict['points'])
    y_lines = float(data_dict['lines'])

    nmPrPix = (x_real/1e-9)/(x_lines)
    if padding == None:

        FFTextent = 1/(nmPrPix*2)
        # FFTpixSize = FFTextent / (x_lines*0.5)

        ymin, ymax = int(y_lines*(zoomFactor-1)/(zoomFactor*2)
                         ), int(y_lines*(zoomFactor+1)/(zoomFactor*2))
        xmin, xmax = int(x_lines*(zoomFactor-1)/(zoomFactor*2)
                         ), int(x_lines*(zoomFactor+1)/(zoomFactor*2))

        subFFT = oneFFT(data)[ymin:ymax, xmin:xmax]

    else:
        data_pad = np.pad(data, padding, pad_with)

        # Recalculate sizes for padding
        x_lines_pad = x_lines + padding*2
        y_lines_pad = y_lines + padding*2

        x_real_pad = x_real + padding*2*nmPrPix
        y_real_pad = y_real + padding*2*nmPrPix

        nmPrPix_pad = x_real_pad/x_lines_pad
        FFTextent_temp = 1/(nmPrPix_pad*2)
        FFTextent = FFTextent_temp / (x_lines_pad*0.5)
        zoomFactor_pad = zoomFactor

        ymin_pad, ymax_pad = int(y_lines_pad*(zoomFactor_pad-1)/(zoomFactor_pad*2)), int(
            y_lines_pad*(zoomFactor_pad+1)/(zoomFactor_pad*2))
        xmin_pad, xmax_pad = int(x_lines_pad*(zoomFactor_pad-1)/(zoomFactor_pad*2)), int(
            x_lines_pad*(zoomFactor_pad+1)/(zoomFactor_pad*2))

        subFFT = oneFFT(data_pad)[ymin_pad:ymax_pad, xmin_pad:xmax_pad]

    FFT_dict = {
        'FFT': subFFT,
        'FFTrange': FFTextent/zoomFactor
    }

    return FFT_dict

# ==============================================================================
# Manipulate data : extract Moire angle
# ==============================================================================
def MoireAngle(l_moire,a,d):
    '''
    calculate the twist angle from the wavelength of the moire material
    
    Parameters
    ----------
    l_moire : float , moire wavelength e.g. from Fourier transform
    a: float , lattice constant of material, e.g. 2.46e-10 for graphene
    d: float , lattice mismatch
    
    Returns
    -------
    theta_moire: float , twist angle of moire material
    '''
    theta=np.arccos(1.-((1.+d)**2*a**2/(l_moire**2)-d**2)/(2.*(1.+d)))
    return theta