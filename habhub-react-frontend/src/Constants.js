// Date Layer IDs to match with Redux store
export const DATA_LAYERS = {
  biovolumeLayer: "biovolume_layer",
  biovolumeSpatialGridLayer: "biovolume_spatialgrid_layer",
  cellConcentrationLayer: "cell_concentration_layer",
  cellConcentrationSpatialGridLayer: "cell_concentration_spatialgrid_layer",
  stationsLayer: "stations_layer",
  closuresLayer: "closures_layer",
  closuresSeasonalLayer: "closures_seasonal_layer",
};

export const METRIC_IDS = {
  biovolume: "biovolume",
  cellConcentration: "cell_concentration",
  shellfishToxicity: "shellfish_toxicity",
};

// define color palette for the species color picker options
export const PALETTE = {
  red: "#ff0000",
  blue: "#0000ff",
  green: "#00ff00",
  yellow: "yellow",
  cyan: "cyan",
  lime: "lime",
  gray: "gray",
  orange: "orange",
  purple: "purple",
  black: "black",
  white: "white",
  pink: "pink",
  darkblue: "darkblue",
};

// Match available species environment options in API Target Species
export const ENVIRONMENTS = ["Marine", "Freshwater"];

// object of Component "types" to work with react-dnd drag and drop functionality
export const ITEM_TYPES = {
  PANE: "pane",
};
