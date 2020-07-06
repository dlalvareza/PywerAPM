from docx import Document
from docx.shared import Inches
from docx.shared import RGBColor
from datetime import datetime

import pandas as pd
from copy import deepcopy

###############################################################################
import geopandas
import contextily as ctx
from shapely import wkt
###############################################################################

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker


from ST_AM_Contingencies_Ploty import Radar_Plot_by_Asset, plot_historic_condition_by_asset


def Report_df(Assets,date_beg,Type=None,N_hours=0):
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
    
    

    hi = []
    for  n in asset_list:
        df = Assets.Asset_Portfolio[n].POF_R_Assessment(date_beg,1)
        if len(df['HI'].values)==0:
            hi.append(None)
        else:
            hi.append(df['HI'].values[-1])

    data_dic['HI']   = hi

    data_dic['EL']   = [Assets.Asset_Portfolio[n].elap_life for n in asset_list]
    
    # Location 
    data_dic['Lat'] =  [Assets.Asset_Location[Assets.Asset_Location.index==Assets.Asset_Portfolio[n].data['Location']].Lat.values[0] for n in asset_list]
    data_dic['Lon'] =  [Assets.Asset_Location[Assets.Asset_Location.index==Assets.Asset_Portfolio[n].data['Location']].Lon.values[0] for n in asset_list]

    # Return dataframe  
    df     = pd.DataFrame.from_dict(data_dic)
    df     = geopandas.GeoDataFrame(df, geometry=geopandas.points_from_xy(df.Lat, df.Lon), crs="EPSG:4326")
    df = df.to_crs(epsg=3857)

    #df     = df.to_crs()
    return df

def Test_Report_AP(data,assets):
    document = Document('STATIC/General_Report.docx')

    document.paragraphs[0].text = data['Name']
    document.paragraphs[1].text = data['Sub_title']
    report_date                 = datetime.date(datetime.now())
    document.paragraphs[2].text = str(report_date)

    df = Report_df(assets,report_date)
    # # # # # # # # # # # # # # #
    document.tables[0]._cells[0].paragraphs[0].text = str(df['Name'].count())
    document.tables[0]._cells[1].paragraphs[0].text = str(round(datetime.now().year-df['Year'].mean(),1))
    document.tables[0]._cells[2].paragraphs[0].text = str(round(df['HI'].mean(),2))
    document.tables[0]._cells[3].paragraphs[0].text = str(round(df['RE'].mean(),2))
    # # # # # # # # # # # # # # #
    
    
    def l_save_figure(table,cells,p_type='Plot'):
        if p_type=='Plot':
            plt.ylabel('Número de activos',fontsize= 14)
            plt.xticks(fontsize=12)
            plt.yticks(fontsize=12)
            ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%d"))
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            #ax.grid(color='grey', linestyle='-', linewidth=0.25, alpha=0.5)

        file_name = 'RESULTS/X1_REPORTS/X1_Images/fig.png'
        plt.savefig(file_name, bbox_inches='tight')
        plt.close()
        paragraph = document.tables[table]._cells[cells].paragraphs[0]
        run = paragraph.add_run()
        run.add_picture(file_name, height=Inches(2.4))
    
    # Hi plot
    ax = df['HI'].plot.hist(alpha=1,color='#e81123')
    l_save_figure(1,2)
    # EL plot 
    ax =df['EL'].plot.hist(alpha=1,color='#ff8c00')
    l_save_figure(2,2)
    # Operative life plot
    ax =df['Year'].plot.hist(alpha=1,color='#009e49')
    ax.xaxis.set_major_formatter(ticker.FormatStrFormatter("%d"))
    l_save_figure(2,3)
    # Asset location plot
    ax = df.plot(figsize=(10, 8), alpha=0.75, edgecolor='k',color='#00188f')
    ctx.add_basemap(ax, zoom=10)
    ax.set_axis_off()
    l_save_figure(1,3,p_type='map')

    
    # Each asset report
    n_table = 3
    for asset_id in  list(assets.Asset_Portfolio_List.index):
        # Add title 
        asset     = assets.Asset_Portfolio[asset_id]
        paragraph = document.add_paragraph(asset.name)
        paragraph.style = document.styles['Title']
        # Table with indexes 
        template = document.tables[0]
        tbl      = template._tbl
        new_tbl = deepcopy(tbl)
        paragraph._p.addnext(new_tbl)

        document.tables[n_table]._cells[0].paragraphs[0].text = asset.type
        document.tables[n_table]._cells[0].paragraphs[1].text = 'Tipo de activo'

        document.tables[n_table]._cells[1].paragraphs[0].text = asset.data['Location']
        document.tables[n_table]._cells[1].paragraphs[1].text = 'Subestación'

        document.tables[n_table]._cells[2].paragraphs[0].text = str(asset.data['Serial'])
        document.tables[n_table]._cells[2].paragraphs[1].text = 'Serial'

        document.tables[n_table]._cells[3].paragraphs[0].text = asset.data['UC']
        document.tables[n_table]._cells[3].paragraphs[1].text = 'UC'

        n_table +=1 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #  
        paragraph = document.add_paragraph()  

        file_name = 'RESULTS/X1_REPORTS/X1_Images/fig.png'
        plot_historic_condition_by_asset(asset,file_name)
        run = paragraph.add_run()
        run.add_picture(file_name, height=Inches(3))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        new_tbl = deepcopy(tbl)
        paragraph._p.addnext(new_tbl)
        document.tables[n_table]._cells[3].paragraphs[0].text = str(round(asset.mttr,2))
        document.tables[n_table]._cells[3].paragraphs[1].text = 'MTTR - [h]'

        document.tables[n_table]._cells[1].paragraphs[0].text = str(round(asset.elap_life,2))
        document.tables[n_table]._cells[1].paragraphs[1].text = 'EL'

        document.tables[n_table]._cells[0].paragraphs[0].text = str(round(asset.hi,2))
        document.tables[n_table]._cells[0].paragraphs[1].text = 'HI '

        document.tables[n_table]._cells[2].paragraphs[0].text = str(round(asset.re,2))
        document.tables[n_table]._cells[2].paragraphs[1].text = 'RE'
        n_table +=1 
# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #  
        paragraph = document.add_paragraph()  
        #file_name = 'RESULTS/X1_REPORTS/X1_Images/fig.png'
        Radar_Plot_by_Asset(asset,[report_date],file_name)
        run = paragraph.add_run()
        run.add_picture(file_name, height=Inches(3.5))

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
        new_tbl = deepcopy(tbl)
        paragraph._p.addnext(new_tbl)

        document.tables[n_table]._cells[0].paragraphs[0].text = asset.data['ID']
        document.tables[n_table]._cells[0].paragraphs[1].text = 'ID'

        document.tables[n_table]._cells[1].paragraphs[0].text = str(asset.data['Opt_Year'].year)
        document.tables[n_table]._cells[1].paragraphs[1].text = 'Año de aoperación'

        document.tables[n_table]._cells[2].paragraphs[0].text = asset.data['Brand']
        document.tables[n_table]._cells[2].paragraphs[1].text = 'Marca'

        document.tables[n_table]._cells[3].paragraphs[0].text = asset.data['Model']
        document.tables[n_table]._cells[3].paragraphs[1].text = 'Modelo'
        n_table +=1 

        document.add_page_break()
        
    
    #Save document 
    document.save('RESULTS/X1_REPORTS/CONDITION.docx')

