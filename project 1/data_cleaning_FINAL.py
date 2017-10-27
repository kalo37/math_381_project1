
# coding: utf-8

# In[1]:


# import necessary packages
import numpy as np
import pandas as pd
import math


# In[2]:


d2r = lambda x: x * np.pi / 180 # convert degrees to radians
def getDistance(lat1, lon1, lat2, lon2): 
    """Calculate the distance between two (lat,lon) points using 'Haversine' Formula"""
    r = 6371 # radias of earth in km
    dLat = d2r(lat2 - lat1)
    dLon = d2r(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(d2r(lat1))          * math.cos(d2r(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = r * c # Distance in km
    return d


# In[3]:


# read raw csv files
gold = pd.read_csv('gold_reserves.csv', header=0)
cities = pd.read_csv('country-capitals.csv', header=0)


# In[4]:


gold_dropped = gold[['Country Name', 'Country Code', '2016']] # select only useful columns


# In[5]:


gold_dropped.set_index('Country Code', inplace = True) # set indices using country code


# In[6]:


# select top 50 countries with most gold
gold_dropped_sorted = gold_dropped.sort_values('2016', ascending=False).head(50)


# In[7]:


cities_dropped = cities.drop('ContinentName',axis=1) # drop unnecessary columns


# In[8]:


# merge dataframes
combined = pd.merge(cities_dropped, gold_dropped_sorted, left_on='CountryName', right_on='Country Name') 


# In[9]:


combined.sort_values('2016', inplace=True) # sort by gold amount


# In[10]:


# check which countries need to be fixed due to inconsistent naming
missing_countries = []
for index, row in gold_dropped_sorted.iterrows():
    if row['Country Name'] not in combined.values:
        missing_countries.append(row['Country Name'])


# In[11]:


# fix the country name of Russia
gold_dropped_sorted.loc[gold_dropped_sorted['Country Name'] == 'Russian Federation', 'Country Name'] = 'Russia'


# In[12]:


# create dictionary of country names to be fixed
missing_countries_corrected = ['Hong Kong', 'Russia', 'South Korea']
correction_dict = dict(zip(missing_countries, missing_countries_corrected))


# In[13]:


# fix the country names
for index, row in gold_dropped_sorted.iterrows():
    if row['Country Name'] in correction_dict.keys():
        gold_dropped_sorted.loc[index, 'Country Name'] = correction_dict[row['Country Name']]


# In[14]:


# re-merge the two tables after fixing the values
combined = pd.merge(cities_dropped, gold_dropped_sorted, left_on='CountryName', right_on='Country Name')


# In[15]:


# manually enter the data for Hong Kong
combined.loc[combined['CountryName'] == 'Hong Kong', 'CapitalName'] = 'Hong Kong'
combined.loc[combined['CountryName'] == 'Hong Kong', 'CapitalLatitude'] = 22.3964
combined.loc[combined['CountryName'] == 'Hong Kong', 'CapitalLongitude'] = 114.1095


# In[16]:


# sort dataframe by gold amount
combined.drop(['Country Name'], inplace = True, axis=1)
combined.set_index('CountryCode', inplace=True)
combined.sort_values("2016", ascending=False, inplace=True)


# In[17]:


pop = pd.read_csv('world_cities.csv') # read data that contains population for each city


# In[18]:


# avoid the conflicts with cities that have the same name, make a new datafram that has the correct cities
# using the latitude and logitude of the city
pop_no_duplicates = pd.DataFrame()
tol = 2
for idx, row in combined.iterrows():
    for idx, p in pop.loc[pop['city'] == row['CapitalName']].iterrows():
        if abs(p['lat'] - row['CapitalLatitude']) < tol and abs(p['lng'] - row['CapitalLongitude']) < tol:
            pop_no_duplicates = pop_no_duplicates.append(p, ignore_index=True)


# In[19]:


# merge both dataframes
combined = pd.merge(left=combined, right=pop_no_duplicates, left_on='CapitalName', right_on='city', how='left')


# In[20]:


# select only useful columns
combined = combined[['CountryName', 'CapitalName', 'CapitalLatitude', 'CapitalLongitude', '2016', 'pop']]


# In[21]:


# some populations did not get merged due to different names for the same city
# create a dictionary with the populations for those cities and add to the dataframe
fix_pop = {'Washington DC': 2445216.5, 'Copenhagen': 1085000, 'Kuwait City': 1061532}
for idx, row in combined.iterrows():
    if row['CapitalName'] in fix_pop.keys():
        combined.loc[idx, 'pop'] = fix_pop[row['CapitalName']]


# In[22]:


# output dataframe to csv
combined.to_csv('clean_capitals_gold_pop.csv')


# In[23]:


# create headers for the csv file
country_names = list(combined.loc[:, 'CountryName'])
country_names = [' '] + country_names


# In[24]:


# get lists of longitudes and latitudes
latitudes = list(combined.loc[:, 'CapitalLatitude'])
longitudes = list(combined.loc[:, 'CapitalLongitude'])


# In[25]:


adjacency_matrix = [country_names] # initialize adjacency matrix, with header


# In[26]:


# zip latitudes and logitudes into (lat, long)
lat_lon_pairs = list(zip(latitudes, longitudes))


# In[27]:


# calculate distances for each coordinates-pair, and add to the adjacency matrix
for index, pair1 in enumerate(lat_lon_pairs):
    temp = [country_names[index + 1]]
    for pair2 in lat_lon_pairs:
        temp.append(getDistance(pair1[0], pair1[1], pair2[0], pair2[1]))
    adjacency_matrix.append(temp)


# In[28]:


# write matrix to file
with open('named_distances.csv', 'w') as f:
    for elt in adjacency_matrix:
        f.write(', '.join(str(v) for v in elt))
        f.write('\n')

