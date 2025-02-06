import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import gridspec
from ete3 import Tree, faces, AttrFace, TreeStyle, NodeStyle
import copy
import geopandas
import distinctipy
import itertools


# The function unique_taxonomy takes a list of taxonomy items and returns the unique items at each level of the taxonomy
def unique_taxonomy(taxonomy_list):
    # Define empty lists to hold items from each level of taxonomy
    domain_list = []
    class_list = []
    process_list = []
    subprocess_list = []

    # the taxonomy list is a comma separated string, turn it into a series
    taxonomy_series = taxonomy_list.split(',')

    for taxonomy_item in taxonomy_series:
        # if nothing in string (stores or fluxes were blank) skip to next item
        if taxonomy_item == " ":
            continue
        if "Human" in taxonomy_item:
            continue

        # Split the string using the period character as the delimiter
        split_taxonomy_item = taxonomy_item.split('.')
        domain_list.append(split_taxonomy_item[0].strip())
        if len(split_taxonomy_item) > 1:
            class_list.append(split_taxonomy_item[0].strip() + '.' + split_taxonomy_item[1].strip())
        if len(split_taxonomy_item) > 2:
            process_list.append(
                split_taxonomy_item[0].strip() + '.' + split_taxonomy_item[1].strip() + '.' + split_taxonomy_item[
                    2].strip())
        if len(split_taxonomy_item) > 3:
            subprocess_list.append(
                split_taxonomy_item[0].strip() + '.' + split_taxonomy_item[1].strip() + '.' + split_taxonomy_item[
                    2].strip() + '.' + split_taxonomy_item[3].strip())

    # Return only the unique taxonomy hashtags from each level of the taxonomy
    domain_unique = list(set(domain_list))
    class_unique = list(set(class_list))
    process_unique = list(set(process_list))
    subprocess_unique = list(set(subprocess_list))

    return domain_unique, class_unique, process_unique, subprocess_unique


#Output folder
output_folder_rev = 'C:/folder/'

# Specify the file path with the database output
file_path = 'C:/folder/Analysis_data/ProcessDatabase3.csv'

# Specify the file path with the biome info for each watershed
file_biomes = 'C:/folder/Analysis_data/Watersheds_Biomes.csv'

# Specify the file path with the aridity info for each watershed
file_aridity = 'C:/folder/Analysis_data/Watersheds_Aridity.csv'

# Specify the file with the watershed landforms for each watershed
file_landforms = 'C:/folder/Analysis_data/Watersheds_Landforms.csv'

# Specify the file with the slope and soil thickness for each watershed
file_soil_slope = 'C:/folder/Analysis_data/Watersheds_Soil_Slope.csv'

# Specify the number of biomes
num_biomes = 14

# -----------------Import files with database information and watershed properties -------------------

# Import the database file
try:
    df = pd.read_csv(file_path)
    print("Database file imported successfully.")
except FileNotFoundError:
    print(f"File not found: {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")

# Import csv with biome numbers
try:
    df_biomes = pd.read_csv(file_biomes)
    print("Biome file imported successfully.")
except FileNotFoundError:
    print(f"File not found: {file_biomes}")
except Exception as e:
    print(f"An error occurred: {e}")

# Import csv with aridity
try:
    df_aridity = pd.read_csv(file_aridity)
    print("Aridity file imported successfully.")
except FileNotFoundError:
    print(f"File not found: {file_aridity}")
except Exception as e:
    print(f"An error occurred: {e}")

# Import csv with landforms
try:
    df_landforms = pd.read_csv(file_landforms)
    print("Landforms file imported successfully.")
except FileNotFoundError:
    print(f"File not found: {file_landforms}")
except Exception as e:
    print(f"An error occurred: {e}")

# Import csv with soil thickness and slope
try:
    df_soil_slope = pd.read_csv(file_soil_slope)
    print("Soil and Slope file imported successfully.")
except FileNotFoundError:
    print(f"File not found: {file_soil_slope}")
except Exception as e:
    print(f"An error occurred: {e}")

# ----------------------------- Read imported files to extract watershed information --------------------------

# Extract the store hashtag column and flux hashtag columns using the indexing operator []
store_hashtag = df['store_id_list']
flux_hashtag = df['flux_id_list']

# Set nans to empty string
store_hashtag = store_hashtag.fillna(" ")
flux_hashtag = flux_hashtag.fillna(" ")

# Get the citations and extract the years
citation = df['citation']
citation_years = []
for cite in citation.items():
    cite_split = ["".join(x) for _, x in itertools.groupby(cite[1], key=str.isdigit)]
    cite_year = cite_split[1]
    citation_years.append(cite_year)

# Make a bar chart of years
fig, ax = plt.subplots(figsize=(10, 7))
ax.hist(pd.to_numeric(citation_years), bins=[1970, 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2023])
plt.show()

# Get locations of the watersheds
watershed_lat = df['lat']
watershed_lon = df['lon']

# Get aridity of the watersheds
aridity = df_aridity['aridity']

# Get biomes numbers and names of the watersheds
biome_numbers = df_biomes['BIOME_NUM']
biome_names = df_biomes['BIOME_NAME']

# Get areas of the watersheds
watershed_area = df_biomes['area_km2']

# Get the landform categories for the watersheds
landform = df_landforms['LF_ClassNa']
landcover = df_landforms['LC_ClassNa']
tempclass = df_landforms['Temp_Class']
moistureclass = df_landforms['Moisture_C']

# Get the soil and slope values for the watersheds
soil_thickness = df_soil_slope['average_soil_and_sedimentary_deposit_thickness']
slope = df_soil_slope['slope_1KMmd_GMTEDmd']


# --------------- Create hierarchical tree structures to describe database ------------------------------------

# ----- TREES PER BIOME #######################################################################

# Regular biome names
biomes_index = ['Tropical Moist Broadleaf Forest', 'Tropical Dry Broadleaf Forest', 'Tropical Conifer Forest',
                'Temperate Broadleaf Forest', 'Temperate Conifer Forest', 'Boreal Forest', 'Tropical Grassland',
                'Temperate Grassland', 'Flooded Grassland', 'Montane Grassland', 'Tundra', 'Mediterranean Forest',
                'Desert', 'Mangroves']

# Original full biome names
biomes_index_full = ['Tundra', 'Deserts & Xeric Shrublands', 'Montane Grasslands & Shrublands',
                     'Temperate Grasslands, Savannas & Shrublands',
                     'Tropical & Subtropical Grasslands, Savannas & Shrublands',
                     'Flooded Grasslands & Savannas','Boreal Forests/Taiga', 'Mediterranean Forests, Woodlands & Scrub',
                     'Temperate Broadleaf & Mixed Forests', 'Temperate Conifer Forests',
                     'Tropical & Subtropical Dry Broadleaf Forests',
                     'Tropical & Subtropical Moist Broadleaf Forests', 'Tropical & Subtropical Coniferous Forests',
                     'Mangroves']

# Very short names for figures
biomes_index_short = ['Tundra', 'Desert', 'Montane\nGrassland', 'Temperate\nGrassland', 'Tropical\nGrassland',
                      'Flooded\nGrassland', 'Boreal\nForest', 'Mediterranean\nForest', 'Temperate\nBroadleaf Forest',
                      'Temperate\nConifer Forest',
                      'Tropical Dry\nBroadleaf Forest', 'Tropical Moist\nBroadleaf Forest', 'Tropical\nConifer Forest',
                      'Mangroves']

