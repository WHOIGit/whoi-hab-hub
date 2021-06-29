import axios from "axios";
// eslint-disable-next-line no-unused-vars
import squareGrid from "@turf/square-grid";
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

const API_URL = process.env.REACT_APP_API_URL;

const initialState = {
  gridSquares: [],
  gridJson: {},
  cellSide: 100,
  status: "idle",
  error: null
};
// eslint-disable-next-line no-unused-vars
const createGridSquares = (bbox, cellSide) => {
  const options = { units: "kilometers" };
  const grid = squareGrid(bbox, cellSide, options);
  console.log(grid);
  return grid;
};

// API request for available dataLayers in HABhub
export const fetchBoundingBox = createAsyncThunk(
  "spatialGrid/fetchBoundingBox",
  async () => {
    const url = API_URL + "api/v1/spatial-cell-concentration/max-bounding-box/";
    const response = await axios.get(url);
    return response.data;
  }
);

export const spatialGridSlice = createSlice({
  name: "spatialGrid",
  initialState: initialState,
  reducers: {
    changeGridSquares: (state, action) => {
      state.gridSquares.forEach(element => {
        if (element.id == action.payload.layerID) {
          element.visibility = action.payload.checked;
        }
      });
    }
  },
  extraReducers: {
    [fetchBoundingBox.pending]: state => {
      state.status = "loading";
    },
    [fetchBoundingBox.fulfilled]: (state, action) => {
      state.status = "succeeded";
      const initialGrid = createGridSquares(
        action.payload.boundingBox,
        state.cellSide
      );
      state.gridJson = initialGrid;
      state.gridSquares = state.gridSquares.concat(initialGrid.features);
    },
    [fetchBoundingBox.rejected]: (state, action) => {
      state.status = "failed";
      state.error = action.error.message;
    }
  }
});

// Action creators are generated for each case reducer function
export const { changeGridSquares } = spatialGridSlice.actions;

export default spatialGridSlice.reducer;

// Selector functions
