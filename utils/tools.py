import re
import os
import intake
import subprocess
import numpy as np
import xarray as xr
from glob import glob

def generate_timestr_1yr(year, hour):
    if isinstance(year, list):
        return [generate_timestr_1yr(y) for y in year]
    else:
        y = int(year)
        start = f"{year}0101{hour:02d}00"
        end = f"{year + 1}0101" + "0000"
        return f"{start}-{end}"

def generate_timestr_5yr(year, hour):
    start = f"{year}0101{hour:02d}00"
    end = f"{year + 5}0101" + "0000"
    return f"{start}-{end}"

def write_to_filelist(infilenames,outfile):
    with open(outfile, 'w') as file:
        for infilename in infilenames:
            file.write(infilename + '\n')

def clear_dir(dir):
    subprocess.run(f'rm -f {dir}/*', shell=True, check=True)

def get_GADI_ERAI(year=2019, parameter='psl', dataset='sfc'):
    if isinstance(year, int):
        year = [year]

	# ERA-Interim on ub04
    parent_dir = f"/g/data/ub4/erai/netcdf/6hr/atmos/oper_an_{dataset}/v01/{parameter}"
    pattern = f"{parameter}_6hrs_ERAI_historical_an-{dataset}_*.nc"
    full_pattern = os.path.join(parent_dir, pattern)
    all_files = glob(full_pattern)

    matched_files = []
    for f in all_files:
        match = re.search(r'_(\d{8})_\d{8}\.nc$', f)
        if match:
            file_year = int(match.group(1)[:4])
            if file_year in year:
                matched_files.append(f)

    return sorted(matched_files)

def get_GADI_JRA55(year=2019, parameter='psl'):
    if isinstance(year, int):
        year = [year]

    # JRA-55 on qu79
    parent_dir = f'/g/data/qu79/replicas/CREATE-IP/reanalysis/JMA/JRA-55/JRA-55/atmos/6hr/v20200612'
    pattern = f"{parameter}_6hr_reanalysis_JRA-55_*.nc"
    full_pattern = os.path.join(parent_dir, pattern)
    
    all_files = glob(full_pattern)
    
    matched_files = []
    for f in all_files:
        match = re.search(r'_(\d{10})-\d{10}\.nc$', os.path.basename(f))
        if match:
            file_year = int(match.group(1)[:4])
            if file_year in year:
                matched_files.append(f)

    return sorted(matched_files)