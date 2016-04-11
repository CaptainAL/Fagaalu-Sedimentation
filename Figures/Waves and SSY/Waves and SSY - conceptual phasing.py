# -*- coding: utf-8 -*-
"""
Created on Tue Jul 01 15:46:56 2014

@author: Alex
"""
import pandas as pd
import datetime


## SedPod Deployment Periods
wavedir+'periods.csv'
periods = pd.DataFrame.from_csv(wavedir+'periods.csv')
periods['start'] = pd.to_datetime(periods['start'])
periods['end'] = pd.to_datetime(periods['end'])

## SSY data from measurement and Qmax model
SSY_data = pd.DataFrame.from_csv('C:/Users/Alex/Documents/GitHub/Fagaalu-Sedimentation/Data/Fagaalu_watershed/SSY_daily-measured and predicted.csv')

## NOAA Wave Watch 3 wave modeling data
data = pd.DataFrame.from_csv(wavedir+'point_data.csv')
data = data[datetime.datetime(2014,3,5):datetime.datetime(2015,4,10)]
#data = data[dt.datetime(2014,2,15):dt.datetime(2014,2,25)]



### Plot Conceptual model, daily data, monthly (deployment data)
fig, (ax1,ax2,ax3) = plt.subplots(3,1,sharex=False,figsize=(10,8))
def letter_subplots(fig,x=0.1,y=0.95,vertical='top',horizontal='right',Color='k',font_size=10,font_weight='bold'):
    sub_plot_count = 0
    sub_plot_letters = {0:'(a)',1:'b)',2:'(c)'}
    for ax in fig.axes:
        ax.text(x,y,sub_plot_letters[sub_plot_count],verticalalignment=vertical, horizontalalignment=horizontal,transform=ax.transAxes,color=Color,fontsize=font_size,fontweight=font_weight)
        sub_plot_count+=1
    return 

letter_subplots(fig,0.05,0.95,'top','right','k',font_size=10,font_weight='bold')


### Conceptual model of Wave/SSY phasing
start = datetime.datetime(2014,3,1)
end = datetime.datetime(2015,4,30)
dates= pd.date_range(start,end,freq='M')
swell = sin(np.linspace(0.5,2.5,14))+0.75
swell = np.append(swell[4:], swell[0:4])

sediment = [2,1.5,2,1.5,1,1.75,1.70,1.8,1.25,1.8,2.1,1.9,1.5,1.2]

df = pd.DataFrame.from_dict({'swell height':swell,'sediment loading':sediment,'months':dates}).set_index('months')
## Waves
ax1.set_ylabel('Hmean (m)',color='b')
df['swell height'].plot(ax=ax1,color='b',ls='-',marker='None',label='Hmean (m)')
for tl in ax1.get_yticklabels():
    tl.set_color('b')
## SSY
ax1_2 = ax1.twinx()
ax1_2.set_ylabel('SSY (tons)',color='r')
df['sediment loading'].plot(ax=ax1_2,color='r',ls='--',marker='None',label='SSY (tons)')
for tl in ax1_2.get_yticklabels():
    tl.set_color('r')
## Fill between
ax1.fill_between(df.index,df['sediment loading'],df['swell height'],where=sediment>=swell,facecolor='red',alpha=0.1,interpolate=True)
ax1.fill_between(df.index,df['sediment loading'],df['swell height'],where=sediment<=swell,facecolor='green',alpha=0.3,interpolate=True)
## Plot wave height again just for the legend
df['swell height'].plot(ax=ax1_2,color='b',ls='-',marker='None',label='Hmean')
ax1_2.legend(loc=3,fontsize=10)


### Daily Wave and SSY data
## Significant Wave Height Thgt over 1.5m (Wave-forcing conditions)
ax2.set_ylabel('Hmean (m)',color='b')
ax2.set_ylim(1.4,5.0)

## take only days with over 1.5m swell ht
data['1.5_Thgt[unit="meters"]']=np.where(data['Thgt[unit="meters"]']>=1.5,data['Thgt[unit="meters"]'],np.nan)   
## Daily mean, na values are = 0m
daily_mean_wave_ht =  data['1.5_Thgt[unit="meters"]'].resample('1D',how='mean')
daily_mean_wave_ht.plot(ax=ax2,ls='steps',color='b')
for tl in ax2.get_yticklabels():
    tl.set_color('b')
## SSY input
ax2_2 = ax2.twinx()
ax2_2.set_ylabel('SSY (tons)',color='r')
SSY_data['SSY_combined'].plot(ax=ax2_2,ls='steps',color='r')
for tl in ax2_2.get_yticklabels():
    tl.set_color('r')
