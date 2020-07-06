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

import pandapower as pp
import pandas as pd
import numpy as np

import copy
import calendar
from time import time
import datetime

from inspyred import ec
import inspyred

import math
from random import Random


# Funtion to return the daily load growth 
def Load_Growth_By_Day(L_growth):
        daily_growth = pow(1+L_growth, 1/365)-1     # Daily growth rate
        
        def f_Load_Daily_Growth(ndays):         # Daily growth rate fuction 
            return pow(1+daily_growth,ndays)

        return  f_Load_Daily_Growth  

# Function for get the contingency analysis    
def ContingencyAnalysis(Netw):
    
    OverloadLines   =[]
    OverLoadTrafos  =[]
    OverVoltageBuses=[]
    AllOverloads    =[]
    # Bring all Buses
    for bus in Netw.res_bus.iterrows():
        indexb  = bus[0]
        vm_pu  = bus[1].vm_pu    
        # Select into the list of Energized Buses, the Busses which have certain values of voltage in p.u   
        #if  (vm_pu >1.1 or vm_pu < 0.9) and vm_pu !=nan:
        if  (vm_pu >1.1 or vm_pu < 0.9):
                # Generate the list of results in a dictionary
                temp_data = {'Name': Netw.bus.name[indexb],
                           'Type': 'BU',
                           'Serial': '0',
                           'Mag': vm_pu}
                OverVoltageBuses.append(temp_data)
                      
    for trafo in Netw.res_trafo.iterrows():
        indext  = trafo[0]
        loadingt = trafo[1].loading_percent 
        # Select into the list of Energized Transformer which have loading parameter higher than 100
        if loadingt>100:
            # Generate the list of results in a dictionary
            temp_data = {'Name': Netw.trafo.name[indext],
                           'Type': 'TR',
                           'Serial': '1',
                           'Mag': loadingt/100}
            OverLoadTrafos.append(temp_data)
                
    for line in Netw.res_line.iterrows():
        indexl  = line[0]
        loadingl = line[1].loading_percent
        # Select into the list of Energized Lines which have loading parameter higher than 100
        if loadingl>100:
            # Generate the list of results in a dictionary
            temp_data = {'Name': Netw.line.name[indexl],
                           'Type': 'LN',
                           'Serial': '2',
                           'Mag': loadingl/100}
            OverloadLines.append(temp_data)
            
    # Set a variable which have the results of all elements
    AllOverloads=OverVoltageBuses+OverloadLines+OverLoadTrafos
    df         =pd.DataFrame(AllOverloads)
    # Define the order of the variables in the dictionary
    if not df.empty:
        df   =df[['Serial','Name','Type','Mag']]
        df.set_index(['Serial'], inplace=True)
    
    return df
    
