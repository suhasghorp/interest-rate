"""
Copyright: Copyright (C) 2015 Baruch College - Interest Rate Model
Description: Main function to run
Author: Weiyi Chen, Wei Liu, Xiaoyu Zhang
"""

# local imports

from curves import OIS, LIBOR
from swaps import Swap, BasisSwap
from splines import Spline
from helper import *

# 3rd party imports

import numpy as np
import pandas as pd
import xlrd
import scipy.optimize as opt
import matplotlib.pyplot as plot


def main():

    # read excel rate data

    df              = read_DataSheetCurve('ED Futures')
    ED_Future_Rate  = df['Rate']
    ED_Future_Date  = [0.] + [toYearFraction(curr_date) - toYearFraction(df['IMM date'][0]) for curr_date in df['IMM date'][1:]]

    df              = read_DataSheetCurve('Swap Rates')
    Swap_Rate       = df['Rate']
    Swap_Date       = [toYearFraction(end_date) - toYearFraction(start_date) for start_date, end_date in zip(df['Start Date'], df['End Date'])]

    df              = read_DataSheetCurve('Basis Swap Rates')
    Basis_Swap_Rate = df['Basis (bp)'] * 1e-4
    Basis_Swap_Date = [toYearFraction(end_date) - toYearFraction(start_date) for start_date, end_date in zip(df['Start Date'], df['End Date'])]

    # generate swap objects, initialization

    ls_swaps  = [Swap(0, Swap_Date[i], 2) for i in range(len(Swap_Date))]
    ls_bswaps = [BasisSwap(Basis_Swap_Date[i],4) for i in range(len(Basis_Swap_Date))]
    ls_knots  = [-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 15.0, 20.0, 25.0, 31.0, 32.0, 33.0, 34.0, 35.0]
    ls_init   = [0.01] * 36
    spline    = Spline(ls_knots)

    # optimization

    def goal(x):
        """ objective function """
        oiscoef = x[0:18]
        liborcoef = x[18:36]
        ois = OIS(ls_knots,oiscoef)
        libor = LIBOR(ls_knots,liborcoef)
        f_ret = sum([(ls_swaps[i].SwapRates(0,ois,libor,spline) - Swap_Rate[i]) ** 2 for i in range(11)]) \
              + sum([(ls_bswaps[i].SwapRates(0,ois,libor,spline) - Basis_Swap_Rate[i]) ** 2 for i in range(16)]) \
              + sum([((libor.forwards(ED_Future_Date[i],ED_Future_Date[i]+0.25,spline) - ED_Future_Rate[i]) ** 2) for i in range(8)])
        penalty = 0.000001 * sum([spline.crossIntegral(k,l,1,30) * (oiscoef[k]*oiscoef[l] + liborcoef[k]*liborcoef[l]) for k in range(4,10) for l in range(4,10)])
        return f_ret + penalty

    def min_bfgs(ls_init):
        res = opt.fmin_bfgs(goal, ls_init, gtol = 1e-6, epsilon = 1e-6)
        xopt = res
        Qmin = goal(xopt)
        return xopt

    print "Step 1: Optimization, please wait ... "
    xopt  = min_bfgs(ls_init)
    ois   = OIS(ls_knots,xopt[0:16])
    libor = LIBOR(ls_knots,xopt[18:36])
    ls_swapsPlot  = [Swap(0,t,2)    for t in range(1,31)]
    ls_bswapsPlot = [BasisSwap(t,4) for t in range(1,31)]

    print "Step 2: Calculating swap rates and basis swap rates ..."
    swapParRates      = [ls_swapsPlot[i].SwapRates(0,ois,libor,spline) for i in range(30)]
    basisSwapParRates = [ls_bswapsPlot[i].SwapRates(0,ois,libor,spline) for i in range(30)]
   
    print "Step 3: Calculating LIBOR ..."
    liborFwdRates = [libor.forwards(range(0.1,2.,0.1)[i],range(0.1,2.,0.1)[i]+0.25,spline) for i in range(19)]

    print "Step 4: Calculating Instantaneous rate..."
    instantLibor = [libor.r(range(0.01,30.,0.01)[i],spline) for i in range(2999)]
    instantOIS[i] = [ois.r(range(0.01,30.,0.01)[i],spline) for i in range(2999)]
    instantBasis[i] = [instantLibor[i]-instantOIS[i] for i in range(2999)]

    print "Step 5: Plotting curves"

    figure1 = plot.figure()

    # Swap Curve

    axis1 = figure1.add_subplot(411) 
    axis1.plot(np.asarray(Swap_Date),       100*np.asarray(Swap_Rate), 'r-')
    axis1.plot(np.asarray(range(30)),       100*np.asarray(swapParRates), 'b-')
    axis1.set_title("Par Swap Rate")

    # Basis Swap Curve

    axis2 = figure1.add_subplot(412) 
    axis2.plot(np.asarray(Basis_Swap_Date), 100*np.asarray(Basis_Swap_Rate), 'r-')
    axis2.plot(np.asarray(range(30)),       100*np.asarray(basisSwapParRates), 'b-')
    axis2.set_title("Basis Swap Rate")

    # Libor Curve

    axis3 = figure1.add_subplot(413) 
    axis3.plot(np.asarray(ED_Future_Date),    100*np.asarray(ED_Future_Rate), 'r-')
    axis3.plot(np.asarray(range(0.1,2.,0.1)), 100*np.asarray(liborFwdRates), 'b-')
    axis3.set_title("LIBOR Rates")
    
    # Instant Rate Curve

    axis4 = figure1.add_subplot(414) 
    axis4.plot(np.asarray(range(0.01,30.,0.01)), 100*np.asarray(instantLibor), 'r-')
    axis4.plot(np.asarray(range(0.01,30.,0.01)), 100*np.asarray(instantOIS), 'b-')
    axis4.plot(np.asarray(range(0.01,30.,0.01)), 100*np.asarray(instantBasis), 'y-')
    axis4.set_title("Instantaneous Rates")

    plot.show()



if __name__ == '__main__':
    main()



