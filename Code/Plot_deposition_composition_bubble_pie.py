# -*- coding: utf-8 -*-
"""
Created on Sun Sep 14 22:12:26 2014

@author: Alex
"""

## Plot pie charts of sediment deposition/composition over Faga'alu Basemap 

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


## Open Spreadsheet of data
BulkWeight_XL = pd.ExcelFile(datadir+'CRCP Sediment Data Bulk Weight and Composition.xlsx')
Comp_XL = pd.ExcelFile(datadir+'LOI/Messina LOI.xls')
Precip = pd.DataFrame.from_csv(datadir+'Fagaalu_rain_gauge-Daily.csv').resample('M',how='sum')


SedPods, SedTubes = pd.DataFrame(),pd.DataFrame()
count = 0
for sheet in Comp_XL.sheet_names[:11]:
#for sheet in Comp_XL.sheet_names[4:5]:
    count +=1
    ## Precip Data
    sampleDates = BulkWeight_XL.parse(sheet,parse_cols='A:B',index_col=1,parse_dates=True)[:2] 
    start, end = pd.to_datetime(sampleDates.index[0]), pd.to_datetime(sampleDates.index[1])
    precip_month = Precip[start:end].sum()[0]
    print 'start: '+str(start)+' end: '+str(end)+' precip: '+"%.0f"%precip_month
    ## Open data and replace NO SED and N/A values
    BulkWeight_Data = BulkWeight_XL.parse(sheet,header=7,na_values=['NAN','N/A (disturbed)'],parse_cols='A:D,F:L',index_col=0)
    BulkWeight_Data['Pod(P)/Tube(T)'] = BulkWeight_Data.index
    BulkWeight_Data = BulkWeight_Data.replace('NO SED',0.00001)
    BulkWeight_Data = BulkWeight_Data.replace('N/A (disturbed)',np.NaN)
    ## Change negative values to zero (actually to .00001 so you don't divide by zero later)
    BulkWeight_Data['Mass Sand Fraction']= BulkWeight_Data['Mass Sand Fraction'].where(BulkWeight_Data['Mass Sand Fraction']>=0.0,0.00001)
    BulkWeight_Data['Mass Fine Fraction']= BulkWeight_Data['Mass Fine Fraction'].where(BulkWeight_Data['Mass Fine Fraction']>=0.0,0.00001)    
    ## Calculate Total Bulk weight
    BulkWeight_Data['Total(g)'] = BulkWeight_Data['Mass Sand Fraction'] + BulkWeight_Data['Mass Fine Fraction']
    
    ## Calculate g/m2/day
    BulkWeight_Data['Total(gm2d)'] = BulkWeight_Data['Total(g)']/BulkWeight_Data['Area(m2)']/BulkWeight_Data['Days deployed:']
    BulkWeight_Data['Mass Sand Fraction(gm2d)'] = BulkWeight_Data['Mass Sand Fraction']/BulkWeight_Data['Area(m2)']/BulkWeight_Data['Days deployed:']
    BulkWeight_Data['Mass Fine Fraction(gm2d)'] = BulkWeight_Data['Mass Fine Fraction']/BulkWeight_Data['Area(m2)']/BulkWeight_Data['Days deployed:']
    ## Round
    round_num = 5
    BulkWeight_Data['Total(gm2d)']=BulkWeight_Data['Total(gm2d)'].round(round_num)
    BulkWeight_Data['Mass Sand Fraction(gm2d)']=BulkWeight_Data['Mass Sand Fraction(gm2d)'].round(round_num)
    BulkWeight_Data['Mass Fine Fraction(gm2d)']=BulkWeight_Data['Mass Fine Fraction(gm2d)'].round(round_num)
    ## Add Month
    BulkWeight_Data['Month'] = sheet
    ## Add Monthly precip
    BulkWeight_Data['Precip'] = precip_month
    
    ## Add Composition Data
    Comp_Data = Comp_XL.parse(sheet,header=0,na_values=['NAN','N/A (disturbed)'],parse_cols='A,D,F,Q:S',index_col=0)
    for line in Comp_Data.iterrows():
        #print line
        loc = line[0][:3] # ex. P1A from P1A coarse
        # Coarse fraction composition
        if line[0].endswith('coarse') or line[0].endswith('coarse '):
            BulkWeight_Data.ix[loc,'Coarse(%organic)'] = line[1]['Total % Organics'] ## insert value into row loc, column Coarse(%..
            BulkWeight_Data.ix[loc,'Coarse(%carb)'] = line[1]['Total % Carbonates']
            BulkWeight_Data.ix[loc,'Coarse(%terr)'] = line[1]['Total % Terrigenous']
        if line[0].endswith('fine') or line[0].endswith('fine '):
            BulkWeight_Data.ix[loc,'Fine(%organic)'] = line[1]['Total % Organics']
            BulkWeight_Data.ix[loc,'Fine(%carb)'] = line[1]['Total % Carbonates']
            BulkWeight_Data.ix[loc,'Fine(%terr)'] = line[1]['Total % Terrigenous']
            
    ## Calculate some stuff
    # Percent fine/coarse
    BulkWeight_Data['%fine'] = BulkWeight_Data['Mass Fine Fraction']/BulkWeight_Data['Total(g)'] *100
    BulkWeight_Data['%coarse'] = BulkWeight_Data['Mass Sand Fraction']/BulkWeight_Data['Total(g)'] *100
    # If the bulkweight is 0, when you divide 0/0 it gives NaN; replace the NaN's with 0.0, unless it is NaN of course

    # Composition of Total sample (Coarse and Fine combined), weighted by % fine/coarse
    # e.g. Total %organic = (Coarse %organic x %coarse ) + (Fine %organic x %fine)
    BulkWeight_Data['Total(%organic)'] = (BulkWeight_Data['Coarse(%organic)']*BulkWeight_Data['%coarse']/100)+(BulkWeight_Data['Fine(%organic)']*BulkWeight_Data['%fine']/100)
    BulkWeight_Data['Total(%carb)'] = (BulkWeight_Data['Coarse(%carb)']*BulkWeight_Data['%coarse']/100)+(BulkWeight_Data['Fine(%carb)']*BulkWeight_Data['%fine']/100)
    BulkWeight_Data['Total(%terr)'] = (BulkWeight_Data['Coarse(%terr)']*BulkWeight_Data['%coarse']/100)+(BulkWeight_Data['Fine(%terr)']*BulkWeight_Data['%fine']/100)

    ## Categorize by Tubes and Pods
    Pods = BulkWeight_Data[BulkWeight_Data['Pod(P)/Tube(T)'].isin(['P1A','P2A','P3A','P1B','P2B','P3B','P1C','P2C','P3C'])]
    Tubes = BulkWeight_Data[BulkWeight_Data['Pod(P)/Tube(T)'].isin(['T1A','T2A','T3A','T1B','T2B','T3B','T1C','T2C','T3C'])]    
    
    ## Add to All Samples
    col_names = ['Month','Pod(P)/Tube(T)','Precip','Mass Sand Fraction','Mass Fine Fraction','Total(g)','Total(gm2d)','Lat','Lon','Total(%organic)','Total(%carb)','Total(%terr)','Coarse(%organic)','Coarse(%carb)','Coarse(%terr)','Fine(%organic)','Fine(%carb)','Fine(%terr)']
    # SedPods
    SedPods = SedPods.append(Pods[col_names])
    # reorder columns
    SedPods = SedPods[col_names]
    # SedTubes
    SedTubes = SedTubes.append(Tubes[col_names])
    SedTubes = SedTubes[col_names]




