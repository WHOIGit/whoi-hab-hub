# Global constants

# DATA_LAYERS constant = default Data Layers
CELL_CONCENTRATION_LAYER = "cell_concentration_layer"
BIOVOLUME_LAYER = "biovolume_layer"
STATIONS_LAYER = "stations_layer"
CLOSURES_LAYER = "closures_layer"

DATA_LAYERS = (
    (CELL_CONCENTRATION_LAYER, "Cell Concentration (Fixed Locations)"),
    (BIOVOLUME_LAYER, "Biovolume (Fixed Locations)"),
    (STATIONS_LAYER, "Shellfish Toxicity"),
    (CLOSURES_LAYER, "Shellfish Bed Closures"),
)

# METRICS constant = default Data Layer Metrics
CELL_CONCENTRATION = "cell_concentration"
BIOVOLUME = "biovolume"
SHELLFISH_TOXICITY = "shellfish_toxicity"

METRICS = (
    (CELL_CONCENTRATION, "Cell Concentration", "cells/L", CELL_CONCENTRATION_LAYER),
    (BIOVOLUME, "Biovolume", "cubic microns/L", BIOVOLUME_LAYER),
    (SHELLFISH_TOXICITY, "Shellfish Toxicity", "micrograms/100 g meat", STATIONS_LAYER),
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
