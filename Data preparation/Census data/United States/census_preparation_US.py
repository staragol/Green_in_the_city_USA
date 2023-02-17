"""
Data preparation of census data US.

This script extracts the needed data from the census file of a city in the
United States of America. The data is cleaned and merged with a shapefile,
containing the geospatial data linked to the census data. The censusfiles
have to be downloaded from https://data.census.gov/cedsci/ and the shape-
file has to contain a column with the same identifiers in order to be able
to merge both datasets.
"""
#%% Preamble: load packages and add path to the censusclean package location.
# Change this path to the main project folder
path = "C:/Users/sande/OneDrive - UGent/Green in the city/Green_in_the_city"
import sys
import os
os.chdir(path)
sys.path.append(path)
# import packages
import pandas as pd
import numpy as np
import geopandas as gpd
# Import function to set raw census data to a template format
from censusclean.data_cleaning_USA import clean_census_us
import censusclean.censusclean as cc
#%% Demographic distribution
# Clean DataFrame
data_age = clean_census_us(
    'Data preparation/Raw data/United States/Social_data_Atlanta/Age_and_sex/'
    'ACSST5Y2020.S0101-Data.csv',
    'Estimate!!Total!!'
    )
# Select wanted variables from cleaned data frame
selected_col = np.array(pd.Series(data_age.columns
                                  ).str.startswith('total population age'))
selected_col[[2,-2,-1]] = True
data_age = data_age.loc[:,selected_col]
#%% Unemployment
# Clean DataFrame
data_unemployment = clean_census_us(
    'Data preparation/Raw data/United States/Social_data_Atlanta/Employment/'
    'ACSST5Y2020.S2301-Data.csv',
    'Estimate!!')
# Select wanted variables from cleaned data frame
selected_col = np.array(pd.Series(data_unemployment.columns
                                   ).str.startswith('unemployment rate '
                                                    'population 20'))
selected_col[[-2,-1]] = True
data_unemployment = data_unemployment.loc[:,selected_col]
data_unemployment = data_unemployment.iloc[:,[0,-2,-1]]
# Merge with previous dataframe
data_census = data_age.merge(data_unemployment,
                             how = 'outer', on= ['census tract','county'])
#%% Income
# Clean DataFrame
data_income = clean_census_us(
    'Data preparation/Raw data/United States/Social_data_Atlanta/Income/'
    'ACSST5Y2020.S1901-Data.csv',
    'Estimate!!Households!!')
# Select wanted variables from cleaned data frame
selected_col = np.array(pd.Series(data_income.columns
                                   ).str.startswith('median income'))
selected_col[-2:] = True
data_income = data_income.loc[:,selected_col]
# Merge with previous dataframes
data_census = data_census.merge(data_income, how = 'outer', 
                                on= ['census tract','county'])
#%% Education
data_education = clean_census_us(
    'Data preparation/Raw data/United States/Social_data_Atlanta/Education/'
    'ACSST5Y2020.S1501-Data.csv',
    'Estimate!!Total!!AGE BY EDUCATIONAL ATTAINMENT!!Population')
# Select wanted variables from cleaned data frame
selected_col = np.array(pd.Series(data_education.columns
                                   ).str.contains('25 years and over'))
selected_col[np.array(pd.Series(data_education.columns
                                   ).str.contains('or higher'))] = False
selected_col[-2:] = True
data_education = data_education.loc[:,selected_col]
# Melt dataframe to easily adapt column names and summarise data
data_edu_long = data_education.melt(id_vars = ['census tract',
                                               'county',
                                               '25 years and over'])
# Change names
data_edu_long.variable = data_edu_long.variable.str.removeprefix("25 years and over ")
data_edu_long.variable[data_edu_long.variable.str.contains('9')] = "no diploma"
data_edu_long.variable[data_edu_long.variable.str.contains(
    'high|some col')] = "High school"
data_edu_long.variable[data_edu_long.variable.str.contains(
    'degree')] = "degree"
# Summarise by name
data_edu_long = data_edu_long.groupby(by = ['census tract', 'county',
                                            'variable']).sum().reset_index()
data_edu_long.value = data_edu_long.value/data_edu_long['25 years and over']
# Pivot data frame wider
data_education = data_edu_long.pivot(columns = 'variable', 
                                     values = 'value',
                                     index = ['census tract', 'county'])
# Normalize data to correct for estimation errors
data_education = data_education.div(data_education.sum(axis = 1), axis = 0)
data_education =data_education.reset_index()
# Merge with previous dataframes
data_census = data_census.merge(data_education, how = 'outer',
                                on= ['census tract','county'])
#%% Physical housing charachteristics
# Clean DataFrame
data_houses = clean_census_us(
    'Data preparation/Raw data/United States/Social_data_Atlanta/PhysicalHousing/'
    'ACSST5Y2020.S2504-Data.csv',
    'Estimate!!')
# Select wanted variables from cleaned data frame
data_houses = cc.select_by_prefix(data_houses,
                                  "percent occupied housing units occupied "
                                  "housing units",
                                  id_cols= ['census tract', 'county'])
data_houses = data_houses.iloc[:,np.array([0,1] + list(np.arange(3,17)))]
# Rename variables
houses_long = pd.melt(data_houses, id_vars=['census tract','county'])
houses_long.variable[houses_long.variable.str.contains('detached')] = "detached"
houses_long.variable[houses_long.variable.str.contains('attached')] = "attached"
houses_long.variable[houses_long.variable.str.contains('apartment')] = "apartments"
houses_long.variable[houses_long.variable.str.contains('other')] = "other type of housing"
houses_long = houses_long.groupby(by = ['census tract', 'variable',
                                        'county']).sum().reset_index()
data_houses = houses_long.pivot(columns = 'variable', 
                                     values = 'value',
                                     index = ['census tract',
                                              'county']).reset_index()
