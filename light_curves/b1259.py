# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/B1259.ipynb (unless otherwise specified).

__all__ = ['B1259Periastron']

# Cell
import numpy as np
import matplotlib.pyplot as plt
from .tools import *
from wtlike.config import *
from wtlike.bayesian import *
from wtlike.lightcurve import *
from utilities.ipynb_docgen import *

# Cell

class B1259Periastron(BayesianBlockAnalysis):

    tp, period = 55544.694, 1236.7243

    def __init__(self, config, bins=None, bin_key=None, clear=None):
        source = PointSource('PSR_B1259-63')
        super().__init__(config, source, bins=bins, clear=clear)
        self.partition( key = bin_key, clear=clear)

        self.mjd_dates = [self.tp+n*self.period for n in range(4)]

    def date_info(self):
        return pd.DataFrame([dict(MJD=round(d,3), UTC=UTC(d)) for d in self.mjd_dates ])

    def full_plot(self, fignum=2):
        fig, ax2 = plt.subplots(1,1, sharex=True, figsize=(20,4), num=fignum)
        self.plot( ax = ax2, yscale='log')
        ax2.text(0.05, 0.85, self.source.name,  transform=ax2.transAxes);
        ax2.set_xlabel('MJD', fontsize=20)
        return fig

    def stacked_plots(self, fignum=3, ylim=(2,200), ts_min=4):

        tp, p =self.tp, self.period
        fig, axx = plt.subplots(4,1, sharex=True, sharey=True, figsize=(12,12), num=fignum)
        plt.subplots_adjust(hspace=0.)
        for i, ax in enumerate(axx.flatten()):
            self.plot( ax=ax, tzero=tp+i*p, xlim=(-60,150), ylim=ylim, ts_min=ts_min,
                     colors=('red', 'bisque', 'blue'),
                     fmt='o', yscale='log', xlabel='',ylabel='', )
            ax.text(0.02, 0.85, UTC(tp+i*p)[:4], transform=ax.transAxes)
            ax.axvline(0, color='grey', ls=':')
        axx[-1].set_xlabel('days about periastron', fontsize=20)
        fig.text(0.04, 0.5, 'Relative Flux', va='center', rotation='vertical', fontsize=20)
        fig.width=600
        return fig