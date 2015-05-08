# -*- coding: utf-8 -*-
"""
Created on Tue Oct 14 17:21:48 2014

@author: Alex
"""

## Plot bar charts of sediment deposition/composition over Faga'alu Basemap 

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
plt.close('all')
## Set Pandas display options
pd.set_option('display.large_repr', 'truncate')
pd.set_option('display.width', 180)
pd.set_option('display.max_rows', 25)
pd.set_option('display.max_columns', 10)

## Set Directories
maindir =  'C:/Users/Alex/Documents/GitHub/Fagaalu-Sedimentation/'
datadir = maindir+'Data/'
GISdir = datadir+'GIS/'
figdirPods= maindir+'Figures/SedPods/'
figdirTubes= maindir+'Figures/SedTubes/'
rawfig= maindir+'rawfig/'

## Figure formatting
#publishable =  plotsettings.Set('GlobEnvChange')    ## plotsettings.py
#publishable.set_figsize(n_columns = 2, n_rows = 2)
mpl.rc_file(maindir+'johrc.rc')
mpl.rcParams['savefig.directory']=maindir+'rawfig/'
mpl.rcParams
## Ticks
my_locator = matplotlib.ticker.MaxNLocator(4)



def show_plot(show=False,fig=figure):
    if show==True:
        plt.draw()
        plt.show()
def logaxes(log=False,fig=figure):
    if log==True:
        print 'log axes'
        for ax in fig.axes:
            ax.set_yscale('log'), ax.set_xscale('log')
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
    
# Open Spreadsheet of data
XL =pd.ExcelFile(datadir+'CRCP Sediment Data Bulk Weight and Composition.xlsx')
Precip = pd.DataFrame.from_csv(datadir+'Fagaalu_rain_gauge_FILLED.csv').resample('M',how='sum')

SedPods, SedTubes = pd.DataFrame(),pd.DataFrame()
count = 0
for sheet in XL.sheet_names:
    count +=1
    ## get start, end dates and add precip and Q
    sampleDates = XL.parse(sheet,parse_cols='A:B',index_col=1,parse_dates=True)[:2] 
    start, end = pd.to_datetime(sampleDates.index[0]), pd.to_datetime(sampleDates.index[1])
    precip_month = Precip[start:end].sum()[0]
    print 'start: '+str(start)+' end: '+str(end)+' precip: '+"%.0f"%precip_month
    
    Data = XL.parse(sheet,header=7,na_values=['NAN','N/A (disturbed)'],parse_cols='A:D,F:L')
    Data = Data.replace('NO SED',0)
    Data = Data.replace('N/A (disturbed)',np.NaN)
    Data['Total(g)'] = Data['Mass Sand Fraction'] + Data['Mass Fine Fraction']
    ## Get rid of negative values
    Data['Total(g)']= Data['Total(g)'][Data['Total(g)']>=0]
    Data['Mass Sand Fraction']= Data['Mass Sand Fraction'][Data['Mass Sand Fraction']>=0]
    Data['Mass Fine Fraction']= Data['Mass Fine Fraction'][Data['Mass Fine Fraction']>=0]    
    ## Convert to g/m2/day
    Data['Total(gm2d)'] = Data['Total(g)']/Data['Area(m2)']/Data['Days deployed:']
    Data['Mass Sand Fraction'] = Data['Mass Sand Fraction']/Data['Area(m2)']/Data['Days deployed:']
    Data['Mass Fine Fraction'] = Data['Mass Fine Fraction']/Data['Area(m2)']/Data['Days deployed:']
    ## Round
    round_num = 5
    Data['Total(gm2d)']=Data['Total(gm2d)'].round(round_num)
    Data['Mass Sand Fraction']=Data['Mass Sand Fraction'].round(round_num)
    Data['Mass Fine Fraction']=Data['Mass Fine Fraction'].round(round_num)
    
    ## Add Month
    Data['Month'] = sheet
    Data['start'] =  start
    Data['end'] = end
    ## Add Monthly precip
    Data['Precip'] = precip_month
    ## Categorize by Tubes and Pods
    Pods = Data[Data['Pod(P)/Tube(T)'].isin(['P1A','P2A','P3A','P1B','P2B','P3B','P1C','P2C','P3C'])]
    Tubes = Data[Data['Pod(P)/Tube(T)'].isin(['T1A','T2A','T3A','T1B','T2B','T3B','T1C','T2C','T3C'])]
    ## Add to All Samples
    SedPods = SedPods.append(Pods)
    SedTubes = SedTubes.append(Tubes)

