# Dyndown
UAF Masters Research, Dynamically Downscaling CMIP6 Models
Scripts were run on NCARs HPC- Derecho (if needed on chinook adjustments must be made) 

Found within post-processing folder:
-
**remove_var_startup_mpi.sh [year]** - when this script is run, the folder post_proc-tpl folder is produced. Example remove_var_startup_mpi.sh 2005 creates the folder post_proc-2004 

**post_proc-tpl** folder consists of scripts needed to extract from the WRF output. Inlcuding scripts **check_files.py**, **crontab -e**, **extract_vars.py**, **extract_vars_pool_tricia.py**, **missing_days_run_ext.sh**, **run_check_files.sh**, **run_extvar.sh**, and **update_and_run.sh**

**extract_vars_pool_tricia.py**- Post processing script used to extract variables from the wrf out files. *Current not most efficient, where need to go back through and remove some specific variables from domains (i.e. sea ice from 1.33 km domain- see remove_var_mpi scripts below) 

**run_extvar.sh** - run the script extract_vars_pool_tricia.py with all necessary inputs, as well as logs to log_date_file.log of startdate, AND python log file

**update_and_run.sh** - reads in date from log_date_file.log, adds 6 days and overwrites run_extvar.sh to new start date to begin processing the next chunk of data 

**move_postproc_out.sh** - takes all post processed data from the output directory (post_proc_out) and moves them into campaign storage in 12km 4km and 1.33km folders 

**check_files.py** - reads each file and counts how many are available to post process from the wrf out file, count how many have already been post processed, and finds the last date in the post processed folder, and checks to make sure all the files are consecutive! (first check by Tricia)
**run_check_files.sh** - runs the python script of check files 

extract_vars.py- original code from Chris, later adjusted and adapted to fit for CMIP6, orginally for ERA5 dyndown (https://github.com/chryss/dyndowntools/tree/main)

Folder within Post processing folder: **remove_var_mpi**

this folder consists of 3 scripts, one for each domain (12km, 4km, and 1.33km) which extracted the final variables which were not properly completed in the orignal extract_vars_pool_trici.py script. (ex. removing the seaice from 1.33km domain) **remove_var_12_mpi.py** ,  **remove_var_133_mpi.py** , **remove_var_4_mpi.py** and **run_remove_var_12_mpy.py**