def Load_Net_Pandapower(data_file,pp_case=None):    
    # data_file -> File name which contains network data, if file name is none by default is load the CIGRE model 
    if data_file==None:
        import pandapower.networks as pn
        
        if pp_case==None: 
            net = pn.create_cigre_network_mv(with_der=False)
        elif pp_case == 'case33bw':
            net =  pn.case33bw()

            load_name = []
            s_val     = []
            for index, row in net.load.iterrows():
                load_name.append('load_'+str(row.bus)) 
                s_val.append(math.sqrt(row.p_mw**2+row.q_mvar**2))

            net.load.name   = load_name
            net.load.sn_mva = load_name   
            
            line_name =  []         
            for index, row in net.line.iterrows():
                line_name.append('line_'+str(row.from_bus)+'_'+str(row.to_bus)) 
            
            net.line.name   = line_name

        #index = net.switch.loc[net.switch['name'] == 'S1'].index[0]
        #net.switch.closed[index] = True                             # Is assumed that switch is closed by defaut
    else: 
        # Import network data using excel 
        data          = pd.read_excel(open(data_file, 'rb'), sheet_name='DATA')
        # Create Network
        net           = pp.create_empty_network(name = data.loc[0,'Name'],f_hz =data.loc[0,'f'],sn_mva=data.loc[0,'sb_mva'])
        # # # # # # # # # # # # # # # # # # Load elements # # # # # # # # # # #
        # Buses
        net.bus       = pd.read_excel(open(data_file, 'rb'), sheet_name='BUS')
        # Lines
        net.line      = pd.read_excel(open(data_file, 'rb'), sheet_name='LINE')
        # Load
        net.load      = pd.read_excel(open(data_file, 'rb'), sheet_name='LOAD')
    
        # External grid
        df = pd.read_excel(open(data_file, 'rb'), sheet_name='EXT_GRID')
        if not df.empty:
            net.ext_grid         = df
        # Generators 
        df = pd.read_excel(open(data_file, 'rb'), sheet_name='GEN')
        if not df.empty:
            net.gen           = df
        # Static generators 
        df = pd.read_excel(open(data_file, 'rb'), sheet_name='SGEN')
        if not df.empty:
            net.sgen           = df    
        # Transformers 
        df = pd.read_excel(open(data_file, 'rb'), sheet_name='TRAFO')
        if not df.empty:
            net.trafo         = df    

        # 3 winding transformer
        df = pd.read_excel(open(data_file, 'rb'), sheet_name='TRAFO3W')
        if not df.empty:
            net.trafo3w  = df
        
        # SWITCHES 
        df = pd.read_excel(open(data_file, 'rb'), sheet_name='SWITCH')
        if not df.empty:
            net.switch         = df

        # Shunt element
        df = pd.read_excel(open(data_file, 'rb'), sheet_name='SHUNT')
        if not df.empty:
            net.shunt          = df
    # Return network        
    return (net)

# Function to load forecatings
def Forecating_Data(net_lf,file,today):
    from Load_Historic_Load import Load_Historical_Data  
  
    
    data            = pd.read_excel(open(file, 'rb'), sheet_name='LOAD_TAGS') # Sheet with loads  tags
    data            = data.set_index('Name')
    
    load_names      = net_lf.load['name']
    df_col_name     = ['Name','Hour','Val']
    hour            = list(range(24))
    df              = pd.DataFrame(columns=df_col_name)
    df_by_load      = pd.DataFrame()
    
    for loads in load_names:                                   # Forecast model for each load
        tag         = data.loc[loads]['TAG']                   # Tag ID
        base        = data.loc[loads]['Base']                  # Power base
        test        = Load_Historical_Data(tag,base)           # Load historical data
        day_data    = test.days[today]                         # Day to analize
        #coef        = day_data.Filt.fitt.coef_hat              # Fitting coeficients
        f_forecast  = day_data.Filt.fitt.Load_Forecast_by_Day  # Function fitted
        
        # Load forecasting        
        l_t0        = day_data.i_rms[-1][0]                    # Initial load, at time 0
        load_forec  = f_forecast(l_t0,1)                       # Load forecasting result

        # update dataframe 
        df_by_load['Val']   = list(load_forec)                 # Assign data frame values
        df_by_load['Hour']  = hour
        df_by_load['Name']  = loads
        df                  = pd.concat([df,df_by_load],sort=True)
    return df