df_biomes_histogram = pd.DataFrame(np.array(np.zeros((num_biomes, 7))),
                                   columns=['Regional Groundwater', 'Groundwater',
                                            'Subsurface Stormflow', 'Soil',
                                            'Near Surface', 'Surface', 'Canopy'],
                                   index=biomes_index)

# Initialize dataframe to hold number of processes per biome for pie charts
df_biomes_pie = pd.DataFrame(np.array(np.zeros((num_biomes, 8))),
                                   columns=['Overland Flow', 'Surface', 'Cold region',
                                            'Soil', 'Subsurface Stormflow', 'Groundwater',
                                            'Channel Flow', 'Channel Storage'],
                                   index=biomes_index)

# This will keep the number of records not just the number of different processes
df_biomes_pie_rec = pd.DataFrame(np.array(np.zeros((num_biomes, 8))),
                                   columns=['Overland Flow', 'Surface', 'Cold region',
                                            'Soil', 'Subsurface Stormflow', 'Groundwater',
                                            'Channel Flow', 'Channel Storage'],
                                   index=biomes_index)

# Initialize list to hold trees
treelist_biome = []
for i in range(0, num_biomes):
    treelist_biome.append(Tree())

# Set up figure to hold process types per biome, organized in a triangle
figBiomeTree = plt.figure(123, figsize=(15, 5))
ax123a = plt.subplot2grid((1, 3), (0, 0))
ax123b = plt.subplot2grid((1, 3), (0, 1))
ax123c = plt.subplot2grid((1, 3), (0, 2))

# Initialize dataframe to hold number of watersheds per biome
biome_watersheds = pd.DataFrame(np.array(np.zeros((num_biomes, 1))),
                                columns=['Watersheds'],
                                index=biomes_index_full)

# Create tree from each cluster to visualize processes included
for i in range(0, num_biomes):
    # Get all the strings from this biome
    clusterindex = np.where(biome_numbers == i + 1)
    clustersize = clusterindex[0].size

    # If there are no watersheds in this biome, move to next biome
    if clustersize == 0:
        continue

    # Create empty list to store the strings
    cluster_storesfluxes = []

    for storeflux_list in pd.concat([store_hashtag[clusterindex[0]], flux_hashtag[clusterindex[0]]]):
        # Get rid of duplicates within sites
        storeflux = storeflux_list.split(',')
        storefluxstrip = [x.strip() for x in storeflux]
        storeflux_unique = list(set(storefluxstrip))
        storeflux_unique = [x for x in storeflux_unique if 'Human' not in x]
        # Add these stores to the list of stores and fluxes in this biome
        cluster_storesfluxes.extend(storeflux_unique)

    # Initialize a tree to hold the biome stores and fluxes
    t = treelist_biome[i]
    t.add_features(num_instances=len(cluster_storesfluxes))
    # Add the Surf, Sub, Chan children to get these in the right order
    tadd = t.add_child(name="Surf")
    tadd.num_instances = 0
    tadd = t.add_child(name="Sub")
    tadd.num_instances = 0
    tadd = t.add_child(name="Chan")
    tadd.num_instances = 0

    # Iterate over biome stores and fluxes, adding each to tree
    for hashtag in cluster_storesfluxes:
        if len(hashtag) == 0:
            continue
        hashpartlist = hashtag.split('.')
        for hash_i in range(0, len(hashpartlist)):
            # Get full taxonomy hashtag
            hash_full = '.'.join(hashpartlist[0:hash_i + 1])
            # Get the parent hashtag
            hash_full_parent = '.'.join(hashpartlist[0:hash_i])

            # Find out whether this taxonomy item is already in the tree
            treenode = t.search_nodes(name=hash_full)

            if len(treenode) != 0:
                # If node already in tree, increase attribute num_instances by 1
                treenode = treenode[0]
                try:
                    treenode.num_instances = treenode.num_instances + 1
                except:
                    print("num instances failed")
            else:
                # If node is not in tree, add the node
                # Get the parent node
                if len(hash_full_parent) == 0:
                    # Then this is the tree root
                    parentnode = t
                else:
                    parentnode = t.search_nodes(name=hash_full_parent)[0]
                # Add the node
                newnode = parentnode.add_child(name=hash_full)
                # Record that so far we only have once instance by adding attribute
                newnode.add_features(num_instances=1)

    # Fill in histogram with number of instances of each process
    num_canopy = 0
    for procname in ['Surf.ET.Evap.Canopy', 'Surf.Int', 'Suf.Snow.Canopy', 'Surf.Snow.Subl.Canopy']:
        procnode = t.search_nodes(name=procname)
        if len(procnode) > 0: num_canopy = num_canopy + procnode[0].num_instances
    df_biomes_histogram.loc[biomes_index[i], 'Canopy'] = num_canopy

    num_surface = 0
    procnode = t.search_nodes(name='Surf')
    if len(procnode) > 0: num_surface = procnode[0].num_instances - num_canopy
    df_biomes_histogram.loc[biomes_index[i], 'Surface'] = num_surface

    num_nearsurface = 0
    for procname in ['Sub.Soil.Store.Organ', 'Sub.SSFlow.Organ']:
        procnode = t.search_nodes(name=procname)
        if len(procnode) > 0: num_nearsurface = num_nearsurface + procnode[0].num_instances
    df_biomes_histogram.loc[biomes_index[i], 'Near Surface'] = num_nearsurface

    num_soil = 0
    procnode = t.search_nodes(name='Sub.Soil')
    if len(procnode) > 0: num_soil = num_soil + procnode[0].num_instances
    procnode = t.search_nodes(name='Sub.Soil.Store.Organ')
    if len(procnode) > 0: num_soil = num_soil - procnode[0].num_instances
    df_biomes_histogram.loc[biomes_index[i], 'Soil'] = num_soil

    num_sssf = 0
    for procname in ['Sub.SSFlow']:  # , 'Sub.GW.Store.Perch']:
        procnode = t.search_nodes(name=procname)
        if len(procnode) > 0: num_sssf = num_sssf + procnode[0].num_instances
    procnode = t.search_nodes(name='Sub.SSFlow.Organ')
    if len(procnode) > 0: num_sssf = num_sssf - procnode[0].num_instances
    df_biomes_histogram.loc[biomes_index[i], 'Subsurface Stormflow'] = num_sssf

    num_regionalgw = 0
    for procname in ['Sub.GW.Store.Region', 'Sub.GW.Flow.Region', 'Sub.GW.Loss']:
        procnode = t.search_nodes(name=procname)
        if len(procnode) > 0: num_regionalgw = num_regionalgw + procnode[0].num_instances
    df_biomes_histogram.loc[biomes_index[i], 'Regional Groundwater'] = num_regionalgw

    num_gw = 0
    procnode = t.search_nodes(name='Sub.GW')
    if len(procnode) > 0: num_gw = num_gw + procnode[0].num_instances
    num_gw = num_gw - num_regionalgw
    df_biomes_histogram.loc[biomes_index[i], 'Groundwater'] = num_gw

    # Create a new tree that removes branches where num_instances < 5
    tpruned = copy.deepcopy(t)
    keep_nodes = []
    for n in tpruned.traverse():
        if n.num_instances >= clustersize / 8:
            keep_nodes.append(n)
    tpruned.prune(keep_nodes)
    # tpruned.show()

    # Sort each of the Surf/Sub/Chan branches by number of instances
    for node in tpruned.children:
        node.ladderize(direction=1)

    # Use pruned tree to fill in histogram with number of instances of each process - pie charts
    num_of = 0
    num_of_rec = 0
    procnode = tpruned.search_nodes(name='Surf.Over')
    if len(procnode) > 0:
        num_of = max(1, len(procnode[0].children))
        num_of_rec = procnode[0].num_instances
    df_biomes_pie.loc[biomes_index[i], 'Overland Flow'] = num_of
    df_biomes_pie_rec.loc[biomes_index[i], 'Overland Flow'] = num_of_rec

    num_surface = 0
    num_surface_rec = 0
    for procname in ['Surf.ET', 'Surf.Int', 'Surf.Water', 'Surf.Inf']:
        procnode = tpruned.search_nodes(name=procname)
        if len(procnode) > 0:
            num_surface = num_surface + max(1, len(procnode[0].children))
            num_surface_rec = num_surface_rec + procnode[0].num_instances
    df_biomes_pie.loc[biomes_index[i], 'Surface'] = num_surface
    df_biomes_pie_rec.loc[biomes_index[i], 'Surface'] = num_surface_rec

    num_cold = 0
    num_cold_rec = 0
    for procname in ['Surf.Snow', 'Surf.Glac', 'Surf.Frozen']:
        procnode = tpruned.search_nodes(name=procname)
        if len(procnode) > 0:
            num_cold = num_cold + max(1, len(procnode[0].children))
            num_cold_rec = num_cold_rec + procnode[0].num_instances
    df_biomes_pie.loc[biomes_index[i], 'Cold region'] = num_cold
    df_biomes_pie_rec.loc[biomes_index[i], 'Cold region'] = num_cold_rec

    num_sssf = 0
    num_sssf_rec = 0
    procnode = tpruned.search_nodes(name='Sub.SSFlow')
    if len(procnode) > 0:
        num_sssf = max(1, len(procnode[0].children))
        num_sssf_rec = procnode[0].num_instances
    df_biomes_pie.loc[biomes_index[i], 'Subsurface Stormflow'] = num_sssf
    df_biomes_pie_rec.loc[biomes_index[i], 'Subsurface Stormflow'] = num_sssf_rec

    num_soil = 0
    num_soil_rec = 0
    procnode = tpruned.search_nodes(name='Sub.Soil')
    if len(procnode) > 0:
        num_soil = max(1, len(procnode[0].children))
        num_soil_rec = procnode[0].num_instances
    df_biomes_pie.loc[biomes_index[i], 'Soil'] = num_soil
    df_biomes_pie_rec.loc[biomes_index[i], 'Soil'] = num_soil_rec

    num_gw = 0
    num_gw_rec = 0
    for procname in ['Sub.GW', 'Sub.GWSW']:
        procnode = tpruned.search_nodes(name=procname)
        if len(procnode) > 0:
            num_gw = num_gw + max(1, len(procnode[0].children))
            num_gw_rec = num_gw_rec + procnode[0].num_instances
    df_biomes_pie.loc[biomes_index[i], 'Groundwater'] = num_gw
    df_biomes_pie_rec.loc[biomes_index[i], 'Groundwater'] = num_gw_rec

    num_chf = 0
    num_chf_rec = 0
    for procname in ['Chan.Flow', 'Chan.Atten', 'Chan.Hypor']:
        procnode = tpruned.search_nodes(name=procname)
        if len(procnode) > 0:
            num_chf = num_chf + max(1, len(procnode[0].children))
            num_chf_rec = num_chf_rec + procnode[0].num_instances
    df_biomes_pie.loc[biomes_index[i], 'Channel Flow'] = num_chf
    df_biomes_pie_rec.loc[biomes_index[i], 'Channel Flow'] = num_chf_rec

    num_chs = 0
    num_chs_rec = 0
    for procname in ['Chan.Store', 'Chan.Extend', 'Chan.Int']:
        procnode = tpruned.search_nodes(name=procname)
        if len(procnode) > 0:
            num_chs = num_chs + max(1, len(procnode[0].children))
            num_chs_rec = num_chs_rec + procnode[0].num_instances
    df_biomes_pie.loc[biomes_index[i], 'Channel Storage'] = num_chs
    df_biomes_pie_rec.loc[biomes_index[i], 'Channel Storage'] = num_chs_rec

    # Store the number of watersheds per biome in an array
    biome_watersheds.at[biome_names[clusterindex[0][0]],'Watersheds'] = clustersize


