# Import necessary packages
import numpy as np
import pandas as pd
import math

d2r = lambda x: x * np.pi / 180 # convert degrees to radians

def getDistance(lat1, lon1, lat2, lon2):
    """Calculate the distance between two (lat,lon) points using 'Haversine' Formula"""
    r = 6371 # radias of earth in km
    dLat = d2r(lat2 - lat1)
    dLon = d2r(lon2 - lon1)
    a = math.sin(dLat/2) * math.sin(dLat/2) + math.cos(d2r(lat1)) \
         * math.cos(d2r(lat2)) * math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = r * c # Distance in km
    return d

# Read databases
gold = pd.read_csv('gold_reserves.csv', header=0)
cities = pd.read_csv('country-capitals.csv', header=0)

# Drop unnecessary columns and sort rows by Gold/Reserve amount, decending, and select top 50 countries
gold_dropped = gold[['Country Name', 'Country Code', '2016']]
gold_dropped.set_index('Country Code', inplace = True)
gold_dropped_sorted = gold_dropped.sort_values('2016', ascending=False).head(50)
cities_dropped = cities.drop('ContinentName',axis=1)

# Merging the two datasets on Country Names
combined = pd.merge(cities_dropped, gold_dropped_sorted, left_on='CountryName', right_on='Country Name')
combined.sort_values('2016', inplace=True)

# Inspect if there is any missing rows because of different names for the same country
missing_countries = []
for index, row in gold_dropped_sorted.iterrows():
    if row['Country Name'] not in combined.values:
        missing_countries.append(row['Country Name'])
# missing countries are ['Hong Kong SAR, China', 'Russian Federation', 'Korea, Rep.']

# Fix the countries name such that they are consistent between the two datasets
gold_dropped_sorted.loc[gold_dropped_sorted['Country Name'] == 'Russian Federation', 'Country Name'] = 'Russia'
missing_countries_corrected = ['Hong Kong', 'Russia', 'South Korea']
correction_dict = dict(zip(missing_countries, missing_countries_corrected))
for index, row in gold_dropped_sorted.iterrows():
    if row['Country Name'] in correction_dict.keys():
        gold_dropped_sorted.loc[index, 'Country Name'] = correction_dict[row['Country Name']]

# re-merge the two tables after fixing the values
combined = pd.merge(cities_dropped, gold_dropped_sorted, left_on='CountryName', right_on='Country Name')

# manually enter the data for Hong Kong, since it had some missing values
combined.loc[combined['CountryName'] == 'Hong Kong', 'CapitalName'] = 'Hong Kong'
combined.loc[combined['CountryName'] == 'Hong Kong', 'CapitalLatitude'] = 22.3964
combined.loc[combined['CountryName'] == 'Hong Kong', 'CapitalLongitude'] = 114.1095
combined.iloc[49]

# drop necessary columns and sort rows by their reserves values
combined.drop(['Country Name'], inplace = True, axis=1)
combined.set_index('CountryCode', inplace=True)
combined.sort_values("2016", ascending=False, inplace=True)
combined.head()

# get a list of the countries name in the order that is the same as the merged dataframe
country_names = list(combined.loc[:, 'CountryName'])
# add an empty cell in the beginning of the list, used for the formatting of the adjacency matrix
country_names = [' '] + country_names

# get the latitudes and logitudes of all the capitals and zip them into the format (lat, long)
latitudes = list(combined.loc[:, 'CapitalLatitude'])
longitudes = list(combined.loc[:, 'CapitalLongitude'])
lat_lon_pairs = list(zip(latitudes, longitudes))

# initialize adjacency matrix, with header
adjacency_matrix = [country_names]

# calculate distances for each coordinates-pair, and add to the adjacency matrix
for index, pair1 in enumerate(lat_lon_pairs):
    temp = [country_names[index + 1]]
    for pair2 in lat_lon_pairs:
        temp.append(getDistance(pair1[0], pair1[1], pair2[0], pair2[1]))
    adjacency_matrix.append(temp)

# write matrix to file
with open('named_distances.csv', 'w') as f:
    for elt in adjacency_matrix:
        f.write(', '.join(str(v) for v in elt))
        f.write('\n')
