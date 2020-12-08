# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/07_cells.ipynb (unless otherwise specified).

__all__ = ['get_cells']

# Cell
import os
import numpy as np
import pandas as pd
from .config import Config, Files, PointSource
from .photon_data import get_photon_data
from .weights import add_weights
from .exposure import get_exposure

# Cell
def _get_time_bins(config, exposure):
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
    return np.diff(cum)/cum[-1] * (len(time_bins)-1)

# Cell
class _WeightedCells(object):
    """ Generate a list of cells, with access to cell data
        weights
    """

    def __init__(self, config, source,
                  photon_data:'DataFrame with photon data',
                  exposure: 'DataFrame with exposure',
                  ):
        """
        Use time binning and data (a TimedData) object to generate list of cells
        """
        self.data = photon_data
        self.source_name =source.name
        self.verbose = config.verbose


        self.bins = bins = _get_time_bins(config, exposure)


        self.N = len(bins)-1 # number of bins
        self.bin_centers = 0.5*(bins[1:]+bins[:-1])
        self.fexposure = _get_binned_exposure(bins, exposure)

        # get the photon data with good weights, not NaN

        w = photon_data.weight
        good = np.logical_not(np.isnan(w))
        self.photons = photon_data.loc[good]
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
            fexp: exposure as fraction of total,
            n : number of photons in bin
            w : list of weights as uint8 integers<=255
            S,B:  value
        """
        k   = self._edges

        wts = np.array(self.weights[k[i]:k[i+1]]*256, np.uint8)
        n = len(wts)
        fexp = self.fexposure[i]
        tw  = self.bins[i+1]-self.bins[i]

        return dict(
                t=self.bin_centers[i], # time
                tw = tw,  # bin width
                fexp=fexp,
                n=n, # number of photons in bin
                w=wts,
                S= fexp*self.S,
                B= fexp*self.B,
                )

    def __len__(self):
        return self.N

    @property
    def dataframe(self):
        """ a view of the data as a DataFrame, using the MJD time as an index
        """
        d = dict()
        for cell in self:
            d[cell['t']] = cell
        return pd.DataFrame.from_dict(d, orient='index' )

    def test_plots(self):
        """Make a set of plots of exposure, counts, properties of weights, if any
        """
        import matplotlib.pyplot as plt

        has_weights = len(self.weights)>0
        fig, axx = plt.subplots( 5 if has_weights else 3, 1,
                    figsize=(12,10 if has_weights else 6),
                    sharex=True,
                    gridspec_kw=dict(hspace=0,top=0.95),)
        times=[]; vals = []

        for cell in self:
            t, e, n, w = [cell[q] for q in 't fexp n w'.split()]
            if e==0:
                continue
            times.append(t)
            v =  [e, n, n/e ]
            if has_weights:
                v= v + [ w.mean(), np.sum(w**2)/sum(w)]
            vals.append(v)
        vals = np.array(vals).T
        labels =  ['rel exp','counts','count rate']
        if has_weights: labels = labels +  ['mean weight', 'rms/mean weight']
        for ax, v, ylabel in zip(axx, vals,labels):
            ax.plot(times, v, '+b')
            ax.set(ylabel=ylabel)
            ax.grid(alpha=0.5)
        axx[-1].set(xlabel='MJD')
        fig.suptitle(self.source_name)

# Cell
def get_cells(config, files, source):
    """Return a DataFrame with the cells

    """

    photon_data = get_photon_data(config, files,  source )
    add_weights(config, files, photon_data, source)
    exposure = get_exposure(config, files, None, source)

    return _WeightedCells(config, source,photon_data, exposure).dataframe