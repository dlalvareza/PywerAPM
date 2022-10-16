# # # # # # # # # # # # # # # # # # # # #
#                                                                         #
#                    By David L. Alvarez                  #
#                         Version 0.0.1                          #
#                                                                         #
# # # # # # # # # # # # # # # # # # # # #


import numpy as np
from math import pi
import pandas as pd
from itertools import cycle

from bokeh.plotting import figure
from bokeh.tile_providers import get_provider
from bokeh.models import Title, ColumnDataSource, Circle
from bokeh.transform import cumsum
from bokeh.palettes import brewer,all_palettes,Category20c
from bokeh.transform import dodge

import datetime 

###############################################################################
color_limits = ['#259B00','#CFE301','#FF5733','#900C3F']
hi_limits    = np.array([0.25,0.5,0.75,1])



pkmn_colors = ['#78C850',  # Grass
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

pkmn_type_colors = cycle(pkmn_colors)

def limit_color(val):
    color_id  = np.where(hi_limits>val)[-1]
    color_id  = color_id[0]
    color     = color_limits[color_id]
    return color

### Plot Maps
def Plot_Asset_Location(Data, TITLE,Index='HI',Factor=1):
    
    TOOLTIPS = [
          #("Ranking", "$index"),
          ("Name", "@Name"),
          ("Substation", "@Loc"),
          #("Brand", "@Brand"),
          ("Year", "@Year"),
          ("HI", "@HI"),
          ("EL", "@EL"),
          #("RI", "@RI"),
          #("OI", "@OI"),  
          ("Type", "@Type"), 
    ]    

    lat          = Data.Loc_x 
    lon          = Data.Loc_y

    df            = Data.copy()
    df['lat']     = lat
    df['lon']     = lon
    df['size']    = (1+np.exp(df[Index].values*4))*2
    df['colors']  = [limit_color(i) for i in df[Index].values]

    #df            = df.drop(['geometry'], axis=1)
    source       = ColumnDataSource(df) 

    x_min = np.amin(lat) #-8324909
    x_max = np.amax(lat) #-8148798

    y_min = np.amin(lon) #417040
    y_max = np.amax(lon) #673868

    fig = figure(x_range=(x_min,x_max), y_range=(y_min,y_max),
           x_axis_type="mercator", y_axis_type="mercator",tooltips=TOOLTIPS,sizing_mode='stretch_width')

    circle = Circle(x="lat", y="lon", size='size', fill_color='colors', fill_alpha=0.5, line_color=None)
    fig.add_tile(get_provider('CARTODBPOSITRON'))
    fig.add_glyph(source, circle)
    
    return fig

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def Plot_Pie_Count(df,col,title="Pie Chart"):
    df1            = df.groupby([col]).count()
    df1['count']   = df1.iloc[:, 0]
    df1['angle']   = df1['count']/df1['count'].sum() * 2*pi
    
    n              = len(df1)
    color_list     = cycle(pkmn_colors)
    color          = [next(color_list)for i in range(n)]
    df1['color']   = color

    # Choose color
    fig = Plot_Pie(df1,title="Pie Chart")

    return fig

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def Plot_Pie_Parm(df,df_porf,col,title="Pie Chart"):
    df1            = df.copy()
    df1            = df1.sort_values(by=[col],ascending=False)

    df1['count']   = df['Name']
    df1['angle']   = df1[col]/df1[col].sum() * 2*pi
    df_data        = pd.merge(df1, df_porf, on='Name',how='inner')

    # Choose color
    df_c            = pd.DataFrame()
    df_c['Type']    = df_porf['Type'].unique()
    n               = len(df_c)

    color_list      = cycle(pkmn_colors)
    color           = [next(color_list)for i in range(n)]
    df_c['color']   = color
    
    df_data        = pd.merge(df_data, df_c, on='Type',how='inner')
    fig            = Plot_Pie(df_data,title=col)

    return fig

### Plot Pie
def Plot_Pie(df,title="Pie Chart"):

    fig = figure(plot_height=320,title=title, toolbar_location=None,
           tools="hover", tooltips="@Type: @count", x_range=(-0.5, 1.0))

    fig.wedge(x=0.25, y=1, radius=0.45,
        start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
        line_color="white", fill_color='color', legend_field='Type', source=df)

    fig.legend.location = "top_left"
    fig.legend.orientation = "horizontal"
    fig.axis.axis_label=None
    fig.axis.visible=False
    fig.grid.grid_line_color = None

    return fig

def Plot_Bars_Per(df,col):
    tooltips = [
          ("Name", "@Name"),
          ("Substation", "@Loc"),
          ("Year", "@Year"),
          ("HI", "@HI"),
          ("EL", "@EL"),
          ("Type", "@Type"), 
    ]  
    
    df['color']  = [limit_color(i) for i in df[col].values]
    df           = df.sort_values(by=[col],ascending=False)
    group        = df['Name'].values
    source = ColumnDataSource(df)
    fig = Plot_Bars(source,group,tooltips,col)
    return fig

def Plot_Bars_Cr(df,df_porf,col):
    tooltips = [
          ("Name", "@Name"),
          ("MTTR", "@MTTR"),
          #("Year", "@Year"),
          #("HI", "@HI"),
          #("EL", "@EL"),
          ("Type", "@Type"), 
    ]  

    # Choose color
    df_c            = pd.DataFrame()
    df_c['Type']    = df_porf['Type'].unique()
    n               = len(df_c)

    color_list      = cycle(pkmn_colors)
    color           = [next(color_list)for i in range(n) ]
    df_c['color']   = color
    
    df              = df.drop(columns=['MTTR'])
    df_data         = pd.merge(df, df_porf, on='Name',how='inner')
    df_data         = pd.merge(df_data, df_c, on='Type',how='inner')

    df_data         = df_data.sort_values(by=[col],ascending=False)

    group           = df_data['Name'].values
    
    source          = ColumnDataSource(df_data)
    fig = Plot_Bars(source,group,tooltips,col)
    return fig


def Plot_Bars(source,group,TOOLTIPS,col,title='Pareto'):

    p = figure(plot_height=400, x_range=group, title=title,toolbar_location=None, tools="hover", tooltips=TOOLTIPS,sizing_mode= "stretch_width")

    p.vbar(x='Name', top=col, width=0.9,source=source, fill_color='color',line_color='color')

    p.y_range.start = 0
    p.xgrid.grid_line_color = None
    p.outline_line_color = None
    p.xaxis.major_label_text_font_size = '0pt'
    
    return p

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
def Plot_Scat_Per(df,col, radius='RE'):

    tooltips = [
          ("Name", "@Name"),
          ("Substation", "@Loc"),
          ("Year", "@Year"),
          ("HI", "@HI"),
          ("EL", "@EL"),
          ("Type", "@Type"), 
    ]  

    df['color']  = [limit_color(i) for i in df[col].values]
    #df            = df.sort_values(by=[col],ascending=False)
    #group = df['Name'].values
    source = ColumnDataSource(df)

    fig = Plot_Scat(source,col,'Year',tooltips,radius)

    return fig


def Plot_Scat_RI(df,col, radius='RI'):

    tooltips = [
          ("Name", "@Name"),
          #("Substation", "@Loc"),
          #("Year", "@Year"),
          #("POF", "@POF"),
          #("EL", "@EL"),
          #("Type", "@Type"), 
    ]  

    # Normalize the criticality
    X       = df[radius].to_numpy()
    
    # # # # # # # # # # # # # # # # # # # # # # #
    # Delete, delete, delete
    X       = np.nan_to_num(X,nan=0)
    # # # # # # # # # # # # # # # # # # # # # # #
    
    df['r'] = X / np.linalg.norm(X)

    df['color']  = [limit_color(i) for i in df['r'].values]
    #df['r']      = (1+df['r'])/16
    df['r']      = (1+df['r'])


    source = ColumnDataSource(df)

    fig = Plot_Scat(source,col,'POF',tooltips,'r')

    return fig

def Plot_Scat(source,col,x,TOOLTIPS,radius):
    

    fig = figure(plot_height=400, title="Scatter matrix " + col,toolbar_location=None, tools="hover", tooltips=TOOLTIPS,sizing_mode= "stretch_width")
    fig.scatter(y=col, x=x, radius=radius,fill_color='color', fill_alpha=0.5,line_color=None,source=source)

    fig.xgrid.grid_line_color = None
    fig.outline_line_color = None
    fig.grid.grid_line_color = None

    return fig


def Plot_Stacker(df):

    df           = df.sort_values(by=['RI'],ascending=False)

    max_year  = df['Year'].max()
    min_year  = df['Year'].min()
    df_test   = df[df['Year']==max_year] 
    names     = list(df_test.loc[df_test['Cr'].nlargest(6).index]['Name'].values)

    df_final  = df[df['Name'].isin(names) ]
    TOOLTIPS = [
        ("isotopologue", "$name"),
        ]
    fig = figure(x_range=(min_year, max_year),plot_height=400, title="Scatter matrix ",toolbar_location=None, tools="hover",sizing_mode= "stretch_width",tooltips=TOOLTIPS)
    table = pd.pivot_table(df_final, values='RI', index=['Year'],columns=['Name'])
    table.index.name = None

    table = table[names]

    #name = list(table.columns)
    color_list      = cycle(pkmn_colors)
    color = [next(color_list)for i in range(len(names)) ]
    

    source = ColumnDataSource(table)
    fig.varea_stack(stackers=names, x='index', source=source,color=color, legend_label=names)

    fig.xgrid.grid_line_color = None
    fig.outline_line_color = None
    fig.grid.grid_line_color = None

    # reverse the legend entries to match the stacked order
    fig.legend.items.reverse()
    fig.legend.location = "top_left"
    #fig.legend.orientation = "horizontal"


    return fig
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #

def plot_condition_forecast(Cond,Asset,N_Days):
    
    df    = Asset.cond[Cond].historic_data
    #->fig      = figure(title="PywerAM - Condition forecasting: " + Cond, plot_height=500, plot_width=950,background_fill_color='#808080',x_axis_type='datetime')
    fig      = figure(title="PywerAM - Condition forecasting: " + Cond, plot_height=500, plot_width=750,x_axis_type='datetime',tools=[])
    
    # Plot measurements
    #->fig.circle(df["Date"], df["val_nor"],fill_alpha=0.5, size=5)
    fig.circle(df["Date"], df["val_nor"], size=8)
    
    # Operatiing conditions
    date_test_beg      = df['Date'].min().date()
    date_test_end      = df['Date'].max().date()
    delta_t            = date_test_end-date_test_beg
    date_oper          = [date_test_beg + datetime.timedelta(days=x) for x in range(delta_t.days)]
    cond_oper          = [Asset.cond[Cond].eval_cond_fit_func(date) for date in date_oper]
    data               = {'x': date_oper,'y': cond_oper}
    data               = pd.DataFrame.from_dict(data)
    fig.line(data['x'], data['y'],color='#A6CEE3')
    
    # Forecast
    date_for      = [date_test_end + datetime.timedelta(days=x) for x in range(N_Days)]
    cond_for      = [Asset.cond[Cond].eval_cond_fit_func(date) for date in date_for]
    data          = {'x': date_for,'y': cond_for}
    data          = pd.DataFrame.from_dict(data)
    fig.line(data['x'], data['y'],color='#B2DF8A')
    
    # Pre-historic data 
    #->date_beg        = l_asset.data['Opt_Year']
    #->delta_t         = date_test_beg-date_beg
    #->date_oper_beg   = [date_beg + datetime.timedelta(days=x) for x in range(delta_t.days)]
    #->cond_beg        = [l_asset.cond[Cond].eval_cond_fit_func(date) for date in date_oper_beg]
    #->data            = {'x': cond_beg,'y': cond_beg}
    #->data            = pd.DataFrame.from_dict(data)
    #->p.line(data['x'], data['y'],color='#B2DF8A')
    
    return fig
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #    
def Plot_HI_Forecast_Stacked(ASSET,TIME):
    p             = figure(title="PyweAM -  health index (HI)", plot_height=500, plot_width=950,x_axis_type='datetime')
    Cond_list     = list(ASSET.cond.keys())
    n =0
    df            = pd.DataFrame()  
    df['date']    = TIME
    w_t           = ASSET.w_total
    
    for cond in Cond_list: 
        cond_for  = [ASSET.cond[cond].eval_cond_fit_func(date) for date in TIME]
        cond_for  = np.array(cond_for)
        w_pu      = ASSET.cond[cond].w/w_t
        df[cond]  = cond_for*w_pu
        n         +=1
    
    if n<3:
        color = all_palettes['Category20'][3]
        color = color[0:n] 
    else:
        color = all_palettes['Category20'][n]

    p.varea_stack(stackers=Cond_list, x='date', color=color, legend_label=Cond_list, source=df, alpha=0.85)
    p.legend.items.reverse()
    
    hi            = [ASSET.Eval_Asset_Condition(date) for date in TIME]
    data          = {'x': TIME,'y': hi}
    data          = pd.DataFrame.from_dict(data)
    p.line(data['x'], data['y'],color='#000000')

    p.legend.orientation = "horizontal"
    p.legend.location = "top_left"
    
    return p    
    
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #      
def plot_condition_assessment(DF):
    #fig      = figure(title="PyweAM", plot_height=500, plot_width=950,background_fill_color='#808080',x_axis_type='datetime')
    fig      = figure(title="PyweAM", plot_height=250, plot_width=350,x_axis_type='datetime',tools=[])
    fig.line(DF['Date'], DF['HI'], legend_label="HI" ,color='#A6CEE3')   
    fig.line(DF['Date'], DF['lambda'], legend_label="FR",color='#B2DF8A')   
    fig.line(DF['Date'], DF['POF'].div(100), legend_label="POF", color='#FF0000')   
    return fig

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #            
def plot_decision_making(DF):   
    x     = DF.id.unique()    
    fig     = figure(x_range=x,title="PyweAM - Asset: ", plot_height=500, plot_width=900)
    
    l_group = DF.groupby(['scenario']) 
    n = 0
    l_n   = len(l_group)
    if l_n<3:
        color = all_palettes['Set1'][3]
    else:
        color = all_palettes['Set1'][l_n]
        
    for name,scen in l_group:
        l_df = scen
        dx = (1/(l_n+1))
        x  = -0.5+(n+1)*dx
        w  = 1/(l_n+1)
        fig.vbar(x=dodge('id', x, range=fig.x_range), top='PV', width=0.8*dx, source=l_df,
        color=color[n], legend_label=name)
        n +=1  
    return fig
    
#
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #  
def plot_scenario(scenario_name,plot,sce):   
    fig             = figure(title="PyweAM - Asset: "+scenario_name, plot_height=500, plot_width=950,x_axis_type='datetime')    
    
    if plot == 'RI':
        table = 'RI'
        col   = 'RI'
    elif plot == 'Cum_Sum_PV':
        table = 'CF'
        col   = 'PV'
        
    def compute_def(data):
        n = True
        df = pd.DataFrame()
        for asset_id in data:
            if n:
                df['Date'] = data[asset_id][table].date
                df['Val'] = data[asset_id][table][col]
                n = False
            df['Val'] += data[asset_id][table][col]
        if col=='PV':
            df['Val']  = df['Val'].cumsum() 
        return df

    l_data = sce['Base'] 
    df     = compute_def(l_data)
    fig.line(df["Date"], -df["Val"])
    
    l_data = sce[scenario_name] 
    df     = compute_def(l_data)    
    fig.line(df["Date"], -df["Val"], color='#FF0000',)   
    
    return fig 
