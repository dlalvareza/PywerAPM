# # # # # # # # # # # # # # # # # # # # # # # #
#                                             # 
#       Procedures to eval and fitt           #
#             load forecast                   #
#      By: David Alvarez and Laura Cruz       #
#              12-22-2018                     #
#             Version 0.1                     #
#                                             #
# # # # # # # # # # # # # # # # # # # # # # # #

# Function to eval the Fourier series, na is the number of coefficients

import numpy as np
from scipy.optimize import curve_fit
        
def make_fourier(na,T):
    def fourier(x, *a):
        ret=a[0]/2
        for deg in range(1, na,2):
            ret += a[deg] * np.cos((deg) *2* np.pi / T * x-a[deg+1])
        return ret
    return fourier
      

class Load_Fitt:
    def __init__(self,Time,Load):        
        T                 = 24*2
        n_coef            = 10   
        fit_f             = make_fourier(2*n_coef,T)
        coef , pcov       = curve_fit(fit_f, Time, Load, [0.0]*(2*n_coef+1))    
        self.T            = T
        self.coef_hat     = coef
        self.func         = fit_f
        
# Function to get the load forecast of an entire day		
    def Load_Forecast_by_Day(self,Load_t0,dt):	 
        # Load_t0 -> loat at instant t_0
		# dt      -> De between hours 
        coef               = self.coef_hat
        coef[0]            = 0
        a0                 = 2*(Load_t0-self.func(0,*coef))
        coef[0]            = a0    
        import numpy as np
        #hour               = np.linspace(0,24,24*60,endpoint=False)
        hour               = np.linspace(0,24,24*dt,endpoint=False)		
        i_forecast         = self.func(hour, *coef)

        return i_forecast 