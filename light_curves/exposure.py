# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/03_exposure.ipynb (unless otherwise specified).

__all__ = ['get_exposure']

# Cell
from astropy.io import fits
import numpy as np
import pandas as pd
from scipy.integrate import simps
from .config import MJD

# Cell
def _process_ft2(config, source, ft2_files, gti, effective_area):
    """Process a set of FT2 files, with S/C history data
    Parameters:
        - config -- verbose, cos_theta_max, z_max
        - source -- l,b for position
        - ft2_files -- list of spacecraft files
        - gti -- GTI object with allowed intervals
        - effective_area -- function of energy and angle with respect to zenity
    Generate a dataset with fields:
        - start, stop : start  and stop times in MJD
        - exposure    : calculated exposure using effective area

     """
    # combine the files into a DataFrame with following fields besides START and STOP (lower case for column)
    fields    = ['LIVETIME','RA_SCZ','DEC_SCZ', 'RA_ZENITH','DEC_ZENITH']
    if config.verbose>1:
        print(f'Processing {len(ft2_files)} S/C history (FT2) files')
        print(f'  applying cuts cos(theta) < {config.cos_theta_max},  z < {config.z_max}')
    sc_data=[]
    for filename in ft2_files:
        with fits.open(filename) as hdu:
            scdata = hdu['SC_DATA'].data
            # get times to check against MJD limits and GTI
            start, stop = [MJD(np.array(scdata.START, float)),
                           MJD(np.array(scdata.STOP, float))]
            if config.mjd_range is not None:
                a,b=  config.mjd_range
                if stop[-1]<a:
                    print(f'\tfile {filename}: skip, before selected range' )
                    continue
                elif start[0]>b:
                    print(f'\tfile {filename}: quit, beyond range')
                    break
            # apply GTI to bin center (avoid edge effects?)
            in_gti = gti(0.5*(start+stop))
            if config.verbose>2:
                print(f'\tfile {filename}: {len(start)} entries, {sum(in_gti)} in GTI')
            t = [('start', start[in_gti]), ('stop',stop[in_gti])]+\
                [(field.lower(), np.array(scdata[field][in_gti],np.float32)) for field in fields ]
            sc_data.append( pd.DataFrame(dict(t) ) )
    df = pd.concat(sc_data, ignore_index=True)

    # calculate cosines with respect to sky direction
    sc = source
    ra_r,dec_r = np.radians(sc.ra), np.radians(sc.dec)
    sdec, cdec = np.sin(dec_r), np.cos(dec_r)

    def cosines( ra2, dec2):
        ra2_r =  np.radians(ra2.values)
        dec2_r = np.radians(dec2.values)
        return np.cos(dec2_r)*cdec*np.cos(ra_r-ra2_r) + np.sin(dec2_r)*sdec

    pcosines = cosines(df.ra_scz,    df.dec_scz)
    zcosines = cosines(df.ra_zenith, df.dec_zenith)

    # mask out entries too close to zenith, or too far away from ROI center
    mask =   (pcosines >= config.cos_theta_max) & (zcosines>=np.cos(np.radians(config.z_max)))
    if config.verbose>1:
        print(f'\tFound {len(mask):,} S/C entries:  {sum(mask):,} remain after zenith and theta cuts')
    dfm = df.loc[mask,:]
    livetime = dfm.livetime.values
    config.dfm = dfm ##############debug
    # apply MJD range if present. note times in MJD
    start, stop = dfm.start,dfm.stop
    lims = slice(None)
    if config.mjd_range is not None:
#         a, b = config._get_limits(start)
        a, b = np.searchsorted(start, config.mjd_range)
        if a>0 or b<len(start):
            if config.verbose>1:
                print(f'\tcut from {len(start):,} to {a} - {b}, or {b-a:,} entries after MJD range selection')
            dfm = dfm.iloc[a:b]
            lims = slice(a,b)


    expose = _exposure(config, effective_area, livetime[lims], pcosines[mask][lims])
    return pd.DataFrame(dict(start=start[lims],stop=stop[lims], exposure=expose))

# Cell
def _exposure(config, effective_area, livetime, pcosine):
    """return exposure calculated for each pair in livetime and cosines arrays

    uses effective area
    """
    assert len(livetime)==len(pcosine), 'expect equal-length arrays'

    # get a set of energies and associated weights from a trial spectrum

    emin,emax = config.energy_range
    loge1=np.log10(emin); loge2=np.log10(emax)

    edom=np.logspace(loge1, loge2, int((loge2-loge1)*config.bins_per_decade+1))
    if config.verbose>1:
        print(f'Calculate exposure using the energy domain'\
              f' {emin}-{emax} {config.bins_per_decade} bins/decade' )
    base_spectrum = eval(config.base_spectrum) #lambda E: (E/1000)**-2.1
    assert base_spectrum(1000)==1.
    wts = base_spectrum(edom)

    # effectivee area function from
    ea = effective_area

    # a table of the weighted for each pair in livetime and pcosine arrays
    rvals = np.empty([len(wts),len(pcosine)])
    for i,(en,wt) in enumerate(zip(edom,wts)):
        faeff,baeff = ea([en],pcosine)
        rvals[i] = (faeff+baeff)*wt

    aeff = simps(rvals,edom,axis=0)/simps(wts,edom)
    return (aeff*livetime)

# Cell
def get_exposure(config, files, gti, source):
    """Return the exposure for the source
    If gti is None, regenerate it
    """
    from  light_curves.load_gti import get_gti
    from .effective_area import EffectiveArea
    gti = gti or get_gti(config, files.gti)
    aeff = EffectiveArea(file_path = files.aeff)
    return _process_ft2(config, source, files.ft2, gti, aeff)
