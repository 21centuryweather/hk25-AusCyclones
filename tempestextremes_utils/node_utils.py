import os
import subprocess

def run_detectNodes(input_filelist, detect_filelist, mpi_np=4,
                    detect_var="msl",
                    merge_dist=6.0,
                    bounds=None,
                    closedcontour_commands="msl,200.0,5.5,0;_DIFF(z(300millibars),z(500millibars)),-58.8,6.5,1.0",
                    output_commands="msl,min,0;_VECMAG(u10,v10),max,2.0;zs,min,0",
                    timeinterval="6hr",
                    lonname="longitude",latname="latitude",
                    logdir="./log/",
                    regional=False,
                    quiet=False,
                    out_command_only=False):
    
    ''' Detect and track minimum based on TempestExtremes
    TC detection is based on warm-core criterion from Zarzycki and Ullrich (2017)
    https://agupubs.onlinelibrary.wiley.com/doi/10.1002/2016GL071606
    
    Parameters
    ----------
   
    input_filelist : dtype str
        String with a path to the textfile containing the input data required.
    detect_filelist : dtype str
        String with a path to the textfile containing the names of the detectNode output.
    mpi_np : dtype int
        Number of cores used in the calculation, given to mpi command.
    detect_var : dtype str
        String with the variable to detect (must match ib the input netcdf file).
    bounds : list (N=4), default=None.
        a list containing the bounds of a bounding box to do detection in the form [minlon,maxlon,minlat,maxlat]
    closedcontour_commands : dtype str
        String with the closed contour commands. Should be of the form <var,op,threshold,dist> with commands separated by a ";"
    output_commands : dtype str
        String with the output commands. Should be of the form <var,op,dist> with commands separated by a ";"
    timeinterval : dtype str
        String with the time interval (e.g. "6hr")
    lonname : dtype str
        String with the longitude variable name, as in the input netcdfs
    latname : dtype str
        String with the latitude variable name, as in the input netcdfs
    logdir : dtype str
        String with the path for logfile output.
    regional : bool
        *Optional*, default ``False``. If ``True``, tells TE that it is expecting a regional grid without periodic boundaries
    quiet : bool
        *Optional*, default ``False``. If ``True``, progress information is suppressed.
    out_command_only : bool
        *Optional*, default ``False``. If ``True``, will not run the TE command but instead with output the command for terminal use.
    '''

    # DetectNode command
    detectNode_command = ["mpirun", "-np", f"{int(mpi_np)}",
                            f"{os.environ['TEMPESTEXTREMESDIR']}/DetectNodes",
                            "--in_data_list",f"{input_filelist}",
                            "--out_file_list", f"{detect_filelist}",
                            "--searchbymin",f"{detect_var}",
                            "--closedcontourcmd",f"\"{closedcontour_commands}\"",
                            "--mergedist",f"{merge_dist}",
                            "--outputcmd",f"\"{output_commands}\"",
                            "--timefilter",f"\"{timeinterval}\"",
                            "--latname",f"{latname}",
                            "--lonname",f"{lonname}",
                            "--logdir",f"{logdir}",
                            ]
    if regional:
        detectNode_command=detectNode_command+["--regional"]
    if bounds is not None:
        detectNode_command=detectNode_command+[f"--minlon {bounds[0]} --maxlon {bounds[1]} --minlat {bounds[2]} --maxlat {bounds[3]}"]
    
    print(*detectNode_command)
    
    if not out_command_only:
        detectNode_process = subprocess.Popen(detectNode_command,
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE, text=True)

        # Wait for the process to complete and capture output
        stdout, stderr = detectNode_process.communicate()

        path,_=os.path.split(input_filelist)
        outfile=path+'/detectNodes_outlog.txt'
        with open(outfile, 'w') as file:
            file.write(stdout)
        outfile=path+'/detectNodes_errlog.txt'
        with open(outfile, 'w') as file:
            file.write(stderr)
        if not quiet:
             return stdout, stderr

def run_stitchNodes(input_filelist, stitch_file, mpi_np=1,
                    output_filefmt="csv",
                    in_fmt_commands="lon,lat,msl",
                    range_dist=8.0,
                    minim_time="54h",
                    maxgap_time="24h",
                    min_endpoint_dist=12.0,
                    threshold_condition="wind,>=,10.0,10;lat,<=,50.0,10;lat,>=,-50.0,10;zs,<,150,10",
                    quiet=False,
                    out_command_only=False):

    # StitchNode command
    stitchNode_command = ["mpirun", "-np", f"{int(mpi_np)}",
                             f"{os.environ['TEMPESTEXTREMESDIR']}/StitchNodes",
                             "--in_list",f"{input_filelist}",
                             "--in_fmt",f"\"{in_fmt_commands}\"",
                             "--range",f"{range_dist}",
                             "--mintime",f"{minim_time}",
                             "--maxgap",f"{maxgap_time}",
                             "--threshold",f"\"{threshold_condition}\"",
                             "--min_endpoint_dist",f"{min_endpoint_dist}",
                             "--out_file_format",f"{output_filefmt}",
                             "--out", f"{stitch_file}"
                             ]
    
    print(*stitchNode_command)
    
    if not out_command_only:
        stitchNode_process = subprocess.Popen(stitchNode_command,
                                              stdout=subprocess.PIPE, 
                                              stderr=subprocess.PIPE, text=True)

        # Wait for the process to complete and capture output
        stdout, stderr = stitchNode_process.communicate()

        path,_=os.path.split(input_filelist)
        outfile=path+'/stitchNodes_outlog.txt'
        with open(outfile, 'w') as file:
            file.write(stdout)
        outfile=path+'/stitchNodes_errlog.txt'
        with open(outfile, 'w') as file:
            file.write(stderr)
        if not quiet:
             return stdout, stderr
