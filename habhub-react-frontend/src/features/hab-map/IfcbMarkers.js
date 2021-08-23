import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/core/styles";
import { Source, Layer } from "react-map-gl";
import { format, parseISO } from "date-fns";
import { CircularProgress } from "@material-ui/core";

import axiosInstance from "../../app/apiAxios";
import IfcbMarkerIcon from "./IfcbMarkerIcon";
import { selectMaxMeanOption } from "../data-layers/dataLayersSlice";
import { selectVisibleSpecies } from "../hab-species/habSpeciesSlice";

// eslint-disable-next-line no-unused-vars
const useStyles = makeStyles(theme => ({
  placeholder: {
    position: "absolute",
    left: "50%",
    top: "40%"
  }
}));

function IfcbMarkers({ onMarkerClick, metricName }) {
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
    async function fetchResults() {
      try {
        const params = new URLSearchParams({
          start_date: format(parseISO(dateFilter.startDate), "MM/dd/yyyy"),
          end_date: format(parseISO(dateFilter.endDate), "MM/dd/yyyy"),
          seasonal: dateFilter.seasonal,
          exclude_month_range: dateFilter.excludeMonthRange,
          smoothing_factor: dateFilter.smoothingFactor
        });
        const res = await axiosInstance.get("api/v1/ifcb-datasets/", {
          params
        });
        console.log(res.request.responseURL);
        setIsLoaded(true);
        setResults(res.data);
      } catch (error) {
        setIsLoaded(true);
        setError(error);
      }
    }
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
        const speciesItem = feature.properties.maxMeanValues.find(
          data => item.id === data.species
        );

        const maxMeanItem = speciesItem.data.find(
          data => data.metricName === metricName
        );
        let value = maxMeanItem.maxValue;

        if (showMaxMean === "mean") {
          value = maxMeanItem.meanValue;
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
