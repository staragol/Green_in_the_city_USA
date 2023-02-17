"""
Functions to simplify the cleaning of Canadian census data.
"""
#%% Preamble
# load packages
import pandas as pd
import censusclean.censusclean as cc
#%% Load data
# Load census data
def clean_census_ca(filename, col_var, col_val, geo_level_tract = 'Census tract'):
    """
    Clean census data of Canada.

    Read the file and set to a useful format for further preprocessing for the
    purpose of the 'green in the city' project. This function might have to be adapted for
    for files after 2021.

    Parameters
    ----------
    filename : string
        Name and path of the census file.
    col_var : string
        Name of the column containing the variable names.
    col_val : string
        Name of the column containing the values.
    geo_level_tract : string or double, optional.
        Value which indicates census tract. The default is 'Census tract'.

    Returns
    -------
    data_estimates : DataFrame
        The cleaned data frame.

    """
    # Read file
    data = pd.read_csv(filename,
                       encoding=cc.get_encoding(filename), sep = ',',
                       na_values=['...','..','x','NaN'],
                       low_memory=False, encoding_errors= 'ignore')
    # Clean data
    # Set ALT_GEO_CODE to string type with format (length: 10, decimals: 2)
    if data.ALT_GEO_CODE.astype(str).str.contains('\.').any() == False:
        # If no point is found in the entire dataset, they have to be intoduced
        # in front of the last 2 numbers of the ID.
        data.ALT_GEO_CODE = data.ALT_GEO_CODE/100
    data.ALT_GEO_CODE = data.ALT_GEO_CODE.apply(lambda a: '%010.2f' % a)
    # Select columns containing geographical information
    data_part1 = data.loc[:,data.columns.str.contains('GEO')]
    # Select columns containing the variables and measurements
    data_part2 = data.loc[:, [col_var, col_val]]
    # Merge columns to one data frame
    data_selected = pd.concat([data_part1,data_part2], axis=1)
    # Only keep census tract data
    data_output = data_selected.loc[data_selected['GEO_LEVEL']==geo_level_tract]
    # Rename the columns
    data_output = data_output.rename({col_var: 'variable',
                                      col_val: 'value',
                                      'ALT_GEO_CODE': 'tract'},
                                     axis = 1)
    # Strip spaces from variable names
    data_output['variable'] = data_output['variable'].str.strip()
    data_output['value'] = pd.to_numeric(data_output['value'], errors = 'coerce')
    # Set column names to lower
    data_output.columns = data_output.columns.str.lower()
    return data_output

def reshape_census_CA(data, var_oi):
    """
    Select variables of interest and reschape data.

    Select the variables of interest from the census data of the tracts in Canada.
    The dataframe has to have following columns: 'tract', 'variable', 'value'.
    If a variable name is used multiple times for the same tract, only the first
    is retained.

    Parameters
    ----------
    data : DataFrame
        Data frame with census data of Canada.
    var_oi : list
        Variables of interest.

    Returns
    -------
    data_wide : DataFrame
        Data frame with the census data in a wide format.

    """
    # Select variables of interest
    data_filtered = data.loc[data['variable'].isin(var_oi)]
    # Check for duplicates
    duplicates = (data_filtered
                  .loc[:,['tract', 'variable']]
                  .duplicated(keep = 'first'))
    # Remove duplicates
    data_no_duplicates = (data_filtered
                          .loc[:,['tract', 'variable', 'value']]
                          .loc[duplicates == False]
                          )
    # Pivot data frame wider
    data_wide = data_no_duplicates.pivot(index = 'tract',
                columns='variable',
                values= 'value').reset_index()
    return data_wide

# %%
