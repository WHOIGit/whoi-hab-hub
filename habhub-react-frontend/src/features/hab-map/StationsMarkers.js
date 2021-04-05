import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/core/styles";
import { Marker } from "react-map-gl";
import { format, parseISO } from "date-fns";

import StationsMarkerIcon from "./StationsMarkerIcon";
import { selectMaxMeanOption } from "../data-layers/dataLayersSlice";

// eslint-disable-next-line no-undef
const API_URL = process.env.REACT_APP_API_URL;

// eslint-disable-next-line no-unused-vars
const useStyles = makeStyles((theme) => ({
  button: {
    background: "none",
    border: "none",
    cursor: "pointer",
  },
}));

export default function StationsMarkers({ onMarkerClick }) {
  const habSpecies = useSelector((state) => state.habSpecies);
  const dateFilter = useSelector((state) => state.dateFilter);
  const showMaxMean = useSelector(selectMaxMeanOption);
  const classes = useStyles();
  const layerID = "stations-layer";
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();

  useEffect(() => {
    function getFetchUrl() {
      const baseURL = API_URL + "api/v1/stations/";
      // build API URL to get set Date Filter
      const filterURL =
        baseURL +
        "?" +
        new URLSearchParams({
          start_date: format(parseISO(dateFilter.startDate), "MM/dd/yyyy"),
          end_date: format(parseISO(dateFilter.endDate), "MM/dd/yyyy"),
          seasonal: dateFilter.seasonal,
          exclude_month_range: dateFilter.excludeMonthRange,
          smoothing_factor: dateFilter.smoothingFactor,
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

  function renderMarker(feature) {
    const visibleSpecies = habSpecies.filter(
      (species) =>
        species.visibility &&
        feature.properties.hab_species.includes(species.id)
    );

    let maxMeanValue;
    if (feature.properties.max_mean_values.length) {
      if (showMaxMean === "mean") {
        maxMeanValue = feature.properties.max_mean_values[0].mean_value;
      } else {
        maxMeanValue = feature.properties.max_mean_values[0].max_value;
      }
    }

    if (visibleSpecies.length && maxMeanValue) {
      return (
        <Marker
          key={feature.id}
          latitude={feature.geometry.coordinates[1]}
          longitude={feature.geometry.coordinates[0]}
          captureClick={true}
        >
          <div
            className={classes.button}
            onClick={(event) => onMarkerClick(event, feature, layerID)}
          >
            <StationsMarkerIcon maxMeanValue={maxMeanValue} />
          </div>
        </Marker>
      );
    } else {
      return;
    }
  }

  return (
    <div>
      {results && results.features.map((feature) => renderMarker(feature))}
    </div>
  );
}
