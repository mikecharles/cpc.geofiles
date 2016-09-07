---
layout: default
title: cpc.geofiles.datasets module
type: apidoc
---
        
# cpc.geofiles.datasets Module
> Defines a Dataset object. Datasets contain one or more data arrays, QC info, etc.



## cpc.geofiles.datasets.Climatology Objects



### <span class="function">\__init__(self, climo=None)</span> 



## cpc.geofiles.datasets.Dataset Objects



### <span class="function">\__init__(self, data_type=None)</span> 



## cpc.geofiles.datasets.DeterministicForecast Objects



### <span class="function">\__init__(self, fcst=None)</span> 



## cpc.geofiles.datasets.EnsembleForecast Objects



### <span class="function">\__init__(self, ens=None, ens_mean=None, ens_spread=None)</span> 



##### *`abstract property`* `ens_mean` 


##### *`abstract property`* `ens_spread` 


### <span class="function">get_ens_mean(self)</span> 

> Returns the ensemble mean
> 
> Since ens_mean is defined as a property which calls this method, it won't take up memory
> by default
> 
> ### Returns
> 
> - array: ensemble mean



### <span class="function">get_ens_spread(self)</span> 

> Returns the ensemble spread
> 
> Since ens_spread is defined as a property which calls this method, it won't take up memory
> by default
> 
> ### Returns
> 
> - array: ensemble spread



## cpc.geofiles.datasets.Forecast Objects



### <span class="function">\__init__(self)</span> 



## cpc.geofiles.datasets.Observation Objects



### <span class="function">\__init__(self, obs=None)</span> 


