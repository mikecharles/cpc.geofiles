"""
Defines a Dataset object. Datasets contain one or more data arrays, QC info, etc.
"""


class Dataset:
    """
    Base Dataset class
    """
    def __init__(self, data_type=None):
        self.data_type = data_type
        self.missing_dates = []
        self.missing_files = []
        self.dates_loaded = []


class Observation(Dataset):
    """
    Observation Dataset
    """
    def __init__(self, obs=None):
        Dataset.__init__(self, data_type='observation')
        self.data_type = 'observation'
        self.obs = obs


class Forecast(Dataset):
    """
    Forecast Dataset
    """
    def __init__(self):
        Dataset.__init__(self, data_type='forecast')
        self.data_type = 'forecast'


class EnsembleForecast(Forecast):
    """
    Ensemble Forecast Dataset
    """
    def __init__(self, ens=None, ens_mean=None, ens_spread=None):
        Forecast.__init__(self)
        self.ens = ens


    # def ens_mean(self):
    #     return


class DeterministicForecast(Forecast):
    """
    Ensemble Forecast Dataset
    """
    def __init__(self, fcst=None):
        Forecast.__init__(self)
        self.fcst = fcst


class Climatology(Dataset):
    """
    Climatology Dataset
    """
    def __init__(self, clim=None):
        Dataset.__init__(self, data_type='climatology')
        self.data_type = 'climatology'
        self.clim = clim
