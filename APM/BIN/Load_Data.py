# # # # # # # # # # # # # # # # # # # # # # # #
#                                                                                              # 
#              Class to read ENEL historical data                     #
#                       By: David Alvarez                                         #
#                            29-May-2019                                           #
#                              Version 0.4.4                                          #
#                                                                                             #  
# # # # # # # # # # # # # # # # # # # # # # # #



# Acces to PI-System
#import ConnPy as PI_Conection


import json

# Functions 
def Loda_Historic_Data(tag_id):         
    #if sett.pi_conection:
    if None:
        test_tra   = PI_Conection.Datos_interpolados(sett.pi_time_start,sett.pi_time_end,tag_id,sett.pi_time_interval)
    else:
        try:
            with open(tag_id, 'r') as Trafo_Info:    
               test_tra = json.load(Trafo_Info)
        except:
            print('Error Loading historical load data')
            tag_id     = 'IAMS/03_Data/XX_Test_Info/Test_Load.json'
            with open(tag_id, 'r') as Trafo_Info:    
                test_tra = json.load(Trafo_Info)
    return(test_tra)
   
