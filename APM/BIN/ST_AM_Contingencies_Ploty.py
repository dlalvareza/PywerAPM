# # # # # # # # # # # # # # # # # # # # # # # #
#                                             # 
#          Module to plot results of          #
#      real time contingencies assessmemnt    #
#             By: David Alvarez               #
#              09-08-2018                     #
#            Version Aplha-0.1                #  
#                                             #
# # # # # # # # # # # # # # # # # # # # # # # #


import pandas as pd
import numpy as np
import calendar
import matplotlib.pyplot as plt
import seaborn as sns
from math import pi
from scipy import stats

import matplotlib.ticker as ticker

color_limits = ['#259B00','#CFE301','#FF5733','#900C3F']
hi_limits    = [0.25,0.5,0.75,1]
cum_ens_pof  = [0.85,0.95,0.99]

warn_colors =['#259B00','#CFE301','#FF5733','#900C3F','#339900','#99CC33','#FFCC00','#FF9966','#CC3300']
warn_colors = sns.color_palette(warn_colors)

pkmn_type_colors = ['#78C850',  # Grass
                    '#F08030',  # Fire
                    '#6890F0',  # Water
                    '#A8B820',  # Bug
                    #'#A8A878',  # Normal
                    '#A040A0',  # Poison
                    '#F8D030',  # Electric
                    #'#E0C068',  # Ground
                    #'#EE99AC',  # Fairy
                    '#C03028',  # Fighting
                    '#F85888',  # Psychic
                    '#B8A038',  # Rock
                    '#705898',  # Ghost
                    '#98D8D8',  # Ice
                    '#7038F8',  # Dragon
                   ]


#-> # # # # # # # # # # # # # # # # # # # # # # # # # #  # 
def Plot_Security_Opteration(DATA,DAY,S_base,TR,LN,BU):
        df    = DATA[DATA.Day==DAY]
        if not BU:
            df     = df[(df.Type != 'BUS')]
        if not TR:
            df     = df[(df.Type != 'TR')]
        if not LN:
            df     = df[(df.Type != 'LN')]

        x,y,s,c = DF_to_List(df,S_base,BU) 
        l_plot,ax = Plot_Scater(x,y,s,c,BU,LN)
        fig = Scater_Labels(l_plot,ax,S_base,BU=BU,LN=LN)
        return fig
        
def Plot_All_Days_Hour_Data(DF,text,S_base=1,TR=True,LN=True,BU=False,day_list=None):

    if day_list==None:
        day_list = list(calendar.day_name)

    for day in day_list:
        #df    = DF[DF.Day==day]
        #if not BU:
        #    df     = df[(df.Type != 'BUS')]
        #if not TR:
        #    df     = df[(df.Type != 'TR')]
        #if not LN:
        #    df     = df[(df.Type != 'LN')]

        #x,y,s,c = DF_to_List(df,S_base,BU) 
        #l_plot,ax = Plot_Scater(x,y,s,c,BU,LN)
        #Scater_Labels(l_plot,ax,S_base,BU=BU,LN=LN)
        fig = Plot_Security_Opteration(DF,day,S_base,TR,LN,z)
        plt.savefig(text+day+'.pdf', bbox_inches = "tight")
        plt.close()
#-> # # # # # # # # # # # # # # # # # # # # # # # # # #  # 

def DF_to_List(DF,s_base,BU):
    x,y,s,c = [],[],[],[]
    for n,row in DF.iterrows():   
        y.append(row['Name'])
        x.append(row['Hour'])
        if BU:
            c.append(abs(1-row['Loading']))
            s.append(0.00001*np.power(row['Loading']*4.75,10))
        else:    
            c.append(row['Loading'])
            s.append(5*100*row['Load']/s_base)
        #print(s)
    return x,y,s,c

def Plot_Scater(x,y,s,c,BU,LN=True):
    from collections import Counter
    #size_y =  int(len(Counter(y).keys())/4)
    #size_y =  int(len(Counter(y).keys())/2)
    #fig, ax = plt.subplots(figsize=(10,8))
    fig, ax = plt.subplots(figsize=(16,9))

    if BU:
        #fig, ax = plt.subplots(figsize=(12,12))
        plot    = ax.scatter(x, y, s=s,alpha=0.85,c=c,cmap='jet', vmin=0,vmax=0.15)
    else:  
        plot    = ax.scatter(x, y, s=s,alpha=0.85,c=c,cmap='jet', vmin=15,vmax=135)
    return plot,ax
    
def Scater_Labels(plot,ax,s_base,BU=False,LN=False):
    if BU:
        legend1 = ax.legend(*plot.legend_elements(num=4,fmt=" {x:.2f}"),loc="upper left", title="$|1-U_{k_{pu}}|$",fontsize=16)
        kw = dict(prop="sizes", num=3, color='gray',alpha=0.5, fmt=" {x:.2f}",func=lambda s: np.power(s/0.00001,1/10)/4.75)
        ax.legend(*plot.legend_elements(**kw),loc="upper right", title="Voltage-[Pu]",fontsize=16)
        #ax.xaxis.set_tick_params(labelsize=18)
        ax.xaxis.set_tick_params(labelsize=10)
        ax.yaxis.set_tick_params(labelsize=10)
        ax.set_xlabel('Time - [h]', fontsize=16)
    else:
        legend1 = ax.legend(*plot.legend_elements(num=4),loc="upper left", title="Loading-[%]",fontsize=16)
        kw = dict(prop="sizes", num=4, color='gray',alpha=0.5, fmt=" {x:.1f}",func=lambda s: s*s_base/(100*5))
        ax.legend(*plot.legend_elements(**kw),loc="upper right", title="Load-[MVA]",fontsize=16)
        #ax.yaxis.set_tick_params(labelsize=18)
        ax.yaxis.set_tick_params(labelsize=10)
        ax.set_xlabel('Time - [h]', fontsize=16)
        #if LN:
        ax.xaxis.set_tick_params(labelsize=10)
    ax.add_artist(legend1)
    
