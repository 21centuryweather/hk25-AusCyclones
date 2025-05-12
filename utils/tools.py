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
    
# Create a single directory
def create_directory(dir_name):
    try:
        os.mkdir(dir_name)
        print(f"Directory '{dir_name}' created successfully.")
    except FileExistsError:
        print(f"Directory '{dir_name}' already exists.")
    except Exception as e:
        print(f"An error occurred: {e}")

def create_Node_dirstruct(runpath,casename):
    #### Create the case directory ####
    create_directory(runpath+casename)
    #### Create the detectBlobs directory ####
    create_directory(runpath+casename+'/input')
    #### Create the detectNodes directory ####
    create_directory(runpath+casename+'/detectNodes')
    #### Create the detectNodes directory ####
    create_directory(runpath+casename+'/stitchNodes')
    
    return runpath+casename, runpath+casename+'/input', runpath+casename+'/detectNodes', runpath+casename+'/stitchNodes'
    

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def generate_datetimes_months(start_date, end_date, interval=1):

    # Create a list to store the datetimes
    date_list = []

    # Loop to generate datetimes at the specified interval
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += relativedelta(months=interval)

    return date_list

def generate_datetimes(start_date, end_date, interval=1):

    # Create a list to store the datetimes
    date_list = []

    # Loop to generate datetimes at the specified interval
    current_date = start_date
    while current_date <= end_date:
        date_list.append(current_date)
        current_date += relativedelta(hours=interval)

    return date_list