ax2.grid(False)   

    
### Monthly(deployment) Mean Waves and Total SSY
mean_hts = pd.DataFrame()
ssy_periods = pd.DataFrame()
for period in periods.iterrows():   
    name,start, end= period[0],period[1]['start'],period[1]['end']
    midtime = period[1]['start']+(period[1]['end']-period[1]['start'])//2
    mean_hts = mean_hts.append(pd.DataFrame({'mean_Thgt':data['Thgt[unit="meters"]'][start:end].mean()},index=[midtime]))
    ssy_periods = ssy_periods.append(pd.DataFrame({'SSY_period':SSY_data['SSY_combined'][start:end].sum()},index=[midtime]))       

## Waves
ax3.set_ylabel('Hmean (m)',color='b')
mean_hts['mean_Thgt'].plot(ax=ax3,marker='o',color='b',ls='-')
for tl in ax3.get_yticklabels():
    tl.set_color('b')
### SSY
ax3_2 = ax3.twinx()
ax3_2.set_ylabel('SSY (tons)',color='r')
ssy_periods['SSY_period'].plot(ax=ax3_2,color='r',marker='o',ls='-')
for tl in ax3_2.get_yticklabels():
    tl.set_color('r')
## Plot SedPod periods vertical lines
ax3.grid(False)
ax3_2.grid(False)
for period in periods.iterrows():   
        name,start, end= period[0],period[1]['start'],period[1]['end']
        midtime = period[1]['start']+(period[1]['end']-period[1]['start'])//3
        ax3.axvline(start,ls='--',c='k')
        ax3.axvline(end,ls='--',c='k')


plt.tight_layout()
fig.subplots_adjust(hspace=0.2)
plt.show()








fig, (ax1, ax2) = plt.subplots(2,1,sharex=False,figsize=(10,6))
letter_subplots(fig,0.05,0.95,'top','right','k',font_size=10,font_weight='bold')

### Daily Wave and SSY data
## Significant Wave Height Thgt over 1.5m (Wave-forcing conditions)
ax1.set_ylabel('Hmean (m)',color='b')
ax1.set_ylim(1.4,5.0)

## take only days with over 1.5m swell ht
data['1.5_Thgt[unit="meters"]']=np.where(data['Thgt[unit="meters"]']>=1.5,data['Thgt[unit="meters"]'],np.nan)   
## Daily mean, na values are = 0m
daily_mean_wave_ht =  data['1.5_Thgt[unit="meters"]'].resample('1D',how='mean')
daily_mean_wave_ht.plot(ax=ax1,ls='steps',color='b')
for tl in ax1.get_yticklabels():
    tl.set_color('b')
    
## SSY input
ax1_2 = ax1.twinx()
ax1_2.set_ylabel('SSY (tons)',color='r')
SSY_data['SSY_combined'].plot(ax=ax1_2,ls='steps',color='r')
for tl in ax1_2.get_yticklabels():
    tl.set_color('r')
  

    
### Monthly(deployment) Mean Waves and Total SSY
mean_hts = pd.DataFrame()
ssy_periods = pd.DataFrame()
for period in periods.iterrows():   
    name,start, end= period[0],period[1]['start'],period[1]['end']
    midtime = period[1]['start']+(period[1]['end']-period[1]['start'])//2
    mean_hts = mean_hts.append(pd.DataFrame({'mean_Thgt':data['Thgt[unit="meters"]'][start:end].mean()},index=[midtime]))
    ssy_periods = ssy_periods.append(pd.DataFrame({'SSY_period':SSY_data['SSY_combined'][start:end].sum()},index=[midtime]))       

#### Waves
ax2.set_ylabel('Hmean (m)',color='b')
mean_hts['mean_Thgt'].plot(ax=ax2,marker='o',color='b',ls='-')
for tl in ax2.get_yticklabels():
    tl.set_color('b')

#### SSY
ax2_2 = ax2.twinx()
ax2_2.set_ylabel('SSY (tons)',color='r')
ssy_periods['SSY_period'].plot(ax=ax2_2,color='r',marker='o',ls='-')
for tl in ax2_2.get_yticklabels():
    tl.set_color('r')
    
### Plot SedPod periods vertical lines
ax1.grid(False)
ax1_2.grid(False)
ax2.grid(False)
ax2_2.grid(False)
for period in periods.iterrows():   
        name,start, end= period[0],period[1]['start'],period[1]['end']
        midtime = period[1]['start']+(period[1]['end']-period[1]['start'])//3
        ax1.axvline(start,ls='--',c='k')
        ax1.axvline(end,ls='--',c='k')
        ax2.axvline(start,ls='--',c='k')
        ax2.axvline(end,ls='--',c='k')
ax1.set_xlim(periods['start'][0],periods['end'][-1])
ax2.set_xlim(periods['start'][0],periods['end'][-1])

plt.tight_layout()
fig.subplots_adjust(hspace=0.2)
plt.show()

