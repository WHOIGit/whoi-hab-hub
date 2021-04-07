import { createSlice } from "@reduxjs/toolkit";

const layers = [
  {
    name: "Shellfish Toxicity",
    id: "stations-layer",
    visibility: true,
    isActive: true,
    hasLegend: true,
    showMaxMean: "max"
  },
  {
    name: "IFCB Cell Concentration",
    id: "ifcb-layer",
    visibility: true,
    isActive: true,
    hasLegend: true,
    showMaxMean: "max"
  },
  {
    name: "Shellfish Bed Closures",
    id: "closures-layer",
    visibility: true,
    isActive: true,
    hasLegend: false,
    showMaxMean: "max"
  }
];

const initialState = {
  layers: layers,
  status: "idle",
  error: null
};

export const dataLayersSlice = createSlice({
  name: "dataLayers",
  initialState: initialState,
  reducers: {
    changeLayerVisibility: (state, action) => {
      state.layers.forEach(element => {
        if (element.id == action.payload.layerID) {
          console.log(element);
          element.visibility = action.payload.checked;
        }
      });
    },
    changeMaxMean: (state, action) => {
      state.layers.forEach(element => {
        element.showMaxMean = action.payload.value;
      });
    }
  }
});

// Action creators are generated for each case reducer function
export const { changeLayerVisibility, changeMaxMean } = dataLayersSlice.actions;

export default dataLayersSlice.reducer;

// Selector functions
// return only the currently visible layers
export const selectVisibleLayers = state =>
  state.dataLayers.layers.filter(layer => layer.visibility);

// return a flat array of just the dataLayer IDs
export const selectVisibleLayerIds = state => {
  const flattenedLayers = state.dataLayers.layers
    .filter(layer => layer.visibility)
    .map(layer => layer.id);
  return flattenedLayers;
};

// return max/mean value selection
export const selectMaxMeanOption = state =>
  state.dataLayers.layers[0].showMaxMean;
