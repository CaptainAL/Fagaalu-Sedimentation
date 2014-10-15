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
## Set Pandas display options
pd.set_option('display.large_repr', 'truncate')
pd.set_option('display.max_rows', 15)

## Set Directories
maindir =  'C:/Users/Alex/Documents/GitHub/Fagaalu-Sedimentation/'
datadir = maindir+'Data/'
GISdir = datadir+'GIS/'
figdirPods= maindir+'Figures/SedPods/'
figdirTubes= maindir+'Figures/SedTubes/'

## Open Spreadsheet of data
XL = pd.ExcelFile(datadir+'BulkWeight/SedPod_Processing_LAB.xlsx')
SedPods, SedTubes = pd.DataFrame(),pd.DataFrame()
count = 0
for sheet in XL.sheet_names:
    count +=1
    Data = XL.parse(sheet,header=7,na_values=['NAN','N/A (disturbed)'],parse_cols='A:D,F:J')
    Data = Data.replace('NO SED',0)
    Data['Total(g)'] = Data['Mass Sand Fraction'] + Data['Mass Fine Fraction']
    Data['Month'] = sheet
    
    Pods = Data[Data['Pod(P)/Tube(T)'].isin(['P1A','P2A','P3A','P1B','P2B','P3B','P1C','P2C','P3C'])]
    Tubes = Data[Data['Pod(P)/Tube(T)'].isin(['T1A','T2A','T3A','T1B','T2B','T3B','T1C','T2C','T3C'])]
    
    SedPods = SedPods.append(Pods)
    SedTubes = SedTubes.append(Tubes)

    ##################################################
    ## Map Extents: Local, Island, Region
    ll = [-14.294238,-170.683732] #ll = [-14.4,-170.8] #ll = [-20,-177]
    ur = [-14.286362, -170.673260] #ur = [-14.23, -170.54] #ur = [-14,-170]
    
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
#            ax.scatter(X,Y,marker=(xyi,0), s=data['Total(g)']*10, facecolor=colors[i])
#            plt.draw()
#    title = 'Sediment accumulation in Tubes: '+sheet
#    plt.suptitle(title)
#    #### Colors legend
#    labels=['coarse%','fine%']
#    [ax.bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]  
#    plt.legend()    
#        
#    plt.savefig(figdirTubes+str(count)+'-Tubes-'+sheet)        
    
    for d in Pods.iterrows():
        data = d[1]
        print sheet+' '+data['Pod(P)/Tube(T)']
        X,Y = m(data['Lon'],data['Lat'])
        #print X,Y
        
        ## Labels
        plt.text(X-50,Y+30,str(data['Pod(P)/Tube(T)']),color='w')
        plt.text(X,Y-50,str(data['Total(g)'])+'(g)',size=10,color='w')
        
        try:
            coarse = data['Mass Sand Fraction']/data['Total(g)']*100.
        except ZeroDivisionError:
            coarse = 0.0
        try:
            fine= data['Mass Fine Fraction']/data['Total(g)']*100.
        except ZeroDivisionError:
            fine = 0.0

        ratios = [coarse/100.,fine/100.]
        #print ratios
        
        xy = []
        start = 0.
        for ratio in ratios:
            x = [0] + np.cos(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()
            y = [0] + np.sin(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()
            xy.append(zip(x,y))
            start += ratio
     
        for i, xyi in enumerate(xy):
            colors=['blue','red']
            ax.scatter(X,Y,marker=(xyi,0), s=data['Total(g)']*10, facecolor=colors[i])
            plt.draw()
    title = 'Sediment accumulation in SedPods: '+sheet
    plt.suptitle(title)
    #### Colors legend
    labels=['coarse%','fine%']
    [ax.bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]  
    plt.legend()    
        
    plt.savefig(figdirPods+str(count)+'-Pods-'+sheet)  
#    
#    
#    
    
    
    
    
    
    
