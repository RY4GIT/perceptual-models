# Interactive map: Perceptual Models Around the World by McMillan lab
Repository for **[the perceptual model interactive map](http://www.mcmillanhydrology.org/PerceptualModelDashboard.html)** :world_map:

Read our paper: 
    McMillan, H., Araki, R., Gnann, S., Woods, R., & Wagener, T. (n.d.). How do hydrologists perceive watersheds? A survey and analysis of perceptual model figures for experimental watersheds. Hydrological Processes. https://doi.org/10.1002/hyp.14845

![alt text](perceptual_model.PNG?raw=true)

# Links
- [The database design (ER diagram)](https://dbdiagram.io/d/63f6895b296d97641d830705)
- [The hydrologic process taxonomy used in the analysis](http://mcmillanhydrology.org/ProcessTaxonomy/ProcessTaxonomyDiagram.html)
- [Technical instruction on how this map is created](https://www.notion.so/raraki/Database-instruction-521fa8f832794cf0aade20bec576a725) (PostgreSQL + Python + Arc-GIS dashboard) 

# Code
## To update database & webmap
- `0-debug_excelsheets.ipynb`
- `1-build_database.ipynb`
- `2-update_webmap.ipynb`
## To initiate the webmap
- Run `0-debug_excelsheets.ipynb` and `1-build_database.ipynb` and then run the followings:
    - `init_create_webmap_private.ipynb`
    - `init_create_webmap_public.ipynb`
## Other utilities
- `calc_stats.sql` holds query script to calculate statistics used in [the paper](https://doi.org/10.1002/hyp.14845)
- `utils` directory holds some codes for standalone utilities
- `debug` holds some codes for debugging database. Use when `1-build_database.ipynb` SQL codes are not working as expected

# Contact
We are looking to add more perceptual models to the interactive map and intersted in developing better design codes for drawing perceptual models in the hydrologic community! 
- If you find perceptual models to be included in the map (both texts and illustrations are welcome!) or want to discuss the model
    - **Hilary McMillan** (hmcmillan (at) sdsu (dot) edu)
- If you have questions about the technical details of the map
    - **Ryoko Araki** (raraki8159 (at) sdsu (dot) edu)

# Acknowledgement
I appreciate [Jessica](https://github.com/jlembury), Atsushi, and Kyle for helping me with the coding!

