# # # # # # # # # # # # # # # # # # # # # # # #
#                                             # 
#      Module to run condition module         #
#             By: David Alvarez               #
#                08-11-2020                   #
#             Version Aplha-0.  1             #  
#                                             #
# # # # # # # # # # # # # # # # # # # # # # # #



#from PywerAPM_Case_Setting import asset_portfolio_source, file_tags,net_file,date_beg,load_growth,h_end,case_settings, report_data 
from PywerAPM_Case_Setting import*

from APM_Module import APM 
from Processing_tools import Report_APM_df, Report_APM_Meta_data, Report_ACM_df, Report_ACM_Meta_data


import pandas as pd
from datetime import datetime


results_path ='RESULTS/'

def run_main():
	# Porfolio assessment 
	Assets  = APM(case_settings,load_growth)

	return Assets


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                        Run conditon                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def run_condition():
    assets    = run_main()
    date      = datetime.date(datetime.now())
    df        = Report_APM_df(assets,date)
    df        = df.drop(columns=['geometry'])
    df        = pd.DataFrame(df)

    # # # # # # # # # # # # # # 
    df_porfolio = assets.Asset_Portfolio_List
    store      = pd.HDFStore(results_path+'Porfolio.h5')
    store.put('df', df_porfolio)
    store.get_storer('df').attrs['TITLE'] = 'AM_Porfolio'
    store.get_storer('df').attrs['Date'] = date
    store.close()

    # # # # # # # # # # # # # # 
    store      = pd.HDFStore(results_path+'Results_APM.h5')
    store.put('df', df)
    store.get_storer('df').attrs['TITLE'] = 'APM_Report'
    store.get_storer('df').attrs['Date'] = date
    store.close()
    return df,date,assets

def load_codition():    
    store   = pd.HDFStore(results_path+'Results_APM.h5')
    df      = store['df']
    date    = store.get_storer('df').attrs['Date']
    store.close()
    # # # # # # # # # # # # # # # # # # # # # # # # # 
    store   = pd.HDFStore(results_path+'Porfolio.h5')
    df_porf = store['df']
    #date   = store.get_storer('df').attrs['Date']
    store.close()

    return df,date,df_porf

# Generate condition report
def Generate_Report_Condition(Assets):
    from  R1_Reports import Test_Report_AP
    #report_data = {
	#	    "Name"      : 'GESTIÓN DE ACTIVOS',
	#	    "Sub_title" : 'Condición Flota de Activos - ENERCA'
	#        }
    Test_Report_AP(report_data,Assets,plan_horizonts=years)