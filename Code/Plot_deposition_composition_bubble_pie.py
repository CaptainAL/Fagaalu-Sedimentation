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
maindir = 'C:/Users/atm19/Documents/GitHub/Fagaalu-Sedimentation/'
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

def lat2str(deg):
    min = 60 * (deg - np.floor(deg))
    deg = np.floor(deg)
    dir = 'N'
    if deg < 0:
        if min != 0.0:
            deg += 1.0
            min -= 60.0
        dir = 'S'
    return ("%d %g' %s") % (np.abs(deg),np.abs(min),dir) + 'S'

def lon2str(deg):
    min = 60 * (deg - np.floor(deg))
    deg = np.floor(deg)
    dir = 'E'
    if deg < 0:
        if min != 0.0:
            deg += 1.0
            min -= 60.0
        dir = 'W'
    return ("%d\N{DEGREE SIGN} %g' %s") % (np.abs(deg),np.abs(min),dir)

def Lon_decdegree2DMS(value):
    """
        Converts a Decimal Degree Value into
        Degrees Minute Seconds Notation.
        
        Pass value as double
        type = {Latitude or Longitude} as string
        
        returns a string as D:M:S:Direction
        created by: anothergisblog.blogspot.com 
    """
    if value > 180:
        value = 360.-value
    degrees = int(value)
    submin = abs( (value - int(value) ) * 60)
    minutes = int(submin)
    subseconds = abs((submin-int(submin)) * 60)
    direction = "W"
    #if degrees < 0:
       # direction = "W"
    #elif degrees > 0:
       # direction = "E"
    #else:
        #direction = ""

    notation = str(degrees) + u"\u00B0" + str(minutes) + "'" +\
               str(subseconds)[0:2] + '"' + direction
    return notation
    
def Lat_decdegree2DMS(value):
    """
        Converts a Decimal Degree Value into
        Degrees Minute Seconds Notation.
        
        Pass value as double
        type = {Latitude or Longitude} as string
        
        returns a string as D:M:S:Direction
        created by: anothergisblog.blogspot.com 
    """
    degrees = int(value)
    submin = abs( (value - int(value) ) * 60)
    minutes = int(submin)
    subseconds = abs((submin-int(submin)) * 60)
    direction = ""
    if degrees < 0:
        direction = "S"
    elif degrees > 0:
        direction = "N"
    else:
        direction = "" 
    notation = str(degrees) + u"\u00B0" + str(minutes) + "'" +\
               str(subseconds)[0:2] + '"' + direction
    return notation

##################################################
## Map Extents: Local, Island, Region
ll = [-14.294238,-170.683732] #ll = [-14.4,-170.8] #ll = [-20,-177]
ur = [-14.286362, -170.673260] #ur = [-14.23, -170.54] #ur = [-14,-170]

def Map_composition_single(SedData,month,show=True,save=False,filename=''):
    plt.ioff()
    ### Make Plot
    fig, ax = plt.subplots(1)
    m = Basemap(projection='merc', resolution='f',
                   llcrnrlon=ll[1], llcrnrlat=ll[0],
                   urcrnrlon=ur[1], urcrnrlat=ur[0],ax=ax)
    #### Show background image from DriftersBackground.mxd
    background = np.flipud(plt.imread(GISdir+'DrifterBackground_new.png'))
    m.imshow(background,origin='lower')#,extent=[ll[1],ll[0],ur[1],ur[0]])
    
    #### Show Lat/Lon Grid               
    gMap.drawparallels(np.arange(ll[0],ur[0],.001),labels=[1,1,0,0])
    gMap.drawmeridians(np.arange(ll[1],ur[1],.001),labels=[0,0,0,1])
    
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
        plt.text(X,Y-50,str("%.1f"%data['Total_gm2d'])+'(g)',size=8,color='w')
        
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

#for sheet in Comp_XL.sheet_names[11:12]:   
#    print sheet
#    Map_composition_single(SedPods,sheet,show=True,save=False,filename=rawfig+'SedPods_composition/'+sheet) 
#    Map_composition_single(SedTubes,sheet,show=True,save=False,filename=rawfig+'SedTubes_composition/'+sheet)     

##################################################
## Map Extents: Local, Island, Region
ll = [-14.294238,-170.683732] #ll = [-14.4,-170.8] #ll = [-20,-177]
ur = [-14.286362, -170.673260] #ur = [-14.23, -170.54] #ur = [-14,-170]

def Map_composition_mean(show=True,save=False,filename=''):
    #plt.ioff()
    ### Make Plot
    fig, (tubes,pods) = plt.subplots(1,2,sharex=False,sharey=False,figsize=(12,5))
    letter_subplots(fig,0.1,0.95,'top','right','w',font_size=12,font_weight='bold')

    
    for ax in fig.axes:
        m = Basemap(projection='merc', resolution='f',
                       llcrnrlon=ll[1], llcrnrlat=ll[0],
                       urcrnrlon=ur[1], urcrnrlat=ur[0],ax=ax)
        #### Show background image from DriftersBackground.mxd
        background = np.flipud(plt.imread(GISdir+'DrifterBackground_new.png'))
        m.imshow(background,origin='lower')#,extent=[ll[1],ll[0],ur[1],ur[0]])
        
        #### Show Lat/Lon Grid               
