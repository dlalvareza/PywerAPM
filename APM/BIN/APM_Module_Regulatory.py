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

import datetime
import calendar

#import calendar
import json
from APM_Module_Tools import Read_Table
class APM_Regulatory():
    def __init__(self,DB,Asset_Data):

        l_UC           = Asset_Data['UC']


        self.db       =   DB
        self.reg_life =  self.Regulatory_life(l_UC)
        #self.reg_EL   = date.year
    def Regulatory_life(self,UC):
        db         = Read_Table(self.db['database_Cons_Set'])
        data       = Read_Table(db['REG']['DB_Name'],Type='Excel',sheet='UC_Life')
        l_rl       = data[data['Name']==UC].Life.values[0] # Regulatory life
        return l_rl
    # Regulatory life    
    def Regulatory_EL(self,Current_Year,Opt_Year):
        self.reg_el = (Current_Year-Opt_Year)/self.reg_life

