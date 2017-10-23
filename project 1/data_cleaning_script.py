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

gold = pd.read_csv('gold_reserves.csv', header=0)
cities = pd.read_csv('country-capitals.csv', header=0)

gold_dropped = gold[['Country Name', 'Country Code', '2016']]
gold_dropped.set_index('Country Code', inplace = True)
gold_dropped_sorted = gold_dropped.sort_values('2016', ascending=False).head(50)
cities_dropped = cities.drop('ContinentName',axis=1)

combined = pd.merge(cities_dropped, gold_dropped_sorted, left_on='CountryName', right_on='Country Name')
combined.sort_values('2016', inplace=True)

missing_countries = []
for index, row in gold_dropped_sorted.iterrows():
    if row['Country Name'] not in combined.values:
        missing_countries.append(row['Country Name'])
# missing countries are ['Hong Kong SAR, China', 'Russian Federation', 'Korea, Rep.']

gold_dropped_sorted.loc[gold_dropped_sorted['Country Name'] == 'Russian Federation', 'Country Name'] = 'Russia'
missing_countries_corrected = ['Hong Kong', 'Russia', 'South Korea']
correction_dict = dict(zip(missing_countries, missing_countries_corrected))
for index, row in gold_dropped_sorted.iterrows():
    if row['Country Name'] in correction_dict.keys():
        gold_dropped_sorted.loc[index, 'Country Name'] = correction_dict[row['Country Name']]
