
#######################################################
## Script to join all Excel files and build a database 
#######################################################

import os
import numpy as np
import pandas as pd
import configparser
from sqlalchemy import create_engine
from sqlalchemy import text

###################################
## 0. Read data
###################################
os.chdir(r'G:\Shared drives\Perceptual model review\ForRyoko\perceptual-model-arcgis\dev\scripts')

df_loc = pd.read_excel('../data/Location_formatted.xlsx') # The lat/lon should be pre-formatted in decimal units
# df_model = pd.read_csv('../data/ModelAnalysis.csv', encoding='utf-8')
df_model = pd.read_excel('../data/ModelAnalysis.xlsx')
df_taxonomy = pd.read_excel('../data/ProcessHierarchyNetwork.xlsx')
df_FunctionType = pd.read_excel('../data/FunctionType.xlsx')

## Parse dataframe into table

# Location table
# Sanity check if data can be joined
# df.set_index('key').join(other.set_index('key'))
df_loc["id"] = df_loc.index + 1
df_loc = df_loc.drop(columns='Unnamed: 0')
df_loc["huc_watershed_id"] = np.nan

# FunctionType table
df_FunctionType["id"] = df_FunctionType.index + 1

# Citation table
df_model["attribution_url"].fillna(df_model["url"], inplace=True)
df_citation = df_model[["citation", "url"]].copy()
df_citation["attribution"] = df_model["attribution"].copy()
df_citation["attribution_url"] = df_model["attribution_url"].copy()
df_citation["id"] = df_citation.index + 1

# Spatial and temporal zone tables
df_spatialZoneType = df_model["spatial_property"].copy().drop_duplicates()
df_spatialZoneType = df_spatialZoneType.to_frame()
df_spatialZoneType.reset_index(inplace=True)
df_spatialZoneType = df_spatialZoneType.drop(columns='index')
df_spatialZoneType['id'] = df_spatialZoneType.index + 1
df_temporalZoneType = df_model["temporal_property"].copy().drop_duplicates()
df_temporalZoneType = df_temporalZoneType.to_frame()
df_temporalZoneType.reset_index(inplace=True)
df_temporalZoneType = df_temporalZoneType.drop(columns='index')
df_temporalZoneType['id'] = df_temporalZoneType.index + 1

# Alternative name table
df_altNames0 = df_taxonomy.set_index(['process', 'function', 'identifier', 'process_level']).apply(
    lambda x: x.str.split(',').explode()).reset_index()
df_altNames = df_altNames0[['alternative_names', 'process']].copy()
df_altNames['alternative_names'] = df_altNames['alternative_names'].str.strip()
df_altNames['alternative_names'] = df_altNames['alternative_names'].str.capitalize()
df_altNames.dropna(axis=0, inplace=True)
df_altNames["id"] = df_altNames.index + 1

# Model table
df_model["id"] = df_model.index + 1
df_modelmain = df_model[['id', 'citation', 'watershed_name',
                        'figure_num', 'figure_url', 'figure_caption',
                        'spatial_property', 'num_spatial_zones', 'temporal_property',
                        'num_temporal_zones', 'vegetation_info', 'soil_info', 'geol_info',
                        'topo_info', 'three_d_info', 'uncertainty_info', 'other_info'
                        ]].copy()

# corgi_fig = "https://i.ibb.co/stdkk6P/corgi-with-notes.png"
corgi_fig = "https://sdsugeo.maps.arcgis.com/sharing/rest/content/items/df499e37a2ef40d7885966952c627e01/data"
df_modelmain['figure_url'] = df_modelmain['figure_url'].fillna(corgi_fig)
df_modelmain['figure_url'][df_citation['attribution']=="Not open-access"] = corgi_fig
df_citation['YN'] = df_citation['attribution']=="Not open-access"
df_modelmain.rename(columns={"figure_num": "model_ref"})