#-> # # # # # # # # # # # # # # # # # # # # # # # # # #  #     
def Plot_Stack_By_Day(DATA,DAY):
        #fig, ax = plt.subplots(figsize=(8,5))
        fig, ax = plt.subplots(figsize=(16,9))
        df       = DATA[DATA.Day==DAY]
        df       = df.drop(columns="Day")
        df_pivot = df.pivot(index='Hour', columns='Name', values='Load')
        df_pivot.plot.area(ax=ax)
        #->ax.legend(loc='lower center', ncol=7, bbox_to_anchor=(0.5, 1), fontsize='x-small')
        ax.legend(loc='lower center', ncol=9, bbox_to_anchor=(0.5, 1))
        ax.set(ylabel='Load - [MVA]')
        ax.set_xlabel('Time - [h]', fontsize=16)
        ax.xaxis.set_tick_params(labelsize=14)
        ax.yaxis.set_tick_params(labelsize=12)
        plt.xlim(0,df['Hour'].max())
        return fig
        
def Plot_Stack(DF,text,day_list=None):

    if day_list==None:
        day_list = list(calendar.day_name)

    for day in day_list:
        #fig, ax = plt.subplots(figsize=(8,5))
        #df       = DF[DF.Day==day]
        #df       = df.drop(columns="Day")
        #df_pivot = df.pivot(index='Hour', columns='Name', values='Load')
        #df_pivot.plot.area(ax=ax)
        #ax.legend(loc='lower center', ncol=7, bbox_to_anchor=(0.5, 1), fontsize='x-small')
        #ax.set(ylabel='Load - [MVA]')
        #ax.set_xlabel('Time - [h]', fontsize=16)
        #ax.xaxis.set_tick_params(labelsize=14)
        #ax.yaxis.set_tick_params(labelsize=12)
        #plt.xlim(0,df['Hour'].max())
        fig = Plot_Stack_By_Day(DF,day)
        plt.savefig(text+day+'_Load.pdf', bbox_inches = "tight")
        plt.close()

#-> # # # # # # # # # # # # # # # # # # # # # # # # # #  #     
    
def Plot_Histogram(DF,Asset_List,Type=None):

    #->if Type==None:
    #->    asset_port = Asset_List.Name.values.tolist()
    #->else:
    #->    asset_port  = Asset_List[Asset_List['Type']==Type] 
    #->    asset_port  = asset_port.Name.values.tolist()

    print('Test Test')
    asset_port  = ['TR_1', 'TR_2', 'TR_3', 'TR_4', 'TR_5', 'TR_6', 'TR_7', 'TR_8', 'TR_9', 'TR_10', 'TR_11', 'TR_12']
    
    data_by_trail = {}
    data_asset_by_trail = {}

    data_by_trail_1 = {}

    for trail in DF['Ite'].unique():
        df = DF[DF['Ite']==trail]
        data_by_trail_1[trail] = df['Cr'].sum()
        if df['Cr'].sum()>0:
            data_by_trail[trail] = df['Cr'].sum()
        test_dic = {}
        for asset in  asset_port:
            df_a = df[df[asset]==True]          # Check if the asset fail
            test_dic[asset]= df_a['Cr'].sum()

        data_asset_by_trail[trail] = test_dic

    df_total    = pd.DataFrame.from_dict(data_by_trail,  orient='index')

    
    df_by_asset = pd.DataFrame.from_dict(data_asset_by_trail,  orient='index')

    #for asset in  asset_port:
    #    if df_by_asset[asset].sum()>0:
    #        sns.distplot(df_by_asset[asset],label=asset, kde=False , bins=50)

    #sns.distplot(df_total,label='Portfolio', kde=False, bins=50)

    #kwargs = {'cumulative': True}
    x  = df_total.values
    import matplotlib.pyplot as plt
    weights = np.ones_like(x)/500
    plt.hist(x, weights=weights)

    df_total    = pd.DataFrame.from_dict(data_by_trail_1,  orient='index')
    x = df_total.values
    plt.hist(x, cumulative = True,alpha=0.25,density=True)
    #print(df_total)
    #sns.kdeplot(df_total, cumulative=True)
    #df_total.hist( cumulative = True )
    #x  = df_total.values


    plt.xlabel('Energy not supplied (ENS) - [MWh]')
    plt.legend()
    plt.ylabel('Density')
    
    plt.show()
    #plt.savefig('Histogram_ENS_Load.pdf', bbox_inches = "tight")
    #plt.close()

