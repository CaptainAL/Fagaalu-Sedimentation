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

## Figure formatting
#publishable =  plotsettings.Set('GlobEnvChange')    ## plotsettings.py
#publishable.set_figsize(n_columns = 2, n_rows = 2)
mpl.rc_file(maindir+'johrc.rc')
mpl.rcParams['savefig.directory']=maindir+'rawfig/'
mpl.rcParams
## Ticks
my_locator = matplotlib.ticker.MaxNLocator(4)

## Set Directories
maindir =  'C:/Users/Alex/Documents/GitHub/Fagaalu-Sedimentation/'
datadir = maindir+'Data/'
GISdir = datadir+'GIS/'
figdirPods= maindir+'Figures/SedPods/'
figdirTubes= maindir+'Figures/SedTubes/'
rawfig= maindir+'rawfig/'

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

## Open Spreadsheet of data
XL = pd.ExcelFile(datadir+'BulkWeight/SedPod_Processing_LAB.xlsx')
SedPods, SedTubes = pd.DataFrame(),pd.DataFrame()
count = 0
for sheet in XL.sheet_names:
    count +=1
    Data = XL.parse(sheet,header=7,na_values=['NAN','N/A (disturbed)'],parse_cols='A:D,F:L')
    Data = Data.replace('NO SED',0)
    Data = Data.replace('N/A (disturbed)',np.NaN)
    Data['Total(g)'] = Data['Mass Sand Fraction'] + Data['Mass Fine Fraction']
    ## Get rid of negative values
    Data['Total(g)']= Data['Total(g)'][Data['Total(g)']>=0]
    Data['Mass Sand Fraction']= Data['Mass Sand Fraction'][Data['Mass Sand Fraction']>=0]
    Data['Mass Fine Fraction']= Data['Mass Fine Fraction'][Data['Mass Fine Fraction']>=0]    
    ## Convert to g/m2/day
    Data['Total(g)'] = Data['Total(g)']/Data['Area(m2)']/Data['Days deployed:']
    Data['Mass Sand Fraction'] = Data['Mass Sand Fraction']/Data['Area(m2)']/Data['Days deployed:']
    Data['Mass Fine Fraction'] = Data['Mass Fine Fraction']/Data['Area(m2)']/Data['Days deployed:']
    ## Round
    round_num = 5
    Data['Total(g)']=Data['Total(g)'].round(round_num)
    Data['Mass Sand Fraction']=Data['Mass Sand Fraction'].round(round_num)
    Data['Mass Fine Fraction']=Data['Mass Fine Fraction'].round(round_num)
    
    ## Add Month
    Data['Month'] = sheet
    ## Categorize by Tubes and Pods
    Pods = Data[Data['Pod(P)/Tube(T)'].isin(['P1A','P2A','P3A','P1B','P2B','P3B','P1C','P2C','P3C'])]
    Tubes = Data[Data['Pod(P)/Tube(T)'].isin(['T1A','T2A','T3A','T1B','T2B','T3B','T1C','T2C','T3C'])]
    ## Add to All Samples
    SedPods = SedPods.append(Pods)
    SedTubes = SedTubes.append(Tubes)

