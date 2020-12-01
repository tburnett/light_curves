import numpy as np
import pylab as plt

import pandas as pd
import os, sys

from lat_timing import Main
from utilities import keyword_options

# class GammaData(Main):
#     """wrapper around main 
#     """

#     defaults=Main.defaults+(
#         ('name', 'Geminga', ''),
#         ('radius', 7, 'ROI radius'),
#         ('weight_file', '/nfs/farm/g/glast/u/burnett/analysis/lat_timing/data/weight_files', 'weight file dir'),
#         ('source_name', 'Geminga', 'source name to use'), 
#         ('interval', 1, 'days'),
#         ('verbose', 0,  'verbosity'),

#     )
#     @keyword_options.decorate(defaults)
#     def __init__(self,  **kwargs):
#         keyword_options.process(self,kwargs)        
#         super().__init__( **kwargs)