# --------FIGURE 3 ----------Make these into pie charts arranged in a biome triangle
numpie = 11
figbt = plt.figure(75, figsize=(11, 8))
gsbt1 = gridspec.GridSpec(4, 4)
gsbt2 = gridspec.GridSpec(4, 3)
gsbt3 = gridspec.GridSpec(4, 6)

labels = ['Overland Flow', 'Surface Process', 'Snow & ice Process',
          'Soil', 'Subsurface Stormflow', 'Groundwater',
          'Channel Flow', 'Channel Storage']
colors = ['lightsalmon', 'tomato', 'red', 'skyblue', 'deepskyblue', 'dodgerblue', 'darkorchid', 'purple']

selected_biomes = [1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 13]
selected_biomes1 = [11]
selected_biomes2 = [6, 10]
selected_biomes3 = [4, 5, 12, 8]
selected_biomes4 = [1, 2, 7, 13]

selected_titles = ['Tropical Moist\nBroadleaf Forest', 'Tropical Dry\nBroadleaf Forest', 'Tropical Conifer Forest',
                   'Temperate\nBroadleaf Forest', 'Temperate\nConifer Forest', 'Boreal Forest', 'Tropical Grassland',
                   'Temperate\nGrassland', 'Flooded Grassland', 'Montane Grassland', 'Tundra', 'Mediterranean\nForest',
                   'Desert', 'Mangroves']

padtitle = 0.9

# First row just has tundra, on offset axes
for ipie in range(0, 1):
    biome = selected_biomes1[ipie] - 1
    pie_sizes = df_biomes_pie_rec.loc[biomes_index[biome]]
    # Find process that do have records
    pie_sizes_positive = pie_sizes > 0
    filtered_pie_sizes = [i for (i, v) in zip(pie_sizes, pie_sizes_positive) if v]
    filtered_labels = [i for (i, v) in zip(labels, pie_sizes_positive) if v]
    filtered_colors = [i for (i, v) in zip(colors, pie_sizes_positive) if v]
    axbt2 = plt.subplot(gsbt2[1])
    axbt2.set_title(selected_titles[biome],y=padtitle)
    axbt2.pie(filtered_pie_sizes, colors=filtered_colors)

# Second row has sub-arctic
for ipie in range(0, 2):
    biome = selected_biomes2[ipie] - 1
    pie_sizes = df_biomes_pie_rec.loc[biomes_index[biome]]
    # Find process that do have records
    pie_sizes_positive = pie_sizes > 0
    filtered_pie_sizes = [i for (i, v) in zip(pie_sizes, pie_sizes_positive) if v]
    filtered_labels = [i for (i, v) in zip(labels, pie_sizes_positive) if v]
    filtered_colors = [i for (i, v) in zip(colors, pie_sizes_positive) if v]
    axbt1 = plt.subplot(gsbt1[5 + ipie])
    axbt1.set_title(selected_titles[biome],y=padtitle)
    axbt1.pie(filtered_pie_sizes, colors=filtered_colors)

