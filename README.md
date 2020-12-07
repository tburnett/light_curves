# The `light_curve` package
> Code for generating fermi-LAT light curves


## Install

After cloning this repository:

`pip install -e .`


## How to use (If you have set up files)
 
Make a DataFrame of cells

```python
from light_curves.config import LCconfig, FileConfiguration, PointSource
from light_curves.cells import get_cells
config = LCconfig()
files = FileConfiguration()
if files.valid:
    cells = get_cells(config, files, PointSource('Geminga'))

    cells.head()
else:
    cells = None                 
```

    Processing 11 GTI files ...  11 files, 63635 intervals with 3,322 days live time
    	GTI MJD range: 54682.66-58698.08, good fraction 0.83 
    Loading  132 months from Arrow dataset /home/burnett/data/dataset
    ....................................................................................................................................
    	Selected 1313726 photons within 5 deg of  (195.13,4.27)
    	Energies: 100.0-1000000 MeV
    	Dates:    2008-08-04 15:46 - 2019-08-03 01:17
    	MJD  :    54682.7          - 58698.1         
    Load weights from file /mnt/c/users/thbur/OneDrive/fermi/weight_files/Geminga_weights.pkl
    	Found: PSR J0633+1746 at (195.14, 4.27)
    	Applyng weights: 240 / 1313726 photon pixels are outside weight region
    	233109 weights set to NaN
    Processing 11 GTI files ...  11 files, 63635 intervals with 3,322 days live time
    	GTI MJD range: 54682.66-58698.08, good fraction 0.83 
    Processing 12 S/C history (FT2) files
      applying cuts cos(theta) < 0.4,  z < 100
    	file /home/burnett/work/lat-data/ft2/ft2_2008.fits: 362996 entries, 360944 in GTI
    	file /home/burnett/work/lat-data/ft2/ft2_2009.fits: 874661 entries, 870446 in GTI
    	file /home/burnett/work/lat-data/ft2/ft2_2010.fits: 889547 entries, 884697 in GTI
    	file /home/burnett/work/lat-data/ft2/ft2_2011.fits: 882832 entries, 871672 in GTI
    	file /home/burnett/work/lat-data/ft2/ft2_2012.fits: 881317 entries, 868109 in GTI
    	file /home/burnett/work/lat-data/ft2/ft2_2013.fits: 885307 entries, 867342 in GTI
    	file /home/burnett/work/lat-data/ft2/ft2_2014.fits: 894730 entries, 886570 in GTI
    	file /home/burnett/work/lat-data/ft2/ft2_2015.fits: 890006 entries, 886086 in GTI
    	file /home/burnett/work/lat-data/ft2/ft2_2016.fits: 890933 entries, 884823 in GTI
    	file /home/burnett/work/lat-data/ft2/ft2_2017.fits: 888349 entries, 883761 in GTI
    	file /home/burnett/work/lat-data/ft2/ft2_2018.fits: 842824 entries, 830723 in GTI
    	file /home/burnett/work/lat-data/ft2/ft2_2019.fits: 737029 entries, 514657 in GTI
    	Found 9,609,830 S/C entries:  2,695,715 remain after zenith and theta cuts
    Calculate exposure using the energy domain 100.0-1000000.0 4 bins/decade
    Time bins: 4015 intervals of 1 days, in range (54683.0, 58698.0)


A look at the content of the first cell

```python
cells.iloc[0]
```




    t                                                 54683.5
    tw                                                      1
    fexp                                              1.26439
    n                                                     330
    w       [244, 214, 174, 5, 246, 150, 187, 65, 91, 215,...
    S                                                  905751
    B                                                  460568
    Name: 54683.5, dtype: object



wher the fields are: 
- t : MJD central time
- tw : width
- fexp : exposure for this interval compared to mean
- n : Number of photons detected
- w : List of int(weight*256) for the photons detected during the interval. stored as uint8
- S, B : expected signal and background