#    ##################################################
#    ## Map Extents: Local, Island, Region
#    ll = [-14.294238,-170.683732] #ll = [-14.4,-170.8] #ll = [-20,-177]
#    ur = [-14.286362, -170.673260] #ur = [-14.23, -170.54] #ur = [-14,-170]
#    
#    ### Make Plot
#    fig, ax = plt.subplots(1)
#    m = Basemap(projection='merc', resolution='f',
#                   llcrnrlon=ll[1], llcrnrlat=ll[0],
#                   urcrnrlon=ur[1], urcrnrlat=ur[0],ax=ax)
#    #### Show background image from DriftersBackground.mxd
#    background = np.flipud(plt.imread(GISdir+'DrifterBackground.png'))
#    m.imshow(background,origin='lower')#,extent=[ll[1],ll[0],ur[1],ur[0]])
#    
#    #### Show Lat/Lon Grid               
#    #gMap.drawparallels(np.arange(ll[0],ur[0],.001),labels=[1,1,0,0])
#    #gMap.drawmeridians(np.arange(ll[1],ur[1],.001),labels=[0,0,0,1])
#    
#    #### Display Shapefiles:
#    m.readshapefile(GISdir+'fagaalugeo','fagaalugeo') ## Display coastline of watershed
#    
#    for d in Tubes.iterrows():
#        data = d[1]
#        print sheet+' '+data['Pod(P)/Tube(T)']
#        X,Y = m(data['Lon'],data['Lat'])
#        #print X,Y
#        
#        ## Labels
#        plt.text(X-50,Y+30,str(data['Pod(P)/Tube(T)']),color='w')
#        plt.text(X,Y-50,str(data['Total(g)'])+'(g)',size=10,color='w')
#        
#        try:
#            coarse = data['Mass Sand Fraction']/data['Total(g)']*100.
#        except ZeroDivisionError:
#            coarse = 0.0
#        try:
#            fine= data['Mass Fine Fraction']/data['Total(g)']*100.
#        except ZeroDivisionError:
#            fine = 0.0
#
#        ratios = [coarse/100.,fine/100.]
#        #print ratios
#        
#        xy = []
#        start = 0.
#        for ratio in ratios:
#            x = [0] + np.cos(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()
#            y = [0] + np.sin(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()
#            xy.append(zip(x,y))
#            start += ratio
#     
#        for i, xyi in enumerate(xy):
#            colors=['blue','red']
#            ax.scatter(X,Y,marker=(xyi,0), s=data['Total(g)']*10000, facecolor=colors[i])
#            plt.draw()
#    title = 'Sediment accumulation in Tubes: '+sheet
#    plt.suptitle(title)
#    #### Colors legend
#    labels=['coarse%','fine%']
#    [ax.bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]  
#    plt.legend()    
#        
#    plt.savefig(figdirTubes+str(count)+'-Tubes-'+sheet)        
#    
#    for d in Pods.iterrows():
#        data = d[1]
#        print sheet+' '+data['Pod(P)/Tube(T)']
#        X,Y = m(data['Lon'],data['Lat'])
#        #print X,Y
#        
#        ## Labels
#        plt.text(X-50,Y+30,str(data['Pod(P)/Tube(T)']),color='w')
#        plt.text(X,Y-50,str(data['Total(g)'])+'(g)',size=10,color='w')
#        
#        try:
#            coarse = data['Mass Sand Fraction']/data['Total(g)']*100.
#        except ZeroDivisionError:
#            coarse = 0.0
#        try:
#            fine= data['Mass Fine Fraction']/data['Total(g)']*100.
#        except ZeroDivisionError:
#            fine = 0.0
#
#        ratios = [coarse/100.,fine/100.]
#        #print ratios
#        
#        xy = []
#        start = 0.
#        for ratio in ratios:
#            x = [0] + np.cos(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()
#            y = [0] + np.sin(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()
#            xy.append(zip(x,y))
#            start += ratio
#     
#        for i, xyi in enumerate(xy):
#            colors=['blue','red']
#            ax.scatter(X,Y,marker=(xyi,0), s=data['Total(g)']*100000, facecolor=colors[i])
#            plt.draw()
#    title = 'Sediment accumulation in SedPods: '+sheet
#    plt.suptitle(title)
#    #### Colors legend
#    labels=['coarse%','fine%']
#    [ax.bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]  
#    plt.legend()    
#        
#    plt.savefig(figdirPods+str(count)+'-Pods-'+sheet)  
#    
substrate = {'P3A':'coral','P3B':'coral','P3C':'coral','P2A':'mud','P2B':'coral','P2C':'coral','P1A':'sand','P1B':'sand','P1C':'coral',
'T3A':'coral','T3B':'coral','T3C':'coral','T2A':'mud','T2B':'coral','T2C':'coral','T1A':'sand','T1B':'sand','T1C':'coral'}
sub_colors={'coral':'blue','mud':'red','sand':'green'}
    
