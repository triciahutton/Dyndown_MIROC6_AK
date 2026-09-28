#!/usr/bin/env python3
import xarray as xr
import numpy as np
from pathlib import Path

BASE_DIR = Path("/beegfs/datasets/DYNDOWN/MIROC6ssp370/12km")

OUTPUT_DIR = Path("/center1/DYNDOWN/phutton5/CMIP6/Exploring_MIROC6/statewide_gridcell/12km")

START_YEAR = 1990 #change to anything from 1979 - 2100 for MIROC6 downscaled data
END_YEAR = 1999 #change to anything from 1979 - 2100 for MIROC6 downscaled data

# Variables to extract
VARIABLES = ["TSLB", "temp"]

SOIL_VARIABLES = ["TSLB",]
PRESSURE_VARIABLES=["temp",]

PLEV_DIM='interp_level'
PRESSURE_LEVELS = [850, 925, 950, 1000]

SOIL_DIM='soil_layers_stag'
SOIL_LAYERS = [0, 1, 2, 3]

# WRF spatial dimensions
YDIM = "south_north"
XDIM = "west_east"

OUTPUT_DIR.mkdir(parents=True,exist_ok=True)

# PROCESS EACH YEAR
for year in range(START_YEAR, END_YEAR + 1):
    print(f"PROCESSING YEAR {year}")
    output_file = (OUTPUT_DIR / f"temp_soil_12km_{year}.nc")
    print(f"Output file:\n  {output_file}")
    print(f"\nSearching for NetCDF files for {year}...")

    files = sorted([f for f in BASE_DIR.rglob("*.nc")if (str(year) in f.name or str(year) in str(f.parent))])
    if not files:
        print(f"No NetCDF files found for {year}")
        continue

    print(f"Found {len(files)} NetCDF files for {year}")
    print("\nFirst files:")

    for f in files[:10]:
        print(f"  {f}")
    if len(files) > 10:
        print(f"  ... and {len(files) - 10} more files")

    print("\nOpening WRF files...")
    ds = xr.open_mfdataset(files,combine="by_coords", chunks={"Time": 168}, data_vars="minimal", coords="minimal", compat="override", parallel=False)
    print(f"Dataset dimensions: {dict(ds.sizes)}")

    available_variables = list(ds.data_vars)
    missing_variables = [variable for variable in VARIABLES if variable not in ds]
    if missing_variables:
        ds.close()

        raise KeyError(f"\nThe following requested variables "
            f"were not found for {year}:\n\n"
            f"Missing :\n"
            f"{missing_variables}\n"
            f"Available variables are :\n"
            f"{available_variables}")

    print("\nVariables being extracted!!!... ")
    for variable in VARIABLES:
        print(f"\n{variable}:")
        print(f"  dimensions: "
            f"{ds[variable].dims}")
        print(f"  shape: "
            f"{ds[variable].shape}")

    for variable in VARIABLES:
        data_variable = ds[variable]
        if (YDIM not in data_variable.dims
            or XDIM not in data_variable.dims):
            ds.close()
            raise ValueError(f"\n{variable} does not contain "
                f"the expected spatial dimensions.\n\n"
                f"Expected:\n"
                f"  {YDIM}\n"
                f"  {XDIM}\n\n"
                f"Actual:\n"
                f"  {data_variable.dims}")
              
    # CHECK GRID SIZE
    y_size = ds[VARIABLES[0]].sizes[YDIM]
    x_size = ds[VARIABLES[0]].sizes[XDIM]
    print("\nSpatial grid:")
    print(f"  {YDIM}: {y_size}")
    print(f"  {XDIM}: {x_size}")
    print(f"  Total grid cells: "
        f"{y_size * x_size:,}")

    for variable in VARIABLES:
        variable_y_size = (ds[variable].sizes[YDIM])
        variable_x_size = (ds[variable].sizes[XDIM])

        if (variable_y_size != y_size or variable_x_size != x_size):
            ds.close()

            raise ValueError(f"\n{variable} has a different "
                f"spatial grid.\n\n"
                f"{VARIABLES[0]}:\n"
                f"  {YDIM} = {y_size}\n"
                f"  {XDIM} = {x_size}\n\n"
                f"{variable}:\n"
                f"  {YDIM} = {variable_y_size}\n"
                f"  {XDIM} = {variable_x_size}")

    print("\n Selecting Variables and specific levels...")

    data_arrays={}
    for variable in VARIABLES:
        da=ds[variable]
        if variable in SOIL_VARIABLES:
            if SOIL_DIM not in da.dims:
                ds.close()
                raise ValueError(
                    f"\n{variable} does not contain the "
                    f"expected soil dimension '{SOIL_DIM}'.\n\n"
                    f"Actual dimensions:\n"
                    f"  {da.dims}")

            da=da.isel({SOIL_DIM: SOIL_LAYERS})
        elif variable in PRESSURE_VARIABLES:
            if PLEV_DIM not in da.dims:
                ds.close()
                raise ValueError(
                    f"\n{variable} does not contain the "
                    f"expected pressure-level dimension "
                    f"'{PLEV_DIM}'.\n\n"
                    f"Actual dimensions:\n"
                    f"  {da.dims}")

            da=da.sel({PLEV_DIM: PRESSURE_LEVELS})
        data_arrays[variable] = da

    data=xr.Dataset(data_arrays)

    #CALCULATING DAILY MEANS
    print("\nCalculating daily means...")
    daily = (data.resample(Time="1D").mean())

    print(f"Daily timesteps: "
        f"{daily.sizes['Time']}")

    print(f"Daily dimensions: "
        f"{dict(daily.sizes)}")

    daily = daily.assign_coords(year=year)
    cell_id = (np.arange(y_size * x_size).reshape(y_size,x_size))

    daily = daily.assign_coords( cell_id=([YDIM, XDIM],cell_id))

    # COMPUTE
    print("\nComputing daily grid-cell data...")

    daily = daily.compute()
    print("Computation complete")
    ds.close()
    print("WRF dataset closed")

    daily.attrs = {"description":
            "Daily mean WRF data for every individual "
            "12-km grid cell",
        "variables":
            "TSLB,temp",
        "year":year,
        "spatial_dimensions":
            f"{YDIM}, {XDIM}",
        "grid_cells":
            y_size * x_size,
        "created_by":
            "Individual grid-cell extraction"}

    encoding = {}
    for variable in VARIABLES:
        dims=daily[variable].dims
        if len(dims) == 4 :
            extra_dim=dims[1]
            extra_size=daily[variable].sizes[extra_dim]
            chunksizes= (30, extra_size, 50, 50)
        else:
            chunksizes=(30,50,50)

        encoding[variable] = {"zlib": True,
            "complevel": 9,
            "shuffle": True,
            "dtype": "float32",
            "chunksizes": chunksizes}

    print("\nWriting NetCDF:")
    print(f"  {output_file}")
    daily.to_netcdf(output_file,mode="w", format="NETCDF4", encoding=encoding)

    print("\nVerifying output...")
    check = xr.open_dataset(output_file)
    print(check)
    print("\nOutput dimensions:")
    print(dict(check.sizes))
    print("\nOutput variables:")
    print(list(check.data_vars))
    check.close()

    del daily
    del data
  
    print(f"\nFinished year {year}.")

# FINISHED
print("ALL YEARS COMPLETE")
print("\nOutput directory:")
print(f"  {OUTPUT_DIR}")
