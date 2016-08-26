---
layout: default
title: cpc.geofiles.reading module
type: apidoc
---
        
# cpc.geofiles.reading Module
> Contains methods for reading gridded data.



## Functions

### <span class="function">read_grib(file, grib_type, variable, level, grid=None, yrev=False, grep_fhr=None, debug=False)</span> 

> Reads a record from a grib file
> 
> Uses wgrib for grib1 files, and wgrib2 for grib2 files. For grib1 files, the record in
> question is written to a temporary binary file, the data is read in, and the file is removed.
> wgrib2 has the ability to write the record to STDIN, so no temporary file is necessary to
> read in a record from a grib2 file.
> 
> ### Parameters
> 
> - file (string): name of the grib file to read from
> - grib_type (string): type of grib file ('grib1', 'grib2')
> - variable (string): name of the variable in the grib record (ex. TMP, UGRD, etc.)
> - level (string): name of the level (ex. '2 m above ground', '850 mb', etc.)
> - grid (GeoGrid): GeoGrid the data should be placed on
> - yrev (optional): option to flip the data in the y-direction (eg. ECMWF grib files)
> - grep_fhr (optional): fhr to grep grib file for - this is useful for gribs that may for some
>   reason have duplicate records for a given variable but with different fhrs. This way you
>   can get the record for the correct fhr.
> 
> ### Returns
> 
> - (array_like): a data array containing the appropriate grib record
> 
> ### Raises
> 
> - IOError: if wgrib has a problem reading the grib and/or writing the temp file
> - IOError: if no grib record is found
> 
> ### Examples
> 
>     #!/usr/bin/env python
>     >>> from data_utils.gridded.reading import read_grib
>     >>> from pkg_resources import resource_filename
>     >>> file = resource_filename('data_utils',
>     ... 'lib/example-tmean-fcst.grb2')
>     >>> grib_type = 'grib2'
>     >>> variable = 'TMP'
>     >>> level = '2 m above ground'
>     >>> data = read_grib(file, grib_type, variable, level)
>     >>> data.shape
>     (65160,)
>     >>> data
>     array([ 248.77000427,  248.77000427,  248.77000427, ...,  241.86000061,
>             241.86000061,  241.86000061], dtype=float32)


