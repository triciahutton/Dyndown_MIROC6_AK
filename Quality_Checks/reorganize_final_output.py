!/usr/bin/env python3
"""
#USED CLAUDE TO HELP ADJUST THIS CODE!
reorganize_wrf_files.py
Moves WRF files from:
    /beegfs/datasets/DYNDOWN/MIROC6ssp370/post_proc-s<YYYY>/<DOMAIN>/<files>.nc
Into:
    /beegfs/datasets/DYNDOWN/MIROC6ssp370/<DOMAIN>/<YEAR>/<files>.nc
Usage:
    python reorganize_wrf_files.py [--dry-run] [--on-conflict skip|overwrite|abort]
"""

import re
import shutil
import argparse
from pathlib import Path

BASE_DIR = Path("/beegfs/datasets/DYNDOWN/MIROC6ssp370")

POST_PROC_YEARS = list(range(1999, 2096, 4))

DOMAINS = ["12km", "4km", "1_33km"]

FILENAME_RE = re.compile(r"^wrf_dscale_.+?_(\d{4})-\d{2}-\d{2}\.nc$")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Reorganize WRF NetCDF files from post_proc folders into domain/year layout."
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print what would happen without moving any files."
    )
    parser.add_argument(
        "--on-conflict", choices=["skip", "overwrite", "abort"], default="skip",
        help="What to do if a destination file already exists (default: skip)."
    )
    return parser.parse_args()


def main():
    args = parse_args()
    dry_run = args.dry_run
    on_conflict = args.on_conflict

    if dry_run:
        print("*** DRY RUN — no files will be moved ***\n")

    moved = skipped = warnings = errors = 0

    for year in POST_PROC_YEARS:
        src_folder = BASE_DIR / f"post_proc-s{year}"

        if not src_folder.is_dir():
            print(f"[WARN] Not found, skipping: {src_folder}")
            warnings += 1
            continue

        for domain in DOMAINS:
            domain_src = src_folder / domain

            if not domain_src.is_dir():
                continue

            nc_files = sorted(domain_src.glob("*.nc"))
            if not nc_files:
                print(f"[WARN] No .nc files in {domain_src}")
                warnings += 1
                continue

            for nc_file in nc_files:
                m = FILENAME_RE.match(nc_file.name)
                if not m:
                    print(f"[WARN] Unexpected filename, skipping: {nc_file.name}")
                    warnings += 1
                    continue

                file_year = m.group(1)
                dest_folder = BASE_DIR / domain / file_year
                dest_file = dest_folder / nc_file.name

                if dest_file.exists():
                    if on_conflict == "skip":
                        print(f"[SKIP] Already exists: {dest_file}")
                        skipped += 1
                        continue
                    elif on_conflict == "abort":
                        raise FileExistsError(f"Destination exists (aborting): {dest_file}")
                    # overwrite: fall through

                action = "WOULD MOVE" if dry_run else "MOVE"
                print(f"[{action}] post_proc-s{year}/{domain}/{nc_file.name}")
                print(f"         -> {domain}/{file_year}/{nc_file.name}")

                if not dry_run:
                    try:
                        dest_folder.mkdir(parents=True, exist_ok=True)
                        shutil.move(str(nc_file), str(dest_file))
                        moved += 1
                    except Exception as e:
                        print(f"[ERROR] {nc_file.name}: {e}")
                        errors += 1
                else:
                    moved += 1

    print("\n-----------------------------------------")
    print(f"  {'Would move' if dry_run else 'Moved'} : {moved}")
    print(f"  Skipped  : {skipped}")
    print(f"  Warnings : {warnings}")
    print(f"  Errors   : {errors}")
    print("-----------------------------------------")


if __name__ == "__main__":
    main()
~                                                                                        
~                    
