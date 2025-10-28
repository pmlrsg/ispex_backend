#! /usr/bin/env python
import logging
from classes import Ispeximage
from classes import Ispexreflectance
import glob
import os
import re

# quality control functions
from quality_control import linearity_qc
from quality_control import acquistion_qc

logging.basicConfig(level=logging.INFO)
log = logging.getLogger('ispex')

# where are the images stored
img_path = os.path.abspath("example_data/iSPEX_Set_20250806_0925_3537")
save_path = os.path.abspath(os.path.join("example_outputs", os.path.basename(img_path)))

if not os.path.isdir(save_path):
    os.makedirs(save_path)

# find all the images
if not os.path.exists(img_path):
    log.error(f"File not found: {img_path}")
    raise FileNotFoundError(f"File path not found: {img_path}")

images = glob.glob(os.path.join(img_path, '*.DNG'))
if len(images) == 0:
    raise FileNotFoundError(f"No images found in {img_path}")

# dictionary to organise the files
card_set = {'E0': None, 'E1': None, 'E2': None, 'E3': None, 'E4': None}
water_set = {'E0': None, 'E1': None, 'E2': None, 'E3': None, 'E4': None}
sky_set = {'E0': None, 'E1': None, 'E2': None, 'E3': None, 'E4': None}
rrs_set = {'E0': None, 'E1': None, 'E2': None, 'E3': None, 'E4': None}

# Check that file spec conforms to expected pattern and populate the dictionary
for impath in images:
    log.info(f"Image: {impath}")
    pattern = re.compile(r"IMG_(?P<datestr>\d{8})_(?P<timestr>\d{4})_(?P<uuid>\w{4})_(?P<obstype>\w{1})_(?P<exposure_seq>\w{2}).DNG")
    match = pattern.match(os.path.basename(impath))
    if match is None:
        raise ValueError(f"Filename {os.path.basename(impath)} does not match expected pattern.")

    obstype = match.groupdict()['obstype']  # 'C', 'S', or 'W' for Card, Sky, Water
    exposure = match.groupdict()['exposure_seq']  # E0, E1, E2, E3, or E4
    # below, we override the cal set lookup (pick E2) until we have a way to select the best exposure
    if obstype == 'C':
        card_set[exposure] = Ispeximage(dng_path=impath,
                                        type='observation',
                                        save_path_root='example_outputs/iSPEX_Set_20251001_1524_0770',
                                        calibration_set='cameras/iPhone14_4/20250813_1501_59E5_E2')
    elif obstype == 'W':
        water_set[exposure] = Ispeximage(dng_path=impath,
                                         type='observation',
                                         save_path_root='example_outputs/iSPEX_Set_20251001_1524_0770',
                                        calibration_set='cameras/iPhone14_4/20250813_1501_59E5_E2')
    elif obstype == 'S':
        sky_set[exposure] = Ispeximage(dng_path=impath,
                                       type='observation',
                                       save_path_root='example_outputs/iSPEX_Set_20251001_1524_0770',
                                        calibration_set='cameras/iPhone14_4/20250813_1501_59E5_E2')
    else:
        log.warning(f"Unknown observation type {obstype} in file {impath}")


# Process each set
for set in [card_set, water_set, sky_set]:
    for exposure in set:
        if set[exposure] is None:
            log.warning(f"Missing image for exposure {exposure}")
        else:
            try:
                log.info(f"Processing {exposure}")
                set[exposure].process()
                set[exposure].plot_bounding_areas()
                #set[exposure].plot_background_correction()
                set[exposure].plot_spectra()
            except Exception as e:
                log.error(f"Error processing {set[exposure].dng_path}: {e}")
                continue


# calculate reflectances                
for exposure in rrs_set:
     # Test set of individual spectra exist before computing rrs
     if  (hasattr(card_set[exposure], 'spectra_calibrated_qp') + 
          hasattr(card_set[exposure], 'spectra_calibrated_qm') +
          hasattr(water_set[exposure],'spectra_calibrated_qp') +
          hasattr(water_set[exposure],'spectra_calibrated_qm') +
          hasattr(sky_set[exposure],  'spectra_calibrated_qp') +
          hasattr(sky_set[exposure],  'spectra_calibrated_qm')) == 6: 
         
              log.info(f"Calculating reflectance: {exposure}")
           
              # Initialize rrs set  
              rrs_set[exposure] = Ispexreflectance(water_set[exposure],
                                                save_path_root = "example_outputs/iSPEX_Set_20250806_0925_3537",
                                                )
                
              # calculate rrs
              rrs_set[exposure].calc_rrs(card_set[exposure], water_set[exposure], sky_set[exposure])
              
              # plot rrs
              rrs_set[exposure].plot_rrs(rrs_set[exposure])
              

     else: 
             log.info(f"calibrated qp and qm spectra were not present: {exposure}")
             
             
# quality control - which image exposures should be used for Rrs
for exposure in rrs_set:
    if hasattr(rrs_set[exposure], 'rrs') == 1:
        acquistion_qc(rrs_set[exposure], card_set[exposure], water_set[exposure], sky_set[exposure])
        
for set in [card_set, water_set, sky_set]:
    linearity_qc(set)
