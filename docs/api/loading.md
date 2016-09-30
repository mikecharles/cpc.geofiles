---
layout: default
title: cpc.geofiles.loading module
type: apidoc
---
        
# cpc.geofiles.loading Module
> Contains methods for loading larger amounts of data than a single day
> 
> For example, let's say you want to load all of the forecasts valid today's
> month and day from all years between 1985 and 2010. This module is intended
> to make that much simpler.



## Functions

### <span class="function">all_int_to_str(input)</span> 



### <span class="function">load_climos(valid_days, file_template, geogrid, num_ptiles=None, debug=False)</span> 

> Loads climatology data
> 
> Data is loaded for a given range of days of the year. Currently the data must be in binary
> format with the dimensions (ptiles x grid points) when num_ptiles is an integer, and (grid
> points [1-d]) when num_ptiles is None
> 
> - {mm}
> - {dd}
> 
> Within a loop over the days, the bracketed variables above are replaced with the appropriate
> value.
> 
> Parameters
> ----------
> 
> - valid_days (list of strings): list of days of the year to load - must be formatted as MMDD
>   (eg. [0501, 0502, 0503, 0504, 0505])
> - file_template (string): file template used to construct file names for each date,
>   fhr and member
> - geogrid (Geogrid): Geogrid associated with the data
> - num_ptiles (int or None): number of percentiles expected in the data file - if None then
> the file is assumed to be a mean or standard deviation instead of percentiles (default: None)
> - debug (boolean): if True the file data is loaded from will be printed out (default: False)
> 
> Returns
> -------
> 
> - Climatology object containing the observation data and some QC data
> 
> Examples
> --------
> 
> Load a few days of climatology data
> 
>     >>> from cpc.geogrids import Geogrid
>     >>> from cpc.geofiles.loading import load_climos
>     >>> valid_days = ['0101', '0102', '0103']
>     >>> file_template = '/path/to/files/tmean_clim_poe_05d_{mm}{dd}.bin'
>     >>> geogrid = Geogrid('1deg-global')
>     >>> num_ptiles = 19
>     >>> dataset = load_climos(valid_days, file_template, geogrid,
>     ...                       num_ptiles=num_ptiles, debug=True)
>     >>> print(dataset.climo.shape)
>     (3, 19, 65160)
>     >>> print(dataset.climo[:, :, 0])
>     [[ nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan
>        nan  nan  nan  nan  nan]
>      [ nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan
>        nan  nan  nan  nan  nan]
>      [ nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan  nan
>        nan  nan  nan  nan  nan]]



### <span class="function">load_dtrm_fcsts(issued_dates, fhrs, file_template, data_type, geogrid, fhr_stat='mean', yrev=False, grib_var=None, grib_level=None, remove_dup_grib_fhrs=False, debug=False)</span> 

