/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { Source, Layer } from "react-map-gl";
import { format, parseISO } from "date-fns";
// local imports
import IfcbSpatialMarkerGrid from "./IfcbSpatialMarkerGrid";
import { selectMaxMeanOption } from "../data-layers/dataLayersSlice";
import { selectVisibleSpecies } from "../hab-species/habSpeciesSlice";
import axiosInstance from "../../app/apiAxios";

export default function SpatialGridMarkers({
  onMarkerClick,
  gridLength,
  metricID,
  layerID,
}) {
  const visibleSpecies = useSelector(selectVisibleSpecies);
  const habSpecies = useSelector((state) => state.habSpecies.species);
  const dateFilter = useSelector((state) => state.dateFilter);
  const showMaxMean = useSelector(selectMaxMeanOption);
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();

  useEffect(() => {
    async function fetchResults() {
      try {
        const params = new URLSearchParams({
          start_date: format(parseISO(dateFilter.startDate), "MM/dd/yyyy"),
          end_date: format(parseISO(dateFilter.endDate), "MM/dd/yyyy"),
          seasonal: dateFilter.seasonal,
          exclude_month_range: dateFilter.excludeMonthRange,
          smoothing_factor: 4,
          grid_level: gridLength,
        });
        const res = await axiosInstance.get("api/v1/ifcb-spatial-grid/", {
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
  }, [dateFilter, gridLength]);

  function renderIconGrid(feature, showMaxMean) {
    // create new Array with Visible Species/Values
    if (!feature.properties.maxMeanValues.length) {
      return null;
    }

    const speciesValues = visibleSpecies.map((item) => {
      const speciesItem = feature.properties.maxMeanValues.find(
        (data) => item.id === data.species
      );

      const maxMeanItem = speciesItem.data.find(
        (data) => data.metricId === metricID
      );
      let value = maxMeanItem?.maxValue;

      if (showMaxMean === "mean") {
        value = maxMeanItem?.meanValue;
      }

      if (!value) {
        return null;
      }

      return {
        species: item.id,
        value: value,
        color: item.primaryColor,
      };
    });
    //.sort((a, b) => (a.value < b.value ? 1 : -1));

    if (!speciesValues.length) {
      return null;
    }

    return (
      <div className="gridSquare">
        <IfcbSpatialMarkerGrid
          feature={feature}
          layerID={layerID}
          speciesValues={speciesValues}
          onMarkerClick={onMarkerClick}
          metricID={metricID}
          key={feature.properties.geohash}
        />
      </div>
    );
  }

  if (results == null) {
    return null;
  }
  return (
    <div>
      {results.features.map((feature) => renderIconGrid(feature, showMaxMean))}
    </div>
  );
}
