# # # # # # # # # # # # # # # # # # # # #
#                                       #
#         By David L. Alvarez           #
#           Version 0.0.1               #
#                                       #
# # # # # # # # # # # # # # # # # # # # #

import pickle
import pandas as pd
import numpy as np

def disc_factor(n,r):
    return 1/((1+r)**n)

def Report_ACM_df_Desc(Date,DF):
    year    = Date.year
    month   = Date.month
    #return  DF[(DF.Date.dt.year==year) & (DF.Date.dt.month==month)]
    return  DF[(DF.Date.dt.year==year)]

def cash_flow(DF,R):
    df              = DF[['date','RI','Inves']]
    df['n']         = round((df['date']-df['date'][0])/np.timedelta64(1,'Y'),2) 
    df['Cash_flow'] = df['RI']+df['Inves']
    df['PV']        = df.apply(lambda row: disc_factor(row.n,R)*row.Cash_flow, axis = 1)  
    pv              = df.PV.sum()
    return df,pv 

def Compute_Ri_Df(asset,df,date_beg,d_day_for):
    df_con         = asset.POF_R_Assessment(date_beg,d_day_for*24)
    df_con['Date'] = pd.to_datetime(df_con['Date'])
    
    RI_df         = pd.DataFrame()
    N_years       = int(d_day_for/365.25+1)
    dti           = pd.date_range(date_beg, periods=N_years, freq='Y')
    
    RI_df['date'] = dti
    cr            = [] 
    pof           = []
    for date in dti:
        df_by_month     = Report_ACM_df_Desc(date,df)
        df_pof_by_month = Report_ACM_df_Desc(date,df_con)
        
        grouped_df      = df_by_month.groupby("Ite")
        
        cr_temp     = grouped_df.sum().Cr.values
        if cr_temp.size ==0:
            cr_temp = 0
        else:    
            cr_temp = np.sqrt(np.mean(cr_temp**2))
        
        cr.append(-cr_temp)  
    
        l_pof           = df_pof_by_month.POF.mean()
        pof.append(l_pof/100)

    RI_df['Cr']          = cr
    RI_df['pof']         = pof
    RI_df['RI']          = RI_df['pof']*RI_df['Cr'] 
    RI_df['Inves']       = 0 
    
    return RI_df,df_con

class Desicion_Making():
    def __init__(self,ASSETS,DF_ACP):
        self.scenario         = {}
        self.assets           = ASSETS
        self.df_ACP           = DF_ACP  # Criticality 
        self.R                = 0.13   # Discount rate
    
    def run_scenario_base(self):
        self.scenario['Base'] = self.scenario_assessment()
        dic                   = self.scenario['Base']
        # Save result as pkl
        l_file                = open('RESULTS/Desicion_Making_Base.pkl', 'wb') 
        pickle.dump(dic, l_file) 
        l_file.close()
    
    def load_scenario_base(self):    
        with open('RESULTS/Desicion_Making_Base.pkl', 'rb') as f:
            data = pickle.load(f)
            
        self.scenario['Base'] = data
    
    def run_scenario(self,Name,DESC):
        # Update decisions
        df                  = DESC.groupby(['Asset_id'])
        self.scenario[Name] = self.scenario_assessment(df_desc=df)
        

    def scenario_assessment(self,df_desc=None):
        import copy 
        scenario     = {}
        l_assets     = copy.deepcopy(self.assets) 
        
        if not df_desc ==None:                  # Update assets conditions 
            scenario  = self.scenario['Base'].copy()
            for asset_id,df_dec in df_desc:
                asset                           = l_assets.Asset_Portfolio[asset_id]
                asset.decision                  = df_dec  # Update decision
                asset_name                      = l_assets.Asset_Portfolio_List.loc[asset_id].Name
                df                              = self.df_ACP[self.df_ACP[asset_name]==True]
                df                              = df[['Date','Cr','Ite']]
                
                RI_df,df_con                    = Compute_Ri_Df(asset,df,self.date_beg,self.N_days)
                
                # Update cost of the decision 
                desc                            = asset.decision
                for index, value in desc.Date.items():
                    desc_year = pd.to_datetime(value).year
                    #desc_year                       = pd.to_datetime(desc['Date']).dt.year[0]
                
                    desc_cost                       = -desc['Cost'][index] 
                    RI_df.loc[RI_df['date'].dt.year == desc_year, 'Inves'] = desc_cost
                
                # Compute cash flow    
                df_cf,PV                        = cash_flow(RI_df,self.R)
                scenario[asset_id]              = {'RI':RI_df,'Con':df_con,'CF':df_cf,'PV':PV} 
            return scenario
                # Update risk 
        else: # Mean that it is the base scenario   
            for asset_id in l_assets.Asset_Portfolio.keys():
                asset          = l_assets.Asset_Portfolio[asset_id]
                asset_name     = l_assets.Asset_Portfolio_List.loc[asset_id].Name
                df             = self.df_ACP[self.df_ACP[asset_name]==True]
                df             = df[['Date','Cr','Ite']]

                RI_df,df_con             = Compute_Ri_Df(asset,df,self.date_beg,self.N_days)
        
                df_cf,PV                 = cash_flow(RI_df,self.R)
                df_cf.head()
                scenario[asset_id]       = {'RI':RI_df,'Con':df_con,'CF':df_cf,'PV':PV} 
        
            return scenario
