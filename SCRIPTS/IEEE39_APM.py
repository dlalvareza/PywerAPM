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
date_beg               = datetime.datetime(2020, 1, 1,1) 
load_growth            = 0.02                              # Assumed load growth per year       
h_end                  = 5*24*365                          # Assumed period of planning 

case_settings = {
				'portfolio_source': 'CASES/01_ENERCA/ENERCA_Asset_Portfolio.xlsx',
				'database_sett': 'CASES/01_ENERCA/ENERCA_DB_Model.json'
				}

# Project data
report_data = {
		"Name"      : 'Asset Management',
		"Sub_title" : 'APM - Fleet Performance'
	}

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                               #
#                 Normal Operating conditions                   #
#                                                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Create contingencies assessment object
Cont_A = RTC_A(net_file,file_tags)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                               #
#                Historical records of condition                #
#                                                               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

# Porfolio assessment 
from APM_Module import APM 
#Assets  = APM(asset_portfolio_source,load_growth)
Assets  = APM(case_settings,load_growth)

# Generate report
from  R1_Reports import Test_Report_AP
Test_Report_AP(report_data,Assets)