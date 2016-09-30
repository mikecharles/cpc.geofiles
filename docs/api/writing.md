---
layout: default
title: cpc.geofiles.writing module
type: apidoc
---
        
# cpc.geofiles.writing Module


## Functions

### <span class="function">stn_terciles_to_txt(below, near, above, stn_ids, output_file, missing_val=None)</span> 

> Writes station tercile data to a text file
> 
> ### Parameters
> 
> - below - *NumPy array* - array of below normal values
> - near - *NumPy array* - array of near normal values
> - above - *NumPy array* - array of above normal values
> - output_file - *string* - text file to write values to
> - missing_val - *float or None* - value to consider missing - if None then don't consider
>   anything missing (write all data), otherwise just write the missing_val in all columns


