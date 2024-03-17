-- Use this code to debug if 1-1-build_database.ipynb don't work well


-- Launch PostgreSQL
-- "C:\Program Files\PostgreSQL\14\bin\psql.exe" -h [HOST_NAME] -U [USER_NAME] -d [PASSWORD]

-- Just to check if PostGIS is properly working
-- https://postgis.net/docs/ST_MakePoint.html
SELECT ST_SetSRID(ST_MakePoint(-71.1043443253471, 42.3150676015829),4326);

-- Preparation
-- Set path in PostgreSQL. Specify the schema names (in this example, 'public' and 'perceptual_model')
SET search_path TO public, perceptual_model;
-- Set encoding
SET CLIENT_ENCODING TO 'UTF8';

-- display all table & schema information
\d

-- display a table informaton
-- \d + table name
\d perceptual_model
\d process_taxonomy
\d citations
\d locations
\d function_type
\d link_process_perceptual
\d process_alt_names
\d spatial_zone_type
\d temporal_zone_type

-- display empty foreign keys (should show nothing)

-- main table
SELECT * FROM perceptual_model
WHERE citation_id IS NULL
OR citation_id::text = '';

SELECT * FROM perceptual_model
WHERE spatialzone_id IS NULL
OR spatialzone_id::text = '';

SELECT * FROM perceptual_model
WHERE temporalzone_id IS NULL
OR temporalzone_id::text = '';

SELECT * FROM perceptual_model
WHERE location_id IS NULL
OR location_id::text = '';

-- link process perceptual 
SELECT * FROM link_process_perceptual
WHERE entry_id IS NULL
OR entry_id::text = '';

-- proces table
SELECT * FROM process_alt_names
WHERE process_id IS NULL
OR process_id::text = '';

-- This can show some results (some process up to Level 2 does not have function (yet))
SELECT * FROM process_taxonomy
WHERE function_id IS NULL
OR function_id::text = '';

-- process table
SELECT * FROM process_taxonomy
WHERE process_level IS NULL
OR process_level::text = '';

-- 
SELECT * FROM citations
WHERE attribution_url IS NULL
OR attribution_url::text = '';



-- Count some key stats

-- count the number of records
SELECT COUNT(id)
FROM perceptual_model;

-- count by spatial zones
SELECT num_spatial_zones, COUNT(id)
FROM perceptual_model
GROUP BY num_spatial_zones
ORDER BY num_spatial_zones;

/*
 num_spatial_zones | count
-------------------+-------
                 1 |    51
                 2 |     7
                 4 |     2
                 6 |     2
                 7 |     1
*/

-- count by temporal zones
SELECT num_temporal_zones, COUNT(id)
FROM perceptual_model
GROUP BY num_temporal_zones
ORDER BY num_temporal_zones;

/*
 num_temporal_zones | count
--------------------+-------
                  1 |    35
                  2 |    11
                  3 |     8
                  4 |     8
                  5 |     1
*/

-- count by flux
WITH flux_count AS 
(SELECT perceptual_model.id, COUNT(perceptual_model.id) AS num_flux_per_model
	FROM perceptual_model
	INNER JOIN link_process_perceptual
		ON perceptual_model.id = link_process_perceptual.entry_id
	INNER JOIN process_taxonomy
		ON link_process_perceptual.process_id = process_taxonomy.id
	INNER JOIN function_type
		ON process_taxonomy.function_id = function_type.id
	WHERE function_type.name ILIKE 'Filling of store'
	OR function_type.name ILIKE 'Release from store'
	OR function_type.name ILIKE 'In-catchment flux'
	OR function_type.name ILIKE 'In-store flux' 
	OR function_type.name ILIKE 'Release' 
	GROUP BY perceptual_model.id)
SELECT num_flux_per_model, COUNT(num_flux_per_model) AS num_models
FROM flux_count
GROUP BY num_flux_per_model
ORDER BY num_flux_per_model;

SELECT num_flux, COUNT(temp_id1)
FROM giant_table_flux
GROUP BY num_flux
ORDER BY num_flux;

