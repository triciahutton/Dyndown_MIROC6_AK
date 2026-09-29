import xarray as xr
from pathlib import Path

INPUT_DIR = Path("/center1/DYNDOWN/phutton5/CMIP6/Exploring_MIROC6/statewide_gridcell/12kmdscaledERA5")

START_YEAR = 2010
END_YEAR = 2025

VARIABLES = ["TSLB", "temp",]

OUTPUT_FILE = (INPUT_DIR /f"daily_temp_soil_gridcells_{START_YEAR}_{END_YEAR}_dscaledERA5_MAXCOMPRESSED.nc")
#make sure this is the right name for the variables condensing 

files = []
for year in range(START_YEAR, END_YEAR + 1):
    f = INPUT_DIR / f"grid_cells_{year}.nc"
    if f.exists():
        files.append(f)
    else:
        print(f"WARNING: Missing file: {f}")

print("Files being combined:")
for f in files:
    print( f"  {f.name}")

print(f"\nFound {len(files)} files.")
if not files:
    raise FileNotFoundError(
        f"No yearly files found for "
        f"{START_YEAR}-{END_YEAR}")

print( "\nOpening yearly files...")

ds = xr.open_mfdataset(files, combine="by_coords",chunks={"Time": 30},data_vars="minimal",coords="minimal",compat="override")
print("\nDataset:")
print(ds)

print( "\nChecking variables...")
for var in VARIABLES:
    if var not in ds:
        ds.close()
        raise KeyError(
            f"Variable {var!r} "
            f"was not found in the dataset.")

    print(f"{var}: "
        f"{ds[var].dims} "
        f"{ds[var].shape}")

print("\nConverting variables to float32...")
for var in VARIABLES:
    ds[var] = ds[var].astype("float32")

encoding = {}
encoding["TSLB"] = {"zlib": True,
    "complevel": 9,"shuffle": True,"dtype": "float32","least_significant_digit": 2,
    "chunksizes": (30,
        4,#only if variables with height
        50,
        50)}

encoding["temp"] = {"zlib": True,"complevel": 9,"shuffle": True,"dtype": "float32","least_significant_digit": 2,
    "chunksizes": (30,
        4,
        50,
        50)}

print( "\nWriting maximally compressed file:")

print(f"  {OUTPUT_FILE}")
ds.to_netcdf(OUTPUT_FILE, mode="w",format="NETCDF4", encoding=encoding)
ds.close()

file_size_gb = (OUTPUT_FILE.stat().st_size/ 1024**3)
print("\nFinished!")
print(f"Output: " f"{OUTPUT_FILE}")
print(f"Size: " f"{file_size_gb:.2f} GB")