#        m.drawparallels(np.arange(ll[0],ur[0],.003),linewidth=0.5,color='grey',labels=[1,0,0,0],fontsize=8,fmt=Lat_decdegree2DMS,rotation='vertical')
#        m.drawmeridians(np.arange(ll[1],ur[1],.003),linewidth=0.5,color='grey',labels=[0,0,1,0],fontsize=8,fmt=Lon_decdegree2DMS)
        
        m.drawparallels(np.arange(ll[0],ur[0],.003),linewidth=0.5,color='grey',labels=[1,0,0,0],fontsize=8,fmt=Lat_decdegree2DMS,rotation='vertical')
        m.drawmeridians([-170.6749, -170.6777,-170.6805,-170.6833],linewidth=0.5,color='grey',labels=[0,0,1,0],fontsize=8,fmt=Lon_decdegree2DMS)
        
        #### Display Shapefiles:
        m.readshapefile(GISdir+'fagaalugeo','fagaalugeo') ## Display coastline of watershed
        #### Colors legend
        labels=['%Organic','%Carbonate','%Terrigenous']
        colors=['g','b','r']
        [ax.bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]  
    tubes.legend(loc='upper right', title='Traps',fontsize=10)       
    pods.legend(loc='upper right',title='Pods',fontsize=10) 
    
    ## SEDTUBES
    for x, loc in enumerate(np.sort(SedTubes['Pod(P)/Tube(T)'].value_counts().index.values)):
        print x, loc
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data = SedTubes[SedTubes['Pod(P)/Tube(T)'] == loc].dropna()
        ## Composition
        org,carb,terr = data['Total_Org_gm2d'].mean(),data['Total_Carb_gm2d'].mean(),data['Total_Terr_gm2d'].mean()
        total_mean = data['Total_gm2d'].mean()
        ratios = [org/total_mean,carb/total_mean,terr/total_mean]
        sum_ratios = sum(ratios)
        print '%.2f'%org+' '+'%.2f'%terr+' '+'%.2f'%carb+' = '+'%.2f'%sum_ratios
        ## Plot
        X,Y = m(data['Lon'].max(),data['Lat'].max())
        #print X,Y
        ## Labels
        tubes.text(X-50,Y+30,str(loc),color='w',fontsize=10)
        tubes.text(X,Y-50,"%.1f"%total_mean,size=8,color='w')
        xy = []
        start = 0.
        for ratio in ratios:
            x = [0] + np.cos(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()
            y = [0] + np.sin(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()
            xy.append(zip(x,y))
            start += ratio
        for i, xyi in enumerate(xy):
            colors=['green','blue','red']
            tubes.scatter(X,Y,marker=(xyi,0), s=total_mean*2, facecolor=colors[i])
            
    ## SEDPODS
    for x, loc in enumerate(np.sort(SedPods['Pod(P)/Tube(T)'].value_counts().index.values)):
        print x, loc
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data = SedPods[SedPods['Pod(P)/Tube(T)'] == loc].dropna()
        ## Composition
        org,carb,terr = data['Total_Org_gm2d'].mean(),data['Total_Carb_gm2d'].mean(),data['Total_Terr_gm2d'].mean()
        total_mean = data['Total_gm2d'].mean()
        ratios = [org/total_mean,carb/total_mean,terr/total_mean]
        sum_ratios = sum(ratios)
        print '%.2f'%org+' '+'%.2f'%terr+' '+'%.2f'%carb+' = '+'%.2f'%sum_ratios
        ## Plot
        X,Y = m(data['Lon'].max(),data['Lat'].max())
        #print X,Y
        ## Labels
        pods.text(X-50,Y+30,str(loc),color='w',fontsize=10)
        pods.text(X,Y-50,"%.1f"%total_mean,size=8,color='w')
        xy = []
        start = 0.
        for ratio in ratios:
            x = [0] + np.cos(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()
            y = [0] + np.sin(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()
            xy.append(zip(x,y))
            start += ratio
        for i, xyi in enumerate(xy):
            colors=['green','blue','red']
            pods.scatter(X,Y,marker=(xyi,0), s=total_mean*8, facecolor=colors[i])
            
            
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.1)
    savefig(save,filename)
    if show==True:
            plt.show()
    elif show==False:
        plt.close('all')
    plt.ion()
    return
Map_composition_mean(show=True,save=True,filename=figdir+'Mean Accumulation Map/Sed_composition_Mean_Annual') 
#Map_composition_mean(SedPods,show=True,save=True,filename=figdir+'Mean Accumulation Map/SedPods_composition_Mean_Annual') 
#Map_composition_mean(SedTubes,show=True,save=True,filename=figdir+'Mean Accumulation Map/SedTubes_composition_Mean_Annual')   


