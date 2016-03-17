# -*- coding: utf-8 -*-
"""
Created on Wed Sep 09 12:03:25 2015

@author: Alex
"""

import pandas as pd
import numpy as np
import datetime as dt
from matplotlib.dates import date2num
import matplotlib as mpl
import math

datadir = 'C:/Users/Alex/Documents/GitHub/Fagaalu-Sedimentation/Data/WW3_data/'

SSY_data = pd.DataFrame.from_csv('C:/Users/Alex/Documents/GitHub/Fagaalu-Sedimentation/Data/Fagaalu_watershed/SSY_daily-measured and predicted.csv')


datafile = datadir+'point_data.csv'

data = pd.DataFrame.from_csv(datafile)
data = data[dt.datetime(2014,3,5):dt.datetime(2015,4,10)]
#data = data[dt.datetime(2014,2,15):dt.datetime(2014,2,25)]

periods_file  = datadir+'periods.csv'
periods = pd.DataFrame.from_csv(periods_file)
periods['start'] = pd.to_datetime(periods['start'])
periods['end'] = pd.to_datetime(periods['end'])

## http://oos.soest.hawaii.edu/thredds/ncss/grid/hioos/model/wav/ww3/samoa/WaveWatch_III_Samoa_Regional_Wave_Model_best.ncd/pointDataset.html

# Accessed 9/9/15

# Tdir = peak wave direction 
# Thgt = significant wave height 
# Tper = peak wave period 
# sdir = swell peak wave direction 
# shgt = swell significant wave height 
# sper = swell peak wave period 
# wdir = wind peak wave direction 
# whgt = wind significant wave height 
# wper = wind peak wave period 

## Swell is given as where it is from (south swell is from the south); we want to change it show it going into the bay
data['back_az'] = np.where(data['Tdir[unit="degrees"]']>=180,-180,180) # if direction is over 180, subtract 180; if direction is less than 180, add 180
data['back_az_Tdir[unit="degrees"]'] = data['Tdir[unit="degrees"]'] + data['back_az']

## Conver to U,V to plot in quiver
data['Tdir_rad'] = np.radians(data['back_az_Tdir[unit="degrees"]'])
u,v = np.sin(data['Tdir_rad']), np.cos(data['Tdir_rad'])

#Normalize and scale by height
N = np.sqrt(u**2+v**2)
u2, v2 = u/N, v/N
u2 *= data['Thgt[unit="meters"]'].values
v2 *= data['Thgt[unit="meters"]'].values

from windrose import WindroseAxes
from matplotlib import pyplot as plt
import matplotlib.cm as cm
from numpy.random import random
from numpy import arange

def wave_rose():
    wvht = data['Thgt[unit="meters"]'].values
    wvdir =data['sdir[unit="degrees"]'].values
    
    #A quick way to create new windrose axes...
    def new_axes():
        fig = plt.figure(figsize=(8, 8), dpi=80, facecolor='w', edgecolor='w')
        rect = [0.1, 0.1, 0.8, 0.8]
        ax = WindroseAxes(fig, rect, axisbg='w')
        fig.add_axes(ax)
        return ax
    def set_legend(ax):
        l = ax.legend()
        plt.setp(l.get_texts(), fontsize=8)
    ax = new_axes()
    ax.bar(wvdir, wvht, normed=True, opening=0.8, edgecolor='white')
    set_legend(ax)    
    return
#wave_rose()


def stick_plot(time, u, v, C,**kw):
    width = kw.pop('width', 0.002)
    headwidth = kw.pop('headwidth', 2)
    headlength = kw.pop('headlength', 3)
    headaxislength = kw.pop('headaxislength', 3)
    angles = kw.pop('angles', 'uv')
    ax = kw.pop('ax', None)
    
    if angles != 'uv':
        raise AssertionError("Stickplot angles must be 'uv' so that"
                             "if *U*==*V* the angle of the arrow on"
                             "the plot is 45 degrees CCW from the *x*-axis.")

    time, u, v = map(np.asanyarray, (time, u, v))
    if not ax:
        fig, ax = plt.subplots(figsize=(12,3))
    
    q = ax.quiver(date2num(time), [[0]*len(time)], u, v, C,
                  angles='uv', width=width, headwidth=headwidth,
                  headlength=headlength, headaxislength=headaxislength,
                  **kw)
                  
    qk = ax.quiverkey(q,.2,.8,1, '1 m',     labelpos='S')
                      
    cb = plt.colorbar(q)
    cb.set_label('Wave Period (sec)')

    ax.axes.get_yaxis().set_visible(False)
    ax.set_ylim(-0.08,5)
    ax.xaxis_date()
    plt.xticks(rotation=70)
    plt.tight_layout()
    return q
    


