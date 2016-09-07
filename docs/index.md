---
layout: default
title: Geospatial Files
---

What is this package?
---------------------

This package makes it simple to load geospatial data from files. Currently binary and grib1/grib2 files are supported. Data can be loaded across a range of dates, forecast hours (for forecast data), and ensemble members (for ensemble forecast data).

How do I read in data?
----------------------

Data can either be read in for a single file, or over a range of dates, forecast hours, or ensemble members.

### Reading data from a single file

The `reading` module contains a function for reading grib1 & grib2 files. Binary files are simple to read in without this module. For example:

```python
import numpy as np
data = np.fromfile('/path/to/file.bin', dtype='float32')
```

Since reading in grib data is a little less straightforward, this module makes it easier. The function that reads in grib data is called `read_grib()`. You'll need to specify the following parameters in order to read in a file:

1. `file` - name of the grib file to read from
2. `grib_type` - type of grib file ('grib1', 'grib2')
3. `grib_var` - name of the variable in the grib record (ex. TMP, UGRD, etc.)
4. `grib_level` - name of the level (ex. '2 m above ground', '850 mb', etc.)
5. `geogrid` - [GeoGrid](https://mikecharles.github.io/cpc.geogrids/) the data fits on

For example, to read in 2m temperature from a grib2 file:

```python
from cpc.geogrids import GeoGrid
from cpc.geofiles.reading import read_grib

file = '/Users/mike/Work/data/TEST/2016/05/15/00/gefs_20160515_00z_f342_m10.grb2'
grib_type = 'grib2'
grib_var = 'TMP'
grib_level = '2 m above ground'
geogrid = GeoGrid('1deg-global')

data = read_grib(file, grib_type, grib_var, grib_level, geogrid)

print(data.shape, data[0])
```
