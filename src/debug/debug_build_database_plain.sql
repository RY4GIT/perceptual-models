-- Use this code to debug if 1-1-build_database.ipynb don't work well

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
DROP COLUMN temp_id2,  
ADD COLUMN dummy_column NUMERIC DEFAULT 1; 
