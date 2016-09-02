"""
Contains methods for loading larger amounts of data than a single day

For example, let's say you want to load all of the forecasts valid today's
month and day from all years between 1985 and 2010. This module is intended
to make that much simpler.
"""

# Built-ins


# Third-party
import numpy as np

# This package
from .datasets import EnsembleForecast, DeterministicForecast, Observation, Climatology
from .reading import read_grib
from .exceptions import LoadingError, ReadingError


def all_int_to_str(input):
    if all(isinstance(x, int) for x in input):
        # Get length of longest int
        max_length = max([len(str(x)) for x in input])
        # Convert all ints to strings, zero-padding to the max length
        return ['{{:0{}.0f}}'.format(max_length).format(x) for x in input]
    elif all(isinstance(x, str) for x in input):
        return input
    else:
        raise ValueError('input must be a list of ints')


def load_ens_fcsts(issued_dates, members, fhrs, file_template, data_type, geogrid,
                   fhr_stat='mean', yrev=False, grib_var=None, grib_level=None,
                   remove_dup_grib_fhrs=False, debug=False):
    """
    Loads ensemble forecast data

    Data is loaded for a given list of dates, forecast hours and members. The file template can
    contain any of the following bracketed variables:

    - {yyyy}
    - {mm}
    - {dd}
    - {cc}
    - {fhr}
    - {member}

    Within a loop over the dates, fhrs and members, the bracketed variables above are replaced
    with the appropriate value.

    Parameters
    ----------

    - issued_dates (list of strings): list of issued dates in YYYYMMDD or YYYYMMDDCC format - if
      YYYYMMDD, the cycle is assumed to be 00
    - fhrs (list of numbers or strings): list of fhrs to load
    - members (list of numbers or strings): list of members to load
    - file_template (string): file template used to construct file names for each date,
      fhr and member
    - data_type (string): data type (bin, grib1 or grib2)
    - geogrid (GeoGrid): GeoGrid associated with the data
    - fhr_stat (string): statistic to calculate over the forecast hour dimension (mean [default]
      or sum)
    - yrev (boolean): whether fcst data is reversed in the y-direction, and should be flipped
      when loaded (default: False)
    - grib_var (string): grib variable name (for grib files only)
    - grib_level (string): grib level name (for grib files only)
    - remove_dup_grib_fhrs (boolean): whether to remove potential duplicate fhrs from the grib
      files (default: False) - sets the `grep_fhr` parameter to the current fhr when calling
      `read_grib()`, which greps for the fhr in the given grib file - this is useful for gribs
      that may for some reason have duplicate records for a given variable but with different
      fhrs. This way you can get the record for the correct fhr.
    - debug (boolean): if True the file data is loaded from will be printed out (default: False)

    Returns
    -------

    If `collapse=True`, a tuple of 2 NumPy arrays will be returned (ensemble
    mean and ensemble spread). For example:

        >>> dataset = load_ens_fcsts(..., collapse=True)  # doctest: +SKIP

    If `collapse=False`, a single NumPy array will be returned. For example:

        >>> dataset = load_ens_fcsts(..., collapse=False))  # doctest: +SKIP

    Examples
    --------

    Load ensemble mean and spread from forecasts initialized on a given
    month/day from 1981-2010

        >>> from string_utils.dates import generate_date_list
        >>> from data_utils.gridded.grid import Grid
        >>> from data_utils.gridded.loading import load_obs
        >>> dates = generate_date_list('19810525', '20100525', interval='years')
        >>> file_tmplt = '/path/to/fcsts/%Y/%m/%d/gefs_%Y%m%d_00z_f{fhr}_m{member}.grb'
        >>> data_type = 'grib2'
        >>> grid = Grid('1deg-global')
        >>> variable = 'TMP'
        >>> level = '2 m above ground'
        >>> num_members = 11
        >>> dataset = \  # doctest: +SKIP
        load_ens_fcsts(dates, file_template=file_tmplt, data_type=data_type,  # doctest: +SKIP
        ...            grid=grid, variable=variable, level=level,  # doctest: +SKIP
        ...            fhr_range=(150, 264), num_members=num_members,  # doctest: +SKIP
        ...            collapse=True)  # doctest: +SKIP
    """
    # ----------------------------------------------------------------------------------------------
    # Create a new EnsembleForecast Dataset
    #
    dataset = EnsembleForecast()

    # ----------------------------------------------------------------------------------------------
    # Initialize arrays for the EnsembleForecast Dataset the full ensemble data array
    #
    dataset.ens = np.nan * np.empty(
        (len(issued_dates), len(members), geogrid.num_y * geogrid.num_x)
    )

    # ----------------------------------------------------------------------------------------------
    # Convert fhrs and members to strings (if necessary)
    #
    fhrs = all_int_to_str(fhrs)
    members = all_int_to_str(members)

    # ----------------------------------------------------------------------------------------------
    # Set dates loaded
    #
    dataset.dates_loaded |= set(issued_dates)

    # ----------------------------------------------------------------------------------------------
    # Loop over date, members, and fhrs
    #
    for d, date in enumerate(issued_dates):
        # Split date into components
        yyyy, mm, dd = date[0:4], date[4:6], date[6:8]
        if len(date) == 10:
            cc = date[8:10]
        else:
            cc = '00'
        for m, member in enumerate(members):
            # Initialize an array for a single day, single member, all fhrs
            data_f = np.nan * np.empty((len(fhrs), geogrid.num_y * geogrid.num_x))
            for f, fhr in enumerate(fhrs):
                # Replace variables in file template
                kwargs = {'yyyy': yyyy, 'mm': mm, 'dd': dd, 'cc': cc, 'fhr': fhr, 'member': member}
                file = file_template.format(**kwargs)
                # Read in data from file
                if data_type in ['grib1', 'grib2']:
                    try:
                        data_f[f] = read_grib(file, data_type, grib_var, grib_level, geogrid,
                                              debug=debug)
                    except ReadingError:
                        # Set this day to missing
                        data_f[f] = np.full((geogrid.num_y * geogrid.num_x), np.nan)
                        # Add this date to the list of dates with missing files
                        dataset.dates_with_missing_files.add(date)
                        # Add this file to the list of missing files
                        dataset.missing_files.add(file)
            # Take stat over fhr (don't use nanmean/nanstd, if an fhr is missing then we
            # don't trust this mean/std
            if fhr_stat == 'mean':
                dataset.ens[d, m] = np.mean(data_f, axis=0)
            elif fhr_stat == 'std':
                dataset.ens[d, m] = np.std(data_f, axis=0)
            else:
                raise LoadingError('fhr_stat must be either mean or std', file)

    return dataset


