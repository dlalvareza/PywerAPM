# # # # # # # # # # # # # # # # # # # # # # # #
#                                             # 
#     Module to compute optimal decisions     #
#            By: David Alvarez                #
#              20-05-2021                     #
#            Version Aplha-0.  1              #  
#                                             #
# # # # # # # # # # # # # # # # # # # # # # # #

from datetime import date
from datetime import datetime
from datetime import timedelta

import numpy as np
from scipy.optimize import curve_fit
from scipy.optimize import fsolve
from math import exp, log
import pandas as pd


def FR_Function_to_fit(L,lam_0):
    def FR_Forecast(t,k,t_0):
        return L/(1+np.exp(-k*(t-t_0)))+lam_0
    return FR_Forecast

# # # # # # # # # Return of invessment # # # # # # # # # # # 
def ROI(pof,inc_vec,Opex,Capex,cr):
    return inc_vec/(cr*pof+Opex+Capex)-1

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
class FR():
    def __init__(self,x,y,l,lam_0):
        
        fr_Forecast        = FR_Function_to_fit(l,lam_0)
        (k,t_0),_          =  curve_fit(fr_Forecast,x,y)
        
        # Update logistic fucntion parameter 
        self.L      = l
        self.k      = k
        self.t_0    = t_0
        self.lam_0  = lam_0
        def eval_fr(t):   # t in years
            return fr_Forecast(t,self.k,self.t_0)

        self.eval_fr = eval_fr        

class OPT():
    def __init__(self,asset,data):
        # Asset -> Asset data
        # Cond  -> Asset data		
        self.Asset    = asset
        self.data     = data
        self.fr_cases = {}
        self.lam_0    =  self.Asset.lambda_f(0)
        self.L        = self.Asset.lambda_f(1)-self.lam_0
        self.dt       = 0.001  # Integral time step 
        self.t_beg    = 0      # Assessment begin      

        self.f_fit_FR()                                            # Fit historical failure rate
        self.new_conditions()                                      # Fit failure rate as a new condition

        # # # # # # # # # # Criticality by year # # # # # # # # #  
        self.Cr      = -self.data['RI']['Cr'].values.mean()
        self.inc     = self.Asset.inc
        # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        
# # # # # # # # # # # # # # # # # # # # # # #
    def f_fit_FR(self):   # Function to fit the failure rate
        l_data                = self.data['Con'].drop_duplicates(subset ="Date", keep='last')
        self.t_0              = l_data['Date'].dt.date.values[0]
        date                  = l_data['Date'].dt.date.values-self.t_0
        x                     =  np.asarray([(x).days/365.25 for x in date])
        x[0]                  = 1e-6                                        # Delete zero for fitting convergence
        y                     = l_data['lambda'].values
        self.fr_cases['Base'] = FR(x,y,self.L,self.lam_0) 

# # # # # # # # # # # # # # # # # # # # # # #
    def new_conditions(self):
         x    = np.linspace(1e-6, 50, num=50)
         hi   = self.Asset.hi_rem(x)
         y    = np.array([self.Asset.lambda_f(x) for x in hi]) 

         self.fr_cases['New'] =  FR(x,y,self.L,self.lam_0)  

# # # # # # # # # # # # # # # # # # # # # # #
    def maint_conditions(self,hi_rem=0.1):
         x     = np.linspace(1e-6, 50, num=50)
         hi    = self.Asset.hi_rem(x)
         y     = np.array([self.Asset.lambda_f(x) for x in hi]) 
         
         def rem_hi(t):        # solve when hi(t)-hi_Rem = 0
         	return self.Asset.hi_rem(t)-hi_rem
         root  = fsolve(rem_hi, 1) 
         
         x     = x-root 
         self.fr_cases['Maint'] =  FR(x,y,self.L,self.lam_0)  
         
# # # # # # # # # Optimal maitenance function # # # # # # # # # # # # # #
    def ROI_cost_func_Maint(self,T_end):   # Optimal replacement
        lambda_0 = self.lam_0
        L        = self.L
        k        = self.fr_cases['Maint'].k
        t        = self.fr_cases['Maint'].t_0
        T_beg    = self.t_beg
	
        capex    = 0#self.Asset.capex
        opex     = self.Asset.opex
        Inc      = self.inc    
        Cr       = self.Cr
    
        def opt_maint(x):
            l_sum_lam  = (T_end/x)*((L/k)*(log(exp(k*( t-x))+1)-log(exp(k* t)+1))+x*(lambda_0+L))
            l_pof = 1-exp(-l_sum_lam)

            return -(T_end*Inc/(Cr*l_pof +(T_end/x-1)*opex+capex) -1)
        return opt_maint


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                                 #
#                             Replacement assessment                                              #
#                                                                                                 #    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

        
# # # # # # # # # Optimal replacement function # # # # # # # # # # # # # #
    def ROI_cost_func(self,T_end):   # Optimal replacement
        lambda_0 = self.lam_0
        L        = self.L
        k1       = self.fr_cases['Base'].k
        t1       = self.fr_cases['Base'].t_0
        k2       = self.fr_cases['New'].k
        t2       = self.fr_cases['New'].t_0
        T_beg    = self.t_beg
	
        capex    = self.Asset.capex
        opex     = self.Asset.opex
        Inc      = self.inc    
        Cr       = self.Cr

        def opt_remp(x):
            func0      = (lambda_0+L)*(T_end-T_beg)
            func1      = (log(exp(k1*(T_beg+t1-x))+1)-log(exp(k1*t1)+1))/k1
            func2      = (log(exp(k2*(x+t2-T_end))+1)-log(exp(k2*t2)+1))/k2
            l_sum_lam  = func0+L*(func1+func2)
            l_pof      = 1-exp(-l_sum_lam)
            return -(T_end*Inc/(Cr*l_pof+opex+capex) -1)
        return opt_remp

    def Reliability_asseesment(self,t_vec,case,t_rem=0):
        lam          = case.eval_fr(t_vec-t_rem) 
        cum_sum_lamb = np.cumsum(lam*self.dt)
        time         = np.array([date.today() + timedelta(days=x*365.25) for x in t_vec])

        df_dic       ={'Time':time,
                      'FR':lam,
                      'Sum_Fr': cum_sum_lamb}
        df           = pd.DataFrame(df_dic)

        df['Time']   = pd.to_datetime(df['Time'])
        return df

