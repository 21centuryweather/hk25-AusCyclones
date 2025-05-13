#!/bin/bash

#PBS -P nf33

#PBS -q normal

#PBS -l ncpus=12

#PBS -l walltime=04:00:00

#PBS -l wd

#PBS -l storage=gdata/rt52+scratch/nf33

#PBS -l mem=12GB

#PBS -N etc_climatology

module use /scratch/nf33/public/miniconda/

module load digital_earths_env

mpirun -np 12 /scratch/nf33/tempestextremes/bin/DetectNodes --in_data_list /scratch/nf33/ad1803/hk25-AusCyclones/ETC_workfolder/ETCs_Climatology/input/input_files.txt --out_file_list /scratch/nf33/ad1803/hk25-AusCyclones/ETC_workfolder/ETCs_Climatology/detectNodes/detect_files.txt --searchbymin msl --closedcontourcmd "msl,200.0,5.5,0" --mergedist 6.0 --outputcmd "msl,min,0;zs,min,0" --timefilter "6hr" --latname latitude --lonname longitude --logdir /scratch/nf33/ad1803/hk25-AusCyclones/ETC_workfolder/ETCs_Climatology/

mpirun -np 12 /scratch/nf33/tempestextremes/bin/StitchNodes --in_list /scratch/nf33/ad1803/hk25-AusCyclones/ETC_workfolder/ETCs_Climatology/detectNodes/detect_files.txt --in_fmt "lon,lat,msl,zs" --range 6.0 --mintime 24h --maxgap 18h --threshold "zs,<=,50,1" --min_endpoint_dist 0.0 --out_file_format csv --out /scratch/nf33/ad1803/hk25-AusCyclones/ETC_workfolder/ETCs_Climatology/stitchNodes/stitchNodes.csv

echo "Complete"
