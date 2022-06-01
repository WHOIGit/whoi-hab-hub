import { createSlice } from "@reduxjs/toolkit";

const guideSteps = [
  { label: "About", tabIndex: null, active: false },
  { label: "Select HAB Species", tabIndex: 0, active: false },
  { label: "Select Data Layers", tabIndex: 1, active: false },
];

const initialState = {
  guideSteps: guideSteps,
};

export const guideSlice = createSlice({
  name: "guide",
  initialState: initialState,
  reducers: {
    changeActiveGuideStep: (state, action) => {
      state.guideSteps.forEach((element) => {
        if (element.id == action.payload.species.id) {
          element.active = true;
        } else {
          element.active = false;
        }
      });
    },
  },
});

// Action creators are generated for each case reducer function
export const { changeDateRange, changeDefaultStartDate } = guideSlice.actions;

export default guideSlice.reducer;
