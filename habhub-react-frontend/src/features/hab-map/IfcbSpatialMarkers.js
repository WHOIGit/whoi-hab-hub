/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/core/styles";
import { Marker } from "react-map-gl";
import { format, parseISO } from "date-fns";

import SquareMarker from "../../images/square-orange.svg";

// eslint-disable-next-line no-undef
const API_URL = process.env.REACT_APP_API_URL;

// eslint-disable-next-line no-unused-vars
const useStyles = makeStyles(theme => ({
  button: {
    background: "none",
    border: "none",
    cursor: "pointer",
    width: "12px",
    height: "12px"
  }
}));

export default function IfcbSpatialMarkers({ onMarkerClick }) {
  const habSpecies = useSelector(state => state.habSpecies.species);
  const dateFilter = useSelector(state => state.dateFilter);

  const classes = useStyles();
  const layerID = "ifcb-spatial-layer";
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();

  useEffect(() => {
    function getFetchUrl() {
      const baseURL = API_URL + "api/v1/ifcb-datasets-spatial/5/";
      // build API URL to get set Date Filter
      const filterURL =
        baseURL +
        "?" +
        new URLSearchParams({
          start_date: format(parseISO(dateFilter.startDate), "MM/dd/yyyy"),
          end_date: format(parseISO(dateFilter.endDate), "MM/dd/yyyy"),
          seasonal: dateFilter.seasonal,
          exclude_month_range: dateFilter.excludeMonthRange,
          smoothing_factor: dateFilter.smoothingFactor
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

  function renderMarker(feature) {
    console.log(feature);
    return (
      <Marker
        key={feature.token}
        latitude={feature.lat}
        longitude={feature.long}
        captureClick={true}
      >
        <div
          className={classes.button}
          onClick={event => onMarkerClick(event, feature, layerID)}
        >
          <img src={SquareMarker} alt="Grid point" />
        </div>
      </Marker>
    );
  }

  return (
    <div>
      {results &&
        results.gridCenterPoints.map(feature => renderMarker(feature))}
    </div>
  );
}