# LinkProcessPerceptual table
# Get all the process original text and taxonomy name from model
frames = [df_model[['id', 'flux1', 'flux1_taxonomy']].copy().rename(
    columns={"id": "entry_id", "flux1": "original_text", "flux1_taxonomy": "process"}),
        df_model[['id', 'flux2', 'flux2_taxonomy']].copy().rename(columns={"id": "entry_id", "flux2": "original_text", "flux2_taxonomy": "process"}),
        df_model[['id', 'flux3', 'flux3_taxonomy']].copy().rename(columns={"id": "entry_id", "flux3": "original_text", "flux3_taxonomy": "process"}),
        df_model[['id', 'flux4', 'flux4_taxonomy']].copy().rename(columns={"id": "entry_id", "flux4": "original_text", "flux4_taxonomy": "process"}),
        df_model[['id', 'flux5', 'flux5_taxonomy']].copy().rename(columns={"id": "entry_id", "flux5": "original_text", "flux5_taxonomy": "process"}),
        df_model[['id', 'flux6', 'flux6_taxonomy']].copy().rename(columns={"id": "entry_id", "flux6": "original_text", "flux6_taxonomy": "process"}),
        df_model[['id', 'flux7', 'flux7_taxonomy']].copy().rename(columns={"id": "entry_id", "flux7": "original_text", "flux7_taxonomy": "process"}),
        df_model[['id', 'flux8', 'flux8_taxonomy']].copy().rename(columns={"id": "entry_id", "flux8": "original_text", "flux8_taxonomy": "process"}),
        df_model[['id', 'flux9', 'flux9_taxonomy']].copy().rename(columns={"id": "entry_id", "flux9": "original_text", "flux9_taxonomy": "process"}),
        df_model[['id', 'flux10', 'flux10_taxonomy']].copy().rename(columns={"id": "entry_id", "flux10": "original_text", "flux10_taxonomy": "process"}),
        df_model[['id', 'flux11', 'flux11_taxonomy']].copy().rename(columns={"id": "entry_id", "flux11": "original_text", "flux11_taxonomy": "process"}),
        df_model[['id', 'flux12', 'flux12_taxonomy']].copy().rename(columns={"id": "entry_id", "flux12": "original_text", "flux12_taxonomy": "process"}),
        df_model[['id', 'store1', 'store1_taxonomy']].copy().rename(columns={"id": "entry_id", "store1": "original_text", "store1_taxonomy": "process"}),
        df_model[['id', 'store2', 'store2_taxonomy']].copy().rename(columns={"id": "entry_id", "store2": "original_text", "store2_taxonomy": "process"}),
        df_model[['id', 'store3', 'store3_taxonomy']].copy().rename(columns={"id": "entry_id", "store3": "original_text", "store3_taxonomy": "process"}),
        df_model[['id', 'store4', 'store4_taxonomy']].copy().rename( columns={"id": "entry_id", "store4": "original_text", "store4_taxonomy": "process"}),
        df_model[['id', 'store5', 'store5_taxonomy']].copy().rename(columns={"id": "entry_id", "store5": "original_text", "store5_taxonomy": "process"}),
        df_model[['id', 'store6', 'store6_taxonomy']].copy().rename(columns={"id": "entry_id", "store6": "original_text", "store6_taxonomy": "process"}),
        df_model[['id', 'store7', 'store7_taxonomy']].copy().rename(columns={"id": "entry_id", "store7": "original_text", "store7_taxonomy": "process"}),
        df_model[['id', 'store8', 'store8_taxonomy']].copy().rename(columns={"id": "entry_id", "store8": "original_text", "store8_taxonomy": "process"}),
        ]

df_linkProcessPerceptual0 = pd.concat(frames, axis=0, ignore_index=True)
df_linkProcessPerceptual0["id"] = df_linkProcessPerceptual0.index + 1

# Create taxonomy table
df_process0 = df_taxonomy.drop(columns='alternative_names')

# join process taxonomy and model table
df_linkProcessPerceptual0["process_lower"] = df_linkProcessPerceptual0['process'].str.lower()
df_linkProcessPerceptual0["process_lower"] = df_linkProcessPerceptual0['process_lower'].str.strip()
df_process0["process_lower"] = df_process0['process'].str.lower()
df_process0["process_lower"] = df_process0['process_lower'].str.strip()

