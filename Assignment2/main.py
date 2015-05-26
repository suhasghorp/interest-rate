"""
Copyright: Copyright (C) 2015 Baruch College - Interest Rate Model
Description: Main file to test
Author: Weiyi Chen, Wei Liu, Xiaoyu Zhang
"""

# local imports
from libor_market import Libor_Market
from swaps import Knock_Out_Swap

# 3rd party imports
import csv
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
        
def read_libor():
    ''' read Libor forward value from Assignment 1 as of b_spline '''
    return pd.read_csv('libor_rates_data.csv')['Libor Rate'].values[:80]


def calc_swapRate():
    ''' calculate swap rate via Monte Carlo '''
    ls_liborInit = read_libor()

    kos = Knock_Out_Swap(ls_liborInit, i_MC=2000, b_frozenCurve=True)
    print 'Use 2,000 simulated paths to carry out the calculation (the exact calculation) - '
    print 'The break-even rate on the fixed leg of the swap: \t', kos.swap_rate(), '\n'

    kos = Knock_Out_Swap(ls_liborInit, i_MC=2000, b_frozenCurve=False)
    print 'Use 2,000 simulated paths to carry out the calculation (the frozen curve approximation) - '
    print 'The break-even rate on the fixed leg of the swap: \t', kos.swap_rate(), '\n'

    kos = Knock_Out_Swap(ls_liborInit, i_MC=5000, b_frozenCurve=False) 
    print 'Compare against a run with 5,000 simulated paths - '
    print 'The break-even rate on the fixed leg of the swap: \t', kos.swap_rate(), '\n'


def analyze_plot():
    ''' plot Libor forward simulation path, acknowledge to Haotian's suggestion '''
    ls_liborInit = read_libor()
    ls_liborMarket_curves = []

    for i in range(0,20):
        libor_market = Libor_Market(ls_liborInit,80)
        libor_market.simulate()
        ls_liborMarket_curves.append(np.asarray(libor_market.ls[4][:-4]))
  
    for i in range(0,10):
        plt.plot(np.linspace(1, 20, 19*4+1)[:-1], ls_liborMarket_curves[i])

    plt.xlabel("Time (Year)")
    plt.ylabel("Libor Forward Rate (%)");
    plt.title("Libor Forward Simulation Path")
    plt.savefig('analyze.pdf')
    plt.show()
    


def main():
    calc_swapRate()
    #analyze_plot()
    

if __name__ == '__main__':
    main()
