import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/core/styles";
import { Marker } from "react-map-gl";
import { format, parseISO } from "date-fns";
import { CircularProgress } from "@material-ui/core";

import IfcbMarkerSquaresGrid from "./IfcbMarkerSquaresGrid";
import { selectMaxMeanOption } from "../data-layers/dataLayersSlice";
import { selectVisibleSpecies } from "../hab-species/habSpeciesSlice";

// eslint-disable-next-line no-undef
const API_URL = process.env.REACT_APP_API_URL;

// eslint-disable-next-line no-unused-vars
const useStyles = makeStyles(theme => ({
  placeholder: {
    position: "absolute",
    left: "50%",
    top: "40%"
  },
  circleMarker: {
    cursor: "pointer",
    width: "22px",
    height: "22px",
    borderRadius: "50%",
    borderColor: "#1976d2",
    borderWidth: "2px",
    borderStyle: "solid",
    backgroundColor: "#90caf9"
  }
}));

export default function IfcbMarkers({ onMarkerClick }) {
  const visibleSpecies = useSelector(selectVisibleSpecies);
  const dateFilter = useSelector(state => state.dateFilter);
  const showMaxMean = useSelector(selectMaxMeanOption);
  const layerID = "ifcb-layer";
  const classes = useStyles();
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();

  useEffect(() => {
    const getFetchUrl = () => {
      let baseURL = API_URL + "api/v1/ifcb-datasets/";
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
    };

    const fetchResults = () => {
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
          // Note: it"s important to handle errors here
          // instead of a catch() block so that we don"t swallow
          // exceptions from actual bugs in components.
          error => {
            setIsLoaded(true);
            setError(error);
          }
        );
    };
    fetchResults();
  }, [dateFilter]);

  const renderSquaresGrid = (feature, showMaxMean) => {
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
      <IfcbMarkerSquaresGrid
        feature={feature}
        layerID={layerID}
        speciesValues={speciesValues}
        onMarkerClick={onMarkerClick}
        key={feature.id}
      />
    );
  };

  const renderCircleMarker = feature => {
    return (
      <Marker
        key={feature.id}
        latitude={feature.geometry.coordinates[1]}
        longitude={feature.geometry.coordinates[0]}
        offsetTop={-10}
        offsetLeft={-10}
        captureClick={true}
      >
        <div
          className={classes.circleMarker}
          onClick={event => onMarkerClick(event, feature, layerID)}
        ></div>
      </Marker>
    );
  };

  return (
    <div>
      {!isLoaded && (
        <div className={classes.placeholder}>
          <CircularProgress />
        </div>
      )}

      {results && (
        <div>
          {results.features.map(feature =>
            renderSquaresGrid(feature, showMaxMean)
          )}
          {results.features.map(feature => renderCircleMarker(feature))}
        </div>
      )}
    </div>
  );
}
