[![Perceptual Model](https://github.com/RY4GIT/perceptual-model-arcgis-public/blob/main/readme/perceptual_model.PNG)](http://www.mcmillanhydrology.org/PerceptualModelDashboard.html)
# Perceptual Model Database
**Perceptual model** is defined as:
> An expert summary of the watershed and its runoff processes often supported by field observations. Perceptual models are often presented as a schematic figure, although such a figure will necessarily simplify the hydrologist's complex mental model (McMillan et al., 2022)

This repo contains a released version of the perceptual data model database, used for the manuscript under review **"Global patterns in observed hydrologic processes (McMillan et al.)"**. Currently our database holds **400 models** in the form of both text (269) and figure (131, including 63 identified in [McMillan et al., 2022](https://doi.org/10.1002/hyp.14845)) collected from hydrologic literature.

Visit **[the perceptual model interactive map](http://www.mcmillanhydrology.org/PerceptualModelDashboard.html)**  for the visualization :world_map:

## Installation/Getting Started
If you are only interested in the pre-built database and not the building process, you can download the database backup (SQLdump) from ```data/backup/*.backup```. Alternatively, check csv files under ```data``` directory.

The following explains the code used to build the Postgres database and webmap.

**1. Create your environment**
Use Conda to create an environment  
```
conda env create -f environment.yml
```
Or use the `environment_minimal.yml` if it fails.

**2. Building the perceptual model database**  
`src/` contains scripts to build the PostgreSQL database based on the raw data in the `data` directory.  
Run the following code in order:
- `0-debug_excelsheets.ipynb`
- `1-build_database.ipynb`

### Query database
`src/query` contains example scripts that can be used to query the database:
- `calc_stats.sql` holds query scripts to calculate statistics used in [the paper McMillan et al., 2022](https://doi.org/10.1002/hyp.14845)
 - Note that analysis for the manuscript "Global patterns in observed hydrologic processes (McMillan et al.)" was implemented using ArcGIS software
- Use `debug_built_database.sql` to debug the database if the SQL database or code (`1-build_database.ipynb`) are not working as expected

### Create webmap
`src/webmap` contains example scripts that are used to create [the ArcGIS interactive webmap](http://www.mcmillanhydrology.org/PerceptualModelDashboard.html).  
To initiate the webmap after building the SQL database:
- Run `init_create_webmap.ipynb` to initiate a webmap
- Or, run `update_webmap.ipynb` to update an existing webmap

### Create Figures
`Analysis_src/` contains scripts to recreate  the figures for McMillan et al., 2025, Nature Water.
`Analysis_data/` contains accompanying data files


## Resources
- [The database design (ER diagram)](https://dbdiagram.io/d/63f6895b296d97641d830705)
- [The hydrologic process taxonomy used in the analysis](http://mcmillanhydrology.org/ProcessTaxonomy/ProcessTaxonomyDiagram.html)

### Contact
We are looking to add more perceptual models to our database and develop better design codes for perceptual models through community effort! Both texts and illustrations are welcome.
- If you find perceptual models to be included in the map or want to discuss the model, contact:
    - **Hilary McMillan** (hmcmillan (at) sdsu (dot) edu)
- If you have questions about the technical details of the map, contact:
    - **Ryoko Araki** (raraki8159 (at) sdsu (dot) edu)

### Acknowledgement
I appreciate [Jessica](https://github.com/jlembury), Atsushi, and [Kyle](https://github.com/kylelmh) for helping me with the coding!

## Citation
```
@ARTICLE{McMillan2022,
  title   = {How do hydrologists perceive watersheds? A survey and analysis of perceptual model figures for experimental watersheds},
  author  = {Hilary McMillan and Ryoko Araki and Sebastian Gnann and Ross Woods and Thorsten Wagener},
  journal = {Hydrological Processes},
  doi     = {10.1002/hyp.14845},
  year    = {2022},
  volume  = {37},
  number  = {3},
  pages   = {e14845},
  url     = {https://doi.org/10.1002/hyp.14845}
}
```