def Plot_Histogram_ENS(DF,Asset_port,Years,Type=None,Factor='GWh'):

    #->if Type==None:
    #->    asset_port = Asset_List.Name.values.tolist()
    #->else:
    #->    asset_port  = Asset_List[Asset_List['Type']==Type] 
    #->    asset_port  = asset_port.Name.values.tolist()

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

    # Plot histogram with seaborn
    sns.set_palette("Set1")
    fig, ax = plt.subplots() 

    for year in Years:
        #kwargs = {'cumulative': True,'bw':3,'cut':0,'shade':True}
        kwargs = {'cumulative': True,'bw':3,'cut':0,'shade':True}
        sns.distplot(df[year], hist=False, kde_kws=kwargs,norm_hist=True,kde=True,label=year,ax=ax)
        
        # Show vertical lines
        data_x, data_y = ax.lines[-1].get_data()
        color          = ax.lines[-1].get_c()
        for yi in cum_ens_pof:   # coordinate where to find the value of kde curve
            xi = np.interp(yi,data_y,data_x)
            y  = [0,yi]
            x  = [xi,xi]
            ax.plot(x, y,color=color,ls='--',linewidth= 1,alpha=0.5)        # Vertical line
            if year==Years[-1]:   # Plot horizontal lines just for the last year - avoid overplotting
                
                y  = [yi,yi]
                x  = [0,xi]
                ax.plot(x, y,color='black',ls=':',linewidth= 0.5,alpha=0.75)        # Horizontal line
    

    plt.xlabel('Energy not supplied (ENS) - ['+Factor+']')
    plt.legend()
    plt.ylabel('Density')
    plt.xlim(0,df[year].max())
    plt.ylim(0,1.05)
    plt.savefig('RESULTS/Histogram_ENS_Cumulative_Load.pdf', bbox_inches = "tight")


    # Plot histogram with seaborn 
    
    for year in Years:
        fig, ax1 = plt.subplots(figsize= [4, 3]) 
        kwargs_hist = {'cumulative': False,'bw':0.5,'cut':0}
        kwargs = {'cumulative': False,"alpha": 0.75,"linewidth": 1.5,'edgecolor':'#000000'}
        sns.distplot(df[year], hist_kws=kwargs, kde_kws=kwargs_hist,norm_hist=True,kde=False,ax=ax1)
    
        plt.xlabel('Energy not supplied (ENS) - ['+Factor+']')
        plt.ylabel('Density')
        plt.xlim(0,df[year].max())
        #plt.savefig('RESULTS/'+str(year)+'_Histogram_ENS_Load.pdf', bbox_inches = "tight",label=year)
        plt.savefig('RESULTS/'+str(year)+'_Histogram_ENS_Load.pdf', bbox_inches = "tight")
        plt.close()