##################################################
## Map Extents: Local, Island, Region
ll = [-14.294238,-170.683732] #ll = [-14.4,-170.8] #ll = [-20,-177]
ur = [-14.286362, -170.673260] #ur = [-14.23, -170.54] #ur = [-14,-170]

def Map_composition(SedData,month,show=True,save=False,filename=''):
    plt.ioff()
    ### Make Plot
    fig, ax = plt.subplots(1)
    m = Basemap(projection='merc', resolution='f',
                   llcrnrlon=ll[1], llcrnrlat=ll[0],
                   urcrnrlon=ur[1], urcrnrlat=ur[0],ax=ax)
    #### Show background image from DriftersBackground.mxd
    background = np.flipud(plt.imread(GISdir+'DrifterBackground.png'))
    m.imshow(background,origin='lower')#,extent=[ll[1],ll[0],ur[1],ur[0]])
    
    #### Show Lat/Lon Grid               
    #gMap.drawparallels(np.arange(ll[0],ur[0],.001),labels=[1,1,0,0])
    #gMap.drawmeridians(np.arange(ll[1],ur[1],.001),labels=[0,0,0,1])
    
    #### Display Shapefiles:
    m.readshapefile(GISdir+'fagaalugeo','fagaalugeo') ## Display coastline of watershed
    #### Colors legend
    labels=['%Organic','%Carbonate','%Terrigenous']
    colors=['g','b','r']
    [ax.bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]  
    if 'T1A' in SedData['Pod(P)/Tube(T)']:
        plt.legend(loc='upper right', title='SedTubes '+month)       
    if 'P1A' in SedData['Pod(P)/Tube(T)']:
        plt.legend(loc='upper right',title='SedPods '+month) 

    SedData = SedData[SedData['Month']==month]
    for d in SedData.iterrows():
        #print d[0]
        data = d[1]
        X,Y = m(data['Lon'],data['Lat'])
        #print X,Y
        ## Labels
        plt.text(X-50,Y+30,str(d[0]),color='w',fontsize=10)
        plt.text(X,Y-50,str("%.1f"%data['Total(gm2d)'])+'(g)',size=8,color='w')
        
        org,carb,terr = data['Total(%organic)'],data['Total(%carb)'],data['Total(%terr)']
        ratios = [org/100.,carb/100.,terr/100.]
        #print ratios
        
        xy = []
        start = 0.
        for ratio in ratios:
            x = [0] + np.cos(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()
            y = [0] + np.sin(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()
            xy.append(zip(x,y))
            start += ratio
     
        for i, xyi in enumerate(xy):
            colors=['green','blue','red']
            ax.scatter(X,Y,marker=(xyi,0), s=data['Total(g)']*10, facecolor=colors[i])
            plt.draw()
    savefig(save,filename)
    if show==True:
            plt.show()
    elif show==False:
        plt.close('all')
    plt.ion()
    return


#for sheet in Comp_XL.sheet_names[:6]:   
#    Map_composition(SedPods,sheet,show=False,save=True,filename=rawfig+'SedPods_composition/'+sheet) 
#    Map_composition(SedTubes,sheet,show=False,save=True,filename=rawfig+'SedTubes_composition/'+sheet)     


#### Plot each SedPod/SedTube over time
def Terr_Sed_timeseries(data,max_y=40, show=True,save=False,filename=''):    
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
        ax2.plot(axes1[x].get_xticks(),sed['Precip'],ls='-',color='k')  
        ax2.set_ylim(0,2000), ax2.xaxis.set_visible(False),ax2.yaxis.set_visible(False)
        if x==2 or x==5 or x==8:
            ax2.yaxis.set_visible(True), ax2.set_ylabel('mm')
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
#Terr_Sed_timeseries(SedPods,max_y=40,show=True,save=True,filename=rawfig+'SedPods-terrig and precip')
#Terr_Sed_timeseries(SedTubes,max_y=650,show=True,save=True,filename=rawfig+'SedTubes-terrig and precip')


#### Plot each SedPod/SedTube over time
def Sed_Comp_timeseries(data,max_y=40,plot_health_thresholds=False,show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(10,8))
    labels=['organic','terrigenous','carbonate','No Data']
    colors=['green','red','blue','grey']
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
            axes1[x].annotate('stress recruits',(4,150),textcoords='data',rotation=0,size=14,color='grey',zorder=2)
            axes1[x].annotate('stress colonies',(4,350),textcoords='data',rotation=0,size=14,color='grey',zorder=2)
            axes1[x].annotate('lethal',(4,550),textcoords='data',rotation=0,size=14,color='grey',zorder=2)     

        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data_to_plot = data[data['Pod(P)/Tube(T)'] == loc]
        ## calculate weight of terrigenous sed
        data_to_plot['Total Org(gm2d)'] = data_to_plot['Total(gm2d)'] * data_to_plot['Total(%organic)']/100
        data_to_plot['Total Terr(gm2d)'] = data_to_plot['Total(gm2d)'] * data_to_plot['Total(%terr)']/100
        data_to_plot['Total Carb(gm2d)'] = data_to_plot['Total(gm2d)'] * data_to_plot['Total(%carb)']/100
        ## Select the points with NA values and replace with the ylim, plot all as grey
        data_to_plot.replace('NaN',max_y)['Total Terr(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='grey',alpha=0.3)
        ## Plot the total gm2d, then if the composition data is NA it will just plot the total
        data_to_plot['Total(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='y',alpha=0.5,label='Total(no comp.)')
        
        ## create dataframe of sed and precip
        sed = pd.DataFrame({'Total Org(gm2d)':data_to_plot['Total Org(gm2d)'].values,'Total Terr(gm2d)':data_to_plot['Total Terr(gm2d)'].values,'Precip':data_to_plot['Precip'].values,'Total Carb(gm2d)':data_to_plot['Total Carb(gm2d)'].values}, index=data_to_plot['Month'].values)
        ## Plot data values in color over the grey
        sed[['Total Org(gm2d)','Total Terr(gm2d)','Total Carb(gm2d)']].plot(kind='bar',stacked=True,ax=axes1[x],color=['g','r','b'])
        ## Plot precip data
        ax2=axes1[x].twinx()
        ax2.yaxis.set_ticks_position('right')
        ax2.plot(axes1[x].get_xticks(),sed['Precip'],ls='-',marker='s',color='b')  
        ax2.set_ylim(0,2000), ax2.xaxis.set_visible(False),ax2.yaxis.set_visible(False)
        if x==2 or x==5 or x==8:
            ax2.yaxis.set_visible(True), ax2.set_ylabel('mm')
        ## Format subplot
        axes1[x].xaxis.set_visible(False)
        axes1[x].tick_params(labelsize=8),ax2.tick_params(labelsize=8)
        axes1[x].xaxis.grid(False),ax2.yaxis.grid(False)
        axes1[x].legend().set_visible(False)
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
    fig.legend(handles,labels,'upper center',ncol=5)
    plt.subplots_adjust(top=0.90)
    show_plot(show,fig)
    savefig(save,filename)
    return
#Sed_Comp_timeseries(SedPods,max_y=40,plot_health_thresholds=False,show=True,save=True,filename=rawfig+'SedPods-composition and precip')
Sed_Comp_timeseries(SedTubes,max_y=650,plot_health_thresholds=True,show=True,save=True,filename=rawfig+'SedTubes-composition and precip')

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
    for mon in Comp_XL.sheet_names[:11]:
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        north_mean = north_sed[north_sed['Month'] == mon]['Total(gm2d)'].mean() * north_sed[north_sed['Month'] == mon]['Total(%terr)'].mean()/100
        south_mean = south_sed[south_sed['Month'] == mon]['Total(gm2d)'].mean() * south_sed[south_sed['Month'] == mon]['Total(%terr)'].mean()/100
        precip = north_sed[north_sed['Month'] == mon]['Precip'].max()
        
        sediment_mean_by_month = sediment_mean_by_month.append(pd.DataFrame({'North terr':north_mean,'South terr':south_mean,'Precip':precip},index=[mon]))
        
    ## Plot data values
    sediment_mean_by_month['North terr'].plot(kind='bar',stacked=True,ax=axes[0],color='r')
    sediment_mean_by_month['South terr'].plot(kind='bar',stacked=True,ax=axes[1],color='r')
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
#Sed_timeseries_mean_NS(SedPods,max_y=40,show=True,save=False,filename=rawfig+'SedPods-monthly mean')
#Sed_timeseries_mean_NS(SedTubes,max_y=650,show=True,save=False,filename=rawfig+'SedTubes-monthly mean')

