
# coding: utf-8

# # Assignment 2
# 
# Before working on this assignment please read these instructions fully. In the submission area, you will notice that you can click the link to **Preview the Grading** for each step of the assignment. This is the criteria that will be used for peer grading. Please familiarize yourself with the criteria before beginning the assignment.
# 
# An NOAA dataset has been stored in the file `data/C2A2_data/BinnedCsvs_d400/fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89.csv`. The data for this assignment comes from a subset of The National Centers for Environmental Information (NCEI) [Daily Global Historical Climatology Network](https://www1.ncdc.noaa.gov/pub/data/ghcn/daily/readme.txt) (GHCN-Daily). The GHCN-Daily is comprised of daily climate records from thousands of land surface stations across the globe.
# 
# Each row in the assignment datafile corresponds to a single observation.
# 
# The following variables are provided to you:
# 
# * **id** : station identification code
# * **date** : date in YYYY-MM-DD format (e.g. 2012-01-24 = January 24, 2012)
# * **element** : indicator of element type
#     * TMAX : Maximum temperature (tenths of degrees C)
#     * TMIN : Minimum temperature (tenths of degrees C)
# * **value** : data value for element (tenths of degrees C)
# 
# For this assignment, you must:
# 
# 1. Read the documentation and familiarize yourself with the dataset, then write some python code which returns a line graph of the record high and record low temperatures by day of the year over the period 2005-2014. The area between the record high and record low temperatures for each day should be shaded.
# 2. Overlay a scatter of the 2015 data for any points (highs and lows) for which the ten year record (2005-2014) record high or record low was broken in 2015.
# 3. Watch out for leap days (i.e. February 29th), it is reasonable to remove these points from the dataset for the purpose of this visualization.
# 4. Make the visual nice! Leverage principles from the first module in this course when developing your solution. Consider issues such as legends, labels, and chart junk.
# 
# The data you have been given is near **Ann Arbor, Michigan, United States**, and the stations the data comes from are shown on the map below.

# In[12]:

import matplotlib.pyplot as plt
import mplleaflet
import pandas as pd
import numpy as np

def leaflet_plot_stations(binsize, hashid):

    df = pd.read_csv('data/C2A2_data/BinSize_d{}.csv'.format(binsize))

    station_locations_by_hash = df[df['hash'] == hashid]

    lons = station_locations_by_hash['LONGITUDE'].tolist()
    lats = station_locations_by_hash['LATITUDE'].tolist()

    plt.figure(figsize=(8,8))

    plt.scatter(lons, lats, c='r', alpha=0.7, s=200)

    return mplleaflet.display()

leaflet_plot_stations(400,'fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89')


# In[13]:

df = pd.read_csv('data/C2A2_data/BinnedCsvs_d400/fb441e62df2d58994928907a91895ec62c2c42e6cd075c2700843b89.csv')


# In[14]:

df['Date'] = pd.to_datetime(df['Date'])


# In[15]:

df = df[df['Date'].map(lambda data: not ((data.month == 2) and (data.day == 29)))]
    
df_2015 = (df[df['Date'].map(lambda data: data.year == 2015)]
           .set_index('Date')
           .copy(True)
          )

df_remain = (df[df['Date'].map(lambda data: data.year != 2015)]
            .groupby('Date')
            .apply(lambda sdf: pd.Series({'Tmax': sdf['Data_Value'].max(), 'Tmin': sdf['Data_Value'].min()}))
            .sort_index()
            .copy(True)
           )


# In[26]:

fig = plt.figure(figsize = (20, 8))
low_level = plt.plot(df_remain.index, df_remain['Tmin'], label='Daily Maximum')
high_level = plt.plot(df_remain.index, df_remain['Tmax'], label='Daily Minimum')
axis = plt.gca()
shade = axis.fill_between(df_remain.index,
                        df_remain['Tmin'],
                        df_remain['Tmax'],
                        facecolor = 'grey',
                        alpha = 0.2)