def Risk_Matrix_ENS(DF,Asset_dF,year_list,N,Type=None,Factor='GWh'):

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
    a_dic        = []
    saidi_dic    = []
    y_beg= min(DF.Date.dt.year)-1

    for asset_id in  Asset_dF.index:
        asset  = Asset_dF.loc[asset_id]
        for year in year_list:
            df_by_year         = DF[DF.Date.dt.year<=year]
            df_asset           = df_by_year[df_by_year[asset.Name]==True]                 # Check if the asset fail
            mttr               = asset.MTTR
            trials             = 24*365*(year-y_beg)*N
            D_time             = 24*365*(year-y_beg)/mttr                           # Cumulative years
            #lam                = D_time*(len(df_asset)/len(df_by_year))
            A                  = 100*((trials-len(df_asset))/trials)                  # Avaliability
            lam                = D_time*(len(df_asset)/trials)
            pof                = 1-np.exp(-lam)
            pof_dic.append(100*pof)
            ens_rms = np.sqrt(np.mean(df_asset['Cr'].values**2))
            saidi_rms = np.sqrt(np.mean(df_asset['SAIDI'].values**2))
            ens.append(ens_rms) 
            mttr_dic.append(mttr)
            asset_name.append(asset.Name)
            year_val.append(year)
            ri_dic.append(pof*ens_rms)                                             # Risk index
            a_dic.append(A)
            saidi_dic.append(saidi_rms)
            #A                  = len(df_asset)/(len(df_by_year))
    
    data_dic['Name']     = asset_name
    data_dic['Year']     = year_val
    data_dic['POF']      = pof_dic
    data_dic['MTTR']     = mttr_dic
    data_dic['A']        = a_dic
    data_dic['SAIDI']    = saidi_dic
    
    if Factor=='GWh':
        data_dic['ENS']      = [n/1000 for n in ens]
        data_dic['RI']       = [round(n/1000,2) for n in ri_dic]
    else:
        data_dic['ENS']      = ens
        data_dic['RI']       = ri_dic
    
    df_data            = pd.DataFrame.from_dict(data_dic)

    # SAIDI   
    for year in year_list:
        fig, ax = plt.subplots(figsize= [4, 3]) 
        query = 'Year=='+str(year)
        df = df_data.query(query) 
        sns.scatterplot(x="POF", y="SAIDI", hue="RI", size="MTTR", alpha=.75, data=df, palette="RdYlGn_r",ax=ax)
        #ax.set(ylim=(0, df['SAIDI'].max()))
        for line in df.index.values:
            ax.text(df.POF[line], df.SAIDI[line], df.Name[line], horizontalalignment='left', va='bottom',size=5, color='black')

        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.setp(ax.get_legend().get_texts(), fontsize='xx-small') # for legend text
        plt.setp(ax.get_legend().get_title(), fontsize='small') # for legend title        
        plt.ylabel('Criticality - $RMS_{SAIDI}$ - [h]')
        plt.xlabel('Probability of Failure (POF) - [%]')
        plt.savefig('RESULTS/'+str(year)+'_Risk_Matrix_SAIDI.pdf', bbox_inches = "tight")
        plt.close()


    # Risk matrix plot
    #plt.xkcd()
    for year in year_list:
        fig, ax = plt.subplots(figsize= [4, 3]) 
        query = 'Year=='+str(year)
        df = df_data.query(query) 
        sns.scatterplot(x="POF", y="ENS", hue="RI", size="MTTR", alpha=.75, data=df, palette="RdYlGn_r",ax=ax)
        for line in df.index.values:
            ax.text(df.POF[line], df.ENS[line], df.Name[line], horizontalalignment='left', va='bottom',size=5, color='black')
        

        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.setp(ax.get_legend().get_texts(), fontsize='xx-small') # for legend text
        plt.setp(ax.get_legend().get_title(), fontsize='small') # for legend title        
        plt.ylabel('Criticality - $RMS_{ENS}$ - ['+Factor+']')
        plt.xlabel('Probability of Failure (POF) - [%]')
        plt.savefig('RESULTS/'+str(year)+'_Risk_Matrix.pdf', bbox_inches = "tight")
        plt.close()

    # Availability risk matrix
    for year in year_list:
        fig, ax = plt.subplots(figsize= [4, 3]) 
        query = 'Year=='+str(year)
        df = df_data.query(query)
        print(df_data) 
        
        
        sns.scatterplot(x=df.POF, y=df.A, hue="RI", size="MTTR", alpha=.75, data=df, palette="RdYlGn_r",ax=ax)
        ax.set(ylim=(99.975, 100))
        for line in df.index.values:
            ax.text(df.POF[line], df.A[line], df.Name[line], horizontalalignment='left', va='bottom',size=5, color='black')
        
        #plt.gca().invert_yaxis()
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
        plt.setp(ax.get_legend().get_texts(), fontsize='xx-small') # for legend text
        plt.setp(ax.get_legend().get_title(), fontsize='small') # for legend title        
        plt.ylabel('Criticality -  $A$ - [%]')
        plt.xlabel('Probability of Failure (POF) - [%]')
        plt.savefig('RESULTS/'+str(year)+'_Risk_Matrix_A.pdf', bbox_inches = "tight")
        plt.close()

    # Pareto plot
    df_data = df_data[df_data['RI'] > 0.05]
    df_data = df_data.sort_values('RI', ascending = False)
    df_data = df_data.sort_values('Year')

    #plt.xkcd()
    f, (ax) = plt.subplots(figsize= [8, 4])
    ax = sns.barplot(x="Year", y="RI", hue="Name", data=df_data, palette="Set1", alpha=.75)
    plt.setp(ax.get_legend().get_texts(), fontsize='x-small') # for legend text
    plt.setp(ax.get_legend().get_title(), fontsize='small') # for legend title

    ax.legend(loc='lower center', ncol=5, bbox_to_anchor=(0.5, 1), fontsize='small')
    plt.ylabel('Risk Index (RI) - ['+Factor+']')
    plt.savefig('RESULTS/Risk_Assessment_Pareto.pdf', bbox_inches = "tight")
    plt.close()


def Plot_Violin_ENS(DF_now,Asset_List,year_list,Type=None,Factor='GWh'):

    #->if Type==None:
    #->    asset_port = Asset_List.Name.values.tolist()
    #->else:
    #->    asset_port  = Asset_List[Asset_List['Type']==Type] 
    #->    asset_port  = asset_port.Name.values.tolist()


    def Test_F(DF):
        test_asset    = []
        test_cr       = []
        test_year     = []

        for trail in DF['Ite'].unique():
            df = DF[DF['Ite']==trail]
            for year in year_list:
                df_by_year = df[df.Date.dt.year<=year]
                for asset in  Asset_List:
                    df_a = df_by_year[df_by_year[asset]==True]          # Check if the asset fail
                    if not df_a.empty:
                        #->if df_a['Cr'].sum()>0:
                            test_cr.append(df_a['Cr'].sum())
                            test_asset.append(asset)
                            test_year.append(year) 
                # Criticity of the year
                test_cr.append(df_by_year['Cr'].sum())
                test_asset.append('Total_CR')
                test_year.append(year) 

        test_dic ={}   
        if Factor=='GWh':
                test_dic['Cr']       = [n/1000 for n in test_cr]  
        else:
                test_dic['Cr']       = test_cr 

       
        test_dic['Asset']    = test_asset 
        test_dic['year']     = test_year
        return test_dic

    data_dic = Test_F(DF_now)
    df_data       = pd.DataFrame.from_dict(data_dic)

    # Plottting
    Cri_asset_list = list(df_data['Asset'].unique())
    Cri_asset_list.remove('Total_CR')

    for asset in Cri_asset_list:
        query = 'Asset=="Total_CR" or Asset=="'+asset+'"'
        df = df_data.query(query)
        sns.violinplot(x="year", y="Cr",data=df,cut=0,hue='Asset',split=False,dodge=False,scale='count',scale_hue=False,palette="Set1_r",bw=.2,inner="quartile")
        plt.ylabel('Energy not supplied (ENS) - ['+Factor+']')
        plt.savefig('RESULTS/'+asset+'_Violin_Plot.pdf', bbox_inches = "tight")
        plt.close()
    

