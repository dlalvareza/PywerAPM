import pandas as pd
from time import time
from math import sqrt
import matplotlib.pyplot as plt
import datetime
import sys

# Import real time contingencies assessment
from ST_AM_Contingencies_Analysis import Real_Time_Contingencies as RTC_A
from ST_AM_Contingencies_Ploty import  Plot_All_Days_Hour_Data
from ST_AM_Contingencies_Ploty import  Plot_Stack


# Performance assessment Settings
path                   = '../CASES/05_Challenge_Data/' 
net_file               = path+'challege_net.json'

#path                   = '../../../02_Develop/PywerAPM/PywerAPM/'
load_data               = path +'Challenge_Asset_Portfolio.xlsx'
load_growth             = 0.02                              # Assumed load growth per year   
date_beg               = datetime.date.today() 
h_end                  = 2*24*365                         # Assumed period of planning 
#asset_portfolio_source = '../../../02_Develop/PywerAPM/PywerAPM/CASES/APM/DATA/IEEE39_Asset_Data.xlsx'


#n_hours                = int(25*24*365.25)                 # Assumed period of planning 


#case_settings = {
#				'path'              : path,
#				'Cr'                : path+'CASES/04_Boot_Data/01_Data/CRITICALITY.xlsx',
#				'portfolio_source'  : '../../../02_Develop/PywerAPM/PywerAPM/CASES/04_Boot_Data/Wakanda_Asset_Portfolio.xlsx',
#				'database_sett'     : '../../../02_Develop/PywerAPM/PywerAPM/CASES/04_Boot_Data/Wakanda_DB_Model.json',
#				'database_Cons_Set' : '../../../02_Develop/PywerAPM/PywerAPM/CASES/04_Boot_Data/Wakanda_DB_Data.json' 
#				}

# Project data
#report_data = {
#		"Name"      : 'Wakanda Asset Management',
#		"Sub_title" : 'APM - Fleet Performance'
#	}

#years             = [2022,2025,2029,2039,2044]
#N                 = 750  

#load_growth       = 0.02  
 