# find and add some new process from model table to taxonomy table (# Check here if you want to check process miscategorization)
df_linkProcessPerceptual1 = df_linkProcessPerceptual0.merge(df_process0, on='process_lower', how='left')
new_process = df_linkProcessPerceptual1.loc[(df_linkProcessPerceptual1['process_x'].isnull() == False) & (
            df_linkProcessPerceptual1['process_y'].isnull() == True)]
new_process.drop_duplicates(subset='process_lower', inplace=True)

add_new_process = pd.DataFrame(
    {'process': new_process['process_x'], 'process_lower': new_process['process_x'].str.lower(),
     'identifier': ['NewProcess'] * len(new_process['process_x'])})
df_process1 = pd.concat([df_process0, add_new_process])
df_process1["id"] = df_process1.reset_index().index + 1


# re-join process taxonomy and model table with new process
df_linkProcessPerceptual2 = df_linkProcessPerceptual0.merge(df_process1, on='process_lower', how='left')
df_linkProcessPerceptual2.rename(columns={"id_y": "process_id"}, inplace=True)
df_linkProcessPerceptual = df_linkProcessPerceptual2.drop(
    columns={'process_x', 'id_x', 'process_lower', 'process_y', 'function', 'identifier', 'process_level'})
df_linkProcessPerceptual.dropna(subset=['original_text'], axis=0, inplace=True)
df_linkProcessPerceptual["id"] = df_linkProcessPerceptual.reset_index().index + 1
df_linkProcessPerceptual["process_id"] = df_linkProcessPerceptual["process_id"].astype('int')
# df_linkProcessPerceptual[df_linkProcessPerceptual['process_id'].isnull()]
df_process = df_process1.drop(columns='process_lower')

###################################
## 1. Connect to SQL database
###################################

# Read config
config = configparser.ConfigParser()
config.read('config.ini')

DB_NAME = config['postgresql']['DB_NAME']
HOST = config['postgresql']['HOST']
PORT = config['postgresql']['PORT']
USER_NAME = config['postgresql']['USER_NAME']
PASSWD = config['postgresql']['PASSWD']

# Connect to database
conn_string = f'postgresql://{USER_NAME}:{PASSWD}@{HOST}:{PORT}/{DB_NAME}'
db = create_engine(conn_string, client_encoding='utf8')
try:
    conn = db.connect()
    print("connection to '%s'@'%s' success!" % (DB_NAME, HOST))
except Exception as e:
    print("connection to '%s'@'%s' failed." % (DB_NAME, HOST))
    print(e)

###################################
## 2. Create database
###################################

tables = ['locations', 'citations', 'spatial_zone_type', 'temporal_zone_type', 'process_alt_names',
            'function_type', 'perceptual_model', 'link_process_perceptual', 'process_taxonomy']
conn.execute(text("set search_path to public, perceptual_model"))
conn.execute(text("SET CLIENT_ENCODING TO 'UTF8';"))
for table in tables:
    try:
        conn.execute(text(f"DROP TABLE {table} CASCADE;"))
        print('drop old tables')
    except Exception as e:
        print(e)

schema = 'perceptual_model'
connarg = {'con': conn, 'schema': 'perceptual_model', 'if_exists': 'replace', 'index': False}

# set table names in lower case https://github.com/pandas-dev/pandas/issues/13206
df_loc.to_sql('locations', **connarg)
df_citation.to_sql('citations', **connarg)
df_spatialZoneType.to_sql('spatial_zone_type', **connarg)
df_temporalZoneType.to_sql('temporal_zone_type', **connarg)
df_altNames.to_sql('process_alt_names', **connarg)
df_FunctionType.to_sql('function_type', **connarg)
df_modelmain.to_sql('perceptual_model', **connarg)
df_linkProcessPerceptual.to_sql('link_process_perceptual', **connarg)
df_process.to_sql('process_taxonomy', **connarg)

