;Created by S. Rahimi on 21 Apr. 2020
;to ingest CMIP6 CESM2 output in prep
;for output to intermdediate binary
;form for use by metgrid

;Version 2.0 of first.ncl. Uses a more
;sophisticated startdate/enddate format

;Variables do not all have the same
;temporal starting point!!!!!!!

;Call this library to link the NCL
;and FORTRAN codes
;;;external DRIVEWRFWITH "./bf90.so"
external DRIVEWRFWITH "./binary_cesm2_seaice.so"

;16 variables drive WRF
;12 different CMIP6 files should be downloaded

;3-D vars are 6-hourly
;--on the CAM grid
;ua, va, ta, pa, and hus  (5 total)
; __  __  __          __   (4 needed from CMIP)

;2-D vars
;--on the CAM grid
;tslsi
;ps, pmsl are 6-hourly    (2 total)

;daily                    (6 total)
;--not on the CAM grid (gx1v7)
;tos
;__

;--on the CAM grid
;mrsol (3-D), tslsi
; ____        _____

;huss, tas, tsl
; ___   ___  __
;missing                  (2 total)
;u10, v10,

;static
;orog, sftlf              (2 total)
; ____  ____
;All variables must be interpolated to
;the CAM 0.9x1.25 fv horizontal grid

;data interpolated to 25 p-levels

begin

;MASTER DIRECTORY | where are your CESM2 files
dir_in = "./hist_cesm2/"

start_year = 1979
end_year = 1979
start_month = 1
end_month = 12
start_day = 1
end_day = 31
start_hour = 0
end_hour = 18

option = 0
option@calendar = "no_leap"

timevalue_start = cd_inv_calendar(start_year,start_month,start_day, \
                        start_hour,0,0,"days since 0001-01-01 00:00:00",option)

timevalue_end = cd_inv_calendar(end_year,end_month,end_day, \
                        end_hour,0,0,"days since 0001-01-01 00:00:00",option)

;Misc.
dumpout = "FALSE"
corr = 0.000001
g = 9.81
T0 = 273.15
iswitch = 0

;p-levels to interpolate to
lev_p_mb = tofloat((/1000,975,950,925,900, \
           850,800,750,700, \
           650,600,550,500, \
           450,400,350,300, \
           250,200,150,100, \
           70, 50, 30, 10/))

;For interpolation
lev_p_mb!0 = "lev_p"
lev_p_mb&lev_p  =  lev_p_mb
lev_p_mb@long_name = "pressure"
lev_p_mb@units     = "hPa"
lev_p_mb@positive  = "down"
np = dimsizes(lev_p_mb)

;For writing to the binary files
lev_p_pa = lev_p_mb * 100
lev_p_mb&lev_p  =  lev_p_pa

;Read in the static files
f_orog = addfile(dir_in+"orog_fx_CESM2_historical_r11i1p1f1_gn.nc","r")
z_sfc = f_orog->orog
f_sftlf = addfile(dir_in+"sftlf_fx_CESM2_historical_r11i1p1f1_gn.nc","r")
landsea = f_sftlf->sftlf
lat_cam = f_sftlf->lat
lon_cam = f_sftlf->lon

file_str = "ua_*"
filei = systemfunc("cd " + dir_in + " ; ls " + file_str)
f_ua = addfiles(dir_in+filei,"r")

file_str = "va_*"
filei = systemfunc("cd " + dir_in + " ; ls " + file_str)
f_va = addfiles(dir_in+filei,"r")

file_str = "ta_*"
filei = systemfunc("cd " + dir_in + " ; ls " + file_str)
f_ta = addfiles(dir_in+filei,"r")

file_str = "hus_*"
filei = systemfunc("cd " + dir_in + " ; ls " + file_str)
f_hus = addfiles(dir_in+filei,"r")

delete(filei)

file_str = "tos_*"
filei = systemfunc("cd " + dir_in + " ; ls " + file_str)
f_tos = addfiles(dir_in+filei,"r")
delete(filei)

file_str = "tas_*"
filei = systemfunc("cd " + dir_in + " ; ls " + file_str)
f_tas = addfiles(dir_in+filei,"r")
delete(filei)

file_str = "tsl_*"
filei = systemfunc("cd " + dir_in + " ; ls " + file_str)
f_tsl = addfiles(dir_in+filei,"r")
delete(filei)

;Remember! CESM2 HAS skin temperature over land!
file_str = "tslsi_*"
filei = systemfunc("cd " + dir_in + " ; ls " + file_str)
f_tslsi = addfiles(dir_in+filei,"r")
delete(filei)