def load_dtrm_fcsts(issued_dates, fhrs, file_template, data_type, geogrid, fhr_stat='mean',
                    yrev=False, grib_var=None, grib_level=None, remove_dup_grib_fhrs=False,
                    debug=False):
    """
    Loads deterministic forecast data

    Data is loaded for a given list of dates and forecast hours. The file template can contain
    any of the following bracketed variables:

    - {yyyy}
    - {mm}
    - {dd}
    - {cc}
    - {fhr}

    Within a loop over the dates and fhrs, the bracketed variables above are replaced with the
    appropriate value.

    Parameters
    ----------

    - issued_dates (list of strings): list of issued dates in YYYYMMDD or YYYYMMDDCC format - if
      YYYYMMDD, the cycle is assumed to be 00
    - fhrs (list of numbers or strings): list of fhrs to load
    - file_template (string): file template used to construct file names for each date,
      fhr and member
    - data_type (string): data type (bin, grib1 or grib2)
    - geogrid (GeoGrid): GeoGrid associated with the data
    - fhr_stat (string): statistic to calculate over the forecast hour dimension (mean [default]
      or sum)
    - yrev (boolean): whether fcst data is reversed in the y-direction, and should be flipped
      when loaded (default: False)
    - grib_var (string): grib variable name (for grib files only)
    - grib_level (string): grib level name (for grib files only)
    - remove_dup_grib_fhrs (boolean): whether to remove potential duplicate fhrs from the grib
      files (default: False) - sets the `grep_fhr` parameter to the current fhr when calling
      `read_grib()`, which greps for the fhr in the given grib file - this is useful for gribs
      that may for some reason have duplicate records for a given variable but with different
      fhrs. This way you can get the record for the correct fhr.
    - debug (boolean): if True the file data is loaded from will be printed out (default: False)

    Returns
    -------

    If `collapse=True`, a tuple of 2 NumPy arrays will be returned (ensemble
    mean and ensemble spread). For example:

        >>> dataset = load_ens_fcsts(..., collapse=True)  # doctest: +SKIP

    If `collapse=False`, a single NumPy array will be returned. For example:

        >>> dataset = load_ens_fcsts(..., collapse=False))  # doctest: +SKIP

    Examples
    --------

    Load ensemble mean and spread from forecasts initialized on a given
    month/day from 1981-2010

        >>> from string_utils.dates import generate_date_list
        >>> from data_utils.gridded.grid import Grid
        >>> from data_utils.gridded.loading import load_obs
        >>> dates = generate_date_list('19810525', '20100525', interval='years')
        >>> file_tmplt = '/path/to/fcsts/%Y/%m/%d/gefs_%Y%m%d_00z_f{fhr}_m{member}.grb'
        >>> data_type = 'grib2'
        >>> grid = Grid('1deg-global')
        >>> variable = 'TMP'
        >>> level = '2 m above ground'
        >>> num_members = 11
        >>> dataset = \  # doctest: +SKIP
        load_ens_fcsts(dates, file_template=file_tmplt, data_type=data_type,  # doctest: +SKIP
        ...            grid=grid, variable=variable, level=level,  # doctest: +SKIP
        ...            fhr_range=(150, 264), num_members=num_members,  # doctest: +SKIP
        ...            collapse=True)  # doctest: +SKIP
    """
    # ----------------------------------------------------------------------------------------------
    # Create a new DeterministicForecast Dataset
    #
    dataset = DeterministicForecast()

    # ----------------------------------------------------------------------------------------------
    # Initialize array for the DeterministicForecast Dataset
    #
    dataset.fcst = np.nan * np.empty((len(issued_dates), geogrid.num_y * geogrid.num_x))

    # ----------------------------------------------------------------------------------------------
    # Convert fhrs to strings (if necessary)
    #
    fhrs = all_int_to_str(fhrs)

    # ----------------------------------------------------------------------------------------------
    # Set dates loaded
    #
    dataset.dates_loaded |= set(issued_dates)

    # ----------------------------------------------------------------------------------------------
    # Loop over date and fhrs
    #
    for d, date in enumerate(issued_dates):
        # Split date into components
        yyyy, mm, dd = date[0:4], date[4:6], date[6:8]
        if len(date) == 10:
            cc = date[8:10]
        else:
            cc = '00'
        # Initialize an array for a single day, all fhrs
        data_f = np.nan * np.empty((len(fhrs), geogrid.num_y * geogrid.num_x))
        for f, fhr in enumerate(fhrs):
            # Replace variables in file template
            kwargs = {'yyyy': yyyy, 'mm': mm, 'dd': dd, 'cc': cc, 'fhr': fhr}
            file = file_template.format(**kwargs)
            # Read in data from file
            if data_type in ['grib1', 'grib2']:
                try:
                    data_f[f] = read_grib(file, data_type, grib_var, grib_level, geogrid,
                                          debug=debug)
                except ReadingError:
                    # Set this day to missing
                    data_f[f] = np.full((geogrid.num_y * geogrid.num_x), np.nan)
                    # Add this date to the list of dates with missing files
                    dataset.dates_with_missing_files.add(date)
                    # Add this file to the list of missing files
                    dataset.missing_files.add(file)
        # Take stat over fhr (don't use nanmean/nanstd, if an fhr is missing then we
        # don't trust this mean/std
        if fhr_stat == 'mean':
            dataset.fcst[d] = np.mean(data_f, axis=0)
        elif fhr_stat == 'std':
            dataset.fcst[d] = np.std(data_f, axis=0)
        else:
            raise LoadingError('fhr_stat must be either mean or std', file)

    return dataset