# Relate the location table to HUC8 watershed table
query = "ALTER TABLE perceptual_model.locations \
ADD COLUMN pt geometry(point, 4326); \
WITH pt_geom AS ( \
	SELECT id, ST_SetSRID(ST_MakePoint(lon, lat), 4326) AS pt \
	from perceptual_model.locations \
	) \
UPDATE perceptual_model.locations \
SET pt = pt_geom.pt \
FROM pt_geom \
WHERE pt_geom.id = locations.id; \
    "
# ALTER TABLE locations \
# ALTER COLUMN huc_watershed_id TYPE INTEGER USING huc_watershed_id::integer; \
# WITH joined_huc8_pt AS ( \
# SELECT locations.id AS pt_id, huc_watersheds.id as huc8_id, huc_watersheds.huc8 AS huc8_code \
# FROM locations \
# JOIN huc_watersheds \
# ON ST_contains(ST_Transform(huc_watersheds.geom, 4326), locations.pt) \
# ) \
# UPDATE locations \
# SET huc_watershed_id = joined_huc8_pt.huc8_id \
# FROM joined_huc8_pt \
# WHERE locations.id = joined_huc8_pt.pt_id;"

try:
    conn.execute(text(query))
    print("success")
except Exception as e:
    print(e)

# add primary keys
for table in tables:
    try:
        conn.execute(text(f"ALTER TABLE {table} ADD PRIMARY KEY (id);"))
        print(f"successfully created table {table}")
    except Exception as e:
        print(e)

# add foreign keys
# model & location
query = "ALTER TABLE perceptual_model ADD COLUMN location_id int; \
UPDATE perceptual_model \
SET location_id = locations.id \
FROM locations \
WHERE perceptual_model.watershed_name = locations.name; \
ALTER TABLE perceptual_model \
ADD FOREIGN KEY (location_id) REFERENCES locations(id); \
ALTER TABLE perceptual_model DROP COLUMN watershed_name;"

try:
    conn.execute(text(query))
    print("success")
except Exception as e:
    print(e)

# model & citation
query = "ALTER TABLE perceptual_model ADD COLUMN citation_id int; \
UPDATE perceptual_model \
SET citation_id = citations.id \
FROM citations \
WHERE perceptual_model.citation = citations.citation; \
ALTER TABLE perceptual_model \
ADD FOREIGN KEY (citation_id) REFERENCES citations(id); \
ALTER TABLE perceptual_model DROP COLUMN citation;"

try:
    conn.execute(text(query))
    print("success")
except Exception as e:
    print(e)

# model & spatial zone
query = "ALTER TABLE perceptual_model ADD COLUMN spatialzone_id int; \
UPDATE perceptual_model \
SET spatialzone_id = spatial_zone_type.id \
FROM spatial_zone_type \
WHERE perceptual_model.spatial_property = spatial_zone_type.spatial_property; \
ALTER TABLE perceptual_model \
ADD FOREIGN KEY (spatialzone_id) REFERENCES spatial_zone_type(id); \
ALTER TABLE perceptual_model DROP COLUMN spatial_property;"

try:
    conn.execute(text(query))
    print("success")
except Exception as e:
    print(e)

# model & temporal zone
query = "ALTER TABLE perceptual_model ADD COLUMN temporalzone_id int; \
UPDATE perceptual_model \
SET temporalzone_id = temporal_zone_type.id \
FROM temporal_zone_type \
WHERE perceptual_model.temporal_property = temporal_zone_type.temporal_property; \
ALTER TABLE perceptual_model \
ADD FOREIGN KEY (temporalzone_id) REFERENCES temporal_zone_type(id); \
ALTER TABLE perceptual_model DROP COLUMN temporal_property;"

try:
    conn.execute(text(query))
    print("success")
except Exception as e:
    print(e)

# model & linktable
query = "ALTER TABLE link_process_perceptual  \
ADD FOREIGN KEY (entry_id) REFERENCES perceptual_model(id);"

try:
    conn.execute(text(query))
    print("success")
except Exception as e:
    print(e)