/*
 num_flux | count
----------+-------
        1 |     1
        2 |     5
        3 |     9
        4 |    14
        5 |     9
        6 |    11
        7 |     4
        8 |     6
        9 |     2
*/


-- count by stores
WITH store_count AS 
(SELECT perceptual_model.id, COUNT(perceptual_model.id) AS num_store_per_model
	FROM perceptual_model
	INNER JOIN link_process_perceptual
		ON perceptual_model.id = link_process_perceptual.entry_id
	INNER JOIN process_taxonomy
		ON link_process_perceptual.process_id = process_taxonomy.id
	INNER JOIN function_type
		ON process_taxonomy.function_id = function_type.id
	WHERE function_type.name ILIKE 'Store'
	OR function_type.name ILIKE 'Store, temporary'
	OR function_type.name ILIKE 'Store characteristics, temporary'
	OR function_type.name ILIKE 'Store characteristics, permanent'
	GROUP BY perceptual_model.id)
SELECT num_store_per_model, COUNT(num_store_per_model) AS num_models
FROM store_count
GROUP BY num_store_per_model
ORDER BY num_store_per_model;

SELECT num_store, COUNT(temp_id2)
FROM giant_table_store
GROUP BY num_store
ORDER BY num_store;

/*
 num_store_per_model | num_models
---------------------+------------
                   1 |          2
                   2 |          2
                   3 |         11
                   4 |         20
                   5 |          8
                   6 |          6
                   7 |          4
                   8 |          2
                   9 |          3
*/

-- count by process

-- subsurface processes 
SELECT COUNT(process_taxonomy.identifier) AS num_process
	FROM perceptual_model
	INNER JOIN link_process_perceptual
		ON perceptual_model.id = link_process_perceptual.entry_id
	INNER JOIN process_taxonomy
		ON link_process_perceptual.process_id = process_taxonomy.id
	WHERE process_taxonomy.identifier ILIKE 'Sub.%';

SELECT link_process_perceptual.id, process_taxonomy.identifier
	FROM perceptual_model
	INNER JOIN link_process_perceptual
		ON perceptual_model.id = link_process_perceptual.entry_id
	INNER JOIN process_taxonomy
		ON link_process_perceptual.process_id = process_taxonomy.id
	WHERE process_taxonomy.identifier ILIKE 'Sub.%';


/*
 num_process
-------------
         436


*/

SELECT process_taxonomy.identifier, COUNT(process_taxonomy.identifier) AS num_process
	FROM perceptual_model
	INNER JOIN link_process_perceptual
		ON perceptual_model.id = link_process_perceptual.entry_id
	INNER JOIN process_taxonomy
		ON link_process_perceptual.process_id = process_taxonomy.id
	WHERE process_taxonomy.identifier ILIKE 'Sub.%'
GROUP BY process_taxonomy.identifier
ORDER BY COUNT(process_taxonomy.identifier) DESC;

-- Need to sum up by the 2nd category ... 

/*
     identifier     | num_process
--------------------+-------------
 Sub.Soil.Store     |          71
 Sub.GW.Store       |          48
 Sub.SSFlow         |          37
 Sub.Soil.Drain     |          20
 Sub.GW.Store.Perch |          15
 */



-- count by process level
SELECT process_taxonomy.process_level, COUNT(process_taxonomy.process_level) AS num_process
	FROM perceptual_model
	INNER JOIN link_process_perceptual
		ON perceptual_model.id = link_process_perceptual.entry_id
	INNER JOIN process_taxonomy
		ON link_process_perceptual.process_id = process_taxonomy.id
GROUP BY process_taxonomy.process_level
ORDER BY COUNT(process_taxonomy.process_level) DESC;

/*
 process_level | num_process
---------------+-------------
             3 |         292
             4 |         177
             2 |          85

True counts --- 
 process_level | num_process
---------------+-------------
             3 |         222
             4 |         103
             2 |          86
               |           0

*/