# # # # # # # # # # # # Scneario assessment # # # # # # # # # # #
    def Current_Con_Rel_asseesment(self,t_end,case_name='Base'):
        t_vec      = np.arange(self.t_beg,t_end,step=self.dt)       # Time vector
        case       = self.fr_cases[case_name]
        df         = self.Reliability_asseesment(t_vec,case) 
        df['pof']  = 1-np.exp(-df['Sum_Fr'].values)
        return df

    def Replacement_asseesment(self,t_end,t_remp):
        t_vec_1        = np.arange(self.t_beg,t_remp,step=self.dt)
        case           = self.fr_cases['Base']
        df_1           = self.Reliability_asseesment(t_vec_1,case)         
        t_vec_2        = np.arange(t_remp,t_end+self.dt,step=self.dt)
        case           = self.fr_cases['New']

        df_2           = self.Reliability_asseesment(t_vec_2,case,t_rem=t_remp)   
        df             = pd.concat([df_1,df_2])
        df['Sum_Fr']   = np.cumsum(df['FR']*self.dt)          # Update cummulative failure rate
        df['pof']      = 1-np.exp(-df['Sum_Fr'].values)
        return df      

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                                 #
#                             Maintenanc assessment                                               #
#                                                                                                 #    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

    def lam_fun_maintenance(self,time,delta_man):
       lam   = np.zeros(len(time))
       man_t = np.zeros(len(time))
       k     = 0
       k_n   = 0
       n_man = 1
       case  = self.fr_cases['Maint']
       
       for t in time:
           if t >= delta_man*n_man:
              n_man   +=1
              k_n      = int(k)
              man_t[k] = 1
           t_k     = t-time[k_n]    
           lam[k]  = case.eval_fr(t_k) 
           k      +=1 

       cum_sum_lamb = np.cumsum(lam*self.dt) 
       
       # Create data frame
       time         = np.array([date.today() + timedelta(days=x*365.25) for x in time])
       df_dic       ={'Time':time,
                      'FR':lam,
                      'Sum_Fr': cum_sum_lamb}
       df           = pd.DataFrame(df_dic)
       df['Time']   = pd.to_datetime(df['Time'])        
       
       return df
    
    def Maintenance_asseesment(self,t_end,t_man):
        t_vec          = np.arange(self.t_beg,t_end,step=self.dt)
        df             = self.lam_fun_maintenance(t_vec,t_man)
        df['pof']      = 1-np.exp(-df['Sum_Fr'].values)
        return df  


    def run_maint_heurisitic(self,t_end):

        K        = np.linspace(1, t_end, t_end*5, endpoint=True)
        cost     = np.zeros(len(K))
        l        = 0
        for k in K:
            man_n             = int(t_end/k)
            l_df              = self.Maintenance_asseesment(t_end,k)
            l_cost            = self.ROI_Assessment(l_df,t_end,inve=0,man_n=man_n)  
            total_cost        = l_cost.roi.values[-1]
            cost[l]           = total_cost
            l                += 1     
	# Update dataframe
        df = {'ROI': cost,
               'Rep': K}
        df   = pd.DataFrame(df)
        return df
         
  
                 
# # # # # # # # # ROI assessment # # # # # # # # # # ## 
    def ROI_Assessment(self,df_R,t_end,inve=1,man_n =1 ):
	 #man_n  -> 
        inc          = self.Asset.inc
        opex         = self.Asset.opex
        cr           = self.Cr
        capex        = self.Asset.capex*inve
        l_R_by_year  = df_R.groupby([df_R.Time.dt.year]).mean()#  df_R.pof.values

        time_vec     =  np.linspace(1, t_end,num=len(l_R_by_year), endpoint=True)
        inc_vec      =  inc*(time_vec)
        #self.inc     =  inc
        pof          = l_R_by_year.pof.values
        
        man_cost     = opex*man_n
        roi          = ROI(pof,inc_vec,man_cost,capex,cr)

        df           = l_R_by_year.copy()
        df['roi']    = roi
        df           = df.reset_index(drop=False)
        return df

# # # # # # # # # Heuristic assessment # # # # # # # # # # # #

    def run_heurisitic(self,t_end):
         K        = np.linspace(0, t_end, t_end+1, endpoint=True)          
         cost     = np.zeros(len(K))

         l        = 0
         for k in K[:-1]:
            l_df           = self.Replacement_asseesment(t_end,k)
            l_cost         = self.ROI_Assessment(l_df,t_end)
            total_cost     = l_cost.roi.values[-1]
            cost[l]        = total_cost
            l             += 1  

	 # None replacement
         l_df           = self.Replacement_asseesment(t_end,t_end)
         l_cost         = self.ROI_Assessment(l_df,t_end,inve=0)
         cost[l]        = l_cost.roi.values[-1]
	 
	 # Update dataframe
         df = {'ROI': cost,
               'Rep': K}
         df   = pd.DataFrame(df)
         return df