def Plot_Distribution(DF,Asset_List,Type=None):

    #->if Type==None:
    #->    asset_port = Asset_List.Name.values.tolist()
    #->else:
    #->    asset_port  = Asset_List[Asset_List['Type']==Type] 
    #->    asset_port  = asset_port.Name.values.tolist()

    print('Test Test')
    asset_port  = ['TR_1', 'TR_2', 'TR_3', 'TR_4', 'TR_5', 'TR_6', 'TR_7', 'TR_8', 'TR_9', 'TR_10', 'TR_11', 'TR_12']
    
    
    data_by_trail = {}
    data_asset_by_trail = {}

    for trail in DF['Ite'].unique():
        df = DF[DF['Ite']==trail]
        data_by_trail[trail] = df['Cr'].sum()
        test_dic = {}
        for asset in  asset_port:
            df_a = df[df[asset]==True]          # Check if the asset fail
            if not df_a.empty:
                test_dic[asset]= df_a['Cr'].sum()
        
        test_dic['Total_Cr']= df['Cr'].sum()   

        data_asset_by_trail[trail] = test_dic

    df_total    = pd.DataFrame.from_dict(data_by_trail,  orient='index',columns=['Cr'])
    df_by_asset = pd.DataFrame.from_dict(data_asset_by_trail,  orient='index')

    #fig, ax = plt.subplots()

    inter = True
    for asset in  asset_port:
        df              = pd.DataFrame()
        df[asset]       = df_by_asset[asset]
        df['Total_Cr']  = df_by_asset['Total_Cr']
        df              = df.dropna()
        if df[asset].sum()>0:
            if inter:
                graph = sns.jointplot(x="Total_Cr", y=asset, data=df,label=asset,kind='kde',cut=0, shade=True, shade_lowest=False)
                graph.plot_joint(plt.scatter, s=25,alpha=0.75)  
                sns.distplot(df[asset].values,ax=graph.ax_marg_y,vertical=True)
                inter = False
            else:
                graph.x = df.Total_Cr
                graph.y = df[asset]
                graph.plot_joint(sns.kdeplot, shade=True, shade_lowest=False,label=asset,cut=0)
                graph.plot_joint(plt.scatter, s=25,alpha=0.75)  
                sns.distplot(df[asset].values,ax=graph.ax_marg_y,vertical=True)

            #g = sns.kdeplot(df_by_asset.Total_Cr, df_by_asset[asset], shade=True, shade_lowest=False,label=asset,cut=0)
            #sns.jointplot(x="Total_Cr", y=asset, data=df_by_asset,label=asset)
            #g.plot_joint(plt.scatter, c="w", s=30, linewidth=1, marker="+")


    
    plt.xlabel('Total Energy not supplied (ENS) - [MWh]')
    plt.legend()
    plt.ylabel('Energy not supplied (ENS) by Asset- [MWh]')
    
    plt.show()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                                             #                                         
#                                                                             #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def Asset_Condition_by_Type(a_list,Asset,Cond_Name):
    asset_l = []
    for n in a_list:
        l_asset = Asset.Asset_Portfolio[n]
        if Cond_Name in l_asset.cond.keys():
            asset_l.append(n)
    asset_list = asset_l
    sns.set(style="whitegrid")
    sns.set_palette(pkmn_type_colors)

    #fig, ax = plt.subplots(figsize= [8, 4])            
    fig, ax = plt.subplots(figsize= [16, 9])            

    x_max = max(Asset.Asset_Portfolio[asset_list[0]].cond[Cond_Name].historic_data.Date.values)
    x_min = min(Asset.Asset_Portfolio[asset_list[0]].cond[Cond_Name].historic_data.Date.values)
    y_max = 0
        
    for n in asset_list:
        asset = Asset.Asset_Portfolio[n]
        df    = asset.cond[Cond_Name].historic_data
        if y_max<df.Val.max():
            y_max = df.Val.max()
        if x_max<df.Date.max():
            x_max = df.Date.max()
        if x_min>df.Date.min():
            x_min = df.Date.min()    

        sns.lineplot(x='Date', y='Val', data=df,label=asset.name,ax=ax)
 
     # Set plot y limits
    if y_max<max(asset.cond[Cond_Name].limits):
        y_max = max(asset.cond[Cond_Name].limits)

    y_min =   min(asset.cond[Cond_Name].limits) 

    # Print condition limits
    n_con_eval = range(len(asset.cond[Cond_Name].limits)-1)
    for n in n_con_eval:
        y1 = asset.cond[Cond_Name].limits[n]
        y2 = asset.cond[Cond_Name].limits[n+1]
        # Check color limits
        if n==0:
            if y1>y2:
                if y1<y_max:
                    y1 = y_max
        if n==n_con_eval[-1]:
            if y2>y1:
                if y2<y_max:
                    y2 = y_max

        ax.axhspan(y1, y2 ,facecolor=color_limits[n], alpha=0.2)

    
    ax.set(ylabel=Cond_Name)
    ax.set_ylim(y_min, y_max)
    ax.set_xlim(x_min, x_max)
    ax.legend(loc='lower center', ncol=6, bbox_to_anchor=(0.5, 1), fontsize='small')
                   
    return fig
