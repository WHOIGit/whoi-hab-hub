import { createSlice } from "@reduxjs/toolkit";
const MAP_LATITUDE = parseFloat(process.env.REACT_APP_MAP_LATITUDE);
const MAP_LONGITUDE = parseFloat(process.env.REACT_APP_MAP_LONGITUDE);

const initialState = {
  latitude: MAP_LATITUDE,
  longitude: MAP_LONGITUDE,
  zoom: 5,
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
    // eslint-disable-next-line no-unused-vars
    resetGuideSteps: (state, action) => {
      state.guideSteps.forEach((element) => {
        element.isActive = false;
      });
    },
  },
});

// Action creators are generated for each case reducer function
export const { changeMapData } = habMapDataSlice.actions;

export default habMapDataSlice.reducer;
