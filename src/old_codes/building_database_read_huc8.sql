-- This script reads HUC8 watershed shapefile and relate it with perceptual model locations using PostGIS
-- Ryoko Araki 

-- 0. Build database using "building_database.py"

-- 1. Read HUC8 shapefiles into PostgreSQL 
-- Run the following command in the command prompt. 
-- Only need to read once when creating a new database
-- "C:\OSGeo4W64\bin\ogr2ogr.exe" -f "PostgreSQL" PG:"host=[HOST_NAME] port=[PORT_NUM] dbname=[DB_NAME] user=[USER_NAME] password=[PASSWROD]" -nln "perceptual_model.huc_watersheds" -nlt POLYGON -lco GEOMETRY_NAME=geom -lco FID=id -lco PRECISION=NO [PATH_TO_THE_SHAPEFILE]

-- c.f.
-- https://gdal.org/programs/ogr2ogr.html
-- "-f": output format name
-- "-nln <name>" Asign an alternate name to the new layer
-- "-nlt <type>" Degine the geometry type
-- "-lco" Layer creation option (format specific)

-- 2. Relate it with point geometry in the perceptual model

-- Log-in to PostgreSQL
-- "C:\Program Files\PostgreSQL\14\bin\psql.exe" -h [HOST_NAME] -U [USER_NAME] -d [DATABASE_NAME]
SET search_path TO public, perceptual_model;
SET CLIENT_ENCODING TO 'UTF8';

SELECT ST_SetSRID((SELECT geom FROM huc_watersheds LIMIT 1),4326) AS geom_4326;
UPDATE huc_watersheds SET geom = ST_Force_2D(geom);
UPDATE huc_watersheds SET geom = ST_SetSRID(geom, 4326);

UPDATE huc_watersheds SET geom = ST_Transform(geom, 4326) WHERE ST_SRID(geom) = 900914;;

ST_Transform(huc_watersheds.geom,4326);
ST_SRID(huc_watersheds.geom);
-- Create a column for the point geometry (perceptual model locations)
ALTER TABLE perceptual_model.locations
ADD COLUMN pt geometry(point, 4326);

SELECT ST_SRID((SELECT geom FROM huc_watersheds LIMIT 1));

WITH pt_geom AS (
	SELECT id, ST_SetSRID(ST_MakePoint(lon, lat), 4326) AS pt
	from perceptual_model.locations
	)
UPDATE perceptual_model.locations 
SET pt = pt_geom.pt
FROM pt_geom
WHERE pt_geom.id = locations.id;

-- Find the HUC8 polygon that a point is contained (PostGIS 'contains'?)
-- This takes a few minutes. 
-- TODO: convert original shapefile and delete ST_Transform to save execution time 
ALTER TABLE locations
ALTER COLUMN huc_watershed_id TYPE INTEGER USING huc_watershed_id::integer;

WITH joined_huc8_pt AS (
SELECT locations.id AS pt_id, huc_watersheds.id as huc8_id, huc_watersheds.huc8 AS huc8_code
FROM locations
JOIN huc_watersheds
ON ST_contains(ST_Transform(huc_watersheds.geom, 4326), locations.pt)
)
UPDATE locations
SET huc_watershed_id = joined_huc8_pt.huc8_id
FROM joined_huc8_pt
WHERE locations.id = joined_huc8_pt.pt_id;

-- Set up primary & foregin keys
ALTER TABLE locations
ADD FOREIGN KEY (huc_watershed_id)
REFERENCES huc_watersheds(id);

-- Just keep all original sources for now 
-- ALTER TABLE huc_watersheds DROP COLUMN lat, DROP COLUMN lon;

-- Check

SELECT locations.name, huc_watersheds.huc8
FROM locations
LEFT JOIN huc_watersheds
ON locations.huc_watershed_id = huc_watersheds.id;

-- 3. Check with QGIS 
-- done 



CREATE TEMP TABLE giant_table AS (
SELECT perceptual_model.id, 
        locations.name AS watershed_name, 
        huc_watersheds.huc8::text AS huc8_id
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
    LEFT JOIN huc_watersheds 
        ON locations.huc_watershed_id = huc_watersheds.id 
ORDER BY perceptual_model.id 
); 

CREATE TEMP TABLE giant_table_base AS ( 
 SELECT DISTINCT 
	 id,  
	 huc8_id AS huc_watershed_id
 FROM giant_table 
); 