# # # # # # # # # # # # # # # # # # # # # # # #
#                                             # 
#      Module to run real time contingencies  #
#        By: David Alvarez and Laura Cruz     #
#              09-08-2018                     #
#            Version Aplha-0.  1              #  
#                                             #
#     Module inputs:                          #
#              -> File name                   #
# # # # # # # # # # # # # # # # # # # # # # # #

import pandas as pd
import random
from scipy.interpolate import interp1d
import calendar
import numpy as np
import datetime

from APM_Module_Tools import Fitt_constants_HI,Read_Table
from APM_Module_Regulatory import APM_Regulatory                    # Import regulatory class
from ACM_Module import ACM                                          # Criticality module

# Function to allocate asset list
def Read_Table_Conditions(DB_name,table,row,ID,source_type='Excel'):
    if source_type=='Excel':
        df            = pd.read_excel(open(DB_name, 'rb'), sheet_name=table) # Sheet with loads  tags
        df            = df[df['Serial']==ID] 
        columms       = ['Test_ID', 'Date', row]
        df            = df[columms]
        df            = df.rename(columns = {row:'Val'})
        df            = df.dropna()
    return df
# Function to allocate asset data
def Read_Asset_Data(DB_name,table,ID,source_type='Excel'):
    if source_type=='Excel':
        df            = pd.read_excel(open(DB_name, 'rb'), sheet_name=table) # Sheet with loads  tags
        df            = df[df['Serial']==ID] 
    return df

def Load_Asset_Portfolio(file,table):
    df            = pd.read_excel(open(file, 'rb'), sheet_name=table) # Sheet with loads  tags
    df            = df.set_index('ID')
    return df

class APM():
    def __init__(self,case_sett,load_growth):
        
        if 'path' in case_sett.keys():
            self.case_path  =  case_sett['path']
        else:
            self.case_path   = ''     
        # Asset porfolio source
        source = case_sett['portfolio_source']
        

        self.Asset_Portfolio_List = Load_Asset_Portfolio(source,'ASSETS')
        self.Asset_Location       = Load_Asset_Portfolio(source,'LOCATIONS')
        asset = {}                                        # create Dictionary of Assets

        #db_structure = case_sett['database_sett']
        for id,row in self.Asset_Portfolio_List.iterrows():
            #asset[id] = Asset_M(row,id,db_structure)
            asset[id] = Asset_M(row,id,case_sett,self.case_path)
        self.Asset_Portfolio = asset
        self.load_growth     = load_growth

    def Compute_All_AM_Index(self,date):
        for id in self.Asset_Portfolio:
            self.Asset_Portfolio[id].AM_Index(date)   

    def POF_Status(self):
        assets = self.Asset_Portfolio
        fail = {}         
         
        for id in assets:
            fail_succes = random.random() 
            asset       = assets[id]
            pof         = asset.pof_2
            if asset.fail==True:
                 asset.time_fail +=1
                 if asset.time_fail>asset.mttr:   # Check if the asset was repaired
                     asset.fail      =False
                     asset.time_fail =0
            elif fail_succes <= pof:          # Dictinary with desconections 
                asset.fail=True
                asset.time_fail =1
            
    
            fail[asset.name]=asset.fail
        return fail    

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def Risk_Index_During_Time(self,Cont,date_beg,n_hours,trail,df_pof=pd.DataFrame()):
        cr_obj = ACM(Cont.load_user,Cont.gen_data)                  # Criticality object, create
        
        date_beg = datetime.datetime.fromordinal(date_beg.toordinal())
        res = []
        for n in range(n_hours):    
            date = date_beg+ datetime.timedelta(hours=n)    
            l_date = date.date()
            h                      = n%24
            if h==0: 
                if df_pof.empty:                             
                    self.Compute_All_AM_Index(l_date)                     # Update performance index 
                else:                                                              
                    for l_id in self.Asset_Portfolio:                     # pof was compute previusly 
                        self.Asset_Portfolio[l_id].pof_2 = df_pof.loc[l_date][l_id]

            '''Asset_status = self.POF_Status()                                 # POF matrix
            day_name     = calendar.day_name[date.weekday()] 
            h            = n%24
            n_days       = datetime.timedelta(hours=n).days
            growth_rate  = Cont.f_growth_rate(n_days)                      # Growth rate at day n
            Cr,SAIDI    = Cont.Run_Load_Flow(Cont.net,day_name,h,Asset_status,growth_rate=growth_rate)
            

            # Review review 
            #if Cr >0:
            if True in Asset_status.values():
                Asset_status['Date']   = date
                Asset_status['Cr']     = Cr
                Asset_status['SAIDI']  = SAIDI
                Asset_status['Ite']    = trail
                res.append(Asset_status)'''

            Asset_status = self.POF_Status()                                 # POF matrix

            if True in Asset_status.values():
                day_name               = calendar.day_name[date.weekday()] 
                n_days                 = datetime.timedelta(hours=n).days
                growth_rate            = Cont.f_growth_rate(n_days)                      # Growth rate at day n
                ENS,SAIDI,ENG,BEN      = Cont.Run_Load_Flow(Cont.net,day_name,h,Asset_status,cr_obj,growth_rate=growth_rate)  
                # Update data              
                Asset_status['Date']   = date
                #Asset_status['ES']     =
                Asset_status['ENS']    = ENS
                #Asset_status['gen']    = PUR_EN  
                Asset_status['Cr']     = -BEN
                Asset_status['SAIDI']  = SAIDI
                Asset_status['Ite']    = trail
                res.append(Asset_status)

        return res

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
#                       Eval HI without data                                #         
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def HI_Replace():
    x        = np.array([0,20,25,45])
    y        = np.array([0,0.1,0.35,0.99])
    fit_f    = Fitt_constants_HI(x,y)
    return fit_f

# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                       #
#                       Asset Class                     # 
#                                                       # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #

class Asset_M():
    def __init__(self,data,id,db,path):
        # id -> Asset id
        # db -> dbase structure name
        self.case_path  =  path
        
        self.db        = db
        db_struc       = db['database_sett']#db
        
        #self.decision  = None                 # List of decisions 
        self.decision  =pd.DataFrame() 

        self.id        = id
        self.name      = data.Name
        self.type      = data.Type
        self.mttr      = data.MTTR
        self.inc       = data.Incomes
        self.capex     = data.CAPEX
        self.opex      = data.OPEX
        self.fail      = False
        self.time_fail = 0                       # Asset time failed
        #self.oper_date = datetime.date(1980, 1, 1)

        self.hi_rem        = HI_Replace()         # Function to estimate the HI of a new asset 

        #DB_Model            = self.Load_DB_Model(db)
        DB_Model            = self.Load_DB_Model(db_struc)
        HI_Weigths          = self.Weights()
        HI_Con_Limits       = self.Load_Cond_Limits()

        # Load constant data 
        #->data = Read_Table(db['database_Cons_Set'])
        #'Cons'
        #->data = Read_Table(data['Cons']['DB_Name'])
        #->l_AL = data[self.type]    # Average life in years
        

        # Load condition 
        self.cond  = self.Load_Condition(DB_Model,HI_Weigths,HI_Con_Limits) 

        # Lambda function 
        self.lambda_f      = self.Load_Lambda_Constants()

        # Load asset data 
        self.data         = self.Load_Asset_Data(DB_Model)

        self.reset_init()
        # Regulatory conditions
        self.apm_reg      = APM_Regulatory(self.db,self.data)

    def reset_init(self):
        # # # # # # # # # # # # # # #
        self.r            = None
        self.pof          = None 
        self.pof_2        = None
        self.r            = None 
        self.lambda_k     = None   
        self.elap_life    = None
        # Cumulative lambda
        self.sum_lambda   = 0      

    def Load_Asset_Data(self,Model):
        date_base_name =  Model['DB_Name']
        df = Read_Asset_Data(date_base_name,self.type,self.id)
        dic =  df.to_dict('r') 
        dic = dic[0]
        dic['Opt_Year'] = datetime.date(dic['Opt_Year'], 1, 1)

        return dic

    def Load_Condition(self,Model,Condition,HI_Limits):
        date_base_name =  Model['DB_Name']
        tables         =  Model['Tables']
        dict_condition = {}
        w_t            = 0          # Total weights of conditions defined by the model
        sum_w          = 0
        self.re        = 0

        for System in Condition:
            for cond in Condition[System]:
                table                = tables[cond]
                df                   = Read_Table_Conditions(date_base_name,table,cond,self.id)
                w_t                  += Condition[System][cond]
                if not df.empty:
                    w                    = Condition[System][cond]
                    sum_w                += w
                    con_limits           = HI_Limits[cond]
                    dict_condition[cond] = Asset_Condition(df,w,con_limits)

                self.re            = sum_w/w_t    # ri ->Reliability index
                self.w_total       = sum_w        # Sum of total weight available conditions
        return(dict_condition)


    def Load_DB_Model(self,db_struc):
        data  = Read_Table(db_struc)
        data  = data[self.type]
        return data

    def Weights(self):
        t_name = self.case_path+'APM/DATA/TABLES/Asset_HI_Weights.json' 
        data = Read_Table(t_name)
        data = data[self.type]
        return data

    def Load_Cond_Limits(self):
        t_name = self.case_path+'APM/DATA/TABLES/Asset_Condition_Limits.json'
        data = Read_Table(t_name)
        data = data[self.type]
        return data

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
    def Load_Lambda_Constants(self,case='Con_1'):
        t_name = self.case_path+'APM/DATA/TABLES/Asset_Lambda_Factors.json'    
        data  = Read_Table(t_name)
        #data  = Read_Table('APM/DATA/TABLES/Asset_Lambda_Factors.json')
        data  = data[self.type]
        data  = data[case]
        a,b,c = data['a'],data['b'],data['c']

        def compute_lambda(HI):
            if HI==None:
                return None
            else:    
                return a*np.exp(b*HI)+c
            
        return compute_lambda

    def Eval_Asset_Condition(self,date,desc_date=None):  
        #
        condition = self.cond

        sum_sw = 0
        sum_w = 0

        if desc_date==None or date<desc_date:   # Check if a decision is planned to be performed 
            for n in condition:
                S = condition[n].eval_cond_fit_func(date)
                w = condition[n].w
                sum_sw +=S*w
                sum_w  +=w

            if sum_w==0:
                hi  = None
            else:
                hi  = sum_sw/sum_w               # Weighted Health index
        else:
            delta_years = (date-desc_date).days/365.25
            hi = self.hi_rem(delta_years)

        self.date_con_eval = date
        return hi
        
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #       
    def HI(self,date,freq='hour',hi=True):
        desc_date = None
        if not self.decision.empty:
            desc_date        = self.decision['Date'].values[0]

        # # # # # # # # # # # # # # # # # # # # # # # # # #
        if  hi:    # Compute and update the health index
            self.hi          = self.Eval_Asset_Condition(date,desc_date=desc_date)
        #else: 
        #    self.hi = hi
        # # # # # # # # # # # # # # # # # # # # # # # # # #

        if self.hi != None:
            lambda_k         = self.lambda_f(self.hi)   # Failure rate in times per year
            if freq=='hour':
                lambda_freq  =  8760            # Number of hours of a year

            self.lambda_k    = lambda_k/lambda_freq
            self.sum_lambda  +=  self.lambda_k

 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #       
    def POF(self):    
        self.r            = np.exp(-self.sum_lambda )
        self.pof          = 1-self.r 

        self.pof_2        = 1-np.exp(-self.lambda_k)

    def RL(self,date):
        l_curr_year    = date.year
        l_opt_year     = self.data['Opt_Year'].year
        data = Read_Table(self.db['database_Cons_Set'])
        #'Cons'
        data           = Read_Table(data['Cons']['DB_Name'])        # Data bases with average lifes
        l_AL           = data[self.type]                            # Average life in years

        if self.type =='AUX':
            if 'Discharge' in self.cond:
                self.elap_life = self.cond['Discharge'].eval_cond_fit_func(date)
        else:
            self.elap_life = (l_curr_year - l_opt_year)/l_AL
        # Regulatory life
        self.apm_reg.Regulatory_EL(l_curr_year,l_opt_year)     
 # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #  

    def AM_Index(self,date,compu_hi=True):      # Compute asset management idex
        self.HI(date,hi=compu_hi)

        if self.hi != None:
            self.POF()
        self.RL(date)             # Remaining life 

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #  
#           Fuction to eval the POF and R in a period of time               #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #  
    
    def POF_R_Assessment(self,date_beg,n_hours):
        self.reset_init()                   # Reset scenario
        pof,r,hi,lambda_k,date,sum_lambda,pof_2 = [],[],[],[],[],[],[]

        #sum_lambda = 0
        for n in range(n_hours):
            test_Date = date_beg+ datetime.timedelta(hours=n)
            
            hour = n%24
            if n%24 == 0:     # The health index is assumed same during an entire day
                compu_hi = True
            else:
               compu_hi = False 
            
            self.AM_Index(test_Date,compu_hi=compu_hi)
            date.append(test_Date)
            pof_2.append(self.pof_2)
            if self.hi !=None:
                pof.append(self.pof*100)
                r.append(self.r*100) 
                hi.append(self.hi)
                lambda_k.append(self.lambda_k*8760)
                sum_lambda.append(self.sum_lambda)
            else:
                pof.append(self.pof)
                r.append(self.r) 
                hi.append(self.hi)
                lambda_k.append(self.lambda_k)
                sum_lambda.append(self.sum_lambda)
            
                
        results_dic = { 'Date':date,
                        'HI':hi,
                        'POF':pof,
                        'pof_2': pof_2, 
                        'R':r,
                        'sum_lambda':sum_lambda,
                        'lambda':lambda_k}

        df          = pd.DataFrame.from_dict(results_dic)
        return df

# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                       #
#                   Asset Condition                     # 
#                                                       # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #


class Asset_Condition():
    def __init__(self,DF,W,limits,con='Cond 1'):
        self.w             = W
        self.limits        = limits[con]
        self.eval_cond_f   = self.eval_condition_function()    
        self.historic_data = self.Update_Data_Frame(DF)
        self.forecast_f    = self.HI_Forecast_Fitt_Function(self.historic_data)


# Fitting exponetial grown using historical condition records
    def HI_Forecast_Fitt_Function(self,df):
        if len(df)>0:
            #df = df.sort('Date')
            df                = df.sort_values(by=['Date'])
            date              =df['Date'].dt.date.values
            self.opt_date     = date[0]-datetime.timedelta(days=365*5)
            x                 =  np.asarray([(x - self.opt_date).days/365.25 for x in date])
            y                 = df['val_nor'].values
            
            x_end      = x[-1]+35                      # Assume 35 years as end of life
            # Add initial and final contion last values 
            x =  np.concatenate(([0], x, [x_end]))
            y =  np.concatenate(([0], y, [1]))

            fit_f   = Fitt_constants_HI(x,y)
        return fit_f

# Eval constion using the fitted function
    def eval_cond_fit_func(self,date):
        #x = (date.date() - self.opt_date).days/365        # Date to eval in years
        x = (date - self.opt_date).days/365.25        # Date to eval in years
        #print(date)
        #x = (date.date() - self.opt_date).days/365        # Date to eval in years
        y = self.forecast_f(x) 
        return y

    def Update_Data_Frame(self,df):
        con_n = []
        for val in df.Val.values:
            val_norm = self.eval_cond_f(val)
            con_n.append(float(val_norm))
        df['val_nor'] =  con_n               # Add condition assessment to the historic dataframe
        return df

    def eval_condition_function(self):
        x     = self.limits 
        #y     = [0,0.25,0.5,0.75,1]
        y = np.linspace(0, 1, len(x), endpoint=True)


        low   = y[0]
        upp   = y[-1]
        if x[0]>x[1]:
            low   = y[-1]
            upp   = y[0]
        return interp1d(x, y,fill_value=(low, upp), bounds_error=False)
