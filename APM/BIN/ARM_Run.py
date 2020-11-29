# # # # # # # # # # # # # # # # # # # # # # # #
#                                             # 
#      Module to run condition module         #
#             By: David Alvarez               #
#                08-11-2020                   #
#             Version Aplha-0.  1             #  
#                                             #
# # # # # # # # # # # # # # # # # # # # # # # #



#from PywerAPM_Case_Setting import asset_portfolio_source, file_tags,net_file,date_beg,load_growth,h_end,case_settings,report_data 
from PywerAPM_Case_Setting import*


from APM_Module import APM 
from Processing_tools import Report_APM_df, Report_APM_Meta_data, Report_ACM_Meta_data


import pandas as pd
from datetime import datetime

results_path ='RESULTS/'

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                     Run criticality                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def run_criticality():
    import PywerACM_Main
    df = PywerACM_Main.run_ACM(N)
    store      = pd.HDFStore(results_path+'Results_ACM.h5')
    store.put('df', df)
    store.get_storer('df').attrs['TITLE'] = 'ACM_Report'
    date      = datetime.date(datetime.now())
    print(date)
    store.get_storer('df').attrs['Date'] = date
    store.close()


def load_criticality():    
    store   = pd.HDFStore(results_path+'Results_ACM.h5')
    df     = store['df']
    #date   = store.get_storer('df').attrs['Date']
    store.close()
    return df

# Generate condition report
def Generate_Report_Risk(DF_ACP,DF_sum):
    from  R1_Reports import Test_Report_AC
    #report_data = {
	#	    "Name"      : 'GESTIÓN DE ACTIVOS',
	#	    "Sub_title" : 'Criticidad Flota de Activos - ENERCA'
	#        }
    Test_Report_AC(report_data,DF_ACP,DF_sum,Years,N)