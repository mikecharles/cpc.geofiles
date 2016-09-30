---
layout: default
title: Geospatial Files
---

What is this package?
=====================

This package makes it simple to load geospatial data from files. Currently binary and grib1/grib2 files are supported. Data can be loaded across a range of dates, forecast hours (for forecast data), and ensemble members (for ensemble forecast data).

This package uses `wgrib` and `wgrib2` in order to read grib files, and must be installed on your system for this package to work. You can test your system to make sure you have wgrib and wgrib2 available with the following code:

    $ python -c "from cpc.geofiles import test_wgrib ; test_wgrib()"

How do I read in data?
======================

Data can either be read in for a single file, or over a range of dates, forecast hours, or ensemble members.

Reading data from a single file
-------------------------------

The `reading` module contains a function for reading grib1 & grib2 files. Binary files are simple to read in without this module. For example:

```python
>>> import numpy as np
>>> data = np.fromfile('/path/to/file.bin', dtype='float32')
```

Since reading in grib data is a little less straightforward, this module makes it easier. The function that reads in grib data is called `read_grib()`. You'll need to specify the following parameters in order to read in a file:

- `file` - name of the grib file to read from
- `grib_type` - type of grib file ('grib1', 'grib2')
- `grib_var` - name of the variable in the grib record (ex. TMP, UGRD, etc.)
- `grib_level` - name of the level (ex. '2 m above ground', '850 mb', etc.)
- `geogrid` - [GeoGrid](https://mikecharles.github.io/cpc.geogrids/) the data fits on

`grib_var` and `grib_level` are used as strings to match grib records. You can see all the grib records in your file using `wgrib` or `wgrib2`. For example, for a concise listing of records:

    $ wgrib2 /path/to/files/gefs_20160515_00z_f342_m10.grb2

or for a verbose listing:

    $ wgrib2 -V /path/to/files/gefs_20160515_00z_f342_m10.grb2

For grib1 files, use `wgrib` the same way. You can filter out just the variables and levels like this:

    $ wgrib2 -var -lev /path/to/files/gefs_20160515_00z_f342_m10.grb2

Once you have the variable and level for the record you want to read in, you can pass that to `read_grib()`. For example, to read in 2m temperature from a grib2 file:

```python
>>> from cpc.geogrids import GeoGrid
>>> from cpc.geofiles.reading import read_grib
>>> file = '/path/to/files/gefs_20160515_00z_f342_m10.grb2'
>>> grib_type = 'grib2'
>>> grib_var = 'TMP'
>>> grib_level = '2 m above ground'
>>> geogrid = GeoGrid('1deg-global')
>>> data = read_grib(file, grib_type, grib_var, grib_level, geogrid)
>>> print(data.shape, data[0])
(65160,) 237.4
```

Reading data from multiple files
--------------------------------

If you want to "load a dataset" (read in data from multiple files), you can use the `loading` module. The `loading` module loops over dates (for all types of datasets), forecast hours (for forecast datasets) and members (for ensemble forecast datasets), and reads in data across the range of all of those parameters.

Like for the `reading` module, the `loading` module depends on `wgrib` and `wgrib2` for reading in grib1/grib2 data.

### Dataset objects

Data is loaded into a `Dataset` object, from which you can extract the data itself, plus a few QC-related attributes such as dates with missing files, a list of the missing files, and the dates that were loaded. There are several types of `Datasets`. Here is the hierarchy of `Dataset` types, and what information they contain:

- Dataset
  - Observation
  - Forecast
    - DeterministicForecast
    - EnsembleForecast
  - Climatology

#### General Datasets

All `Datasets` contain the following attributes:

- `data_type` - Type of `Dataset` (None for general Datasets)
- `dates_with_missing_files` - Dates which had at least one file that was missing or couldn't be opened
- `missing_files` - Files that were missing or couldn't be opened
- `dates_loaded` - Dates for which data was loaded (includes dates which have all missing data)

#### Observations

`Observations` contain all attributes that `Datasets` have, plus:

- `data_type` set to `observation`
- `obs` - NumPy array of observations loaded, formatted as `(date, grid point)`, NaN where data couldn't be loaded

#### Forecasts

`Forecasts` contain all attributes that `Datasets` have, plus:

- `data_type` set to `forecast`

`EnsembleForecasts` contain all attributes that `Forecasts` have, plus:

- `ens` - NumPy array of ensemble forecasts, formatted as `(date, member, grid point)`, NaN where data couldn't be loaded - note that data is averaged/accumulated over forecast hour
- `ens_mean` - NumPy array of ensemble mean forecasts, formatted as `(date, grid point)`, NaN where data couldn't be loaded - note that data is averaged/accumulated over forecast hour
- `ens_spread` - NumPy array of ensemble forecast spread, formatted as `(date, grid point)`, NaN where data couldn't be loaded - note that data is averaged/accumulated over forecast hour

`DeterministicForecasts` contain all attributes that `Forecasts` have, plus:

- `fcst` - NumPy array of deterministic forecasts, formatted as `(date, grid point)`, NaN where data couldn't be loaded - note that data is averaged/accumulated over forecast hour

#### Climatologies

`Climatologies` contain all attributes that `Datasets` have, plus:

- `data_type` set to `climatology`
- `climo` - NumPy array of climatologies, formatted as `(day, ptile, grid point)` when `num_ptiles is not None` and `(day, grid point)` when `num_ptiles is None`, NaN where data couldn't be loaded

### Loading observation data

To load observation data, use the `loading.load_obs()` function. You'll need to specify the following parameters:

- `valid_dates` - list of valid dates in YYYYMMDD or YYYYMMDDHH format (if HH is not supplied, it is assumed to be '00')
- `file_template` - file template used to construct file names for each date - it can contain any of the following bracketed variables:
   - `{yyyy}`
   - `{mm}`
   - `{dd}`
   - `{hh}`
- `data_type` - data type (binary, grib1 or grib2)
- `geogrid` - [Geogrid](https://mikecharles.github.io/cpc.geogrids/) that the data should fit on

Some optional parameters are:

- `yrev` - whether fcst data is reversed in the y-direction, and should be flipped when loaded (default: False)
- `grib_var` - grib variable name (for grib files only)
- `grib_level` - grib level name (for grib files only)
- `debug` - if True the file data is loaded from will be printed out (default: False)

Note that observation binary files are assumed to have the format `record-num` x `grid-point` for multi-record files, or just a sequence of grid points for single-record files.

Here's an example of how to load a few days of observation data:

```python
>>> from cpc.geogrids import Geogrid
>>> from cpc.geofiles.loading import load_obs
>>> valid_dates = ['20150101', '20150102', '20150103']
>>> file_template = '/path/to/files/{yyyy}/{mm}/{dd}/'\
                    'tmean_01d_{yyyy}{mm}{dd}.bin'
>>> data_type = 'binary'
>>> geogrid = Geogrid('1deg-global')
>>> dataset = load_obs(valid_dates, file_template, data_type, geogrid)
>>> print(dataset.obs.shape, dataset.obs[:, 0])
(3, 65160) [-28.48999405 -28.04499435 -27.81749725]
```

### Loading deterministic forecast data

To load deterministic forecast data, use the `loading.load_dtrm_fcsts()` function. You'll need to specify the following parameters:

- `issued_dates` - list of issued dates in YYYYMMDD or YYYYMMDDCC format (if CC [cycle] is not supplied, it is assumed to be '00')
- `fhrs` - list of forecast hours to load - either a list of strings, or a list of ints; if a list of ints, numbers will be zero-padded to the number of characters of the highest fhr
- `file_template` - file template used to construct file names for each date - it can contain any of the following bracketed variables:
   - `{yyyy}`
   - `{mm}`
   - `{dd}`
   - `{cc}`
   - `{fhr}`
- `data_type` - data type (binary, grib1 or grib2)
- `geogrid` - [Geogrid](https://mikecharles.github.io/cpc.geogrids/) that the data should fit on

Some optional parameters are:

- `fhr_stat` - statistic to calculate over the forecast hour dimension (mean [default] or sum)
- `yrev` - whether fcst data is reversed in the y-direction, and should be flipped when loaded (default: False)
- `grib_var` - grib variable name (for grib files only)
- `grib_level` - grib level name (for grib files only)
- `remove_dup_grib_fhrs` - whether to remove potential duplicate fhrs from the grib files (default: False) - sets the `grep_fhr` parameter to the current fhr when calling `read_grib()`, which greps for the fhr in the given grib file - this is useful for gribs that may for some reason have duplicate records for a given variable but with different fhrs. This way you can get the record for the correct fhr.
- `debug` - if True the file data is loaded from will be printed out (default: False)

Here's an example of how to load a few days of deterministic forecast data:

```python
>>> from cpc.geogrids import Geogrid
>>> from cpc.geofiles.loading import load_dtrm_fcsts
>>> valid_dates = ['20160101', '20160102', '20160103']
>>> fhrs = range(0, 120, 6)
>>> file_template = '/path/to/files/{yyyy}/{mm}/{dd}/{cc}/' \
                    'gfs_{yyyy}{mm}{dd}_{cc}z_f{fhr}.grb2'
>>> data_type = 'grib2'
>>> geogrid = Geogrid('0.5-deg-global-center-aligned')
>>> grib_var = 'TMP'
>>> grib_level = '2 m above ground'
>>> dataset = load_dtrm_fcsts(valid_dates, fhrs, file_template,
                              data_type, geogrid, grib_var=grib_var,
                              grib_level=grib_level)
>>> print(dataset.fcst.shape, dataset.fcst[:, 0])
(3, 259920) [ 246.64699936  246.50599976  245.97450104]
```

### Loading ensemble forecast data

To load ensemble forecast data, use the `loading.load_ens_fcsts()` function. You'll need to specify the following parameters:

- `issued_dates` - list of issued dates in YYYYMMDD or YYYYMMDDCC format (if CC [cycle] is not supplied, it is assumed to be '00')
- `fhrs` - list of forecast hours to load - either a list of strings, or a list of ints; if a list of ints, numbers will be zero-padded to the number of characters of the highest fhr
- `members` - list of members to load - either a list of strings, or a list of ints; if a list of ints, numbers will be zero-padded to the number of characters of the highest member number
- `file_template` - file template used to construct file names for each date - it can contain any of the following bracketed variables:
   - `{yyyy}`
   - `{mm}`
   - `{dd}`
   - `{cc}`
   - `{fhr}`
- `data_type` - data type (binary, grib1 or grib2)
- `geogrid` - [Geogrid](https://mikecharles.github.io/cpc.geogrids/) that the data should fit on

Some optional parameters are:

- `fhr_stat` - statistic to calculate over the forecast hour dimension (mean [default] or sum)
- `yrev` - whether fcst data is reversed in the y-direction, and should be flipped when loaded (default: False)
- `grib_var` - grib variable name (for grib files only)
- `grib_level` - grib level name (for grib files only)
- `remove_dup_grib_fhrs` - whether to remove potential duplicate fhrs from the grib files (default: False) - sets the `grep_fhr` parameter to the current fhr when calling `read_grib()`, which greps for the fhr in the given grib file - this is useful for gribs that may for some reason have duplicate records for a given variable but with different fhrs. This way you can get the record for the correct fhr.
- `debug` - if True the file data is loaded from will be printed out (default: False)

Here's an example of how to load a few days of ensemble forecast data:

```python
>>> from cpc.geogrids import Geogrid
>>> from cpc.geofiles.loading import load_ens_fcsts
>>> valid_dates = ['20160101', '20160102', '20160103']
>>> fhrs = range(0, 120, 6)
>>> members = range(0, 21)
>>> file_template = '/path/to/files/{yyyy}/{mm}/{dd}/{cc}/' \
                    'gefs_{yyyy}{mm}{dd}_{cc}z_f{fhr}_m{member}.grb2'
>>> data_type = 'grib2'
>>> geogrid = Geogrid('1deg-global')
>>> grib_var = 'TMP'
>>> grib_level = '2 m above ground'
>>> dataset = load_ens_fcsts(valid_dates, fhrs, members, file_template,
                             data_type, geogrid, grib_var=grib_var,
                             grib_level=grib_level)
>>> print(dataset.ens.shape)
(3, 21, 65160)
>>> print(dataset.ens[:, :, 0])
[[ 246.18849945  246.40299683  247.11050034  245.95850067  246.17949905
   246.91550064  247.41700134  246.53700104  247.96300125  246.05699921
   246.08150101  247.11800003  247.46500015  247.30050049  247.44899979
   245.84649963  247.8234993   246.21900101  246.45600128  245.72950058
   246.05299988]
 [ 246.11650085  245.45250092  247.54049759  246.35499878  245.56750107
   246.74899902  247.23949966  246.52750015  247.40500031  245.96500092
   245.85749969  246.07099915  247.3465004   246.61099854  245.78749771
   247.18349838  246.47999954  245.44049988  245.78899994  245.67700043
   245.87299957]
 [ 245.88300095  245.5995018   247.63799896  247.21050034  245.88849945
   246.78749847  246.15800018  246.15749969  246.41600113  246.00299988
   246.80950012  246.51200104  247.11650009  246.2659996   245.96800156
   247.20250168  246.22499924  245.72900162  245.85200043  244.81850128
   245.73949966]]
>>> print(dataset.ens_mean.shape)
(3, 65160)
>>> print(dataset.ens_mean[:, 0])
[ 246.67957157  246.33497583  246.28476225]
```

### Loading climatology data

To load climatology data, use the `loading.load_obs()` function. You'll need to specify the following parameters:

- `valid_days` - list of valid dates in MMDD format
- `file_template` - file template used to construct file names for each date - it can contain any of the following bracketed variables:
   - `{mm}`
   - `{dd}`
- `geogrid` - [Geogrid](https://mikecharles.github.io/cpc.geogrids/) that the data should fit on

Some optional parameters are:

- `geogrid` - Geogrid associated with the data
- `num_ptiles` - number of percentiles expected in the data file - if None then the file is assumed to be a mean or standard deviation instead of percentiles (default: None)
- `debug` - if True the file data is loaded from will be printed out (default: False)

Here's an example of how to load a few days of climatology data:

```python
>>> from cpc.geogrids import Geogrid
>>> from cpc.geofiles.loading import load_climos
>>> valid_days = ['0101', '0102', '0103']
>>> file_template = '/path/to/files/tmean_clim_poe_05d_{mm}{dd}.bin'
>>> geogrid = Geogrid('1deg-global')
>>> num_ptiles = 19
>>> dataset = load_climos(valid_days, file_template, geogrid,
                          num_ptiles=num_ptiles, debug=True)
>>> print(dataset.climo.shape)
>>> print(dataset.climo[:, :, 0])
```

How do I convert data?
======================

Binary files can be converted to text files using functions in `cpc.geofiles.conversion`.

To convert a binary forecast file to text, use the function `cpc.geofiles.conversion.fcst_bin_to_txt()`. You'll need to specify the following parameters:

- `bin_file` - binary forecast file (assumed to contain probabilities of exceeding a given set of percentiles)
- `grid` - [Geogrid](https://mikecharles.github.io/cpc.geogrids/) that the data should fit on
- `fcst_ptiles` - list of percentiles found in the forecast binary file
- `desired_output_thresholds` - list of percentile thresholds to extract and write to the text file
- `txt_file` - name of the text file to write data to
- `terciles` - if True, will output tercile probabilities (with headers below, normal, and above) - if False (default) will probabilities of exceeding percentiles (with headers ptileXX, ptileYY, etc.)
- `output_grid` - [Geogrid](https://mikecharles.github.io/cpc.geogrids/) that the data should be interpolated to before writing the text file

To convert a binary observation file to text, use the function `cpc.geofiles.conversion.obs_bin_to_txt()`. You'll need to specify the following parameters:

- `bin_file` - binary forecast file (assumed to contain probabilities of exceeding a given set of percentiles)
- `grid` - [Geogrid](https://mikecharles.github.io/cpc.geogrids/) that the data should fit on
- `desired_output_thresholds` - list of percentile thresholds to extract and write to the text file
- `txt_file` - name of the text file to write data to
- `output_threshold_type` - type of thresholds to write out ('ptile' or 'raw')
- `climo_file` - binary file containing the climatology (needed to convert raw observations to a category), with the dimensions (Y x X)
- `climo_ptiles` - list of percentiles found in the climatology file
- `output_grid` - [Geogrid](https://mikecharles.github.io/cpc.geogrids/) that the data should be interpolated to before writing the text file

See the [API documentation](api/conversion.html) for more information.
