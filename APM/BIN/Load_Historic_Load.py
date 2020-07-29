# # # # # # # # # # # # # # # # # # # # # # # #
#                                             # 
#       Clase para leer y clasificar          #
#         información de corriente            #
#            histórica de demanda             #
#           By: David Alvarez                 #
#              18-10-2018                     #
#              Version 0.1                    #
#                                             #
#           By: David Alvarez                 #
#              11-22-2018                     #
#              Version 0.2                    #
#            Current in per unit              #
# # # # # # # # # # # # # # # # # # # # # # # #
#           By: David Alvarez                 #
#              11-22-2018                     #
#           Version Alpha 0.2                 #
#           Any load                          #
# # # # # # # # # # # # # # # # # # # # # # # #
#           By: David Alvarez                 #
#              05-15-2019                     #
#           Version Alpha 0.5.1               #
#        Function load_Historical_Data        #
#             was created                     #
# # # # # # # # # # # # # # # # # # # # # # # #

import importlib

class One_day_data:
    def __init__(self, date, value):
        self.date  = date
        self.i_rms = value
         
class Historic_Data:
    def __init__(self, date, value, day_1,U_kV,I_BC,S_BC):
        self.date   = date
        self.i_rms  = value
        self.days   = day_1
        self.U_kV   = U_kV
        self.I_BC   = I_BC
        self.S_BC   = S_BC
         

class Load_Historic_Data:
    def __init__(self, date, value, days):
        #self.date   = date
        #self.i_rms  = value
        #self.val    = value
        self.days   = days
        
# # For shunt banks
# def Main_Historical_Data(File_Name,Base):
#     import csv
#     import json     
#     from datetime import datetime   
     
#     with open(File_Name, 'r') as Asset_Info:    
#         test_tra            = json.load(Asset_Info)
#         date                = []
#         value               = []
#         U_kV                = []
#         I_BC                = []
#         S_BC                = []
           
#         for test_data in test_tra:
#             date_str        = test_data['Sample_Date'] 
#             format_str      = '%d/%m/%Y %H:%M'           # The time format
#             datetime_obj    = datetime.strptime(date_str, format_str) 
#             date.append(datetime_obj)
#             l_pu            = float(test_data['I_BC'])/Base
#             value.append(l_pu)
            
#             U = float(test_data['U_kV'])
#             I = float(test_data['I_BC'])
#             S = float(test_data['S_BC'])
            
#             U_kV.append(U)
#             I_BC.append(I)
#             S_BC.append(S)
            
    
#     Monday                    = Sort_Data_By_Date(date,value,0)
#     Tuesday                   = Sort_Data_By_Date(date,value,1)
#     Wednesday                 = Sort_Data_By_Date(date,value,2)
#     Thursday                  = Sort_Data_By_Date(date,value,3)
#     Friday                    = Sort_Data_By_Date(date,value,4)
#     Saturday                  = Sort_Data_By_Date(date,value,5)
#     Sunday                    = Sort_Data_By_Date(date,value,6)
    
#     Day                       = {'Monday':Monday,'Tuesday':Tuesday,'Wednesday': Wednesday,'Thursday':Thursday,'Friday':Friday,'Saturday':Saturday,'Sunday':Sunday} 
        
#     asset                     = Historic_Data(date,value,Day,U_kV,I_BC,S_BC)
    
    
#     return asset


# For transformers and loads 
def Load_Historical_Data(tag,Base):
    
    import json     
    from datetime import datetime   
    
    import Load_Data as  Lod_data_module
    
    test_tra            = Lod_data_module.Loda_Historic_Data(tag)    # Load data    
    date                = []
    value               = []        
    for test_data in test_tra:
        date_str        = test_data['Sample_Date'] 
        format_str      = '%d/%m/%Y %H:%M'           # The time format
        datetime_obj    = datetime.strptime(date_str, format_str) 
        date.append(datetime_obj)
        i_pu            = float(test_data['Val'])/Base
        value.append(i_pu)

# Sort by day
    Monday                    = Sort_Data_By_Date(date,value,0)
    Tuesday                   = Sort_Data_By_Date(date,value,1)
    Wednesday                 = Sort_Data_By_Date(date,value,2)
    Thursday                  = Sort_Data_By_Date(date,value,3)
    Friday                    = Sort_Data_By_Date(date,value,4)
    Saturday                  = Sort_Data_By_Date(date,value,5)
    Sunday                    = Sort_Data_By_Date(date,value,6)
          
    Day                       = {'Monday':Monday,'Tuesday':Tuesday,'Wednesday': Wednesday,'Thursday':Thursday,'Friday':Friday,'Saturday':Saturday,'Sunday':Sunday} 
    data                      = Load_Historic_Data(date,value,Day)
    return data 

def Sort_Data_By_Date(DATE,VALUE,DAY_ID):

    import Historical_Load_Filtering as Load_Filtered
        
    Day   = One_day_data([],[])        
    l_n      = 0
    l_t      = []
    l_i      = []
    for n in range(len(DATE)-1):
        x = DATE[n]
        if x.weekday() == DAY_ID:
            l_date  = x.toordinal()
            l_t.append((x-x.fromordinal(l_date)).total_seconds()/3600.0)
            l_i.append(VALUE[l_n])
            if not x.toordinal() == DATE[l_n+1].toordinal():   
                Day.date.append(l_t)
                Day.i_rms.append(l_i)
                l_t = []
                l_i = []
        l_n +=1
    
    Day.Filt    = Load_Filtered.Main_Data_Filtering(Day)
    return Day  