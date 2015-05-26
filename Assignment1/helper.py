"""
Copyright: Copyright (C) 2015 Baruch College - Interest Rate Model
Description: Helper functions for main file
Author: Weiyi Chen, Wei Liu, Xiaoyu Zhang
"""

# 3rd party imports

import pandas as pd
from datetime import datetime as dt
import time

def read_DataSheetCurve(s_type):
    ''' handy function to read given excel '''
    s_filename = 'DataSheetCurve.xls'
    s_sheetname = '3M LIBOR  OIS'
    if s_type == 'LIBOR':
        return pd.read_excel(s_filename, s_sheetname, skiprows=1,  parse_cols='B:E')[:2]
    elif s_type == 'ED Futures':
        return pd.read_excel(s_filename, s_sheetname, skiprows=5,  parse_cols='B:F')[:8]
    elif s_type == 'Swap Rates':
        return pd.read_excel(s_filename, s_sheetname, skiprows=15, parse_cols='B:E')[:11]
    elif s_type == 'Fed Funds':
        return pd.read_excel(s_filename, s_sheetname, skiprows=28, parse_cols='B:E')[:1]
    elif s_type == 'Basis Swap Rates':
        return pd.read_excel(s_filename, s_sheetname, skiprows=32, parse_cols='B:E')[:16]
    else:
        raise TypeError('The paramter s_type can only be: LIBOR, ED Futures, Swap Rates, Fed Funds or Basis Swap Rates')

def toYearFraction(date):
    ''' convert datetime object to fractional year '''
    def sinceEpoch(date): # returns seconds since epoch
        return time.mktime(date.timetuple())
    s = sinceEpoch

    year = date.year
    startOfThisYear = dt(year=year, month=1, day=1)
    startOfNextYear = dt(year=year+1, month=1, day=1)

    yearElapsed = s(date) - s(startOfThisYear)
    yearDuration = s(startOfNextYear) - s(startOfThisYear)
    fraction = yearElapsed/yearDuration

    return date.year + fraction