# Third rows have 4 biomes slightly compressed
for ipie in range(0, 4):
    biome = selected_biomes3[ipie] - 1
    pie_sizes = df_biomes_pie_rec.loc[biomes_index[biome]]
    # Find process that do have records
    pie_sizes_positive = pie_sizes > 0
    filtered_pie_sizes = [i for (i, v) in zip(pie_sizes, pie_sizes_positive) if v]
    filtered_labels = [i for (i, v) in zip(labels, pie_sizes_positive) if v]
    filtered_colors = [i for (i, v) in zip(colors, pie_sizes_positive) if v]
    axbt1 = plt.subplot(gsbt3[13 + ipie])
    axbt1.set_title(selected_titles[biome],y=padtitle)
    patches, texts = axbt1.pie(filtered_pie_sizes, colors=filtered_colors)

# Fourth rows has all other biomes
for ipie in range(0, 4):
    biome = selected_biomes4[ipie] - 1
    pie_sizes = df_biomes_pie_rec.loc[biomes_index[biome]]
    # Find process that do have records
    pie_sizes_positive = pie_sizes > 0
    filtered_pie_sizes = [i for (i, v) in zip(pie_sizes, pie_sizes_positive) if v]
    filtered_labels = [i for (i, v) in zip(labels, pie_sizes_positive) if v]
    filtered_colors = [i for (i, v) in zip(colors, pie_sizes_positive) if v]
    axbt1 = plt.subplot(gsbt1[12 + ipie])
    axbt1.set_title(selected_titles[biome],y=padtitle)
    axbt1.pie(filtered_pie_sizes, colors=filtered_colors)

# Add a legend off to the side
figbt.legend(patches, labels, loc="upper left")

plt.subplots_adjust(right=0.95, left=0.05)
plt.savefig(f"{output_folder_rev}Figure3_pie_chart_triangle.svg")


# --------------FIGURE 1 ---------- inset plots of biomes and years

fig44 = plt.figure(44, figsize=(12, 4))
gs = gridspec.GridSpec(1, 2, width_ratios=[1, 1.7])
ax44 = plt.subplot(gs[0])

# Make a bar chart of years
ax44.hist(pd.to_numeric(citation_years), bins=[1970, 1975, 1980, 1985, 1990, 1995, 2000, 2005, 2010, 2015, 2020, 2025],
        rwidth = 0.8, color='grey')
ax44.set_title('b   Process Descriptions By Year')

# Make a bar chart of biomes
ax45 = plt.subplot(gs[1])
biome_watersheds.plot(kind='bar', ax=ax45, color='grey', legend=False, width=0.63, bottom=0.3)
# Replace long biome names with short names
ax45.set_xticklabels(biomes_index_short, ma='right')
plt.subplots_adjust(bottom=0.32, right=0.95, left=0.05)

ax45.set_title('c   Process Descriptions By Biome')
plt.savefig(f"{output_folder_rev}Figure1_b_c_watersheds_by year_biome_400.svg")

# TREES PER ARIDITY CLASS #############################################################################

# Initialize list to hold trees for each aridity class
treelist_aridity = []
num_aridity = 6
for i in range(0, num_aridity):
    treelist_aridity.append(Tree())

# Create dataframe as histogram to hold aridity information
aridity_index = ['-1 - -0.66', '-0.66 - -0.33', '-0.33 - 0',
                 '0 - 0.33', '0.33 - 0.66', '0.66 - 1']

columns_original=['Regional Groundwater', 'Groundwater', 'Subsurface Stormflow', 'Soil', 'Near Surface', 'Surface',
                  'Canopy']
columns_dunne=['Subsurface Stormflow', 'Saturation Excess and Return Flow', 'Infiltration Excess']
columns_use = columns_original
col_num_arid = 7

df_aridity_histogram = pd.DataFrame(np.array(np.zeros((num_aridity, col_num_arid))), columns=columns_use,
                                    index=aridity_index)
aridity_totals = []

