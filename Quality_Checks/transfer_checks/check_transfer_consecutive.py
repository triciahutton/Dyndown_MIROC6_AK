import os
import re
import glob
from datetime import datetime, timedelta
BASE_DIR= '/beegfs/datasets/DYNDOWN/MIROC6ssp370'
INNER_DIRS = ["12km", "4km", "1_33km"]

def check_sequential_dates(data_dir):
    pattern = r'.*_(\d{4})-(\d{2})-(\d{2}).*'
    dates = []

    for file in os.listdir(data_dir):
        match = re.search(pattern, file)
        if match:
            year, month, day = match.groups()
            file_date = datetime(int(year), int(month), int(day))
            dates.append(file_date)

    if not dates:
        print(f"No dated files found in {data_dir}")
        return False

    dates.sort()

    for i in range(1, len(dates)):
        expected_date = dates[i-1] + timedelta(days=1)
        if dates[i] != expected_date:
            print(f"[{data_dir}] Missing date: {expected_date.date()} "
                  f"between {dates[i-1].date()} and {dates[i].date()}")
            return False

    print(f"[{data_dir}] All dates are sequential.")
    return True


# Loop over post_proc-s*
postproc_dirs = glob.glob(os.path.join(BASE_DIR, "post_proc-s*"))

for post_dir in sorted(postproc_dirs):
    print(f"\nChecking {post_dir}")

    for inner in INNER_DIRS:
        inner_path = os.path.join(post_dir, inner)

        if os.path.isdir(inner_path):
            check_sequential_dates(inner_path)
        else:
            print(f"{inner_path} does not exist.")
~                                                      
