// array of Data Layers to display on the map
export const layers = [
  {
    name: "Shellfish Toxicity",
    id: "stations-layer",
    visibility: true,
    isActive: true,
    hasLegend: true,
  },
  {
    name: "IFCB Cell Concentration",
    id: "ifcb-layer",
    visibility: true,
    isActive: true,
    hasLegend: true,
  },
  {
    name: "Shellfish Closures",
    id: "closures-layer",
    visibility: true,
    isActive: true,
    hasLegend: false,
  },
];

// object of Component "types" to work with react-dnd drag and drop functionality
export const ItemTypes = {
  PANE: "pane",
};