# Create tree from each cluster to visualize processes included
for i in range(0, num_aridity):
    # Get all the strings from this aridity class
    aridity_min = -1 + i * (2 / num_aridity)
    aridity_max = -1 + (i + 1) * (2 / num_aridity)
    clusterindex = np.where(np.logical_and(aridity > aridity_min, aridity < aridity_max))

    clustersize = clusterindex[0].size
    print(f"Aridity size class: {aridity_index[i]} has {clustersize} watersheds")
    aridity_totals.append(clustersize)

    # If there are no watersheds in this class, move to next class
    if clustersize == 0:
        continue

    # Create empty list to store the strings
    cluster_storesfluxes = []

    for storeflux_list in pd.concat([store_hashtag[clusterindex[0]], flux_hashtag[clusterindex[0]]]):
        # Get rid of duplicates within sites
        storeflux = storeflux_list.split(',')
        storefluxstrip = [x.strip() for x in storeflux]
        storeflux_unique = list(set(storefluxstrip))
        storeflux_unique = [x for x in storeflux_unique if 'Human' not in x]
        # Add these stores to the list of stores and fluxes in this class
        cluster_storesfluxes.extend(storeflux_unique)

    # Initialize a tree to hold the class stores and fluxes
    t = treelist_aridity[i]
    t.add_features(num_instances=len(cluster_storesfluxes))
    # Add the Surf, Sub, Chan children to get these in the right order
    tadd = t.add_child(name="Surf")
    tadd.num_instances = 0
    tadd = t.add_child(name="Sub")
    tadd.num_instances = 0
    tadd = t.add_child(name="Chan")
    tadd.num_instances = 0

    # Iterate over class stores and fluxes, adding each to tree
    for hashtag in cluster_storesfluxes:
        if len(hashtag) == 0:
            continue
        hashpartlist = hashtag.split('.')
        for hash_i in range(0, len(hashpartlist)):
            # Get full taxonomy hashtag
            hash_full = '.'.join(hashpartlist[0:hash_i + 1])
            # Get the parent hashtag
            hash_full_parent = '.'.join(hashpartlist[0:hash_i])

            # Find out whether this taxonomy item is already in the tree
            treenode = t.search_nodes(name=hash_full)

            if len(treenode) != 0:
                # If node already in tree, increase attribute num_instances by 1
                treenode = treenode[0]
                try:
                    treenode.num_instances = treenode.num_instances + 1
                except:
                    print("num instances failed")
            else:
                # If node is not in tree, add the node
                # Get the parent node
                if len(hash_full_parent) == 0:
                    # Then this is the tree root
                    parentnode = t
                else:
                    parentnode = t.search_nodes(name=hash_full_parent)[0]
                # Add the node
                newnode = parentnode.add_child(name=hash_full)
                # Record that so far we only have once instance by adding attribute
                newnode.add_features(num_instances=1)

    if col_num_arid == 7:

        # Fill in histogram with number of instances of each process
        num_canopy = 0
        for procname in ['Surf.ET.Evap.Canopy', 'Surf.Int', 'Suf.Snow.Canopy', 'Surf.Snow.Subl.Canopy']:
            procnode = t.search_nodes(name=procname)
            if len(procnode) > 0:
                num_canopy = num_canopy + procnode[0].num_instances
        df_aridity_histogram.loc[aridity_index[i], 'Canopy'] = num_canopy

        num_surface = 0
        procnode = t.search_nodes(name='Surf')
        if len(procnode) > 0:
            num_surface = procnode[0].num_instances - num_canopy
        df_aridity_histogram.loc[aridity_index[i], 'Surface'] = num_surface

        num_nearsurface = 0
        for procname in ['Sub.Soil.Store.Organ', 'Sub.SSFlow.Organ']:
            procnode = t.search_nodes(name=procname)
            if len(procnode) > 0:
                num_nearsurface = num_nearsurface + procnode[0].num_instances
        df_aridity_histogram.loc[aridity_index[i], 'Near Surface'] = num_nearsurface

        num_soil = 0
        procnode = t.search_nodes(name='Sub.Soil')
        if len(procnode) > 0:
            num_soil = num_soil + procnode[0].num_instances
        procnode = t.search_nodes(name='Sub.Soil.Store.Organ')
        if len(procnode) > 0:
            num_soil = num_soil - procnode[0].num_instances
        df_aridity_histogram.loc[aridity_index[i], 'Soil'] = num_soil

        num_sssf = 0
        for procname in ['Sub.SSFlow']:  # , 'Sub.GW.Store.Perch']:
            procnode = t.search_nodes(name=procname)
            if len(procnode) > 0:
                num_sssf = num_sssf + procnode[0].num_instances
        procnode = t.search_nodes(name='Sub.SSFlow.Organ')
        if len(procnode) > 0:
            num_sssf = num_sssf - procnode[0].num_instances
        df_aridity_histogram.loc[aridity_index[i], 'Subsurface Stormflow'] = num_sssf

        num_regionalgw = 0
        for procname in ['Sub.GW.Store.Region', 'Sub.GW.Flow.Region', 'Sub.GW.Loss']:
            procnode = t.search_nodes(name=procname)
            if len(procnode) > 0:
                num_regionalgw = num_regionalgw + procnode[0].num_instances
        df_aridity_histogram.loc[aridity_index[i], 'Regional Groundwater'] = num_regionalgw

        num_gw = 0
        procnode = t.search_nodes(name='Sub.GW')
        if len(procnode) > 0:
            num_gw = num_gw + procnode[0].num_instances
        num_gw = num_gw - num_regionalgw
        df_aridity_histogram.loc[aridity_index[i], 'Groundwater'] = num_gw


    elif col_num_arid == 3:

        num_sssf = 0
        for procname in ['Sub.SSFlow']:  # , 'Sub.GW.Store.Perch']:
            procnode = t.search_nodes(name=procname)
            if len(procnode) > 0:
                num_sssf = num_sssf + procnode[0].num_instances
        procnode = t.search_nodes(name='Sub.SSFlow.Organ')
        if len(procnode) > 0:
            num_sssf = num_sssf - procnode[0].num_instances
        df_aridity_histogram.loc[aridity_index[i], 'Subsurface Stormflow'] = num_sssf

        num_ie = 0
        procnode = t.search_nodes(name='Surf.Over.IE')
        if len(procnode) > 0:
            num_ie = procnode[0].num_instances
        df_aridity_histogram.loc[aridity_index[i], 'Infiltration Excess'] = num_ie

        num_se = 0
        for procname in ['Surf.Over.SE', 'Sub.GW.Ret']:
            procnode = t.search_nodes(name=procname)
            if len(procnode) > 0:
                num_se = num_se + procnode[0].num_instances
        df_aridity_histogram.loc[aridity_index[i], 'Saturation Excess and Return Flow'] = num_se



# TREES PER SOIL THICKNESS CLASS #############################################################################

# Initialize list to hold trees for each aridity class
treelist_soil = []
num_soil = 5
columns_of_sssf = ['Subsurface Stormflow', 'Overland Flow']
columns_use = columns_of_sssf
col_num = 2

for i in range(0, num_soil):
    treelist_soil.append(Tree())

# Create dataframe as histogram to hold aridity information
soil_index = ['0.01 - 1', '1 - 1.5', '1.5 - 3', '3 - 6', '6 - 100']
soil_points = [0.01, 1, 1.5, 3, 6, 100]

df_soil_histogram = pd.DataFrame(np.array(np.zeros((num_soil, col_num))), columns=columns_use, index=soil_index)

# Create tree from each soil thickness class to visualize processes included
for i in range(0, num_soil):
    soil_min = soil_points[i]
    soil_max = soil_points[i+1]
    # Only humid watersheds (aridity > 0) and soil thickness within band
    clusterindex = np.where(np.logical_and(aridity > 0,
                                              np.logical_and(soil_thickness >= soil_min, soil_thickness < soil_max)))

    clustersize = clusterindex[0].size
    print(f"Soil thickness class: {soil_index[i]} has {clustersize} watersheds")

    # If there are no watersheds in this biome, move to next biome
    if clustersize == 0:
        continue

    # Create empty list to store the strings
    cluster_storesfluxes = []

    for storeflux_list in pd.concat([store_hashtag[clusterindex[0]], flux_hashtag[clusterindex[0]]]):
        # Get rid of duplicates within sites
        storeflux = storeflux_list.split(',')
        storefluxstrip = [x.strip() for x in storeflux]
        storeflux_unique = list(set(storefluxstrip))
        storeflux_unique = [x for x in storeflux_unique if 'Human' not in x]
        # Add these stores to the list of stores and fluxes in this cluster
        cluster_storesfluxes.extend(storeflux_unique)

    # Initialize a tree to hold the cluster stores and fluxes
    t = treelist_soil[i]
    t.add_features(num_instances=len(cluster_storesfluxes))
    # Add the Surf, Sub, Chan children to get these in the right order
    tadd = t.add_child(name="Surf")
    tadd.num_instances = 0
    tadd = t.add_child(name="Sub")
    tadd.num_instances = 0
    tadd = t.add_child(name="Chan")
    tadd.num_instances = 0

    # Iterate over cluster stores and fluxes, adding each to tree
    for hashtag in cluster_storesfluxes:
        if len(hashtag) == 0:
            continue
        hashpartlist = hashtag.split('.')
        for hash_i in range(0, len(hashpartlist)):
            # Get full taxonomy hashtag
            hash_full = '.'.join(hashpartlist[0:hash_i + 1])
            # Get the parent hashtag
            hash_full_parent = '.'.join(hashpartlist[0:hash_i])

            # Find out whether this taxonomy item is already in the tree
            treenode = t.search_nodes(name=hash_full)

            if len(treenode) != 0:
                # If node already in tree, increase attribute num_instances by 1
                treenode = treenode[0]
                try:
                    treenode.num_instances = treenode.num_instances + 1
                except:
                    print("num instances failed")
            else:
                # If node is not in tree, add the node
                # Get the parent node
                if len(hash_full_parent) == 0:
                    # Then this is the tree root
                    parentnode = t
                else:
                    parentnode = t.search_nodes(name=hash_full_parent)[0]
                # Add the node
                newnode = parentnode.add_child(name=hash_full)
                # Record that so far we only have once instance by adding attribute
                newnode.add_features(num_instances=1)

    if col_num == 2:

        num_sssf = 0
        for procname in ['Sub.SSFlow']:  # , 'Sub.GW.Store.Perch']:
            procnode = t.search_nodes(name=procname)
            if len(procnode) > 0:
                num_sssf = num_sssf + procnode[0].num_instances
        procnode = t.search_nodes(name='Sub.SSFlow.Organ')
        # if len(procnode) > 0: num_sssf = num_sssf - procnode[0].num_instances
        df_soil_histogram.loc[soil_index[i], 'Subsurface Stormflow'] = num_sssf

        num_ov = 0
        for procname in ['Surf.Over', 'Sub.GW.Ret']:
            procnode = t.search_nodes(name=procname)
            if len(procnode) > 0:
                num_ov = num_ov + procnode[0].num_instances
        df_soil_histogram.loc[soil_index[i], 'Overland Flow'] = num_ov


