#!/bin/bash

fsdir=$(jq -r .output config.json)

mri_convert $fsdir/mri/aparc+aseg.mgz secondary/aparc+aseg.nii.gz
mri_convert $fsdir/mri/aparc.a2009s+aseg.mgz secondary/aparc.a2009s+aseg.nii.gz
if [ -f $fsdir/mri/aparc.DKTatlas+aseg.mgz ]; then
    mri_convert $fsdir/mri/aparc.DKTatlas+aseg.mgz secondary/aparc.DKTatlas+aseg.nii.gz
fi
