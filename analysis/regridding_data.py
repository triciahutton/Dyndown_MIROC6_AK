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


dscaledera5_12km='/center1/DYNDOWN/phutton5/CMIP6/Exploring_MIROC6/statewide_gridcell/12kmdscaledERA5'
dscaledera5_12km_file='daily_temp_soil_all_gridcells_1990_1999_dscaledERA5_MAXCOMPRESSED.nc'
miroc6_12km='/center1/DYNDOWN/phutton5/CMIP6/Exploring_MIROC6/statewide_gridcell/12km'
miroc6_12km_file='daily_T2_TSK_SLP_gridcells_1979_1989_MAXCOMPRESSED.nc'

dscaled12toregrid=xr.open_dataset(dscaledera5_12km+'/'+dscaledera5_12km_file)
miroc6_12kmsource=xr.open_dataset(miroc6_12km+'/'+miroc6_12km_file)

#change output file depening on input file variables 
output_file = ("/center1/DYNDOWN/phutton5/CMIP6/Exploring_MIROC6/"
    "statewide_gridcell/12kmdscaledERA5/"
    "daily_temp_soil_all_gridcells_1990_1999_dscaledERA5_MAXCOMPRESSED_"
    "regridded_to_miroc6_12kmdscaledERA5.nc")

lat_miroc = miroc6_12kmsource["XLAT"]
lon_miroc = miroc6_12kmsource["XLONG"]

lat_dscaled = dscaled12toregrid["XLAT"]
lon_dscaled = dscaled12toregrid["XLONG"]

print("ERA5/dscaled lat shape:", lat_dscaled.shape)
print("ERA5/dscaled lon shape:", lon_dscaled.shape)

print("MIROC lat shape:", lat_miroc.shape)
print("MIROC lon shape:", lon_miroc.shape)

print("ERA5/dscaled latitude range:", float(lat_dscaled.min()),"to",float(lat_dscaled.max()))
print("ERA5/dscaled longitude range:",float(lon_dscaled.min()), "to",float(lon_dscaled.max()))
print("MIROC latitude range:",float(lat_miroc.min()),"to",float(lat_miroc.max()))
print("MIROC longitude range:",float(lon_miroc.min()),"to",float(lon_miroc.max()))

miroc_inside_era5 = ((lat_miroc >= lat_dscaled.min()) &
    (lat_miroc <= lat_dscaled.max()) &
    (lon_miroc >= lon_dscaled.min()) &
    (lon_miroc <= lon_dscaled.max()))

ys, xs = np.where(miroc_inside_era5.values)
if len(ys) == 0:
    raise ValueError("No MIROC grid cells were found inside the ERA5/dscaled domain...")

y_min = ys.min()
y_max = ys.max()

x_min = xs.min()
x_max = xs.max()

print("Original MIROC shape:", lat_miroc.shape)
print("MIROC south_north indices:", y_min, "to", y_max)
print("MIROC west_east indices:", x_min, "to", x_max)


lat_miroc_sub = lat_miroc.isel(south_north=slice(y_min, y_max + 1), west_east=slice(x_min, x_max + 1))

lon_miroc_sub = lon_miroc.isel(south_north=slice(y_min, y_max + 1), west_east=slice(x_min, x_max + 1))

print("Subset MIROC shape:", lat_miroc_sub.shape)

src_grid = xr.Dataset({"lat": lat_dscaled,"lon": lon_dscaled})

tgt_grid = xr.Dataset({"lat": lat_miroc_sub,"lon": lon_miroc_sub})

regridder = xe.Regridder(src_grid,tgt_grid, method="nearest_s2d", #can change this to bilinear
    periodic=False,reuse_weights=False)

vars_to_regrid = [v
    for v in dscaled12toregrid.data_vars
    if {"south_north", "west_east"}.issubset(
        dscaled12toregrid[v].dims)]

print("Number of variables to regrid:", len(vars_to_regrid))
print(vars_to_regrid)

dscaled_to_miroc = xr.Dataset()

for v in vars_to_regrid:
    print(f"Regridding {v}...")
    dscaled_to_miroc[v] = regridder(dscaled12toregrid[v])

miroc_inside_era5_sub = miroc_inside_era5.isel(south_north=slice(y_min, y_max + 1),west_east=slice(x_min, x_max + 1))

for v in dscaled_to_miroc.data_vars:
    dscaled_to_miroc[v] = dscaled_to_miroc[v].where(miroc_inside_era5_sub)

print(dscaled_to_miroc)
print("\nOriginal dataset estimated memory:",dscaled12toregrid.nbytes / 1e9,"GB")
print("Regridded dataset estimated memory:",dscaled_to_miroc.nbytes / 1e9, "GB")
print("\nOriginal MIROC spatial shape:",lat_miroc.shape)
print("Subset MIROC spatial shape:", lat_miroc_sub.shape)

encoding = {}

for v in dscaled_to_miroc.data_vars:
    original_dtype = dscaled12toregrid[v].dtype
    encoding[v] = {"zlib": True,"complevel": 9,"shuffle": True,"dtype": original_dtype}

dscaled_to_miroc.to_netcdf(output_file,encoding=encoding)

print("\nSaved regridded ERA5 → MIROC data to:")
print(output_file)

