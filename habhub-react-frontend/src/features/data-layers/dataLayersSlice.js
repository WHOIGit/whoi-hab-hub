import axios from "axios";
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

const API_URL = process.env.REACT_APP_API_URL;

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
    const url = API_URL + "api/v1/core/data-layers/";
    const response = await axios.get(url);
    return response.data;
  }
);

export const dataLayersSlice = createSlice({
  name: "dataLayers",
  initialState: initialState,
  reducers: {
    changeLayerVisibility: (state, action) => {
      state.layers.forEach(element => {
        if (element.id == action.payload.layerID) {
          element.visibility = action.payload.checked;
        }
      });
    },
    changeMaxMean: (state, action) => {
      state.showMaxMean = action.payload.value;
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
        element.visibility = true;
        element.hasLegend = true;
      });
    },
    [fetchLayers.rejected]: (state, action) => {
      state.status = "failed";
      state.error = action.error.message;
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
export const selectMaxMeanOption = state => state.dataLayers.showMaxMean;
