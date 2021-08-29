// Date Layer IDs to match with Redux store
export const DATA_LAYERS = {
  ifcbBiovolumeLayer: "ifcb_biovolume_layer",
  ifcbLayer: "ifcb_layer",
  stationsLayer: "stations_layer",
  closuresLayer: "closures_layer"
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
  darkblue: "darkblue"
};

// Match available species environment options in API Target Species
export const ENVIRONMENTS = ["Marine", "Freshwater"];

// object of Component "types" to work with react-dnd drag and drop functionality
export const ItemTypes = {
  PANE: "pane"
};
