"""
Contains methods for reading gridded data.
"""

# Built-ins
import subprocess
import uuid
import os

# Third-party
import numpy as np

# This package
from .exceptions import ReadingError


def read_grib(file, grib_type, grib_var, grib_level, grid=None, yrev=False, grep_fhr=None, debug=False):
    """
    Reads a record from a grib file

    Uses wgrib for grib1 files, and wgrib2 for grib2 files. For grib1 files, the record in
    question is written to a temporary binary file, the data is read in, and the file is removed.
    wgrib2 has the ability to write the record to STDIN, so no temporary file is necessary to
    read in a record from a grib2 file.

    ### Parameters

    - file (string): name of the grib file to read from
    - grib_type (string): type of grib file ('grib1', 'grib2')
    - variable (string): name of the variable in the grib record (ex. TMP, UGRD, etc.)
    - level (string): name of the level (ex. '2 m above ground', '850 mb', etc.)
    - grid (GeoGrid): GeoGrid the data should be placed on
    - yrev (optional): option to flip the data in the y-direction (eg. ECMWF grib files)
    - grep_fhr (optional): fhr to grep grib file for - this is useful for gribs that may for some
      reason have duplicate records for a given variable but with different fhrs. This way you
      can get the record for the correct fhr.

    ### Returns

    - (array_like): a data array containing the appropriate grib record

    ### Raises

    - ReadingError: if wgrib has a problem reading the grib and/or writing the temp file
    - ReadingError: if no grib record is found

    ### Examples

        #!/usr/bin/env python
        >>> from data_utils.gridded.reading import read_grib
        >>> from pkg_resources import resource_filename
        >>> file = resource_filename('data_utils',
        ... 'lib/example-tmean-fcst.grb2')
        >>> grib_type = 'grib2'
        >>> variable = 'TMP'
        >>> level = '2 m above ground'
        >>> data = read_grib(file, grib_type, variable, level)
        >>> data.shape
        (65160,)
        >>> data
        array([ 248.77000427,  248.77000427,  248.77000427, ...,  241.86000061,
                241.86000061,  241.86000061], dtype=float32)
    """
    # Make sure grib file exists first
    if not os.path.isfile(file):
        raise ReadingError('Grib file not found', file)
    # Generate a temporary file name
    temp_file = str(uuid.uuid4()) + '.bin'
    # Set the grep_fhr string
    if grep_fhr:
        grep_fhr_str = grep_fhr
    else:
        grep_fhr_str = '.*'
    # Set the name of the wgrib program to call
    if grib_type == 'grib1':
        wgrib_call = 'wgrib "{}" | grep ":{}:" | grep ":{}:" | grep -P "{}" | wgrib ' \
                     '-i "{}" -nh -bin -o "{}"'.format(file, grib_var, grib_level,
                                                       grep_fhr_str, file, temp_file)
    elif grib_type == 'grib2':
        # Note that the binary data is written to stdout
        wgrib_call = 'wgrib2 "{}" -match "{}" -match "{}" -match "{}" -end ' \
                     '-order we:sn -no_header -inv /dev/null -bin -'.format(
            file, grib_var, grib_level, grep_fhr_str)
    else:
        raise ReadingError(__name__ + ' requires grib_type to be grib1 or grib2')
    if debug:
        print('wgrib command: {}'.format(wgrib_call))
    # Generate a wgrib call
    try:
        if grib_type == 'grib1':
            output = subprocess.call(wgrib_call, shell=True, stderr=subprocess.DEVNULL,
                                     stdout=subprocess.DEVNULL)
        else:
            proc = subprocess.Popen(wgrib_call, shell=True, stderr=subprocess.DEVNULL,
                                    stdout=subprocess.PIPE)
    except Exception as e:
        if grib_type == 'grib1':
            os.remove(temp_file)
        raise ReadingError('Couldn\'t read {} file: {}'.format(grib_type, str(e)))
    # Read in the binary data
    if grib_type == 'grib1':
        data = np.fromfile(temp_file, dtype=np.float32)
    else:
        data = np.frombuffer(bytearray(proc.stdout.read()), dtype='float32')
    if data.size == 0:
        raise ReadingError('No grib record found')
    # Delete the temporary file
    if grib_type == 'grib1':
        os.remove(temp_file)
    # Flip the data in the y-dimension (if necessary)
    if yrev:
        # Reshape into 2 dimensions
        try:
            data = np.reshape(data, (grid.num_y, grid.num_x))
        except AttributeError:
            raise ValueError('The yrev parameter requires that the grid parameter be defined')
        # Flip
        data = np.flipud(data)
        # Reshape back into 1 dimension
        data = np.reshape(data, data.size)
    # Return data
    return data
