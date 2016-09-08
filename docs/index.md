---
layout: default
title: Geospatial Files
---

What is this package?
---------------------

This package makes it simple to load geospatial data from files. Currently binary and grib1/grib2 files are supported. Data can be loaded across a range of dates, forecast hours (for forecast data), and ensemble members (for ensemble forecast data).

This package uses `wgrib` and `wgrib2` in order to read grib files, and must be installed on your system for this package to work. You can test your system to make sure you have wgrib and wgrib2 available with the following code:

    $ python -c "from cpc.geofiles import test_wgrib ; test_wgrib()"

How do I read in data?
----------------------

Data can either be read in for a single file, or over a range of dates, forecast hours, or ensemble members.

### Reading data from a single file

The `reading` module contains a function for reading grib1 & grib2 files. Binary files are simple to read in without this module. For example:

```python
>>> import numpy as np
>>> data = np.fromfile('/path/to/file.bin', dtype='float32')
```

Since reading in grib data is a little less straightforward, this module makes it easier. The function that reads in grib data is called `read_grib()`. You'll need to specify the following parameters in order to read in a file:

1. `file` - name of the grib file to read from
2. `grib_type` - type of grib file ('grib1', 'grib2')
3. `grib_var` - name of the variable in the grib record (ex. TMP, UGRD, etc.)
4. `grib_level` - name of the level (ex. '2 m above ground', '850 mb', etc.)
5. `geogrid` - [GeoGrid](https://mikecharles.github.io/cpc.geogrids/) the data fits on

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

### Reading data from multiple files

If you want to "load a dataset" (read in data from multiple files), you can use the `loading` module. The `loading` module loops over dates (for all types of datasets), forecast hours (for forecast datasets) and members (for ensemble forecast datasets), and reads in data across the range of all of those parameters.

Like for the `reading` module, the `loading` module depends on `wgrib` and `wgrib2` for reading in grib1/grib2 data.

Data is loaded into a `Dataset` object, from which you can extract the data itself, plus a few QC-related attributes such as dates with missing files, a list of the missing files, and the dates that were loaded. There are several types of `Datasets`. Here is the hierarchy of `Dataset` types:

- Dataset
  - Observation
  - Forecast
    - DeterministicForecast
    - EnsembleForecast
  - Climatology

#### Loading observation data

To load observation data, use the `loading.load_obs()` function. You'll need to specify the following parameters:

1. `valid_dates` - list of valid dates in YYYYMMDD or YYYYMMDDHH format (if HH is not supplied, it is assumed to be '00')
2. `file_template` - file template used to construct file names for each date - it can contain any of the following bracketed variables:
   - `{yyyy}`
   - `{mm}`
   - `{dd}`
   - `{hh}`
3. `data_type` - data type (binary, grib1 or grib2)
4. `geogrid` - [Geogrid](https://mikecharles.github.io/cpc.geogrids/) that the data should fit on

Here's an example of how to load a few days of observation data:

```python
>>> from cpc.geogrids import Geogrid
>>> from cpc.geofiles.loading import load_obs
>>> valid_dates = ['20150101', '20150102', '20150103']
>>> file_template = '/path/to/files/{yyyy}/{mm}/{dd}/tmean_01d_{yyyy}{mm}{dd}.bin'
>>> data_type = 'binary'
>>> geogrid = Geogrid('1deg-global')
>>> dataset = load_obs(valid_dates, file_template, data_type, geogrid)
>>> print(dataset.obs.shape, dataset.obs[:, 0])
(3, 65160) [-28.48999405 -28.04499435 -27.81749725]
```

#### Loading deterministic forecast data

To load deterministic forecast data, use the `loading.load_obs()` function. You'll need to specify the following parameters:

1. `valid_dates` - list of valid dates in YYYYMMDD or YYYYMMDDHH format (if HH is not supplied, it is assumed to be '00')
2. `file_template` - file template used to construct file names for each date - it can contain any of the following bracketed variables:
   - `{yyyy}`
   - `{mm}`
   - `{dd}`
   - `{hh}`
3. `data_type` - data type (binary, grib1 or grib2)
4. `geogrid` - [Geogrid](https://mikecharles.github.io/cpc.geogrids/) that the data should fit on

Here's an example of how to load a few days of observation data:

```python
>>> from cpc.geogrids import Geogrid
>>> from cpc.geofiles.loading import load_obs
>>> valid_dates = ['20150101', '20150102', '20150103']
>>> file_template = '/path/to/files/{yyyy}/{mm}/{dd}/tmean_01d_{yyyy}{mm}{dd}.bin'
>>> data_type = 'binary'
>>> geogrid = Geogrid('1deg-global')
>>> dataset = load_obs(valid_dates, file_template, data_type, geogrid)
>>> print(dataset.obs.shape, dataset.obs[:, 0])
(3, 65160) [-28.48999405 -28.04499435 -27.81749725]
```
