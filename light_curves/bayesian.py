# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/14_bayesian.ipynb (unless otherwise specified).

__all__ = ['CountFitness', 'LikelihoodFitness', 'get_bb_partition']

# Cell
import os
import numpy as np
import pandas as pd
from astropy.stats.bayesian_blocks import FitnessFunc
from .lightcurve import get_lightcurve, flux_plot


# Cell
class CountFitness(FitnessFunc):
    """
    Adapted version of a astropy.stats.bayesian_blocks.FitnessFunc
    Considerably modified to give the `fitness function` access to the cell data.
    Implements the Event model using exposure instead of time.

    """

    def __init__(self, lc, p0=0.05,):
        """lc  : a LightCurve data table, with  exposure (e) and counts (n),
            as well as a representation of the likelihood for each cell
        """
        self.p0=p0
        self.df= df= lc
        N = self.N = len(df)
        # Invoke empirical function from Scargle 2012
        self.ncp_prior = self.p0_prior(N)

        #actual times for bin edges
        t = df.t.values
        dt = df.tw.values/2
        self.mjd = np.concatenate([t-dt, [t[-1]+dt[-1]] ] ) # put one at the end
        self.name = self.__class__.__name__
        self.setup()

    def setup(self):
        df = self.df

        # counts per cell
        self.nn = df.n.values
        assert min(self.nn)>0, 'Attempt to Include a cell with no contents'

        # edges and block_length use exposure as "time"
        e = df.e.values
        self.edges = np.concatenate([[0], np.cumsum(e)])
        self.block_length = self.edges[-1] - self.edges

    def __str__(self):

        return f'{self.name}: {self.N} cells, spanning {self.block_length[0]:.1f} days, prior={self.ncp_prior:.1f}'

    def __call__(self, R):
        """ The fitness function needed for BB algorithm
        For cells 0..R return array of length R+1 of the maximum log likelihoods for combined cells
        0..R, 1..R, ... R
        """
        # exposures and corresponding counts
        w_k = self.block_length[:R + 1] - self.block_length[R + 1]
        N_k = np.cumsum(self.nn[:R + 1][::-1])[::-1]

        # Solving eq. 26 from Scargle 2012 for maximum $\lambda$ gives
        return N_k * (np.log(N_k) - np.log(w_k))

    def fit(self):
        """Fit the Bayesian Blocks model given the specified fitness function.
        Refactored version using code from bayesian_blocks.FitnesFunc.fit
        Returns
        -------
        edges : ndarray
            array containing the (M+1) edges, in MJD units, defining the M optimal bins
        """
        # This is the basic Scargle algoritm, copied almost verbatum
        # ---------------------------------------------------------------

        # arrays to store the best configuration
        N = self.N
        best = np.zeros(N, dtype=float)
        last = np.zeros(N, dtype=int)

        # ----------------------------------------------------------------
        # Start with first data cell; add one cell at each iteration
        # ----------------------------------------------------------------
        for R in range(N):

            # evaluate fitness function
            fit_vec = self(R)

            A_R = fit_vec - self.ncp_prior
            A_R[1:] += best[:R]

            i_max = np.argmax(A_R)
            last[R] = i_max
            best[R] = A_R[i_max]

        # ----------------------------------------------------------------
        # Now find changepoints by iteratively peeling off the last block
        # ----------------------------------------------------------------
        change_points = np.zeros(N, dtype=int)
        i_cp = N
        ind = N
        while True:
            i_cp -= 1
            change_points[i_cp] = ind
            if ind == 0:
                break
            ind = last[ind - 1]
        change_points = change_points[i_cp:]

        return self.mjd[change_points]

# Cell
class LikelihoodFitness(CountFitness):
    """ Fitness function that uses the full likelihood
    """

    def __init__(self, lc,  p0=0.05, npt=25):
        self.npt = npt
        super().__init__(lc, p0)

    def setup(self):
        df = self.df
        N = self.N

        def liketable(prep):
            return prep.create_table(self.npt)

        self.tables = df.fit.apply(liketable).values

    def __str__(self):
        return f'{self.__class__.__name__}: {self.N} cells,  prior={self.ncp_prior:.1f}'

    def __call__(self, R):

        a, y  = self.tables[R]
        x = np.linspace(*a)
        y = np.zeros(self.npt)
        rv = np.empty(R+1)
        for i in range(R, -1, -1):
            a, yi = self.tables[i]
            xi = np.linspace(*a)
            y += np.interp(x, xi, yi, left=-np.inf, right=-np.inf)
            amax = np.argmax(y)
            rv[i] =y[amax]
        return rv

# Cell
def get_bb_partition(config, lc, fitness_class=CountFitness, p0=0.05):

    """Perform Bayesian Block partition of the cells found in a light curve

    - lc : input light curve
    - fitness_func :

    return edges for partition
    """
    cells = lc
    assert 'fit' in cells.columns, 'Expect the dataframe ho have the Poisson representation'
    assert issubclass(fitness_class,CountFitness), 'fitness_class wrong'
    # Now run the astropy Bayesian Blocks code using my version of the 'event' model
    fitness = fitness_class(lc, p0=p0)
    edges = fitness.fit()

    if config.verbose>0:
        print(f'Partitioned {fitness.N} cells into {len(edges)-1} blocks, with prior {fitness.ncp_prior:.1f}'\
              f' using {fitness.__class__.__name__} ' )
    return edges