def Plot_Asset_Condition_Assessment(Asset,Type=None,Cond_Name='TDCG'):
    df = Asset.Asset_Portfolio_List
    if Type==None:
        asset_list = df
    else:
        asset_list = df[df['Type']==Type]

    asset_list = list(asset_list.index)

    # Check if the condition exist or it is available  
    '''asset_l = []
    for n in asset_list:
        asset = Asset.Asset_Portfolio[n]
        if Cond_Name in asset.cond.keys():
            asset_l.append(n)

    asset_list = asset_l
    sns.set(style="whitegrid")
    #sns.set_palette('current_palette = sns.color_palette()',n_colors=len(asset_list),desat=0.5)
    sns.set_palette(pkmn_type_colors)

    f, (ax) = plt.subplots(figsize= [8, 4])
   
    #try:
    x_max = max(Asset.Asset_Portfolio[asset_list[0]].cond[Cond_Name].historic_data.Date.values)
    x_min = min(Asset.Asset_Portfolio[asset_list[0]].cond[Cond_Name].historic_data.Date.values)
    #except:
    #    x_max = 0
    #    x_min = 0
    y_max = 0
    
    
    for n in asset_list:
        asset = Asset.Asset_Portfolio[n]
        df    = asset.cond[Cond_Name].historic_data
        if y_max<df.Val.max():
            y_max = df.Val.max()
        if x_max<df.Date.max():
            x_max = df.Date.max()
        if x_min>df.Date.min():
            x_min = df.Date.min()    

        sns.lineplot('Date', 'Val', data=df,label=asset.name,ax=ax)

    # Set plot y limits
    if y_max<max(asset.cond[Cond_Name].limits):
        y_max = max(asset.cond[Cond_Name].limits)

    y_min =   min(asset.cond[Cond_Name].limits) 

    # Print condition limits
    n_con_eval = range(len(asset.cond[Cond_Name].limits)-1)
    for n in n_con_eval:
        y1 = asset.cond[Cond_Name].limits[n]
        y2 = asset.cond[Cond_Name].limits[n+1]
        # Check color limits
        if n==0:
            if y1>y2:
                if y1<y_max:
                    y1 = y_max
        if n==n_con_eval[-1]:
            if y2>y1:
                if y2<y_max:
                    y2 = y_max

        ax.axhspan(y1, y2 ,facecolor=color_limits[n], alpha=0.2)

    
    ax.set_ylim(y_min, y_max)
    ax.set_xlim(x_min, x_max)
    ax.legend(loc='lower center', ncol=6, bbox_to_anchor=(0.5, 1), fontsize='small')'''
    fig = Asset_Condition_by_Type(asset_list,Asset,Cond_Name)
    plt.savefig('RESULTS/'+Cond_Name+'_Condition_Trend.pdf', bbox_inches = "tight")
    plt.close()
        

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                             # 
#                    Historical HI plot                       #
#                                                             # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def Histotical_HI_PLot(Assets,date,n_hours,plot_list):
    
        # Plot settings 
        #sns.set(style="whitegrid")
        f1, (ax1) = plt.subplots(figsize= [6, 3.5])
        ax1_t     = ax1.twinx()

        f2, (ax2) = plt.subplots(figsize= [6, 3.5])

        f3, (ax3) = plt.subplots(figsize= [6, 3.5])
        #ax2_t     = ax2.twinx()

        for n in plot_list:
            asset = Assets.Asset_Portfolio[n]
            df    = asset.POF_R_Assessment(date,n_hours)

            #sns.lineplot('Date', 'HI',data=df,label=asset.name+' - $HI_{t_k}$',ax=ax1)
            #sns.lineplot('Date', 'lambda',data=df, linestyle="--",label=asset.name+' - $\lambda_{t_k}$',ax=ax1_t)
            df.plot.line(x='Date',y= 'HI',label=asset.name+' - $HI_{t_k}$',ax=ax1)
            df.plot.line(x='Date',y= 'lambda',label=asset.name+' - $\lambda_{t_k}$',ax=ax1_t,style='--')

            #sns.lineplot('Date', 'POF',data=df,label=asset.name+' - POF',ax=ax2)
            #sns.lineplot('Date', 'R',data=df,linestyle="--",label=asset.name+'- R',ax=ax2_t)
            
            #df.plot.area(x='Date',y='sum_lambda',stacked=False,ax=ax2,label=asset.name+'- $\sum {\lambda_{t_k}}$')
            df.plot.area(x='Date',y='sum_lambda',stacked=False,ax=ax2,label=asset.name)
            #df.plot.line(x='Date',y= 'POF',label=asset.name+' - POF',ax=ax2,style='--')
            df.plot.area(x='Date',y='POF',stacked=False,ax=ax3,label=asset.name)

        ax1.legend(loc='upper left', ncol=1, fontsize='x-small')
        ax1_t.legend(loc='lower right', ncol=1, fontsize='x-small')

        ax2.legend(loc='center left', ncol=1, fontsize='x-small')

        ax3.legend(loc='center left', ncol=1,  fontsize='x-small')

        f1.savefig('RESULTS/HI_Condition_Trend.pdf', bbox_inches = "tight")
        f2.savefig('RESULTS/Reliability_Asessment_Trend.pdf', bbox_inches = "tight")
        f3.savefig('RESULTS/POF_Trend.pdf', bbox_inches = "tight")

        plt.close()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#                                                             # 
#                        Radar plot                           #
#                                                             # 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def Radar_Plot_by_Asset(asset,date):
        df    =  pd.DataFrame()
        for dat in date:
            temp_cond = {}
            for con_Id in asset.cond:
                cond_fore = asset.cond[con_Id].eval_cond_fit_func(dat)
                temp_cond[con_Id]= cond_fore
            df_new    = pd.DataFrame.from_dict(temp_cond, orient='index',columns=[str(dat.year)])
            df = pd.concat([df, df_new], axis=1, sort=False)
 
        #ax = Radar_Plot(df)         # Radar plot
        return Radar_Plot(df)        

