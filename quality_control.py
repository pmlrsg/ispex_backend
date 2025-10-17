#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 17 14:20:59 2025

Quality control functions and plots.

"""

import logging
import numpy as np
from matplotlib import pyplot as plt

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('ispex')

def linearity_check(set):
    
    """
    This function tests for intensity linearity of a set of card, water or sky
    exposures. It plots intensity as a function of exposure time, and the stepwise
    intensity-exposure time slopes.

    """

 
    exposure_times = []
    qp_max = [] 
    qm_max = []
    qp_max_index = []
    qm_max_index = []
        
    # breakpoint()
    for exposure in set:
        data_flag = (hasattr(set[exposure], 'spectra_calibrated_qp') +
                     hasattr(set[exposure], 'spectra_calibrated_qm'))
                
        if set[exposure] is None or data_flag != 2:
            log.warning(f"Missing image for exposure {exposure}")
        else:
            # search for max and argmax of each band and append
            exposure_times.append(set[exposure].exposure_time)
            qp_max.append(np.max(set[exposure].spectra_calibrated_qp, axis=0)[1:4])
            qp_max_index.append(np.argmax(set[exposure].spectra_calibrated_qp, axis=0)[1:4])
            qm_max.append(np.max(set[exposure].spectra_calibrated_qm, axis=0)[1:4])
            qm_max_index.append(np.argmax(set[exposure].spectra_calibrated_qm, axis=0)[1:4])
    
    exposure_times = np.array(exposure_times)
    qp_max = np.stack(qp_max)       
    qm_max = np.stack(qm_max)  
    
    # graph of intensity versus exposure time
    plt.figure(figsize=(16, 8))   
#    plt.suptitle(str(set[exposure].label.split[:-3]))
    
    plt.rcParams.update({'font.size': 14, 'axes.labelsize': 14})
    colors = ['red', 'green', 'blue']
    plt.subplot(1,2,1)
    for j in range(len(colors)): # loop over bands
        plt.plot(exposure_times, qp_max[:,j], color=colors[j],label = 'Qp')
        plt.scatter(exposure_times, qp_max[:,j], color=colors[j])
        plt.plot(exposure_times, qm_max[:,j], color=colors[j], linestyle='dashed', label = 'Qm')
        plt.scatter(exposure_times, qm_max[:,j], color=colors[j])
    plt.xlabel('Exposure time [s]')    
    plt.ylabel('Intensity [AU]')
    # plt.gca().set_xlim(left=0)
    plt.gca().set_ylim(bottom=0)
    
    # graph of local slopes - should be the same if linear    
    mean_exposure_times = (exposure_times[1:] + exposure_times[0:-1])/2
    plt.subplot(1,2,2)
    for j in range(len(colors)): # loop over bands
        slope_qp_max_j = np.diff(qp_max[:,j], axis =0)/np.diff(exposure_times)
        slope_qm_max_j = np.diff(qm_max[:,j], axis =0)/np.diff(exposure_times)
        plt.plot(mean_exposure_times, slope_qp_max_j, color=colors[j],label = 'Qp')
        plt.scatter(mean_exposure_times, slope_qp_max_j, color=colors[j])
        plt.plot(mean_exposure_times, slope_qm_max_j, color=colors[j],linestyle='dashed', label = 'Qm')
        plt.scatter(mean_exposure_times, slope_qm_max_j, color=colors[j])
    plt.ylabel('Intensity: exposure slope [AU/s]')
    plt.xlabel('Exposure time [s]')    
    # plt.gca().set_xlim(left=0)
    plt.gca().set_ylim(bottom=0)
    
    return
