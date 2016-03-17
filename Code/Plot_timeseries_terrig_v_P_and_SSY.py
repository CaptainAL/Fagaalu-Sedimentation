# -*- coding: utf-8 -*-
"""
Created on Mon Mar 14 04:03:08 2016

@author: Alex
"""

## Plot time series charts of sediment deposition

import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import numpy as np
from numpy import sin,cos,radians,arctan2,degrees
import gpxpy
from mpl_toolkits.basemap import Basemap
import utm
import shapefile ## from pyshp
import datetime as dt
pd.set_option('display.large_repr', 'info')
## Set Directories
maindir = 'C:/Users/Alex/Documents/GitHub/Fagaalu-Sedimentation/'
datadir = maindir+'Data/'
GISdir = datadir+'GIS/'
rawfig= maindir+'rawfig/'

def show_plot(show=False,fig=figure):
    if show==True:
        plt.draw()
        plt.show()
    return
def savefig(save=True,filename=''):
    if save==True:
        plt.savefig(filename+'.pdf') ## for publication
        plt.savefig(filename+'.png') ## for manuscript
    return
def pltdefault():
    global figdir
    plt.rcdefaults()
    #figdir = datadir+'samoa/WATERSHED_ANALYSIS/GoodFigures/rawfigoutput/'
    return  
def letter_subplots(fig,x=0.1,y=0.95,vertical='top',horizontal='right',Color='k',font_size=10,font_weight='bold'):
    sub_plot_count = 0
    sub_plot_letters = {0:'(a)',1:'(b)',2:'(c)',3:'(d)',4:'(e)',5:'(f)',6:'(g)',7:'(h)',8:'(i)'}
    for ax in fig.axes:
        ax.text(x,y,sub_plot_letters[sub_plot_count],verticalalignment=vertical, horizontalalignment=horizontal,transform=ax.transAxes,color=Color,fontsize=font_size,fontweight=font_weight)
        sub_plot_count+=1
    plt.draw()
    return 


