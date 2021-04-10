import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/core/styles";
import { Source, Layer } from "react-map-gl";
import { format, parseISO } from "date-fns";
import { CircularProgress } from "@material-ui/core";

import IfcbMarkerIcon from "./IfcbMarkerIcon";
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
  }
}));

function IfcbMarkers({ onMarkerClick }) {
  const visibleSpecies = useSelector(selectVisibleSpecies);
  const dateFilter = useSelector(state => state.dateFilter);
  const showMaxMean = useSelector(selectMaxMeanOption);
  const layerID = "ifcb-layer";
  const classes = useStyles();
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();
  const [circleRadius, setCircleRadius] = useState(12);

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

  useEffect(() => {
    const radiusFactor = visibleSpecies.length > 3 ? 3 : visibleSpecies.length;
    const newRadius = 8 * radiusFactor;
    setCircleRadius(newRadius);
  }, [visibleSpecies]);

  const layerIfcbCircles = {
    id: "ifcb-circles-layer",
    type: "circle",
    source: "ifcb-circles-src",
    paint: {
      "circle-opacity": 0,
      "circle-radius": circleRadius,
      "circle-stroke-width": 4,
      "circle-stroke-color": "#467fcf"
    },
    layout: {
      visibility: "visible"
    }
  };

  const renderMarker = (feature, showMaxMean) => {
    // create new Array with Visible Species/Values
    if (feature.properties.maxMeanValues.length) {
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

      if (speciesValues.length) {
        return (
          <IfcbMarkerIcon
            feature={feature}
            layerID={layerID}
            speciesValues={speciesValues}
            onMarkerClick={onMarkerClick}
            key={feature.id}
          />
        );
      } else {
        return;
      }
    } else {
      return;
    }
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
          {results.features.map(feature => renderMarker(feature, showMaxMean))}

          <Source
            id="ifcb-circles-src"
            type="geojson"
            data={results}
            buffer={10}
            maxzoom={12}
          >
            <Layer {...layerIfcbCircles} />
          </Source>
        </div>
      )}
    </div>
  );
}

export default IfcbMarkers;