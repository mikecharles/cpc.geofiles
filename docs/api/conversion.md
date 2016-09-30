---
layout: default
title: cpc.geofiles.conversion module
type: apidoc
---
        
# cpc.geofiles.conversion Module
> Contains methods for converting between different file formats



## Functions

### <span class="function">fcst_bin_to_txt(bin_file, grid, fcst_ptiles, desired_output_thresholds, txt_file, output_threshold_type='ptile', terciles=False, output_grid=None)</span> 

> Converts a forecast binary file to a text file
> 
> The forecast binary file must contain probabilities of exceeding certain
> percentiles (AKA a POE file), where the percentiles are ascending in the
> file. The dimensions of the file should be (P x L), where:
> 
>   - P is the percentile
>   - L is the location
> 
> If `output_threshold_type` is set to 'ptile' ('raw'), then the
> probability  of exceeding the given ptiles (raw values) will be written
> to the output file under the headers ptileXX, ptileYY (rawvalXX,
> rawvalYY), etc.
> 
> If `terciles=True`, then headers will be different (see the Parameters
> section
> below)
> 
> Parameters
> ----------
> 
> - bin_file (string)
>     - Binary file containing the forecast, with the dimensions (ptile x Y x
>     X)
> - grid (Grid)
>     - Grid that the binary file maps to
> - fcst_ptiles (list)
>     - 1-dimensional list of ptiles found in the forecast file
> - desired_output_thresholds (list)
>     - 1-dimensional list of ptiles or raw values to include in the output
>     file
> - txt_file (string)
>     - Text file to write data to (will be overwritten)
> - output_threshold_type (string, optional)
>     - Type of thresholds to write out ('ptile' or 'raw')
> - terciles (bool, optional)
>     - If True, will output tercile probabilities (with headers below, normal
>       , and above)
>     - If False (default), will output probabilities of exceeding percentiles
>       (with headers ptileXX, ptileYY, etc.)
>     - Can only be set when 2 percentiles are supplied
> - output_grid (Grid, optional))
>     - `data_utils.gridded.grid` to interpolate to before converting to a
>     txt file
> 
> Raises
> ------
> 
> - ValueError
>     - If arguments are incorrect



### <span class="function">obs_bin_to_txt(bin_file, grid, desired_output_thresholds, txt_file, output_threshold_type='ptile', climo_file=None, climo_ptiles=None, output_grid=None)</span> 

> Converts an observation binary file to a text file
> 
> The observation binary file must contain raw values of the given variable.
> The file should be a single dimension (locations).
> 
> A climatology file is necessary if output_threshold_type='ptile', in which
> case the raw values in the observation file needs to first be converted to
> ptiles. The climatology file must have probabilities of exceeding a given
> set of percentiles, and be of dimensions (P x L) where:
> 
>   - P is the percentile
>   - L is the location
> 
> climo_ptiles must also be provided specifying the percentiles in the file.
> 
> Parameters
> ----------
> 
> - bin_file (string)
>     - Binary file containing the observation, with the dimensions (Y x X)
> - grid (Grid)
>     - `data_utils.gridded.grid.Grid` that the binary file maps to
> - desired_output_thresholds (array_like)
>     - 1-dimensional list of thresholds (either ptiles or raw values) to
>     include in the output file
> - txt_file (string)
>     - Text file to write data to (will be overwritten)
> - output_threshold_type (string, optional)
>     - Type of thresholds to write out ('ptile' or 'raw')
> - climo_file (string, optional)
>     - Binary file containing the climatology (needed to convert raw observations to a
>       category), with the dimensions (Y x X)
> - climo_ptiles (array_like, optional)
>     - List of percentiles found in the climatology file
> - output_grid (Grid, optional)
>     - `data_utils.gridded.grid.Grid` to interpolate to before
>     converting to a txt file
> 
> Raises
> ------
> 
> - ValueError
>     - If arguments are incorrect


