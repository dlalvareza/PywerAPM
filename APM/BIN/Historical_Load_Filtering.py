# # # # # # # # # # # # # # # # # # # # # # # #
#                                             # 
#       Clase para filtrar por día            #
#         información de corriente            #
#            histórica de demanda             #
#           By: David Alvarez                 #
#              18-10-2018                     #
#                                             #
# # # # # # # # # # # # # # # # # # # # # # # #
class Return_Data:
     def __init__(self, rms, mean,std,fitt):
         self.date  = rms
         self.mean  = mean
         self.std   = std
         self.fitt  = fitt
		 
def Main_Data_Filtering(Transformer_Data):
     import numpy as np
     i_rms              = []
     i_mean             = []
     i_std              = []
     #for n in range(len(Transformer_Data.date[1])):
     for n in range(24):
        Value              = []
        
        for irms in Transformer_Data.i_rms:
           if n<len(irms):
              Value.append(irms[n])
        i_mean.append(np.mean(Value))
        i_std.append(np.std(Value))
        i_rms.append(Value)        
     
	 # Fitting
     import Load_Function_Fitting
     hour          = np.linspace(0,len(i_mean),num = len(i_mean),endpoint=False)
     Fitt          = Load_Function_Fitting.Load_Fitt(hour,i_mean)

	 
     l_data        = Return_Data(i_rms,i_mean,i_std,Fitt)
     return l_data 
   
