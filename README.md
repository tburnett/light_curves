# The `light_curve` package
> Code for generating fermi-LAT light curves. <a href='https://tburnett.github.io/light_curves/'>link to this document</a>


## Background

This package has code that is being adapted to the [nbdev](https://nbdev.fast.ai/) environment from [github package lat-timing](https://github.com/tburnett/lat-timing) to manage light curves of Fermi-LAT sources.  

As pointed out there, it is based on a [paper](https://arxiv.org/pdf/1910.00140.pdf) by Matthew Kerr, 

And at the same time, I've ported some code from  my [jupydoc](https://github.com/tburnett/jupydoc) documention package to allow enhanced documentation combining Markdown and code. This is demonstrated below.

## Installation
After cloning, in its folder run the command
`pip install -e .`

## Instructions on set up / use

`instructions`

## Demonstrate some actual light curves
 
 
<details class="description">
    <summary>Code details ...</summary>
    
```python
#collapse_hide

def plot_demo():
    """
    ### Light curve plots
    
    {print_out}
    
    <br>
    Test with {source1.name}:
    
    {fig1}
    
    This is to be compared with Kerr's Figure 1:
    
    {kerr_fig1}
    
    This flaring AGN, {source2.name} was used in the Kerr paper as well.
    
    {fig2}
    
 
    """
    from light_curves.config import Config, Files, PointSource
    from light_curves.lightcurve import get_lightcurve, flux_plot
    
    config = Config()
    files = Files()
    assert files.valid
    #files.clear_cache()
    
    kerr_fig1 = image('kerr_fig1.png', width=300)
    
    with capture_print(summary='printout from this analysis') as print_out:
        source1 = PointSource('Geminga')
        lc1 = get_lightcurve(config, files, source1)
        fig1 = flux_plot(config, lc1, fignum=1, title=source1.name)
        fig1.caption=f'{source1.name}'
        fig1.width=500

        source2 = PointSource('3C 279')
        lc2 = get_lightcurve(config, files, source2)
        fig2 = flux_plot(config, lc2, fignum=2, yscale='log' )
        fig2.caption=f'{source2.name}'
        fig2.width=500


from light_curves.config import Files
if Files().valid:
    nbdoc(plot_demo)
```

</details>


### Light curve plots

<details class="descripton" ><summary data-open="Hide " data-close="Show "> printout from this analysis </summary> <p style="margin-left: 5%"><pre>Restoring the light curve from /tmp/light_curves/Geminga_lightcurve.pkl <br>Restoring the light curve from /tmp/light_curves/3C_279_lightcurve.pkl <br></pre></p> </details>

<br>
Test with Geminga:

<div class="jupydoc_fig"><a href="images/plot_demo_fig_01.png"<figure>   <img src="images/plot_demo_fig_01.png" alt="Figure 1 at images/plot_demo_fig_01.png" width=500>  <figcaption><b>Figure 1</b>. Geminga</figcaption></figure></a></div>


This is to be compared with Kerr's Figure 1:

<div class="jupydoc_fig"> <a href="images/kerr_fig1.png">  <figure>    <img src="images/kerr_fig1.png"  width=300       alt="Image kerr_fig1.png at images/kerr_fig1.png">
  <figcaption></figcaption></figure></a></div>


This flaring AGN, 3C 279 was used in the Kerr paper as well.

<div class="jupydoc_fig"><a href="images/plot_demo_fig_02.png"<figure>   <img src="images/plot_demo_fig_02.png" alt="Figure 2 at images/plot_demo_fig_02.png" width=500>  <figcaption><b>Figure 2</b>. 3C 279</figcaption></figure></a></div>