#### Plot each SedPod/SedTube over time
def Sed_timeseries(data,max_y=40, show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(12,8))
    labels=['coral','mud','sand','No Data']
    colors=['blue','red','green','grey']
    [axes[-1,-1].bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]   
    plt.legend(ncol=2)
    
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        axes1=axes.reshape(-1)
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data_to_plot = data[data['Pod(P)/Tube(T)'] == loc]
        ## Select the points with NA values and replace with the ylim, plot all as grey
        data_to_plot.replace('NaN',max_y)['Total(g)'].plot(kind='bar',stacked=True,ax=axes1[x],color='grey',alpha=0.5)
        ## Plot data values in color over the grey
        data_to_plot['Total(g)'].plot(kind='bar',stacked=True,ax=axes1[x],color=sub_colors[substrate[loc]])
        ## Format subplot
        axes1[x].set_xticklabels(data_to_plot['Month'].values)
        axes1[x].set_title(loc)
        axes1[x].axhline(y=100,ls='-',c='y')
        axes1[x].axhline(y=500,ls='-',c='r')
        axes1[x].axhline(y=data_to_plot['Total(g)'].mean(),ls='-',c='b')
        axes1[x].annotate('%.1f'%data_to_plot['Total(g)'].mean(),(1,data_to_plot['Total(g)'].mean()),textcoords='data',size=9)
        axes1[x].tick_params(labelsize=8)
        #axes1[x].xaxis.grid(False)
       
    axes[0,0].set_ylabel('NORTHERN \n g/'+r'$m^2$'+'/day'), axes[1,0].set_ylabel('CENTRAL \n g/'+r'$m^2$'+'/day'), axes[2,0].set_ylabel('SOUTHERN \n g/'+r'$m^2$'+'/day')   
    axes[0,0].set_ylim(0,max_y)
    
    #plt.suptitle('Sediment Accumulation in SedPods over time',fontsize=16)
    plt.tight_layout(pad=0.1)
    show_plot(show,fig)
    savefig(save,filename)
    return
#Sed_timeseries(SedPods,max_y=40,show=True,save=False,filename='')
#Sed_timeseries(SedTubes,max_y=650,show=True,save=False,filename='')


#### Plot each SedPod/SedTube over time, separating the Coarse/Fine fraction
def Sed_fraction_timeseries(data,max_y=40,plot_health_thresholds=False,show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(12,8))
    labels=['coarse','fines']
    colors=['blue','green']
    [axes[-1,-1].bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]   
    plt.legend(ncol=2)
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
        data_to_plot.replace('NaN',max_y)['Total(g)'].plot(kind='bar',stacked=True,ax=axes1[x],color='grey',alpha=0.5,zorder=3)
        ## Plot data values in color over the grey
        data_to_plot[['Mass Sand Fraction','Mass Fine Fraction']].plot(kind='bar',stacked=True,ax=axes1[x],legend=False,zorder=5)
        ## Format subplot
        axes1[x].set_xticklabels(data_to_plot['Month'].values)
        axes1[x].set_title(loc)
        axes1[x].axhline(y=data_to_plot['Total(g)'].mean(),ls='-',c='b',zorder=6)
        axes1[x].annotate('%.1f'%data_to_plot['Total(g)'].mean(),(1,data_to_plot['Total(g)'].mean()),textcoords='data',size=9,zorder=6)
        axes1[x].tick_params(labelsize=8)
        axes1[x].grid(False)
       
    axes[0,0].set_ylabel('NORTHERN \n g/'+r'$m^2$'+'/day'), axes[1,0].set_ylabel('CENTRAL \n g/'+r'$m^2$'+'/day'), axes[2,0].set_ylabel('SOUTHERN \n g/'+r'$m^2$'+'/day')   
    axes[0,0].set_ylim(0,max_y)

    #plt.suptitle('Sediment Accumulation in SedPods over time',fontsize=16)
    plt.tight_layout(pad=0.1)
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

