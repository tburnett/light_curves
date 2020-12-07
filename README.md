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

cells = get_cells(LCconfig(), FileConfiguration(), PointSource('Geminga'))

cells.head()
                  
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





<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>t</th>
      <th>tw</th>
      <th>fexp</th>
      <th>n</th>
      <th>w</th>
      <th>S</th>
      <th>B</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>54683.5</th>
      <td>54683.5</td>
      <td>1.0</td>
      <td>1.264387</td>
      <td>330</td>
      <td>[244, 214, 174, 5, 246, 150, 187, 65, 91, 215,...</td>
      <td>9.057506e+05</td>
      <td>460567.995839</td>
    </tr>
    <tr>
      <th>54684.5</th>
      <td>54684.5</td>
      <td>1.0</td>
      <td>1.215870</td>
      <td>348</td>
      <td>[245, 217, 219, 244, 240, 235, 232, 235, 54, 2...</td>
      <td>8.709950e+05</td>
      <td>442895.014603</td>
    </tr>
    <tr>
      <th>54685.5</th>
      <td>54685.5</td>
      <td>1.0</td>
      <td>1.182915</td>
      <td>338</td>
      <td>[138, 13, 107, 13, 195, 219, 247, 148, 245, 5,...</td>
      <td>8.473877e+05</td>
      <td>430890.876652</td>
    </tr>
    <tr>
      <th>54686.5</th>
      <td>54686.5</td>
      <td>1.0</td>
      <td>1.407341</td>
      <td>378</td>
      <td>[216, 237, 235, 245, 235, 218, 51, 232, 153, 0...</td>
      <td>1.008157e+06</td>
      <td>512640.693290</td>
    </tr>
    <tr>
      <th>54687.5</th>
      <td>54687.5</td>
      <td>1.0</td>
      <td>1.299117</td>
      <td>341</td>
      <td>[246, 185, 82, 163, 240, 182, 31, 200, 200, 14...</td>
      <td>9.306291e+05</td>
      <td>473218.512548</td>
    </tr>
  </tbody>
</table>
</div>