# TREES PER SLOPE CLASS #############################################################################
# Initialize list to hold trees for each slope class
treelist_slope = []
num_slope = 6
columns_of_sssf = ['Subsurface Stormflow', 'Overland Flow']
columns_use = columns_of_sssf
col_num_slope = 2

for i in range(0, num_slope):
    treelist_slope.append(Tree())

slope_index = ['0.01 - 1', '1 - 2', '2 - 4', '4 - 6', '6 - 10', '10 - 25']
slope_points = [0.01, 1, 2, 4, 6, 10, 25]

df_slope_histogram = pd.DataFrame(np.array(np.zeros((num_slope, col_num_slope))), columns=columns_use, index=slope_index)

# Create tree from each slope class to visualize processes included
for i in range(0, num_slope):
    slope_min = slope_points[i]
    slope_max = slope_points[i+1]
    # Only humid watersheds (aridity > 0) and soil thickness within band
    clusterindex = np.where(np.logical_and(aridity > 0, np.logical_and(slope >= slope_min, slope < slope_max)))

    clustersize = clusterindex[0].size
    print(f"slope class: {slope_index[i]} has {clustersize} watersheds")

    # If there are no watersheds in this biome, move to next biome
    if clustersize == 0:
        continue

    # Create empty list to store the strings
    cluster_storesfluxes = []

    for storeflux_list in pd.concat([store_hashtag[clusterindex[0]], flux_hashtag[clusterindex[0]]]):
        # Get rid of duplicates within sites
        storeflux = storeflux_list.split(',')
        storefluxstrip = [x.strip() for x in storeflux]
        storeflux_unique = list(set(storefluxstrip))
        storeflux_unique = [x for x in storeflux_unique if 'Human' not in x]
        # Add these stores to the list of stores and fluxes in this class
        cluster_storesfluxes.extend(storeflux_unique)

    # Initialize a tree to hold the cluster stores and fluxes
    t = treelist_slope[i]
    t.add_features(num_instances=len(cluster_storesfluxes))
    # Add the Surf, Sub, Chan children to get these in the right order
    tadd = t.add_child(name="Surf")
    tadd.num_instances = 0
    tadd = t.add_child(name="Sub")
    tadd.num_instances = 0
    tadd = t.add_child(name="Chan")
    tadd.num_instances = 0

    # Iterate over cluster stores and fluxes, adding each to tree
    for hashtag in cluster_storesfluxes:
        if len(hashtag) == 0:
            continue
        hashpartlist = hashtag.split('.')
        for hash_i in range(0, len(hashpartlist)):
            # Get full taxonomy hashtag
            hash_full = '.'.join(hashpartlist[0:hash_i + 1])
            # Get the parent hashtag
            hash_full_parent = '.'.join(hashpartlist[0:hash_i])

            # Find out whether this taxonomy item is already in the tree
            treenode = t.search_nodes(name=hash_full)

            if len(treenode) != 0:
                # If node already in tree, increase attribute num_instances by 1
                treenode = treenode[0]
                try:
                    treenode.num_instances = treenode.num_instances + 1
                except:
                    print("num instances failed")
            else:
                # If node is not in tree, add the node
                # Get the parent node
                if len(hash_full_parent) == 0:
                    # Then this is the tree root
                    parentnode = t
                else:
                    parentnode = t.search_nodes(name=hash_full_parent)[0]
                # Add the node
                newnode = parentnode.add_child(name=hash_full)
                # Record that so far we only have once instance by adding attribute
                newnode.add_features(num_instances=1)

    if col_num_slope == 2:

        num_sssf = 0
        for procname in ['Sub.SSFlow']:  # , 'Sub.GW.Store.Perch']:
            procnode = t.search_nodes(name=procname)
            if len(procnode) > 0:
                num_sssf = num_sssf + procnode[0].num_instances
        procnode = t.search_nodes(name='Sub.SSFlow.Organ')
        df_slope_histogram.loc[slope_index[i], 'Subsurface Stormflow'] = num_sssf

        num_ov = 0
        for procname in ['Surf.Over', 'Sub.GW.Ret']:
            procnode = t.search_nodes(name=procname)
            if len(procnode) > 0:
                num_ov = num_ov + procnode[0].num_instances
        df_slope_histogram.loc[slope_index[i], 'Overland Flow'] = num_ov


# FIGURE 4 -------STACKED BAR ARIDITY ##########################################################################

# Scale the aridity dataframe so it adds to one for each aridity category row
df_aridity_histogram_div = df_aridity_histogram.div(df_aridity_histogram.sum(axis=1), axis=0)

if col_num_arid == 2:
    title_arid = 'Infiltration vs Saturation Excess'
elif col_num_arid == 3:
    title_arid = 'b   Dunne process category by aridity class'
else:
    title_arid = 'a   Vertically organized process category by aridity class'

# Change colormap
color = plt.colormaps["Blues_r"](np.linspace(0, .75 ,3))

if col_num_arid == 3:
    # plot data in stack manner of bar type
    ax = df_aridity_histogram_div.plot(kind='bar', stacked=True,
                                       title=title_arid, color=color)
else:
    # plot data in stack manner of bar type
    ax = df_aridity_histogram_div.plot(kind='bar', stacked=True,
                                   title=title_arid, colormap="viridis")

for i, total in enumerate(aridity_totals):
    ax.text(i, 0.05, round(total), ha='center', color='silver')

# Setting the fontsize of the axis label to 20
plt.xlabel('Aridity (-1 is most arid, 1 is most humid)')
plt.ylabel('Fraction of processes in each category')

handles, labels = ax.get_legend_handles_labels()
if col_num_arid == 7:
    newlabels = ['Canopy', 'Surface', 'Near Surface', 'Soil', "Subsurface \n Stormflow", 'Groundwater',
                 'Regional \n Groundwater']
elif col_num_arid == 3:
    newlabels = ['Infiltration \n Excess', 'Saturation \n Excess', 'Subsurface \n Stormflow']

handles.reverse()
ax.legend(handles, newlabels, bbox_to_anchor=(1.0, 1.0))
plt.subplots_adjust(right=0.75, bottom=0.25)
plt.savefig(f"{output_folder_rev}Figure4_process_by_aridity_original.svg")


# FIGURE S1 -----STACKED BAR SOIL THICKNESS ##########################################################################

# Scale the soil thickness dataframe so it adds to one for each category row
df_soil_histogram_div = df_soil_histogram.div(df_soil_histogram.sum(axis=1), axis=0)

# plot data in stacked bar
ax = df_soil_histogram_div.plot(kind='bar', stacked=True,
                                title='b   Depths of process by soil thickness in humid watersheds', colormap="tab20")
plt.xlabel('Soil thickness (m)')
plt.ylabel('Fraction of processes in each category')

