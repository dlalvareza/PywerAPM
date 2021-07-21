# # # # # # # # # # # # # # # # # # # # #
#                                       #
#         By David L. Alvarez           #
#           Version 0.0.1               #
#                                       #
# # # # # # # # # # # # # # # # # # # # #

import pickle
import pandas as pd
import numpy as np


from OPT_Module import OPT

def disc_factor(n,r):
    return 1/((1+r)**n)

def Report_ACM_df_Desc(Date,DF):
    year    = Date.year
    #month   = Date.month
    return  DF[(DF.Date.dt.year==year)]

def cash_flow(DF,R):
    df              = DF[['date','RI','Inves']]
    df['n']         = round((df['date']-df['date'][0])/np.timedelta64(1,'Y'),2) 
    df['Cash_flow'] = df['RI']+df['Inves']
    df['PV']        = df.apply(lambda row: disc_factor(row.n,R)*row.Cash_flow, axis = 1)  
    pv              = df.PV.sum()
    return df,pv 

def Compute_Ri_Df(asset,df,date_beg,d_day_for,Cr_Fixed):

    df_con         = asset.POF_R_Assessment(date_beg,d_day_for*24)
    df_con['Date'] = pd.to_datetime(df_con['Date'])
  

    RI_df         = pd.DataFrame()
    N_years       = int(d_day_for/365.25+1)
    dti           = pd.date_range(date_beg, periods=N_years, freq='Y')
    
    RI_df['date'] = dti
    cr            = [] 
    pof           = []
    for date in dti:
        if df.empty:           # Check if montecarlo simulation are provided
            df_by_month     = Report_ACM_df_Desc(date,df_con)
        else: 
            df_by_month     = Report_ACM_df_Desc(date,df)

        df_pof_by_month     = Report_ACM_df_Desc(date,df_con)

        cr_temp   = 0
        if not df.empty:   # Check if montecarlo simulations are provided
            grouped_df     = df_by_month.groupby("Ite")
            cr_temp        = grouped_df.sum().Cr.values
            if cr_temp.size ==0:
                cr_temp = 0
            else:    
                cr_temp = np.sqrt(np.mean(cr_temp**2))*3 # Energy cost
        

        cr_temp += Cr_Fixed   # Add fixed criticality
        cr.append(-cr_temp)  
    
        l_pof           = df_pof_by_month.POF.mean()
        pof.append(l_pof/100)

    RI_df['Cr']          = cr
    RI_df['pof']         = pof
    RI_df['RI']          = RI_df['pof']*RI_df['Cr'] 
    RI_df['Inves']       = 0 
    
    return RI_df,df_con

class Decision_Making():
    def __init__(self,ASSETS,DF_ACP=pd.DataFrame(), df_AC_Fixed=pd.DataFrame()):
        self.scenario         = {}
        self.assets           = ASSETS
        self.df_ACP           = DF_ACP         # Criticality by montecarlo  
        self.df_AC_Fixed      = df_AC_Fixed    # Fixed criticality
        self.R                = 0.13   # Discount rate
    
    def run_scenario_base(self):
        self.scenario['Base'] = self.scenario_assessment()
        dic                   = self.scenario['Base']
        # Save result as pkl
        l_file                = open('RESULTS/Decision_Making_Base.pkl', 'wb') 
        pickle.dump(dic, l_file) 
        l_file.close()
    
    def load_scenario_base(self):    
        with open('RESULTS/Decision_Making_Base.pkl', 'rb') as f:
            data = pickle.load(f)
            
        self.scenario['Base'] = data
    
    def run_scenario(self,Name,DESC):
        # Update decisions
        #df                  = DESC.groupby(['Asset_id'])
        df                  = DESC#.groupby(['Asset_id'])
        self.scenario[Name] = self.scenario_assessment(df_desc=DESC)
        

    def scenario_assessment(self,df_desc=pd.DataFrame()):
        import copy 
        scenario     = {}
        l_assets     = copy.deepcopy(self.assets) 
        
        if not df_desc.empty:                  # Update assets conditions 
            l_scenario  = self.scenario['Base'].copy()
            for project in df_desc.iterrows():
                try: 
                    l_project = project[1] 
                    name                = l_project.Asset_Name
                    df                  = l_assets.Asset_Portfolio_List
                    asset_id            = df[df['Name'] == name].index.values[0]
                    l_asset             = l_assets.Asset_Portfolio[asset_id]
                    data                = l_scenario[asset_id]
                    opt_des             = OPT(l_asset,data)  
                    n_years             = self.N_days/365.25
                    t_desc              = l_project.Date.date()

                    t_remp              = (t_desc-self.date_beg).days/365.25
                    RI_df               = l_scenario[asset_id]['RI'].copy()

                    #print(l_project) 
                    if l_project.Des_Type== 'Replace':
                        df_desc             = opt_des.Replacement_asseesment(n_years,t_remp)
                        cost                = df.loc[asset_id].CAPEX
                        desc_year           = project[1].Date.date().year
                        RI_df.loc[RI_df['date'].dt.year == desc_year, 'Inves'] = -cost
                    elif l_project.Des_Type == 'Maintenance':
                        opt_des.maint_conditions(hi_rem=0.2)
                        df_desc             = opt_des.Maintenance_asseesment(n_years,t_remp)
                        N                   = int(n_years/t_remp)
                        x1                  = np.linspace(t_remp, n_years, N, endpoint=False)
                        x1                  = self.date_beg.year+x1
                        desc_year           = list(x1.astype(int))
                        cost                = df.loc[asset_id].OPEX
                        for y in desc_year: # Update costs
                            RI_df.loc[RI_df['date'].dt.year == y, 'Inves'] = -cost
                        

                    df_pof_by_year      = df_desc.groupby(df_desc.Time.dt.year).mean()
                    
                    RI_df.pof          = df_pof_by_year.pof.values
                    RI_df.RI           = RI_df.pof*RI_df.Cr

                    #print(RI_df)
                    # Compute cash flow    
                    df_cf,PV                        = cash_flow(RI_df,self.R)
                    df_con                          = l_scenario[asset_id]['Con']

                    l_scenario[asset_id]              = {'RI':RI_df,'Con':df_con,'CF':df_cf,'PV':PV} 
                except:
                    print('Project '+name+ ' is not well defined')
                    pass
            return l_scenario
                # Update risk 
        else: # Mean that it is the base scenario   
            for asset_id in l_assets.Asset_Portfolio.keys():
                asset          = l_assets.Asset_Portfolio[asset_id]
                asset_name     = l_assets.Asset_Portfolio_List.loc[asset_id].Name

               # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #    
                df = pd.DataFrame()
                if not self.df_ACP.empty:
                    df             = self.df_ACP[self.df_ACP[asset_name]==True]
                    df             = df[['Date','Cr','Ite']]
                    
                cr_fixed = 0
                if not self.df_AC_Fixed.empty:
                    #mttr     = self.df_AC_Fixed.loc[asset_id].MTTR
                    cr       =  self.df_AC_Fixed.loc[asset_id].T_Cr
                    cr_fixed = cr 

                RI_df,df_con             = Compute_Ri_Df(asset,df,self.date_beg,self.N_days,cr_fixed)
        
                df_cf,PV                 = cash_flow(RI_df,self.R)
                df_cf.head()
                scenario[asset_id]       = {'RI':RI_df,'Con':df_con,'CF':df_cf,'PV':PV} 
        
            return scenario
