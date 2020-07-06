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
import matplotlib.pyplot as plt
import seaborn as sns



color_limits = ['#259B00','#CFE301','#FF5733','#900C3F']
hi_limits    = [0.25,0.5,0.75,1]
cum_ens_pof  = [0.85,0.95,0.99]

warn_colors =['#259B00','#CFE301','#FF5733','#900C3F','#339900','#99CC33','#FFCC00','#FF9966','#CC3300']
warn_colors = sns.color_palette(warn_colors)

my_colors        = ['#fff100',  # Grass
                    '#ff8c00',  # Fire
                    '#e81123',  # Water
                    '#ec008c',  # Bug
                    '#68217a',  # Poison
                    '#00188f',  # Electric
                    '#00bcf2',  # Fighting
                    '#00b294',  # Psychic
                    '#009e49',  # Rock
                    '#bad80a',  # Ghost
                   ]

pkmn_type_colors = ['#78C850',  # Grass
                    '#F08030',  # Fire
                    '#6890F0',  # Water
                    '#A8B820',  # Bug
                    '#A040A0',  # Poison
                    '#F8D030',  # Electric
                    '#C03028',  # Fighting
                    '#F85888',  # Psychic
                    '#B8A038',  # Rock
                    '#705898',  # Ghost
                    '#98D8D8',  # Ice
                    '#7038F8',  # Dragon
                   ]

my_col  = ['#e41a1c', '#377eb8', '#4daf4a', '#984ea3', '#ff7f00', '#ffff33', '#a65628', '#f781bf', '#999999']

def Plot_Bar_Energy_Suplied_Week(df,file_name):
    f, ax = plt.subplots(figsize=(14, 4))
    
    #pal = sns.color_palette("Set1")
    #print(pal.as_hex())

    warn_colors = sns.color_palette([my_col[0]])
    #sns.barplot(x="Day", y="ES_NO",   data=df,hue="Hour", palette=warn_colors, alpha=0.75,ax=ax,saturation=1)
    sns.barplot(x="Hour", y="ES_NO",   data=df, palette=warn_colors, alpha=0.75,ax=ax,saturation=1)
    warn_colors = sns.color_palette([my_col[1]])
    #sns.barplot(x="Day", y="ES_CO_0", data=df,hue="Hour", palette=warn_colors, alpha=0.75,ax=ax,saturation=1)
    sns.barplot(x="Hour", y="ES_CO_0", data=df, palette=warn_colors, alpha=0.75,ax=ax,saturation=1)
    warn_colors = sns.color_palette([my_col[2]])
    #sns.barplot(x="Day", y="ES_CO_1", data=df,hue="Hour", palette=warn_colors, alpha=0.75,ax=ax,saturation=1)
    sns.barplot(x="Hour", y="ES_CO_1", data=df, palette=warn_colors, alpha=0.75,ax=ax,saturation=1)
    
    # Plot labels
    import matplotlib.patches as mpatches
    patch_1 = mpatches.Patch(color=my_col[0], label='Normal Operation')
    patch_2 = mpatches.Patch(color=my_col[1], label='Cont.  Load Curtailment')
    patch_3 = mpatches.Patch(color=my_col[2], label='Cont. Open Line 21-11')
    plt.legend(handles=[patch_1, patch_2,patch_3])
    plt.ylabel('Energy Supplied - [MWh]')
    plt.savefig(file_name+'.pdf', bbox_inches = "tight")
    plt.close()