def Radar_Plot_by_Asset_save(asset,date,path):
        #asset = Asset.Asset_Portfolio[n]
        #path = 'RESULTS/'+str(asset.name)+'_Condition_Radart.pdf'
        fig = Radar_Plot_by_Asset(asset,date)
        plt.savefig(path, bbox_inches = "tight")
        plt.close() 
        
def Radar_Plot_Asset_Condition_Assessment(Asset,date,Type='TR'):
    df         = Asset.Asset_Portfolio_List
    asset_list = list(df[df['Type']==Type].index)
  
    for n in asset_list:     
        asset = Asset.Asset_Portfolio[n]
        path = 'RESULTS/'+str(asset.name)+'_Condition_Radart.pdf'
        fig = Radar_Plot_by_Asset(asset,date)
        plt.savefig(path, bbox_inches = "tight")
        plt.close()

# -> # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# Historical health condition plot 
def HI_Radar_Plot_I(Asset_Data,date_period,Type='TR'):
    hi_hist_dic         = {}
    hi_hist_dic['Year'] = [date.year for date in date_period]

    for asset_id in list(Asset_Data.Asset_Portfolio_List.index):
        asset = Asset_Data.Asset_Portfolio[asset_id]
        hi_hist = []
        for date in date_period:
            asset.HI(date)
            hi_hist.append(round(asset.hi,2))
        hi_hist_dic[asset.name] = hi_hist

    df          = pd.DataFrame.from_dict(hi_hist_dic)
    df          = df.set_index('Year')
    df          = df.T
    return Radar_Plot(df) 
    
def HI_Radar_Plot(Asset_Data,date_period,Type='TR'):

    fig = HI_Radar_Plot_I(Asset_Data,date_period,Type='TR')
    plt.savefig('RESULTS/HI_Asset_Fleet_Radar.pdf', bbox_inches = "tight")
    plt.close()

# -> # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #  
# Historical POF condition plot 
def POF_Radar_Plot_I(Asset_Data,N_hours,date_period,date_beg,Type='TR'):
    pof_hist_dic         = {}
    pof_hist_dic['Year'] = [date.year for date in date_period]

    for asset_id in list(Asset_Data.Asset_Portfolio_List.index):
        asset = Asset_Data.Asset_Portfolio[asset_id]
        df       = asset.POF_R_Assessment(date_beg,N_hours)
        pof_hist = []
        for date in date_period:
            pof_hist.append(df[df.Date==date].POF.values[0]/100)
        pof_hist_dic[asset.name] = pof_hist

    df          = pd.DataFrame.from_dict(pof_hist_dic)
    df          = df.set_index('Year')
    df          = df.T
    return Radar_Plot(df) 



def POF_Radar_Plot(Asset_Data,N_hours,date_period,date_beg,Type='TR'):    
    fig =  POF_Radar_Plot_I(Asset_Data,N_hours,date_period,date_beg,Type='TR')
    plt.savefig('RESULTS/POF_Asset_Fleet_Radar.pdf', bbox_inches = "tight")
    plt.close()


# Radar plot with a dataframe as input
def Radar_Plot(df):
   # number of variable
    categories=list(df.index)
    N = len(categories)
    angles = [n / float(N) * 2 * pi for n in range(N)]
    #sns.set_palette(warn_colors)
    sns.set_palette("Set1")
    # Initialise the spider plot
    ax = plt.subplot(polar=True)
    plt.gcf().set_size_inches(8, 8)


    # If you want the first axis to be on top:
    ax.set_theta_offset(pi / 2)
    ax.set_theta_direction(-1)

    # Draw one axe per variable + add labels labels yet
    plt.xticks(angles, categories)

    # Draw ylabels
    ax.set_rlabel_position(0)
    plt.yticks(hi_limits, hi_limits, color="gray", size=8)
    plt.ylim(0,1)

    for lim in reversed(range(len(hi_limits))):
        values = [hi_limits[lim] for n in angles]
        ax.fill(angles, values, color=color_limits[lim], alpha=0.2)
    
    # Radar plot assets
    angles += angles[:1]
    for name in df.columns:
        values = list(df[name].values)
        values += values[:1] 
        ax.plot(angles, values, linewidth=1, linestyle='solid', label=name)   
    ax.legend(loc='lower center', ncol=5, bbox_to_anchor=(0.5,1.1), fontsize='small')

    return ax

