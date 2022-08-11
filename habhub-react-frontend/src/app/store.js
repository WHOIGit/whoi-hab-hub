import { configureStore } from "@reduxjs/toolkit";
import habSpeciesReducer from "../features/hab-species/habSpeciesSlice";
import dataLayersReduder from "../features/data-layers/dataLayersSlice";
import dateFilterReducer from "../features/date-filter/dateFilterSlice";
//import spatialGridReducer from "../features/hab-map/spatialGridSlice";
import guideReducer from "../features/guide/guideSlice";
import habMapDataReducer from "../features/hab-map/habMapDataSlice";

export default configureStore({
  reducer: {
    habSpecies: habSpeciesReducer,
    dataLayers: dataLayersReduder,
    dateFilter: dateFilterReducer,
    //spatialGrid: spatialGridReducer,
    guide: guideReducer,
    habMapData: habMapDataReducer,
  },
});
