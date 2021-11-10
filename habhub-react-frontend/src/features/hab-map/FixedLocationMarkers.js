import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/core/styles";
import { Marker } from "react-map-gl";
import { format, parseISO } from "date-fns";
import { CircularProgress } from "@material-ui/core";

import axiosInstance from "../../app/apiAxios";

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
  const dateFilter = useSelector((state) => state.dateFilter);

  const classes = useStyles();
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
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
          {results.features.map((feature) => renderCircleMarker(feature))}
        </div>
      )}
    </div>
  );
}
