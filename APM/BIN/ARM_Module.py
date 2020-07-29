# # # # # # # # # # # # # # # # # # # # # # # #
#                                             # 
#           Module to assess risk             #
#               By: David Alvarez             #
#              09-08-2018                     #
#            Version Aplha-0.  1              #  
#                                             #
# # # # # # # # # # # # # # # # # # # # # # # #

import pandas as pd




class ARM():
    def __init__(self):
        self.Asset_Portfolio = 1
        self.load_growth     = 1

    def Energy_Suplied_By_Day(self,DF_NO,*argv):
        # -> DF_NO: Dataframe under normal operation 
        # -> DF_CO: Dataframe under contingencies  
        df = pd.DataFrame()
        l_EN    = []                # Energy Non puplied vector
        l_ES_NO = []
        l_ES_CO = {}
        l_DAY   = []
        l_HOUR  = []

        dict_case = {}
        n           = 0
        for df_case in argv:
            dict_case[n] = df_case
            l_ES_CO[n]   = []
            n           +=1

        for day in DF_NO['Day'].unique():
            for  hour in DF_NO['Hour'].unique():
                # Query 
                query = 'Day=="' +day + '" and Hour=="'+str(hour) +'"'
                # Energy supplied in normal operation
                es_no = DF_NO.query(query)    
                es_no = es_no['Load'].sum()
                l_ES_NO.append(es_no)
                # Energy supplied in contingency scenario operation
                for case in dict_case:
                    es_co = dict_case[case].query(query)    
                    es_co = es_co['Load'].sum() 
                    l_ES_CO[case].append(es_co)
                 # Energy not supplied
                l_EN.append(es_no-es_co)        
                l_DAY.append(day)
                l_HOUR.append(hour)


        dic_result = {'Day':l_DAY,'Hour':l_HOUR,'ES_NO':l_ES_NO}
        n = 0
        for case in dict_case:
            case_name               = 'ES_CO_'+str(n) 
            dic_result[case_name]   = l_ES_CO[case]
            n                      +=1

        df         = pd.DataFrame.from_dict(dic_result)
        return df

    def ENS_SAIDI_By_Day(self,df,Case):
        l_dic_day   = []
        l_dic_ens   = []
        l_dic_saidi = []
        for day in df['Day'].unique():
            l_ens_day     = 0
            l_saidi_day   = 0
            for  hour in df['Hour'].unique():
                query = 'Day=="' +day + '" and Hour=="'+str(hour) +'"'
                l_df         = df.query(query)
                e_no         = l_df['ES_NO'].values.sum()   # Normal operation 
                e_co         = l_df[Case].values.sum()      # Contingency
                ens          = e_no-e_co
                l_ens_day   += ens
                saidi        = ens/e_no
                l_saidi_day +=saidi

            l_dic_ens.append(round(l_ens_day,1))
            l_dic_saidi.append(round(l_saidi_day,2))
            l_dic_day.append(day)

        l_dic = {'day':l_dic_day,'ENS':l_dic_ens,'SAIDI':l_dic_saidi}
        df    = pd.DataFrame.from_dict(l_dic)

        return df

    
