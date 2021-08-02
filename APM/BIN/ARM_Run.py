# # # # # # # # # # # # # # # # # # # # # # # #
#                                             # 
#      Module to run condition module         #
#             By: David Alvarez               #
#                08-11-2020                   #
#             Version Aplha-0.  1             #  
#                                             #
# # # # # # # # # # # # # # # # # # # # # # # #

from PywerAPM_Case_Setting import*

from APM_Module import APM 
from Processing_tools import Report_APM_df, Report_APM_Meta_data, Report_ACM_Meta_data
import pandas as pd
from datetime import datetime

#results_path ='RESULTS/'

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


def load_criticality(cr_type='Monte_Carlo',assets=None):      
    if cr_type == 'Monte_Carlo':               # Load Montecarlo simulations
        store   = pd.HDFStore(results_path+'Results_ACM.h5')
        df     = store['df']
        store.close()
    else:                         # Fixed conditios
        df  = assets.copy()
        df_type  = {}
        df_group = assets.groupby(['Disc_Type'])
        for group in df_group:              # Read criticality by type of asset 
            name = group[0]
            df_type       = pd.read_excel(cr_type, sheet_name=name,usecols = "A:H")
            for index, row in df_type.iterrows(): 
                df.loc[(df.Disc_Type==name) & (df.Asset_To_Disconet==row.Asset),['Cr_Env','Cr_Sec','Cr_Leg']] = [row.ENVIRONMENTAL,row.SECURITY,row.LEGAL]
        # Total criticality
        df['T_Cr'] = df['Cr_Env']+df['Cr_Sec']+df['Cr_Leg']+df['Cr_Fin'] 
    return df

# Generate condition report
def Generate_Report_Risk(DF_ACP,DF_sum):
    from  R1_Reports import Test_Report_AC
    Test_Report_AC(report_data,DF_ACP,DF_sum,years,N)
