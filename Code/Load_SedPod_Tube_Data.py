# -*- coding: utf-8 -*-
"""
Created on Tue Jan 12 14:51:35 2016

@author: Alex
"""
import pandas as pd
from scipy.stats import spearmanr as spearman_r
import statsmodels.api as sm
import statsmodels.formula.api as smf

## Set Pandas display options
pd.set_option('display.large_repr', 'truncate')
pd.set_option('display.width', 180)
pd.set_option('display.max_rows', 30)
pd.set_option('display.max_columns', 13)


def show_plot(show=False,fig=figure):
    if show==True:
        plt.show()
def savefig(fig,save=True,filename=''):
    if save==True:
        fig.savefig(filename+'.pdf') ## for publication
        fig.savefig(filename+'.png') ## for manuscript
    return
    
    
## Set Directories
maindir = 'C:/Users/Alex/Documents/GitHub/Fagaalu-Sedimentation/'
datadir = maindir+'Data/'
watersheddir  = datadir+'Fagaalu_watershed/'
wavedir = datadir+'WW3_data/'
GISdir = datadir+'GIS/'
rawfig= maindir+'rawfig/'
figdir= maindir+'Figures/'
tabledir= maindir+'Tables/'

## Open Spreadsheet of data
BulkWeight_XL = pd.ExcelFile(datadir+'CRCP Sediment Data Bulk Weight and Composition.xlsx')
Comp_XL = pd.ExcelFile(datadir+'LOI/Messina LOI.xls')
Precip_daily = pd.DataFrame.from_csv(watersheddir+'Fagaalu_rain_gauge-Daily.csv')#.resample('M',how='sum')
SSY_daily = pd.DataFrame.from_csv(watersheddir+'SSY_daily-measured and predicted.csv')#.resample('M',how='sum') from code: SedFlux_for_SedPods.py
Waves = pd.DataFrame.from_csv(wavedir+'point_data.csv')
Waves_daily = Waves.resample('1D',how='mean')

SedPods, SedTubes = pd.DataFrame(),pd.DataFrame()

