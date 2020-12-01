"""
Useful plotting routines
"""
import os, sys
import numpy as np
import matplotlib.pylab as plt
import pandas as pd

def poiss_pars_hist(pars:'array of 3-tuples', bins=25, fignum=101):
    
    pars =np.array(list(map(list,pars))).T
    labels=['flux', 'equivalent couints', 'background']
    fig, axx = plt.subplots(1,3, figsize=(12,2.5), num=fignum)
    hkw = dict(bins=bins, histtype='step', lw=2)
    for ax, par, label in zip(axx, pars, labels):
        ax.hist(par, label=f'median:{np.median(par):.2f}', **hkw)
        ax.set(xlabel=label)
        ax.legend()
        ax.grid(alpha=0.5)
    return fig
        
def phase_plot(df:'DataFrame with columns t, sigma and pull', 
               period, 
               bins=50, 
               name:'column in the dataframe to plt'='pull',
               ax=None,
               fignum=1,
              )->'Figure':
    """ Return a figure showing phases"""

    def phase_bins():
        phase = np.mod(df.t, period)
        phase_bin = np.digitize(phase, np.linspace(0,period,bins+1))
        g = df.groupby(phase_bin)
        p = g[name]
        return p.agg(np.mean), p.agg(np.std)/np.sqrt(p.agg(len))

    y, yerr = phase_bins()
    sig = (df.sigma).mean()
    y = 1+ y* sig
    yerr *= sig
    x = (np.arange(bins)+0.5)/bins
    fig,ax = plt.subplots(figsize=(8,3),num=fignum) if not ax else (ax.figure, ax) 
    ax.errorbar(x=x, y=y, yerr=yerr, fmt=' ', marker='o');
    ax.set(xlabel=f'phase within {period:.2f} day period', xlim=(0,1),
          ylabel='relative flux',)
    ax.axhline(1.0, color='grey')
    ax.grid(alpha=0.5)
    return fig