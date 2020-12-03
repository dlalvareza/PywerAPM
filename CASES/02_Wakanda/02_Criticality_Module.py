print('The platform is running')
 

 # Path to the main functions
import sys
sys.path.insert(0,'WEB_APP/')
sys.path.insert(0,'APM/BIN/')

import pandas as pd
from datetime import datetime
import numpy as np



# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                     Run criticality                       #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

'''def run_criticality():
    import PywerACM_Main
    df = PywerACM_Main.run_ACM()
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
def Generate_Report_Risk(DF_ACP,DF_sum,Years,N):
    from  R1_Reports import Test_Report_AC
    report_data = {
		    "Name"      : 'GESTIÓN DE ACTIVOS',
		    "Sub_title" : 'Criticidad Flota de Activos - ENERCA'
	        }
    Test_Report_AC(report_data,DF_ACP,DF_sum,Years,N)'''


# # # # # # # # # # # # # # # # # # # # # # #    

##from APM_Run import run_condition, Generate_Report_Condition, load_codition
##data_APM_df,report_date,assets = run_condition()

# # # # # # # # # # # # # # # # # # # # # # #    
#->data_APM_df,report_date,assets = run_condition()
##Generate_Report_Condition(assets)


##data_APM_df,report_date,df_porf        = load_codition()
# Metadata 
#df_apm_meta_data = Report_APM_Meta_data(data_APM_df,report_date.year)



from Processing_tools import  Report_ACM_df
from ARM_Run import load_criticality,Generate_Report_Risk, run_criticality
from APM_Run import load_codition

#years            = [2020,2021,2025,2029]
#N                = 750 

from PywerAPM_Case_Setting import years, N 
#Years             = [2021,2022,2025,2029,2039,2044]
#N                 = 750  
#asset_port   =  list(data_APM_df['Name'].values)
df_ACP           = run_criticality()
df_ACP           = load_criticality()

print(df_ACP)


_,_,df_porf        = load_codition()
data_ACP_df      = Report_ACM_df(df_ACP,df_porf,years,N)


Generate_Report_Risk(df_ACP,data_ACP_df)