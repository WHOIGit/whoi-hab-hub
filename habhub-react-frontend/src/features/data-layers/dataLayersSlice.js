import { createSlice } from "@reduxjs/toolkit";

const initialLayers = [
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

export const dataLayersSlice = createSlice({
  name: "dataLayers",
  initialState: initialLayers,
  reducers: {
    changeLayerVisibility: (state, action) => {
      state.forEach((element) => {
        if (element.id == action.payload.layer.id) {
          console.log(element);
          element.visibility = action.payload.checked;
        }
      });
    },
  },
});

// Action creators are generated for each case reducer function
export const { changeLayerVisibility } = dataLayersSlice.actions;

export default dataLayersSlice.reducer;
