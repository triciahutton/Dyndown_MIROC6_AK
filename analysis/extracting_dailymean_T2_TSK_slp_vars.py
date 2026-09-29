#!/usr/bin/env python3

import xarray as xr
from pathlib import Path


BASE_DIR = Path("/beegfs/datasets/DYNDOWN/MIROC6ssp370/12km")
#change final location to 4km or 12km depending on resoltuion extraction 
OUTPUT_DIR = Path("/center1/DYNDOWN/phutton5/CMIP6/"
    "Exploring_MIROC6/statewide_gridcell/12km")
#change final location to 4km or 12km depending on resoltuion extraction 

START_YEAR = 1979
END_YEAR = 1999
#change from 1979-2100 but do not exceed time limit of node

VARIABLES = ["T2", "TSK", "slp"]

YDIM = "south_north"
XDIM = "west_east"
TDIM = "Time"

OUTPUT_DIR.mkdir(parents=True,exist_ok=True)

for year in range(START_YEAR,END_YEAR + 1):
    print(f"PROCESSING YEAR {year}")
    year_dir = BASE_DIR / str(year)
    files = sorted(year_dir.glob("wrf_dscale_*.nc"))

    if not files:
        print(f"No files found for {year}")
        continue
    print(f"Found {len(files)} files")

    output_file = ( OUTPUT_DIR /f"daily_all_gridcells_{year}.nc")

    if output_file.exists():
        print(f"Output already exists:"
            f"\n  {output_file}")
        print("Skipping this year")
        continue

    print( "\nOpening WRF files...")

    ds = xr.open_mfdataset(files,combine="by_coords",chunks={TDIM: 168},data_vars="minimal",coords="minimal",compat="override",parallel=False)

    print("Dataset opened")
    print("\nDataset dimensions:")

    print(ds.dims)
    print( "\nChecking requested variables...")

    missing_variables = [ variable
        for variable in VARIABLES
        if variable not in ds]

    if missing_variables:
        print("\nERROR: The following variables "
            "were not found:")

        for variable in missing_variables:
            print(f" {variable}")

        print("\nVariables available in dataset:")

        for variable in ds.data_vars:
            print(f"  {variable}")

        ds.close()
        raise ValueError( "One or more requested variables were not found")

    print("All requested variables found:")

    for variable in VARIABLES:
        print(f"  {variable}")

    print("\nRequested variable information:")

    for variable in VARIABLES:
        print(f"\n--- {variable} ---")
        print(ds[variable])

    data = ds[VARIABLES]
  
    print("Calculating daily means for every grid cell...")
    daily = (data.resample({TDIM: "1D"}).mean())

    print("\nDaily timesteps:")
    print(f"  {daily.sizes[TDIM]}")
    print("\nGrid dimensions:")
    print(f"  {YDIM}: " f"{daily.sizes[YDIM]}")

    print(f"  {XDIM}: "f"{daily.sizes[XDIM]}")
    print("\nTotal grid cells:")
    print(f"  {daily.sizes[YDIM] * daily.sizes[XDIM]:,}")
    print("\nVariables being saved:")

    for variable in daily.data_vars:
        print(f"  {variable}")

    daily.attrs["description"] = ("Daily mean WRF variables for every 12-km grid cell")
    daily.attrs["spatial_aggregation"] = ( "None - individual grid cells retained")
    daily.attrs["temporal_aggregation"] = ("Daily mean")
    daily.attrs["source"] = ("MIROC6ssp370 downscaled WRF 12-km data")
    daily.attrs["processing_year"] = year
    encoding = {}
    for variable in VARIABLES:
        encoding[variable] = {"zlib": True, "complevel": 9,"shuffle": True, "dtype": "float32","chunksizes": (30, 50, 50)}

    print("Writing NetCDF:")
    print(f"  {output_file}")
    daily.to_netcdf(output_file,mode="w",format="NETCDF4", encoding=encoding)
  
    file_size_gb = (output_file.stat().st_size/ (1024 ** 3))
    print("\nNetCDF successfully written")
    print(f"Output size: "
        f"{file_size_gb:.2f} GB")

    del daily
    del data
    ds.close()
    print(f"FINISHED YEAR {year}")

print("PROCESSING COMPLETE")
print(f"Years: "
    f"{START_YEAR}-{END_YEAR}")

print("\nVariables:")

for variable in VARIABLES:
    print(f"  {variable}")
print(f"\nOutput directory:"
    f"\n{OUTPUT_DIR}")
print("\nDaily means were calculated independently for every 12-km grid cell.")
