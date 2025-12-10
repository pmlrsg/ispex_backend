#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 17 14:20:59 2025

Quality control functions and plots.

"""

import os
import logging
import numpy as np
from matplotlib import pyplot as plt
import datetime

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('ispex')

def linearity_qc(set):
    
    """
    This function tests for intensity linearity of a set of card, water or sky
    exposures. It plots the maximum intensity of each band as a function of 
    exposure time and the stepwise intensity-exposure time slope, which can be 
    to identify departures from linearity
    
    I have yet to consider how to store as qc flag 
    (it belongs to set of exposures rather than an individual class instance)
                                                    
    
    """

    # lists for exposure times, max values
    exposure_times = []
    qp_max = [] 
    qm_max = []
    qp_max_index = []
    qm_max_index = []
        
    for exposure in set:
        data_flag = (hasattr(set[exposure], 'spectra_calibrated_qp') +
                     hasattr(set[exposure], 'spectra_calibrated_qm'))
                
        if set[exposure] is None or data_flag != 2:
            log.warning(f"Missing image for exposure linearity test: {exposure}")
    
        else:
            # search for max and argmax of each band and append to lists
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

    plt.rcParams.update({'font.size': 14, 'axes.labelsize': 14})
    colors = ['red', 'green', 'blue']
    plt.subplot(1,2,1)
    for j in range(len(colors)): # loop over bands
        plt.plot(exposure_times, qp_max[:,j], color=colors[j],label = 'Qp: ' + str(colors[j]))
        plt.scatter(exposure_times, qp_max[:,j], color=colors[j])
        plt.plot(exposure_times, qm_max[:,j], color=colors[j], linestyle='dashed', label = 'Qm: ' +str(colors[j]))
        plt.scatter(exposure_times, qm_max[:,j], color=colors[j])
    plt.xlabel('Exposure time [s]')    
    plt.ylabel('Intensity [AU]')
    plt.legend()
    # plt.gca().set_xlim(left=0)
    plt.gca().set_ylim(bottom=0)
    
    # graph of stepwise local slopes - should be the same if linear    
    plt.subplot(1,2,2)
    if len(exposure_times) > 2: # need at least 3 points for a meaningful slope comparrison 
        mean_exposure_times = (exposure_times[1:] + exposure_times[0:-1])/2 # centre time bin
        for j in range(len(colors)): # loop over bands
            slope_qp_max_j = np.diff(qp_max[:,j], axis =0)/np.diff(exposure_times)
            slope_qm_max_j = np.diff(qm_max[:,j], axis =0)/np.diff(exposure_times)
            plt.plot(mean_exposure_times, slope_qp_max_j, color=colors[j],label = 'Qp')
            plt.scatter(mean_exposure_times, slope_qp_max_j, color=colors[j])
            plt.plot(mean_exposure_times, slope_qm_max_j, color=colors[j],linestyle='dashed', label = 'Qm')
            plt.scatter(mean_exposure_times, slope_qm_max_j, color=colors[j])
        plt.ylabel('Intensity-exposure slope [AU/s]')
        plt.xlabel('Exposure time [s]')    
        # plt.gca().set_xlim(left=0)
        plt.gca().set_ylim(bottom=0)


    plt.savefig(os.path.join(set[exposure].save_path, 
               f'{set[exposure].save_path.split('/')[1]}_{set[exposure].obstype}_LinearityPlot.png'), 
                bbox_inches="tight", dpi=300)
                        
    plt.close()
    
    return


def acquistion_qc(rrs_exp, card_exp, water_exp, sky_exp):
    
    """
    Quality control for measurement geometry and measurement sequence timing
    
    (i) Elevation flag tests for 140/40 angles for sky and water (5 deg tol.)
       
    (ii) Azimuth 135 flag tests for 135 angle for sky and water (10 deg tol.)
    
    (iii) Azimuth range flag tests for valid on range [90,145] deg.
    
    (iv) Sequence time flag tests for measurements collected within 1 min
    
    For now, measurement angles on card are not included in QC
    
    """

    # elevation_40 flag - target angles (140, 40) are constants
    elevation_tol= 5
    if (abs(water_exp.true_elevation - 140) >  elevation_tol 
        or abs(sky_exp.true_elevation - 40) >  elevation_tol):
        rrs_exp.elevation_flag = True
        
    # azimuth_135 flag - target angle (135) is constant
    azimuth135_tol = 10
    if (abs(abs(water_exp.relative_azimuth) - 135) > azimuth135_tol 
        or abs(abs(sky_exp.relative_azimuth) - 135) > azimuth135_tol): 
        rrs_exp.azimuth135_flag = True
        
    # azimuth valid-range flag
    azimuth_max = 145 
    azimuth_min = 90 
    if (abs(abs(water_exp.relative_azimuth)) > azimuth_max
        or abs(abs(water_exp.relative_azimuth)) < azimuth_min
        or abs(abs(sky_exp.relative_azimuth)) > azimuth_max   
        or abs(abs(sky_exp.relative_azimuth)) < azimuth_min):
        rrs_exp.azimuthrange_flag = True
    
    # sequence timing flag
    max_time_delay = 60 # tests for maximum time delay betweem card/sky (seconds)
    card_time = datetime.datetime.fromtimestamp(card_exp.time_utc, tz=datetime.timezone.utc)     
    sky_time = datetime.datetime.fromtimestamp(sky_exp.time_utc, tz=datetime.timezone.utc)     
    if (sky_time - card_time).total_seconds() > max_time_delay:
        rrs_exp.sequencetime_flag = True
    
 
    return
   
