import pandas as pd
from time import time
import datetime
import sys
sys.path.insert(1,'APM/BIN/')


# Import real time contingencies assessment
from ST_AM_Contingencies_Analysis import Real_Time_Contingencies as RTC_A



# Project data
report_data = {
		"Name"      : 'GESTIÓN DE ACTIVOS',
		"Sub_title" : 'Estimación de Índice de Salud y Vida Remanente de equipos Auxiliares de Subestación'
	}

# Performance assessment Settings
file_tags              = 'APM/DATA/IEEE39_Asset_Data.xlsx'
asset_portfolio_source = 'APM/DATA/IEEE39_Asset_Data.xlsx'
net_file               = 'APM/DATA/IEEE39NODES.xlsx'
date_beg               = datetime.datetime(2020, 1, 1,1) 
load_growth            = 0.02                              # Assumed load growth per year       
h_end                  = 1*24*1                            # Assumed period of planning 


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
Assets  = APM(asset_portfolio_source,load_growth)


# Generate report
from  R1_Reports import Test_Report_AP
Test_Report_AP(report_data,Assets)