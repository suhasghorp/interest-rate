"""
Copyright: Copyright (C) 2015 Baruch College - Interest Rate Model
Description: Libor Market Model Class
Author: Weiyi Chen, Wei Liu, Xiaoyu Zhang
"""

# python imports
import math

# 3rd party imports
import numpy as np


class Libor_Market(object):
    ''' Class Libor_Market to do Monte Carlo, 1 Brownian Motion '''

    def __init__(self, ls_init, i_N, b_frozenCurve=False):
        '''
        @summary: constructor to do initialization
        @param ls_init: list of init value 
        @param i_N: size of matrix column
        @param b_frozenCurve: whether to use frozen curve
        '''
        super(Libor_Market, self).__init__()

        self.f_t = 1.0/4.0
        self.f_sigma = 0.0085
        self.i_M = len(ls_init)
        self.i_N = i_N
        self.ls_init = ls_init
        self.b_frozenCurve = b_frozenCurve
        self.ls = np.zeros((self.i_M, self.i_N))
        
    def simulate(self):
        ''' 
        @summary: simulate of the matrix value 
        @return: None, just to update self.ls
        '''
        
        # initialize
        self.ls[0] = self.ls_init
        
        # simulate
        for i in range(1,self.i_N):  
            d_brownianMotion = math.sqrt(self.f_t) * np.random.standard_normal()
            for j in range(0,self.i_M):
                j = self.i_M - j - 1 
                if j < (self.i_M-i):
                    f_currLiborRate = self.delta(i,j) * self.f_t + self.f_sigma * d_brownianMotion
                    self.ls[i][j] = max(self.ls[i-1][j+1] + f_currLiborRate,0.0)
    
    def delta(self, i, j):
        '''
        @summary: calculate delta by using terminal forward measure
        @param i: i-th row in the matrix
        @param j: j-th column in the matrix
        @return: delta value of float type
        '''
        if j == (self.i_M-1):
            return 0.
        else:
            result = 0
            for n in range(j+1, self.i_M-i):
                if self.b_frozenCurve==False:
                    result -= self.f_t * self.f_sigma / (1+self.f_t*self.ls[i][n])
                else:
                    result -= self.f_t * self.f_sigma / (1+self.f_t*self.ls[0][n+i])
            return result * self.f_sigma