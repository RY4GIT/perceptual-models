-- Calculate statistics from database

-- Launch PostgreSQL
-- "C:\Program Files\PostgreSQL\14\bin\psql.exe" -h localhost -U postgres -d postgres

-- Preparation
-- Set path in PostgreSQL. Specify the schema names (in this example, 'public' and 'perceptual_model')
SET search_path TO public, perceptual_model;
-- Set encoding
SET CLIENT_ENCODING TO 'UTF8';

-- Calculate key stats

-- 1. Histograms (#spatial zones, temporal zones, fluxes, and stores)

-- count the number of records
SELECT COUNT(id)
FROM perceptual_model;

-- count by spatial zones
SELECT id, num_spatial_zones
FROM perceptual_model
ORDER BY id;

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
SELECT id, num_temporal_zones
FROM perceptual_model
ORDER BY id;

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
SELECT perceptual_model.id, flux_count.num_flux_per_model
FROM flux_count
RIGHT JOIN perceptual_model
ON perceptual_model.id = flux_count.id
ORDER BY perceptual_model.id;

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

/*
 num_flux_per_model | num_models
--------------------+------------
                  1 |          1
                  2 |          5
                  3 |          9
                  4 |         17
                  5 |         10
                  6 |          7
                  7 |          7
                  8 |          4
                  9 |          1
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
SELECT perceptual_model.id, store_count.num_store_per_model
FROM store_count
RIGHT JOIN perceptual_model
ON perceptual_model.id = store_count.id
ORDER BY perceptual_model.id;

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

-- 2. Count by process

-- Make a giant process table 
DROP TABLE process_table;
CREATE TEMP TABLE process_table AS (
SELECT perceptual_model.id, process_taxonomy.identifier, function_type.name AS function
	FROM perceptual_model
	INNER JOIN link_process_perceptual
		ON perceptual_model.id = link_process_perceptual.entry_id
	INNER JOIN process_taxonomy
		ON link_process_perceptual.process_id = process_taxonomy.id
	INNER JOIN function_type
		ON function_type.id = process_taxonomy.function_id
ORDER BY perceptual_model.id);


-- # fluxes surface
SELECT COUNT(id)
FROM process_table 
	WHERE (function ILIKE 'Filling of store'
	OR function ILIKE 'Release from store'
	OR function ILIKE 'In-catchment flux'
	OR function ILIKE 'In-store flux' 
	OR function ILIKE 'Release' )
	AND identifier ILIKE 'Surf.%';

-- # fluxes channel

SELECT COUNT(id)
FROM process_table 
	WHERE (function ILIKE 'Filling of store'
	OR function ILIKE 'Release from store'
	OR function ILIKE 'In-catchment flux'
	OR function ILIKE 'In-store flux' 
	OR function ILIKE 'Release' )
	AND identifier ILIKE 'Chan.%';

-- # fluxes subsurface
SELECT COUNT(id)
FROM process_table 
	WHERE (function ILIKE 'Filling of store'
	OR function ILIKE 'Release from store'
	OR function ILIKE 'In-catchment flux'
	OR function ILIKE 'In-store flux' 
	OR function ILIKE 'Release' )
	AND identifier ILIKE 'Sub.%';

-- # fluxes human
SELECT COUNT(id)
FROM process_table 
	WHERE (function ILIKE 'Filling of store'
	OR function ILIKE 'Release from store'
	OR function ILIKE 'In-catchment flux'
	OR function ILIKE 'In-store flux' 
	OR function ILIKE 'Release' )
	AND identifier ILIKE 'Human.%';

	-- # stores surface
	SELECT COUNT(id)
	FROM process_table 
		WHERE (function ILIKE 'Store'
		OR function ILIKE 'Store, temporary'
		OR function ILIKE 'Store characteristics, temporary'
		OR function ILIKE 'Store characteristics, permanent')
		AND identifier ILIKE 'Surf.%';

	-- # stores channel
	SELECT COUNT(id)
	FROM process_table 
		WHERE (function ILIKE 'Store'
		OR function ILIKE 'Store, temporary'
		OR function ILIKE 'Store characteristics, temporary'
		OR function ILIKE 'Store characteristics, permanent')
		AND identifier ILIKE 'Chan.%';

	-- # stores subsurface
	SELECT COUNT(id)
	FROM process_table 
		WHERE (function ILIKE 'Store'
		OR function ILIKE 'Store, temporary'
		OR function ILIKE 'Store characteristics, temporary'
		OR function ILIKE 'Store characteristics, permanent')
		AND identifier ILIKE 'Sub.%';

-- # total process
	SELECT COUNT(id)
	FROM process_table;

-- # Surface
	SELECT COUNT(id)
	FROM process_table 
		WHERE identifier ILIKE 'Surf%';

-- # Subsurface
	SELECT COUNT(id)
	FROM process_table 
		WHERE identifier ILIKE 'Sub%';

-- # Channel
	SELECT COUNT(id)
	FROM process_table 
		WHERE identifier ILIKE 'Chan%';

-- # Channel
	SELECT COUNT(id)
	FROM process_table 
		WHERE identifier ILIKE 'Human%';

-- Common process in subsurface process
-- # Groundwater
	SELECT COUNT(id)
	FROM process_table 
		WHERE identifier ILIKE 'Sub.GW%';

-- # Soil
	SELECT COUNT(id)
	FROM process_table 
		WHERE identifier ILIKE 'Sub.Soil%';

-- # Subsurface stormflow
	SELECT COUNT(id)
	FROM process_table 
		WHERE identifier ILIKE 'Sub.SSFlow%';

-- # S-Groundwater 
	SELECT COUNT(id)
	FROM process_table 
		WHERE identifier ILIKE 'Sub.GWSW%';


-- # Infiltration
	SELECT COUNT(id)
	FROM process_table 
		WHERE identifier ILIKE 'Surf.Inf%';

	SELECT identifier
	FROM process_table 
		WHERE identifier ILIKE 'Surf.Inf%'
		GROUP BY identifier;

-- # Overland flow
	SELECT COUNT(id)
	FROM process_table 
		WHERE identifier ILIKE 'Surf.Over%';

	SELECT identifier
	FROM process_table 
		WHERE identifier ILIKE 'Surf.Over%'
		GROUP BY identifier;


-- # Channel storage
	SELECT COUNT(id)
	FROM process_table 
		WHERE identifier ILIKE 'Chan.Store%';

	SELECT identifier
	FROM process_table 
		WHERE identifier ILIKE 'Chan.Store%'
		GROUP BY identifier;



-- # Class, Process, Subprocess
-- Count the # dots in the identifier
	SELECT 
	CHAR_LENGTH(identifier) - CHAR_LENGTH(REPLACE(identifier, '.', '')) AS process_level,
	COUNT(identifier)
	FROM process_table
	GROUP BY CHAR_LENGTH(identifier) - CHAR_LENGTH(REPLACE(identifier, '.', ''));

/*
 process_level | count
---------------+-------
             3 |   177
             2 |   292
             1 |    85
             */