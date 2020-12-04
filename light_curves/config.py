# AUTOGENERATED! DO NOT EDIT! File to edit: 00_config.ipynb (unless otherwise specified).

__all__ = ['MJD', 'UTC', 'day', 'first_data', 'Config', 'FileConfiguration', 'PointSource']

# Cell
from astropy.time import Time
from astropy.coordinates import SkyCoord
from dataclasses import dataclass
from typing import Tuple
import os,glob
import numpy as np

# Cell

day = 24*3600.
first_data=54683

def MJD(met):
    "convert MET to MJD"
    #mission_start = Time('2001-01-01T00:00:00', scale='utc').mjd
    # From a FT2 file header
    # MJDREFI =               51910. / Integer part of MJD corresponding to SC clock S
    # MJDREFF =  0.00074287037037037 / Fractional part of MJD corresponding to SC cloc
    mission_start = 51910.00074287037
    return (mission_start + met/day  )

def UTC(mjd):
    " convert MJD value to ISO date string"
    t=Time(mjd, format='mjd')
    t.format='iso'; t.out_subfmt='date_hm'
    return t.value

# Cell
@dataclass
class Config:
    """configuration parameters"""
    verbose : int = 3

    # photon selection
    mjd_range : Tuple=None
    radius: float = 5
    cos_theta_max:float=0.5
    z_max : float=100

    #binning
    energy_edges = np.logspace(2,6,17)

    # healpix
    nside : int=1024
    nest: bool=False

    #exposure calculation
    bins_per_decade: int=4
    base_spectrum: str='lambda E: (E/1000)**-2.1'
    energy_range: Tuple = (100.,1e6)

# Cell
@dataclass
class FileConfiguration:
    data:str = '$HOME/data'
    ft2: str = '$HOME/work/lat-data/ft2/*.fits'
    gti: str = '$HOME/work/lat-data/binned/*.fits'
    aeff:str = '$HOME/work/lat-data/aeff'

    def __post_init__(self):
        d = self.__dict__
        for name, value in d.items():
            d[name] = os.path.expandvars(value)
            if '*' in value:
                d[name] = glob.glob(d[name])

# Cell
class PointSource():
    """Manage the position and name of a point source
    """
    def __init__(self, name, position=None):
        """position: (l,b) tuple or None. if None, expect to be found by lookup
        """
        self.name=name
        if position is None:
            skycoord = SkyCoord.from_name(name)
            gal = skycoord.galactic
            self.l,self.b = (gal.l.value, gal.b.value)
        else:
            self.l,self.b = position
            skycoord = SkyCoord(self.l,self.b, unit='deg', frame='galactic')
        self.skycoord = skycoord
    def __str__(self):
        return f'Source "{self.name}" at: (l,b)=({self.l:.3f},{self.b:.3f})'
    def __repr__(self): return str(self)

    @property
    def ra(self):
        sk = self.skycoord.transform_to('fk5')
        return sk.ra.value
    @property
    def dec(self):
        sk = self.skycoord.transform_to('fk5')
        return sk.dec.value

    @classmethod
    def fk5(cls, name, position):
        """position: (ra,dec) tuple """
        ra,dec = position
        sk = SkyCoord(ra, dec, unit='deg',  frame='fk5').transform_to('galactic')
        return cls(name, (sk.l.value, sk.b.value))
