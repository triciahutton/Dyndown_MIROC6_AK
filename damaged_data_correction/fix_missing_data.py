#6 files were corrupt in the trasfer, missing hours of data here and there.
#This script copied the prior day in the year and overwrote the damaged data with the previous day.
'''
12km  /wrf_dscale_12km_1989-11-11.nc Final fix from time step issue. (July 6 2026)
4km final fix wrf_dscale_4km_1991-08-19.nc
wrf_dscale_4km_2000-10-11.nc
4km  wrf_dscale_4km_2020-04-08.nc, extra time step was saved but removed. (Fixed July 6 2026)
'''

import netCDF4 as nc
import numpy as np
import os
from datetime import datetime, timedelta

path = '/center1/DYNDOWN/phutton5/CMIP6/MIROC6_damaged_data'
old_name = "wrf_dscale_4km_2000-10-10.nc"
new_name = "wrf_dscale_4km_2000-10-11.nc"

old_path = os.path.join(path, old_name)
new_path = os.path.join(path, new_name)
#os.rename(old_path, new_path)
#UNCOMMENT OUT TO RENAME THE FILE

with nc.Dataset(new_path, "r+") as ds:
    ds.comment = "error in extraction, copied day before for fluent dataset"
    # Update Time variable (hours since date)
    if "Time" in ds.variables:
        time_var = ds.variables["Time"]
        units = getattr(time_var, "units", "")
        print("Before - Time values:", time_var[:])
        print("Before - Time units:", units)
        time_var[:] = time_var[:] + 24
        time_var.units = units.replace("2000-10-10", "2000-10-11")
        print("After  - Time values:", time_var[:])
        print("After  - Time units:", time_var.units)

    # Update XTIME variable
    if "XTIME" in ds.variables:
        xtime_var = ds.variables["XTIME"]
        print("Before - XTIME:", xtime_var[:])
        xtime_var[:] = xtime_var[:] + 1440
        print("After  - XTIME:", xtime_var[:])
print("Done!")



#If the issue is an extra hour was included (April 8 2020) then run this portion of the code.
#this date had one hour that ended in :06 instead of :00 ....

'''
import xarray as xr
import pandas as pd
#path to data with extra hour...
original = '/center1/DYNDOWN/phutton5/CMIP6/MIROC6_damaged_data/wrf_dscale_4km_2020-04-08_extra.nc'
#path to data named final out put...
fixed = '/center1/DYNDOWN/phutton5/CMIP6/MIROC6_damaged_data/wrf_dscale_4km_2020-04-08.nc'

ds = xr.open_dataset(original)
# Keep only exact on-the-hour timesteps
mask = (pd.DatetimeIndex(ds.Time.values).minute == 0) & \
       (pd.DatetimeIndex(ds.Time.values).second == 0)

ds_clean = ds.isel(Time=mask)

# Verify
print(f"Before: {len(ds.Time)} timesteps")
print(f"After:  {len(ds_clean.Time)} timesteps")
print(ds_clean.Time.values)

# Save
ds_clean.to_netcdf(fixed)
'''
