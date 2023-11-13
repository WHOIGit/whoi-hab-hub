import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/core/styles";
import { Marker } from "react-map-gl";
import { format, parseISO } from "date-fns";
import axiosInstance from "../../app/apiAxios";
import StationsMarkerIcon from "./StationsMarkerIcon";
import { selectMaxMeanOption } from "../data-layers/dataLayersSlice";

// eslint-disable-next-line no-unused-vars
const useStyles = makeStyles((theme) => ({
  button: {
    background: "none",
    border: "none",
    cursor: "pointer",
  },
}));

export default function StationsMarkers({ onMarkerClick, metricID, layerID }) {
  const habSpecies = useSelector((state) => state.habSpecies.species);
  const dateFilter = useSelector((state) => state.dateFilter);
  const showMaxMean = useSelector(selectMaxMeanOption);
  const classes = useStyles();

  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();

  useEffect(() => {
    async function fetchResults() {
      try {
        const params = new URLSearchParams({
          start_date: format(parseISO(dateFilter.startDate), "yyyy-MM-dd"),
          end_date: format(parseISO(dateFilter.endDate), "yyyy-MM-dd"),
          seasonal: dateFilter.seasonal,
          exclude_month_range: dateFilter.excludeMonthRange,
          smoothing_factor: 6,
        });
        const res = await axiosInstance.get("api/v1/stations/", { params });
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

  function renderMarker(feature) {
    const visibleSpecies = habSpecies.filter(
      (species) =>
        species.visibility && feature.properties.habSpecies.includes(species.id)
    );

    let maxMeanValue;
    if (feature.properties.maxMeanValues.length) {
      if (showMaxMean === "mean") {
        maxMeanValue = feature.properties.maxMeanValues[0].meanValue;
      } else {
        maxMeanValue = feature.properties.maxMeanValues[0].maxValue;
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
            onClick={(event) =>
              onMarkerClick(event, feature, layerID, metricID)
            }
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
