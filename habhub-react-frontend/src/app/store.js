import { configureStore } from "@reduxjs/toolkit";
import habSpeciesReducer from "../features/hab-species/habSpeciesSlice";
import dataLayersReduder from "../features/data-layers/dataLayersSlice";
import dateFilterReducer from "../features/date-filter/dateFilterSlice";
import userReducer from "../features/user/userSlice";

export default configureStore({
  reducer: {
    habSpecies: habSpeciesReducer,
    dataLayers: dataLayersReduder,
    dateFilter: dateFilterReducer,
    user: userReducer
  }
});
