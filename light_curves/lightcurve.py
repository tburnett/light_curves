# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/09_lightcurve.ipynb (unless otherwise specified).

__all__ = ['fit_cells', 'get_lightcurve', 'flux_plot']

# Cell
import numpy as np
import pylab as plt
import pandas as pd

# Cell
from .loglike import (LogLike, GaussianRep, Gaussian2dRep, PoissonRep, PoissonRepTable)

class _LightCurve(object):
    """ Apply likelihood fits to a set of cells

    parameters:
       - cells : a table with index t, columns  tw, n, e, w, S, B
       - min_exp : minimum fractional exposure allowed
       - rep_name : represention to use

    Generates a DataTable with columns n, ep, fit

    """

    rep_class =  [GaussianRep, Gaussian2dRep, PoissonRep, PoissonRepTable]
    rep_list =   'gauss gauss2d poisson poissontable'.split()

    def __init__(self, config,
                all_cells,
                source,
                min_exp:  'minimum exposure factor'= 0.3,
                rep_name: 'likelihood rep name'='',

                ):
        """Apply fits to the likelihoods for a set of cells


        """

        self.source_name = source.name

        # select the set of cells
        cells = all_cells.query(f'e>{min_exp}').copy()

        # generate a list of LogLike objects for each
        cells.loc[:,'loglike'] = cells.apply(LogLike, axis=1)
        if config.verbose>0:
            print(f'Loaded {len(cells)} / {len(all_cells)} cells with exposure >'\
                  f' {min_exp} for light curve analysis')
            print(f'first cell: {cells.iloc[0]}')

        # analyze using selected rep
        rep_name = rep_name or config.likelihood_rep

        if rep_name not in self.rep_list:
            raise Exception(f'Unrecognized rep: "{rep_name}", must be one of {self.rep_list}')
        repcl = self.rep_class[self.rep_list.index(rep_name)]

        if config.verbose>1:
            print(f'Fitting likelihoods with {rep_name} representation')

        # making output with reduced columns
        self.ll_fits = cells['t tw n e'.split()].copy()
        self.ll_fits.loc[:,'fit'] = cells.loglike.apply(repcl)

    def __repr__(self):
        return f'{self.__class__.__name__}: source "{self.source_name}" fit with {len(self.ll_fits)} cells'


    @property
    def dataframe(self):
        """return the DataFrame
        """
        return self.ll_fits

# Cell
def fit_cells(config,
            input_cells,
            min_exp:  'minimum exposure factor'= 0.3,
            repcl = PoissonRep,

            ):
    """Apply fits to the likelihoods for a set of cells
    return light-curve dataframe

    """

    # select the set of cells
    cells = input_cells.query(f'e>{min_exp}').copy()

    # generate a list of LogLike objects for each
    cells.loc[:,'loglike'] = cells.apply(LogLike, axis=1)
    if config.verbose>0:
        print(f'Loaded {len(cells)} / {len(input_cells)} cells with exposure >'\
              f' {min_exp} for fitting')

    # making output with reduced columns
    ll_fits = cells['t tw n e'.split()].copy()
    ll_fits.loc[:,'fit'] = cells.loglike.apply(repcl)

    return ll_fits

# Cell

from .config import Config,  PointSource
from .cells import get_cells

def get_lightcurve(config,  source, bin_edges=None, key=''):
    """Returns a lightcurve table for the source

    - `source` -- a PointSource object
    - `bin_edges` -- optional to select other than default described in config
    - `key` -- optional cache key. Set to None to disable cache use

    """
    def doit():
        cells = get_cells(config,  source, bin_edges)
        lc = _LightCurve(config, cells, source).dataframe
        return lc

    if bin_edges is None:
        # use cache only with default bins
        key = f'lightfcurve_{source.name}' if key=='' else  key
        description = f'Light curve for {source.name}' if config.verbose>0 and key is not None else ''
        return config.cache(key, doit, description=description)
    else:
        return doit()

# Cell
def flux_plot(config, lightcurve, ts_min=9,
              title=None, ax=None, fignum=1, figsize=(12,4),
              step=False,
              tzero:'time offset'=0,
              colors=('cornflowerblue','sandybrown', 'blue'), fmt=' ',
              **kwargs):
    """Make a plot of flux vs. MJD

    - lightcurve
    - ts_min -- threshold for ploting signal
    - colors -- tuple of colors for signal, limit, step
    - tzero -- time offset
    - kwargs -- apply to the Axis object
    - step   -- add a "step" plot

    returns the Figure instance
    """
    kw=dict(yscale='linear',
            xlabel='MJD'+ f' - {tzero}' if tzero else '' ,
            ylabel='relative flux')
    kw.update(**kwargs)
    df=lightcurve
    rep = config.likelihood_rep
    if rep =='poisson':
        ts = df.fit.apply(lambda f: f.ts)
        limit = ts<ts_min
        bar = df.loc[~limit,:]
        lim = df.loc[limit,:]
        allflux= np.select([~limit, limit],
                        [df.fit.apply(lambda f: f.flux).values,
                         df.fit.apply(lambda f: f.limit).values],
                       )

    else:
        bar=df; lim=[]

    fig, ax = plt.subplots(figsize=figsize, num=fignum) if ax is None else (ax.figure, ax)\
        if ax is not None else (ax.figure,ax)

    # the points with error bars
    t = bar.t.values-tzero
    tw = bar.tw.values
    fluxmeas = allflux[~limit]
    upper = bar.fit.apply(lambda f: f.errors[1]).values
    lower = bar.fit.apply(lambda f: f.errors[0]).values
    error = np.array([upper-fluxmeas, fluxmeas-lower])

#     if rep=='poisson':
#         dy = [bar.errors.apply(lambda x: x[i]).clip(0,4) for i in range(2)]
#     elif rep==='gauss' or rep=='gauss2d':
#         dy = bar.sig_flux.clip(0,4)
#     else: assert False, f'Unrecognized likelihood rep: {rep}'

    ax.errorbar(x=t, xerr=tw/2, y=fluxmeas, yerr=error, fmt=fmt, color=colors[0], )#'silver')

    if step:
        t = df.t.values-tzero
        xerr = df.tw.values/2;
        x = np.append(t-xerr, [t[-1]+xerr[-1]]);
        y = np.append(allflux, [allflux[-1]])
        ax.step(x, y, color=colors[2], where='post', lw=2)


    # now do the limits (only for poisson rep)
    error_size=2
    if len(lim)>0:
        t = lim.t-tzero
        tw = lim.tw

        y = allflux[limit]
        yerr=0.2*(1 if kw['yscale']=='linear' else y)
        ax.errorbar(x=t, y=y, xerr=tw/2,
                yerr=yerr,  color=colors[1],
                uplims=True, ls='', lw=error_size, capsize=3*error_size, capthick=0,
               )

    #ax.axhline(1., color='grey')
    ax.set(**kw)
    ax.set_title(title) # or f'{source_name}, rep {self.rep}')
    ax.grid(alpha=0.5)
    return fig