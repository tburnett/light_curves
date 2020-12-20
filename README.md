# The `light_curve` package
> Code for generating fermi-LAT light curves. <br>


## Background

This package has code that is being adapted to the [nbdev](https://nbdev.fast.ai/) environment from [github package lat-timing](https://github.com/tburnett/lat-timing) to manage light curves of Fermi-LAT sources.  

As pointed out there, it is based on a [paper](https://arxiv.org/pdf/1910.00140.pdf) by Matthew Kerr, 

And at the same time, I've ported some code from  my [jupydoc](https://github.com/tburnett/jupydoc) documention package to allow enhanced documentation combining Markdown and code.

## Installation
Currently in pre-alpha, and must be cloned. This brings up the `nbdev` stuff as well.


<details class="description">
    <summary>Code details ...</summary>
    
```python
#collapse_hide

def road_map():
    """
    ## Setup declarations
    
    The following describes the module `config`. The defaults are wired-in
    for now, but could be obtained from an editable yaml file.
    
    ### config.Config -- parameters
    
    {config_text}
    
    ### config.Files -- default file paths
    {files_text}
 
    These are dataclass classes, and can be initialized with
    parameters. For example, to suppress printout 
        
    ```
    config = Config(verbose=0)
    ```
    
    
    ### config.cache -- a file cache
    The class `Cache`, available from `config.cache` implements a file cache.
    
    {cache_text}
    


    
    ## The light curve
    
    The light curve can be represented by plots of flux vs. time. The time range,
    limited by 'config.mjd_range`, if set. The actual livetime, during which *Fermi* is
    collecting data, is further limited by the GTI, for good-time interval. This is a list
    of start,stop pairs.
    
    The module [gti](/light_curves/lgti.html) defines `get_gti`.
    
    During the valid times, a the flux, or rate, is estimated by counting the number 
    of photons and dividing by the exposure.
    
    The source is defined by instantiating a [PointSource(/light_curves/config#PointSource) object, defined in 
    
    
    ### Exposure
    
    The exposure for the specified source is calculated from the  [exposure](/light_curves/exposure.html) module,
    which implements `get_exposure`. It depends on:

    - Space craft info (FT2)
    The FT2 file(s) contain spacecraft position and orientation as a function of time.
    
    - Efffective Area
    The module [effective_area](light_curves/effective_area.html) defines the functor class
    `EffectiveArea`, needed to calculate the exposure
    
    
    ### Photon data
    
    ### Weights
    
    Each photon 
    
    ### Cells
    
    A "cell" represents a time interval to measure the flux.
    
    This is where the ...
    

    """
    from light_curves.config import Config, Files, PointSource
    from light_curves.lightcurve import get_lightcurve, flux_plot
    
    config = Config()
    config_text = monospace(config, summary='config parameter list')
    files_text = monospace(Files(), summary='file list')
    files = Files()
 
    cache_text = monospace(config.cache, 'cache contents' )
    assert files.valid
    return locals()
    
from light_curves.config import Files
if Files().valid:
    nbdoc(road_map) 
```

</details>


## Setup declarations

The following describes the module `config`. The defaults are wired-in
for now, but could be obtained from an editable yaml file.

### config.Config -- parameters

<details class="descripton" ><summary data-open="Hide " data-close="Show "> config parameter list </summary> <p style="margin-left: 5%"><pre>Configuration parameters <br>  verbose         : 3<br>  mjd_range       : None<br>  radius          : 5<br>  cos_theta_max   : 0.4<br>  z_max           : 100<br>  time_interval   : 1<br>  nside           : 1024<br>  nest            : True<br>  bins_per_decade : 4<br>  base_spectrum   : lambda E: (E/1000)**-2.1<br>  energy_range    : (100.0, 1000000.0)<br>  likelihood_rep  : poisson<br></pre></p> </details>

### config.Files -- default file paths
<details class="descripton" ><summary data-open="Hide " data-close="Show "> file list </summary> <p style="margin-left: 5%"><pre>File paths for light curves<br>  data       : /home/burnett/data<br>  ft2        : /home/burnett/work/lat-data/ft2<br>  gti        : /home/burnett/work/lat-data/binned<br>  aeff       : /home/burnett/work/lat-data/aeff<br>  weights    : /home/burnett/onedrive/fermi/weight_files<br>  cachepath  : /tmp/lc_cache<br></pre></p> </details>

These are dataclass classes, and can be initialized with
parameters. For example, to suppress printout 
    
```
config = Config(verbose=0)
```


### config.cache -- a file cache
The class `Cache`, available from `config.cache` implements a file cache.

<details class="descripton" ><summary data-open="Hide " data-close="Show "> cache contents </summary> <p style="margin-left: 5%"><pre>Cache contents<br> key                          size  time                 name, in folder /tmp/lc_cache<br>  gti                      1018319  2020-12-17 15:17     cache_file_26e0b050cac876b4.pkl<br>  exposure_Geminga        86263776  2020-12-17 15:47     cache_file_3d18a74e668c437.pkl<br>  lightcurve_Geminga      12193571  2020-12-17 15:50     cache_file_5f8c1fe2233119ff.pkl<br>  photons_3C 279           3659049  2020-12-17 15:50     cache_file_005a8b245230afe.pkl<br>  exposure_3C 279         78040992  2020-12-17 15:51     cache_file_86f97125c87ecd8.pkl<br>  lightcurve_3C 279        4687729  2020-12-17 15:51     cache_file_509522c898fe52.pkl<br>  photons_Geminga         22334705  2020-12-18 06:39     cache_file_52b89da960a98f6.pkl<br>  cells_Geminga            1500794  2020-12-18 08:48     cache_file_6f2eb7e7fa4947f8.pkl<br>  lightfcurve_Geminga     12193634  2020-12-18 09:06     cache_file_f721860d03c0aa7.pkl<br>  cells_3C 279              557725  2020-12-18 09:06     cache_file_3e45b0fd33e29f7.pkl<br>  lightfcurve_3C 279       4687739  2020-12-18 09:06     cache_file_446256afd621452.pkl<br>  binned_exposure_Geminga       64448  2020-12-19 10:39     cache_file_517bbf0830c3a4c3.pkl<br></pre></p> </details>




## The light curve

The light curve can be represented by plots of flux vs. time. The time range,
limited by 'config.mjd_range`, if set. The actual livetime, during which *Fermi* is
collecting data, is further limited by the GTI, for good-time interval. This is a list
of start,stop pairs.

The module [gti](/light_curves/lgti.html) defines `get_gti`.

During the valid times, a the flux, or rate, is estimated by counting the number 
of photons and dividing by the exposure.

The source is defined by instantiating a [PointSource(/light_curves/config#PointSource) object, defined in 


### Exposure

The exposure for the specified source is calculated from the  [exposure](/light_curves/exposure.html) module,
which implements `get_exposure`. It depends on:

- Space craft info (FT2)
The FT2 file(s) contain spacecraft position and orientation as a function of time.

- Efffective Area
The module [effective_area](light_curves/effective_area.html) defines the functor class
`EffectiveArea`, needed to calculate the exposure


### Photon data

### Weights

Each photon 

### Cells

A "cell" represents a time interval to measure the flux.

This is where the ...