def plot_historic_condition_by_asset(asset,path):
    
    sns.set(style="darkgrid")
    f, (ax) = plt.subplots(figsize= [8, 4])
    for con_Id in asset.cond:
        df = asset.cond[con_Id].historic_data
        sns.lineplot('Date', 'val_nor', data=df,label=con_Id,ax=ax, marker='o')
    
    plt.ylabel('Condición - $S_n$',fontsize= 14)
    plt.xlabel('Fecha',fontsize= 14)
    plt.xticks(fontsize=12)
    plt.yticks(fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.savefig(path, bbox_inches = "tight")
    plt.close()


def Pie_Plot_Asset_Cr(data,path):
    
    sns.set(style="darkgrid")
    Cr_fin = data.Cr_Fin.values[0]  
    Cr_Env = data.Cr_Env.values[0]  
    Cr_Sec = data.Cr_Sec.values[0]
    Cr_Leg = data.Cr_Leg.values[0]  
    print(data)
    labels = 'Financiero', 'Ambiental', 'Seguridad', 'Legal'
    sizes = [Cr_fin, Cr_Env, Cr_Sec, Cr_Leg]

    f, ax = plt.subplots(figsize= [8, 4])
    ax.pie(sizes, labels=labels, autopct='%1.1f%%',shadow=True, startangle=90)
    ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle.

    plt.savefig(path, bbox_inches = "tight")
    plt.close()
    
# Plot reports 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def f_risk_aversion(DF,Years,file,Factor='GWh'):
    sns.set_palette("Set1")
    fig, ax = plt.subplots(figsize= [6, 3]) 
    for year in Years:
        kwargs = {'cumulative': True,'bw':3,'cut':0,'shade':True}
        sns.distplot(DF[year], hist=False, kde_kws=kwargs,norm_hist=True,kde=True,label=year,ax=ax)
        
        # Show vertical lines
        data_x, data_y = ax.lines[-1].get_data()
        color          = ax.lines[-1].get_c()
        for yi in cum_ens_pof:   # coordinate where to find the value of kde curve
            xi = np.interp(yi,data_y,data_x)
            y  = [0,yi]
            x  = [xi,xi]
            ax.plot(x, y,color=color,ls='--',linewidth= 1,alpha=0.5)        # Vertical line
            if year==Years[-1]:   # Plot horizontal lines just for the last year - avoid overplotting
                
                y  = [yi,yi]
                x  = [0,xi]
                ax.plot(x, y,color='black',ls=':',linewidth= 0.5,alpha=0.75)        # Horizontal line

    plt.xlabel('Energy not supplied (ENS) - ['+Factor+']')
    plt.legend()
    plt.ylabel('Density')
    plt.xlim(0,DF[year].max())
    plt.ylim(0,1.05)
    plt.savefig(file, bbox_inches = "tight", dpi=300)

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def f_Cr_Hist(DF,file,Factor='GWh'):
    #sns.set_palette("Set1")
    #fig, ax = plt.subplots() 

    fig, ax1 = plt.subplots(figsize= [7, 3]) 
    kwargs_hist = {'cumulative': False,'bw':0.5,'cut':0}
    kwargs = {'cumulative': False,"alpha": 0.75,"linewidth": 1.5,'edgecolor':'#000000'}
    sns.distplot(DF, hist_kws=kwargs, kde_kws=kwargs_hist,norm_hist=True,kde=False,ax=ax1)
    
    plt.xlabel('Energy not supplied (ENS) - ['+Factor+']')
    plt.ylabel('Density')
    plt.xlim(0,DF.max())
    plt.savefig(file, bbox_inches = "tight", dpi=300)
    plt.close()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def f_Risk_Matrix(DF,file,Factor='GWh',y="ENS"):

    fig, ax = plt.subplots(figsize= [7, 3]) 

    sns.scatterplot(x="POF", y=y, hue="RI", size="MTTR", alpha=.75, data=DF, palette="RdYlGn_r",ax=ax)
    #for line in DF.index.values:
    #    ax.text(DF.POF[line], DF.ENS[line], DF.Name[line], horizontalalignment='left', va='bottom',size=4, color='black')
        
    plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.setp(ax.get_legend().get_texts(), fontsize='xx-small') # for legend text
    plt.setp(ax.get_legend().get_title(), fontsize='small') # for legend title        
    plt.ylabel('Criticality - $RMS_{'+y+'}$ - ['+Factor+']')
    plt.xlabel('Probability of Failure (POF) - [%]')
    plt.savefig(file, bbox_inches = "tight", dpi=300)
    plt.close()


# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def f_Pareto_Year(DF,file,Factor='GWh'):
    df_data = DF[DF['RI'] > 0.005]
    df_data = df_data.sort_values('RI', ascending = False)

    f, (ax) = plt.subplots(figsize= [8, 3])
    ax = sns.barplot(x="Name", y="RI", hue="MTTR", data=df_data, palette="Set1", alpha=.5)
    #plt.setp(ax.get_legend().get_texts(), fontsize='x-small') # for legend text
    #plt.setp(ax.get_legend().get_title(), fontsize='small') # for legend title

    #ax.legend(loc='lower center', ncol=5, bbox_to_anchor=(0.5, 1), fontsize='small')
    #plt.ylabel('Risk Index (RI) - ['+Factor+']')
    ax.set_xticklabels(ax.get_xticklabels(),rotation=90,Fontsize=8)
    plt.savefig(file, bbox_inches = "tight")
    plt.close()

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def f_Pareto(DF,file,Factor='GWh'):
    df_data = DF[DF['RI'] > 0.05]
    df_data = df_data.sort_values('RI', ascending = False)
    df_data = df_data.sort_values('Year')

    #plt.xkcd()
    f, (ax) = plt.subplots(figsize= [8, 4])
    ax = sns.barplot(x="Year", y="RI", hue="Name", data=df_data, palette="Set1", alpha=.75)
    plt.setp(ax.get_legend().get_texts(), fontsize='x-small') # for legend text
    plt.setp(ax.get_legend().get_title(), fontsize='small') # for legend title

    ax.legend(loc='lower center', ncol=5, bbox_to_anchor=(0.5, 1), fontsize='small')
    plt.ylabel('Risk Index (RI) - ['+Factor+']')
    plt.savefig(file, bbox_inches = "tight")
    plt.close()

