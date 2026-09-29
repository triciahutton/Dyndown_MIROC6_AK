import xarray as xr
import os
import glob
import geopandas as gpd
import pandas as pd
import matplotlib.colors as mcolors
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import xesmf as xe
import matplotlib.pyplot as plt

#RUN THIS AFTER EXTRACTED THE 4km T2 TSK SLP... 
#loading in all the MIROC6 datasets (4km)

miroc_4km = '/center1/DYNDOWN/phutton5/CMIP6/Exploring_MIROC6/statewide_gridcell/4km'
files = sorted(glob.glob(miroc_4km +'/daily_all_gridcells_*_MAXCOMPRESSED.nc'))

print(f'Found {len(files)} files:')
for f in files:
    print(os.path.basename(f))

miroc_4km = xr.open_mfdataset(files,combine='by_coords')
print('Start:', miroc_4km['Time'].min().values)
print('End:', miroc_4km['Time'].max().values)
print('Number of days:', miroc_4km['Time'].size)

miroc_4km = miroc_4km.isel(west_east=slice(0, 642))
#creating monthly data for dscaled MIROC 4km 
test_miroc_4km=miroc_4km.resample(Time='MS').mean(dim='Time',skipna=True)
miroc_output = ('/center1/DYNDOWN/phutton5/CMIP6/Exploring_MIROC6/statewide_gridcell/4km/monthly_dscaledmiroc_T2_TSK_slp_1979_2025.nc')
#need to change the output fine name!!
test_miroc_4km.to_netcdf(miroc_output,format='NETCDF4')