count = 0
for sheet in Comp_XL.sheet_names[1:12]:
#for sheet in Comp_XL.sheet_names[4:5]:
    print sheet
    count +=1
    ## Forcing Data
    sampleDates = BulkWeight_XL.parse(sheet,parse_cols='A:B',index_col=1,parse_dates=True)[:2] 
    start, end = pd.to_datetime(sampleDates.index[0]), pd.to_datetime(sampleDates.index[1])
    ## Total Precip
    precip_month = Precip_daily.ix[start:end].sum()[0]
    ## Total SSY
    ssy_month = SSY_daily['SSY_combined'].ix[start:end].sum()
    ## Mean monthly (from mean daily) Significant Wave Height (m)
    waves_month = Waves_daily['Thgt[unit="meters"]'].ix[start:end].mean()  
    
    print 'start: '+str(start)+' end: '+str(end)+' precip: '+"%.0f"%precip_month+' ssy: '+"%.0f"%ssy_month+' waves: '"%.2f"%waves_month
    ## Open data and replace NO SED and N/A values
    BulkWeight_Data = BulkWeight_XL.parse(sheet,header=7,na_values=['NAN','N/A (disturbed)'],parse_cols='A:D,F:L',index_col=0)
    BulkWeight_Data['Pod(P)/Tube(T)'] = BulkWeight_Data.index
    BulkWeight_Data = BulkWeight_Data.replace('NO SED',0.00001)
    BulkWeight_Data = BulkWeight_Data.replace('N/A (disturbed)',np.NaN)
    ## Change negative values to zero (actually to .00001 so you don't divide by zero later)
    ## CAREFUL!! Don't replace the NaN values with .00001
    BulkWeight_Data['Mass Sand Fraction'][BulkWeight_Data['Mass Sand Fraction'] < 0] = .0001
    BulkWeight_Data['Mass Fine Fraction'][BulkWeight_Data['Mass Fine Fraction'] < 0] = .0001
    ## Calculate Total Bulk weight
    BulkWeight_Data['Total(g)'] = BulkWeight_Data['Mass Sand Fraction'] + BulkWeight_Data['Mass Fine Fraction']
    
    ## Calculate g/m2/day
    BulkWeight_Data['Total_gm2d'] = BulkWeight_Data['Total(g)']/BulkWeight_Data['Area(m2)']/BulkWeight_Data['Days deployed:']
    BulkWeight_Data['Coarse(gm2d)'] = BulkWeight_Data['Mass Sand Fraction']/BulkWeight_Data['Area(m2)']/BulkWeight_Data['Days deployed:']
    BulkWeight_Data['Fine_gm2d'] = BulkWeight_Data['Mass Fine Fraction']/BulkWeight_Data['Area(m2)']/BulkWeight_Data['Days deployed:']
    ## Round
    round_num = 5
    BulkWeight_Data['Total_gm2d']=BulkWeight_Data['Total_gm2d'].round(round_num)
    BulkWeight_Data['Coarse(gm2d)']=BulkWeight_Data['Coarse(gm2d)'].round(round_num)
    BulkWeight_Data['Fine_gm2d']=BulkWeight_Data['Fine_gm2d'].round(round_num)
    ## Add Month
    BulkWeight_Data['Month'] = sheet
    BulkWeight_Data['start'] = start
    BulkWeight_Data['end'] = end
    ## Add Monthly precip
    BulkWeight_Data['Precip'] = precip_month
    ## Add Monthly SSY data
    BulkWeight_Data['SSY'] = ssy_month
    ## Add Monthly Wave data
    BulkWeight_Data['Waves'] = waves_month
    
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
    
    
    BulkWeight_Data['Total_Org_gm2d'] = BulkWeight_Data['Total_gm2d'] * BulkWeight_Data['Total(%organic)']/100
    BulkWeight_Data['Total_Terr_gm2d'] = BulkWeight_Data['Total_gm2d'] * BulkWeight_Data['Total(%terr)']/100
    BulkWeight_Data['Total_TerrOrg_gm2d'] = BulkWeight_Data['Total_Terr_gm2d'] + BulkWeight_Data['Total_Org_gm2d'] 
    BulkWeight_Data['Total_Carb_gm2d'] = BulkWeight_Data['Total_gm2d'] * BulkWeight_Data['Total(%carb)']/100
    
    BulkWeight_Data['Coarse Org(gm2d)'] = BulkWeight_Data['Coarse(gm2d)'] * BulkWeight_Data['Coarse(%organic)']/100
    BulkWeight_Data['Coarse Terr(gm2d)'] = BulkWeight_Data['Coarse(gm2d)'] * BulkWeight_Data['Coarse(%terr)']/100
    BulkWeight_Data['Coarse Terr+Org(gm2d)'] = BulkWeight_Data['Coarse Terr(gm2d)'] + BulkWeight_Data['Coarse Org(gm2d)'] 
    BulkWeight_Data['Coarse Carb(gm2d)'] = BulkWeight_Data['Coarse(gm2d)'] * BulkWeight_Data['Coarse(%carb)']/100
    
    BulkWeight_Data['Fine Org(gm2d)'] = BulkWeight_Data['Fine_gm2d'] * BulkWeight_Data['Fine(%organic)']/100
    BulkWeight_Data['Fine_Terr_gm2d'] = BulkWeight_Data['Fine_gm2d'] * BulkWeight_Data['Fine(%terr)']/100
    BulkWeight_Data['Fine_TerrOrg_gm2d'] = BulkWeight_Data['Fine_Terr_gm2d'] + BulkWeight_Data['Fine Org(gm2d)'] 
    BulkWeight_Data['Fine_Carb_gm2d'] = BulkWeight_Data['Fine_gm2d'] * BulkWeight_Data['Fine(%carb)']/100

    ## Categorize by Tubes and Pods
    Pods = BulkWeight_Data[BulkWeight_Data['Pod(P)/Tube(T)'].isin(['P1A','P2A','P3A','P1B','P2B','P3B','P1C','P2C','P3C'])]
    Tubes = BulkWeight_Data[BulkWeight_Data['Pod(P)/Tube(T)'].isin(['T1A','T2A','T3A','T1B','T2B','T3B','T1C','T2C','T3C'])]    
    
    ## Add to All Samples
    #col_names = ['Month','start','end','Pod(P)/Tube(T)','Precip','SSY','Waves','Mass Sand Fraction','Mass Fine Fraction','Total(g)','Total_gm2d','Lat','Lon','Total(%organic)','Total(%carb)','Total(%terr)','Coarse(%organic)','Coarse(%carb)','Coarse(%terr)','Fine(%organic)','Fine(%carb)','Fine(%terr)']
    # SedPods
    SedPods = SedPods.append(Pods)
    # reorder columns
    #SedPods = SedPods[col_names]
    # SedTubes
    SedTubes = SedTubes.append(Tubes)
    #SedTubes = SedTubes[col_names]

