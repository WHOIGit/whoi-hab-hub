import { createSlice } from "@reduxjs/toolkit";

const guideSteps = [
  {
    stepId: 0,
    label: "About",
    text: `Add up to 6 HAB Species/Syndromes of interest at a time. 
  You can change the color indicated by clicking the square      
  to use the color picker tool and create your own custom color palette.`,
    tabIndex: null,
    active: false,
  },
  {
    stepId: 1,
    label: "Select HAB Species",
    text: "New text",
    tabIndex: 0,
    active: false,
  },
  {
    stepId: 2,
    label: "Select Data Layers",
    text: "New text",
    tabIndex: 1,
    active: false,
  },
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
        if (element.stepId == action.payload.stepId) {
          element.active = true;
        } else {
          element.active = false;
        }
      });
    },
  },
});

// Action creators are generated for each case reducer function
export const { changeActiveGuideStep } = guideSlice.actions;

export default guideSlice.reducer;

// Selector functions
// return all species
export const selectGuideSteps = (state) => state.guide.guideSteps;