/* The results show that Subsurface Processes dominate the diagrams (299 instances), followed by Surface Processes (65) and Channel Processes (47). 
The most common classes in Subsurface Processes were Groundwater (126), Soils (94) and Subsurface Stormflow (62). 
The most common classes in Surface Processes were Overland Flow (35) and Infiltration (14). 
The most common class in Channel Processes was Channel Storage (33). 
For level of detail, diagrams most commonly contained Processes (222), followed by Sub-Processes (103) and Classes (86).
*/

-- Join almost all tables for webmap
DROP TABLE giant_table;
CREATE TEMP TABLE giant_table AS (
SELECT perceptual_model.id, 
		citations.citation, 
		citations.url,
		perceptual_model.figure_num,
		locations.name AS watershed_name,
		locations.lat, 
		locations.lon, 
		process_taxonomy.process, 
		process_taxonomy.identifier,
		function_type.name AS function_name,
		perceptual_model.num_spatial_zones,
		spatial_zone_type.spatial_property,
		perceptual_model.num_temporal_zones,
		temporal_zone_type.temporal_property,
		perceptual_model.vegetation_info,
		perceptual_model.soil_info,
		perceptual_model.geol_info,
		perceptual_model.topo_info,
		perceptual_model.three_d_info,
		perceptual_model.uncertainty_info,
		perceptual_model.other_info
	FROM perceptual_model
	INNER JOIN citations
		ON citations.id = perceptual_model.citation_id
	INNER JOIN locations
		ON locations.id = perceptual_model.location_id
	INNER JOIN spatial_zone_type
		ON spatial_zone_type.id = perceptual_model.spatialzone_id
	INNER JOIN temporal_zone_type
		ON temporal_zone_type.id = perceptual_model.temporalzone_id
	INNER JOIN link_process_perceptual
		ON perceptual_model.id = link_process_perceptual.entry_id
	INNER JOIN process_taxonomy
		ON link_process_perceptual.process_id = process_taxonomy.id
	INNER JOIN function_type
		ON process_taxonomy.function_id = function_type.id
ORDER BY perceptual_model.id
);

-- Compare giant_table_flux and giant_table_store with Excel for debug
DROP TABLE giant_table_flux;
CREATE TEMP TABLE giant_table_flux AS (
SELECT DISTINCT 
 id, 
 citation, 
 url, 
 figure_num, 
 watershed_name, 
 lat, 
 lon, 
 num_spatial_zones, 
 spatial_property, 
 num_temporal_zones, 
 temporal_property, 
 vegetation_info, 
 soil_info, 
 geol_info, 
 topo_info, 
 three_d_info, 
 uncertainty_info, 
 other_info, 
 COUNT(process) OVER(PARTITION BY id) AS num_flux, 
 STRING_AGG(process, ', ') OVER(PARTITION BY id) AS flux_list,
 STRING_AGG(identifier, ', ') OVER(PARTITION BY id) AS flux_id_list
FROM   giant_table
	WHERE function_name ILIKE 'Filling of store'
	OR function_name ILIKE 'Release from store'
	OR function_name ILIKE 'In-catchment flux'
	OR function_name ILIKE 'In-store flux' 
	OR function_name ILIKE 'Release' 
	);

DROP TABLE giant_table_store;
CREATE TEMP TABLE giant_table_store AS (
SELECT DISTINCT id AS temp_id, 
COUNT(process) OVER(PARTITION BY id) AS num_store, 
 STRING_AGG(process, ', ') OVER(PARTITION BY id) AS store_list,
 STRING_AGG(identifier, ', ') OVER(PARTITION BY id) AS store_id_list
FROM giant_table
	WHERE function_name ILIKE 'Store'
	OR function_name ILIKE 'Store, temporary'
	OR function_name ILIKE 'Store characteristics, temporary'
	OR function_name ILIKE 'Store characteristics, permanent'
	);

DROP TABLE giant_table_update;
CREATE TEMP TABLE giant_table_update AS (
SELECT DISTINCT * FROM giant_table_flux
FULL JOIN giant_table_store
ON giant_table_flux.id = giant_table_store.temp_id
ORDER BY id
	);

ALTER TABLE giant_table_update 
DROP COLUMN temp_id;