def load_obs(valid_dates, file_template, data_type, geogrid, record_num=None, yrev=False,
             grib_var=None, grib_level=None, debug=False):
    """
    Loads observation data

    Data is loaded for a given list of dates. The file template can contain any of the following
    bracketed variables:

    - {yyyy}
    - {mm}
    - {dd}
    - {hh}

    Within a loop over the dates, the bracketed variables above are replaced with the appropriate
    value.

    Parameters
    ----------

    - valid_dates (list of strings): list of valid dates in YYYYMMDD or YYYYMMDDHH format
    - file_template (string): file template used to construct file names for each date,
      fhr and member
    - data_type (string): data type (bin, grib1 or grib2)
    - geogrid (GeoGrid): GeoGrid associated with the data
    - record_num (int): binary record containing the desired variable - if None then the file is
      assumed to be a single record (default)
    - yrev (boolean): whether fcst data is reversed in the y-direction, and should be flipped
      when loaded (default: False)
    - grib_var (string): grib variable name (for grib files only)
    - grib_level (string): grib level name (for grib files only)
    - debug (boolean): if True the file data is loaded from will be printed out (default: False)

    Returns
    -------

    If `collapse=True`, a tuple of 2 NumPy arrays will be returned (ensemble
    mean and ensemble spread). For example:

        >>> dataset = load_ens_fcsts(..., collapse=True)  # doctest: +SKIP

    If `collapse=False`, a single NumPy array will be returned. For example:

        >>> dataset = load_ens_fcsts(..., collapse=False))  # doctest: +SKIP

    Examples
    --------

    Load ensemble mean and spread from forecasts initialized on a given
    month/day from 1981-2010

        >>> from string_utils.dates import generate_date_list
        >>> from data_utils.gridded.grid import Grid
        >>> from data_utils.gridded.loading import load_obs
        >>> dates = generate_date_list('19810525', '20100525', interval='years')
        >>> file_tmplt = '/path/to/fcsts/%Y/%m/%d/gefs_%Y%m%d_00z_f{fhr}_m{member}.grb'
        >>> data_type = 'grib2'
        >>> grid = Grid('1deg-global')
        >>> variable = 'TMP'
        >>> level = '2 m above ground'
        >>> num_members = 11
        >>> dataset = \  # doctest: +SKIP
        load_ens_fcsts(dates, file_template=file_tmplt, data_type=data_type,  # doctest: +SKIP
        ...            grid=grid, variable=variable, level=level,  # doctest: +SKIP
        ...            fhr_range=(150, 264), num_members=num_members,  # doctest: +SKIP
        ...            collapse=True)  # doctest: +SKIP
    """
    # ----------------------------------------------------------------------------------------------
    # Create a new Observation Dataset
    #
    dataset = Observation()

    # ----------------------------------------------------------------------------------------------
    # Initialize array for the Observation Dataset
    #
    dataset.obs = np.nan * np.empty((len(valid_dates), geogrid.num_y * geogrid.num_x))

    # ----------------------------------------------------------------------------------------------
    # Set dates loaded
    #
    dataset.dates_loaded |= set(valid_dates)

    # ----------------------------------------------------------------------------------------------
    # Loop over date
    #
    for d, date in enumerate(valid_dates):
        # Split date into components
        yyyy, mm, dd = date[0:4], date[4:6], date[6:8]
        if len(date) == 10:
            cc = date[8:10]
        else:
            cc = '00'
        # Replace variables in file template
        kwargs = {'yyyy': yyyy, 'mm': mm, 'dd': dd, 'cc': cc}
        file = file_template.format(**kwargs)
        # Read in data from file
        if data_type in ['grib1', 'grib2']:
            try:
                # Read grib with read_grib()
                dataset.obs[d] = read_grib(file, data_type, grib_var, grib_level, geogrid,
                                           debug=debug)
            except ReadingError:
                # Set this day to missing
                dataset.obs[d] = np.full((geogrid.num_y * geogrid.num_x), np.nan)
                # Add this date to the list of dates with missing files
                dataset.dates_with_missing_files.add(date)
                # Add this file to the list of missing files
                dataset.missing_files.add(file)
        elif data_type in ['bin', 'binary']:
            try:
                # Load data from file
                dataset.obs[d] = np.fromfile(file, dtype='float32')
                # Determine number of records in the binary file
                num_records = int(dataset.obs[d].size / (geogrid.num_y * geogrid.num_x))
                # Reshape data and extract the appropriate record - if record_num is specified,
                # extract that record number, otherwise just take the entire array
                if record_num is not None:
                    dataset.obs[d] = dataset.obs[d].reshape(
                        num_records, geogrid.num_y * geogrid.num_x
                    )[record_num]
                else:
                    dataset.obs[d] = dataset.obs[d].reshape(
                        num_records, geogrid.num_y * geogrid.num_x
                    )
            except:
                # Set this day to missing
                dataset.obs[d] = np.full((geogrid.num_y * geogrid.num_x), np.nan)
                # Add this date to the list of dates with missing files
                dataset.dates_with_missing_files.add(date)
                # Add this file to the list of missing files
                dataset.missing_files.add(file)

    return dataset