file_str = "mrsol_*" ;[kg/m2] -- needs to be in a fraction
filei = systemfunc("cd " + dir_in + " ; ls " + file_str)
f_mrsol = addfiles(dir_in+filei,"r")
delete(filei)

file_str = "huss_*"
filei = systemfunc("cd " + dir_in + " ; ls " + file_str)
f_huss = addfiles(dir_in+filei,"r")
delete(filei)

file_str = "siconc_*"
filei = systemfunc("cd " + dir_in + " ; ls " + file_str)
f_siconc = addfiles(dir_in+filei,"r")
delete(filei)

;Timing -- specific for each variable
;to ensure correct time is used for each
time_ua = f_ua[:]->time
time_ta = f_ta[:]->time
time_va = f_va[:]->time
time_hus = f_hus[:]->time
time_tos = f_tos[:]->time
time_tas = f_tas[:]->time
time_tsl = f_tsl[:]->time
time_tslsi = f_tslsi[:]->time
time_mrsol = f_mrsol[:]->time
time_huss = f_huss[:]->time
time_siconc = f_siconc[:]->time

utc_tos = cd_calendar(time_tos, 0)
utc_tsl = cd_calendar(time_tsl, 0)
utc_tslsi = cd_calendar(time_tslsi, 0)
utc_huss = cd_calendar(time_huss, 0)
utc_mrsol = cd_calendar(time_mrsol, 0)
utc_tas = cd_calendar(time_tas, 0)
utc_siconc = cd_calendar(time_siconc, 0)

;Define reference time index array based
;on 6-h ua. Make sure the startdate mathces
;the first time in this array
time_master = f_ua[:]->time
utc_master = cd_calendar(time_master, 0)

;Find start_master and end_master indices
start_master = ind(time_master .eq. timevalue_start)
end_master = ind(time_master .eq. timevalue_end)


print(start_master+" "+end_master)

