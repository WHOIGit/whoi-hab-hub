/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/core/styles";
import { Marker } from "react-map-gl";
import { format, parseISO } from "date-fns";
import IfcbSpatialMarkerGrid from "./IfcbSpatialMarkerGrid";
import SquareMarker from "../../images/square-orange.svg";
import { selectMaxMeanOption } from "../data-layers/dataLayersSlice";
import { selectVisibleSpecies } from "../hab-species/habSpeciesSlice";

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
  const visibleSpecies = useSelector(selectVisibleSpecies);
  const habSpecies = useSelector(state => state.habSpecies.species);
  const dateFilter = useSelector(state => state.dateFilter);
  const showMaxMean = useSelector(selectMaxMeanOption);

  const classes = useStyles();
  const layerID = "ifcb-spatial-layer";
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();

  useEffect(() => {
    function getFetchUrl() {
      const baseURL = API_URL + "api/v1/ifcb-datasets-spatial/";
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

  function renderIconGrid(feature, showMaxMean) {
    // create new Array with Visible Species/Values
    if (!feature.properties.maxMeanValues.length) {
      return null;
    }
    const speciesValues = visibleSpecies.map(item => {
      const maxMeanItem = feature.properties.maxMeanValues.filter(
        data => item.id === data.species
      );
      let value = maxMeanItem[0].maxValue;

      if (showMaxMean === "mean") {
        value = maxMeanItem[0].meanValue;
      }

      return {
        species: item.id,
        value: value,
        color: item.primaryColor
      };
    });
    //.sort((a, b) => (a.value < b.value ? 1 : -1));

    if (!speciesValues.length) {
      return null;
    }
    return (
      <IfcbSpatialMarkerGrid
        feature={feature}
        layerID={layerID}
        speciesValues={speciesValues}
        onMarkerClick={onMarkerClick}
        key={feature.id}
      />
    );
  }

  function renderMarker(feature) {
    console.log(feature);
    return (
      <>
        <Marker
          key={feature.properties.s2Token}
          latitude={feature.geometry.coordinates[1]}
          longitude={feature.geometry.coordinates[0]}
          captureClick={true}
        >
          <div
            className={classes.button}
            onClick={event => onMarkerClick(event, feature, layerID)}
          >
            <img src={SquareMarker} alt="Grid point" />
          </div>
        </Marker>
      </>
    );
  }

  if (results === undefined) {
    return null;
  }
  return (
    <div>
      {results[0].features.map(feature => renderIconGrid(feature, showMaxMean))}
    </div>
  );
}
