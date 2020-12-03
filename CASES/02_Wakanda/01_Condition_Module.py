print('The platform is running')
 

 # Path to the main functions
import sys
sys.path.insert(0,'WEB_APP/')
sys.path.insert(0,'APM/BIN/')

import pandas as pd
from datetime import datetime
import numpy as np


# # # # # # # # # # # # # # # # # # # # # # #    

from APM_Run import run_condition, Generate_Report_Condition, load_codition

data_APM_df,report_date,assets    = run_condition()


data_APM_df,report_date,df_porf   = load_codition()
Generate_Report_Condition(assets)




