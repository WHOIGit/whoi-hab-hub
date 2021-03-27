import { configureStore } from "@reduxjs/toolkit";
import habSpeciesReducer from "../features/hab-species/habSpeciesSlice";
import dateFilterReducer from "../features/date-filter/dateFilterSlice";

export default configureStore({
  reducer: {
    habSpecies: habSpeciesReducer,
    dateFilter: dateFilterReducer,
  },
});
