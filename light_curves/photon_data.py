# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/04_photon_data.ipynb (unless otherwise specified).

__all__ = ['get_photon_data']

# Cell
import os, sys
import healpy
import pickle
import pandas as pd
import numpy as np
import pyarrow.parquet as pq
from .config import *
from .load_gti import get_gti

# Cell
def _load_photon_data(config, table, tstart,
                      conepix, gti, center, band_limits, radius,
                      nest=True):
    """For a given month table, select photons in cone, add tstart to times,
    return DataFrame with band, time, pixel, radius
    """
    allpix = np.array(table.column('nest_index'))

    def cone_select(allpix, conepix, shift=None):
        """Fast cone selection using NEST and shift
        """
        if shift is None:
            return np.isin(allpix, conepix)
        assert nest, 'Expect pixels to use NEST indexing'
        a = np.right_shift(allpix, shift)
        c = np.unique(np.right_shift(conepix, shift))
        return np.isin(a,c)

    # a selection of all those in an outer cone
    incone = cone_select(allpix, conepix, 13)

    # times: convert to double, add to start, convert to MJD
    time = MJD(np.array(table['time'],float)[incone]+tstart)
    in_gti = gti(time)
    if np.sum(in_gti)==0:
        print(f'WARNING: no photons in GTI for month {month}!', file=sys.stderr)

    pixincone = allpix[incone][in_gti]

    # distance from center for all accepted photons
    ll,bb = healpy.pix2ang(config.nside, pixincone,  nest=nest, lonlat=True)
    cart = lambda l,b: healpy.dir2vec(l,b, lonlat=True)
    t2 = np.degrees(np.array(np.sqrt((1.-np.dot(center, cart(ll,bb)))*2), np.float32))

    # assemble the DataFrame, remove those outside the radius
    out_df = pd.DataFrame(np.rec.fromarrays(
        [np.array(table['band'])[incone][in_gti], time[in_gti], pixincone, t2],
        names='band time pixel radius'.split()))

    # apply final selection for radius and energy range

    if band_limits is None: return out_df.query(f'radius<{radius}')

    return out_df.query(f'radius<{radius} & {band_limits[0]} < band < {band_limits[1]}')

# Cell
def _get_photons(config, source, nest=True):
    # check GTI
    gti = get_gti(config)

    # cone geometry stuff: get corresponding pixels and center vector
    l,b,radius = source.l, source.b, config.radius
    cart = lambda l,b: healpy.dir2vec(l,b, lonlat=True)
    conepix = healpy.query_disc(config.nside, cart(l,b), np.radians(radius), nest=nest)
    center = healpy.dir2vec(l,b, lonlat=True)

    ebins = config.energy_edges
    ecenters = np.sqrt(ebins[:-1]*ebins[1:]);
    band_limits = 2*np.searchsorted(ecenters, config.energy_range) if config.energy_range is not None else None


    # get the monthly-partitioned dataset and tstart values
    datapath = config.files.data
    dataset = datapath/'dataset'
    tstart_dict= pickle.load(open(datapath/'tstart.pkl', 'rb'))
    months = tstart_dict.keys()

    if config.verbose>0:
        print(f'Loading  {len(months)} months from Arrow dataset {dataset}\n', end='')

    dflist=[]
    for month, tstart in tstart_dict.items(): #months:
        table= pq.read_table(dataset, filters=[f'month == {month}'.split()])

        d = _load_photon_data(config, table, tstart,
                              conepix, gti, center, band_limits, radius,
                              nest)
        if d is not None:
            dflist.append(d)
            if config.verbose>1: print('.', end='')
        else:
            if config.verbose>1: print('x', end='')
            continue

    assert len(dflist)>0, '\nNo photon data found?'
    df = pd.concat(dflist, ignore_index=True)
    return df

# Cell
def get_photon_data(config: 'configuration data',
                    source: 'Source data',
                    key='',
                    ):
    """
    Parameters:

    - `source` -- `PointSource` object
    - `key` [''] cache key -- default, use "photons_name", set to None to ignore cache

    Steps:
    -  Read photon data from a Parquet dataset,
    -  select cone around the source
    -  use exposure to add exposures
    -  return DataFrame with columns `band time pixel radius`
    """

    key = f'photons_{source.name}' if key=='' else key

    if config.verbose>0 and key is not None:
        print(f'Photon data: {"Saving to" if key not in config.cache else "Restoring from"} cache with key "{key}"')

    df = config.cache(key, _get_photons, config, source)

    if config.verbose>0:
        emin,emax = config.energy_range or (config.energy_edges[0],config.energy_edges[-1])
        print(f'\n\tSelected {len(df):,} photons within {config.radius}'\
              f' deg of  ({source.l:.2f},{source.b:.2f})')
        print(f'\tEnergies: {emin:.1f}-{emax:.0f} MeV')
        ta,tb = df.iloc[0].time, df.iloc[-1].time
        print(f'\tDates:    {UTC(ta):16} - {UTC(tb)}'
            f'\n\tMJD  :    {ta:<16.1f} - {tb:<16.1f}')

    return df