def pval_aster(pval):
    #print pval
    try:
        pval = float(pval)
    except: 
        pval = np.nan
    if pval >= 0.10:
        ast = ''
        pcol = 'grey'
    if pval < 0.10 and pval>=0.05:
        ast = '+'
        pcol = 'k'
    elif pval < 0.05 and pval >= 0.01:
        ast = '*'
        pcol = 'r'
    elif pval < 0.01 and pval >= 0.001:
        ast = '**'
        pcol = 'y'
    elif pval < 0.001:
        ast = '***'
        pcol = 'g'
    elif np.isnan(pval)==True:
        ast='NaN'
        pcol = 'grey'
    return ast, pcol

#### Plot each SedPod vs SSY
def SedAcc_vs_SSY_Waves(data,sed_acc='Total_gm2d',max_y=40,plot_health_thresholds=False,show=True,save=False,filename=''):  
    plt.ioff()
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]

    north_reef = ['1A','1B','1C','2A','2C']
    south_reef = ['2B','3A','3B','3C']
    if 'T1A' in data['Pod(P)/Tube(T)'].values:
        tubes_or_pods = 'Tubes'
        north_reef = ['T'+x for x in north_reef] 
        south_reef = ['T'+x for x in south_reef] 
    if 'P1A' in data['Pod(P)/Tube(T)'].values:
        tubes_or_pods = 'Pods'
        north_reef = ['P'+x for x in north_reef] 
        south_reef = ['P'+x for x in south_reef]     
    ## Plot accumulation
    fig, axes = plt.subplots(3, 3,sharey=False,figsize=(12,8))
    ## Plot residuals of Sed_Acc and SSY
    fig_resid, axes_resid = plt.subplots(3, 3,sharey=False,figsize=(12,8))

    ## Regressions
    reg = pd.DataFrame()    
    reg_table = pd.DataFrame()
    ## Plot Sed data
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        print x, loc
        ## Data for Regression
        reg_loc = data[data['Pod(P)/Tube(T)'] == loc][['Month',sed_acc,'SSY','Waves']]
        reg_loc = reg_loc.dropna()
        reg = reg.append(reg_loc)
        ## Fit regression
        #reg_mod = sm.OLS(reg_loc[sed_acc], reg_loc[['SSY','Waves']]).fit()
        reg_mod = smf.ols(formula=sed_acc+" ~ SSY + Waves", data=reg_loc).fit()
        ## regression betas
        SSY_beta, Waves_beta = '%.3f'%reg_mod.params['SSY'], '%.3f'%reg_mod.params['Waves']
        ## P values
        SSY_pval  = '%.3f'%reg_mod.pvalues['SSY'] + pval_aster(reg_mod.pvalues['SSY'])[0]
        SSY_pval_col = pval_aster(reg_mod.pvalues['SSY'])[1]
        Waves_pval = '%.3f'%reg_mod.pvalues['Waves'] + pval_aster(reg_mod.pvalues['Waves'])[0]
        Waves_pval_col = pval_aster(reg_mod.pvalues['Waves'])[1]
        ## Spearman
        SSY_spear = spearman_r(reg_loc[sed_acc], reg_loc['SSY'])
        if SSY_spear[1] < 0.10:
            SSY_spear_r = '%.3f'%SSY_spear[0]
        elif SSY_spear[1] >= 0.10:
            SSY_spear_r = ''
        Waves_spear = spearman_r(reg_loc[sed_acc], reg_loc['Waves'])
        if Waves_spear[1] < 0.10:
            Waves_spear_r = '%.3f'%Waves_spear[0]
        elif Waves_spear[1] >= 0.10:
            Waves_spear_r = ''
        ## Make table of model parameters
        reg_mod_table = pd.DataFrame({'Sed':sed_acc, 'r2adj':'%.2f'%reg_mod.rsquared_adj,'SSY_spear_r':SSY_spear_r,'SSY_beta':SSY_beta,'SSY_pval':SSY_pval[:5],'Waves_spear_r':Waves_spear_r,'Waves_beta':Waves_beta,'Waves_pval':Waves_pval[:5]},index=[loc])
        reg_table = reg_table.append(reg_mod_table)
        
        ## PLOTS
        axes1=axes.reshape(-1)
        ## Plot SSY vs Sed_Acc
        reg_loc.plot(x='SSY',y=sed_acc,ax=axes1[x],color='r',ls='None',marker='o',fillstyle='none')
        axes1[x].set_xlim(0,250), axes1[x].set_ylim(0,max_y)
        ## Plot Waves vs Sed_Acc
        axes2 = axes1[x].twiny()
        reg_loc.plot(x='Waves',y=sed_acc,ax=axes2,color='b',ls='None',marker='s',fillstyle='none')
        axes2.set_xlim(0,2.5), axes2.set_ylim(0,max_y)
        
        ## Figure/Plots of residuals vs predicted value
        axes1_resid = axes_resid.reshape(-1)        
        sed_acc_vs_ssy_mod = sm.OLS(reg_loc[sed_acc], reg_loc['SSY']).fit()
        sed_acc_vs_ssy_mod = smf.ols(formula=sed_acc+" ~ SSY", data=reg_loc).fit()
        reg_loc['SSY_resid'] = sed_acc_vs_ssy_mod.resid
        reg_loc['SSY_pred'] = sed_acc_vs_ssy_mod.predict()
        reg_loc.plot(x='SSY_pred',y='SSY_resid',ax=axes1_resid[x],color='k',ls='None',marker='v')
        axes1_resid[x].set_ylabel('SSY residuals'), axes1_resid[x].set_xlim(0,reg_loc['SSY_pred'].max()*1.1)
        axes1_resid[x].grid(False)
        ## Annotate Points
        for row in reg_loc.iterrows():
            print row[1]['Month']
            try:
                #axes1[x].annotate(row[1]['Month'],xy=(row[1]['SSY']+10,row[1]['Total_TerrOrg_gm2d']),fontsize=6)
                print
            except:
                raise   
        ## Format subplot
        axes1[x].xaxis.set_visible(False), axes2.xaxis.set_visible(False)
        axes1[x].tick_params(labelsize=8), axes2.tick_params(labelsize=8)
        axes1[x].xaxis.grid(False), axes2.xaxis.grid(False)
        axes1[x].legend().set_visible(False), axes2.legend().set_visible(False)
        # Subplot title eg P1A
        axes1[x].text(0.05,.95,loc,verticalalignment='top', horizontalalignment='left',transform=axes1[x].transAxes)
        ## Plot text Pvalues
        axes1[x].text(0.55,.95,'p_SSY:'+SSY_pval,verticalalignment='top', horizontalalignment='left',transform=axes1[x].transAxes,fontsize=9,color=SSY_pval_col)
        axes1[x].text(0.55,.90,'p_Wave:'+Waves_pval,verticalalignment='top', horizontalalignment='left',transform=axes1[x].transAxes,fontsize=9,color=Waves_pval_col)        
                
        if x<=2:
            axes2.xaxis.set_visible(True), axes2.set_xlabel('Waves (m)',color='b')
            for tl in axes2.get_xticklabels():
                tl.set_color('b')
                
    ## Label left axes
    axes[0,0].set_ylabel('NORTHERN \n g/'+r'$m^2$'+'/day')
    axes[1,0].set_ylabel('CENTRAL \n g/'+r'$m^2$'+'/day')
    axes[2,0].set_ylabel('SOUTHERN \n g/'+r'$m^2$'+'/day') 
    #axes[0,0].set_ylim(0,max_y)
    axes[2,0].set_xlabel('SSY (tons)',color='r'), axes[2,1].set_xlabel('SSY (tons)',color='r'), axes[2,2].set_xlabel('SSY (tons)',color='r')
    ## turn on axes
    for ax in axes[2]:
        ax.xaxis.set_visible(True)
        for tl in ax.get_xticklabels():
            tl.set_color('r')
    fig.tight_layout(pad=0.2)
    fig.subplots_adjust(top=0.9), fig.suptitle(tubes_or_pods+' '+sed_acc,fontsize=16)
    
    fig_resid.tight_layout(pad=0.2)
    fig_resid.subplots_adjust(top=0.9), fig_resid.suptitle(tubes_or_pods+' '+sed_acc,fontsize=16)
    
    show_plot(show,fig)
    savefig(fig,save,filename)
    savefig(fig_resid,save,filename+'_residuals')
    
    ### Mean North/South
    north_sed = data[data['Pod(P)/Tube(T)'].isin(north_reef)].dropna()
    south_sed = data[data['Pod(P)/Tube(T)'].isin(south_reef)].dropna()

    north_mean_acc = pd.DataFrame()
    south_mean_acc = pd.DataFrame()
    ## Select Sed data
    for mon in Comp_XL.sheet_names[1:12]:
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        ## Mean organic
        north_mean_sed_acc = north_sed[north_sed['Month'] == mon][sed_acc].mean()
        south_mean_sed_acc = south_sed[south_sed['Month'] == mon][sed_acc].mean() 
        ## Aux Data
        precip = north_sed[north_sed['Month'] == mon]['Precip'].max()
        ssy = north_sed[north_sed['Month'] == mon]['SSY'].max()
        waves = north_sed[north_sed['Month'] == mon]['Waves'].max()
        ## Make DF
        north_mean_acc = north_mean_acc.append(pd.DataFrame({sed_acc:north_mean_sed_acc,'Precip':precip,'SSY':ssy,'Waves':waves},index=['North_'+tubes_or_pods]))
        south_mean_acc = south_mean_acc.append(pd.DataFrame({sed_acc:south_mean_sed_acc,'Precip':precip,'SSY':ssy,'Waves':waves},index=['South_'+tubes_or_pods]))
     
    for data in [north_mean_acc, south_mean_acc]:
        ## Regression for Monthly mean on North/South
        ## Data for Regression
        reg_loc = data[[sed_acc,'SSY','Waves']]
        reg = reg.append(reg_loc)
        ## Fit regression
        reg_mod = sm.OLS(reg_loc[sed_acc], reg_loc[['SSY','Waves']]).fit()
        reg_mod = smf.ols(formula=sed_acc+" ~ SSY + Waves", data=reg_loc).fit()
        ## regression betas
        SSY_beta, Waves_beta = '%.3f'%reg_mod.params['SSY'], '%.3f'%reg_mod.params['Waves']
        ## P values
        SSY_pval  = '%.3f'%reg_mod.pvalues['SSY'] + pval_aster(reg_mod.pvalues['SSY'])[0]
        SSY_pval_col = pval_aster(reg_mod.pvalues['SSY'])[1]
        Waves_pval = '%.3f'%reg_mod.pvalues['Waves'] + pval_aster(reg_mod.pvalues['Waves'])[0]
        Waves_pval_col = pval_aster(reg_mod.pvalues['Waves'])[1]
        ## Spearman
        SSY_spear = spearman_r(reg_loc[sed_acc], reg_loc['SSY'])
        if SSY_spear[1] < 0.10:
            SSY_spear_r = '%.3f'%SSY_spear[0]
        elif SSY_spear[1] >= 0.10:
            SSY_spear_r = ''
        Waves_spear = spearman_r(reg_loc[sed_acc], reg_loc['Waves'])
        if Waves_spear[1] < 0.10:
            Waves_spear_r = '%.3f'%Waves_spear[0]
        elif Waves_spear[1] >= 0.10:
            Waves_spear_r = ''
        
        reg_mod_table = pd.DataFrame({'Sed':sed_acc, 'r2adj':'%.2f'%reg_mod.rsquared_adj,'SSY_spear_r':SSY_spear_r,'SSY_beta':SSY_beta,'SSY_pval':SSY_pval[:5],'Waves_spear_r':Waves_spear_r,'Waves_beta':Waves_beta,'Waves_pval':Waves_pval[:5]},index=[data.index[0]])
        reg_table = reg_table.append(reg_mod_table)
 
    return reg_table[['Sed','r2adj','SSY_spear_r','SSY_beta','SSY_pval','Waves_spear_r','Waves_beta','Waves_pval']]
    
