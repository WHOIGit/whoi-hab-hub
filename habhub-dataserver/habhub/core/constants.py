# Global constants

# DATA_LAYERS constant = default Data Layers
CELL_CONCENTRATION_LAYER = "cell_concentration_layer"
CELL_CONCENTRATION_SPATIALGRID_LAYER = "cell_concentration_spatialgrid_layer"
BIOVOLUME_LAYER = "biovolume_layer"
BIOVOLUME_SPATIALGRID_LAYER = "biovolume_spatialgrid_layer"
STATIONS_LAYER = "stations_layer"
CLOSURES_LAYER = "closures_layer"
CLOSURES_SEASONAL_LAYER = "closures_seasonal_layer"

DATA_LAYERS = (
    (CELL_CONCENTRATION_LAYER, "Cell Concentration (Fixed Locations)"),
    (CELL_CONCENTRATION_SPATIALGRID_LAYER, "Cell Concentration (Spatial Grid)"),
    (BIOVOLUME_LAYER, "Biovolume (Fixed Locations)"),
    (BIOVOLUME_SPATIALGRID_LAYER, "Biovolume (Spatial Grid)"),
    (STATIONS_LAYER, "Shellfish Toxicity"),
    (CLOSURES_LAYER, "Shellfish Bed Closures (Event Triggered)"),
    (CLOSURES_SEASONAL_LAYER, "Shellfish Bed Closures (Seasonal)"),
)

# METRICS constant = default Data Layer Metrics
CELL_CONCENTRATION = "cell_concentration"
BIOVOLUME = "biovolume"
SHELLFISH_TOXICITY = "shellfish_toxicity"

METRICS = (
    (
        CELL_CONCENTRATION,
        "Cell Concentration",
        "cells/L",
        [CELL_CONCENTRATION_LAYER, CELL_CONCENTRATION_SPATIALGRID_LAYER],
    ),
    (
        BIOVOLUME,
        "Biovolume",
        "cubic microns/L",
        [BIOVOLUME_LAYER, BIOVOLUME_SPATIALGRID_LAYER],
    ),
    (
        SHELLFISH_TOXICITY,
        "Shellfish Toxicity",
        "micrograms/100 g meat",
        [STATIONS_LAYER],
    ),
)

# TARGET_SPECIES constant of HAB species we're monitoring
ALEXANDRIUM_CATENELLA = "Alexandrium_catenella"
DINOPHYSIS_ACUMINATA = "Dinophysis_acuminata"
DINOPHYSIS_NORVEGICA = "Dinophysis_norvegica"
KARENIA = "Karenia"
MARGALEFIDINIUM = "Margalefidinium"
PSEUDO_NITZSCHIA = "Pseudo-nitzschia"

TARGET_SPECIES = (
    (ALEXANDRIUM_CATENELLA, "Alexandrium catenella"),
    (DINOPHYSIS_ACUMINATA, "Dinophysis acuminata"),
    (DINOPHYSIS_NORVEGICA, "Dinophysis norvegica"),
    (KARENIA, "Karenia"),
    (MARGALEFIDINIUM, "Margalefidinium polykrikoides"),
    (PSEUDO_NITZSCHIA, "Pseudo nitzschia"),
)
