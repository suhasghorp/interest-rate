"""
Copyright: Copyright (C) 2015 Baruch College - Interest Rate Model
Description: Swap rates
Author: Weiyi Chen, Wei Liu, Xiaoyu Zhang
"""

from libor_market import Libor_Market

class Swap(object):
    ''' Swap object '''
    def __init__(self, f_notional, f_maturity, f_payments):
        '''
        @summary: constructor
        @param f_notional: f_notional
        @param f_maturity: f_maturity
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
        @param f_notional: f_notional
        @param f_maturity: f_maturity
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


class Knock_Out_Swap(Swap):
    ''' Knock Out Swap object derived from Swap '''
    def __init__(self, ls_init, f_fixedRate=0.0218233230043, f_notional=100, f_maturity=10, i_MC=2000, f_barrier=0.0095, b_frozenCurve=False):
        '''
        @summary: Constructor
        @param ls_init: initial list of values for Libor Market Model
        @param f_fixedRate: fixed rate
        @param f_notional: swap notional
        @param f_maturity: swap maturity 
        @param i_MC: Monte Carlo Number
        @param f_barrier: knock out barrier 
        @param b_frozenCurve: whether to use frozen curve
        '''

        # swap paramters
        self.f_fixedRate = f_fixedRate
        self.f_maturity  = f_maturity
        self.f_notional  = f_notional

        # monte carlo paramters
        self.i_MC = i_MC

        # Knock out paramters
        self.f_barrier      = f_barrier
        self.f_kos_rate     = 0
        self.f_kos_value    = 0
        self.b_simulatePool = False
        self.Libor_Market   = Libor_Market(ls_init,int(2*self.f_maturity*4.0), b_frozenCurve=b_frozenCurve)
        

    def simulate(self):
        '''
        @summary: main function to derive value of knock-out swap via MC 
        @return: None, update f_kos_rate and f_kos_value
        '''

        # tmp value to run simulation
        tmp_value     = 0.0
        tmp_float_leg = 0.0
        tmp_annuity   = 0.0
        tmp_swap_rate = 0.0

        # MC simulation
        for i in range(0,self.i_MC):
            self.Libor_Market.simulate()
            tmp_swap       = self.init_swap(self.Libor_Market.ls)
            tmp_value     += self.f_notional*(self.f_fixedRate*tmp_swap[0]-tmp_swap[1])
            tmp_annuity   += tmp_swap[0]
            tmp_float_leg += tmp_swap[1]
            tmp_swap_rate += tmp_swap[1]/tmp_swap[0]

        # Average knock out swap value
        self.f_kos_value = tmp_value/self.i_MC
        test_Swap_val    = self.f_notional*(self.f_fixedRate*tmp_annuity-tmp_float_leg) / self.i_MC
        KOS_par_rate     = tmp_float_leg / tmp_annuity

        # Average knock out swap rate
        self.f_kos_rate = KOS_par_rate
        self.b_simulatePool = True

    
    def swap_rate(self):
        ''' handy function to return calculated cache value '''
        if self.b_simulatePool == False:
            self.simulate()
        return self.f_kos_rate


    def swap_value(self):
        ''' handy function to return calculated cache value '''
        if self.b_simulatePool == False:
            self.simulate()
        return self.f_kos_value
        
    
    def init_swap(self,L):
        ''' swap initialization with only one path '''

        # knock out case
        for n in range(1, int(self.f_maturity * 2.0)):
            if self.swap_rate_t(n,L) < self.f_barrier:
                f_floatLeg = sum([(1.0/4.0) * L[i][0] * self.disc_factor(L, float(i+1)/4.0) for i in range(int(4.0*n/2.0))])
                f_annuity = sum([(1.0/2.0)*self.disc_factor(L, float(i+1)/2.0) for i in range(n)])
                return f_annuity, f_floatLeg, 1

        # No knock out occurs in this path
        f_floatLeg = sum([(1.0/4.0)*L[i][0]*self.disc_factor(L, float(i+1)/4.0) for i in range(int(4.0*self.f_maturity))])
        f_annuity = sum([(1.0/2.0)*self.disc_factor(L, float(i+1)/2.0) for i in range(0,int(2.0*self.f_maturity))])
        return f_annuity, f_floatLeg, 0
    

    def disc_factor(self,L,T,s=0):
        ''' discount factor by using LIBOR fwd '''
        result = 1.
        for i in range(int(4.0*s),int(4.0*T)):
            result *= 1+1.0/4.0*L[i][0]
        return 1.0/result/self.disc_factor_t(int(T*4.0)-1, L, T)
    

    def disc_factor_t(self,i,L,T,s=0):
        ''' discount factor by using LIBOR fwd at time t'''
        result = 1.
        for j in range(int(4.0*s),int(4.0*T)):
            result *= 1+1.0/4.0*L[i][j]
        return 1.0/result
    

    def swap_rate_t(self,i,L):
        ''' swap rate of knock-out swap at time t'''
        f_floatLeg = sum([(1.0/4.0)*L[i][j]*self.disc_factor_t(i,L, float(j+1)/4.0) for j in range(int(4.0*self.f_maturity))])
        f_annuity = sum([(1.0/2.0)*self.disc_factor_t(i,L, float(j+1)/2.0) for j in range(int(2.0*self.f_maturity))])
        return f_floatLeg / f_annuity
