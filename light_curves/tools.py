# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/tools.ipynb (unless otherwise specified).

__all__ = ['analyze_data', 'all_data_likelihood', 'fit_table', 'simulation', 'bb_overplot', 'WeightedSource']

# Cell
import pickle
import numpy as np
import matplotlib.pyplot as plt
from wtlike.config import *
from wtlike.bayesian import *
from wtlike.simulation import *
from wtlike.lightcurve import *
from wtlike.loglike import *
from wtlike.cells import *

def analyze_data(config, source):
    """
    Analyze data from the source

    Returns data and partitioned light curves
    """
    lc = get_lightcurve(config, source)
    cells = get_cells(config, source)
    edges = get_bb_partition(config, lc, LikelihoodFitness, key=f'BB-{source.name}')
    bb_cells = partition_cells(config, cells, edges);
    bb_lc  = fit_cells(config, bb_cells, )
    bb_lc.loc[:,'TS'] = (bb_lc.fit.apply(lambda fit: fit.ts))
    return lc, bb_lc

def all_data_likelihood(config, source):
    """
    Return likekihood for full dataset
    """
    cells = get_cells(config, source)
    return LogLike(concatenate_cells(cells))
    # fig1, ax1 = plt.subplots(num=1, figsize=(3,2))
    # ll.plot(xlim =( 0.5, 1.5), ax=ax1)

def fit_table(lc, expect=1.0):
    """Generate a summary table from a light curve"""
    fits = lc.fit
    flux = fits.apply(lambda f: f.flux)
    errors = fits.apply(lambda f: (round(f.errors[0]-f.flux,3), round(f.errors[1]-f.flux ,3) ) )
    sigma_dev = fits.apply(lambda f: round(f.poiss.sigma_dev(expect),1) )
    df = lc['t tw n'.split()].copy() # maybe fix warnings?
    df.loc[:,'flux'] = flux.values.round(4)
    df.loc[:, 'errors'] = errors.values
    df.loc[:, 'sigma_dev'] = sigma_dev.values
    df.loc[:, 'limit'] =  fits.apply(lambda f: f.limit)
    return df

def simulation(config, source, bb_key=None):
    """Create and analyze a simulation for the source
    Returns the simulated, and fit light curves
    """

    lc = get_lightcurve(config, source)
    data_cells = get_cells(config, source)

    #  Get the rate from the data
    cq = data_cells.query('e>0.3')
    T, N = np.sum(cq.tw), np.sum(cq.n)
    sflux=lambda t: N/T

    # simulate, then fit cells to create a simulated light curve
    sim_cells = simulate_cells(config, source, source_flux=sflux  )
    sim_lc  = fit_cells(config, sim_cells)

    sim_edges = get_bb_partition(config, sim_lc,  key=bb_key) #'simulated_BB_partition_Geminga')

    # partion, then fit the cells according to the edges
    sim_bb_cells = partition_cells(config, sim_cells, sim_edges);
    sim_bb_fit  = fit_cells(config, sim_bb_cells, )
    return sim_lc, sim_bb_fit

def bb_overplot(config, lc, bb_fit, ax=None,  **kwargs):
    fig, ax = plt.subplots(1,1, figsize=(12,4)) if not ax else (ax.figure, ax)
    flux_plot(config, lc, ax=ax, colors=(('lightblue', 'sandybrown', 'blue')),**kwargs)
    flux_plot(config, bb_fit, ax=ax, step=True, **kwargs)

class WeightedSource(PointSource):
    """
    """
    def __init__(self, config, sname):
        self.config=config

        fname = sname.replace(' ', '_').replace('+', 'p')
        wff = config.files.weights
        wfiles =list(wff.glob(f'{fname}_weights.pkl'))
        if len(wfiles)!=1:
            raise Exception(f'Weights for source {sname} not found.')
        with open(wfiles[0], 'rb') as file:
            self.weights =w = pickle.load(file, encoding='latin1')
        super().__init__(sname, w['source_lb'] )

    def analyze(self):
        lc, bb_lc = self.lt_curves = analyze_data(self.config, self)
        bb_overplot(self.config, *self.lt_curves , yscale='log', title=self.name);
        bb_lc.loc[:,'TS'] = (bb_lc.fit.apply(lambda fit: fit.ts)).round()
        return bb_lc