## SHOW == True    

## TOTAL
#Pods_Total = SedAcc_vs_SSY_Waves(SedPods,'Total_gm2d',max_y=40,plot_health_thresholds=False,show=True,save=False,filename='')
#Tubes_Total= SedAcc_vs_SSY_Waves(SedTubes,'Total_gm2d',max_y=600,plot_health_thresholds=False,show=True,save=False,filename='')  
## TERR
#Pods_Terr = SedAcc_vs_SSY_Waves(SedPods,'Total_Terr_gm2d',max_y=40,plot_health_thresholds=False,show=True,save=False,filename='')
#Tubes_Terr= SedAcc_vs_SSY_Waves(SedTubes,'Total_Terr_gm2d',max_y=600,plot_health_thresholds=False,show=True,save=False,filename='')  
## TERR + ORG
#Pods_TerrOrg = SedAcc_vs_SSY_Waves(SedPods,'Total_TerrOrg_gm2d',max_y=40,plot_health_thresholds=False,show=True,save=False,filename='')
#Tubes_TerrOrg= SedAcc_vs_SSY_Waves(SedTubes,'Total_TerrOrg_gm2d',max_y=600,plot_health_thresholds=False,show=True,save=False,filename='')     
### CARB
#Pods_Carb = SedAcc_vs_SSY_Waves(SedPods,'Total_Carb_gm2d',max_y=40,plot_health_thresholds=False,show=True,save=False,filename='')
#Tubes_Carb= SedAcc_vs_SSY_Waves(SedTubes,'Total_Carb_gm2d',max_y=600,plot_health_thresholds=False,show=True,save=False,filename='')  

