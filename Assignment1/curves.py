"""
Copyright: Copyright (C) 2015 Baruch College - Interest Rate Model
Description: OIS and LIBOR curves
Author: Weiyi Chen, Wei Liu, Xiaoyu Zhang
"""

# python imports

import math

# local imports

from splines import Spline

class Curve(object):
    ''' Base Class for OIS and LIBOR '''
    def __init__(self, ls_knots, ls_coefs):
        '''
        @summary: constructor
        @param ls_knots: a list of knots, i.e. time points
        @param ls_coefs: a list of coefficients for B-spline
        '''
        super(Curve, self).__init__()
        self.ls_knots = ls_knots
        self.ls_coefs = ls_coefs

    def r(self, f_time, spl):
        '''
        @summary: compute the instantaneous rate
        @param f_time: time point 
        @param spl: spline object to access function
        '''
        return sum([self.ls_coefs[i]*spl.splrep(i,3,f_time) for i in range(0, len(self.ls_coefs)-4)])

    def disc_factor(self, f_start, f_end, spl):
        ''' computes the discount factor between any two dates '''
        return math.exp(-sum([self.ls_coefs[i]*spl.splgamma(i,f_start,f_end) for i in range(0, len(self.ls_coefs)-4)]))

    def forwards(self, f_start, f_end, spl):
        ''' computes the forward rates between any two dates '''
        return (math.exp(sum([self.ls_coefs[i] * spl.splgamma(i,f_start,f_end) for i in range(0, len(self.ls_coefs)-4)])) - 1.0) / (f_end-f_start)


class OIS(Curve):
    ''' OIS Curve '''
    def __init__(self, ls_knots, ls_coefs):
        ''' constructor '''
        super(OIS, self).__init__(ls_knots, ls_coefs)


class LIBOR(Curve):
    ''' LIBOR Curve '''
    def __init__(self, ls_knots, ls_coefs):
        super(LIBOR, self).__init__(ls_knots, ls_coefs)
