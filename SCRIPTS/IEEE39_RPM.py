import pandapower as pp
import pandapower.networks as pn
import pandas as pd
from time import time
from math import sqrt
import matplotlib.pyplot as plt
import calendar
import datetime

import sys
sys.path.insert(0,'APM/BIN/')





file_tags              = 'APM/DATA/IEEE39_Asset_Data.xlsx'
asset_portfolio_source = 'APM/DATA/IEEE39_Asset_Data.xlsx'
net_file               = 'APM/DATA/IEEE39NODES.xlsx'
load_growth            = 0.02  

#
from APM_Module_Tools import year_day_number_to_day_name
from APM_Module_Tools import trail_date


# Import real time contingencies assessment
from ST_AM_Contingencies_Analysis import Real_Time_Contingencies as RTC_A
Cont_A = RTC_A(net_file,file_tags)
Cont_A.Load_Growth_Update(load_growth)        # Update load growth rate


# Asset porfolio 
from APM_Module import APM 
Assets  = APM(asset_portfolio_source,load_growth)




# Monte Carlo Simulation
#N     = 750
N     = 24



date_beg = datetime.datetime(2020, 1, 1,1)  
n_hours  = 10*8760



# Parallezite 
import multiprocessing as mp
print("Number of processors: ", mp.cpu_count())
pool      = mp.Pool(mp.cpu_count()) 



def parallel_test(x):
    print(x)
    res_dic = Assets.Risk_Index_During_Time(Cont_A,date_beg,n_hours,x)
    return res_dic

if __name__ == '__main__':
    pool      = mp.Pool(mp.cpu_count()) 
    trails    =  range(N)
    rest      = pool.map(parallel_test, trails)

LoL = []
for r in rest:
    LoL.extend(r)

'''for trail in range(N):
    print('Iteration '+str(trail))
    
    res_dic = Assets.Risk_Index_During_Time(Cont_A,date_beg,n_hours,trail)'''    

df = pd.DataFrame(LoL)
print(df)

df.to_feather("RESULTS/dummy.ft")