def load_climos(valid_days, file_template, geogrid, num_ptiles=None, debug=False):
    """
    Loads climatology data

    Data is loaded for a given range of days of the year. Currently the data must be in binary
    format with the dimensions (ptiles x grid points) when num_ptiles is an integer, and (grid
    points [1-d]) when num_ptiles is None

    - {mm}
    - {dd}

    Within a loop over the days, the bracketed variables above are replaced with the appropriate
    value.

    Parameters
    ----------

    - valid_days (list of strings): list of days of the year to load - must be formatted as MMDD
      (eg. [0501, 0502, 0503, 0504, 0505])
    - file_template (string): file template used to construct file names for each date,
      fhr and member
    - geogrid (GeoGrid): GeoGrid associated with the data
    - record_num (int): binary record containing the desired variable - if None then the file is
      assumed to be a single record (default)
    - num_ptiles (int or None): number of percentiles expected in the data file - if None then
    the file is assumed to be a mean or standard deviation instead of percentiles (default: None)
    - debug (boolean): if True the file data is loaded from will be printed out (default: False)

    Returns
    -------

    - Climatology object

        >>> dataset = load_ens_fcsts(..., collapse=True)  # doctest: +SKIP

    If `collapse=False`, a single NumPy array will be returned. For example:

        >>> dataset = load_ens_fcsts(..., collapse=False))  # doctest: +SKIP

    Examples
    --------

    Load ensemble mean and spread from forecasts initialized on a given
    month/day from 1981-2010

        >>> from string_utils.dates import generate_date_list
        >>> from data_utils.gridded.grid import Grid
        >>> from data_utils.gridded.loading import load_obs
        >>> dates = generate_date_list('19810525', '20100525', interval='years')
        >>> file_tmplt = '/path/to/fcsts/%Y/%m/%d/gefs_%Y%m%d_00z_f{fhr}_m{member}.grb'
        >>> data_type = 'grib2'
        >>> grid = Grid('1deg-global')
        >>> variable = 'TMP'
        >>> level = '2 m above ground'
        >>> num_members = 11
        >>> dataset = \  # doctest: +SKIP
        load_ens_fcsts(dates, file_template=file_tmplt, data_type=data_type,  # doctest: +SKIP
        ...            grid=grid, variable=variable, level=level,  # doctest: +SKIP
        ...            fhr_range=(150, 264), num_members=num_members,  # doctest: +SKIP
        ...            collapse=True)  # doctest: +SKIP
    """
    # ----------------------------------------------------------------------------------------------
    # Create a new Climatology Dataset
    #
    dataset = Climatology()

    # ----------------------------------------------------------------------------------------------
    # Initialize array for the Climatology Dataset
    #
    # If num_ptiles is an integer, add a ptile dimension to the climo array
    if num_ptiles is not None:
        try:
            dataset.climo = np.nan * np.empty((len(valid_days), num_ptiles,
                                               geogrid.num_y * geogrid.num_x))
        except:
            raise LoadingError('num_ptiles must be an integer or None')
    else:
        dataset.climo = np.nan * np.empty((len(valid_days), geogrid.num_y * geogrid.num_x))

    # ----------------------------------------------------------------------------------------------
    # Set dates loaded
    #
    dataset.dates_loaded |= set(valid_days)

    # ----------------------------------------------------------------------------------------------
    # Loop over date
    #
    for d, date in enumerate(valid_days):
        # Split date into components
        mm, dd = date[0:2], date[2:4]
        # Replace variables in file template
        kwargs = {'mm': mm, 'dd': dd}
        file = file_template.format(**kwargs)
        # Read in data from file
        try:
            # Load data from file
            if num_ptiles is not None:
                dataset.climo[d] = np.fromfile(file, 'float32').reshape(
                    num_ptiles, geogrid.num_y * geogrid.num_x)
            else:
                dataset.climo[d] = np.fromfile(file, 'float32').reshape(
                    geogrid.num_y * geogrid.num_x)
        except:
            # Set this day to missing
            if num_ptiles:
                dataset.climo[d] = np.full((num_ptiles, geogrid.num_y * geogrid.num_x), np.nan)
            else:
                dataset.climo[d] = np.full((geogrid.num_y * geogrid.num_x), np.nan)
            # Add this date to the list of dates with missing files
            dataset.dates_with_missing_files.add(date)
            # Add this file to the list of missing files
            dataset.missing_files.add(file)

    return dataset

