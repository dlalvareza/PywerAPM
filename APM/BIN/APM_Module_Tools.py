# # # # # # # # # # # # # # # # # # # # # # # #
#                                             # 
#      Module to run real time contingencies  #
#        By: David Alvarez and Laura Cruz     #
#              09-08-2018                     #
#            Version Aplha-0.  1              #  
#                                             #
#     Module inputs:                          #
#              -> File name                   #
# # # # # # # # # # # # # # # # # # # # # # # #

import datetime
import calendar
from scipy.optimize import curve_fit
import numpy as np
from math import exp
import calendar
import json
import pandas as pd

def trail_date(year,day_number,h=1):
    return  (datetime.datetime(year, 1, 1,h) + datetime.timedelta(day_number - 1))

def year_day_number_to_day_name(year,day_number):
    date           = trail_date(year,day_number)
    day_name  = calendar.day_name[date.weekday()] 
    
    return day_name

# Health index forecast function
def HI_Forecast(t,beta,alpha):
    # t   -> Time to eval
    # l,m -> Health forecast constans 

    return (1 - np.exp(-((t*beta)**(1/alpha))))


# Funtion to fitt weibull HI parameters
def Fitt_constants_HI(x,y):
     # Curve fitt of HI
    (beta,alpha),_  =  curve_fit(HI_Forecast,x,y,method='dogbox')
    def eval_hi(t):
        #t =date.toordinal()
        return HI_Forecast(t,beta,alpha)

    return eval_hi          # Return fitted function 


# Read tables and return dicctinary  
def Read_Table(source,Type='Json',sheet=None):
    data = None
    if Type=='Json':
        with open(source) as json_file:
            data = json.load(json_file)
    if Type=='Excel':
            data   = pd.read_excel(open(source, 'rb'), sheet_name=sheet) # Sheet with loads  tags
    return data   