scatter = plt.scatter(df_2015.index, df_2015['Data_Value'], label = 'Temperature, 2015',
                     color='lavender', marker='.', s=1.5, alpha=0.2)
legend = plt.legend(loc=3, ncol=4, handlelength=8, scatterpoints=8)
scatter_legend = legend.legendHandles[2]
scatter_legend._sizes = [20]
scatter_legend.set_alpha(1)
plt.title('Temperature from 2005 to 2015 Near Ann Arbor, Michigan, United States',
         size=20)
plt.show()
fig.savefig('p1.jpg')


# In[28]:

df_2015_month = (df[df['Date'].map(lambda d: d.year == 2015)]
               .groupby(df['Date'].map(lambda d: d.timetuple().tm_yday))
               .apply(lambda sdf: pd.Series({'Tmax': sdf['Data_Value'].max(), 'Tmin': sdf['Data_Value'].min()}))
               .sort_index()
               .copy(True)
              )
    
df_remain_month = (df[df['Date'].map(lambda d: d.year != 2015)]
           .groupby(df['Date'].map(lambda d: d.timetuple().tm_yday))
           .apply(lambda sdf: pd.Series({'Tmax': sdf['Data_Value'].max(), 'Tmin': sdf['Data_Value'].min()}))
           .sort_index()
           .copy(True)
          )
df_2015_month = df_2015_month.merge(df_remain_month, left_index=True, right_index=True, suffixes=('_2015', '_rest'))
df_2015_month_low = df_2015_month[df_2015_month['Tmin_2015'] < df_2015_month['Tmin_rest']]['Tmin_2015']
df_2015_month_high = df_2015_month[df_2015_month['Tmax_2015'] > df_2015_month['Tmax_rest']]['Tmax_2015']

fig_month = plt.figure(figsize=(20, 8))
low_plot = plt.plot(df_remain_month.index, df_remain_month['Tmin'], label='One Day Maximum(2004-2014)', lw=2)
high_plot = plt.plot(df_remain_month.index, df_remain_month['Tmax'], label='One Day Minimum(2004-2014)', lw=2)
axis_month = plt.gca()
shade = axis_month.fill_between(df_remain_month.index,
                       df_remain_month['Tmin'],
                       df_remain_month['Tmax'],
                       facecolor='grey',
                       alpha=0.4)
scatter_high = plt.scatter(df_2015_month_high.index, df_2015_month_high, label='Maximum in 2015', marker='+',
                          color='red', s=80, alpha=0.6)
scatter_low = plt.scatter(df_2015_month_low.index, df_2015_month_low, label='Maximum in 2015', marker='*', 
                          color='blue', s=80, alpha=0.6)
legend_month = plt.legend(loc=1, ncol=4, handlelength=8, scatterpoints=8)
scatter_legend_month = legend.legendHandles[2]
scatter_legend_month._sizes = [20]
scatter_legend_month.set_alpha(1)

month_day = [0] + list(np.cumsum(pd.date_range('2019-01-01', periods=12, freq='M').map(lambda d: d.day)))
day_anno_pos = list(map(np.mean, zip(month_day[: -1], month_day[1: ])))
month_label = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
for pos, text in zip(day_anno_pos, month_label):
    axis_month.annotate(s=text, xy =(pos, -350), xycoords='data', size=12,
                verticalalignment='top', horizontalalignment='center' , rotation=0)


temp_anno_pos = list(range(-300, 401, 100))
temp_anno_label = list(map(lambda t: '{}$^{{\circ}}$C'.format(int(t/10)), temp_anno_pos))
for pos, text in zip(temp_anno_pos, temp_anno_label):
    axis_month.annotate(s=text, xy =(-2, pos), xycoords='data', size=12,
                verticalalignment='center', horizontalalignment='right' , rotation=0)

plt.title('Temperature from 2005 to 2015 Near Ann Arbor, Michigan, United States',
         size=20)
plt.tick_params(labelleft='off', labelbottom='off')
plt.show()
fig_month.savefig('p2.jpg')

