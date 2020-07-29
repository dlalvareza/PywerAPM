# # # # # # # # # # # # # # # # # # # # # # # #
#                                             # 
#      Module to run real time contingencies  #
#        By: David Alvarez and Laura Cruz     #
#              09-08-2018                     #
#            Version Aplha-0.5.1              #  
#                                             #
#     Module inputs:                          #
#              -> File name                   #
# # # # # # # # # # # # # # # # # # # # # # # #

import pandapower as pp
import pandas as pd
import numpy as np

# Function for disconnect Assets from the system
def run_pp_load_flow(net_lf,Asset_type,Asset_id):
    # Disconnect Transformers
    if Asset_type=='TR':
        index = net_lf.trafo.loc[net_lf.trafo['name'] == Asset_id].index[0]
        net_lf.trafo.in_service[index] = False
    # Disconnect Lines     
    if Asset_type=='LN':
        indexL = net_lf.line.loc[net_lf.line['name'] == Asset_id].index[0]
        net_lf.line.in_service[indexL] = False       
    
    pp.runpp(net_lf)
    return net_lf

# Function for get the contingency analysis    
def ContingencyAnalysis(Netw):
    
    OverloadLines   =[]
    OverLoadTrafos  =[]
    OverVoltageBuses=[]
    OverLoad        =[]
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
    
def FunctionNet(data_file):    
    # Import network data
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
        coef        = day_data.Filt.fitt.coef_hat              # Fitting coeficients
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

# # # # # # # # # # # # # # # # # # # # # # # #
# # # # # # # # # # # # # # # # # # # # # # # #

class Real_Time_Contingencies:
# Run contingencies by a specific hour
    def Run_Load_Contingencies(self,Net,hour):
        load_flow                 = run_pp_load_flow(Net,self.Type,self.ID)
        l_table                      = ContingencyAnalysis(load_flow)
        return(l_table)
        
#  Sett contingiencies
    def Set_Contingencies(self,hour,*load_shed):
          import copy   
          Net                    = copy.deepcopy(self.net)
          df_hour                = self.forecast[self.forecast.Hour==hour]
          df_hour                = df_hour.drop(columns = 'Hour')
          df_hour                = df_hour.set_index('Name')
            
          load_factor = []
          for ind,row in Net.load.iterrows():
                lf = df_hour.loc[row['name']]['Val'] 
                try:
                    if not load_shed==():
                        l_shed_factor = load_shed[0][0][row['name']] 
                except:     
                       l_shed_factor = 1
                lf  = lf*l_shed_factor       
                load_factor.append(lf)
          #print(load_factor) 
          cond_new    = (Net.load['p_mw']*load_factor).sum()
          cond_base   = Net.load['p_mw'].sum()
            
          # Generation load factor
          g_f         = cond_new/cond_base
          Net.load['p_mw']       = Net.load['p_mw']*load_factor
          Net.load['q_mvar']     = Net.load['q_mvar']*load_factor
          Net.gen['p_mw']        = Net.gen['p_mw']*g_f
            
          # Run contingencies
          table                  = self.Run_Load_Contingencies(Net,hour)
          table['time']          = hour
          
          return table,Net                  
        
# Contingency report for each hour of the day    
    def Table_Of_Contingencies(self):
        
        from random import gauss
        import copy        
        n_hours = 24
        # Empty data frame
        df               = pd.DataFrame()
        
        #print(self.forecast)
        for hour in range(n_hours):
            table,net = self.Set_Contingencies(hour) 
            df                     = pd.concat([df,table], sort=False)
            
        return(df)

# Run at specific hour contingcies
    def Cont_by_hour(self,hour,*load_shedding):
        table,net           = self.Set_Contingencies(hour,load_shedding) 
        return (table,net) 

# Run 24 hours contingeincies         
    def Cont_all_day(self):  
        self.cont_df          = self.Table_Of_Contingencies()       
# Main file
    def __init__(self,data_file,Type,ID,load_tags,day):
        ##try:
            # Net data
            self.net                  = FunctionNet(data_file)
            self.Type               = Type 
            self.ID                     = ID
            # Forecasting methods
            self.forecast         = Forecating_Data(self.net,load_tags,day)
            # Getting contingencies table
            #self.cont_df          = self.Table_Of_Contingencies()
        ##except:
        ##    self.cont_df          = pd.DataFrame()
        ##    print('Error running contingencies') 




