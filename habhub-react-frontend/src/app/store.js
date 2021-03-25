import { configureStore } from "@reduxjs/toolkit";
import habSpeciesReducer from "../features/hab-species/habSpeciesSlice";

export default configureStore({
  reducer: {
    habSpecies: habSpeciesReducer,
  },
});