## FINE TERR
#Pods_Terr = SedAcc_vs_SSY_Waves(SedPods,'Fine_Terr_gm2d',max_y=40,plot_health_thresholds=False,show=True,save=False,filename='')
#Tubes_Terr= SedAcc_vs_SSY_Waves(SedTubes,'Fine_Terr_gm2d',max_y=600,plot_health_thresholds=False,show=True,save=False,filename='')  

### Compile all regression models
## Plot and save all of them, but don't display them
Regressions = pd.DataFrame()
comps = ['Total_gm2d', 'Total_Terr_gm2d', 'Total_TerrOrg_gm2d', 'Total_Carb_gm2d']
comps = ['Fine_gm2d', 'Fine_Terr_gm2d', 'Fine_TerrOrg_gm2d', 'Fine_Carb_gm2d']
for comp in comps:
    Regressions = Regressions.append(SedAcc_vs_SSY_Waves(SedPods,comp,max_y=25,plot_health_thresholds=False,show=False,save=True,filename=rawfig+'Regressions_Pods/'+comp.replace(" ", "")) )
    Regressions = Regressions.append(SedAcc_vs_SSY_Waves(SedTubes,comp,max_y=600,plot_health_thresholds=False,show=False,save=True,filename=rawfig+'Regressions_Tubes/'+comp.replace(" ", "")) )
    plt.close('all')