# Function to load forecatings
def Fourier_Fit(file):
    from Load_Historic_Load import Load_Historical_Data  
    
    data            = pd.read_excel(open(file, 'rb'), sheet_name='LOAD_TAGS') # Sheet with loads  tags
    data            = data.set_index('Name')
    
    #load_names      = net_lf.load['name']
    df_col_name     = ['Name','Hour','Val','Day']
    hour            = list(range(24))
    df              = pd.DataFrame(columns=df_col_name)
    df_by_load      = pd.DataFrame()

    for loads in data.index:                                   # Forecast model for each load
        tag         = data.loc[loads]['TAG']                   # Tag ID
        base        = data.loc[loads]['Base']                  # Power base
        hist_data   = Load_Historical_Data(tag,base)           # Load historical data
        #print(hist_data)
        for day in list(calendar.day_name):                    # Eval each week day
            day_data    = hist_data.days[day]                       # Day to analize
            #print(day_data)
            #coef        = day_data.Filt.fitt.coef_hat              # Fitting coeficients
            f_forecast  = day_data.Filt.fitt.Load_Forecast_by_Day  # Function fitted
        
            # Load forecasting        
            l_t0        = day_data.i_rms[-1][0]                    # Initial load, at time 0
            load_forec  = f_forecast(l_t0,1)                       # Load forecasting result
        # update dataframe 
            df_by_load['Val']   = list(load_forec)                 # Assign data frame values
            df_by_load['Hour']  = hour
            df_by_load['Name']  = loads
            df_by_load['Day']   = day
            df                  = pd.concat([df,df_by_load],sort=True)
    return df

# Function to allocate asset list
def Make_Asset_List(file):
    df            = pd.read_excel(open(file, 'rb'), sheet_name='ASSETS') # Sheet with loads  tags
    df            = df.set_index('Name')
    return df

# Function to allocate asset list
def User_Data_List(file):
    df            = pd.read_excel(open(file, 'rb'), sheet_name='LOAD_TAGS') # Sheet with loads  tags
    df            = df.set_index('Name')
    df            = df.drop(columns=['TAG', 'Base'])
    return df

# # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # #

class Real_Time_Contingencies:
# Main file
    def __init__(self,data_file,ID_Load_Tag_File,pp_case=None):
        try:
            # Net data
            self.net                = Load_Net_Pandapower(data_file,pp_case)
            self.load_forecast      = Fourier_Fit(ID_Load_Tag_File)
            self.asset_list         = Make_Asset_List(ID_Load_Tag_File)
            self.load_user          = User_Data_List(ID_Load_Tag_File)                        # Users data by load
            self.N_Users            = self.load_user['N_Users'].sum()
        except:
            self.cont_df          = pd.DataFrame()
            print('Error running contingencies') 

# Function for disconnect Assets from the system
    def Disconet_Asset(self,net,Asset_id, Service=False):
        #Asset_type = self.asset_list.loc[Asset_id].Type
        Asset_type    = self.asset_list.loc[Asset_id].Disc_Type
        asset_to_disc = self.asset_list.loc[Asset_id].Asset_To_Disconet
        net_lf     = copy.deepcopy(net)


        # Disconnect Transformers
        if Asset_type=='TR':
            #index = net_lf.trafo.loc[net_lf.trafo['name'] == Asset_id].index[0]
            index = net_lf.trafo.loc[net_lf.trafo['name'] == asset_to_disc].index[0]
            net_lf.trafo.in_service[index] = Service
        # Disconnect Lines     
        elif Asset_type=='LN':
            #index = net_lf.line.loc[net_lf.line['name'] == Asset_id].index[0]
            index = net_lf.line.loc[net_lf.line['name'] == asset_to_disc].index[0]
            net_lf.line.in_service[index] = Service       
        elif Asset_type=='SW':
            #index = net_lf.switch.loc[net.switch['name'] == Asset_id].index[0]
            index = net_lf.switch.loc[net.switch['name'] == asset_to_disc].index[0]
            net_lf.switch.closed[index]   = Service 
        elif Asset_type=='LO':
            #index = net_lf.load.loc[net.load['name'] == Asset_id].index[0]
            index = net_lf.load.loc[net.load['name'] == asset_to_disc].index[0]
            net_lf.load.in_service[index] = Service 

        return net_lf


# Function to filter forecast data frame
    def Forecast_Val_By_Day_By_Hour(self,Day,Hour):
        DF       = self.load_forecast
        df       = DF[DF.Hour==Hour]
        df       = df[df.Day==Day]
        df       = df.drop(columns = ['Hour','Day'])
        df       = df.set_index('Name')

        return df

