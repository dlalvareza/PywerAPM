# # # # # # # # # # # # # # # # # # # # # # # #
#                                             # 
#      Module with toos for processing data   #
#           By: David L. Alvarez              #
#               09-10-2020                    #
#            Version Aplha-0.1                #  
#                                             #
# # # # # # # # # # # # # # # # # # # # # # # #


import pandas as pd
import numpy as np
###############################################################################
import geopandas
import contextily as ctx
from shapely import wkt


#from 
def Report_APM_df(Assets,date_beg,Type=None,N_hours=0):
    df = Assets.Asset_Portfolio_List
    if Type==None:
        asset_list = df
    else:
        asset_list = df[df['Type']==Type]

    asset_list = list(asset_list.index)

    data_dic         = {}
    data_dic['Year'] = [Assets.Asset_Portfolio[n].data['Opt_Year'].year for n in asset_list]
    data_dic['Name'] = [Assets.Asset_Portfolio[n].name for n in asset_list]
    data_dic['RE']   = [Assets.Asset_Portfolio[n].re for n in asset_list]

    data_dic['Type'] = [Assets.Asset_Portfolio[n].type for n in asset_list]

    hi = []
    for  n in asset_list:
        df = Assets.Asset_Portfolio[n].POF_R_Assessment(date_beg,1)
        if len(df['HI'].values)==0:
            hi.append(None)
        else:
            hi.append(df['HI'].values[-1])

    data_dic['HI']    = hi
    data_dic['year']  = date_beg.year
    data_dic['EL']    = [Assets.Asset_Portfolio[n].elap_life for n in asset_list]
    data_dic['R_EL']  = [Assets.Asset_Portfolio[n].apm_reg.reg_el for n in asset_list] 
    # Location 
    data_dic['Loc']   =  [Assets.Asset_Portfolio[n].data['Location'] for n in asset_list]
    data_dic['Lat']   =  [Assets.Asset_Location[Assets.Asset_Location.index==Assets.Asset_Portfolio[n].data['Location']].Lat.values[0] for n in asset_list]
    data_dic['Lon']   =  [Assets.Asset_Location[Assets.Asset_Location.index==Assets.Asset_Portfolio[n].data['Location']].Lon.values[0] for n in asset_list]

    # Return dataframe  
    df     = pd.DataFrame.from_dict(data_dic)
    
    df     = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.Lat, df.Lon), crs="EPSG:4326")

    df = df.to_crs(epsg=3857)
    df['Loc_x']  =df.geometry.values.x 
    df['Loc_y']  =df.geometry.values.y
    return df

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #


def Report_APM_Meta_data(df,year):
    data = {
            'N_asset': df.index.size,
            'OL'     : round((year-df['Year']).mean(),1),
            'RL'     : round(df['EL'].mean()*100,1),
            'BRA'    : 0,
            'HI'     : round(df['HI'].mean()*100,1),
            'R_EL'   : round(df['EL'].mean()*100*0.37,1),
            'RE'     : round(df['RE'].mean()*100,1),
            }


    return data 

def Report_ACM_Meta_data(DF,year):
    df = DF[DF.Year==year]
    print(DF)
    print(df)
    data = {
            'Cr'     : round(df['Cr'].sum(),1),
            'RI'     : round(df['RI'].sum(),2),
            'A'      : round(df['A'].mean(),3),
            'SAIDI'  : round(df['SAIDI'].sum(),3),
            'ENS'    : round(df['ENS'].sum(),2),
            }


    return data 

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def Report_ACM_df(DF,Asset_dF,year_list,N,Type=None,Factor='GWh'):

    #->if Type==None:
    #->    asset_port = Asset_List.Name.values.tolist()
    #->else:
    #->    asset_port  = Asset_List[Asset_List['Type']==Type] 
    #->    asset_port  = asset_port.Name.values.tolist()
    #->    N -> Number of montecarlo trials

    data_dic     = {}
    pof_dic      = []
    ens          = []
    ri_dic       = []
    asset_name   = []
    year_val     = []
    mttr_dic     = []
    cr_dic       = []
    a_dic        = []
    saidi_dic    = []
    y_beg        = min(DF.Date.dt.year)-1

    for asset_id in  Asset_dF.index:
        asset  = Asset_dF.loc[asset_id]
        for year in year_list:
            df_by_year         = DF[DF.Date.dt.year<=year]
            df_asset           = df_by_year[df_by_year[asset.Name]==True]                 # Check if the asset fail
            mttr               = asset.MTTR
            trials             = 24*365.25*(year-y_beg)*N
            D_time             = 24*365.25*(year-y_beg)/mttr                           # Cumulative years
            #lam                = D_time*(len(df_asset)/len(df_by_year))
            A                  = 100*((trials-len(df_asset))/trials)                  # Avaliability
            lam                = D_time*(len(df_asset)/trials)
            pof                = 1-np.exp(-lam)
            pof_dic.append(100*pof)
            ens_rms            = np.sqrt(np.mean(df_asset['Cr'].values**2))
            saidi_rms          = np.sqrt(np.mean(df_asset['SAIDI'].values**2))
            ens.append(ens_rms) 
            mttr_dic.append(mttr)
            cr_rms             = np.sqrt(np.mean(df_asset['Cr'].values**2))
            asset_name.append(asset.Name)
            year_val.append(year)

            cr_dic.append(cr_rms)
            ri_dic.append(pof*cr_rms)                                             # Risk index
            a_dic.append(A)
            saidi_dic.append(saidi_rms)

    
    data_dic['Name']     = asset_name
    data_dic['Year']     = year_val
    data_dic['POF']      = pof_dic
    data_dic['MTTR']     = mttr_dic
    data_dic['Cr']       = cr_dic
    data_dic['A']        = a_dic
    data_dic['SAIDI']    = saidi_dic
    
    if Factor=='GWh':
        data_dic['ENS']      = [n/1000 for n in ens]
        ##data_dic['RI']       = [round(n/1000,2) for n in ri_dic]
        #data_dic['RI']       = [round(n/1000,2) for n in ri_dic]
        data_dic['RI']       = ri_dic
    else:
        data_dic['ENS']      = ens
        data_dic['RI']       = ri_dic
    
    df_data            = pd.DataFrame.from_dict(data_dic)    

    return df_data

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # 
def CR_Time_df(DF,Years,Factor='GWh'):
    data_by_trail = {}
    data_dic               = {}

    for year in Years:
        df_by_year         = DF[DF.Date.dt.year<=year]
        data_by_trail      = {}
        data_temp          = []
        for trail in DF['Ite'].unique():
            df                   = df_by_year[df_by_year['Ite']==trail]
            data_by_trail[trail] = df['Cr'].sum()
            if Factor=='GWh':
                data_temp.append(df['Cr'].sum()/1e3)
            else:
                data_temp.append(df['Cr'].sum())
        data_dic[year] = data_temp


    df = pd.DataFrame.from_dict(data_dic)
    return df
