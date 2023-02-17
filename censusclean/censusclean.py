# -*- coding: utf-8 -*-
"""
This module was created to simplify the data cleaning of census data from
cities in Canada and the US. These functions have only been tested on the
demo data, but can be applied to other data as well, provided due care is
taken.

Created on Fri Sep  2 15:26:57 2022

@author: Sander Taragola
"""
#%% Preamble
import pandas as pd
import numpy as np
import geopandas as gpd
#%% Functions
def select_by_prefix(data, prefix, id_cols = None, keep_index = False):
    """
    Select columns based on the prefix of the column names and deletes the prefix afterwards.
    
    This helps to improve the clarity of dataframe.
    
    Parameters
    ----------
    data : DataFrame
        A dataframe of which a subset is needed.
    prefix: string
        The prefix on which the columns are filtered.
    id_cols: list or string, optional
        The columns to which the function is not applied. The default is None.
    keep_index: boolean
        Does the dataframe have a meaningful index that should be preserved.

    Returns
    -------
    A data frame containing only the columns whose names start with the
    specified prefix and where the prefix is removed from the column names.

    """
    if id_cols is not None:
        data = data.set_index(id_cols, append = keep_index)
    subset_col = data.columns.str.startswith(prefix)
    data_subset = data.loc[:,subset_col]
    data_subset.columns = data_subset.columns.str.slice(start = len(prefix))
    data_subset = data_subset.reset_index()
    return data_subset

def split_header(data, sep = ' ', id_cols = None):
    """
    Split the header of a data frame where the header is composed of multiple parts.

    Parameters
    ----------
    data : DataFrame
        A dataframe with a header containing multiple variables.
    sep : string, optional
        String indicating the splitting of variables in the header. The default is ' '.
    id_cols: list or string, optional
        The columns to which the function is not applied. The default is None.

    Returns
    -------
    A data frame whose header is split into 2 variables.

    """
    data_long = data.melt(id_vars = id_cols)
    split_colnames = pd.DataFrame(data_long["variable"]
                                  .str.split(sep, expand = True)
                                  ).add_prefix("variable")
    data_long = pd.concat([data_long, split_colnames], axis = 1
                      ).drop('variable', axis = 1)
    variable_columns = list(data_long.columns[data_long.columns
                                              .str.startswith('variable')])
    data_long = data_long.set_index(id_cols, append = False)
    data_wide = (data_long
                 .pivot(columns = variable_columns, values = 'value')
                 .reset_index())
    return data_wide

def extract_part(data, col_id, new_id = 'extracted', separators = ' ', locations = 0):
    """
    Extract a specific part of a string into a dataframe column based on separators.

    The function extracts part of the string by splitting it at the separator
    and the part given by location is retained. When multiple separators are
    given, this operation is iterated over this list. This requires locations
    to be as long as separators.

    Parameters
    ----------
    data : DataFrame
        The dataframe with a column of strings.
    col_id : string
        Name of the column containing the full strings.
    new_id : string, optional
        Name of the column that will be added to data with the extracted
        information. The default is 'extracted'.
    separators : list or string, optional
        characters on which the strings have to be split. The default is ' '.
    locations : numeric, optional
        Part of the splitted string that has to be retained for each split
        operation. The default is 0.

    Returns
    -------
    data : DataFrame
        Input data frame with an extra column containing the extracted information.

    """
    col_extract = data[col_id]
    for i in np.arange(len(separators)):
        col_extract = (col_extract.str.split(separators[i], expand = True)
                       ).iloc[:,locations[i]]
    col_extract = col_extract.str.strip()
    data[new_id] = col_extract
    return data

def set_format_colnames(data, sep = '_',
                        manually_name = None, manually_location = None):
    """
    Set format of header to be uniform with other DataFrames.

    Set all names in the same format, this is important when merging different
    datasets In this function, the following format is chosen:
    all lower case and words separated by space and no spaces at the beginning
    or the end.

    Parameters
    ----------
    data : DataFrame
        Data frame with a messy header.
    sep : string, optional
        The symbol used to separate words in the header. The default is '_'.
    manually_name : list, optional
        If some column names have to be changed to a specific name, the names
        can be given here. Always enter a list, not just a string. The default
        is None.
    manually_location : list, optional
        The location of the columns whose name has to be changed manually.
        This list has to be equally long as manually_name. Always enter a list,
        not just a string. The default is None.

    Returns
    -------
    data : DataFrame
        Data frame with headers in wanted format.

    """
    col_names = list(data.columns)
    col_names = [col_name.replace(sep, ' ').strip().lower() for col_name in col_names]
    if manually_name is not None:
        try:
            for i in np.arange(len(manually_name)):
                col_names[manually_location[i]] = manually_name[i]
        except:
            print('Error:',
                  'Cannot change column name, please check the input variables.')
    data.columns = col_names
    return data

def get_encoding(filename):
    """
    Get file encoding.
    """
    with open(filename) as f:
        return f.encoding

def join_by_location(layer_1, layer_2, col_id,
                            lsuffix = 'x', rsuffix = 'y'):
    """
    Add columns from layer_2 to layer_1 based on overlaps.
    
    Spatially join both layers one-to-one. The feature of layer_2 of which 
    the attribute is used is the feature that contains the centroid of 
    layer_1's feature.

    Parameters
    ----------
    layer_1 : GeoDataFrame
        A GeoDataFrame with polygons as geometries. This is the base layer.
    layer_2 : GeoDataFrame
        A GeoDataFrame with polygons as geometries. This is the layer of 
        which the attributes are sampled.
    col_id : string
        The column names of the attributes of layer_2.
    lsuffix : string, optional
        suffix added to the column names of layer_1, which are also 
        present in layer_2. The default is 'x'.
    rsuffix : string, optional
        suffix added to the column names of layer_2, which are also 
        present in layer_1. The default is 'y'.

    Returns
    -------
    output_layer : GeoDataFrame
        Joined GeoDataFrame.

    """
    layer_2 = layer_2.to_crs(layer_1.crs)
    if isinstance(col_id, list)==False:
        col_id = [col_id]
    layer_2 = layer_2.loc[:,['geometry']+col_id]
    # Use centroids to join layers one-to-one
    samplers = layer_1.copy()
    samplers.geometry = layer_1.geometry.centroid
    samplers = gpd.sjoin(samplers, layer_2, 
                     how = 'left', lsuffix=lsuffix, rsuffix=rsuffix)
    samplers.geometry = layer_1.geometry
    output_layer = samplers.copy()
    return output_layer