#  Sett contingiencies
    def Update_Net_With_Load_Forecast(self,Net,DF,*load_shed):   
          l_net                    = copy.deepcopy(Net)
            
          load_factor = []
          for ind,row in l_net.load.iterrows():
                load_name =row['name']
                lf = DF.loc[load_name]['Val'] 
                try:
                    if not load_shed==():
                        l_shed_factor = load_shed[0][load_name] 
                    else:   
                        l_shed_factor = 1 
                except:     
                       l_shed_factor = 1
                lf  = lf*l_shed_factor       
                load_factor.append(lf)
          #print(load_factor) 
          cond_new    = (l_net.load['p_mw']*load_factor).sum()
          cond_base   = l_net.load['p_mw'].sum()
            
          # Generation load factor
          g_f         = cond_new/cond_base
          l_net.load['p_mw']       = l_net.load['p_mw']*load_factor
          l_net.load['q_mvar']     = l_net.load['q_mvar']*load_factor
          l_net.gen['p_mw']        = l_net.gen['p_mw']*g_f
              
          return l_net

# Load growth function 
    def Load_Growth_Update(self,growth_rate):
        self.f_growth_rate =  Load_Growth_By_Day(growth_rate)  

# Run Non-Contingencies case
    def Run_Case_Load_growth(self,net,L_growth,date_beg,hour=0,opt_load_sheeding=False):  
        ndays          = datetime.timedelta(hours=hour).days
        self.Load_Growth_Update(L_growth)  
        growth_rate    = self.f_growth_rate(ndays)
        print(growth_rate)
        return self.Run_Case_Base(net,growth_rate)
        #print('Dave')
# Run Non-Contingencies case
    def Run_Case_Base(self,net,growth_rate=1,opt_load_sheeding=False,day_list=None):
        df_sec       = pd.DataFrame()                   # Dataframe that return security margins results
        df_load      = pd.DataFrame()                   # Dataframe that return security margins results
        

        df_temp              = pd.DataFrame()
        df_temp_0            = pd.DataFrame()
        if day_list==None:
            day_list = list(calendar.day_name)

        for day in day_list:   # Loop for each day 
            print(day)
            for hour in range(24):            # Loop for each hour
                df_load_forecast     = self.Forecast_Val_By_Day_By_Hour(day,hour)       #Load forecast filtered
                net_lf               = self.Update_Net_With_Load_Forecast(net,df_load_forecast)  # Update network with forecast
                net_lf.load.scaling  = growth_rate  
                net_lf.gen.scaling   = growth_rate              
                pp.runpp(net_lf)                                                                 # Run load flow with pandapower

                if opt_load_sheeding:
                    dave = RTC(net_lf)
                    net_lf = dave.Main_Load_Shedding_Opt()
                # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #    
                # # # # # # # # # Security margins dataframe  # # # # # # # #
                # Lines data frame
                df_temp_0            = pd.DataFrame()
                df_temp_0['Loading'] = net_lf.res_line['loading_percent']
                df_temp_0['Load']    = (net_lf.res_line['p_from_mw']**2+net_lf.res_line['q_from_mvar']**2).pow(1./2)
                df_temp_0['Name']    = net_lf.line['name']
                df_temp_0['Type']    = 'LN'
                # Transformer data frame
                df_temp              = pd.DataFrame()
                df_temp['Loading']   = net_lf.res_trafo['loading_percent']
                df_temp['Load']      = (net_lf.res_trafo['p_hv_mw']**2+net_lf.res_trafo['q_hv_mvar']**2).pow(1./2)
                df_temp['Name']      = net_lf.trafo['name']
                df_temp['Type']      = 'TR'

                # Concatenate
                df_temp              = pd.concat([df_temp,df_temp_0],ignore_index=True)

                # Bus data frame
                df_temp_0            = pd.DataFrame()
                df_temp_0['Loading'] = net_lf.res_bus['vm_pu']
                df_temp_0['Load']    = net_lf.res_bus['p_mw']
                df_temp_0['Name']    = net_lf.bus['name']
                df_temp_0['Type']    = 'BUS'
                # Concatenate
                df_temp              = pd.concat([df_temp,df_temp_0],ignore_index=True)

                # Add to dataframe the day and hour
                df_temp['Day']       = day
                df_temp['Hour']      = hour
                # Final concatenation
                df_sec                   = pd.concat([df_sec,df_temp],ignore_index=True)
                
                # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #    
                # # # # # # # # # # # # # Load data frame  # # # # # # # #
                df_load_temp            = pd.DataFrame() 
                df_load_temp['Name']    = net_lf.load['name']
                df_load_temp['Load']    = (net_lf.res_load['p_mw']**2+net_lf.res_load['q_mvar']**2).pow(1./2)              
                df_load_temp['Day']     = day
                df_load_temp['Hour']    = hour
                df_load                 = pd.concat([df_load,df_load_temp],ignore_index=True)
        return df_sec,df_load