Regressions = Regressions[['Sed','SSY_spear_r','SSY_beta','Waves_spear_r','Waves_beta','SSY_pval','Waves_pval','r2adj']]

## Save to csv
#Regressions.to_csv(datadir+'Regressions.csv')


### Significant SSY
#Regressions[Regressions['SSY_pval'].astype(np.float)<0.10]
### Significant Waves
#Regressions[Regressions['Waves_pval'].astype(np.float)<0.10]
### Both SSY and Waves
#Regressions[Regressions['r2adj'].astype(np.float)<0.10]

def summary_table_DFs():
    ## Make summary table of Pvalues
    pval_summary_table = pd.DataFrame()
    for x, loc in enumerate(Regressions.index.unique()):
        print loc
        
        reg = Regressions.ix[loc].T
        reg.columns = reg.ix['Sed'].values
        
        def pval_asterisks_together(name):
            pval_wave = pval_aster(reg.ix['Waves_pval'][name])[0]
            if pval_wave != '':
                pval_wave = 'w'+'<sup>'+ pval_wave+'</sup>'
                
            pval_ssy = pval_aster(reg.ix['SSY_pval'][name])[0] 
            if pval_ssy != '':
                pval_ssy = ' ssy'+'<sup>'+pval_ssy +'</sup>'
            pvals = pval_wave + pval_ssy
            return pvals
            
        total = pval_asterisks_together(comps[0])
        total_terr = pval_asterisks_together(comps[1])
        total_terr_org = pval_asterisks_together(comps[2])
        total_carb = pval_asterisks_together(comps[3])
    
        pval_summary_table = pval_summary_table.append(pd.DataFrame({comps[0]:total,comps[1]:total_terr, comps[2]:total_terr_org, comps[3]:total_carb},index=[loc]))
    
    
    ## Make summary table of Spearman R
    spear_summary_table = pd.DataFrame()
    for x, loc in enumerate(Regressions.index.unique()):
        #print loc
        
        reg = Regressions.ix[loc].T
        reg.columns = reg.ix['Sed'].values
        
        def spearman_together(name):
            spear_wave = reg.ix['Waves_spear_r'][name]
            if spear_wave != '':
                spear_wave = 'w: '+spear_wave
            spear_ssy = reg.ix['SSY_spear_r'][name]
            if spear_ssy != '':
                spear_ssy = ' ssy:'+spear_ssy
            spear = spear_wave + spear_ssy
            return spear
            
        total = spearman_together(comps[0])
        total_terr = spearman_together(comps[1])
        total_terr_org = spearman_together(comps[2])
        total_carb = spearman_together(comps[3])
    
        spear_summary_table = spear_summary_table.append(pd.DataFrame({comps[0]:total,comps[1]:total_terr, comps[2]:total_terr_org, comps[3]:total_carb},index=[loc]))
    return pval_summary_table[[comps[0],comps[1],comps[2],comps[3]]], spear_summary_table[[comps[0],comps[1],comps[2],comps[3]]]
    