substrate = {'P3A':'coral','P3B':'coral','P3C':'coral','P2A':'mud','P2B':'coral','P2C':'coral','P1A':'sand','P1B':'sand','P1C':'coral',
'T3A':'coral','T3B':'coral','T3C':'coral','T2A':'mud','T2B':'coral','T2C':'coral','T1A':'sand','T1B':'sand','T1C':'coral'}
sub_colors={'coral':'blue','mud':'red','sand':'green'}
    
#### Plot each SedPod/SedTube over time
def Sed_timeseries(data,max_y=40, show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(10,6))
    labels=['coral','mud','sand','No Data']
    colors=['blue','red','green','grey']
    bars=[axes[0,2].bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]
    lines= axes[0,2].plot(0,0,color='k',label='Precip(mm)')
    handles, labels = axes[0,2].get_legend_handles_labels()
    ## Plot Sed data
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        print loc
        axes1=axes.reshape(-1)
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data_to_plot = data[data['Pod(P)/Tube(T)'] == loc]
        ## Select the points with NA values and replace with the ylim, plot all as grey
        data_to_plot.replace('NaN',max_y)['Total(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='grey',alpha=0.5)
        ## Plot data values in color over the grey
        sed = pd.DataFrame({'Total(gm2d)':data_to_plot['Total(gm2d)'].values,'Precip':data_to_plot['Precip'].values}, index=data_to_plot['Month'].values)
        sed['Total(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color=sub_colors[substrate[loc]])
        ## Plot precip data
        ax2=axes1[x].twinx()
        ax2.yaxis.set_ticks_position('right')
        ax2.plot(axes1[x].get_xticks(),sed['Precip'],ls='-',color='k')  
        ax2.set_ylim(0,2000), ax2.xaxis.set_visible(False),ax2.yaxis.set_visible(False)
        if x==2 or x==5 or x==8:
            ax2.yaxis.set_visible(True), ax2.set_ylabel('mm')
        ## Format subplot
        axes1[x].xaxis.set_visible(False)
        # Subplot title eg P1A
        axes1[x].text(0.05,.95,loc,verticalalignment='top', horizontalalignment='left',transform=axes1[x].transAxes)
        ## Mean line and number
        axes1[x].axhline(y=data_to_plot['Total(gm2d)'].mean(),ls='--',color='b')
        axes1[x].annotate('%.1f'%data_to_plot['Total(gm2d)'].mean(),(1,data_to_plot['Total(gm2d)'].mean()+1),textcoords='data',size=9)
        axes1[x].tick_params(labelsize=8),ax2.tick_params(labelsize=8)
        axes1[x].xaxis.grid(False),ax2.yaxis.grid(False)
    ## Label left axes
    axes[0,0].set_ylabel('NORTHERN \n g/'+r'$m^2$'+'/day'), axes[1,0].set_ylabel('CENTRAL \n g/'+r'$m^2$'+'/day'), axes[2,0].set_ylabel('SOUTHERN \n g/'+r'$m^2$'+'/day') 
    axes[0,0].set_ylim(0,max_y)
    ## turn on axes
    for ax in axes[2]:
        ax.xaxis.set_visible(True)
    axes[2,0].set_xticklabels(data_to_plot['Month'].values)
    #plt.suptitle('Sediment Accumulation in SedPods over time',fontsize=16)
    plt.tight_layout(pad=0.2)
    fig.legend(handles,labels,'upper center',ncol=5)
    plt.subplots_adjust(top=0.95)
    show_plot(show,fig)
    savefig(save,filename)
    return
#Sed_timeseries(SedPods,max_y=40,show=True,save=True,filename=rawfig+'SedPods-bulkweight and precip')
#Sed_timeseries(SedTubes,max_y=650,show=True,save=True,filename=rawfig+'SedTubes-bulkweight and precip')


#### Plot each SedPod/SedTube over time, separating the Coarse/Fine fraction
def Sed_fraction_timeseries(data,max_y=40,plot_health_thresholds=False,show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(10,6))
    labels=['coarse','fines','no data']
    colors=['blue','green','grey']
    bars=[axes[0,2].bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]
    lines= axes[0,2].plot(0,0,color='k',label='Precip(mm)')
    handles, labels = axes[0,2].get_legend_handles_labels()
    ## Plot Sed data
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        axes1=axes.reshape(-1)
        ## Plot Coral health thresholds
        if plot_health_thresholds==True:
            axes1[x].axhspan(0, 100, facecolor='g',alpha=.75,zorder=1)
            axes1[x].axhspan(100, 300, facecolor='y',alpha=.75,zorder=1)
            axes1[x].axhspan(300, 500, facecolor='orange',alpha=.75,zorder=1)
            axes1[x].axhspan(500, 2000, facecolor='r',alpha=.75,zorder=1)   
            ## Label Coral health thresholds
            axes1[x].annotate('stress recruits',(4,150),textcoords='data',rotation=0,size=14,color='y',zorder=2)
            axes1[x].annotate('stress colonies',(4,350),textcoords='data',rotation=0,size=14,color='orange',zorder=2)
            axes1[x].annotate('lethal',(4,550),textcoords='data',rotation=0,size=14,color='r',zorder=2) 
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data_to_plot = data[data['Pod(P)/Tube(T)'] == loc]        
        ## Select the points with NA values and replace with the ylim, plot all as grey
        data_to_plot.replace('NaN',max_y)['Total(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='grey',alpha=0.5,zorder=3)
        ## Plot data values in color over the grey
        sed = pd.DataFrame({'Coarse':data_to_plot['Mass Sand Fraction'].values,'Fine':data_to_plot['Mass Fine Fraction'].values,'Precip':data_to_plot['Precip'].values}, index=data_to_plot['Month'].values)
        sed[['Coarse','Fine']].plot(kind='bar',stacked=True,ax=axes1[x],legend=False,zorder=5)
        ## Plot precip data
        ax2=axes1[x].twinx()
        ax2.yaxis.set_ticks_position('right')
        ax2.plot(axes1[x].get_xticks(),sed['Precip'],ls='-',color='k')  
        ax2.set_ylim(0,2000), ax2.xaxis.set_visible(False),ax2.yaxis.set_visible(False)
        if x==2 or x==5 or x==8:
            ax2.yaxis.set_visible(True), ax2.set_ylabel('mm')
        ## Format subplot
        axes1[x].xaxis.set_visible(False)
        axes1[x].xaxis.grid(False),ax2.yaxis.grid(False)
        axes1[x].tick_params(labelsize=8),ax2.tick_params(labelsize=8)
        # Subplot title eg P1A
        axes1[x].text(0.05,.95,loc,verticalalignment='top', horizontalalignment='left',transform=axes1[x].transAxes)
        ## Mean line and number
        #axes1[x].axhline(y=data_to_plot['Total(gm2d)'].mean(),ls='--',color='b')
        #axes1[x].annotate('%.1f'%data_to_plot['Total(gm2d)'].mean(),(1,data_to_plot['Total(gm2d)'].mean()+1),textcoords='data',size=9)
        
    ## Label left axes
    axes[0,0].set_ylabel('NORTHERN \n g/'+r'$m^2$'+'/day'), axes[1,0].set_ylabel('CENTRAL \n g/'+r'$m^2$'+'/day'), axes[2,0].set_ylabel('SOUTHERN \n g/'+r'$m^2$'+'/day') 
    axes[0,0].set_ylim(0,max_y)
    ## turn on axes
    for ax in axes[2]:
        ax.xaxis.set_visible(True)
    axes[2,0].set_xticklabels(data_to_plot['Month'].values)
    #plt.suptitle('Sediment Accumulation in SedPods over time',fontsize=16)
    plt.tight_layout(pad=0.2)
    fig.legend(handles,labels,'upper center',ncol=5)
    plt.subplots_adjust(top=0.95)
    show_plot(show,fig)
    savefig(save,filename)
    return
#Sed_fraction_timeseries(SedPods,max_y=40,plot_health_thresholds=False,show=True,save=True,filename=rawfig+'SedPods-fraction')
#Sed_fraction_timeseries(SedTubes,max_y=650,plot_health_thresholds=True,show=True,save=True,filename=rawfig+'SedTubes-fraction')


#### Plot %fine in each SedTube over time
def perc_fines_timeseries(data,show=True,save=False,filename=''):
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(12,8))
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        axes1=axes.reshape(-1)

        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data_to_plot = data[(data['Pod(P)/Tube(T)'] == loc)]
        ## Calculate % fine fraction
        data_to_plot['%fine'] = data_to_plot['Mass Fine Fraction']/data_to_plot['Total(g)']*100
        ## Select the points with NA values and replace with the ylim, plot all as grey
        data_to_plot.replace('NaN',100)['%fine'].plot(kind='bar',stacked=True,ax=axes1[x],color='grey',alpha=0.5,zorder=3,label='No Data')
        ## Plot data values in color over the grey
        data_to_plot['%fine'].plot(kind='bar',stacked=True,ax=axes1[x],color='g')
        ## Format subplot
        axes1[x].set_xticklabels(data_to_plot['Month'].values,rotation='vertical')
        axes1[x].set_title(loc)
    axes[0,0].set_ylabel('% fine fraction'), axes[1,0].set_ylabel('% fine fraction'),axes[2,0].set_ylabel('% fine fraction')
    axes[0,0].set_ylim(0,100)
    ## Legend, title
    plt.legend()
    plt.tight_layout(pad=0.1)
    show_plot(show,fig)
    savefig(save,filename)
    return
#perc_fines_timeseries(SedPods,show=True,save=False,filename='')
#perc_fines_timeseries(SedTubes,show=True,save=False,filename='')


#### Plot each SedPod/SedTube over time
def Sed_timeseries_mean_NS(data,max_y=40, show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(2, 1,sharey=True,figsize=(8,6))

    north_reef = ['1A','1B','1C','2A','2C']
    south_reef = ['2B','3A','3B','3C']
    if 'T1A' in data['Pod(P)/Tube(T)'].values:
        north_reef = ['T'+x for x in north_reef] 
        south_reef = ['T'+x for x in south_reef] 
    if 'P1A' in data['Pod(P)/Tube(T)'].values:
        north_reef = ['P'+x for x in north_reef] 
        south_reef = ['P'+x for x in south_reef] 
    
    north_sed = data[data['Pod(P)/Tube(T)'].isin(north_reef)]
    south_sed = data[data['Pod(P)/Tube(T)'].isin(south_reef)]

    sediment_mean_by_month= pd.DataFrame()
    ## Select Sed data
    for mon in XL.sheet_names:
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        north_mean = north_sed[north_sed['Month'] == mon]['Total(gm2d)'].mean()
        south_mean = south_sed[south_sed['Month'] == mon]['Total(gm2d)'].mean()
        precip = north_sed[north_sed['Month'] == mon]['Precip'].max()
        
        sediment_mean_by_month = sediment_mean_by_month.append(pd.DataFrame({'North':north_mean,'South':south_mean,'Precip':precip},index=[mon]))
        
    ## Plot data values
    sediment_mean_by_month['North'].plot(kind='bar',stacked=True,ax=axes[0])
    sediment_mean_by_month['South'].plot(kind='bar',stacked=True,ax=axes[1])
    for ax in axes:    
        ## Plot precip data
        ax2=ax.twinx()
        ax2.yaxis.set_ticks_position('right')
        ax2.plot(ax.get_xticks(),sediment_mean_by_month['Precip'],ls='-',color='k')  
        ax2.set_ylim(0,2000), ax2.set_ylabel('mm')
        ax2.xaxis.grid(False), ax2.yaxis.grid(False)

    
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
Sed_timeseries_mean_NS(SedPods,max_y=40,show=True,save=True,filename=rawfig+'SedPods-monthly mean')
Sed_timeseries_mean_NS(SedTubes,max_y=650,show=True,save=True,filename=rawfig+'SedTubes-monthly mean')




