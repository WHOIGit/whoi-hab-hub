/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { Source, Layer } from "react-map-gl";
import { format, parseISO } from "date-fns";
// eslint-disable-next-line no-undef
const API_URL = process.env.REACT_APP_API_URL;

export default function SpatialGridBinsLayer({
  onMarkerClick,
  mapBounds,
  gridZoom,
}) {
  console.log(gridZoom);
  const dateFilter = useSelector((state) => state.dateFilter);

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
      "circle-opacity": 0.5,
    },
    layout: {
      visibility: "visible",
    },
  };

  useEffect(() => {
    function getFetchUrl() {
      const baseURL = API_URL + "api/v1/ifcb-spatial-grid/";
      // build API URL to get set Date Filter
      const filterURL =
        baseURL +
        "?" +
        new URLSearchParams({
          start_date: format(parseISO(dateFilter.startDate), "MM/dd/yyyy"),
          end_date: format(parseISO(dateFilter.endDate), "MM/dd/yyyy"),
          seasonal: dateFilter.seasonal,
          exclude_month_range: dateFilter.excludeMonthRange,
          smoothing_factor: 8,
        });
      return filterURL;
    }

    function fetchResults() {
      const url = getFetchUrl();
      console.log(url);
      fetch(url)
        .then((res) => res.json())
        .then(
          (result) => {
            console.log(result);
            setIsLoaded(true);
            setResults(result);
          },
          // Note: it's important to handle errors here
          // instead of a catch() block so that we don't swallow
          // exceptions from actual bugs in components.
          (error) => {
            setIsLoaded(true);
            setError(error);
          }
        );
    }
    fetchResults();
  }, [dateFilter]);

  if (results == null) {
    return null;
  }
  return (
    <div>
      <Source id="grid-src" type="geojson" data={results}>
        <Layer {...layerGrid} key="grid-layer" />
      </Source>
    </div>
  );
}
