import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import makeStyles from '@mui/styles/makeStyles';
import { Marker } from "react-map-gl";
import { format, parseISO } from "date-fns";
import { CircularProgress } from "@mui/material";

import IfcbMarkerTrianglesGrid from "./IfcbMarkerTrianglesGrid";
import axiosInstance from "../../app/apiAxios";
// eslint-disable-next-line no-unused-vars
import IfcbMarkerIcon from "./IfcbMarkerIcon";
import {
  selectMaxMeanOption,
  selectVisibleLayerIds,
} from "../data-layers/dataLayersSlice";
import { selectVisibleSpecies } from "../hab-species/habSpeciesSlice";
import { DATA_LAYERS } from "../../Constants";

// eslint-disable-next-line no-unused-vars
const useStyles = makeStyles((theme) => ({
  placeholder: {
    position: "absolute",
    left: "50%",
    top: "40%",
  },
  circleMarker: {
    cursor: "pointer",
    width: "22px",
    height: "22px",
    borderRadius: "50%",
    borderColor: "#1976d2",
    borderWidth: "2px",
    borderStyle: "solid",
    backgroundColor: "#90caf9",
  },
}));

export default function IfcbMarkers({ onMarkerClick, metricID, layerID }) {
  console.log(metricID);
  const visibleSpecies = useSelector(selectVisibleSpecies);
  const visibleLayerIds = useSelector(selectVisibleLayerIds);
  const dateFilter = useSelector((state) => state.dateFilter);
  const showMaxMean = useSelector(selectMaxMeanOption);

  const classes = useStyles();
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();
  const [showGlyphs, setShowGlyphs] = useState(true);

  // check if the Spatial Grid layer is visible,
  // if so need to hide the triangle glyphs
  useEffect(() => {
    if (
      visibleLayerIds.includes(DATA_LAYERS.cellConcentrationSpatialGridLayer)
    ) {
      setShowGlyphs(false);
    } else {
      setShowGlyphs(true);
    }
  }, [visibleLayerIds]);

  useEffect(() => {
    async function fetchResults() {
      try {
        const params = new URLSearchParams({
          start_date: format(parseISO(dateFilter.startDate), "MM/dd/yyyy"),
          end_date: format(parseISO(dateFilter.endDate), "MM/dd/yyyy"),
          seasonal: dateFilter.seasonal,
          exclude_month_range: dateFilter.excludeMonthRange,
          smoothing_factor: dateFilter.smoothingFactor,
        });
        const res = await axiosInstance.get("api/v1/ifcb-datasets/", {
          params,
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

  const renderSquaresGrid = (feature, showMaxMean) => {
    // create new Array with Visible Species/Values
    if (feature.properties.maxMeanValues.length) {
      const speciesValues = visibleSpecies.map((item) => {
        const speciesItem = feature.properties.maxMeanValues.find(
          (data) => item.id === data.species
        );

        const maxMeanItem = speciesItem.data.find(
          (data) => data.metricId === metricID
        );
        let value = maxMeanItem.maxValue;

        if (showMaxMean === "mean") {
          value = maxMeanItem.meanValue;
        }

        return {
          species: item.id,
          value: value,
          color: item.primaryColor,
        };
      });
      //.sort((a, b) => (a.value < b.value ? 1 : -1));

      if (speciesValues.length) {
        return (
          <IfcbMarkerTrianglesGrid
            feature={feature}
            layerID={layerID}
            speciesValues={speciesValues}
            onMarkerClick={onMarkerClick}
            metricID={metricID}
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

  const renderCircleMarker = (feature) => {
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
          onClick={(event) => onMarkerClick(event, feature, layerID, metricID)}
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
          {showGlyphs &&
            results.features.map((feature) =>
              renderSquaresGrid(feature, showMaxMean)
            )}

          {results.features.map((feature) => renderCircleMarker(feature))}
        </div>
      )}
    </div>
  );
}