pval_summary_table, spear_summary_table = summary_table_DFs() 
    
    
## Call R modules
#from rpy2.robjects.packages import importr
import rpy2.robjects as ro
import pandas.rpy.common as com

## Make sure R is communicating
ro.r('x=c()')
ro.r('x[1]="lets talk to R"')
print(ro.r('x'))

### Summary Table to htmlTables
def summary_table_R(summary_table, caption, browser=True):

    ## convert to R Data Frame
    table_df = com.convert_to_r_dataframe(summary_table)
    #caption="Significant p values for Waves; SSY."
    table_num=1
    ## Send to R
    ro.globalenv['table_df_vals'] = table_df
    ## format #s
    ro.r("table_df= apply(table_df_vals, 2, function(x) as.character(format(x,digits=2)))")
    ro.r("rownames(table_df)<- rownames(table_df_vals) ")
    #print (ro.r('table_df'))
    ro.globalenv['table_caption'] = 'Table '+str(table_num)+'. '+caption
    ## import htmlTable
    ro.r("library(htmlTable)")
    ## Create table in R
    table_code_str = " \
    table_df, \
    header= c('"+comps[0]+"', '"+comps[1]+"', '"+comps[2]+"', '"+comps[3]+"'), \
    caption=table_caption, \
    css.cell = 'padding-left: .5em; padding-right: .2em;'  \
    "
    ## run htmlTable
    ro.r("table_out <- htmlTable("+table_code_str+")")
    ## output to browser
    if browser == True:
        print (ro.r("table_out"))
    ## save to html from R
    ro.r("setwd("+"'"+tabledir+"'"+")")
    ro.r("sink('Table"+str(table_num)+"_pvalues.html')")
    ro.r("print(table_out,type='html',useViewer=FALSE)")
    ro.r("sink()")
    
    ## send back to python
    #htmlcode = com.load_data("table_out")[0] 
    #print htmlcode
    ## output to file through pandoc
    #pypandoc.convert(htmlcode, 'markdown', format='markdown', outputfile= datadir+'landcover.html')
    return 
