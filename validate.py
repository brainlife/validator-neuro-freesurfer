#!/usr/bin/env python3

import csv
import json
import numpy
import glob
import sys
import os
import pandas as pd
from freesurfer_stats import CorticalParcellationStats

results = {"errors": [], "warnings": [], "brainlife": []}

def extract_measures(path):
    measures = {}
    with open(path, 'r') as input_file:
        #parse Measures
        lines = input_file.readlines()
        for line in lines:
            if line.startswith("# Measure"):
                tokens = line.split(",")
                #['# Measure VentricleChoroidVol', ' VentricleChoroidVol', ' Volume of ventricles and choroid plexus', ' 9296.000000', ' mm^3\n']
                #assume last 2 are the value and unit
                name = tokens[1].strip()
                desc = tokens[2].strip()
                value = float(tokens[3].strip())
                unit = tokens[4].strip()
                measures[name] = {"value": value, "unit": unit, "desc": desc}

    return measures

with open('config.json') as config_f:
    config = json.load(config_f)
    freesurfer_dir = config["output"]

    if not os.path.exists("output"):
        os.mkdir("output")

    if os.path.lexists("output/output"):
        os.remove("output/output")
    os.symlink("../"+freesurfer_dir, "output/output")

    if not os.path.exists("secondary"):
        os.mkdir("secondary")

    #copy important parcellations to secondary
    for parc in [ "aparc", "aparc.a2009s", "aparc.DKTatlas" ]:
        if os.path.lexists("secondary/"+parc+"+aseg.mgz"):
            os.remove("secondary/"+parc+"+aseg.mgz")
        os.symlink("../"+freesurfer_dir+"/output/output/"+parc+"+aseg.mgz", "secondary/"+parc+"+aseg.mgz")
    
    wm_measures = extract_measures(freesurfer_dir+'/stats/wmparc.stats')
    with open("secondary/wmparc.json", "w") as fp:
        json.dump(wm_measures, fp)

    #create plotly for wmparc
    x = []
    y = []
    for key in wm_measures:
        wm_measure = wm_measures[key]
        x.append(wm_measure["value"])
        y.append(key)

    graph = {
        "type": "plotly",
        "name": "White Matter Parcellation Stats",
        "data": [{
            #"name": parc,
            "type": "bar",
            "x": x,
            "y": y,
        }],
        "layout": { 
            "xaxis_title": "Volume (mm^3)"
        }
    }
    results["brainlife"].append(graph)

    for parc in [ "aparc", "aparc.a2009s", "aparc.DKTatlas" ]:

        #convert stats to csv
        lh_stats = CorticalParcellationStats.read(freesurfer_dir+'/stats/lh.'+parc+'.stats')
        dfl = lh_stats.structural_measurements
        dfl.to_csv("secondary/"+parc+'_lh-cortex.csv')

        rh_stats = CorticalParcellationStats.read(freesurfer_dir+'/stats/rh.'+parc+'.stats')
        dfr = rh_stats.structural_measurements
        dfr.to_csv("secondary/"+parc+'_rh-cortex.csv')

        #these value are very close between different parcellation, so let's just output for aparc
        if parc == "aparc":
            ######################### volume ###################################################
            x = []
            y = []
            x.append(lh_stats.whole_brain_measurements['brain_segmentation_volume_mm^3'][0])
            y.append("TotalBrainVol")
            #LR are same
            #x.append(rh_stats.whole_brain_measurements['brain_segmentation_volume_mm^3'][0])
            #y.append("RH TotalBrainVol")

            x.append(lh_stats.whole_brain_measurements['estimated_total_intracranial_volume_mm^3'][0])
            y.append("TotalIntracranialVol")
            #LR are same
            #x.append(rh_stats.whole_brain_measurements['estimated_total_intracranial_volume_mm^3'][0])
            #y.append("RH TotalIntracranialVol")

            x.append(lh_stats.whole_brain_measurements['total_cortical_gray_matter_volume_mm^3'][0])
            y.append("TotalCorticalGrayMatterVol")
            #LR are same
            #x.append(rh_stats.whole_brain_measurements['total_cortical_gray_matter_volume_mm^3'][0])
            #y.append("RH TotalCorticalGrayMatterVol")

            x.append(int(numpy.sum(lh_stats.structural_measurements['gray_matter_volume_mm^3'])))
            y.append("LH CorticalGrayMatterVol")
            x.append(int(numpy.sum(rh_stats.structural_measurements['gray_matter_volume_mm^3'])))
            y.append("RH CorticalGrayMatterVol")

            graph = {
                "type": "plotly",
                "name": parc+ " Volumes",
                "data": [{
                    "type": "bar",
                    "x": x,
                    "y": y,
                }],
                "layout": { 
                    #"barmode": "stack" 
                    "xaxis_title": "volume (mm^3)"
                },
            }
            results["brainlife"].append(graph)

            ####################### thickness ####################################################
        

            x = []
            y = []
            x.append(lh_stats.whole_brain_measurements['mean_thickness_mm'][0])
            y.append("LH MeanCorticalGrayMatterThickness")
            x.append(rh_stats.whole_brain_measurements['mean_thickness_mm'][0])
            y.append("RH MeanCorticalGrayMatterThickness")

            graph = {
                "type": "plotly",
                "name": parc+ " Thickness",
                "data": [{
                    "type": "bar",
                    "x": x,
                    "y": y,
                }],
                "layout": { 
                    #"barmode": "stack" 
                    "xaxis_title": "mm"
                },
            }
            results["brainlife"].append(graph)

with open("product.json", "w") as fp:
    json.dump(results, fp)

