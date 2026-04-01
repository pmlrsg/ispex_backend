#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example script to load processed iPSEX image sets and relfectance sets saved in 
JSON data format

"""

import os
import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
import json
import glob
import datetime


def load_json(filename):
    with open(filename, 'r') as file:
        data = json.load(file)     
    return data

def plot_radiances():
    
    wl_corr = lp[:,0]
    
    # Masks for spectral channels in rrs plots - these are hardcoded for now
    mask_R_corr = np.zeros(341) # `Red mask'
    mask_R_corr[240-30:331-30] = 1
    
    mask_G_corr = np.zeros(341) # `Green mask'
    mask_G_corr[130-30:271-30] = 1
    
    mask_B_corr = np.zeros(341) # `Blue mask'
    mask_B_corr[60-30:161-30] = 1
    
    mask_corr = [mask_R_corr, mask_G_corr, mask_B_corr]
    
    # Spectrum plot
    plt.rcParams.update({'font.size': 14, 'axes.labelsize': 14})
    plt.figure(figsize=(10, 4))  # Wider figure
    
    # Use a loop to plot each spectrum with a thicker line for visibility
    for j, color in zip(range(1, 4), ['red', 'green', 'blue']):  # Explicit color names for clarity
        plt.plot(wl_corr[mask_corr[j-1]==1], lp[:,j][mask_corr[j-1]==1] + lm[:,j][mask_corr[j-1]==1], c=color, linewidth=2)  # Thicker lines
        plt.plot(wl_corr[mask_corr[j-1]==1], lm[:,j][mask_corr[j-1]==1], c=color, linewidth=2, linestyle='--')  # Thicker lines
        plt.plot(wl_corr[mask_corr[j-1]==1], lp[:,j][mask_corr[j-1]==1], c=color, linewidth=2, linestyle=':')  # Thicker lines
    
    plt.legend(["Red_L", "Red_Lm", "Red_Lp",
                "Green_L", "Green_Lm", "Green_Lp",
                "Blue_L", "Blue_Lm", "Blue_Lp"], loc='upper right', fontsize=10)
    plt.xlabel("Wavelength [nm]", fontsize=14, fontweight='bold')
    plt.ylabel("Intensity [a.u.]", fontsize=14, fontweight='bold')
    plt.grid(color='grey', linestyle='--', linewidth=0.5, alpha=0.7)
    #  lpmax = np.nanmax(self.lp_corr[:,1:])
    # lmmax = np.nanmax(self.lm_corr[:,1:])
    # plt.ylim(0, 1.1*(lpmax+lmmax))  # 10% more space above the max value
    plt.xlim(400, 700)
    plt.gca().set_ylim(bottom=0)


# where are the images collected in the field are stored
img_path = os.path.abspath("example_data/iSPEX_Set_20250806_0925_3537")

# where are the processed data (output spectra, etc) are stored
save_path = os.path.abspath(os.path.join("example_outputs", os.path.basename(img_path)))

# this command sorts and searches for card/water/files
card_files = sorted(glob.glob(os.path.join(save_path, '*IMG*C*.json')))
water_files = sorted(glob.glob(os.path.join(save_path, '*IMG*W*.json')))
sky_files = sorted(glob.glob(os.path.join(save_path, '*IMG*S*.json')))

# this command searches for reflectance files
rrs_files = glob.glob(os.path.join(save_path, '*RRS*.json'))

# load first card file as a dictionary, and print fields
data = load_json(card_files[0])
print(data.keys())

# extract key meta data (fields are in `green')
lat = data['latitude']
lon = data['longitude']
time = data['timestr'] # time as HHMM
date = data['datestr'] # date as YYYYMMDD
timestamp = datetime.datetime.strptime(date  + time, '%Y%m%d%H%M') # timestamp as datetime 

# load the RGB band responses
qp = np.array(data['spectra_calibrated_qp']) # plus polarization
qm = np.array(data['spectra_calibrated_qm']) # minus polarization

wl = qp[:,0] # the wavelength is stored as the 0th column
red_band = qp[:,1] # the red band is stored as the 1st column
green_band = qp[:,2] # the green band is stored as the 2nd column
blue_band = qp[:,3] # the blue band is stored as the 3rd column

# example figure for RGB band responses
plt.figure()
plt.plot(wl, red_band, color='red')
plt.plot(wl, green_band, color='green')
plt.plot(wl, blue_band, color='blue')
plt.xlabel('Wavelength [nm]')
plt.ylabel('Intensity [Relative units]')


# load the SRF-corrected spectra
lp = np.array(data['lp_corr']) # plus polarization
lm = np.array(data['lm_corr']) # minus polarization
I = lp + lm # iy

# example figure fopr
plt.figure()
plt.plot(I[:,0], I[:,1], color='red')
plt.plot(I[:,0], I[:,2], color='green')
plt.plot(I[:,0], I[:,3], color='blue')
plt.xlabel('Wavelength [nm]')
plt.ylabel('Intensity [Relative units]')

# example fig
plot_radiances()
