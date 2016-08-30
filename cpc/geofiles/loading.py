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
from .datasets import EnsembleForecast
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


def load_day(**kwargs):
    date = kwargs['date']
    members = kwargs['members']
    fhrs = kwargs['fhrs']
    file_template = kwargs['file_template']
    data_type = kwargs['data_type']
    geogrid = kwargs['geogrid']
    fhr_stat = kwargs['fhr_stat']
    yrev = kwargs['yrev']
    grib_var = kwargs['grib_var']
    grib_level = kwargs['grib_level']
    remove_dup_grib_fhrs = kwargs['remove_dup_grib_fhrs']
    debug = kwargs['debug']

    # Initialize data array
    data = np.nan * np.empty((len(members), geogrid.num_y * geogrid.num_x))

    # Split date into components
    yyyy, mm, dd = date[0:4], date[4:6], date[6:8]
    if len(date) == 10:
        cc = date[8:10]
    else:
        cc = '00'
    for m, member in enumerate(members):
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
                    raise LoadingError('File {} couldn\'t be loaded...', file)
            # Take stat over fhr
            if fhr_stat == 'mean':
                data[m] = np.nanmean(data_f, axis=0)
            elif fhr_stat == 'std':
                data[m] = np.nanstd(data_f, axis=0)
            else:
                raise LoadingError('fhr_stat must be either mean or std', file)
    return data


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
    # Initialize arrays for the EnsembleForecast Dataset
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
    # Loop over date, members, and fhrs
    #
    for d, date in enumerate(issued_dates):
        try:
            dataset.ens[d] = load_ens_fcst_day(**locals())
            dataset.dates_loaded.append(date)
        except LoadingError as e:
            dataset.missing_dates.append(date)
            dataset.missing_files.append(e.file)

    return dataset


def load_dtrm_fcsts():
    pass


def load_obs():
    pass


def load_clim():
    pass

