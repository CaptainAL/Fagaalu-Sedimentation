# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:51:35 2016

@author: Alex
"""

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
    BulkWeight_Data['start'] = start
    BulkWeight_Data['end'] = end
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
    col_names = ['Month','start','end','Pod(P)/Tube(T)','Precip','Mass Sand Fraction','Mass Fine Fraction','Total(g)','Total(gm2d)','Lat','Lon','Total(%organic)','Total(%carb)','Total(%terr)','Coarse(%organic)','Coarse(%carb)','Coarse(%terr)','Fine(%organic)','Fine(%carb)','Fine(%terr)']
    # SedPods
    SedPods = SedPods.append(Pods[col_names])
    # reorder columns
    SedPods = SedPods[col_names]
    # SedTubes
    SedTubes = SedTubes.append(Tubes[col_names])
    SedTubes = SedTubes[col_names]
    
    
    
    
def Sed_Time_Series_plots():
    study_start , study_end= dt.datetime(2014,3,1), dt.datetime(2015,4,30)
    
    SedPods_TS= pd.DataFrame(columns=['Precip',u'P1A', u'P1B', u'P1C', u'P2A', u'P2B', u'P2C', u'P3A', u'P3B', u'P3C'], index=pd.date_range(study_start,study_end,freq='15Min'))
    
    as_lines = True
    
    # Create DataFrame of SedPods time series
    for col in SedPods_TS.columns:
        print col
        pod = SedPods[SedPods.index == col]
        for row in pod.iterrows():
            dep_start = row[1]['start']
            dep_end = row[1]['end'] - dt.timedelta(minutes = 15)
            # Stepped lines
            if as_lines == False:
                SedPods_TS[col].ix[dep_start:dep_end] = row[1]['Total(gm2d)'] 
                # Add Precip data
                SedPods_TS['Precip'].ix[dep_start:dep_end] = row[1]['Precip']
            # Point lines
            if as_lines == True:
                SedPods_TS[col].ix[dep_end] = row[1]['Total(gm2d)'] 
                # Add Precip data
                SedPods_TS['Precip'].ix[dep_end] = row[1]['Precip']
    
    
                
    if as_lines == True:            
        SedPods_TS = SedPods_TS.dropna()            
    
    fig, (precip, pods, tubes)  = plt.subplots(3,1,sharex = True,figsize=(11,7))
    SedPods_TS['Precip'].plot(ax=precip, c='b',ls='-')
    
    SedPods_TS['P1A'].plot(ax=pods, c='r',alpha=1)
    SedPods_TS['P1B'].plot(ax=pods, c='r',ls='--',alpha=0.8)
    SedPods_TS['P1C'].plot(ax=pods, c='r',ls='-.',alpha=0.6)
    
    SedPods_TS['P2A'].plot(ax=pods, c='y',alpha=1)
    SedPods_TS['P2B'].plot(ax=pods, c='y',ls='--',alpha=0.8)
    SedPods_TS['P2C'].plot(ax=pods, c='y',ls='-.',alpha=0.6)
    
    SedPods_TS['P3A'].plot(ax=pods, c='g',alpha=1)
    SedPods_TS['P3B'].plot(ax=pods, c='g',ls='--',alpha=0.8)
    SedPods_TS['P3C'].plot(ax=pods, c='g',ls='-.',alpha=0.6)
    
    pods.legend(bbox_to_anchor=(1.12,1))
    
    #plt.yscale('log')
    
    
    SedTubes_TS= pd.DataFrame(columns=[u'T1A', u'T1B', u'T1C', u'T2A', u'T2B', u'T2C', u'T3A', u'T3B', u'T3C'], index=pd.date_range(study_start,study_end,freq='15Min'))
    
    # Create DataFrame of SedPods time series
    for col in SedTubes_TS.columns:
        print col
        tube = SedTubes[SedTubes.index == col]
        for row in tube.iterrows():
            dep_start = row[1]['start']
            dep_end = row[1]['end'] - dt.timedelta(minutes = 15)
            # Stepped lines
            if as_lines == False:
                SedTubes_TS[col].ix[dep_start:dep_end] = row[1]['Total(gm2d)'] 
                SedTubes_TS['Precip'].ix[dep_end] = row[1]['Precip']
            # Point lines
            if as_lines == True:
                SedTubes_TS[col].ix[dep_end] = row[1]['Total(gm2d)'] 
                SedTubes_TS['Precip'].ix[dep_end] = row[1]['Precip']
                
    if as_lines == True:
        SedTubes_TS = SedTubes_TS.dropna()
        
    ax2 = fig.add_subplot()
    SedTubes_TS['T1A'].plot(ax=tubes, c='r',alpha=1)
    SedTubes_TS['T1B'].plot(ax=tubes, c='r',ls='--',alpha=0.8)
    SedTubes_TS['T1C'].plot(ax=tubes, c='r',ls='-.',alpha=0.6)
    
    SedTubes_TS['T2A'].plot(ax=tubes, c='y',alpha=1)
    SedTubes_TS['T2B'].plot(ax=tubes, c='y',ls='--',alpha=0.8)
    SedTubes_TS['T2C'].plot(ax=tubes, c='y',ls='-.',alpha=0.6)
    
    SedTubes_TS['T3A'].plot(ax=tubes, c='g',alpha=1)
    SedTubes_TS['T3B'].plot(ax=tubes, c='g',ls='--',alpha=0.8)
    SedTubes_TS['T3C'].plot(ax=tubes, c='g',ls='-.',alpha=0.6)
    
    tubes.legend(bbox_to_anchor=(1.12,1))
    
    pods.grid(False,which='both')
    tubes.grid(False,which='both')
    plt.subplots_adjust(left=0.05, right=0.90, top=0.95, bottom=0.08,hspace=0.1,wspace=0.01)
    
    #tubes.set_yscale('log')

    return
    
#Sed_Time_Series_plots()   


def Sed_Time_Series_dots():
    study_start , study_end= dt.datetime(2014,3,1), dt.datetime(2015,4,30)
    
    SedPods_TS= pd.DataFrame(columns=['Precip',u'P1A', u'P1B', u'P1C', u'P2A', u'P2B', u'P2C', u'P3A', u'P3B', u'P3C'], index=pd.date_range(study_start,study_end,freq='15Min'))
    
    as_lines = True
    
    # Create DataFrame of SedPods time series
    for col in SedPods_TS.columns:
        print col
        pod = SedPods[SedPods.index == col]
        for row in pod.iterrows():
            dep_start = row[1]['start']
            dep_end = row[1]['end'] - dt.timedelta(minutes = 15)
            # Stepped lines
            if as_lines == False:
                SedPods_TS[col].ix[dep_start:dep_end] = row[1]['Total(gm2d)'] 
                # Add Precip data
                SedPods_TS['Precip'].ix[dep_start:dep_end] = row[1]['Precip']
            # Point lines
            if as_lines == True:
                SedPods_TS[col].ix[dep_end] = row[1]['Total(gm2d)'] 
                # Add Precip data
                SedPods_TS['Precip'].ix[dep_end] = row[1]['Precip']
    
                
    if as_lines == True:            
        SedPods_TS = SedPods_TS.dropna()            
    
    fig, (precip, pods, tubes)  = plt.subplots(3,1,sharex = True,figsize=(11,7))
    SedPods_TS['Precip'].plot(ax=precip, c='b',ls='-')
    
    SedPods_TS['P1A'].plot(ax=pods, c='r',ls='None',marker='o',alpha=1)
    SedPods_TS['P1B'].plot(ax=pods, c='r',ls='None',marker='o',alpha=0.8)
    SedPods_TS['P1C'].plot(ax=pods, c='r',ls='None',marker='o',alpha=0.6)
    
    SedPods_TS['P2A'].plot(ax=pods, c='y',ls='None',marker='o',alpha=1)
    SedPods_TS['P2B'].plot(ax=pods, c='y',ls='None',marker='o',alpha=0.8)
    SedPods_TS['P2C'].plot(ax=pods, c='y',ls='None',marker='o',alpha=0.6)
    
    SedPods_TS['P3A'].plot(ax=pods, c='g',ls='None',marker='o',alpha=1)
    SedPods_TS['P3B'].plot(ax=pods, c='g',ls='None',marker='o',alpha=0.8)
    SedPods_TS['P3C'].plot(ax=pods, c='g',ls='None',marker='o',alpha=0.6)
    
    pods.legend(bbox_to_anchor=(1.12,1))
    
    #plt.yscale('log')
    
    
    SedTubes_TS= pd.DataFrame(columns=['Precip',u'T1A', u'T1B', u'T1C', u'T2A', u'T2B', u'T2C', u'T3A', u'T3B', u'T3C'], index=pd.date_range(study_start,study_end,freq='15Min'))
    
    # Create DataFrame of SedPods time series
    for col in SedTubes_TS.columns:
        print col
        tube = SedTubes[SedTubes.index == col]
        for row in tube.iterrows():
            dep_start = row[1]['start']
            dep_end = row[1]['end'] - dt.timedelta(minutes = 15)
            # Stepped lines
            if as_lines == False:
                SedTubes_TS[col].ix[dep_start:dep_end] = row[1]['Total(gm2d)'] 
                SedTubes_TS['Precip'].ix[dep_end] = row[1]['Precip']
            # Point lines
            if as_lines == True:
                SedTubes_TS[col].ix[dep_end] = row[1]['Total(gm2d)'] 
                SedTubes_TS['Precip'].ix[dep_end] = row[1]['Precip']
                
    if as_lines == True:
        SedTubes_TS = SedTubes_TS.dropna()
        
    ax2 = fig.add_subplot()
    SedTubes_TS['T1A'].plot(ax=tubes, c='r',ls='None',marker='o',alpha=1)
    SedTubes_TS['T1B'].plot(ax=tubes, c='r',ls='None',marker='o',alpha=0.8)
    SedTubes_TS['T1C'].plot(ax=tubes, c='r',ls='None',marker='o',alpha=0.6)
    
    SedTubes_TS['T2A'].plot(ax=tubes, c='y',ls='None',marker='o',alpha=1)
    SedTubes_TS['T2B'].plot(ax=tubes, c='y',ls='None',marker='o',alpha=0.8)
    SedTubes_TS['T2C'].plot(ax=tubes, c='y',ls='None',marker='o',alpha=0.6)
    
    SedTubes_TS['T3A'].plot(ax=tubes, c='g',ls='None',marker='o',alpha=1)
    SedTubes_TS['T3B'].plot(ax=tubes, c='g',ls='None',marker='o',alpha=0.8)
    SedTubes_TS['T3C'].plot(ax=tubes, c='g',ls='None',marker='o',alpha=0.6)
    
    tubes.legend(bbox_to_anchor=(1.12,1))
    
    pods.grid(False,which='both')
    tubes.grid(False,which='both')
    plt.subplots_adjust(left=0.05, right=0.90, top=0.95, bottom=0.08,hspace=0.1,wspace=0.01)
    
    #tubes.set_yscale('log')

    return
    
#Sed_Time_Series_dots() 
    
# Select individual location
# ex. SedPods[['Month','Total(gm2d)','Total(%terr)']][0::9] gets P1A, [1::9] gets P1B etc
        

#### Plot each SedPod vs Precip
def Sed_vs_Precip(data,max_y=40,plot_health_thresholds=False,show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(10,8))

    ## Plot Sed data
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        print x, loc
        axes1=axes.reshape(-1)
        
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data_to_plot = data[data['Pod(P)/Tube(T)'] == loc]
        ## calculate weight of terrigenous sed
        data_to_plot['Total Org(gm2d)'] = data_to_plot['Total(gm2d)'] * data_to_plot['Total(%organic)']/100
        data_to_plot['Total Terr(gm2d)'] = data_to_plot['Total(gm2d)'] * data_to_plot['Total(%terr)']/100
        data_to_plot['Total Terr+Org(gm2d)'] = data_to_plot['Total Terr(gm2d)'] + data_to_plot['Total Org(gm2d)'] 


        
        ## Plot the total gm2d, then if the composition data is NA it will just plot the total
        data_to_plot.plot(x='Precip',y='Total(gm2d)',ax=axes1[x],color='k',ls='None',marker='o')

    
        ## Format subplot
        axes1[x].xaxis.set_visible(False)
        axes1[x].tick_params(labelsize=8)
        axes1[x].xaxis.grid(False)
        axes1[x].legend().set_visible(False)
        # Subplot title eg P1A
        axes1[x].text(0.05,.95,loc,verticalalignment='top', horizontalalignment='left',transform=axes1[x].transAxes)
        
    ## Label left axes
    axes[0,0].set_ylabel('NORTHERN \n g/'+r'$m^2$'+'/day')
    axes[1,0].set_ylabel('CENTRAL \n g/'+r'$m^2$'+'/day')
    axes[2,0].set_ylabel('SOUTHERN \n g/'+r'$m^2$'+'/day') 
    axes[0,0].set_ylim(0,max_y)
    axes[2,0].set_xlabel('Precip (mm)'), axes[2,1].set_xlabel('Precip (mm)'), axes[2,2].set_xlabel('Precip (mm)')
    ## turn on axes
    for ax in axes[2]:
        ax.xaxis.set_visible(True)

    plt.tight_layout(pad=0.2)

    show_plot(show,fig)
    savefig(save,filename)
    return
#Sed_vs_Precip(SedPods,max_y=40,plot_health_thresholds=False,show=True,save=False,filename='')
Sed_vs_Precip(SedTubes,max_y=600,plot_health_thresholds=False,show=True,save=False,filename='')


