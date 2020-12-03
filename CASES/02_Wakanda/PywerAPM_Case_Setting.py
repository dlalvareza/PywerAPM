import pandas as pd
from time import time
from math import sqrt
import matplotlib.pyplot as plt
import datetime
import sys
sys.path.insert(0,'APM/BIN/')

# Import real time contingencies assessment
from ST_AM_Contingencies_Analysis import Real_Time_Contingencies as RTC_A
from ST_AM_Contingencies_Ploty import  Plot_All_Days_Hour_Data
from ST_AM_Contingencies_Ploty import  Plot_Stack


# Performance assessment Settings

file_tags              = 'APM/DATA/IEEE39_Asset_Data.xlsx'
asset_portfolio_source = 'APM/DATA/IEEE39_Asset_Data.xlsx'
net_file               = 'APM/DATA/IEEE39NODES.xlsx'
date_beg               = datetime.date.today() 
load_growth            = 0.02                              # Assumed load growth per year   
n_hours                = int(25*24*365.25)                 # Assumed period of planning 
#h_end                  = 5*24*365                         # Assumed period of planning 

case_settings = {
				'portfolio_source'  : 'CASES/02_Wakanda/Wakanda_Asset_Portfolio.xlsx',
				'database_sett'     : 'CASES/02_Wakanda/Wakanda_DB_Model.json',
				'database_Cons_Set' : 'CASES/02_Wakanda/Wakanda_DB_Data.json' 
				}

# Project data
report_data = {
		"Name"      : 'Wakanda Asset Management',
		"Sub_title" : 'APM - Fleet Performance'
	}

years             = [2022,2025,2029,2039,2044]
N                 = 750  


load_growth            = 0.02  


#Years  = [2020,2021,2025,2029]
#N      = 750  



#Years  = [2020,2021,2025,2029]
#N      = 400  
