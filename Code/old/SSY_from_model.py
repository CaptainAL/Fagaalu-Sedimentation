# -*- coding: utf-8 -*-
"""
Created on Wed Sep 23 10:30:23 2015

@author: Alex
"""

SedPods_start, SedPods_stop = dt.datetime(2014,3,5,0,0), dt.datetime(2015,4,10,11,59)    
  
def Q_SedPods(log=False,show=False,save=False,filename=''):
    mpl.rc('lines',markersize=6)
    fig, Q=plt.subplots(1)
    #letter_subplots(fig,0.1,0.95,'top','right','k',font_size=10,font_weight='bold')
    
    for ax in fig.axes:
        ax.plot_date(LBJ['Q'].index,LBJ['Q'],ls='-',marker='None',c='k',label='Q FG3')
        #ax.plot(LBJstageDischarge.index,LBJstageDischarge['Q-AV(L/sec)'],ls='None',marker='o',color='k')
        #ax.plot_date(DAM['Q'].index,DAM['Q'],ls='-',marker='None',c='grey',label='Q FG1')
        #ax.plot(DAMstageDischarge.index,DAMstageDischarge['Q-AV(L/sec)'],ls='None',marker='o',color='grey')
        ax.set_ylim(0,LBJ['Q'].max()+500)    
    Q.set_xlim(SedPods_start,SedPods_stop)
    Q.legend(loc='best')
    Q.set_ylabel('Discharge (Q) L/sec')
    #Q2012.set_title("Discharge (Q) L/sec at the Upstream and Downstream Sites, Faga'alu")
    for ax in fig.axes:
        showstormintervals(ax,LBJ_storm_threshold,LBJ_StormIntervals)
        ax.locator_params(nbins=6,axis='y')
        ax.xaxis.set_major_locator(mpl.dates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mpl.dates.DateFormatter('%b %Y'))
        
    plt.tight_layout(pad=0.1)
    logaxes(log,fig)
    show_plot(show,fig)
    savefig(save,filename)
    return
Q_SedPods(log=False,show=True,save=False,filename='')

def predict_SSY_events(model,data,watershed_area):
    a,b = model.iloc[0][['a','b']]
    SSY_predicted = a * ((data/watershed_area) **b)
    SSY_predicted = SSY_predicted * watershed_area
    return SSY_predicted.round(3)

SedPod_Storms_Qmax_SSY = pd.DataFrame({'Qmax':SedFluxStorms_LBJ[SedPods_start:SedPods_stop]['Qmax']},index=SedFluxStorms_LBJ[SedPods_start:SedPods_stop].index)
SedPod_Storms_Qmax_SSY['Qmax-SSY-predicted'] = predict_SSY_events(QmaxS_total_power,SedPod_Storms_Qmax_SSY['Qmax']/1000,1.78)

SedPod_Storms_Qmax_SSY.to_csv('C:/Users/Alex/Documents/GitHub/Fagaalu-Sedimentation/Data/Qmax-SSY from model.csv')

