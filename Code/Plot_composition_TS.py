# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:52:51 2016

@author: Alex
"""

def plot_coral_health_thresholds(axes1,x):
    print 'plot coral health thresholds x:'+str(x)
    axes1[x].axhspan(0, 100, facecolor='g',alpha=.75,zorder=1)
    axes1[x].axhspan(100, 300, facecolor='y',alpha=.75,zorder=1)
    axes1[x].axhspan(300, 500, facecolor='orange',alpha=.75,zorder=1)
    axes1[x].axhspan(500, 2000, facecolor='r',alpha=.75,zorder=1)   
    ## Label Coral health thresholds
    axes1[x].annotate('stress recruits',(4,150),textcoords='data',rotation=0,size=14,color='grey',zorder=2)
    axes1[x].annotate('stress colonies',(4,350),textcoords='data',rotation=0,size=14,color='grey',zorder=2)
    axes1[x].annotate('lethal',(4,550),textcoords='data',rotation=0,size=14,color='grey',zorder=2)  
    return

#### Plot each SedPod/SedTube over time with PRECIP
def Sed_Comp_v_Precip_TS(data,max_y=40,plot_health_thresholds=False,show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(10,8))
    labels=['organic','terrigenous','carbonate','No Data']
    colors=['green','red','blue','grey']
    bars=[axes[0,2].bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]
    lines= axes[0,2].plot(0,0,color='b',marker='s',label='Precip(mm)')
    handles, labels = axes[0,2].get_legend_handles_labels()
    ## Plot Sed data
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        axes1=axes.reshape(-1)
        
        ## Plot Coral health thresholds
        if plot_health_thresholds==True:
            plot_coral_health_thresholds(axes1,x)   

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
        ax2.plot(axes1[x].get_xticks(),sed['Precip'],ls='-',marker='s',color='b',label='Precip(mm)')  
        ax2.set_ylim(0,2000), ax2.xaxis.set_visible(False),ax2.yaxis.set_visible(False)
        if x==2 or x==5 or x==8:
            ax2.yaxis.set_visible(True), ax2.set_ylabel('Precip(mm)',color='b')
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
#Sed_Comp_v_Precip_TS(SedPods,max_y=40,plot_health_thresholds=False,show=True,save=True,filename=rawfig+'SedPods-composition v Precip')
#Sed_Comp_v_Precip_TS(SedTubes,max_y=650,plot_health_thresholds=True,show=True,save=True,filename=rawfig+'SedTubes-composition v Precip')

#### Plot each SedPod/SedTube over time wtih SSY
def Sed_Comp_v_SSY_TS(data,max_y=40,plot_health_thresholds=False,show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(10,8))
    labels=['organic','terrigenous','carbonate','No Data']
    colors=['green','red','blue','grey']
    bars=[axes[0,2].bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]
    lines= axes[0,2].plot(0,0,color='b',marker='s',label='SSY(tons)')
    handles, labels = axes[0,2].get_legend_handles_labels()
    ## Plot Sed data
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        axes1=axes.reshape(-1)
        
        ## Plot Coral health thresholds
        if plot_health_thresholds==True:
            plot_coral_health_thresholds(axes1,x)   

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
        sed = pd.DataFrame({'Total Org(gm2d)':data_to_plot['Total Org(gm2d)'].values,'Total Terr(gm2d)':data_to_plot['Total Terr(gm2d)'].values,'SSY':data_to_plot['SSY'].values,'Total Carb(gm2d)':data_to_plot['Total Carb(gm2d)'].values}, index=data_to_plot['Month'].values)
        ## Plot data values in color over the grey
        sed[['Total Org(gm2d)','Total Terr(gm2d)','Total Carb(gm2d)']].plot(kind='bar',stacked=True,ax=axes1[x],color=['g','r','b'])
        ## Plot precip data
        ax2=axes1[x].twinx()
        ax2.yaxis.set_ticks_position('right')
        ax2.plot(axes1[x].get_xticks(),sed['SSY'],ls='-',marker='s',color='r',label='SSY(tons)')  
        ax2.set_ylim(0,250), ax2.xaxis.set_visible(False),ax2.yaxis.set_visible(False)
        if x==2 or x==5 or x==8:
            ax2.yaxis.set_visible(True), ax2.set_ylabel('SSY (tons)',color='r')
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
#Sed_Comp_v_SSY_TS(SedPods,max_y=40,plot_health_thresholds=False,show=True,save=True,filename=rawfig+'SedPods-composition v SSY')
#Sed_Comp_v_SSY_TS(SedTubes,max_y=650,plot_health_thresholds=True,show=True,save=True,filename=rawfig+'SedTubes-composition v SSY')

#### Plot each SedPod/SedTube over time
def Sed_Comp_Terr_v_Precip_TS(data,max_y=40,plot_health_thresholds=False,show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(10,8))
    labels=['organic','terrigenous','No Data']
    colors=['green','red','grey']
    bars=[axes[0,2].bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]
    lines= axes[0,2].plot(0,0,color='b',marker='s',label='Precip(mm)')
    handles, labels = axes[0,2].get_legend_handles_labels()
    ## Plot Sed data
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        print x, loc
        axes1=axes.reshape(-1)
        ## Plot Coral health thresholds
        if plot_health_thresholds==True:
            plot_coral_health_thresholds(axes1,x)  

        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data_to_plot = data[data['Pod(P)/Tube(T)'] == loc]
        ## calculate weight of terrigenous sed
        data_to_plot['Total Org(gm2d)'] = data_to_plot['Total(gm2d)'] * data_to_plot['Total(%organic)']/100
        data_to_plot['Total Terr(gm2d)'] = data_to_plot['Total(gm2d)'] * data_to_plot['Total(%terr)']/100

        ## Select the points with NA values and replace with the ylim, plot all as grey
        data_to_plot.replace('NaN',max_y)['Total Terr(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='grey',alpha=0.3)
        
        ## Plot the total gm2d, then if the composition data is NA it will just plot the total
        #data_to_plot['Total(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='y',alpha=0.5,label='Total(no comp.)')
        
        ## create dataframe of sed and precip
        sed = pd.DataFrame({'Total Org(gm2d)':data_to_plot['Total Org(gm2d)'].values,'Total Terr(gm2d)':data_to_plot['Total Terr(gm2d)'].values,'Precip':data_to_plot['Precip'].values}, index=data_to_plot['Month'].values)
        ## Plot data values in color over the grey
        sed[['Total Org(gm2d)','Total Terr(gm2d)']].plot(kind='bar',stacked=True,ax=axes1[x],color=['g','r','b'])
        ## Plot precip data
        ax2=axes1[x].twinx()
        ax2.yaxis.set_ticks_position('right')
        ax2.plot(axes1[x].get_xticks(),sed['Precip'],ls='-',marker='s',color='b',label='Precip(mm)')  
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
#Sed_Comp_Terr_v_Precip_TS(SedPods,max_y=40,plot_health_thresholds=False,show=True,save=True,filename=rawfig+'SedPods-composition and precip')
#Sed_Comp_Terr_v_Precip_TS(SedTubes,max_y=650,plot_health_thresholds=True,show=True,save=True,filename=rawfig+'SedTubes-composition and precip')


#### Plot each SedPod/SedTube over time
def Sed_Comp_Terr_v_SSY_TS(data,comp='Total',max_y=40,plot_health_thresholds=False,show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(10,8))
    labels=['organic','terrigenous','No Data']
    colors=['green','red','grey']
    bars=[axes[0,2].bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]
    lines= axes[0,2].plot(0,0,color='b',marker='s',label='Precip(mm)')
    handles, labels = axes[0,2].get_legend_handles_labels()
    ## Plot Sed data
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        print x, loc
        axes1=axes.reshape(-1)
        ## Plot Coral health thresholds
        if plot_health_thresholds==True:
            plot_coral_health_thresholds(axes1,x)  

        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data_to_plot = data[data['Pod(P)/Tube(T)'] == loc]
        ## calculate weight of terrigenous sed
        data_to_plot[comp+' Org(gm2d)'] = data_to_plot[comp+'(gm2d)'] * data_to_plot[comp+'(%organic)']/100
        data_to_plot[comp+' Terr(gm2d)'] = data_to_plot[comp+'(gm2d)'] * data_to_plot[comp+'(%terr)']/100

        ## Select the points with NA values and replace with the ylim, plot all as grey
        data_to_plot.replace('NaN',max_y)[comp+' Terr(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='grey',alpha=0.3)
        
        ## Plot the total gm2d, then if the composition data is NA it will just plot the total
        #data_to_plot[comp+'(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='y',alpha=0.5,label=comp+'(no comp.)')
        
        ## create dataframe of sed and precip
        sed = pd.DataFrame({comp+' Org(gm2d)':data_to_plot[comp+' Org(gm2d)'].values,comp+' Terr(gm2d)':data_to_plot[comp+' Terr(gm2d)'].values,'SSY':data_to_plot['SSY'].values}, index=data_to_plot['Month'].values)
        ## Plot data values in color over the grey
        sed[[comp+' Org(gm2d)',comp+' Terr(gm2d)']].plot(kind='bar',stacked=True,ax=axes1[x],color=['g','r','b'])
        ## Plot precip data
        ax2=axes1[x].twinx()
        ax2.yaxis.set_ticks_position('right')
        ax2.plot(axes1[x].get_xticks(),sed['SSY'],ls='-',marker='s',color='r',label='SSY(tons)')  
        ax2.set_ylim(0,250), ax2.xaxis.set_visible(False),ax2.yaxis.set_visible(False)
        if x==2 or x==5 or x==8:
            ax2.yaxis.set_visible(True), ax2.set_ylabel('SSY(tons)')
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
Sed_Comp_Terr_v_SSY_TS(SedPods,'Fine',max_y=40,plot_health_thresholds=False,show=True,save=True,filename=rawfig+'SedPods-composition and precip')
Sed_Comp_Terr_v_SSY_TS(SedTubes,'Fine',max_y=650,plot_health_thresholds=True,show=True,save=True,filename=rawfig+'SedTubes-composition and precip')

#### Plot each SedPod/SedTube over time
def Sed_Comp_Terr_v_Precip_SSY_TS(data,max_y=40,plot_health_thresholds=False,show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(10,8))
    labels=['organic','terrigenous','No Data']
    colors=['green','red','grey']
    bars=[axes[0,2].bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]
    lines = axes[0,2].plot(0,0,color='b',label='Precip(mm)')
    lines = axes[0,2].plot(0,0,color='r',label='SSY(tons)')
    lines = axes[0,2].plot(0,0,color='k',label='MMSWH(m)')
    handles, labels = axes[0,2].get_legend_handles_labels()
    ## Plot Sed data
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        print x, loc
        axes1=axes.reshape(-1)
        ## Plot Coral health thresholds
        if plot_health_thresholds==True:
            plot_coral_health_thresholds(axes1,x)  

        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data_to_plot = data[data['Pod(P)/Tube(T)'] == loc]
        ## calculate weight of terrigenous sed
        data_to_plot['Total Org(gm2d)'] = data_to_plot['Total(gm2d)'] * data_to_plot['Total(%organic)']/100
        data_to_plot['Total Terr(gm2d)'] = data_to_plot['Total(gm2d)'] * data_to_plot['Total(%terr)']/100

        ## Select the points with NA values and replace with the ylim, plot all as grey
        data_to_plot.replace('NaN',max_y)['Total Terr(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='grey',alpha=0.3)
        
        ## Plot the total gm2d, then if the composition data is NA it will just plot the total
        #data_to_plot['Total(gm2d)'].plot(kind='bar',stacked=True,ax=axes1[x],color='y',alpha=0.5,label='Total(no comp.)')
        
        ## create dataframe of sed and precip
        sed = pd.DataFrame({'Total Org(gm2d)':data_to_plot['Total Org(gm2d)'].values,'Total Terr(gm2d)':data_to_plot['Total Terr(gm2d)'].values,'Precip':data_to_plot['Precip'].values, 'SSY':data_to_plot['SSY'].values,'Waves':data_to_plot['Waves'].values}, index=data_to_plot['Month'].values)
        ## Plot data values in color over the grey
        sed[['Total Org(gm2d)','Total Terr(gm2d)']].plot(kind='bar',stacked=True,ax=axes1[x],color=['g','r','b'])
        
        ## Plot SSY data
        ax2=axes1[x].twinx()
        ax2.yaxis.set_ticks_position('right')
        ax2.plot(axes1[x].get_xticks(),sed['SSY'],ls='-',color='r',label='SSY(tons)')  
        ax2.set_ylim(0,250), ax2.xaxis.set_visible(False),ax2.yaxis.set_visible(False)
        for tl in ax2.get_yticklabels():
            tl.set_color('r')
        ## Plot Precip data
        ax3=axes1[x].twinx()
        ax3.yaxis.set_ticks_position('right')
        ax3.plot(axes1[x].get_xticks(),sed['Precip'],ls='-',color='b',label='Precip(mm)')  
        ax3.set_ylim(0,2000), ax3.xaxis.set_visible(False),ax3.yaxis.set_visible(False)
        ax3.spines['right'].set_position(('axes', 1.2))
        for tl in ax3.get_yticklabels():
            tl.set_color('b')
        ## Plot Wave data
        ax4=axes1[x].twinx()
        ax4.yaxis.set_ticks_position('right')
        ax4.plot(axes1[x].get_xticks(),sed['Waves'],ls='-',color='k',label='MMSWH(m)')  
        ax4.set_ylim(0,2.5), ax4.xaxis.set_visible(False),ax4.yaxis.set_visible(False)
        ax4.spines['right'].set_position(('axes', 1.6))
        
        ## y labels
        if x==2 or x==5 or x==8:
            ax2.yaxis.set_visible(True), ax2.set_ylabel('SSY(tons)',color='r')
            ax3.yaxis.set_visible(True), ax3.set_ylabel('Precip(mm)',color='b')
            ax4.yaxis.set_visible(True), ax4.set_ylabel('MMSWH(m)',color='k')
            
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
    fig.legend(handles,labels,'upper center',ncol=6,fontsize=12)
    plt.subplots_adjust(top=0.90)
    show_plot(show,fig)
    savefig(save,filename)
    return
#Sed_Comp_Terr_v_SSY_TS(SedPods,max_y=40,plot_health_thresholds=False,show=True,save=True,filename=rawfig+'SedPods-composition and precip')
#Sed_Comp_Terr_v_Precip_SSY_TS(SedTubes,max_y=650,plot_health_thresholds=False,show=True,save=True,filename=rawfig+'SedTubes-composition P SSY MMSWH')


#### Plot each SedPod/SedTube over time
def Sed_Comp_Terr_timeseries_single(data,max_y=40,plot_health_thresholds=False,show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, ax = plt.subplots(1,1,figsize=(6,4))
    labels=['organic','terrigenous','No Data']
    colors=['green','red','grey']
    bars=[ax.bar(0,0,color=c,label=l) for c,l in zip(colors,labels)]
    lines= ax.plot(0,0,color='b',marker='s',label='Precip(mm)')
    handles, labels = ax.get_legend_handles_labels()
    ## Plot Sed data
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        print x, loc
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data_to_plot = data[data['Pod(P)/Tube(T)'] == loc]
        ## calculate weight of terrigenous sed
        data_to_plot['Total Org(gm2d)'] = data_to_plot['Total(gm2d)'] * data_to_plot['Total(%organic)']/100
        data_to_plot['Total Terr(gm2d)'] = data_to_plot['Total(gm2d)'] * data_to_plot['Total(%terr)']/100

        ## Select the points with NA values and replace with the ylim, plot all as grey
        data_to_plot.replace('NaN',max_y)['Total Terr(gm2d)'].plot(ax=ax,color='grey',ls='None',marker='s',label='No Data')
        
        ## Plot the total gm2d, then if the composition data is NA it will just plot the total
        data_to_plot['Total(gm2d)'].plot(ax=ax,color='y',ls='None',marker='s',label='Total(no comp.)')
    return
#Sed_Comp_Terr_timeseries_single(SedTubes,max_y=650,plot_health_thresholds=True,show=True,save=True,filename=rawfig+'SedTubes-composition and precip')



#### Are Waves and SSY correlated?
#ssy_and_waves = SedPods[SedPods.index=='P1A'][['SSY','Waves']]
#ssy_v_waves = sm.OLS(ssy_and_waves['SSY'],ssy_and_waves['Waves']).fit()
#ssy_v_waves_r2, ssy_v_waves_pval = ssy_v_waves.rsquared_adj, ssy_v_waves.pvalues
#ssy_v_waves_VIF = 1/(1-ssy_v_waves_r2)
#
#
#
#
### Plot Sed data
#for x, loc in enumerate(np.sort(SedTubes['Pod(P)/Tube(T)'].value_counts().index.values)):
#    print x, loc
#    ## Select data corresponding to the site location e.g. P1A, T2B etc
#    Tube = SedTubes[SedTubes['Pod(P)/Tube(T)'] == loc]
#    Tube = Tube[['Month','SSY','Waves','Total(gm2d)']]
#    est = sm.OLS(Tube['Total(gm2d)'],Tube[['SSY','Waves']]).fit()
#
#    r2_adj = est.rsquared_adj
#    pvals = est.pvalues
#    print 'SSY: '+'%.2f'%est.params['SSY']+'  '+'Waves: '+'%.2f'%est.params['Waves']
#









