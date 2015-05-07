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
Comp_XL = pd.ExcelFile(datadir+'LOI/Messina LOI 4.3.15.xls')

SedPods, SedTubes = pd.DataFrame(),pd.DataFrame()
count = 0
for sheet in Comp_XL.sheet_names[:6]:
    count +=1
    ## Open data and replace NO SED and N/A values
    BulkWeight_Data = BulkWeight_XL.parse(sheet,header=7,na_values=['NAN','N/A (disturbed)'],parse_cols='A:D,F:L',index_col=0)
    BulkWeight_Data['Pod(P)/Tube(T)'] = BulkWeight_Data.index
    BulkWeight_Data = BulkWeight_Data.replace('NO SED',0)
    BulkWeight_Data = BulkWeight_Data.replace('N/A (disturbed)',np.NaN)
    ## Calculate Total Bulk weight
    BulkWeight_Data['Total(g)'] = BulkWeight_Data['Mass Sand Fraction'] + BulkWeight_Data['Mass Fine Fraction']
    ## Get rid of negative values
    BulkWeight_Data['Total(g)'] = BulkWeight_Data['Total(g)'][BulkWeight_Data['Total(g)']>=0]
    BulkWeight_Data['Mass Sand Fraction']= BulkWeight_Data['Mass Sand Fraction'][BulkWeight_Data['Mass Sand Fraction']>=0]
    BulkWeight_Data['Mass Fine Fraction']= BulkWeight_Data['Mass Fine Fraction'][BulkWeight_Data['Mass Fine Fraction']>=0]    
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
    
    ## Add Composition Data
    Comp_Data = Comp_XL.parse(sheet,header=0,na_values=['NAN','N/A (disturbed)'],parse_cols='A,D,F,Q:S',index_col=0)
    for line in Comp_Data.iterrows():
        loc = line[0][:3] # ex. P1A from P1A coarse
        # Coarse fraction composition
        if line[0].endswith('coarse'):
            BulkWeight_Data.ix[loc,'Coarse(%organic)'] = line[1]['Total % Organics'] ## insert value into row loc, column Coarse(%..
            BulkWeight_Data.ix[loc,'Coarse(%carb)'] = line[1]['Total % Carbonates']
            BulkWeight_Data.ix[loc,'Coarse(%terr)'] = line[1]['Total % Terrigenous']
        if line[0].endswith('fine'):
            BulkWeight_Data.ix[loc,'Fine(%organic)'] = line[1]['Total % Organics']
            BulkWeight_Data.ix[loc,'Fine(%carb)'] = line[1]['Total % Carbonates']
            BulkWeight_Data.ix[loc,'Fine(%terr)'] = line[1]['Total % Terrigenous']
            
    ## Calculate some stuff
    # Percent fine/coarse
    BulkWeight_Data['%fine'] = BulkWeight_Data['Mass Fine Fraction']/BulkWeight_Data['Total(g)'] *100
    BulkWeight_Data['%coarse'] = BulkWeight_Data['Mass Sand Fraction']/BulkWeight_Data['Total(g)'] *100
    # Composition of Total sample (Coarse and Fine combined), weighted by % fine/coarse
    # e.g. Total %organic = (Coarse %organic x %coarse ) + (Fine %organic x %fine)
    BulkWeight_Data['Total(%organic)'] = (BulkWeight_Data['Coarse(%organic)']*BulkWeight_Data['%coarse']/100)+(BulkWeight_Data['Fine(%organic)']*BulkWeight_Data['%fine']/100)
    BulkWeight_Data['Total(%carb)'] = (BulkWeight_Data['Coarse(%carb)']*BulkWeight_Data['%coarse']/100)+(BulkWeight_Data['Fine(%carb)']*BulkWeight_Data['%fine']/100)
    BulkWeight_Data['Total(%terr)'] = (BulkWeight_Data['Coarse(%terr)']*BulkWeight_Data['%coarse']/100)+(BulkWeight_Data['Fine(%terr)']*BulkWeight_Data['%fine']/100)

    ## Categorize by Tubes and Pods
    Pods = BulkWeight_Data[BulkWeight_Data['Pod(P)/Tube(T)'].isin(['P1A','P2A','P3A','P1B','P2B','P3B','P1C','P2C','P3C'])]
    Tubes = BulkWeight_Data[BulkWeight_Data['Pod(P)/Tube(T)'].isin(['T1A','T2A','T3A','T1B','T2B','T3B','T1C','T2C','T3C'])]    
    
    ## Add to All Samples
    col_names = ['Month','Pod(P)/Tube(T)','Mass Sand Fraction','Mass Fine Fraction','Total(g)','Total(gm2d)','Lat','Lon','Total(%organic)','Total(%carb)','Total(%terr)','Coarse(%organic)','Coarse(%carb)','Coarse(%terr)','Fine(%organic)','Fine(%carb)','Fine(%terr)']
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


for sheet in Comp_XL.sheet_names[:6]:   
    Map_composition(SedPods,sheet,show=False,save=True,filename=rawfig+'SedPods_composition/'+sheet) 
    Map_composition(SedTubes,sheet,show=False,save=True,filename=rawfig+'SedTubes_composition/'+sheet)     


#for d in SedPods.iterrows():
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
#        ax.scatter(X,Y,marker=(xyi,0), s=data['Total(g)']*20, facecolor=colors[i])
#        plt.draw()
#plt.suptitle('Sediment accumulation in SedPods-April 2014')      



