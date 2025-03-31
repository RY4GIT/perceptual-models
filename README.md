[![Perceptual Model](https://github.com/RY4GIT/perceptual-models/blob/main/readme/dashboard_v2.png)](https://hydroprocess.cuahsi.io/)
# Perceptual Model Database
**Perceptual model** is defined as:
> An expert summary of the watershed and its runoff processes often supported by field observations. Perceptual models are often presented as a schematic figure, although such a figure will necessarily simplify the hydrologist's complex mental model (McMillan et al., 2022)

This repository contains the released version of the perceptual data model database, used for **"Global patterns in observed hydrologic processes (McMillan et al., 2025)"** available at https://doi.org/10.1038/s44221-025-00407-w. Currently, our database holds **400 models** in the form of both text (269) and figures (131, including 63 identified in [McMillan et al., 2022](https://doi.org/10.1002/hyp.14845)) collected from hydrologic literature.

**Visit and explore the data using [the perceptual model interactive map](https://hydroprocess.cuahsi.io/)** :world_map: 

This dashboard is developed by [CUAHSI](https://www.cuahsi.org/) and made possible through their support.

## Installation/Getting Started
If you’re only interested in the pre-built database and not the building process, you can download the database backup (SQLdump) from ```data/backup/*.backup```. Alternatively, check the csv files in the ```data``` directory.

The following explains the code used to build the PostgreSQL database.

**1. Create your environment**
Use Conda to create an environment  
```
conda env create -f environment.yml
```
If that fails, use the `environment_minimal.yml` instead.

**2. Building the perceptual model database**  
The `src/` directory contains scripts to build the PostgreSQL database based on the raw data in the `data` directory.  
Run the following notebooks in order:
- `0-debug_excelsheets.ipynb`
- `1-build_database.ipynb`

### Query database
The `src/query` directory contains example scripts to query the database:
- `calc_stats.sql` includes queries to calculate statistics used in [McMillan et al., 2022](https://doi.org/10.1002/hyp.14845)
- Use `debug_built_database.sql` to  if the  SQL database or the notebook (`1-build_database.ipynb`) isn't working as expected

### Create Figures
Analysis for [McMillan et al., 2025](https://doi.org/10.1038/s44221-025-00407-w) was implemented using ArcGIS software, and the data and code are available at `Analysis_data` and `Analysis_src`.
- `Analysis_src/` contains scripts to recreate  the figures for McMillan et al., 2025, Nature Water.
- `Analysis_data/` contains accompanying data files

## Legacy Dashboard
If you're interested in exploring the previous version of the dashboard, you can access it here: **[Legacy ArcGIS Dashboard](https://sdsugeo.maps.arcgis.com/apps/dashboards/71e3e8cf745847928ecb7db8467b023b)**

`src/webmap` contains scripts used to generate this earlier version of the dashboard.

To initiate the webmap after building the SQL database:
- Run `init_create_webmap.ipynb` to initiate a webmap
- Or, run `update_webmap.ipynb` to update an existing webmap


## Resources
- [The database design (ER diagram)](https://dbdiagram.io/d/63f6895b296d97641d830705)
- [The hydrologic process taxonomy used in the analysis](http://mcmillanhydrology.org/ProcessTaxonomy/ProcessTaxonomyDiagram.html)

## Contact
We welcome contributions of additional perceptual models and ideas for improving perceptual model design through community collaboration! Both textual and illustrated models are appreciated.
- For questions about the models or data, contact:
    - **Hilary McMillan** (hmcmillan (at) sdsu (dot) edu)
- For technical questions about the database or ArcGIS dashboard, contact:
    - **Ryoko Araki** (raraki8159 (at) sdsu (dot) edu)
- For technical questions about the current dashboard, contact:
    - **Tony Castronova** (acastronova (at) cuahsi (dot) org)
    - **Irene Garousi-Nejad** (igarousi (at) cuahsi (dot) org)

## Acknowledgement
Special thanks to [Jessica](https://github.com/jlembury), Atsushi, and [Kyle](https://github.com/kylelmh) for their help with coding. We are grateful to the CUAHSI team for hosting the interactive dashboard and supporting this project.

## Citation
For perceptual model database (text and figures),
```
@ARTICLE{McMillan2025,
  title   = {Global patterns in observed hydrologic processes},
  author  = {Hilary McMillan and Ryoko Araki and Lauren Bolotin and Dohn-Hyun Kim and Gemma Coxon and Martyn Clark and Jan Seibert},
  journal = {Nature Water},
  doi     = {10.1038/s44221-025-00407-w},
  year    = {2025},
  url     = {https://doi.org/10.1038/s44221-025-00407-w}
}
```
Specifically for perceptual models in figure forms, 
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