# Merge with previous dataframes
data_census = data_census.merge(data_houses, how = 'outer', 
                                on = ['census tract', 'county'])
#%% Households
# Clean DataFrame
data_households = clean_census_us(
    'Data preparation/Raw data/United States/Social_data_Atlanta/Households/'
    'ACSST5Y2020.S1101-Data.csv',
    'Estimate!!')
# Select poeple living alone
data_households['living alone'] = np.sum(data_households.iloc[:,[38,56]],
                                     axis = 1).div(data_households.iloc[:,2])*100
# Select wanted variables from cleaned data frame
data_households = data_households.iloc[:,-3:]
# Merge with previous dataframes
data_census = data_census.merge(data_households, how = 'outer', 
                                on = ['census tract', 'county'])

#%% Owner renter
# Clean DataFrame
data_renter = clean_census_us(
    'Data preparation/Raw data/United States/Social_data_Atlanta/PhysicalHousing/'
    'ACSST5Y2020.S2504-Data.csv',
    'Estimate!!')
houses = data_renter.iloc[:,2]
# Select wanted variables from cleaned data frame
selected_col = np.array(pd.Series(data_renter.columns)
                        .str.startswith('renter-occupied'))
selected_col[-2:] = True
data_renter = data_renter.loc[:,selected_col].iloc[:,[0,-1,-2]]
data_renter.iloc[:,0] = data_renter.iloc[:,0].div(houses)*100
data_renter.rename({"renter-occupied":
                    "renter-occupied housing units occupied housing units"})
# Merge with previous dataframes
data_census = data_census.merge(data_renter, how = 'outer', 
                                on = ['census tract', 'county'])
data_census = cc.set_format_colnames(data_census)
#%% Geographic information
tracts_Atlanta = gpd.read_file('Data preparation/Raw data/United States/'
                               'census_tracts_Georgia/tl_2021_13_tract.shp'
                               )
counties_Atlanta = gpd.read_file('Data preparation/Raw data/United States/'
                                 'counties_Georgia/Counties_Georgia.shp')  
census_Atlanta = cc.join_by_location(tracts_Atlanta, counties_Atlanta, col_id = 'NAME10'
                                    ).rename(columns = {'NAME10':'county'})
census_Atlanta = cc.extract_part(data= census_Atlanta, 
                                 col_id='NAMELSAD', new_id= 'census tract', 
                                 separators = [' '], locations=[2])
census_Atlanta['Area'] = census_Atlanta.to_crs('EPSG:2163').area/1000000 #km²
# Select variables
census_Atlanta = census_Atlanta[['census tract','county', 'Area', 'geometry']]
census_Atlanta = census_Atlanta.merge(data_census, how = 'left', 
                                      on= ['census tract', 'county'])
census_Atlanta.columns = list(census_Atlanta.columns.str.lower())
census_Atlanta['pop_dens'] = (census_Atlanta['total population']
                              /census_Atlanta['area'])
census_Atlanta = census_Atlanta.iloc[(census_Atlanta
                  .iloc[:,4:]
                  .dropna(how='all')
                  .index)]
#%% select and mutate variables to match format wanted by the project
census_Atlanta['under_10'] = census_Atlanta[['total population age under 5 years',
                                          'total population age 5 to 9 years'
                                          ]].sum(axis = 1)
census_Atlanta['under_15'] = census_Atlanta[['total population age under 5 years',
                                          'total population age 5 to 9 years',
                                          'total population age 10 to 14 years'
                                          ]].sum(axis = 1)
census_Atlanta['over_65'] = census_Atlanta[['total population age 65 to 69 years',
                                         'total population age 70 to 74 years',
                                         'total population age 75 to 79 years',
                                         'total population age 80 to 84 years',
                                         'total population age 85 years and over'
                                          ]].sum(axis = 1)
census_Atlanta['over_70'] = census_Atlanta[['total population age 70 to 74 years',
                                         'total population age 75 to 79 years',
                                         'total population age 80 to 84 years',
                                         'total population age 85 years and over'
                                          ]].sum(axis = 1)
census_Atlanta['over_80'] = census_Atlanta[['total population age 80 to 84 years',
                                         'total population age 85 years and over'
                                          ]].sum(axis = 1)
census_Atlanta['pre_1960'] = census_Atlanta[['year structure built 1939 or earlier',
                                          'year structure built 1940 to 1959'
                                          ]].sum(axis = 1)
census_Atlanta['pre_1980'] = census_Atlanta[['year structure built 1939 or earlier',
                                          'year structure built 1940 to 1959',
                                          'year structure built 1960 to 1979',
                                          ]].sum(axis = 1)
var_oi = ['census tract', 'county', 'area', 'total population', 'pop_dens',
          'median income (dollars)','unemployment rate population 20 to 64 years',
          'total population age under 5 years','under_10','under_15','over_65',
          'over_70','over_80','living alone','no diploma','high school','degree',
          'renter-occupied housing units occupied housing units', 'pre_1960',
          'pre_1980', 'year structure built 2014 or later', 'apartments',
          'attached','detached', 'geometry']
census_Atlanta = census_Atlanta[var_oi]
census_Atlanta.columns = ['tract', 'county', 'area', 'tot_pop', 'pop_dens',
          'med_inc','unempl','under_5_y','under_10_y','under_15_y','over_65_y',
          'over_70_y','over_80_y','alone','no_dipl','high_sch','degree',
          'renter', 'pre_1960','pre_1980', 'after_2014', 'apartments',
          'attached','detached', 'geometry']
#%% Export shp-file
census_Atlanta.plot()
census_Atlanta.to_file('Data preparation/Raw data/United States/'
                        'census_Georgia/prep_census_georgia.shp')
