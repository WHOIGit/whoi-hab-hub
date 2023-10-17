/* eslint-disable no-unused-vars */
import axios from "axios";
import { v4 as uuidv4 } from "uuid";
import squareGrid from "@turf/square-grid";
import bboxPolygon from "@turf/bbox-polygon";
import booleanIntersects from "@turf/boolean-intersects";
import * as turfMeta from "@turf/meta";
import { createSlice, createAsyncThunk } from "@reduxjs/toolkit";

const API_URL = import.meta.env.VITE_API_URL;

const gridLengths = [40, 70, 150];
const initialState = {
  gridSquares: [],
  gridBoundingBox: [],
  gridJson: {},
  cellSide: 70,
  status: "idle",
  error: null,
};

const createGridSquares = (bbox) => {
  const options = {
    units: "kilometers",
    properties: { isActive: false },
  };
  const newGrid = gridLengths.map((item) => {
    const gridCollection = squareGrid(bbox, item, options);

    return gridCollection.features.map((feature) => {
      feature.id = uuidv4();
      feature.gridLength = item;
      return feature;
    });
  });
  console.log(newGrid.flat());
  return newGrid.flat();
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
    changeGridZoom: (state, action) => {
      const zoomRange = action.payload.zoomRange;
      console.log(zoomRange);
      const newGrid = createGridSquares(
        state.gridBoundingBox,
        zoomRange.gridLength
      );

      const mapPoly = bboxPolygon(state.gridBoundingBox);

      newGrid.forEach((item) => {
        if (booleanIntersects(item, mapPoly)) {
          item.properties.isActive = true;
        } else {
          item.properties.isActive = false;
        }
      });
      state.gridSquares = newGrid;
    },
    changeActiveGridSquares: (state, action) => {
      const bbox = action.payload.mapBounds;
      const mapPoly = bboxPolygon(bbox);
      state.gridSquares.forEach((item) => {
        if (booleanIntersects(item, mapPoly)) {
          item.properties.isActive = true;
        } else {
          item.properties.isActive = false;
        }
      });
    },
  },
  extraReducers: {
    [fetchBoundingBox.pending]: (state) => {
      state.status = "loading";
    },
    [fetchBoundingBox.fulfilled]: (state, action) => {
      state.status = "succeeded";
      const initialGrid = createGridSquares(action.payload.boundingBox);
      state.gridJson = initialGrid;
      state.gridBoundingBox = action.payload.boundingBox;
      state.gridSquares = state.gridSquares.concat(initialGrid);
    },
    [fetchBoundingBox.rejected]: (state, action) => {
      state.status = "failed";
      state.error = action.error.message;
    },
  },
});

// Action creators are generated for each case reducer function
export const { changeGridZoom, changeActiveGridSquares } =
  spatialGridSlice.actions;

export default spatialGridSlice.reducer;

// Selector functions

// return only the currently visible layers by Zoom level
export const selectActiveGridSquaresByZoom = (state, gridLength) => {
  const squares = state.spatialGrid.gridSquares.filter(
    (item) => item.properties.isActive && item.gridLength == gridLength
  );
  return squares;
};
