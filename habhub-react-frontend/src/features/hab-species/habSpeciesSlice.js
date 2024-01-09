import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";
import { createSelector } from "reselect";
// local
import axiosInstance from "../../app/apiAxios";
import { colorShade } from "../../app/utils/colorUtils";
import { ENVIRONMENTS, SPECIES_TYPES } from "../../Constants";

let INITIAL_SPECIES_LIST = null;
// eslint-disable-next-line no-undef
if (import.meta.env.VITE_INITIAL_SPECIES_LIST) {
  INITIAL_SPECIES_LIST = import.meta.env.VITE_INITIAL_SPECIES_LIST.split(",");
}

let SHOW_SPECIES_LIST = null;
// eslint-disable-next-line no-undef
if (import.meta.env.VITE_SHOW_SPECIES_LIST) {
  SHOW_SPECIES_LIST = import.meta.env.VITE_SHOW_SPECIES_LIST.split(",");
}
console.log(SHOW_SPECIES_LIST);

const initialState = {
  species: [],
  enviroments: ENVIRONMENTS,
  species_types: SPECIES_TYPES,
  status: "idle",
  error: null,
};

/*
const initialSpecies = [
  {
    id: "Alexandrium_catenella",
    speciesName: "Alexandrium catenella",
    syndrome: "PSP",
    visibility: true,
    colorPrimary: "#e31a1c",
    colorGradient: ["#fee5d9", "#fcae91", "#fb6a4a", "#e31a1c", "#a50f15"]
  },
  {
    id: "Dinophysis_acuminata",
    speciesName: "Dinophysis acuminata",
    syndrome: "DSP",
    visibility: true,
    colorPrimary: "#1f78b4",
    colorGradient: ["#eff3ff", "#bdd7e7", "#6baed6", "#1f78b4", "#08519c"]
  },
  {
    id: "Dinophysis_norvegica",
    speciesName: "Dinophysis norvegica",
    syndrome: "DSP",
    visibility: true,
    colorPrimary: "#9e9e9e",
    colorGradient: ["#fafafa", "#eeeeee", "#bdbdbd", "#9e9e9e", "#616161"]
  },
  {
    id: "Karenia",
    speciesName: "Karenia",
    syndrome: "Fish Kills",
    visibility: true,
    colorPrimary: "#33a02c",
    colorGradient: ["#edf8e9", "#bae4b3", "#74c476", "#33a02c", "#006d2c"]
  },
  {
    id: "Margalefidinium",
    speciesName: "Margalefidinium polykrikoides",
    syndrome: "Fish Kills",
    visibility: true,
    colorPrimary: "#ffeb3b",
    colorGradient: ["#fffde7", "#fff59d", "#fff176", "#ffeb3b", "#fdd835"]
  },
  {
    id: "Pseudo-nitzschia",
    speciesName: "Pseudo-nitzschia",
    syndrome: "ASP",
    visibility: true,
    colorPrimary: "#673ab7",
    colorGradient: ["#ede7f6", "#d1c4e9", "#9575cd", "#673ab7", "#311b92"]
  }
];*/

// API request for available dataLayers in HABhub
export const fetchHabSpecies = createAsyncThunk(
  "habSpecies/fetchHabSpecies",
  async () => {
    const endpoint = "api/v1/core/target-species/";
    const response = await axiosInstance.get(endpoint);
    console.log(response.data);

    let data = response.data;
    if (SHOW_SPECIES_LIST) {
      const newData = data.filter((element) =>
        SHOW_SPECIES_LIST.includes(element.id)
      );
      data = newData;
      console.log(data);
    }

    return data;
  }
);

export const habSpeciesSlice = createSlice({
  name: "habSpecies",
  initialState: initialState,
  reducers: {
    changeSpeciesVisibility: (state, action) => {
      state.species.forEach((element) => {
        if (element.id == action.payload.species.id) {
          element.visibility = action.payload.checked;
        }
      });
    },
    setAllSpeciesVisibility: (state, action) => {
      state.species.forEach((element) => {
        if (action.payload.speciesList.includes(element.id)) {
          element.visibility = true;
        } else {
          element.visibility = false;
        }
      });
    },
    changeSpeciesActiveOption: (state, action) => {
      state.species.forEach((element) => {
        if (element.id == action.payload.species.id) {
          element.isActive = action.payload.checked;
        }
      });
    },
    changeSpeciesColor: (state, action) => {
      state.species.forEach((element) => {
        if (element.id == action.payload.species.id) {
          element.primaryColor = action.payload.primaryColor;
          element.colorGradient = [
            colorShade(action.payload.primaryColor, 120),
            colorShade(action.payload.primaryColor, 80),
            action.payload.primaryColor,
            colorShade(action.payload.primaryColor, -40),
            colorShade(action.payload.primaryColor, -80),
          ];
        }
      });
    },
  },
  extraReducers: {
    [fetchHabSpecies.pending]: (state) => {
      state.status = "loading";
    },
    [fetchHabSpecies.fulfilled]: (state, action) => {
      state.status = "succeeded";
      // Add any fetched layers to the array
      state.species = state.species.concat(action.payload);
      state.species.forEach((element, index) => {
        // check if env variable to set initial species list exists.
        // if not, use first 6
        if (INITIAL_SPECIES_LIST) {
          if (INITIAL_SPECIES_LIST.includes(element.id)) {
            element.visibility = true;
          } else {
            element.visibility = false;
          }
        } else {
          if (index < 6) {
            element.visibility = true;
          } else {
            element.visibility = false;
          }
        }
      });
    },
    [fetchHabSpecies.rejected]: (state, action) => {
      state.status = "failed";
      state.error = action.error.message;
    },
  },
});

// Action creators are generated for each case reducer function
export const {
  changeSpeciesVisibility,
  changeSpeciesColor,
  changeSpeciesActiveOption,
  setAllSpeciesVisibility,
} = habSpeciesSlice.actions;

export default habSpeciesSlice.reducer;

// Selector functions
// return all species
export const selectAllSpecies = (state) => state.habSpecies.species;

// return only the currently selected/visible species
export const selectVisibleSpecies = createSelector(
  (state) => state.habSpecies.species,
  (items) => items.filter((item) => item.visibility)
);

// get species by syndrome
export const selectSpeciesBySyndrome = (state, syndrome) =>
  state.habSpecies.species.filter((item) => item.syndrome === syndrome);

// get species by enviroment
export const selectSpeciesByEnvironment = (state, environment) =>
  state.habSpecies.species.filter(
    (item) => item.speciesEnvironment === environment
  );

// get species by type
export const selectSpeciesByType = (state, species_type) =>
  state.habSpecies.species.filter((item) => item.speciesType === species_type);
