"""
Copyright: Copyright (C) 2015 Baruch College - Interest Rate Model
Description: B-splines library
Author: Weiyi Chen, Wei Liu, Xiaoyu Zhang
"""

# Python imports

from numpy import *
from scipy.interpolate import splrep, splev, splint
from matplotlib.pyplot import plot, show

def test_splrep():
    """
    Find the B-spline representation of 1-D curve.
    Given the set of data points ``(x[i], y[i])`` determine a smooth spline
    approximation of degree k on the interval ``xb <= x <= xe``.
    Parameters
    ----------
    x, y : array_like
        The data points defining a curve y = f(x).
    w : array_like
        Strictly positive rank-1 array of weights the same length as x and y.
        The weights are used in computing the weighted least-squares spline
        fit. If the errors in the y values have standard-deviation given by the
        vector d, then w should be 1/d. Default is ones(len(x)).
    xb, xe : float
        The interval to fit.  If None, these default to x[0] and x[-1]
        respectively.
    k : int
        The order of the spline fit. It is recommended to use cubic splines.
        Even order splines should be avoided especially with small s values.
        1 <= k <= 5
    task : {1, 0, -1}
        If task==0 find t and c for a given smoothing factor, s.
        If task==1 find t and c for another value of the smoothing factor, s.
        There must have been a previous call with task=0 or task=1 for the same
        set of data (t will be stored an used internally)
        If task=-1 find the weighted least square spline for a given set of
        knots, t. These should be interior knots as knots on the ends will be
        added automatically.
    s : float
        A smoothing condition. The amount of smoothness is determined by
        satisfying the conditions: sum((w * (y - g))**2,axis=0) <= s where g(x)
        is the smoothed interpolation of (x,y). The user can use s to control
        the tradeoff between closeness and smoothness of fit. Larger s means
        more smoothing while smaller values of s indicate less smoothing.
        Recommended values of s depend on the weights, w. If the weights
        represent the inverse of the standard-deviation of y, then a good s
        value should be found in the range (m-sqrt(2*m),m+sqrt(2*m)) where m is
        the number of datapoints in x, y, and w. default : s=m-sqrt(2*m) if
        weights are supplied. s = 0. (interpolating) if no weights are
        supplied.
    t : array_like
        The knots needed for task=-1. If given then task is automatically set
        to -1.
    full_output : bool
        If non-zero, then return optional outputs.
    per : bool
        If non-zero, data points are considered periodic with period x[m-1] -
        x[0] and a smooth periodic spline approximation is returned. Values of
        y[m-1] and w[m-1] are not used.
    quiet : bool
        Non-zero to suppress messages.
        This parameter is deprecated; use standard Python warning filters
        instead.
    Returns
    -------
    tck : tuple
        (t,c,k) a tuple containing the vector of knots, the B-spline
        coefficients, and the degree of the spline.
    fp : array, optional
        The weighted sum of squared residuals of the spline approximation.
    ier : int, optional
        An integer flag about splrep success. Success is indicated if ier<=0.
        If ier in [1,2,3] an error occurred but was not raised. Otherwise an
        error is raised.
    msg : str, optional
        A message corresponding to the integer flag, ier.

    """
    x = linspace(0,10,10)
    y = sin(x)
    tck = splrep(x, y)
    print tck


def test_splev():
    """
    Evaluate a B-spline or its derivatives.
    Given the knots and coefficients of a B-spline representation, evaluate
    the value of the smoothing polynomial and its derivatives.  This is a
    wrapper around the FORTRAN routines splev and splder of FITPACK.
    Parameters
    ----------
    x : array_like
        An array of points at which to return the value of the smoothed
        spline or its derivatives.  If `tck` was returned from `splprep`,
        then the parameter values, u should be given.
    tck : tuple
        A sequence of length 3 returned by `splrep` or `splprep` containing
        the knots, coefficients, and degree of the spline.
    der : int
        The order of derivative of the spline to compute (must be less than
        or equal to k).
    ext : int
        Controls the value returned for elements of ``x`` not in the
        interval defined by the knot sequence.
        * if ext=0, return the extrapolated value.
        * if ext=1, return 0
        * if ext=2, raise a ValueError
        * if ext=3, return the boundary value.
        The default value is 0.
    Returns
    -------
    y : ndarray or list of ndarrays
        An array of values representing the spline function evaluated at
        the points in ``x``.  If `tck` was returned from `splprep`, then this
        is a list of arrays representing the curve in N-dimensional space.
    """
    x = linspace(0,10,10)
    y = cos(x)
    tck = splrep(x, y)
    x2 = linspace(0,10,10)
    y2 = splev(x2, tck)
    plot(x,y,'o',x2,y2)
    show()


