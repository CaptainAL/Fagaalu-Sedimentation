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
    Data = XL.parse(sheet,header=7,na_values=['NAN','N/A (disturbed)'],parse_cols='A:D,F:L')
    Data = Data.replace('NO SED',0)
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
    
## Plot each SedPod over time
cols =SedPods['Pod(P)/Tube(T)'].value_counts().shape[0]
fig, axes = plt.subplots(1, cols,sharey=True)
labels=['coral','mud','sand']
colors=['blue','red','green']
[axes[x].bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]  
plt.legend()

for x, loc in enumerate(np.sort(SedPods['Pod(P)/Tube(T)'].value_counts().index.values)):
    data = SedPods[(SedPods['Pod(P)/Tube(T)'] == loc)]
    data['Total(g)'].plot(kind='bar',stacked=True,ax=axes[x],color=sub_colors[substrate[loc]])
    axes[x].set_xticklabels(data['Month'].values)
    axes[x].set_title(loc)
    axes[x].axhline(y=100,ls='-',c='y')
    axes[x].axhline(y=500,ls='-',c='r')
    axes[x].axhline(y=data['Total(g)'].mean(),ls='-',c='b')
    axes[x].annotate('%.1f'%data['Total(g)'].mean(),(1,data['Total(g)'].mean()),textcoords='data',size=9)
    
axes[0].set_ylabel('g/'+r'$m^2$'+'/day')   
axes[0].set_ylim(0,35)

plt.suptitle('Sediment Accumulation in SedPods over time',fontsize=16)
plt.draw()
plt.show()
    
## Plot each SedTube over time
cols =SedTubes['Pod(P)/Tube(T)'].value_counts().shape[0]
fig, axes = plt.subplots(1, cols,sharey=True)
labels=['coral','mud','sand']
colors=['blue','red','green']
[axes[x].bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]  
plt.legend()

for x, loc in enumerate(np.sort(SedTubes['Pod(P)/Tube(T)'].value_counts().index.values)):
    data = SedTubes[(SedTubes['Pod(P)/Tube(T)'] == loc)]
    data['Total(g)'].plot(kind='bar',ax=axes[x],color=sub_colors[substrate[loc]])
    axes[x].set_xticklabels(data['Month'].values)
    axes[x].set_title(loc)
    axes[x].axhline(y=100,ls='-',c='y')
    axes[x].axhline(y=500,ls='-',c='r')
    axes[x].axhline(y=data['Total(g)'].mean(),ls='-',c='b')
    axes[x].annotate('%.1f'%data['Total(g)'].mean(),(1,data['Total(g)'].mean()+10),textcoords='data',size=9)
    
axes[0].set_ylabel('g/'+r'$m^2$'+'/day')    
axes[0].set_ylim(0,650)

plt.suptitle('Sediment Accumulation in SedTubes over time',fontsize=16)
plt.draw()
plt.show()


#TODO Label water depth (WD=...)
## Plot each SedPod over time
cols =SedPods['Pod(P)/Tube(T)'].value_counts().shape[0]
fig, axes = plt.subplots(1, cols,sharey=True)
for x, loc in enumerate(np.sort(SedPods['Pod(P)/Tube(T)'].value_counts().index.values)):
    data = SedPods[(SedPods['Pod(P)/Tube(T)'] == loc)]
    data[['Mass Sand Fraction','Mass Fine Fraction']].plot(kind='bar',stacked=True,ax=axes[x],legend=False)
    axes[x].set_xticklabels(data['Month'].values)
    axes[x].set_title(loc)
    axes[x].axhline(y=100,ls='-',c='y')
    axes[x].axhline(y=500,ls='-',c='r')
    
axes[0].set_ylabel('g/'+r'$m^2$'+'/day')
axes[0].set_ylim(0,35)
plt.legend()
plt.suptitle('Sediment Accumulation in SedPods over time',fontsize=16)
plt.draw()
plt.show()
    
## Plot each SedTube over time
cols =SedTubes['Pod(P)/Tube(T)'].value_counts().shape[0]
fig, axes = plt.subplots(1, cols,sharey=True)
for x, loc in enumerate(np.sort(SedTubes['Pod(P)/Tube(T)'].value_counts().index.values)):
    ## Plot Coral health thresholds
    axes[x].axhspan(0, 100, facecolor='g',alpha=.5)
    axes[x].axhspan(100, 500, facecolor='y',alpha=.5)
    axes[x].axhspan(300, 2000, facecolor='r',alpha=.5)    
    ## Plot Data
    data = SedTubes[(SedTubes['Pod(P)/Tube(T)'] == loc)]
    data[['Mass Sand Fraction','Mass Fine Fraction']].plot(kind='bar',stacked=True,ax=axes[x],legend=False)
    axes[x].set_xticklabels(data['Month'].values)
    axes[x].set_title(loc)
    ## Plot means
    axes[x].axhline(y=data['Total(g)'].mean(),ls='-',c='b')
    axes[x].annotate('%.1f'%data['Total(g)'].mean(),(1,data['Total(g)'].mean()+10),textcoords='data',size=9)
## Label Coral health thresholds
axes[0].annotate('stress recruits',(1,220),textcoords='data',rotation=90,size=9)
axes[0].annotate('stress colonies',(1,420),textcoords='data',rotation=90,size=9)
axes[0].annotate('lethal',(1,600),textcoords='data',rotation=90,size=9)    
## Labels, limits
axes[0].set_ylabel('g/'+r'$m^2$'+'/day')
axes[0].set_ylim(0,650)
## Legend, title
plt.legend()
plt.suptitle('Sediment Accumulation in SedTubes over time',fontsize=16)
plt.draw()
plt.show()

## Plot each SedTube over time
cols =SedTubes['Pod(P)/Tube(T)'].value_counts().shape[0]
fig, axes = plt.subplots(1, cols,sharey=True)
for x, loc in enumerate(np.sort(SedTubes['Pod(P)/Tube(T)'].value_counts().index.values)):
    ## Plot Data
    data = SedTubes[(SedTubes['Pod(P)/Tube(T)'] == loc)]
    data['%fine'] = data['Mass Fine Fraction']/data['Total(g)']*100
    axes[x].plot(range(1,6),data['%fine'],marker='o',ls='-',c='g')
    axes[x].set_xticklabels(data['Month'].values,rotation='vertical')
    axes[x].set_title(loc)
axes[0].set_ylabel('% total mass fine fraction')
## Legend, title
plt.legend()
plt.suptitle('Percentage fine fraction mass in SedTubes',fontsize=16)
plt.draw()
plt.show()


