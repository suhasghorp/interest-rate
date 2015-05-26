"""
Copyright: Copyright (C) 2015 Baruch College - Interest Rate Model
Description: Swap rates
Author: Weiyi Chen, Wei Liu, Xiaoyu Zhang
"""

class Swap(object):
    ''' Swap object '''
    def __init__(self, f_notional, f_maturity, f_payments):
        '''
        @summary: constructor
        @param f_notional: Notional
        @param f_maturity: Maturity
        @param f_payments: payments per year 
        '''
        super(Swap, self).__init__()
        self.f_notional = f_notional
        self.f_maturity = f_maturity
        self.f_payments = f_payments 


    def SwapRates(self, f_time, ois, libor, spl):
        """ 
        @summary: calculate par swap rate, S_0(T_0,T), 
        @param f_time: settlement 
        @param ois: OIS object 
        @param libor: LIBOR object
        @param spl: Spline object
        """
        # fixed leg
        f_AV       = 0.
        f_maturity = self.f_maturity
        while f_maturity > 0:
            f_AV       += 1.0 / self.f_maturity * ois.disc_factor(f_time, f_maturity, spl)
            f_maturity -= 1.0 / self.f_maturity

        # floating leg
        f_PV = 0 
        f_maturity = self.f_maturity #Work payment dates back from maturity
        while f_maturity > 0:
            f_PV += 0.25 * libor.forwards(f_maturity-0.25,f_maturity,spl)*ois.disc_factor(f_time,f_maturity,spl)
            f_maturity -= .25 #quarterly in US

        return f_PV / f_AV


    def PV(self, f_time, ois, libor, spl, f_coupon): #Make sure to include coupon rate (fixed payer's rate)
        """
        @summary: calculate swap value
        @param f_time: settlement 
        @param ois: OIS object 
        @param libor: LIBOR object
        @param spl: Spline object
        @param f_coupon: coupon rate
        """
        # PV of fixed leg
        f_AV = 0  
        f_maturity = self.f_maturity
        while f_maturity > 0:
            f_AV       += 1.0 / self.f_maturity * ois.disc_factor(f_time, f_maturity, spl)
            f_maturity -= 1.0 / self.f_maturity
        f_AV *= f_coupon 

        # PV of floating leg 
        f_PV = 0.
        f_maturity = self.f_maturity 
        while f_maturity > 0:
            f_PV += .25 *libor.forwards(f_maturity-0.25,f_maturity,spl)*ois.disc_factor(f_time,f_maturity,spl)
            f_maturity -= .25 

        return self.f_notional * (f_AV - f_PV)


class BasisSwap(Swap):
    """ Basis Swap Object derived from Swap """
    def __init__(self, f_maturity, f_payments):
        '''
        @summary: constructor
        @param f_notional: Notional
        @param f_maturity: Maturity
        @param f_payments: payments per year 
        '''
        super(BasisSwap, self).__init__(1.0, f_maturity, f_payments)
    
    def SwapRates(self, f_time, ois, libor, spl):
        """ 
        @summary: calculate par swap rate, S_0(T_0,T), 
        @param f_time: settlement 
        @param ois: OIS object 
        @param libor: LIBOR object
        @param spl: Spline object
        """

        f_AV = 0.
        f_maturity = self.f_maturity
        while f_maturity > 0:
            f_AV += 1.0 / self.f_maturity *(libor.forwards(f_maturity - 1.0/self.f_maturity, f_maturity, spl)-ois.forwards(f_maturity - 1.0/self.f_maturity, f_maturity,spl))*ois.disc_factor(f_time, f_maturity, spl)
            f_maturity -= 1.0/self.f_maturity
        
        f_PV = 0.
        f_maturity = self.f_maturity
        while f_maturity > 0:
            f_PV += 1.0 / self.f_maturity * ois.disc_factor(f_time, f_maturity, spl)
            f_maturity -= 1.0 / self.f_maturity
        
        return f_AV / f_PV 

    def PV(self, f_time, ois, libor, spl, f_basis, f_notional):
        """
        @summary: calculate swap value
        @param f_time: settlement 
        @param ois: OIS object 
        @param libor: LIBOR object
        @param spl: Spline object
        @param f_basis: basis point
        """
        f_PV = 0
        f_maturity = self.f_maturity
        while f_maturity > 0: 
            P_0 = ois.disc_factor(f_time, f_maturity, spl)
            L_j = libor.forwards(f_maturity - 1.0/self.f_maturity, f_maturity, spl)
            F_j = ((1./ P_0)-1.) / (1.0/ self.f_maturity)
            f_PV += (1.0/self.f_maturity)*P_0*(L_j-F_j-f_basis) 
            f_maturity -= 1.0/self.f_maturity
        return f_notional * f_PV
