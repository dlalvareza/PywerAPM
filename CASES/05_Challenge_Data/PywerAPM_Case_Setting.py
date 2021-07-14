import datetime
import sys



# Performance assessment Settings
path                    = '../CASES/05_Challenge_Data/' 
load_growth             = 0.02                              # Assumed load growth per year   
date_beg                = datetime.date.today()
h_end                   = 2*24*365                          # Assumed period of planning 
n_years                 = 20
n_days                  = int(n_years*365.25)               # Assumed period of planning 
n_hours                 = n_days*24
N                       = 20                               # Monte-Carlo Simulations  
results_path            = path+'02_Results/'
test_date_2 = datetime.date(2022, 1, 1)
test_date_3 = datetime.date(2025, 1, 1)
test_date_4 = datetime.date(2030, 1, 1)
test_date_5 = datetime.date(2035, 1, 1)

case_settings = {
				'path'              : '../',
				'net_file'          : path+'challege_net.json',	
				'load_data'         : path +'Challenge_Asset_Portfolio.xlsx',
				'Cr'                : path+'01_Data/CRITICALITY.xlsx',
				'portfolio_source'  : path +'Challenge_Asset_Portfolio.xlsx',
				'database_sett'     : path+'Challenge_DB_Model.json',
				'cont_stra'         : path+'Operation_Strategies.json',
				'AM_Plan'           : path+'AM_Plan.json',
				'database_Cons_Set' : path+'Challenge_DB_Data.json' 
				}

# Project data
report_data = {
		"Name"      : 'Gestión de activos y principios de inteligencia computacional aplicada al sector eléctrico',
		"Sub_title" : 'APM - Fleet Performance'
	}

years             = [2022,2025,2029,2039,2044]
#N                 = 750  

#load_growth       = 0.02  
 
