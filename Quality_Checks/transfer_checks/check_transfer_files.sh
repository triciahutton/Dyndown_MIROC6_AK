shopt -s nullglob  # google says to use for safety-avoid errors if nothing

for year_dir in /beegfs/datasets/DYNDOWN/MIROC6ssp370/post_proc-s*/; do
  YEAR=${year_dir##*-s}
        #extract year for directories after -s 
  echo "Checking files for YEAR=$YEAR"

  # loop over the 3 resolutions 
  for file in "$year_dir"{12km,4km,1_33km}/*; do
    if [ ! -f "$file" ] || [ ! -s "$file" ]; then
            #if file DOES NOT exist  (-f)  or||  if file exists but has zero size
            echo "$file is missing or zero size"
            #tell me which is missing 
    fi
  done
done
