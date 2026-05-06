#!/bin/sh

echo $1

yr=$1

if [[ yr -lt 1978 || yr -gt 2100 ]]; then
echo "bad year entry"
exit
fi

cd /glade/campaign/uwyo/wyom0200/alaska/miroc6/ssp370
mkdir out-s${yr}
cd /glade/derecho/scratch/pbieniek/dscale/miroc6

cd wps
cp -r wps-dscale_tpl wps-s${yr}
cd ../wrf
cp -r run-dscale_tpl run-s${yr}
cd run-s${yr}

JNAME="s_${yr}"

eyr=`expr $yr + 6`
sed -e "s/SYY/${yr}/" -e "s/EYY/${eyr}/" -e "s/JNAME/${JNAME}/" wrf_dscale.sh-tpl  > miroc6_wrf-$yr-07-01.sh
#chmod +x miroc6_wrf-$yr-07-01.sh
qsub miroc6_wrf-$yr-07-01.sh

cd ../..

exit
