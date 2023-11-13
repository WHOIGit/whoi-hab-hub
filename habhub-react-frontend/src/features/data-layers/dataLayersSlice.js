import axiosInstance from "../../app/apiAxios";
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { createSelector } from "reselect";
// local
import { DATA_LAYERS } from "../../Constants";

// list of dataLayer IDs that have an available floating Legend window pane
// need to check it against the active layers in the API results
const legendLayerIds = [
  DATA_LAYERS.stationsLayer,
  DATA_LAYERS.cellConcentrationLayer,
  DATA_LAYERS.cellConcentrationSpatialGridLayer,
];
const interactiveLayerIds = [
  DATA_LAYERS.closuresIconsLayer,
  DATA_LAYERS.closuresSeasonalIconsLayer,
];

const initialState = {
  layers: [],
  showMaxMean: "mean",
  status: "idle",
  error: null,
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
      console.log(action);
      state.layers.forEach((element) => {
        if (element.id === action.payload.layerID) {
          element.visibility = action.payload.checked;
        }
      });
    },
    setAllLayersVisibility: (state, action) => {
      state.layers.forEach((element) => {
        if (action.payload.layerList.includes(element.id)) {
          element.visibility = true;
        } else {
          element.visibility = false;
        }
      });
    },
    changeMaxMean: (state, action) => {
      state.showMaxMean = action.payload.value;
    },
    changeLegendVisibility: (state, action) => {
      state.layers.forEach((element) => {
        if (element.id === action.payload.layerID) {
          element.legendVisibility = action.payload.legendVisibility;
        }
      });
    },
  },
  extraReducers: {
    [fetchLayers.pending]: (state) => {
      state.status = "loading";
    },
    [fetchLayers.fulfilled]: (state, action) => {
      state.status = "succeeded";
      // Add any fetched layers to the array
      state.layers = state.layers.concat(action.payload);
      state.layers.forEach((element) => {
        // hide closures layer by default on load
        // only one of cell_concentration/biovolume can be active at one time
        // default to cell_concentration as initial active layer
        if (
          element.id === DATA_LAYERS.closuresLayer ||
          element.id === DATA_LAYERS.closuresSeasonalLayer ||
          element.id === DATA_LAYERS.biovolumeLayer ||
          element.id === DATA_LAYERS.biovolumeSpatialGridLayer
        ) {
          element.visibility = false;
        } else {
          element.visibility = true;
        }

        // fixed and spatial cell_concentration have same legend pane
        // only one should show at a single time
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
    },
  },
});

// Action creators are generated for each case reducer function
export const {
  changeLayerVisibility,
  changeMaxMean,
  changeLegendVisibility,
  setAllLayersVisibility,
} = dataLayersSlice.actions;

export default dataLayersSlice.reducer;

// Selector functions
// return only the currently visible layers
export const selectVisibleLayers = (state) =>
  state.dataLayers.layers.filter((layer) => layer.visibility);

// return a memoized flat array of just the visible dataLayer IDs
export const selectVisibleLayerIds = createSelector(
  (state) => state.dataLayers.layers,
  (items) => {
    const layerIds = items
      .filter((layer) => layer.visibility)
      .map((layer) => layer.id);
    return layerIds;
  }
);

// return a flat array of just the dataLayer IDs that are interactive with Mapbox Layer propery
export const selectInteractiveLayerIds = (state) => {
  const layerIds = state.dataLayers.layers
    .filter((layer) => layer.visibility)
    .filter((layer) => layer.interactiveLayer)
    .map((layer) => layer.id);
  return layerIds;
};

// return a flat array of just the dataLayer IDs that have a Legend pane
/*
export const selectLayerLegendIds = (state) => {
  const layerIds = state.dataLayers.layers
    .filter((layer) => layer.legendVisibility)
    .map((layer) => layer.id);
  return layerIds;
};*/

export const selectLayerLegendIds = createSelector(
  (state) => state.dataLayers.layers,
  (items) => {
    let activeLegends = items
      .filter((layer) => layer.legendVisibility && layer.visibility)
      .map((layer) => layer.id);
    // fixed and spatial cell_concentration have same legend pane
    // only one should show at a single time
    const checkForFixed = activeLegends.some(
      (layer) => layer === DATA_LAYERS.cellConcentrationLayer
    );
    const checkForSpatial = activeLegends.some(
      (layer) => layer === DATA_LAYERS.cellConcentrationSpatialGridLayer
    );
    console.log(checkForFixed, checkForSpatial, activeLegends);

    if (checkForFixed && checkForSpatial) {
      //remove one of the legends
      activeLegends = activeLegends.filter(
        (layer) => layer !== DATA_LAYERS.cellConcentrationLayer
      );
    }

    return activeLegends;
  }
);

// return max/mean value selection
export const selectMaxMeanOption = (state) => state.dataLayers.showMaxMean;