handles, labels = ax.get_legend_handles_labels()
newlabels = ['Overland \n Flow', 'Subsurface \n Stormflow']

handles.reverse()
ax.legend(handles, newlabels, bbox_to_anchor=(1.0, 1.0))
plt.subplots_adjust(right=0.75, bottom=0.25)
plt.savefig(f"{output_folder_rev}Figure_S1_process_by_soil_thickness.svg")

# FIGURE S1 ---------- STACKED BAR SLOPE ##########################################################################

# Scale the slope dataframe, so it adds to one for each category row
df_slope_histogram_div = df_slope_histogram.div(df_slope_histogram.sum(axis=1), axis=0)

# plot data in stack manner of bar type
ax = df_slope_histogram_div.plot(kind='bar', stacked=True,
                                 title='a   Depths of process by slope in humid watersheds', colormap="tab20")

# Setting the fontsize of the axis label to 20
plt.xlabel('Slope (degree)')
plt.ylabel('Fraction of processes in each category')

handles, labels = ax.get_legend_handles_labels()
newlabels = ['Overland \n Flow', 'Subsurface \n Stormflow']

handles.reverse()
ax.legend(handles, newlabels, bbox_to_anchor=(1.0, 1.0))
plt.subplots_adjust(right=0.75, bottom=0.25)
plt.savefig(f"{output_folder_rev}Figure_S1_process_by_slope.svg")

# ----------FIGURE 5 -----Lateral/Vertical process analysis ----------------------------------
# Create empty lists to store the numbers of vertical and lateral fluxes for each location
num_lateral = []
num_vertical = []

# Create empty list to store the strings
cluster_storesfluxes = []

# For each site, combine the stores and fluxes lists into a single comma-separated list
combined_storefluxlist = flux_hashtag

# For each site
for storeflux_list in combined_storefluxlist:
    # Get rid of duplicates within sites
    storeflux = storeflux_list.split(',')
    storefluxstrip = [x.strip() for x in storeflux]
    storeflux_unique = list(set(storefluxstrip))
    storeflux_unique = [x for x in storeflux_unique if 'Human' not in x]

    # Count the number of lateral fluxes
    num_vertical.append(sum('Sub.Soil.Matrix' in s for s in storeflux_unique) +
                        sum('Sub.Soil.Macro' in s for s in storeflux_unique) +
                        sum('Sub.Soil.Drain' in s for s in storeflux_unique))

    num_lateral.append(sum('Sub.SSFlow' in s for s in storeflux_unique) +
                       sum('Sub.Soil.Lat' in s for s in storeflux_unique))

# Convert lateral/vertical lists to arrays
num_lateral_array = np.array(num_lateral)
num_vertical_array = np.array(num_vertical)
lat_diff = num_lateral_array - num_vertical_array

lat_vert = np.zeros(len(num_lateral_array))
lat_vert[num_lateral_array > num_vertical_array] = 1
lat_vert[num_vertical_array > num_lateral_array] = -1

# Make map showing positions of watersheds with their lateral/vertical fluxes
fig10 = plt.figure(105, figsize=(15, 9))

ax10 = plt.subplot2grid((1, 4), (0, 0), colspan=3)
ax10a = plt.subplot2grid((2, 4), (0, 3))
ax10b = plt.subplot2grid((2, 4), (1, 3))

# Add world map outline
countries = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
countries.plot(edgecolor="lightblue", facecolor="none", ax=ax10, aspect=None)
# Scatter plot experimental watershed locations
max_color = max([np.max(lat_diff), np.max(-lat_diff)])
norm = plt.Normalize(-1.5, 1.5)
zero_pts = np.array(np.where(lat_diff == 0)).flatten()
non_zero_pts = np.array(np.where(lat_diff != 0)).flatten()
sc11 = ax10.scatter(watershed_lon[zero_pts], watershed_lat[zero_pts], marker='o', c=lat_diff[zero_pts], cmap='coolwarm',
                    alpha=0.8, norm=norm)
sc10 = ax10.scatter(watershed_lon[non_zero_pts], watershed_lat[non_zero_pts], marker='o',
                    c=lat_diff[non_zero_pts]/abs(lat_diff[non_zero_pts]),
                    cmap='bwr', alpha=0.8, norm=norm)
h_sc10 = sc10.legend_elements(num=[-1,1])[0]
h_sc11 = sc11.legend_elements(num=[0])[0]
myhandles = [h_sc10[0]] + h_sc11 + [h_sc10[1]]
mylabels = ['Vertical dominated', 'Equal', 'Lateral Dominated']
legend10 = ax10.legend(*sc10.legend_elements(), handles=myhandles, labels=mylabels, loc="lower left",
                       title="Prevalence of lateral flow")
ax10.add_artist(legend10)
ax10.set_ylim(-80, 80)
ax10.set_xlim(-170, 180)

# Add subplot showing lateral/vertical by landform
landform_index = ['Plains', 'Hills', 'Mountains', 'Tablelands']
df_landform_histogram = pd.DataFrame(np.array(np.zeros((4, 3))), columns=['Vertical', 'Equal', 'Lateral'],
                                     index=landform_index)
for lf in landform_index:
    df_landform_histogram.loc[lf, 'Lateral'] = sum((landform == lf) & (lat_vert == 1))
    df_landform_histogram.loc[lf, 'Vertical'] = sum((landform == lf) & (lat_vert == -1))
    df_landform_histogram.loc[lf, 'Equal'] = sum((landform == lf) & (lat_vert == 0))

# Make a stacked bar chart
# Scale the dataframe so it adds to one for each row
df_landform_histogram_div = df_landform_histogram.div(df_landform_histogram.sum(axis=1), axis=0)
ax_lf = df_landform_histogram_div.plot(kind='bar', stacked=True,
                                       title='Lateral/Vertical by landform', colormap="coolwarm", ax=ax10a)

handles, labels = ax_lf.get_legend_handles_labels()
ax10a.set_xticklabels(ax10a.get_xticklabels(), rotation=35)
ax10a.get_legend().remove()
plt.subplots_adjust(bottom=0.3)

# Add subplot showing lateral/vertical by biome
lve = ['Vertical', 'Equal', 'Lateral']

df_biomes_lv_histogram = pd.DataFrame(np.array(np.zeros((14, 3))), columns=lve,
                                      index=biomes_index)
lat_diff_norm = lat_diff
lat_diff_norm[lat_diff_norm!=0] = lat_diff_norm[lat_diff_norm!=0]/abs(lat_diff_norm[lat_diff_norm!=0])

for i in range(0, num_biomes):
    for diff in range(-1, 2):
        df_biomes_lv_histogram.loc[biomes_index[i], lve[diff + 1]] = \
            sum((biome_numbers == i + 1) & (lat_diff_norm == diff))

biomes_combined_index = ['Desert', 'Grassland', 'Dry Forest', 'Tundra', 'Temperate Forest', 'Tropical Forest',
                         'Boreal Forest']

df_biomes_comb_lv_histogram = pd.DataFrame(np.array(np.zeros((7, 3))), columns=lve,
                                           index=biomes_combined_index)

# Combine similar biomes for clarity
df_biomes_comb_lv_histogram.loc['Tropical Forest',] = df_biomes_lv_histogram.loc[biomes_index[0],]
df_biomes_comb_lv_histogram.loc['Temperate Forest',] = df_biomes_lv_histogram.loc[biomes_index[3],] + \
                                                       df_biomes_lv_histogram.loc[biomes_index[4],]
