"""
Preparation of the census data of Canada.

This script extracts the needed data from the census file of a city in Canada. 
The data is cleaned and merged with a shapefile, containing the geospatial data
linked to the census data. The censusfiles have to be downloaded from 
https://www150.statcan.gc.ca/n1/en/type/data?MM=1 and the shapefile has to contain 
a column with the same identifiers in order to be able to merge both datasets.
"""

#%% Preamble
# Change this path to the main project folder
path = "C:/Users/sande/OneDrive - UGent/Green in the city/Green_in_the_city"
import sys
import os
os.chdir(path)
sys.path.append(path)
import pandas as pd
import numpy as np
import censusclean.censusclean as cc
from censusclean.data_cleaning_CA import clean_census_ca
from censusclean.data_cleaning_CA import reshape_census_CA
import geopandas as gpd
from tkinter import Tk     # from tkinter import Tk for Python 3.x
from tkinter.filedialog import askopenfilename
#%% Load census data
data = clean_census_ca('Data preparation/Raw data/Canada/98-401-X2021007_eng_CSV/'
                       '98-401-X2021007_English_CSV_data.csv',
                       col_var = 'CHARACTERISTIC_NAME',
                       col_val= 'C1_COUNT_TOTAL')
#%% Select variables of interest
# variables of interest
var_oi = ['Population, 2021', 'Population density per square kilometre',
       'Land area in square kilometres',
       '0 to 4 years', '5 to 9 years', '10 to 14 years',
       '15 to 19 years', '20 to 24 years',
       '25 to 29 years', '30 to 34 years', '35 to 39 years',
       '40 to 44 years', '45 to 49 years', '50 to 54 years',
       '55 to 59 years', '60 to 64 years','65 to 69 years',
       '70 to 74 years', '75 to 79 years','80 to 84 years',
       '85 to 89 years','90 to 94 years', '95 to 99 years', '100 years and over',
       'Total - Occupied private dwellings by structural type of dwelling - 100% data',
       'Single-detached house', 'Semi-detached house', 'Row house',
       'Apartment or flat in a duplex',
       'Apartment in a building that has fewer than five storeys',
       'Apartment in a building that has five or more storeys',
       'Total - Private households by household size - 100% data',
       '1 person', '2 persons', '3 persons', '4 persons',
       '5 or more persons', 'Median total income in 2020 among recipients ($)',
       'Total - Total income groups in 2020 for the population aged 15 years and'
       'over in private households - 100% data','Without total income']
# Pivot wider to selected variables
data_wide = reshape_census_CA(data, var_oi)
del data
#%% Education and unemployment
education = clean_census_ca('Data preparation/Raw data/Canada/98-401-X2016043_'
                            'eng_CSV/98-401-X2016043_English_CSV_data.csv',
                            col_var= 'DIM: Profile of Census Tracts (2247)',
                            col_val= 'Dim: Sex (3): Member ID: [1]: Total - Sex',
                            geo_level_tract=2)

var_oi = ['Total - Highest certificate, diploma or degree for the population '
          'aged 15 years and over in private households - 25% sample data',
          'No certificate, diploma or degree',
          'Secondary (high) school diploma or equivalency certificate',
          'Postsecondary certificate, diploma or degree', 'Unemployment rate',
          'Median monthly shelter costs for owned dwellings ($)','Median value '
          'of dwellings ($)']
#%%
edu_wide = reshape_census_CA(education, var_oi)
del education
#%% Load geographical data
census_tracts_2021 = gpd.read_file('Data preparation/Raw data/Canada/'
                                   'lct_000b21a_e/lct_000b21a_e.shp')
census_tracts_2016 = gpd.read_file('Data preparation/Raw data/Canada/'
                                   'lct_000b16a_e/lct_000b16a_e.shp')
census_tracts = cc.join_by_location(layer_1=census_tracts_2021,
                                    layer_2=census_tracts_2016,
                                    col_id='CTUID',
                                    lsuffix='2021', rsuffix='2016')
#%% Merge GeoDataFrame with Dataframes
census_data = census_tracts.merge(data_wide, 
                                  how = 'left', 
                                  left_on= 'CTUID_2021',
                                  right_on= 'tract')
