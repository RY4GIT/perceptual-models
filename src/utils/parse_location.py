from hashlib import new
import pandas as pd
import numpy as np
import os
import folium

df = pd.read_excel('Location.xlsx', sheet_name='WatershedLocations')

strValue = 'N'
replacementStr = '-'

column_name = df.columns
for col in column_name[1:7]:
    """
    # Drop direction char and add sign
    if 'lat' in col:
        directions = ['S', 'N']
        coord = 'lat'
    elif 'lon' in col:
        directions = ['W', 'E']
        coord = 'lon'
    """

    df2 = df[col].copy()
    """
    for d in range(len(directions)):
        if directions[d] == 'S' or directions[d] == 'W':
            idx_negative = df2.str.endswith(directions[d], na=False)
            df2[idx_negative] = df2[idx_negative].str[:-1]
        elif directions[d] == 'N' or directions[d] == 'E':
            idx_positive = df2.str.endswith(directions[d], na=False)
            df2[idx_positive] = df2[idx_positive].str[:-1]
    """
    df_degree = df2.str.split('d', expand=True)
    df_second = df_degree[1].str.split('s', expand=True)
    df_miute = df_second[0].str.split('m', expand=True)
    
    df3 = pd.concat([df_degree[0].str.strip(), df_miute[0].str.strip(), df_miute[1].str.strip()], axis=1, ignore_index=True)
    df3 = df3.replace(r'^\s*$', np.nan, regex=True)
    df3.fillna(value=np.nan, inplace=True)
    df3.fillna(value=0, inplace=True)
    new_value = df3[0].astype(float) + df3[1].astype(float)/60 + df3[2].astype(float)/3600

    if col == 'lat':
        lat = new_value.to_numpy()
    if col == 'lon':
        lon = new_value.to_numpy()
    if col == 'max_lat':
        max_lat = new_value.to_numpy()
    if col == 'min_lat':
        min_lat = new_value.to_numpy()
    if col == 'max_lon':
        max_lon = new_value.to_numpy()
    if col == 'min_lon':
        min_lon = new_value.to_numpy()

avg_lat = (max_lat + min_lat) / 2
avg_lon = (max_lon + min_lon) / 2
lat[lat==0] = avg_lat[lat==0]
lon[lon==0]= avg_lon[lon==0]

list_of_tuples = list(zip(lat, lon))
df_calc_coord = pd.DataFrame(list_of_tuples, columns=['lat','lon'])
df_calc_coord = pd.concat([df.Name, df_calc_coord],axis=1)
df_calc_coord.to_json('./location.json')
df_calc_coord.to_excel('./Location_formatted.xlsx', sheet_name='Formatted_coordinates')
