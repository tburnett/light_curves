# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/07_cells.ipynb (unless otherwise specified).

__all__ = ['get_cells']

# Cell
import os
import numpy as np
import pandas as pd
from .config import Config, Files, PointSource
from .photon_data import get_photon_data
from .weights import add_weights, check_source
from .exposure import get_exposure

# Cell
def _get_default_bins(config, exposure):
    """set up default bins from exposure; adjust stop to come out even
    # round to whole day
    """

    start = np.round(exposure.start.values[0])
    stop =  np.round(exposure.stop.values[-1])
    if config.mjd_range is None:
        config.mjd_range = (start,stop)

    step = config.time_interval
    nbins = int(round((stop-start)/step))
    tb =time_bins = np.linspace(start, stop, nbins+1)
    if config.verbose>0:
        print(f'Time bins: {nbins} intervals of {step} days, '\
              f'in range ({time_bins[0]:.1f}, {time_bins[-1]:.1f})')
    return time_bins

# Cell
def _get_binned_exposure(time_bins, exposure):

    # get stuff from photon data, exposure calculation
    exp   = exposure.exposure.values
    estart= exposure.start.values
    estop = exposure.stop.values

    #use cumulative exposure to integrate over larger periods
    cumexp = np.concatenate(([0],np.cumsum(exp)) )

    # get index into tstop array of the bin edges
    edge_index = np.searchsorted(estop, time_bins)
    # return the exposure integrated over the intervals
    cum = cumexp[edge_index]
    return np.diff(cum)/(cum[-1]-cum[0]) * (len(time_bins)-1)

# Cell
class _WeightedCells(object):
    """ Generate a list of cells, with access to cell data
        weights
    """

    def __init__(self, config, source,
                 photon_data:'DataFrame with photon data',
                 exposure: 'DataFrame with exposure',
                 bins: 'time bins default if None'=None,
                ):
        """
        Use time binning photon_data to generate list of cells
        """
        self.source_name =source.name
        self.verbose = config.verbose

        bins = bins if bins is not None else  _get_default_bins(config, exposure)
        self.bins = bins

        # restrict photons to range of bin times
        photons = photon_data.query(f'{bins[0]}<time<{bins[-1]}')

        self.N = len(bins)-1 # number of bins
        self.bin_centers = 0.5*(bins[1:]+bins[:-1])

        # exposure binned as well
        self.fexposure = _get_binned_exposure(bins, exposure)

        # get the photon data with good weights, not NaN
        w = photons.weight
        good = np.logical_not(np.isnan(w))
        self.photons = photons.loc[good]
        self.weights = w = self.photons.weight.values

        # estimates for averate signal and background per cell
        self.S = np.sum(w)/self.N
        self.B = np.sum(1-w)/self.N

        # use photon times to get indices of bin edges
        self._edges = np.searchsorted(self.photons.time, bins)


    def __repr__(self):
        return f'''{self.__class__}:
        {len(self.fexposure)} intervals from {self.bins[0]:.1f} to {self.bins[-1]:.1f} for source {self.source_name}
        S {self.S:.2f}  B {self.B:.2f} '''

    def __getitem__(self, i):
        """ get info for ith time bin and return dict with
            t : MJD
            tw: bin width,
            e: exposure as fraction of total,
            n : number of photons in bin
            w : list of weights as uint8 integers<=255
            S,B:  value
        """
        k   = self._edges

        wts = np.array(self.weights[k[i]:k[i+1]]*256, np.uint8)
        n = len(wts)
        e = self.fexposure[i]
        tw  = self.bins[i+1]-self.bins[i]

        return dict(
                t=self.bin_centers[i], # time
                tw = tw,  # bin width
                e=e, # moving to this name
                n=n, # number of photons in bin
                w=wts,
                S= e *self.S,
                B= e *self.B,
                )

    def __len__(self):
        return self.N

    @property
    def dataframe(self):
        """ combine all cells into a dataframe
        """
        df = pd.DataFrame([cell for cell in self])
        return df


# Cell
def get_cells(config, files, source, bins=None):
    """Return a cells DataFrame for the source
    bins is an array of bin edges to define cells. Use default
    binning from config is None
    """

    photon_data = get_photon_data(config, files,  source )
    add_weights(config, files, photon_data, source)
    exposure = get_exposure(config, files, None, source)

    return _WeightedCells(config, source,photon_data, exposure, bins).dataframe