do itime = start_master, end_master
 print("itime = "+itime)
 ;Based on 6-h intervals
 year   = tointeger(utc_master(itime,0))
 month  = tointeger(utc_master(itime,1))
 day   = tointeger(utc_master(itime,2))
 hour   = tointeger(utc_master(itime,3))
 minute = tointeger(utc_master(itime,4))
 second = tointeger(utc_master(itime,5))

 date_str6 = sprinti("%0.2i", year)+ "-"+ sprinti("%0.2i", month)+ \
             "-"+ sprinti("%0.2i", day)+ "_"+ sprinti("%0.2i", hour)+ \
             ":"+ sprinti("%0.2i", minute)+ ":"+ sprinti("%0.2i", second)

 ;Daily time vaule
 time24 = doubletoint(time_master(itime))

 if (iswitch .eq. 0) then
  nn = dimsizes(f_ta[:]->ta(itime,:,:,:))
  nz_atmos = nn(0)
  ny = nn(1)
  nx = nn(2)
  iswitch = 1
  print (nz_atmos+"     "+ny+"  "+nx)
 end if

 ;6-h variables
 ;For pressure
 ps = f_ua[:]->ps(itime,:,:)
 hyam = f_ua[0]->a
 hybm = f_ua[0]->b
 p0 = f_ua[0]->p0

 ;Explicit 3-D variables (6-h)
 u = f_ua[:]->ua(itime,:,:,:)
 v = f_va[:]->va(itime,:,:,:)
 t = f_ta[:]->ta(itime,::-1,:,:)        ;Must be top-to-bottom for interpolation
 q = f_hus[:]->hus(itime,:,:,:)

 ;Derived 3-D and 2-D variables (6-h)
 ;Compute the full pressure at mass points
 p = pres_hybrid_ccm(ps,p0,hyam,hybm)
 copy_VarCoords(t,p)

 ;Compute slp using ECMWF formulation (6-h)
 pmsl = pslec(t(nz_atmos-1,:,:),z_sfc*g,ps,p(nz_atmos-1,:,:))

 ;Geopotential height
 tnew = t(lat|:,lon|:,lev|::-1)
 pnew = p(lat|:,lon|:,lev|::-1)
 zh = hydro (pnew,tnew,z_sfc)   ;Must be bottom-to-top

 if(any(ismissing(zh))) then
    print("Your data contains some missing values. Beware.")
    print (num(ismissing(zh)) )
  end if

 copy_VarCoords(pnew,zh)
 zh_new = zh(lev|::-1,lat|:,lon|:)      ;Must be top-to-bottom

 ;Derive U10, V10 (diagnostic initialization?)
 ;using lowest 2 vertical levels
 U10 = dim_avg_n_Wrap(u(nz_atmos-2:nz_atmos-1,:,:),0)
 V10 = dim_avg_n_Wrap(v(nz_atmos-2:nz_atmos-1,:,:),0)

 ;Interpolate to p-levels
 P0mb = p0/100

 U = vinth2p (u,hyam,hybm,lev_p_mb,ps,1,P0mb,1,True)
 V = vinth2p (v,hyam,hybm,lev_p_mb,ps,1,P0mb,1,True)
 Q = vinth2p (q,hyam,hybm,lev_p_mb,ps,1,P0mb,1,True)
 T = vinth2p (t,hyam,hybm,lev_p_mb,ps,1,P0mb,1,True)
 PHI = vinth2p (zh_new,hyam,hybm,lev_p_mb,ps,1,P0mb,1,True)

 if(any(ismissing(U))) then
    print("U contains some missing values. Beware.")
    print (num(ismissing(U)) )
  end if

 if(any(ismissing(V))) then
    print("V contains some missing values. Beware.")
    print (num(ismissing(V)) )
  end if

 if(any(ismissing(Q))) then
    print("Q contains some missing values. Beware.")
    print (num(ismissing(Q)) )
  end if

 if(any(ismissing(T))) then
    print("T contains some missing values. Beware.")
    print (num(ismissing(T)) )
  end if

 if(any(ismissing(PHI))) then
    print("PHI contains some missing values. Beware.")
    print (num(ismissing(PHI)) )
  end if

 ;Explicit 2-D and 3-D variables (daily)

 ;On the CAM grid
 ;dtime changes for each variable!

 dtime = ind(time_tas .eq. time24)
 yearx   = tointeger(utc_tas(dtime,0))
 monthx  = tointeger(utc_tas(dtime,1))
 dayx   = tointeger(utc_tas(dtime,2))
 hourx   = tointeger(utc_tas(dtime,3))
 minutex = tointeger(utc_tas(dtime,4))
 secondx = tointeger(utc_tas(dtime,5))
 date_str = sprinti("%0.2i", yearx)+ "-"+ sprinti("%0.2i", monthx)+ \
             "-"+ sprinti("%0.2i", dayx)+ "_"+ sprinti("%0.2i", hourx)+ \
             ":"+ sprinti("%0.2i", minutex)+ ":"+ sprinti("%0.2i", secondx)
 print (date_str6+"      "+itime)
 print ("tas "+date_str+"      "+dtime)

 t2 = f_tas[:]->tas(dtime,:,:)

 dtime = ind(time_tsl .eq. time24)
 yearx   = tointeger(utc_tsl(dtime,0))
 monthx  = tointeger(utc_tsl(dtime,1))
 dayx   = tointeger(utc_tsl(dtime,2))
 hourx   = tointeger(utc_tsl(dtime,3))
 minutex = tointeger(utc_tsl(dtime,4))
 secondx = tointeger(utc_tsl(dtime,5))
 date_str = sprinti("%0.2i", yearx)+ "-"+ sprinti("%0.2i", monthx)+ \
             "-"+ sprinti("%0.2i", dayx)+ "_"+ sprinti("%0.2i", hourx)+ \
             ":"+ sprinti("%0.2i", minutex)+ ":"+ sprinti("%0.2i", secondx)
 print ("tsoil "+date_str+"      "+dtime)
 tsoil = f_tsl[:]->tsl(dtime,:,:,:)

 dtime = ind(time_tslsi .eq. time24)
 yearx   = tointeger(utc_tslsi(dtime,0))
 monthx  = tointeger(utc_tslsi(dtime,1))
 dayx   = tointeger(utc_tslsi(dtime,2))
 hourx   = tointeger(utc_tslsi(dtime,3))
 minutex = tointeger(utc_tslsi(dtime,4))
 secondx = tointeger(utc_tslsi(dtime,5))
 date_str = sprinti("%0.2i", yearx)+ "-"+ sprinti("%0.2i", monthx)+ \
             "-"+ sprinti("%0.2i", dayx)+ "_"+ sprinti("%0.2i", hourx)+ \
             ":"+ sprinti("%0.2i", minutex)+ ":"+ sprinti("%0.2i", secondx)
 print ("tslsi "+date_str+"      "+dtime)
 tskin_land = f_tslsi[:]->tslsi(dtime,:,:)
 dtime = ind(time_mrsol .eq. time24)
 yearx   = tointeger(utc_mrsol(dtime,0))
 monthx  = tointeger(utc_mrsol(dtime,1))
 dayx   = tointeger(utc_mrsol(dtime,2))
 hourx   = tointeger(utc_mrsol(dtime,3))
 minutex = tointeger(utc_mrsol(dtime,4))
 secondx = tointeger(utc_mrsol(dtime,5))
 date_str = sprinti("%0.2i", yearx)+ "-"+ sprinti("%0.2i", monthx)+ \
             "-"+ sprinti("%0.2i", dayx)+ "_"+ sprinti("%0.2i", hourx)+ \
             ":"+ sprinti("%0.2i", minutex)+ ":"+ sprinti("%0.2i", secondx)
 print ("mrsol "+date_str+"      "+dtime)
 qsoil = f_mrsol[:]->mrsol(dtime,:,:,:)
 soil_depth = doubletofloat(f_mrsol[0]->depth)

 dtime = ind(time_huss .eq. time24)
 yearx   = tointeger(utc_huss(dtime,0))
 monthx  = tointeger(utc_huss(dtime,1))
 dayx   = tointeger(utc_huss(dtime,2))
 hourx   = tointeger(utc_huss(dtime,3))
 minutex = tointeger(utc_huss(dtime,4))
 secondx = tointeger(utc_huss(dtime,5))
 date_str = sprinti("%0.2i", yearx)+ "-"+ sprinti("%0.2i", monthx)+ \
             "-"+ sprinti("%0.2i", dayx)+ "_"+ sprinti("%0.2i", hourx)+ \
             ":"+ sprinti("%0.2i", minutex)+ ":"+ sprinti("%0.2i", secondx)
 print ("huss "+date_str+"      "+dtime)
 q2 = f_huss[:]->huss(dtime,:,:)

 ;On the gx1v7 grid
 dtime = ind(time_tos .eq. time24)

 yearx   = tointeger(utc_tos(dtime,0))
 monthx  = tointeger(utc_tos(dtime,1))
 dayx   = tointeger(utc_tos(dtime,2))
 hourx   = tointeger(utc_tos(dtime,3))
 minutex = tointeger(utc_tos(dtime,4))
 secondx = tointeger(utc_tos(dtime,5))
 date_str = sprinti("%0.2i", yearx)+ "-"+ sprinti("%0.2i", monthx)+ \
             "-"+ sprinti("%0.2i", dayx)+ "_"+ sprinti("%0.2i", hourx)+ \
             ":"+ sprinti("%0.2i", minutex)+ ":"+ sprinti("%0.2i", secondx)
 print ("tos "+date_str+"       "+dtime)
 sst = f_tos[:]->tos(dtime,:,:) + T0
 lat_gx1v7 = f_tos[0]->lat
 lon_gx1v7 = f_tos[0]->lon

 ;Now to merge sst and tskin_land

 ;Regrid sst from gx1v7 grid to CAM grid
 Opt                 = True                     ; Regridding optioins
 Opt@SrcGridMask = where(ismissing(sst),0,1)    ; Mask
 Opt@SrcRegional     = True
 Opt@DstRegional     = True
 Opt@SrcGridType = "curvilinear"
 Opt@DstGridType = "rectilinear"
 Opt@SrcFileName     = "cesm2_MPAS_ESMF"+start_year+".nc"           ; output files
 Opt@DstFileName     = "cesm2_World_SCRIP"+start_year+".nc"
 Opt@WgtFileName     = "cesm2_MPAS_2_World"+start_year+".nc"
 Opt@ForceOverwrite  = True
 Opt@SrcGridLat      = lat_gx1v7   ;source grid
 Opt@SrcGridLon      = lon_gx1v7
 Opt@DstGridLat    = lat_cam
 Opt@DstGridLon    = lon_cam
 Opt@Debug         = False
 Opt@SkipDstGrid   = False
 Opt@SkipWgtGen    = False
 Opt@SrcRegional          = False
 Opt@DstRegional          = False
 sst_regrid = ESMF_regrid(sst,Opt)

 ;Now merge with tskin_land
 tskin = where(landsea.eq.0,sst_regrid,tskin_land)
 landmask = where(landsea.eq.0,0,1)
 landmask = tointeger(landmask)

 ;read sea ice
 dtime = ind(time_siconc .eq. time24)

 yearx   = tointeger(utc_tos(dtime,0))
 monthx  = tointeger(utc_tos(dtime,1))
 dayx   = tointeger(utc_tos(dtime,2))
 hourx   = tointeger(utc_tos(dtime,3))
 minutex = tointeger(utc_tos(dtime,4))
 secondx = tointeger(utc_tos(dtime,5))
 date_str = sprinti("%0.2i", yearx)+ "-"+ sprinti("%0.2i", monthx)+ \
             "-"+ sprinti("%0.2i", dayx)+ "_"+ sprinti("%0.2i", hourx)+ \
             ":"+ sprinti("%0.2i", minutex)+ ":"+ sprinti("%0.2i", secondx)
 print ("siconc "+date_str+"      "+dtime)
 sic = f_siconc[:]->siconc(dtime,:,:)
 sic@_FillValue=-99999
 sic=sic/100.0

 Opt@SrcGridMask = where(ismissing(sic),0,1)    ; Mask
 sic_regrid = ESMF_regrid(sic,Opt)
 delete(Opt)

 ;Prepare soild fields for write
 ;144 |   1  |   0  |      | SOILM000 | kg m-3  | Soil Moist   0 cm below ground          |  2 >
 ;144 | 111  |   5  |      | SOILM005 | kg m-3  | Soil Moist   5 cm below ground          |  2 >
 ;144 | 111  |  20  |      | SOILM020 | kg m-3  | Soil Moist  20 cm below ground          |  2 >
 ;144 | 111  |  40  |      | SOILM040 | kg m-3  | Soil Moist  40 cm below ground          |  2 >
 ;144 | 111  | 160  |      | SOILM160 | kg m-3  | Soil Moist 160 cm below ground          |  2 >
 ;144 | 111  | 300  |      | SOILM300 | kg m-3  | Soil Moist 300 cm below ground          |  2 >
 ; 85 |   1  |   0  |      | SOILT000 | K       | Soil Temp    0 cm below ground          |  2 >
 ; 85 | 111  |   5  |      | SOILT005 | K       | Soil Temp    5 cm below ground          |  2 >
 ; 85 | 111  |  20  |      | SOILT020 | K       | Soil Temp   20 cm below ground          |  2 >
 ; 85 | 111  |  40  |      | SOILT040 | K       | Soil Temp   40 cm below ground          |  2 >
 ; 85 | 111  | 160  |      | SOILT160 | K       | Soil Temp  160 cm below ground          |  2 >
 ; 85 | 111  | 300  |      | SOILT300 | K       | Soil Temp  300 cm below ground

 ;Depths from CESM2/CLM
 ; depth = 0.00999999977648258, 0.0399999991059303, 0.0900000035762787,
 ;   0.159999996423721, 0.259999990463257, 0.400000005960464,

 ;Soil temperature
 tsoil1 = tsoil(0,:,:)
 tsoil2 = tsoil(1,:,:)
 tsoil3 = tsoil(2,:,:)
 tsoil4 = tsoil(3,:,:)

 ;Soil Moisture [kg/m2]
 qsoil000010 = qsoil(0,:,:)
 qsoil010040 = qsoil(1,:,:)
 qsoil040090 = qsoil(2,:,:)
 qsoil090160 = qsoil(3,:,:)

 ;Convert to a fraction -- divide by deltaz of GCM
 ;Depth of water divided by depth of layer [unitless]
 qsoil1 = qsoil000010 / (soil_depth(1) - soil_depth(0)) / 1000. ;[m water m dz]
 qsoil2 = qsoil010040 / (soil_depth(2) - soil_depth(1)) / 1000.
 qsoil3 = qsoil040090 / (soil_depth(3) - soil_depth(2)) / 1000.
 qsoil4 = qsoil090160 / (soil_depth(4) - soil_depth(3)) / 1000.

 print (date_str6+"      "+itime)

printMinMax(qsoil1,1)
printMinMax(qsoil2,1)
printMinMax(qsoil3,1)
printMinMax(qsoil4,1)

 ;Write to binary file using .f90 subroutine
 ;Transfer to .f90 code
 DRIVEWRFWITH::tofortran(T,Q,U,V,PHI,ps,pmsl,U10,V10,tskin,landmask, \
             t2,q2,tsoil1,tsoil2,tsoil3,tsoil4, \
             qsoil1,qsoil2,qsoil3,qsoil4, \
             lev_p_pa,nx,ny,np, \
             year,month,day,hour,z_sfc,sst_regrid,sic_regrid)

end do  ;end time loop

end
~                                                                                                                                                                                                                                                                                                                                       
~                        
