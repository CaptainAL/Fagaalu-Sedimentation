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
datadir = 'C:/Users/Alex/Documents/GitHub/Fagaalu-Sedimentation/Data/'
GISdir = datadir+'GIS/'

## Open Spreadsheet of data
XL = pd.ExcelFile(datadir+'CRCP Sediment Data.xlsx')
Data = XL.parse('CRCP 2014',header=1,na_values='NAN',index_col=4)

SedPods = Data[Data['Device']=='SedPod']
Tubes = Data[Data['Device']=='Tube']

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

#for d in Tubes.iterrows():
#    print d[0]
#    data = d[1]
#    X,Y = m(data['Lon'],data['Lat'])
#    #print X,Y
#    ## Labels
#    plt.text(X-50,Y+30,str(d[0]),color='w')
#    plt.text(X,Y-50,str(data['Total(g)'])+'(g)',size=10,color='w')
#    
#    org,carb,terr = data['Total(%organic)'],data['Total(%carb)'],data['Total(%terr)']
#    ratios = [org/100.,carb/100.,terr/100.]
#    #print ratios
#    
#    xy = []
#    start = 0.
#    for ratio in ratios:
#        x = [0] + np.cos(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()
#        y = [0] + np.sin(np.linspace(2*math.pi*start,2*math.pi*(start+ratio), 30)).tolist()
#        xy.append(zip(x,y))
#        start += ratio
# 
#    for i, xyi in enumerate(xy):
#        colors=['green','blue','red']
#        ax.scatter(X,Y,marker=(xyi,0), s=data['Total(g)']*10, facecolor=colors[i])
#        plt.draw()
#plt.suptitle('Sediment accumulation in tubes-April 2014')        


for d in SedPods.iterrows():
    print d[0]
    data = d[1]
    X,Y = m(data['Lon'],data['Lat'])
    #print X,Y
    ## Labels
    plt.text(X-50,Y+30,str(d[0]),color='w')
    plt.text(X,Y-50,str(data['Total(g)'])+'(g)',size=10,color='w')
    
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
        ax.scatter(X,Y,marker=(xyi,0), s=data['Total(g)']*20, facecolor=colors[i])
        plt.draw()
plt.suptitle('Sediment accumulation in SedPods-April 2014')      

#### Colors legend
labels=['%Organic','%Carbonate','%Terrigenous']
[ax.bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]  
plt.legend()

   
plt.show()