> Loads deterministic forecast data
> 
> Data is loaded for a given list of dates and forecast hours. The file template can contain
> any of the following bracketed variables:
> 
> - {yyyy}
> - {mm}
> - {dd}
> - {cc}
> - {fhr}
> 
> Within a loop over the dates and fhrs, the bracketed variables above are replaced with the
> appropriate value.
> 
> Parameters
> ----------
> 
> - issued_dates (list of strings): list of issued dates in YYYYMMDD or YYYYMMDDCC format - if
>   YYYYMMDD, the cycle is assumed to be 00
> - fhrs (list of numbers or strings): list of fhrs to load
> - file_template (string): file template used to construct file names for each date,
>   fhr and member
> - data_type (string): data type (bin, grib1 or grib2)
> - geogrid (Geogrid): Geogrid associated with the data
> - fhr_stat (string): statistic to calculate over the forecast hour dimension (mean [default]
>   or sum)
> - yrev (boolean): whether fcst data is reversed in the y-direction, and should be flipped
>   when loaded (default: False)
> - grib_var (string): grib variable name (for grib files only)
> - grib_level (string): grib level name (for grib files only)
> - remove_dup_grib_fhrs (boolean): whether to remove potential duplicate fhrs from the grib
>   files (default: False) - sets the `grep_fhr` parameter to the current fhr when calling
>   `read_grib()`, which greps for the fhr in the given grib file - this is useful for gribs
>   that may for some reason have duplicate records for a given variable but with different
>   fhrs. This way you can get the record for the correct fhr.
> - debug (boolean): if True the file data is loaded from will be printed out (default: False)
> 
> Returns
> -------
> 
> - DeterministicForecast object containing the forecast data and some QC data
> 
> Examples
> --------
> 
> Load a few days of deterministic forecast data
> 
>     >>> from cpc.geogrids import Geogrid
>     >>> from cpc.geofiles.loading import load_dtrm_fcsts
>     >>> valid_dates = ['20160101', '20160102', '20160103']
>     >>> fhrs = range(0, 120, 6)
>     >>> file_template = '/path/to/files/{yyyy}/{mm}/{dd}/{cc}/'                             'gfs_{yyyy}{mm}{dd}_{cc}z_f{fhr}.grb2'
>     >>> data_type = 'grib2'
>     >>> geogrid = Geogrid('0.5-deg-global-center-aligned')
>     >>> grib_var = 'TMP'
>     >>> grib_level = '2 m above ground'
>     >>> dataset = load_dtrm_fcsts(valid_dates, fhrs, file_template,
>     ...                           data_type, geogrid, grib_var=grib_var,
>     ...                           grib_level=grib_level)
>     >>> print(dataset.fcst.shape, dataset.fcst[:, 0])  # doctest: +SKIP
>     (3, 259920) [ 246.64699936  246.50599976  245.97450104]



### <span class="function">load_ens_fcsts(issued_dates, fhrs, members, file_template, data_type, geogrid, fhr_stat='mean', yrev=False, grib_var=None, grib_level=None, remove_dup_grib_fhrs=False, debug=False)</span> 

> Loads ensemble forecast data
> 
> Data is loaded for a given list of dates, forecast hours and members. The file template can
> contain any of the following bracketed variables:
> 
> - {yyyy}
> - {mm}
> - {dd}
> - {cc}
> - {fhr}
> - {member}
> 
> Within a loop over the dates, fhrs and members, the bracketed variables above are replaced
> with the appropriate value.
> 
> Parameters
> ----------
> 
> - issued_dates (list of strings): list of issued dates in YYYYMMDD or YYYYMMDDCC format - if
>   YYYYMMDD, the cycle is assumed to be 00
> - fhrs (list of numbers or strings): list of fhrs to load
> - members (list of numbers or strings): list of members to load
> - file_template (string): file template used to construct file names for each date,
>   fhr and member
> - data_type (string): data type (bin, grib1 or grib2)
> - geogrid (Geogrid): Geogrid associated with the data
> - fhr_stat (string): statistic to calculate over the forecast hour dimension (mean [default]
>   or sum)
> - yrev (boolean): whether fcst data is reversed in the y-direction, and should be flipped
>   when loaded (default: False)
> - grib_var (string): grib variable name (for grib files only)
> - grib_level (string): grib level name (for grib files only)
> - remove_dup_grib_fhrs (boolean): whether to remove potential duplicate fhrs from the grib
>   files (default: False) - sets the `grep_fhr` parameter to the current fhr when calling
>   `read_grib()`, which greps for the fhr in the given grib file - this is useful for gribs
>   that may for some reason have duplicate records for a given variable but with different
>   fhrs. This way you can get the record for the correct fhr.
> - debug (boolean): if True the file data is loaded from will be printed out (default: False)
> 
> Returns
> -------
> 
> - EnsembleForecast object containing the forecast data and some QC data
> 
> Examples
> --------
> 
> Load a few days of ensemble forecast data
> 
>     >>> from cpc.geogrids import Geogrid
>     >>> from cpc.geofiles.loading import load_ens_fcsts
>     >>> valid_dates = ['20160101', '20160102', '20160103']
>     >>> fhrs = range(0, 120, 6)
>     >>> members = range(0, 21)
>     >>> file_template = '/path/to/files/{yyyy}/{mm}/{dd}/{cc}/'                             'gefs_{yyyy}{mm}{dd}_{cc}z_f{fhr}_m{member}.grb2'
>     >>> data_type = 'grib2'
>     >>> geogrid = Geogrid('1deg-global')
>     >>> grib_var = 'TMP'
>     >>> grib_level = '2 m above ground'
>     >>> dataset = load_ens_fcsts(valid_dates, fhrs, members, file_template,
>     ...                          data_type, geogrid, grib_var=grib_var,
>     ...                          grib_level=grib_level)
>     >>> print(dataset.ens.shape)
>     (3, 21, 65160)
>     >>> print(dataset.ens[:, :, 0])  # doctest: +SKIP
>     [[ 246.18849945  246.40299683  247.11050034  245.95850067  246.17949905
>        246.91550064  247.41700134  246.53700104  247.96300125  246.05699921
>        246.08150101  247.11800003  247.46500015  247.30050049  247.44899979
>        245.84649963  247.8234993   246.21900101  246.45600128  245.72950058
>        246.05299988]
>      [ 246.11650085  245.45250092  247.54049759  246.35499878  245.56750107
>        246.74899902  247.23949966  246.52750015  247.40500031  245.96500092
>        245.85749969  246.07099915  247.3465004   246.61099854  245.78749771
>        247.18349838  246.47999954  245.44049988  245.78899994  245.67700043
>        245.87299957]
>      [ 245.88300095  245.5995018   247.63799896  247.21050034  245.88849945
>        246.78749847  246.15800018  246.15749969  246.41600113  246.00299988
>        246.80950012  246.51200104  247.11650009  246.2659996   245.96800156
>        247.20250168  246.22499924  245.72900162  245.85200043  244.81850128
>        245.73949966]]
>     >>> print(dataset.ens_mean.shape)
>     (3, 65160)
>     >>> print(dataset.ens_mean[:, 0])  # doctest: +SKIP
>     [ 246.67957157  246.33497583  246.28476225]



