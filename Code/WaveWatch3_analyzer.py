# -*- coding: utf-8 -*-
"""
Created on Tue Sep 08 15:32:05 2015

@author: Alex
"""
import netCDF4
from netCDF4 import Dataset
import numpy as np
import pandas as pd
plt.close('all')

datadir = 'C:/Users/Alex/Documents/GitHub/Fagaalu-Sedimentation/Data/WW3_data/'
datafile = datadir+'samoa_regional-2_12_14_2100.nc'

fh = Dataset(datafile, mode='r')
fv = fh.variables

params = [v for v in fv]
data_param = 'Thgt'
data_units = fh.variables[data_param].units
data = fh.variables[data_param][:][0,0,:,:]
lats, lons = fv['lat'][:], fv['lon'][:]
## Create DataFrame
## format lat/lons as they go in
df = pd.DataFrame(data.data,columns=['{:.2f}'.format(i) for i in lons], index=['{:.2f}'.format(i) for i in lats])

## Subset Data
## Lat/Lon subset bounding box
latbounds = [ '-14.60' , '-14.00' ] # string to .2f
lonbounds = [ '189.00' , '189.60' ] # degrees east ? 
# subset data
df_sub = df.ix[latbounds[0]:latbounds[1],lonbounds[0]:lonbounds[1]]
# subset lat/lons
lons = np.array([float(c) for c in df_sub.columns])
lats = np.array([float(c) for c in df_sub.index])

fh.close()

import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
plt.figure(figsize=(6,7))

m=Basemap(projection='merc',llcrnrlon=lons.min(),urcrnrlon=lons.max(),llcrnrlat=lats.min(),urcrnrlat=lats.max(),resolution='h')
x, y = m(*np.meshgrid(lons,lats))

df_sub_mask = np.ma.masked_invalid(df_sub.values)
cs = m.pcolormesh(x,y,df_sub_mask)

cbar = m.colorbar(cs, location='bottom', pad="5%")
cbar.set_label(data_units)

## Plot Station Point
fagaalu = {'name':'Fagaalu,AS','lon':'189.35','lat':'-14.30'}
x_i, y_i = m(float(fagaalu['lon']), float(fagaalu['lat']))
m.plot(x_i,y_i,color='k',marker='o', markersize=6)
# plot station data
data_at_point= "%.2f"%df_sub.ix[fagaalu['lat'],fagaalu['lon']]
plt.text(x_i,y_i,data_at_point,color='k',fontsize=12)

#m.bluemarble()
#m.etopo()
m.drawcoastlines()
#m.fillcontinents()
m.drawmapboundary()
m.drawparallels(np.arange(-15.,-13.,.2),labels=[1,0,0,0])
m.drawmeridians(np.arange(-175.,-168.,.2),labels=[0,0,1,0],rotation=60)

plt.subplots_adjust(top=0.04)
plt.show()