-- save to csv
\copy giant_table TO 'G://Shared drives/Perceptual model review/ForRyoko/perceptual-model-arcgis/db_dev/data/giant_table.csv' WITH DELIMITER ',' CSV HEADER;
\copy giant_table_update TO 'G://Shared drives/Perceptual model review/ForRyoko/perceptual-model-arcgis/db_dev/data/giant_table_update.csv' WITH DELIMITER ',' CSV HEADER;

\copy giant_table_store TO 'G://Shared drives/Perceptual model review/ForRyoko/perceptual-model-arcgis/db_dev/data/store.csv' WITH DELIMITER ',' CSV HEADER;
\copy giant_table_flux TO 'G://Shared drives/Perceptual model review/ForRyoko/perceptual-model-arcgis/db_dev/data/flux.csv' WITH DELIMITER ',' CSV HEADER;


------------------- some cutouts

SELECT perceptual_model.id, COUNT(perceptual_model.id) AS num_flux_per_model
	FROM perceptual_model
	INNER JOIN link_process_perceptual
		ON perceptual_model.id = link_process_perceptual.entry_id
	INNER JOIN process_taxonomy
		ON link_process_perceptual.process_id = process_taxonomy.id
	INNER JOIN function_type
		ON process_taxonomy.function_id = function_type.id
	WHERE function_type.name ILIKE '%flux%'
	GROUP BY perceptual_model.id
	ORDER BY perceptual_model.id;

SELECT perceptual_model.id, process_taxonomy.process, citations.citation
	FROM perceptual_model
	INNER JOIN link_process_perceptual
		ON perceptual_model.id = link_process_perceptual.entry_id
	INNER JOIN process_taxonomy
		ON link_process_perceptual.process_id = process_taxonomy.id
	INNER JOIN function_type
		ON process_taxonomy.function_id = function_type.id
	INNER JOIN citations
		ON citations.id = perceptual_model.citation_id
	WHERE function_type.name ILIKE 'Filling of store'
	OR function_type.name ILIKE 'Release from store'
	OR function_type.name ILIKE 'In-catchment flux'
	OR function_type.name ILIKE 'In-store flux' 
	OR function_type.name ILIKE 'Release' 
	and perceptual_model.id = 1;

 select * from link_process_perceptual 
 INNER JOIN process_taxonomy
 ON link_process_perceptual.process_id = process_taxonomy.id
 where entry_id =1;

-- Compare giant_table_flux and giant_table_store with Excel for debug
DROP TABLE giant_table;
CREATE TEMP TABLE giant_table AS (
SELECT perceptual_model.id, 
		citations.citation, 
		citations.url, 
        citations.attribution, 
        citations.attribution_url, 
		perceptual_model.figure_num, 
        perceptual_model.figure_caption, 
        perceptual_model.figure_url, 
        locations.name AS watershed_name, 
		locations.lat, 
		locations.lon, 
        locations.area_km2, 
        locations.huc_watershed_id, 
		process_taxonomy.process, 
		process_taxonomy.identifier,
		function_type.name AS function_name,
		perceptual_model.num_spatial_zones,
		spatial_zone_type.spatial_property,
		perceptual_model.num_temporal_zones,
		temporal_zone_type.temporal_property,
		perceptual_model.vegetation_info,
		perceptual_model.soil_info,
		perceptual_model.geol_info,
		perceptual_model.topo_info,
		perceptual_model.three_d_info,
		perceptual_model.uncertainty_info,
		perceptual_model.other_info
	FROM perceptual_model 
	INNER JOIN citations 
		ON citations.id = perceptual_model.citation_id 
	INNER JOIN locations 
		ON locations.id = perceptual_model.location_id 
	INNER JOIN spatial_zone_type 
		ON spatial_zone_type.id = perceptual_model.spatialzone_id 
	INNER JOIN temporal_zone_type 
		ON temporal_zone_type.id = perceptual_model.temporalzone_id 
	INNER JOIN link_process_perceptual 
		ON perceptual_model.id = link_process_perceptual.entry_id 
	INNER JOIN process_taxonomy 
		ON link_process_perceptual.process_id = process_taxonomy.id 
	INNER JOIN function_type 
		ON process_taxonomy.function_id = function_type.id 
ORDER BY perceptual_model.id 
);