#### Plot each SedPod/SedTube over time
def Terr_Sed_v_Precip_timeseries(data,max_y=40, show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(10,6))
    ## Plot Sed data
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        axes1=axes.reshape(-1)
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data_to_plot = data[data['Pod(P)/Tube(T)'] == loc]
        ## calculate weight of terrigenous sed
        data_to_plot['Total Terr(gm2d)'] = data_to_plot['Total(gm2d)'] * data_to_plot['Total(%terr)']/100
        ## Select the points with NA values and replace with the ylim, plot all as grey
        data_to_plot.replace('NaN',max_y)['Total Terr(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='grey',alpha=0.5)
        ## create dataframe of sed and precip
        sed = pd.DataFrame({'Total Terr(gm2d)':data_to_plot['Total Terr(gm2d)'].values,'Precip':data_to_plot['Precip'].values}, index=data_to_plot['Month'].values)
        ## Plot data values in color over the grey
        sed['Total Terr(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='r')
        ## Plot precip data
        ax2=axes1[x].twinx()
        ax2.yaxis.set_ticks_position('right')
        ax2.plot(axes1[x].get_xticks(),sed['Precip'],ls='-',color='b')  
        ax2.set_ylim(0,2000), ax2.xaxis.set_visible(False),ax2.yaxis.set_visible(False)
        if x==2 or x==5 or x==8:
            ax2.yaxis.set_visible(True), ax2.set_ylabel('Precip (mm)',color='b')
        ## Format subplot
        axes1[x].xaxis.set_visible(False)
        axes1[x].tick_params(labelsize=8),ax2.tick_params(labelsize=8)
        axes1[x].xaxis.grid(False),ax2.yaxis.grid(False)
        # Subplot title eg P1A
        axes1[x].text(0.05,.95,loc,verticalalignment='top', horizontalalignment='left',transform=axes1[x].transAxes)
    ## Label left axes
    axes[0,0].set_ylabel('NORTHERN \n g/'+r'$m^2$'+'/day'), axes[1,0].set_ylabel('CENTRAL \n g/'+r'$m^2$'+'/day'), axes[2,0].set_ylabel('SOUTHERN \n g/'+r'$m^2$'+'/day') 
    axes[0,0].set_ylim(0,max_y)
    ## turn on axes
    for ax in axes[2]:
        ax.xaxis.set_visible(True)
    axes[2,0].set_xticklabels(data_to_plot['Month'].values)
    #plt.suptitle('Sediment Accumulation in SedPods over time',fontsize=16)
    plt.tight_layout(pad=0.2)
    show_plot(show,fig)
    savefig(save,filename)
    return
#Terr_Sed_v_Precip_timeseries(SedPods,max_y=40,show=True,save=True,filename=rawfig+'SedPods-terrig and precip')
#Terr_Sed_v_Precip_timeseries(SedTubes,max_y=650,show=True,save=True,filename=rawfig+'SedTubes-terrig and precip')
    

#### Plot each SedPod/SedTube over time
def Terr_Sed_v_SSY_timeseries(data,max_y=40, show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(10,6))
    ## Plot Sed data
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        axes1=axes.reshape(-1)
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data_to_plot = data[data['Pod(P)/Tube(T)'] == loc]
        ## calculate weight of terrigenous sed
        data_to_plot['Total Terr(gm2d)'] = data_to_plot['Total(gm2d)'] * data_to_plot['Total(%terr)']/100
        ## Select the points with NA values and replace with the ylim, plot all as grey
        data_to_plot.replace('NaN',max_y)['Total Terr(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='grey',alpha=0.5)
        ## create dataframe of sed and precip
        sed = pd.DataFrame({'Total Terr(gm2d)':data_to_plot['Total Terr(gm2d)'].values,'SSY':data_to_plot['SSY'].values}, index=data_to_plot['SSY'].values)
        ## Plot data values in color over the grey
        sed['Total Terr(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='r')
        ## Plot precip data
        ax2=axes1[x].twinx()
        ax2.yaxis.set_ticks_position('right')
        ax2.plot(axes1[x].get_xticks(),sed['SSY'],ls='-',color='r')  
        ax2.set_ylim(0,250), ax2.xaxis.set_visible(False),ax2.yaxis.set_visible(False)
        if x==2 or x==5 or x==8:
            ax2.yaxis.set_visible(True), ax2.set_ylabel('SSY (tons)',color='r')
        ## Format subplot
        axes1[x].xaxis.set_visible(False)
        axes1[x].tick_params(labelsize=8),ax2.tick_params(labelsize=8)
        axes1[x].xaxis.grid(False),ax2.yaxis.grid(False)
        # Subplot title eg P1A
        axes1[x].text(0.05,.95,loc,verticalalignment='top', horizontalalignment='left',transform=axes1[x].transAxes)
    ## Label left axes
    axes[0,0].set_ylabel('NORTHERN \n g/'+r'$m^2$'+'/day'), axes[1,0].set_ylabel('CENTRAL \n g/'+r'$m^2$'+'/day'), axes[2,0].set_ylabel('SOUTHERN \n g/'+r'$m^2$'+'/day') 
    axes[0,0].set_ylim(0,max_y)
    ## turn on axes
    for ax in axes[2]:
        ax.xaxis.set_visible(True)
    axes[2,0].set_xticklabels(data_to_plot['Month'].values)
    #plt.suptitle('Sediment Accumulation in SedPods over time',fontsize=16)
    plt.tight_layout(pad=0.2)
    show_plot(show,fig)
    savefig(save,filename)
    return
#Terr_Sed_v_SSY_timeseries(SedPods,max_y=40,show=True,save=True,filename=rawfig+'SedPods-terrig and ssy')
#Terr_Sed_v_SSY_timeseries(SedTubes,max_y=650,show=True,save=True,filename=rawfig+'SedTubes-terrig and ssy')

#### Plot each SedPod/SedTube over time
def Total_Sed_v_Precip_timeseries(data,max_y=40, show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(10,6))
    ## Plot Sed data
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        axes1=axes.reshape(-1)
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data_to_plot = data[data['Pod(P)/Tube(T)'] == loc]
        ## Select the points with NA values and replace with the ylim, plot all as grey
        data_to_plot.replace('NaN',max_y)['Total(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='grey',alpha=0.5)
        ## create dataframe of sed and precip
        sed = pd.DataFrame({'Total(gm2d)':data_to_plot['Total(gm2d)'].values,'Precip':data_to_plot['Precip'].values}, index=data_to_plot['Month'].values)
        ## Plot data values in color over the grey
        sed['Total(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='w')
        ## Plot precip data
        ax2=axes1[x].twinx()
        ax2.yaxis.set_ticks_position('right')
        ax2.plot(axes1[x].get_xticks(),sed['Precip'],ls='-',color='b')  
        ax2.set_ylim(0,2000), ax2.xaxis.set_visible(False),ax2.yaxis.set_visible(False)
        if x==2 or x==5 or x==8:
            ax2.yaxis.set_visible(True), ax2.set_ylabel('Precip (mm)',color='b')
        ## Format subplot
        axes1[x].xaxis.set_visible(False)
        axes1[x].tick_params(labelsize=8),ax2.tick_params(labelsize=8)
        axes1[x].xaxis.grid(False),ax2.yaxis.grid(False)
        # Subplot title eg P1A
        axes1[x].text(0.05,.95,loc,verticalalignment='top', horizontalalignment='left',transform=axes1[x].transAxes)
    ## Label left axes
    axes[0,0].set_ylabel('NORTHERN \n g/'+r'$m^2$'+'/day'), axes[1,0].set_ylabel('CENTRAL \n g/'+r'$m^2$'+'/day'), axes[2,0].set_ylabel('SOUTHERN \n g/'+r'$m^2$'+'/day') 
    axes[0,0].set_ylim(0,max_y)
    ## turn on axes
    for ax in axes[2]:
        ax.xaxis.set_visible(True)
    axes[2,0].set_xticklabels(data_to_plot['Month'].values)
    #plt.suptitle('Sediment Accumulation in SedPods over time',fontsize=16)
    plt.tight_layout(pad=0.2)
    show_plot(show,fig)
    savefig(save,filename)
    return
#Total_Sed_v_Precip_timeseries(SedPods,max_y=40,show=True,save=True,filename=rawfig+'SedPods-total and precip')
#Total_Sed_v_Precip_timeseries(SedTubes,max_y=650,show=True,save=True,filename=rawfig+'SedTubes-total and precip')
    

#### Plot each SedPod/SedTube over time
def Total_Sed_v_SSY_timeseries(data,max_y=40, show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,sharex=True,figsize=(10,6))
    ## Plot Sed data
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        axes1=axes.reshape(-1)
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data_to_plot = data[data['Pod(P)/Tube(T)'] == loc]
        ## Select the points with NA values and replace with the ylim, plot all as grey
        data_to_plot.replace('NaN',max_y)['Total(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='grey',alpha=0.5)
        ## create dataframe of sed and precip
        sed = pd.DataFrame({'Total(gm2d)':data_to_plot['Total(gm2d)'].values,'SSY':data_to_plot['SSY'].values}, index=data_to_plot['SSY'].values)
        ## Plot data values in color over the grey
        sed['Total(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='w')
        ## Plot precip data
        ax2=axes1[x].twinx()
        ax2.yaxis.set_ticks_position('right')
        ax2.plot(axes1[x].get_xticks(),sed['SSY'],ls='-',color='r')  
        ax2.set_ylim(0,250), ax2.xaxis.set_visible(False),ax2.yaxis.set_visible(False)
        if x==2 or x==5 or x==8:
            ax2.yaxis.set_visible(True), ax2.set_ylabel('SSY (tons)',color='r')
        ## Format subplot
        axes1[x].xaxis.set_visible(False)
        axes1[x].tick_params(labelsize=8),ax2.tick_params(labelsize=8)
        axes1[x].xaxis.grid(False),ax2.yaxis.grid(False)
        # Subplot title eg P1A
        axes1[x].text(0.05,.95,loc,verticalalignment='top', horizontalalignment='left',transform=axes1[x].transAxes)
    ## Label left axes
    axes[0,0].set_ylabel('NORTHERN \n g/'+r'$m^2$'+'/day'), axes[1,0].set_ylabel('CENTRAL \n g/'+r'$m^2$'+'/day'), axes[2,0].set_ylabel('SOUTHERN \n g/'+r'$m^2$'+'/day') 
    axes[0,0].set_ylim(0,max_y)
    ## turn on axes
    for ax in axes[2]:
        ax.xaxis.set_visible(True)
    axes[2,0].set_xticklabels(data_to_plot['Month'].values)
    #plt.suptitle('Sediment Accumulation in SedPods over time',fontsize=16)
    plt.tight_layout(pad=0.2)
    show_plot(show,fig)
    savefig(save,filename)
    return
#Total_Sed_v_SSY_timeseries(SedPods,max_y=40,show=True,save=True,filename=rawfig+'SedPods-terrig and ssy')
#Total_Sed_v_SSY_timeseries(SedTubes,max_y=650,show=True,save=True,filename=rawfig+'SedTubes-total and ssy')


#### Plot each SedPod/SedTube over time
def Sed_timeseries_mean_NS(data,max_y=40, show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(2, 1,sharey=True,figsize=(12,6))

    north_reef = ['1A','1B','1C','2A','2C']
    south_reef = ['2B','3A','3B','3C']
    if 'T1A' in data['Pod(P)/Tube(T)'].values:
        north_reef = ['T'+x for x in north_reef] 
        south_reef = ['T'+x for x in south_reef] 
    if 'P1A' in data['Pod(P)/Tube(T)'].values:
        north_reef = ['P'+x for x in north_reef] 
        south_reef = ['P'+x for x in south_reef] 
    
    north_sed = data[data['Pod(P)/Tube(T)'].isin(north_reef)].dropna()
    south_sed = data[data['Pod(P)/Tube(T)'].isin(south_reef)].dropna()

    sediment_mean_by_month= pd.DataFrame()
    ## Select Sed data
    for mon in Comp_XL.sheet_names[1:12]:
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        ## Mean organic
        north_mean_org = north_sed[north_sed['Month'] == mon]['Total Org(gm2d)'].mean()
        south_mean_org = south_sed[south_sed['Month'] == mon]['Total Org(gm2d)'].mean() 
        ## Mean terrigenous
        north_mean_terr = north_sed[north_sed['Month'] == mon]['Total Terr(gm2d)'].mean()
        south_mean_terr = south_sed[south_sed['Month'] == mon]['Total Terr(gm2d)'].mean()
        ## Mean Carbonate
        north_mean_carb = north_sed[north_sed['Month'] == mon]['Total Carb(gm2d)'].mean() 
        south_mean_carb = south_sed[south_sed['Month'] == mon]['Total Carb(gm2d)'].mean()  
        
        ## Aux Data
        precip = north_sed[north_sed['Month'] == mon]['Precip'].max()
        ssy = north_sed[north_sed['Month'] == mon]['SSY'].max()
        waves = north_sed[north_sed['Month'] == mon]['Waves'].max()
        
        sediment_mean_by_month = sediment_mean_by_month.append(pd.DataFrame({'North org':north_mean_org,'South org':south_mean_org,'North terr':north_mean_terr,'South terr':south_mean_terr,'North carb':north_mean_carb,'South carb':south_mean_carb,'Precip':precip,'SSY':ssy,'Waves':waves},index=[mon]))
        
    ## Plot data values
    sediment_mean_by_month[['North org','North terr','North carb']].plot(kind='bar',stacked=True,ax=axes[0],color=['g','r','b'])
    sediment_mean_by_month[['South org','South terr','South carb']].plot(kind='bar',stacked=True,ax=axes[1],color=['g','r','b'])
    for ax in axes:    
        ## Plot precip data
        ax2=ax.twinx()
        ax2.yaxis.set_ticks_position('right')
        ax2.plot(ax.get_xticks(),sediment_mean_by_month['Precip'],ls='-',color='b')  
        ax2.set_ylim(0,2000)
        ax2.xaxis.grid(False), ax2.yaxis.grid(False)
        for tl in ax2.get_yticklabels():
            tl.set_color('b')
        ## Plot SSY data
        ax3=ax.twinx()
        ax3.yaxis.set_ticks_position('right')
        ax3.plot(ax.get_xticks(),sediment_mean_by_month['SSY'],ls='-',color='r',label='SSY(tons)')  
        ax3.set_ylim(0,250)
        ax3.spines['right'].set_position(('axes', 1.2))
        for tl in ax3.get_yticklabels():
            tl.set_color('r')
        ## Plot Wave data
        ax4=ax.twinx()
        ax4.yaxis.set_ticks_position('right')
        ax4.plot(ax.get_xticks(),sediment_mean_by_month['Waves'],ls='-',color='k',label='MMSWH(m)')  
        ax4.set_ylim(0,2.5)
        ax4.spines['right'].set_position(('axes', 1.4))
        
        ax2.yaxis.set_visible(True), ax2.set_ylabel('Precip(mm)',color='b')
        ax3.yaxis.set_visible(True), ax3.set_ylabel('SSY(tons)',color='r')
        ax4.yaxis.set_visible(True), ax4.set_ylabel('MMSWH(m)',color='k')
    
    for ax in axes:
        ax.legend(fontsize=10)

    ## Label left axes
    axes[0].set_ylabel('NORTHERN \n g/'+r'$m^2$'+'/day') 
    axes[1].set_ylabel('SOUTHERN \n g/'+r'$m^2$'+'/day') 
    axes[0].set_ylim(0,max_y)
    axes[0].xaxis.set_visible(False)
    axes[0].xaxis.grid(False),axes[1].xaxis.grid(False)
    plt.tight_layout(pad=0.2)

    plt.subplots_adjust(top=0.95)
    show_plot(show,fig)
    savefig(save,filename)
    return
Sed_timeseries_mean_NS(SedPods,max_y=40,show=True,save=True,filename=figdir+'Mean Accumulation Timeseries/SedPods-monthly mean')
Sed_timeseries_mean_NS(SedTubes,max_y=650,show=True,save=True,filename=figdir+'Mean Accumulation Timeseries/SedTubes-monthly mean')