census_data = census_data.merge(edu_wide, 
                                how = 'left', 
                                left_on= 'CTUID_2016',
                                right_on= 'tract')
#%% Mutate variables to match information of other cities
census_data['under 10'] = (census_data[['0 to 4 years',
                                       '5 to 9 years'
                                       ]].sum(axis = 1)/
                           census_data['Population, 2021'])*100
census_data['under 15'] = (census_data[['0 to 4 years',
                                       '5 to 9 years',
                                       '10 to 14 years'
                                       ]].sum(axis = 1)/
                           census_data['Population, 2021'])*100
census_data['over 65'] = (census_data[['65 to 69 years', '70 to 74 years', 
                                       '75 to 79 years','80 to 84 years', 
                                       '85 to 89 years', '90 to 94 years', 
                                       '95 to 99 years', '100 years and over'
                                       ]].sum(axis = 1)/
                           census_data['Population, 2021'])*100
census_data['over 70'] = (census_data[[ '70 to 74 years', 
                                       '75 to 79 years','80 to 84 years', 
                                       '85 to 89 years', '90 to 94 years', 
                                       '95 to 99 years', '100 years and over'
                                       ]].sum(axis = 1)/
                           census_data['Population, 2021'])*100
census_data['over 80'] = (census_data[[ '80 to 84 years', 
                                       '85 to 89 years', '90 to 94 years', 
                                       '95 to 99 years', '100 years and over'
                                       ]].sum(axis = 1)/
                           census_data['Population, 2021'])*100
census_data['alone'] = (census_data[['1 person']]/
                           census_data['Population, 2021'])*100
census_data['over 80'] = (census_data[[ '80 to 84 years', 
                                       '85 to 89 years', '90 to 94 years', 
                                       '95 to 99 years', '100 years and over'
                                       ]].sum(axis = 1)/
                           census_data['Population, 2021'])*100
census_data['no diploma'] = (census_data['No certificate, diploma or degree']/
                             census_data['Total - Highest certificate, diploma'
                                         ' or degree for the population aged 15'
                                         ' years and over in private households'
                                         ' - 25% sample data'])*100
census_data['high school'] = (census_data['Secondary (high) school diploma or '
                                          'equivalency certificate']/
                             census_data['Total - Highest certificate, diploma'
                                         ' or degree for the population aged 15'
                                         ' years and over in private households'
                                         ' - 25% sample data'])*100
census_data['higher diploma'] = (census_data['Postsecondary certificate, diploma'
                                             ' or degree']/
                             census_data['Total - Highest certificate, diploma'
                                         ' or degree for the population aged 15'
                                         ' years and over in private households'
                                         ' - 25% sample data'])*100
census_data['apartments'] = (census_data.loc[:,census_data.columns
                                             .str.contains('partment')]
                                         .sum(axis=1)/
                             census_data['Total - Occupied private dwellings by'
                                         ' structural type of dwelling - 100% '
                                         'data'])*100
census_data['attached'] = (census_data['Row house']/
                             census_data['Total - Occupied private dwellings by'
                                         ' structural type of dwelling - 100% '
                                         'data'])*100
census_data['detached'] = ((census_data['Semi-detached house']+
                            census_data['Single-detached house'])/
                             census_data['Total - Occupied private dwellings by'
                                         ' structural type of dwelling - 100% '
                                         'data'])*100

var_oi = ['tract_x', 'LANDAREA', 'Population, 2021', 'Population density per '
          'square kilometre','Median total income in 2020 among recipients ($)',
          'Unemployment rate', '0 to 4 years', 'under 10', 'under 15', 'over 65',
          'over 70', 'over 80', 'alone', 'no diploma', 'high school', 'higher'
          ' diploma', 'Median value of dwellings ($)',  'apartments','attached',
          'detached','geometry']
census_data = census_data[var_oi]
census_data.columns = ['tract', 'area', 'tot_pop', 'pop_dens',
          'med_inc','unempl','under_5_y','under_10_y','under_15_y','over_65_y',
          'over_70_y','over_80_y','alone','no_dipl','high_sch','degree',
          'house_val', 'apartments','attached','detached', 'geometry']
# %% Export to shapefile
census_data.to_file('Data preparation/Raw data/Canada/Census_Canada/Census_'
                    'tracts_Canada_new.shp')
# %%
