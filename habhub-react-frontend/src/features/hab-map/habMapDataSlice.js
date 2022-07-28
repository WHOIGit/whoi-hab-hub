import { createSlice } from "@reduxjs/toolkit";

const initialState = {
  latitude: 0.0,
  longitude: 0.0,
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
