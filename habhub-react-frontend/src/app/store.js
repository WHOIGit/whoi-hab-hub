import { configureStore } from "@reduxjs/toolkit";
import habSpeciesReducer from "../features/hab-species/habSpeciesSlice";
import dataLayersReduder from "../features/data-layers/dataLayersSlice";
import dateFilterReducer from "../features/date-filter/dateFilterSlice";
import spatialGridReducer from "../features/hab-map/spatialGridSlice";

export default configureStore({
  reducer: {
    habSpecies: habSpeciesReducer,
    dataLayers: dataLayersReduder,
    dateFilter: dateFilterReducer,
    spatialGrid: spatialGridReducer
  }
});
