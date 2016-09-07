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
> - geogrid (GeoGrid): GeoGrid associated with the data
> - record_num (int): binary record containing the desired variable - if None then the file is
>   assumed to be a single record (default)
> - num_ptiles (int or None): number of percentiles expected in the data file - if None then
> the file is assumed to be a mean or standard deviation instead of percentiles (default: None)
> - debug (boolean): if True the file data is loaded from will be printed out (default: False)
> 
> Returns
> -------
> 
> - Climatology object
> 
>     >>> dataset = load_ens_fcsts(..., collapse=True)  # doctest: +SKIP
> 
> If `collapse=False`, a single NumPy array will be returned. For example:
> 
>     >>> dataset = load_ens_fcsts(..., collapse=False))  # doctest: +SKIP
> 
> Examples
> --------
> 
> Load ensemble mean and spread from forecasts initialized on a given
> month/day from 1981-2010
> 
>     >>> from string_utils.dates import generate_date_list
>     >>> from data_utils.gridded.grid import Grid
>     >>> from data_utils.gridded.loading import load_obs
>     >>> dates = generate_date_list('19810525', '20100525', interval='years')
>     >>> file_tmplt = '/path/to/fcsts/%Y/%m/%d/gefs_%Y%m%d_00z_f{fhr}_m{member}.grb'
>     >>> data_type = 'grib2'
>     >>> grid = Grid('1deg-global')
>     >>> variable = 'TMP'
>     >>> level = '2 m above ground'
>     >>> num_members = 11
>     >>> dataset = \  # doctest: +SKIP
>     load_ens_fcsts(dates, file_template=file_tmplt, data_type=data_type,  # doctest: +SKIP
>     ...            grid=grid, variable=variable, level=level,  # doctest: +SKIP
>     ...            fhr_range=(150, 264), num_members=num_members,  # doctest: +SKIP
>     ...            collapse=True)  # doctest: +SKIP



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
> - geogrid (GeoGrid): GeoGrid associated with the data
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
> If `collapse=True`, a tuple of 2 NumPy arrays will be returned (ensemble
> mean and ensemble spread). For example:
> 
>     >>> dataset = load_ens_fcsts(..., collapse=True)  # doctest: +SKIP
> 
> If `collapse=False`, a single NumPy array will be returned. For example:
> 
>     >>> dataset = load_ens_fcsts(..., collapse=False))  # doctest: +SKIP
> 
> Examples
> --------
> 
> Load ensemble mean and spread from forecasts initialized on a given
> month/day from 1981-2010
> 
>     >>> from string_utils.dates import generate_date_list
>     >>> from data_utils.gridded.grid import Grid
>     >>> from data_utils.gridded.loading import load_obs
>     >>> dates = generate_date_list('19810525', '20100525', interval='years')
>     >>> file_tmplt = '/path/to/fcsts/%Y/%m/%d/gefs_%Y%m%d_00z_f{fhr}_m{member}.grb'
>     >>> data_type = 'grib2'
>     >>> grid = Grid('1deg-global')
>     >>> variable = 'TMP'
>     >>> level = '2 m above ground'
>     >>> num_members = 11
>     >>> dataset = \  # doctest: +SKIP
>     load_ens_fcsts(dates, file_template=file_tmplt, data_type=data_type,  # doctest: +SKIP
>     ...            grid=grid, variable=variable, level=level,  # doctest: +SKIP
>     ...            fhr_range=(150, 264), num_members=num_members,  # doctest: +SKIP
>     ...            collapse=True)  # doctest: +SKIP



### <span class="function">load_ens_fcsts(issued_dates, members, fhrs, file_template, data_type, geogrid, fhr_stat='mean', yrev=False, grib_var=None, grib_level=None, remove_dup_grib_fhrs=False, debug=False)</span> 

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
> - geogrid (GeoGrid): GeoGrid associated with the data
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
> If `collapse=True`, a tuple of 2 NumPy arrays will be returned (ensemble
> mean and ensemble spread). For example:
> 
>     >>> dataset = load_ens_fcsts(..., collapse=True)  # doctest: +SKIP
> 
> If `collapse=False`, a single NumPy array will be returned. For example:
> 
>     >>> dataset = load_ens_fcsts(..., collapse=False))  # doctest: +SKIP
> 
> Examples
> --------
> 
> Load ensemble mean and spread from forecasts initialized on a given
> month/day from 1981-2010
> 
>     >>> from string_utils.dates import generate_date_list
>     >>> from data_utils.gridded.grid import Grid
>     >>> from data_utils.gridded.loading import load_obs
>     >>> dates = generate_date_list('19810525', '20100525', interval='years')
>     >>> file_tmplt = '/path/to/fcsts/%Y/%m/%d/gefs_%Y%m%d_00z_f{fhr}_m{member}.grb'
>     >>> data_type = 'grib2'
>     >>> grid = Grid('1deg-global')
>     >>> variable = 'TMP'
>     >>> level = '2 m above ground'
>     >>> num_members = 11
>     >>> dataset = \  # doctest: +SKIP
>     load_ens_fcsts(dates, file_template=file_tmplt, data_type=data_type,  # doctest: +SKIP
>     ...            grid=grid, variable=variable, level=level,  # doctest: +SKIP
>     ...            fhr_range=(150, 264), num_members=num_members,  # doctest: +SKIP
>     ...            collapse=True)  # doctest: +SKIP



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
> - geogrid (GeoGrid): GeoGrid associated with the data
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
> If `collapse=True`, a tuple of 2 NumPy arrays will be returned (ensemble
> mean and ensemble spread). For example:
> 
>     >>> dataset = load_ens_fcsts(..., collapse=True)  # doctest: +SKIP
> 
> If `collapse=False`, a single NumPy array will be returned. For example:
> 
>     >>> dataset = load_ens_fcsts(..., collapse=False))  # doctest: +SKIP
> 
> Examples
> --------
> 
> Load ensemble mean and spread from forecasts initialized on a given
> month/day from 1981-2010
> 
>     >>> from string_utils.dates import generate_date_list
>     >>> from data_utils.gridded.grid import Grid
>     >>> from data_utils.gridded.loading import load_obs
>     >>> dates = generate_date_list('19810525', '20100525', interval='years')
>     >>> file_tmplt = '/path/to/fcsts/%Y/%m/%d/gefs_%Y%m%d_00z_f{fhr}_m{member}.grb'
>     >>> data_type = 'grib2'
>     >>> grid = Grid('1deg-global')
>     >>> variable = 'TMP'
>     >>> level = '2 m above ground'
>     >>> num_members = 11
>     >>> dataset = \  # doctest: +SKIP
>     load_ens_fcsts(dates, file_template=file_tmplt, data_type=data_type,  # doctest: +SKIP
>     ...            grid=grid, variable=variable, level=level,  # doctest: +SKIP
>     ...            fhr_range=(150, 264), num_members=num_members,  # doctest: +SKIP
>     ...            collapse=True)  # doctest: +SKIP