summary_table_R(pval_summary_table, "P-values", browser=True)
summary_table_R(spear_summary_table, "Spearman correlation coefficients", browser=True)








#### Plot each SedPod vs Precip
def SedAcc_vs_Precip(data,max_y=40,plot_health_thresholds=False,show=True,save=False,filename=''):    
    cols =data['Pod(P)/Tube(T)'].value_counts().shape[0]
    fig, axes = plt.subplots(3, 3,sharey=True,figsize=(10,8))

    ## Plot Sed data
    for x, loc in enumerate(np.sort(data['Pod(P)/Tube(T)'].value_counts().index.values)):
        print x, loc
        axes1=axes.reshape(-1)
        
        ## Select data corresponding to the site location e.g. P1A, T2B etc
        data_to_plot = data[data['Pod(P)/Tube(T)'] == loc]
        ## calculate weight of terrigenous sed
        data_to_plot['Total_Org_gm2d'] = data_to_plot['Total_gm2d'] * data_to_plot['Total(%organic)']/100
        data_to_plot['Total_Terr_gm2d'] = data_to_plot['Total_gm2d'] * data_to_plot['Total(%terr)']/100
        data_to_plot['Total_TerrOrg_gm2d'] = data_to_plot['Total_Terr_gm2d'] + data_to_plot['Total_Org_gm2d'] 

        ## Plot the total gm2d, then if the composition data is NA it will just plot the total
        data_to_plot.plot(x='Precip',y='Total_TerrOrg_gm2d',ax=axes1[x],color='k',ls='None',marker='o')
        
        for row in data_to_plot.dropna().iterrows():
            print row[1]['Month']
            try:
                axes1[x].annotate(row[1]['Month'],xy=(row[1]['Precip']+10,row[1]['Total_TerrOrg_gm2d']),fontsize=6)
            except:
                raise

    
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

    #show_plot(show,fig)
    #savefig(save,filename)
    return
#SedAcc_vs_Precip(SedPods,max_y=40,plot_health_thresholds=False,show=True,save=False,filename='')
#SedAcc_vs_Precip(SedTubes,max_y=600,plot_health_thresholds=False,show=True,save=False,filename='')  
    
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
                SedPods_TS[col].ix[dep_start:dep_end] = row[1]['Total_gm2d'] 
                # Add Precip data
                SedPods_TS['Precip'].ix[dep_start:dep_end] = row[1]['Precip']
            # Point lines
            if as_lines == True:
                SedPods_TS[col].ix[dep_end] = row[1]['Total_gm2d'] 
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
                SedTubes_TS[col].ix[dep_start:dep_end] = row[1]['Total_gm2d'] 
                SedTubes_TS['Precip'].ix[dep_end] = row[1]['Precip']
            # Point lines
            if as_lines == True:
                SedTubes_TS[col].ix[dep_end] = row[1]['Total_gm2d'] 
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
                SedPods_TS[col].ix[dep_start:dep_end] = row[1]['Total_gm2d'] 
                # Add Precip data
                SedPods_TS['Precip'].ix[dep_start:dep_end] = row[1]['Precip']
            # Point lines
            if as_lines == True:
                SedPods_TS[col].ix[dep_end] = row[1]['Total_gm2d'] 
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
                SedTubes_TS[col].ix[dep_start:dep_end] = row[1]['Total_gm2d'] 
                SedTubes_TS['Precip'].ix[dep_end] = row[1]['Precip']
            # Point lines
            if as_lines == True:
                SedTubes_TS[col].ix[dep_end] = row[1]['Total_gm2d'] 
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
# ex. SedPods[['Month','Total_gm2d','Total(%terr)']][0::9] gets P1A, [1::9] gets P1B etc
        






