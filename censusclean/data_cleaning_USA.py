"""
Functions to simplify the cleaning of American census data.
"""
#%% Preamble
# load packages
import pandas as pd
import numpy as np
import geopandas as gpd
import censusclean.censusclean as cc
#%% Load data
# Load census data
def clean_census_us(filename, prefix = "Estimate!!"):
    """
    Clean census data from the United States of America.
    
    Read the file and set to a useful format for selecting variables and merging
    with other census data for the purpose of the 'green in the city' project.

    Parameters
    ----------
    filename : string
        Name and path of the census file.
    prefix : string
        Prefix that charachterises the columns needed, but has no further use 
        after a subset of only these columns is made. The columns with geo-
        graphical information will be preserved as well.

    Returns
    -------
    data_estimates : DataFrame
        The cleaned data frame.

    """
    data = pd.read_csv(filename,
                       header=1, na_values=('-','(X)'), decimal='.',
                       low_memory=False)
    # Clean the dataframe
    # Filter on tract data only
    data = data.loc[data['Geographic Area Name'].str.contains('Tract'),:]
    # Select the columns with usefull data based on the prefix (Optional)
    id_cols = ['Geography',
               'Geographic Area Name']
    data_estimates = cc.select_by_prefix(data, prefix, id_cols)
    # Extract census tract identifiers
    col_id = 'Geographic Area Name'
    new_id = 'Census Tract'
    separators = [', ', ' ']
    locations = [0, 2]
    data_estimates = cc.extract_part(data_estimates, 
                                     col_id, new_id, 
                                     separators, locations)
    col_id = 'Geographic Area Name'
    new_id = 'County'
    separators = [', ', ' ']
    locations = [1, 0]
    data_estimates = cc.extract_part(data_estimates, 
                                     col_id, new_id, 
                                     separators, locations)
    # Clean column names
    data_estimates = cc.set_format_colnames(data = data_estimates, sep='!!')
    return data_estimates



