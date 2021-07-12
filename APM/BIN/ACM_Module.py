# # # # # # # # # # # # # # # # # # # # # # # #
#                                             # 
#           Module to assess criticality      #
#               By: David Alvarez             #
#              04-07-2021                     #
#            Version Aplha-0.  1              #  
#                                             #
# # # # # # # # # # # # # # # # # # # # # # # #

import pandas as pd


class ACM():
    def __init__(self,load,gen):
        self.Asset_Portfolio = 1
        self.load_data       = load
        self.gen_data        = gen
    def Monetized_Energy_During_Contingency_by_hour(self,DF_Load):
        DF_Load          = DF_Load.set_index('name')
        df               = DF_Load.copy() 
        df['ES_Ben']     = DF_Load['ES']*self.load_data['Benefit']
        df['ENS_Cost']   = DF_Load['ENS']*self.load_data['Cost']
        df               = df[['ES_Ben','ENS_Cost']]
        return df

    def Monetized_Gen_During_Contingency_by_hour(self,DF_Gen):
        DF_Gen           = DF_Gen.set_index('name')
        df               = DF_Gen.copy() 
        df['Gen_Env']    = DF_Gen['gen']*self.gen_data['Env_Impact']
        df['Gen_Cost']   = DF_Gen['gen']*self.gen_data['Cost']
        df               = df[['Gen_Cost','Gen_Env']]
        return df
   
    def Benefit_During_Contingency(self,df_load,df_gen):
       l_benefit  = df_load['ES_Ben'].sum()-df_load['ENS_Cost'].sum()-df_gen['Gen_Cost'].sum()-df_gen['Gen_Env'].sum()
       return l_benefit
   
