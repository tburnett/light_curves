# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/11_lightcurve.ipynb (unless otherwise specified).

__all__ = ['get_lightcurve', 'flux_plot']

# Cell
import numpy as np
import pylab as plt
import pandas as pd

# Cell
from .loglike import (LogLike, GaussianRep, Gaussian2dRep, PoissonRep, PoissonRepTable)

class _LightCurve(object):
    """ Apply likelihood fits to a set of cells

    parameters:
       - cells : a table with index t, columns  tw, n, fexp, w, S, B
       - min_exp : minimum fractional exposure allowed
       - rep_name : represention to use

    Generates a DataTable with columns n, fexp, fit

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
        cells = all_cells.query(f'fexp>{min_exp}').copy()

        # generate a list of LogLike objects for each
        cells.loc[:,'loglike'] = cells.apply(LogLike, axis=1)
        if config.verbose>0:
            print(f'Loaded {len(cells)} / {len(all_cells)} cells with exposure >'\
                  f' {min_exp} for light curve analysis')

        # analyze using selected rep
        rep_name = rep_name or config.likelihood_rep

        if rep_name not in self.rep_list:
            raise Exception(f'Unrecognized rep: "{rep_name}", must be one of {self.rep_list}')
        repcl = self.rep_class[self.rep_list.index(rep_name)]

        if config.verbose>1:
            print(f'Fitting likelihoods with {rep_name} representation')

        # making output with reduced columns
        self.ll_fits = cells['n fexp'.split()].copy()
        self.ll_fits.loc[:,'tw'] = config.time_interval
        self.ll_fits.loc[:,'fit'] = cells.loglike.apply(repcl)

    def __repr__(self):
        return f'{self.__class__.__name__}: source "{self.source_name}" fit with {len(self.ll_fits)} cells'


    @property
    def dataframe(self):
        """return the DataFrame
        """
        return self.ll_fits

# Cell

from .config import Config, Files, PointSource
from .cells import get_cells

def get_lightcurve(config, files, source):
    """Returns a lightcurve table for the source

    """
    fcache = files.cache/f'{source.filename}_lightcurve.pkl' if config.use_cache else None

    if fcache and fcache.exists():
        if config.verbose>1:
            print(f'Restoring the light curve from {fcache} ' )
        lc = pd.read_pickle(fcache)
        return lc

    all_cells = get_cells(config, files, source)
    lc = _LightCurve(config, all_cells, source).dataframe

    if fcache:
        if config.verbose>1:
            print(f'Saving the light curve at {fcache} ')
        lc.to_pickle(fcache)

    return lc


# Cell
def flux_plot(config, lightcurve, ts_max=9,  title=None, ax=None, fignum=1, **kwargs):
    """Make a plot of flux vs. MJD

    - lightcurve
    - ts_max -- threshold for ploting limit
    - kwargs -- apply to the Axis object
    """
    kw=dict(yscale='linear',xlabel='MJD', ylabel='relative flux',)
    kw.update(**kwargs)
    df=lightcurve
    rep = config.likelihood_rep
    if rep =='poisson':
        ts = df.fit.apply(lambda f: f.ts)
        limit = ts<ts_max
        bar = df.loc[~limit,:]
        lim = df.loc[limit,:]
    else:
        bar=df; lim=[]

    fig, ax = plt.subplots(figsize=(12,4), num=fignum) if ax is None else (ax.figure, ax)\
        if ax is not None else (ax.figure,ax)

    # the points with error bars
    t = bar.index
    tw = bar.tw if 'tw' in bar.columns else np.full(len(t), config.time_interval)
    flux =  bar.fit.apply(lambda f: f.flux).values
    error = bar.fit.apply(lambda f: np.array(f.errors)-f.flux).values

#     if rep=='poisson':
#         dy = [bar.errors.apply(lambda x: x[i]).clip(0,4) for i in range(2)]
#     elif rep==='gauss' or rep=='gauss2d':
#         dy = bar.sig_flux.clip(0,4)
#     else: assert False, f'Unrecognized likelihood rep: {rep}'

    ax.errorbar(x=t, xerr=tw/2, y=flux, yerr=error, fmt=' ', color='silver')

    # now do the limits (only for poisson rep)
    if len(lim)>0:
        t = lim.index
        tw = lim.tw

        y = lim.fit.apply(lambda f: f.limit).values
        yerr=0.2*(1 if kw['yscale']=='linear' else y)
        ax.errorbar(x=t, y=y, xerr=tw/2,
                yerr=yerr,  color='lightsalmon',
                uplims=True, ls='', lw=2, capsize=4, capthick=0,
                alpha=0.5)

    #ax.axhline(1., color='grey')
    ax.set(**kw)
    ax.set_title(title) # or f'{source_name}, rep {self.rep}')
    ax.grid(alpha=0.5)
    return fig