stick_plot(data.index,u2,v2,data['Tper[unit="seconds"]'].values,cmap=plt.cm.rainbow,norm=mpl.colors.Normalize(vmin=0,vmax=20),scale=30)


def wave_time_series():
    fig, ((Thgt, shgt, whgt, mean_ht, ssy)) = plt.subplots(5,1,sharex=False,figsize=(14,12))
    Thgt.tick_params(\
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off') # labels along the bottom edge are off
    Thgt.xaxis.set_visible(False)
    
    shgt.tick_params(\
        axis='x',          # changes apply to the x-axis
        which='both',      # both major and minor ticks are affected
        bottom='off',      # ticks along the bottom edge are off
        top='off',         # ticks along the top edge are off
        labelbottom='off') # labels along the bottom edge are off    
    shgt.xaxis.set_visible(False)    
       
    data['1.5_Thgt[unit="meters"]']=np.where(data['Thgt[unit="meters"]']>=1.5,data['Thgt[unit="meters"]'],np.nan)    
    data['1.5_Thgt[unit="meters"]'].plot(ax=Thgt)
    Thgt.set_ylabel('Sig Wave ht (m)')
    
    data['shgt[unit="meters"]'].plot(ax=shgt)
    shgt.set_ylabel('Swell Sig Wave ht (m)')
    
    data['whgt[unit="meters"]'].plot(ax=whgt)
    whgt.set_ylabel('Wind Sig Wave ht (m)')
    
    mean_hts = pd.DataFrame()
    ssy_periods = pd.DataFrame()
    for ax in fig.axes[:-1]:
        for period in periods.iterrows():   
            name,start, end= period[0],period[1]['start'],period[1]['end']
            midtime = period[1]['start']+(period[1]['end']-period[1]['start'])//3
            #ax.axvline(start,ls='--',c='k')
            #ax.axvline(end,ls='--',c='k')
            #ax.text(start,5, name,fontsize=10)
            #ax.set_ylim(0,6)
            
            mean_hts = mean_hts.append(pd.DataFrame({'mean_Thgt':data['1.5_Thgt[unit="meters"]'][start:end].sum()},index=[midtime]))
            ssy_periods = ssy_periods.append(pd.DataFrame({'SSY_period':SSY_data['SSY_combined'][start:end].sum()},index=[midtime]))
            
    mean_hts=mean_hts.drop_duplicates().reindex(data.index)
    ssy_periods=ssy_periods.drop_duplicates().reindex(data.index)
    
    mean_ht.plot_date(mean_hts.index,mean_hts['mean_Thgt'])
    ssy.plot_date(ssy_periods.index,ssy_periods['SSY_period'])
    
    #mean_ht.set_ylim(0.5,3)
    mean_ht.set_ylabel('Mean Sig Wave ht (m)')
    for period in periods.iterrows():   
            name,start, end= period[0],period[1]['start'],period[1]['end']
            midtime = period[1]['start']+(period[1]['end']-period[1]['start'])//3
            ssy.axvline(start,ls='--',c='k')
            ssy.axvline(end,ls='--',c='k')
            ssy.text(start,2.5, name,fontsize=10)
            ssy.set_ylabel('SSY (tons)')
    #plt.tight_layout()
    plt.show()   
    return
#wave_time_series()
    
    
    ## Plot of wave height and ssy 
def daily_wave_and_wind():
    fig, ax1 = plt.subplots(1,1,sharex=True,figsize=(8,4))
    
    ## Significant Wave Height Thgt over 1.5m (Wave-forcing conditions)
    ax1.set_ylabel('Mean daily \n Sig Wave ht (m)',color='b')
    ## take only days with over 1.5m swell ht
    data['1.5_Thgt[unit="meters"]']=np.where(data['Thgt[unit="meters"]']>=1.5,data['Thgt[unit="meters"]'],np.nan)   
    ## Daily mean, na values are = 0m
    daily_mean_wave_ht =  data['1.5_Thgt[unit="meters"]'].resample('1D',how='mean')
    daily_mean_wave_ht.plot(ax=ax1,ls='steps',color='b')
    for tl in ax1.get_yticklabels():
        tl.set_color('b')
        
    ## SSY input
    ax2 = ax1.twinx()
    ax2.set_ylabel('SSY (tons/day)',color='r')
    SSY_data['SSY_combined'].plot(ax=ax2,ls='steps',color='r')
    for tl in ax2.get_yticklabels():
        tl.set_color('r')
    
    plt.show()
    return
#daily_wave_and_wind()