df_biomes_comb_lv_histogram.loc['Boreal Forest',] = df_biomes_lv_histogram.loc[biomes_index[5],]
df_biomes_comb_lv_histogram.loc['Dry Forest',] = df_biomes_lv_histogram.loc[biomes_index[1],] + \
                                                 df_biomes_lv_histogram.loc[biomes_index[11],]
df_biomes_comb_lv_histogram.loc['Grassland',] = df_biomes_lv_histogram.loc[biomes_index[6],] + \
                                                df_biomes_lv_histogram.loc[biomes_index[7],] + \
                                                df_biomes_lv_histogram.loc[biomes_index[9],]
df_biomes_comb_lv_histogram.loc['Tundra',] = df_biomes_lv_histogram.loc[biomes_index[10],]
df_biomes_comb_lv_histogram.loc['Desert',] = df_biomes_lv_histogram.loc[biomes_index[12],]

# Scale the aridity dataframe, so it adds to one for each aridity category row
df_biomes_comb_lv_histogram_div = df_biomes_comb_lv_histogram.div(df_biomes_comb_lv_histogram.sum(axis=1), axis=0)

# plot data in stack manner of bar type
df_biomes_comb_lv_histogram_div.plot(kind='bar', stacked=True,
                                     title='Lateral/Vertical by biome', colormap="coolwarm", ax=ax10b)

handles, labels = ax10b.get_legend_handles_labels()
ax10b.set_xticklabels(ax10b.get_xticklabels(), rotation=35, ha='right')
ax10b.get_legend().remove()
plt.subplots_adjust(bottom=0.2, hspace=0.4)
plt.savefig(f"{output_folder_rev}Figure5_lateral_vertical_location_landform_biome.svg")


# --------- FIGURE 2 ---- Process Locations

# Create empty lists to store the numbers of processes for each location
num_eph_int = []
num_eph_int1 = []
num_eph_int2 = []
num_eph_int3 = []
num_eph_int4 = []

# For each site, combine the stores and fluxes lists into a single comma-separated list
combined_storefluxlist = flux_hashtag

# For each site
for storeflux_list in combined_storefluxlist:
    # Get rid of duplicates within sites
    storeflux = storeflux_list.split(',')
    storefluxstrip = [x.strip() for x in storeflux]
    storeflux_unique = list(set(storefluxstrip))
    storeflux_unique = [x for x in storeflux_unique if 'Human' not in x]

    #Count 4 types of processes
    num_eph_int1.append(sum('Sub.SSFlow' in s for s in storeflux_unique))
    num_eph_int2.append(sum('Sub.SSFlow.Organ' in s for s in storeflux_unique))
    num_eph_int3.append(sum('Surf.Over' in s for s in storeflux_unique))
    num_eph_int4.append(sum('Chan.Flow.Ephem' in s for s in storeflux_unique) +
                        sum('Chan.Flow.Interm' in s for s in storeflux_unique))

# Convert process lists to arrays
num_eph_int_array1 = np.array(num_eph_int1)
num_eph_int_array2 = np.array(num_eph_int2)
num_eph_int_array3 = np.array(num_eph_int3)
num_eph_int_array4 = np.array(num_eph_int4)
tf_eph_int_array1 = np.zeros(len(num_eph_int_array1))
tf_eph_int_array2 = np.zeros(len(num_eph_int_array2))
tf_eph_int_array3 = np.zeros(len(num_eph_int_array3))
tf_eph_int_array4 = np.zeros(len(num_eph_int_array4))
tf_eph_int_array1[num_eph_int_array1 > 0] = 1
tf_eph_int_array2[num_eph_int_array2 > 0] = 1
tf_eph_int_array3[num_eph_int_array3 > 0] = 1
tf_eph_int_array4[num_eph_int_array4 > 0] = 1
non_zero_pts1 = np.array(np.where(tf_eph_int_array1 != 0)).flatten()
non_zero_pts2 = np.array(np.where(tf_eph_int_array2 != 0)).flatten()
non_zero_pts3 = np.array(np.where(tf_eph_int_array3 != 0)).flatten()
non_zero_pts4 = np.array(np.where(tf_eph_int_array4 != 0)).flatten()


# Make map showing four processes at once
fig85 = plt.figure(85, figsize=(15, 10))
gs85 = gridspec.GridSpec(2, 2, width_ratios=[1, 1])
selected_titles = ['a   Subsurface Stormflow', 'b   Organic Layer Subsurface StormFlow',
                   'c   Overland Flow', 'd   Non-Perennial Flow']
selected_legendtitles = ['Subsurface Stormflow', 'Organic Layer Subsurface StormFlow',
                         'Overland Flow', 'Non-Perennial Flow']

for i in range(0, 4):
    ax85 = plt.subplot(gs85[i])
    ax85.set_title(selected_titles[i])

    # Add world map outline
    countries = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
    countries.plot(edgecolor="lightblue", facecolor="none", ax=ax85, aspect=None)

    # Scatter plot experimental watershed locations
    if i == 0:
        sc85 = ax85.scatter(watershed_lon, watershed_lat, marker='o', c=tf_eph_int_array1, cmap='Set2_r', alpha=0.8)
        norm = plt.Normalize(0, 1)
        sc86 = ax85.scatter(watershed_lon[non_zero_pts1], watershed_lat[non_zero_pts1], marker='o',
                        c=tf_eph_int_array1[non_zero_pts1], cmap='bwr', norm=norm, alpha=0.8)
    elif i == 1:
        sc85 = ax85.scatter(watershed_lon, watershed_lat, marker='o', c=tf_eph_int_array2, cmap='Set2_r', alpha=0.8)
        norm = plt.Normalize(0, 1)
        sc86 = ax85.scatter(watershed_lon[non_zero_pts2], watershed_lat[non_zero_pts2], marker='o',
                        c=tf_eph_int_array2[non_zero_pts2], cmap='bwr', norm=norm, alpha=0.8)
    elif i == 2:
        sc85 = ax85.scatter(watershed_lon, watershed_lat, marker='o', c=tf_eph_int_array3, cmap='Set2_r', alpha=0.8)
        norm = plt.Normalize(0, 1)
        sc86 = ax85.scatter(watershed_lon[non_zero_pts3], watershed_lat[non_zero_pts3], marker='o',
                    c=tf_eph_int_array3[non_zero_pts3], cmap='bwr', norm=norm, alpha=0.8)
    elif i == 3:
        sc85 = ax85.scatter(watershed_lon, watershed_lat, marker='o', c=tf_eph_int_array4, cmap='Set2_r', alpha=0.8)
        norm = plt.Normalize(0, 1)
        sc86 = ax85.scatter(watershed_lon[non_zero_pts4], watershed_lat[non_zero_pts4], marker='o',
                    c=tf_eph_int_array4[non_zero_pts4], cmap='bwr', norm=norm, alpha=0.8)

    mylabels = ['Not Recorded', 'Recorded']
    legend85 = ax85.legend(*sc85.legend_elements(), loc="lower left", labels=mylabels, title=selected_legendtitles[i])

plt.subplots_adjust(right=0.95, left=0.05)
plt.savefig(f"{output_folder_rev}Figure2_Processes4_map.svg")