# Run load flow
    def Run_Load_Flow(self,net,day,hour,asset_status,growth_rate=1):

            run_lf = False
            if True in asset_status.values():                                           # Check if some asset is disconect
                df_load_forecast     = self.Forecast_Val_By_Day_By_Hour(day,hour)       #Load forecast filtered
                net_lf               = self.Update_Net_With_Load_Forecast(net,df_load_forecast)  # Update network with forecast
                
                net_lf.load.scaling  = growth_rate  
                net_lf.gen.scaling   = growth_rate   


                for asset in asset_status:                                              # Disconnet assets 
                    if asset_status[asset] ==True:
                        run_lf               = True
                        net_lf               = self.Disconet_Asset(net_lf,asset)
            
            df   = pd.DataFrame()                                                       # Empty dataframe
            ENS   = 0
            SAIDI = 0
            if run_lf:
                N_Users = self.N_Users
                try:
                    #print('Running Flow')
                    pp.runpp(net_lf)                                                        # Run load flow with pandapower
                    df                   = ContingencyAnalysis(net_lf)                      # Check contingencies

                    load_cut  = round(net_lf.load.p_mw.sum()*growth_rate-net_lf.res_load.p_mw.sum(),3)  # Check if loading was cutting
                    if not df.empty:        # Security margins are violeted
                        ENS = net_lf.load.p_mw.sum()      
                        SAIDI = 1
                    elif load_cut>0:               
                        ENS = load_cut
                        for index, row  in net_lf.load.iterrows():
                            #print(row)
                            load_name = row['name']
                            p_exp = row.p_mw*row.scaling
                            p_sup = net_lf.res_load.loc[index].p_mw
                            users_by_load = self.load_user.loc[load_name].N_Users
                            p_ratio = (p_exp-p_sup)/p_exp
                            SAIDI   += p_ratio*users_by_load/N_Users
                    SAIDI = round(SAIDI,5)

                except:          # If the load flow don't converge
                    ENS   = net_lf.load.p_mw.sum()
                    SAIDI = 1
                
            return ENS,SAIDI

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                           #
#              Optimization of contingencies using PSO                      #
#                                                                           #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #



class RTC_inspyred_Settings():

    def __init__(self, dimensions=2):
        self.dimensions = dimensions
        self.bounder = ec.Bounder([0] * dimensions, [1] * dimensions)
        self.maximize = False
        # Load real tiem contingecies module
        self.sample     = RTC()
    def generator(self, random, args):
        return [random.uniform(0, 1) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            fitness.append(self.sample.cost_function(c))
        return fitness  


class RTC():

    TR_Penalty     = 2000
    LN_Penalty     = 2000
    BUS_Penalty    = 2000
        
    def __init__(self,Net):

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # Run first contingencies # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        # Create default dictionary of loads
        self.Net      = Net
        self.dict_loads = {name:1 for name in self.Net.load['name'].values}


    def Update_Load_Shedding(self,load_she_fac):
        up_net                    = copy.deepcopy(self.Net)
        for idx, row in up_net.load.iterrows():
            load_name = row['name']
            up_net.load.loc[idx,'p_mw']   = up_net.load.loc[idx,'p_mw']*load_she_fac[load_name]
            up_net.load.loc[idx,'q_mvar'] = up_net.load.loc[idx,'q_mvar']*load_she_fac[load_name]
        return(up_net)    


    def Main_Load_Shedding_Opt(self):
        self.objetive_load   = self.Net.res_load['p_mw'].sum()      # Allocate objetive load
        # Load optimization problem settings 
        problem   = RTC_inspyred_Settings(self.cost_function,len(self.Net.res_load['p_mw']))
        # Run optmization 
        result    =  Inspyred_Main(problem,display=True)   

        x = result.candidate
        n = 0
        load_she_fac  = {}
        for load in self.dict_loads:
            load_she_fac[load]  = x[n]
            n += 1
   
        l_net_cont              = self.Update_Load_Shedding(load_she_fac)
        pp.runpp(l_net_cont)
        return (l_net_cont)

    # Cost function 
    def cost_function(self,x):
        n = 0
        load_she_fac  = {}
        for load in self.dict_loads:
            load_she_fac[load]  = x[n]
            n += 1

        # Update contingency with load shedding
        l_net_cont = self.Update_Load_Shedding(load_she_fac)
        # Load flow under contingency with load shedding
        pp.runpp(l_net_cont)
        # Table of contingencies
        df                   = ContingencyAnalysis(l_net_cont)
        # Eval of the cost function
        cost             = abs(self.objetive_load-self.Penalty_Function(l_net_cont,df))
        return cost

    
# # # # # # # # # # # # # # # Total Load# # # # # # # # # # # # # # # # # # # # #

    def Penalty_Function(self,net,const_violations):            
        # Compute the total load 
        load     = net.res_load['p_mw'].sum()
        if not const_violations.empty:
          const_violations.set_index('Name', inplace=True)
          for index, row in const_violations.iterrows():
               if const_violations.loc[index,'Type']=='BU':
                   load=load+self.BUS_Penalty
               if const_violations.loc[index,'Type']=='TR':
                   load=load+self.TR_Penalty
               if const_violations.loc[index,'Type']=='LN':
                   load=load+self.LN_Penalty
        
        return load

class RTC_inspyred_Settings():

    def __init__(self,COST_FUNCTION, dimensions=2):
        self.dimensions = dimensions
        self.bounder = ec.Bounder([0] * dimensions, [1] * dimensions)
        self.maximize = False
        # Load real tiem contingecies module
        self.cost_function     = COST_FUNCTION
    def generator(self, random, args):
        return [random.uniform(0, 1) for _ in range(self.dimensions)]
        
    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            fitness.append(self.cost_function(c))
        return fitness



def Inspyred_Main(problem,prng=None, display=False):
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    
    ea = inspyred.swarm.PSO(prng)
    ea.terminator = inspyred.ec.terminators.evaluation_termination
    ea.topology      = inspyred.swarm.topologies.ring_topology
    final_pop = ea.evolve(generator=problem.generator,
                          evaluator=problem.evaluator,
                          #evaluator=inspyred.ec.evaluators.parallel_evaluation_mp,                       
                          #mp_evaluator=problem.evaluator,
                          #pop_size=50,
                          pop_size=40,
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          max_evaluations=2000,
                          #max_evaluations=1000, 
                          neighborhood_size=10)

    if display:
        best = max(final_pop) 
        print('Best Solution: \n{0}'.format(str(best)))
    #return ea
    return max(final_pop) 