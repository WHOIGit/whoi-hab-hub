/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { Source, Layer } from "react-map-gl";
import { format, parseISO } from "date-fns";
import { v4 as uuidv4 } from "uuid";
import squareGrid from "@turf/square-grid";
import centroid from "@turf/centroid";
import pointsWithinPolygon from "@turf/points-within-polygon";
import * as turfHelpers from "@turf/helpers";
import * as turfMeta from "@turf/meta";
import { selectActiveGridSquaresByZoom } from "./spatialGridSlice";
const API_URL = process.env.REACT_APP_API_URL;

export default function SpatialBinsLayer({
  onMarkerClick,
  mapBounds,
  gridZoom
}) {
  console.log(gridZoom);
  const dateFilter = useSelector(state => state.dateFilter);
  const gridSquares = useSelector(state =>
    selectActiveGridSquaresByZoom(state, gridZoom.gridLength)
  );
  const [dataSquares, setDataSquares] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();

  const layerGrid = {
    id: "grid-layer",
    type: "circle",
    source: "grid-src",
    paint: {
      "circle-radius": 3,
      "circle-color": "#223b53",
      "circle-stroke-color": "white",
      "circle-stroke-width": 1,
      "circle-opacity": 0.5
    },
    layout: {
      visibility: "visible"
    }
  };

  useEffect(() => {
    function getFetchUrl() {
      const baseURL = API_URL + "api/v1/ifcb-bins/";
      // build API URL to get set Date Filter
      const filterURL =
        baseURL +
        "?" +
        new URLSearchParams({
          start_date: format(parseISO(dateFilter.startDate), "MM/dd/yyyy"),
          end_date: format(parseISO(dateFilter.endDate), "MM/dd/yyyy"),
          seasonal: dateFilter.seasonal,
          exclude_month_range: dateFilter.excludeMonthRange,
          smoothing_factor: 8
        });
      return filterURL;
    }

    function fetchResults() {
      const url = getFetchUrl();
      console.log(url);
      fetch(url)
        .then(res => res.json())
        .then(
          result => {
            console.log(result);
            setIsLoaded(true);
            setResults(result);
          },
          // Note: it's important to handle errors here
          // instead of a catch() block so that we don't swallow
          // exceptions from actual bugs in components.
          error => {
            setIsLoaded(true);
            setError(error);
          }
        );
    }
    fetchResults();
  }, [dateFilter]);

  useEffect(() => {
    // use API Bin results to collect Bin points within the local redux spatialGrid squares
    // transform grid squares to centroids, calculate max/mean
    /*

    const activeSquares = gridSquares.reduce((acc, item) => {
      const ptsWithin = pointsWithinPolygon(results, item);
      if (ptsWithin.features.length) {
        const centerPnt = centroid(item);
        centerPnt.properties.id = item.id;
        acc.push(centerPnt);
      }
      return acc;
    }, []);
    */
    const squareFeatures = turfHelpers.featureCollection(gridSquares);
    console.log(squareFeatures);
    setDataSquares(squareFeatures);
  }, [results, gridZoom]);

  if (dataSquares == null) {
    return null;
  }
  return (
    <div>
      <Source id="grid-src" type="geojson" data={dataSquares}>
        <Layer {...layerGrid} key="grid-layer" />
      </Source>
    </div>
  );
}
