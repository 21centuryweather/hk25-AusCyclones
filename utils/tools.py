import re
import os
import subprocess
import numpy as np
#import xarray as xr
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