# process taxonomy & alternative names
query = "ALTER TABLE process_alt_names ADD COLUMN process_id int; \
UPDATE process_alt_names \
SET process_id = process_taxonomy.id \
FROM process_taxonomy \
WHERE process_alt_names.process = process_taxonomy.process; \
ALTER TABLE process_alt_names \
ADD FOREIGN KEY (process_id) REFERENCES process_taxonomy(id); \
ALTER TABLE process_alt_names DROP COLUMN process;"

try:
    conn.execute(text(query))
    print("success")
except Exception as e:
    print(e)

# process taxonomy & function type
query = "ALTER TABLE process_taxonomy ADD COLUMN function_id int; \
UPDATE process_taxonomy \
SET function_id = function_type.id \
FROM function_type \
WHERE process_taxonomy.function = function_type.name; \
ALTER TABLE process_taxonomy \
ADD FOREIGN KEY (function_id) REFERENCES function_type(id); \
ALTER TABLE process_taxonomy DROP COLUMN function;"

try:
    conn.execute(text(query))
    print("success")
except Exception as e:
    print(e)

# # huc_watersheds & locations
# query = "ALTER TABLE locations \
# ADD FOREIGN KEY (huc_watershed_id) \
# REFERENCES huc_watersheds(id);"

# try:
#     conn.execute(text(query))
#     print("success")
# except Exception as e:
#     print(e)


# linktable & process taxonomy

# somehow this does not work ...
"""
# try joining on pandas ...
query = "ALTER TABLE link_process_perceptual ADD COLUMN process_id int; \
UPDATE link_process_perceptual \
SET process_id = process_taxonomy.id \
FROM process_taxonomy \
WHERE link_process_perceptual.process::text ILIKE process_taxonomy.process::text; \
ALTER TABLE link_process_perceptual \
ADD FOREIGN KEY (process_id) REFERENCES process_taxonomy(id);" # \
# ALTER TABLE link_process_perceptual DROP COLUMN process_name;"
"""

# try joining on pandas ...
query = "ALTER TABLE link_process_perceptual \
ADD FOREIGN KEY (process_id) REFERENCES process_taxonomy(id);"
# \
# ALTER TABLE link_process_perceptual DROP COLUMN process_name;"

try:
    conn.execute(text(query))
    print("Link taxonomy & perceptual model -- success")
except Exception as e:
    print(e)

# drop_tables = "DROP TABLE giant_table, giant_table_flux, giant_table_store, giant_table_update;"
# try:
#     conn.execute(text(drop_tables))
#     print("Drop old temp tables -- success")
# except Exception as e:
#     print(e)

## Join tables and dump everything into csv file
# https://hevodata.com/learn/postgres-export-to-csv/
join_desired_tables = "\
CREATE TEMP TABLE giant_table AS (\
SELECT perceptual_model.id, \
		citations.citation, \
		citations.url, \
        citations.attribution, \
        citations.attribution_url, \
		perceptual_model.figure_num, \
        perceptual_model.figure_caption, \
        perceptual_model.figure_url, \
        locations.name AS watershed_name, \
		locations.lat, \
		locations.lon, \
        locations.area_km2, \
		process_taxonomy.process, \
		process_taxonomy.identifier,\
		function_type.name AS function_name,\
		perceptual_model.num_spatial_zones,\
		spatial_zone_type.spatial_property,\
		perceptual_model.num_temporal_zones,\
		temporal_zone_type.temporal_property,\
		perceptual_model.vegetation_info,\
		perceptual_model.soil_info,\
		perceptual_model.geol_info,\
		perceptual_model.topo_info,\
		perceptual_model.three_d_info,\
		perceptual_model.uncertainty_info,\
		perceptual_model.other_info\
	FROM perceptual_model \
	INNER JOIN citations \
		ON citations.id = perceptual_model.citation_id \
	INNER JOIN locations \
		ON locations.id = perceptual_model.location_id \
	INNER JOIN spatial_zone_type \
		ON spatial_zone_type.id = perceptual_model.spatialzone_id \
	INNER JOIN temporal_zone_type \
		ON temporal_zone_type.id = perceptual_model.temporalzone_id \
	INNER JOIN link_process_perceptual \
		ON perceptual_model.id = link_process_perceptual.entry_id \
	INNER JOIN process_taxonomy \
		ON link_process_perceptual.process_id = process_taxonomy.id \
	INNER JOIN function_type \
		ON process_taxonomy.function_id = function_type.id \
ORDER BY perceptual_model.id \
);"