def test_splint():
    """
    Evaluate the definite integral of a B-spline.
    Given the knots and coefficients of a B-spline, evaluate the definite
    integral of the smoothing polynomial between two given points.
    Parameters
    ----------
    a, b : float
        The end-points of the integration interval.
    tck : tuple
        A tuple (t,c,k) containing the vector of knots, the B-spline
        coefficients, and the degree of the spline (see `splev`).
    full_output : int, optional
        Non-zero to return optional output.
    Returns
    -------
    integral : float
        The resulting integral.
    wrk : ndarray
        An array containing the integrals of the normalized B-splines
        defined on the set of knots.
    """
    x = linspace(0,10,10)
    y = sin(x)
    tck = splrep(x, y)
    y2 = splint(x[0],x[-1],tck)
    print y2
        


class Spline(object):
    ''' B-spline class '''
    def __init__(self, ls_knots):
        '''
        @summary: B-spline constructor
        @param t: type of list, the vector of knots
        '''
        super(Spline, self).__init__()
        self.ls_knots       = ls_knots
        self.d_cache        = {}
        self.d_cache_gamma  = {}
        self.d_cache_crsint = {}


    def splrep(self, i_start, i_degree, f_time):
        '''
        @summary: B-spline functions
        @param i_start: start index
        @param i_degree: B-spline degree
        @param f_time: time 
        '''
        f_begin = self.ls_knots[i_start]
        f_end   = self.ls_knots[i_start+i_degree+1]
        if f_time < f_begin or f_time >= f_end:
            return 0.
        elif i_degree == 0:
            return 1.
        else:
            if (i_start, i_degree, f_time) in self.d_cache.keys():
                return self.d_cache[(i_start, i_degree, f_time)]
            else:
                if (i_start, i_degree, f_time) in self.d_cache.keys():
                    return self.d_cache[(i_start, i_degree, f_time)]
                else:
                    self.d_cache[(i_start ,i_degree ,f_time)] = (f_time-f_begin) / (self.ls_knots[i_start+i_degree]-f_begin) * self.splrep(i_start,   i_degree-1, f_time) \
                                                              + (f_end -f_time)  / (f_end-self.ls_knots[i_start+1])          * self.splrep(i_start+1, i_degree-1, f_time)
                    return self.d_cache[(i_start ,i_degree ,f_time)]


    def splint(self, i_start, i_degree, f_time):
        '''
        @summary: B-spline integration
        @param i_start: start index
        @param i_degree: B-spline degree
        @param f_time: time 
        '''
        f_begin = self.ls_knots[i_start]
        f_end   = self.ls_knots[i_start+i_degree+1]
        if f_time < f_begin:
            return 0.
        elif f_time >= f_end:
            return (f_end-f_begin) / (i_degree+1)
        else:
            f_sum = 0.
            while self.ls_knots[i_start] < f_time:
                f_sum += (f_end - f_begin) / (i_degree + 1) * self.splrep(i_start, i_degree + 1, f_time)
                i_start += 1
            return f_sum


    def splder(self, i_start, i_degree, f_time, order):
        '''
        summary: B-spline derivative
        @param i_start: start index
        @param i_degree: B-spline degree
        @param f_time: time 
        @param i_order: highest order
        '''
        f_begin = self.ls_knots[i_start]
        f_end   = self.ls_knots[i_start+i_degree+1]
        if order == 0:
            return self.splrep(i_start, i_degree, f_time)
        elif order == 1 and i_degree < 1.:
                return 0.
        else:
            return i_degree / ( self.ls_knots[i_start+i_degree]-f_begin) * self.splder(i_start,   i_degree-1, f_time, order-1) \
                 + i_degree / (-self.ls_knots[i_start+1]       +f_end  ) * self.splder(i_start+1, i_degree-1, f_time, order-1)


    def splgamma(self, i_start, f_start, f_end):
        ''' B-spline gamma '''
        if (i_start, f_start, f_end) in self.d_cache_gamma.keys():
            pass
        else:
            self.d_cache_gamma[(i_start, f_start, f_end)] = self.splint(i_start,3,f_end) - self.splint(i_start,3,f_start)
        return self.d_cache_gamma[(i_start, f_start, f_end)]


    def splcrsint(self, i_start, i_start2, f_start, f_end):
        ''' B-spline cross integration, as of \int_a^b B^{''}_k*B^{''}_l dt '''
        if (i_start, i_start2, f_start, f_end) in self.d_cache_crsint.keys():
            pass
        else:
            f_term1 = self.splder(i_start, 3, f_end  , 1) * self.splder(i_start2, 3, f_end,   2)
            f_term2 = self.splder(i_start, 3, f_start, 1) * self.splder(i_start2, 3, f_start, 2)
            ls_windows = [f_start] + [f_time for t_time in self.ls_knots if f_start < f_time < f_end] + [f_end]
            f_term3 = sum(self.splder(f_start2, 3, ls_windows[j-1], 3) * (self.splrep(i_start, 3, ls_windows[j])- self.splrep(i_start, 3, ls_windows[j-1])) for j in range(1, len(ls_windows)+2))
            self.d_cache_crsint[(i_start, i_start2, f_start, f_end)] = f_term1 - f_term2 - f_term3
        return self.d_cache_crsint[(i_start, i_start2, f_start, f_end)]


def main():
	test_splrep()
	test_splev()
	test_splint()


if __name__ == '__main__':
	main()
