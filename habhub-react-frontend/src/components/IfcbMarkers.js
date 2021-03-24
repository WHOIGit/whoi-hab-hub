import React, { useState, useEffect } from "react";
import { makeStyles } from "@material-ui/core/styles";
import { Source, Layer } from "react-map-gl";
import { format } from "date-fns";
import { CircularProgress } from "@material-ui/core";

import IfcbMarkerIcon from "./IfcbMarkerIcon";

const API_URL = process.env.REACT_APP_API_URL;

// eslint-disable-next-line no-unused-vars
const useStyles = makeStyles((theme) => ({
  placeholder: {
    position: "absolute",
    left: "50%",
    top: "40%",
  },
}));

function IfcbMarkers({
  habSpecies,
  onMarkerClick,
  dateFilter,
  smoothingFactor,
  visibility,
  showMaxMean,
}) {
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
          start_date: format(dateFilter.startDate, "MM/dd/yyyy"),
          end_date: format(dateFilter.endDate, "MM/dd/yyyy"),
          seasonal: dateFilter.seasonal,
          exclude_month_range: dateFilter.exclude_month_range,
          smoothing_factor: smoothingFactor,
        });
      return filterURL;
    };

    const fetchResults = () => {
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
          // Note: it"s important to handle errors here
          // instead of a catch() block so that we don"t swallow
          // exceptions from actual bugs in components.
          (error) => {
            setIsLoaded(true);
            setError(error);
          }
        );
    };
    fetchResults();
  }, [dateFilter]);

  useEffect(() => {
    const visibleSpecies = habSpecies.filter((species) => species.visibility);
    const radiusFactor = visibleSpecies.length > 3 ? 3 : visibleSpecies.length;
    const newRadius = 8 * radiusFactor;
    setCircleRadius(newRadius);
  }, [habSpecies]);

  const layerIfcbCircles = {
    id: "ifcb-circles-layer",
    type: "circle",
    source: "ifcb-circles-src",
    paint: {
      "circle-opacity": 0,
      "circle-radius": circleRadius,
      "circle-stroke-width": 4,
      "circle-stroke-color": "#467fcf",
    },
    layout: {
      visibility: "visible",
    },
  };

  function renderMarker(feature, showMaxMean) {
    // create new Array with Visible Species/Values
    if (feature.properties.max_mean_values.length) {
      const speciesValues = habSpecies
        .filter((species) => species.visibility)
        .map((item) => {
          const maxMeanItem = feature.properties.max_mean_values.filter(
            (data) => item.id === data.species
          );
          let value = maxMeanItem[0].max_value;

          if (showMaxMean === "mean") {
            value = maxMeanItem[0].mean_value;
          }

          return {
            species: item.id,
            value: value,
            color: item.colorPrimary,
          };
        });

      if (speciesValues.length) {
        return (
          <IfcbMarkerIcon
            feature={feature}
            layerID={layerID}
            speciesValues={speciesValues}
            onMarkerClick={onMarkerClick}
          />
        );
      } else {
        return;
      }
    } else {
      return;
    }
  }

  if (visibility) {
    return (
      <div>
        {!isLoaded && (
          <div className={classes.placeholder}>
            <CircularProgress />
          </div>
        )}

        {results && (
          <div>
            {results.features.map((feature) =>
              renderMarker(feature, showMaxMean)
            )}

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
  } else {
    return null;
  }
}

export default IfcbMarkers;