join_desired_tables2 = "\
CREATE TEMP TABLE giant_table_base AS ( \
SELECT DISTINCT \
    id,  \
	citation,  \
	url,  \
	attribution,  \
	attribution_url,  \
	figure_num,  \
	figure_caption,  \
	figure_url,  \
	watershed_name,  \
	lat,  \
	lon,  \
	area_km2,  \
	num_spatial_zones,  \
	spatial_property,  \
	num_temporal_zones,  \
	temporal_property,  \
	vegetation_info,  \
	soil_info,  \
	geol_info,  \
	topo_info,  \
	three_d_info,  \
	uncertainty_info,  \
	other_info \
FROM giant_table \
); \
CREATE TEMP TABLE giant_table_flux AS (  \
SELECT DISTINCT  \
id AS temp_id1,  \
COUNT(process) OVER(PARTITION BY id) AS num_flux,  \
STRING_AGG(process, ', ') OVER(PARTITION BY id) AS flux_list,  \
STRING_AGG(identifier, ', ') OVER(PARTITION BY id) AS flux_id_list  \
FROM   giant_table  \
	WHERE function_name ILIKE 'Filling of store'  \
	OR function_name ILIKE 'Release from store'  \
	OR function_name ILIKE 'In-catchment flux'  \
	OR function_name ILIKE 'In-store flux'  \
	OR function_name ILIKE 'Release'  \
	); \
CREATE TEMP TABLE giant_table_store AS ( \
SELECT DISTINCT id AS temp_id2,  \
COUNT(process) OVER(PARTITION BY id) AS num_store,  \
STRING_AGG(process, ', ') OVER(PARTITION BY id) AS store_list,  \
STRING_AGG(identifier, ', ') OVER(PARTITION BY id) AS store_id_list  \
FROM giant_table  \
	WHERE function_name ILIKE 'Store'  \
	OR function_name ILIKE 'Store, temporary'  \
	OR function_name ILIKE 'Store characteristics, temporary'  \
	OR function_name ILIKE 'Store characteristics, permanent'  \
	);  \
CREATE TEMP TABLE giant_table_update AS ( \
SELECT * FROM giant_table_base  \
LEFT JOIN giant_table_store  \
ON giant_table_base.id = giant_table_store.temp_id2 \
LEFT JOIN giant_table_flux \
ON giant_table_base.id = giant_table_flux.temp_id1 \
ORDER BY id  \
	); \
ALTER TABLE giant_table_update \
DROP COLUMN temp_id1, \
DROP COLUMN temp_id2,  \
ADD COLUMN dummy_column NUMERIC DEFAULT 1; \
"

try:
    conn.execute(text(join_desired_tables))
    print("success")
except Exception as e:
    print(e)

try:
    conn.execute(text(join_desired_tables2))
    print("success")
except Exception as e:
    print(e)


# save_table = "\copy giant_table_update TO 'G://Shared drives/Perceptual model review/ForRyoko/perceptual-model-arcgis/db_dev/data/giant_table_update.csv' WITH DELIMITER ',' CSV HEADER;"
# conn.execute(save_table)

query = "SELECT * FROM giant_table_update"
try:
    df_results = pd.read_sql(text(query), conn)
    # results = conn.execute(query).fetchall()
    print("success")
    print(df_results.columns)
except Exception as e:
    print(e)

df_results['huc_watershed_id'] = 'N/A'
df_results['num_store'].fillna(0, inplace=True)
df_results['num_flux'].fillna(0, inplace=True)
df_results['area_km2'].fillna(-9999, inplace=True)
df_results.fillna('N/A', inplace=True)
df_results.to_csv('../data/giant_table_v4.csv', sep=',', header=True, index=False, encoding='utf-8')

conn.close()
db.dispose()
print('closed connections')