CREATE TEMP TABLE giant_table_base AS (
 SELECT DISTINCT
	 id, 
	 citation, 
	 url, 
	 attribution, 
	 attribution_url, 
	 figure_num, 
	 figure_caption, 
	 figure_url, 
	 watershed_name, 
	 lat, 
	 lon, 
	 area_km2, 
	 huc_watershed_id, 
	 num_spatial_zones, 
	 spatial_property, 
	 num_temporal_zones, 
	 temporal_property, 
	 vegetation_info, 
	 soil_info, 
	 geol_info, 
	 topo_info, 
	 three_d_info, 
	 uncertainty_info, 
	 other_info
 FROM giant_table
);

DROP TABLE giant_table_flux;
CREATE TEMP TABLE giant_table_flux AS ( 
SELECT DISTINCT 
 id AS temp_id1, 
 COUNT(process) OVER(PARTITION BY id) AS num_flux, 
 STRING_AGG(process, ', ') OVER(PARTITION BY id) AS flux_list, 
 STRING_AGG(identifier, ', ') OVER(PARTITION BY id) AS flux_id_list 
FROM   giant_table 
	WHERE function_name ILIKE 'Filling of store' 
	OR function_name ILIKE 'Release from store' 
	OR function_name ILIKE 'In-catchment flux' 
	OR function_name ILIKE 'In-store flux' 
	OR function_name ILIKE 'Release' 
	);

DROP TABLE giant_table_store;
CREATE TEMP TABLE giant_table_store AS (
SELECT DISTINCT id AS temp_id2, 
COUNT(process) OVER(PARTITION BY id) AS num_store, 
 STRING_AGG(process, ', ') OVER(PARTITION BY id) AS store_list, 
 STRING_AGG(identifier, ', ') OVER(PARTITION BY id) AS store_id_list 
FROM giant_table 
	WHERE function_name ILIKE 'Store' 
	OR function_name ILIKE 'Store, temporary' 
	OR function_name ILIKE 'Store characteristics, temporary' 
	OR function_name ILIKE 'Store characteristics, permanent' 
	);

CREATE TEMP TABLE giant_table_update AS (
SELECT * FROM giant_table_base 
LEFT JOIN giant_table_store 
ON giant_table_base.id = giant_table_store.temp_id2
LEFT JOIN giant_table_flux
ON giant_table_base.id = giant_table_flux.temp_id1
ORDER BY id 
	);
ALTER TABLE giant_table_update
DROP COLUMN temp_id1,
DROP COLUMN temp_id2;

---------- Some more debugs
-- Channel storage is not recognized as flux 

SELECT * FROM process_taxonomy INNER JOIN function_type
ON process_taxonomy.function_id = function_type.id
WHERE process_taxonomy.process ILIKE 'Channel%';

SELECT * FROM process_taxonomy 
WHERE process_taxonomy.process ILIKE 'Channel%';

-- function_id is missing where the 'Release' had extra white space in the string
SELECT * FROM process_taxonomy
WHERE function_id IS NULL;


---- Some debugs 
SELECT id, flux_list, function_name FROM giant_table_update
WHERE num_flux = 2; 

SELECT id, process, function_name
FROM giant_table
WHERE process LIKE 'Evapotranspiration'; 

SELECT id, process, function_name
FROM giant_table
WHERE process LIKE 'Riparian transpiration'; 

SELECT id, process, function_name
FROM giant_table
WHERE process LIKE 'Soil surface evaporation'; 

SELECT citation, process, function_name, identifier
FROM giant_table
WHERE identifier ILIKE 'Human.%';



CREATE TEMP TABLE giant_table_base AS ( \
SELECT DISTINCT \
    id,  \
	model_type,\
	citation,  \
	url,  \
	attribution,  \
	attribution_url,  \
	figure_num,  \
	figure_caption,  \
	figure_url,  \
	textmodel_snipped, \
	textmodel_section_number, \
	textmodel_section_name, \
	textmodel_page_number, \
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
    OR function_name IS NULL\
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