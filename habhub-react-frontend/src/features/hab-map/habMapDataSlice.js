import { createSlice } from "@reduxjs/toolkit";
const MAP_LATITUDE = parseFloat(import.meta.env.VITE_MAP_LATITUDE);
const MAP_LONGITUDE = parseFloat(import.meta.env.VITE_MAP_LONGITUDE);

const initialState = {
  latitude: MAP_LATITUDE,
  longitude: MAP_LONGITUDE,
  zoom: 5,
  activeFeatures: [],
};

export const habMapDataSlice = createSlice({
  name: "habMapData",
  initialState: initialState,
  reducers: {
    changeMapData: (state, action) => {
      state.latitude = action.payload.latitude;
      state.longitude = action.payload.longitude;
      state.zoom = action.payload.zoom;
    },
    addFeature(state, action) {
      state.activeFeatures.push(action.payload);
    },
    deleteFeature(state, action) {
      const newFeatures = state.activeFeatures.filter(
        (feature) => feature.id !== action.payload
      );
      // "Mutate" the existing state to save the new array
      state.activeFeatures = newFeatures;
    },
    setAllFeatures(state, action) {
      // set all active features to new array
      state.activeFeatures = action.payload;
    },
  },
});

// Action creators are generated for each case reducer function
export const { changeMapData, addFeature, deleteFeature, setAllFeatures } =
  habMapDataSlice.actions;

export default habMapDataSlice.reducer;

// Selector functions
// return all active features
export const selectActiveFeatues = (state) => state.habMapData.activeFeatures;
