import axiosInstance from "../../app/apiAxios";
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
// local
import { DATA_LAYERS } from "../../Constants";

// list of dataLayer IDs that have an available floating Legend window pane
// need to check it against the active layers in the API results
const legendLayerIds = [DATA_LAYERS.stationsLayer, DATA_LAYERS.ifcbLayer];
const interactiveLayerIds = [DATA_LAYERS.closuresLayer];

const initialState = {
  layers: [],
  showMaxMean: "max",
  status: "idle",
  error: null
};

// API request for available dataLayers in HABhub
export const fetchLayers = createAsyncThunk(
  "dataLayers/fetchLayers",
  async () => {
    const endpoint = "api/v1/core/data-layers/";
    const response = await axiosInstance.get(endpoint);
    return response.data;
  }
);

export const dataLayersSlice = createSlice({
  name: "dataLayers",
  initialState: initialState,
  reducers: {
    changeLayerVisibility: (state, action) => {
      state.layers.forEach(element => {
        if (element.id === action.payload.layerID) {
          element.visibility = action.payload.checked;
        }
      });
    },
    changeMaxMean: (state, action) => {
      state.showMaxMean = action.payload.value;
    },
    changeLegendVisibility: (state, action) => {
      state.layers.forEach(element => {
        if (element.id === action.payload.layerID) {
          element.legendVisibility = action.payload.legendVisibility;
        }
      });
    }
  },
  extraReducers: {
    [fetchLayers.pending]: state => {
      state.status = "loading";
    },
    [fetchLayers.fulfilled]: (state, action) => {
      state.status = "succeeded";
      // Add any fetched layers to the array
      state.layers = state.layers.concat(action.payload);
      state.layers.forEach(element => {
        // only one of ifcb-layer/ifcb-biovolume-layer can be active at one time
        // default to ifcb-layer (cell_concentration) as initial active layer
        if (element.id === DATA_LAYERS.ifcbBiovolumeLayer) {
          element.visibility = false;
        } else {
          element.visibility = true;
        }

        if (legendLayerIds.includes(element.id)) {
          element.legendVisibility = true;
        }
        if (interactiveLayerIds.includes(element.id)) {
          element.interactiveLayer = true;
        }
      });
    },
    [fetchLayers.rejected]: (state, action) => {
      state.status = "failed";
      state.error = action.error.message;
    }
  }
});

// Action creators are generated for each case reducer function
export const {
  changeLayerVisibility,
  changeMaxMean,
  changeLegendVisibility
} = dataLayersSlice.actions;

export default dataLayersSlice.reducer;

// Selector functions
// return only the currently visible layers
export const selectVisibleLayers = state =>
  state.dataLayers.layers.filter(layer => layer.visibility);

// return a flat array of just the dataLayer IDs
export const selectVisibleLayerIds = state => {
  const layerIds = state.dataLayers.layers
    .filter(layer => layer.visibility)
    .map(layer => layer.id);
  return layerIds;
};

// return a flat array of just the dataLayer IDs that are interactive with Mapbox Layer propery
export const selectInteractiveLayerIds = state => {
  const layerIds = state.dataLayers.layers
    .filter(layer => layer.visibility)
    .filter(layer => layer.interactiveLayer)
    .map(layer => layer.id);
  return layerIds;
};

// return a flat array of just the dataLayer IDs that have a Legend pane
export const selectLayerLegendIds = state => {
  const layerIds = state.dataLayers.layers
    .filter(layer => layer.legendVisibility)
    .map(layer => layer.id);
  return layerIds;
};

// return max/mean value selection
export const selectMaxMeanOption = state => state.dataLayers.showMaxMean;