### <span class="function">load_obs(valid_dates, file_template, data_type, geogrid, record_num=None, yrev=False, grib_var=None, grib_level=None, debug=False)</span> 

> Loads observation data
> 
> Data is loaded for a given list of dates. The file template can contain any of the following
> bracketed variables:
> 
> - {yyyy}
> - {mm}
> - {dd}
> - {hh}
> 
> Within a loop over the dates, the bracketed variables above are replaced with the appropriate
> value.
> 
> Parameters
> ----------
> 
> - valid_dates (list of strings): list of valid dates in YYYYMMDD or YYYYMMDDHH format
> - file_template (string): file template used to construct file names for each date,
>   fhr and member
> - data_type (string): data type (bin, grib1 or grib2)
> - geogrid (Geogrid): Geogrid associated with the data
> - record_num (int): binary record containing the desired variable - if None then the file is
>   assumed to be a single record (default)
> - yrev (boolean): whether fcst data is reversed in the y-direction, and should be flipped
>   when loaded (default: False)
> - grib_var (string): grib variable name (for grib files only)
> - grib_level (string): grib level name (for grib files only)
> - debug (boolean): if True the file data is loaded from will be printed out (default: False)
> 
> Returns
> -------
> 
> - Observation object containing the observation data and some QC data
> 
> Examples
> --------
> 
> Load a few days of observation data
> 
>     >>> from cpc.geogrids import Geogrid
>     >>> from cpc.geofiles.loading import load_obs
>     >>> valid_dates = ['20150101', '20150102', '20150103']
>     >>> file_template = '/path/to/files/{yyyy}/{mm}/{dd}/tmean_01d_{yyyy}{mm}{dd}.bin'
>     >>> data_type = 'binary'
>     >>> geogrid = Geogrid('1deg-global')
>     >>> dataset = load_obs(valid_dates, file_template, data_type, geogrid)
>     >>> print(dataset.obs.shape, dataset.obs[:, 0])  # doctest: +SKIP
>     (3, 65160) [-28.48999405 -28.04499435 -27.81749725]


