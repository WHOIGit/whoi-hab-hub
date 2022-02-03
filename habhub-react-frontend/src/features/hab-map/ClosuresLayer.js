import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { Source, Layer } from "react-map-gl";
import { format, parseISO } from "date-fns";
import { makeStyles } from "@material-ui/styles";
import { CircularProgress } from "@material-ui/core";

import axiosInstance from "../../app/apiAxios";
import { DATA_LAYERS } from "../../Constants";

// eslint-disable-next-line no-unused-vars
const useStyles = makeStyles((theme) => ({
  placeholder: {
    position: "absolute",
    left: "50%",
    top: "40%",
  },
}));

export default function ClosuresLayer({ layerID }) {
  console.log(layerID);
  const dateFilter = useSelector((state) => state.dateFilter);
  const classes = useStyles();
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();
  const [labels, setLabels] = useState();

  useEffect(() => {
    async function fetchResults() {
      let layerStates;
      if (layerID === DATA_LAYERS.closuresLayer) {
        layerStates = "MA,NH";
      } else if (layerID === DATA_LAYERS.closuresSeasonalLayer) {
        layerStates = "ME";
      }

      try {
        const params = new URLSearchParams({
          start_date: format(parseISO(dateFilter.startDate), "MM/dd/yyyy"),
          end_date: format(parseISO(dateFilter.endDate), "MM/dd/yyyy"),
          seasonal: dateFilter.seasonal,
          exclude_month_range: dateFilter.excludeMonthRange,
          smoothing_factor: dateFilter.smoothingFactor,
          states: layerStates,
        });
        const res = await axiosInstance.get("api/v1/closures/", {
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

  // Need to create a new data source/layer to put label on polygon centroid
  // update the Labels text layer when API results change
  useEffect(() => {
    if (results) {
      const centerPoints = results.features.map((item) => {
        const point = {
          type: "Feature",
          properties: {
            name: item.properties.name,
            //"count": item.properties.closures.length
          },
          geometry: item.properties.geomCenterPoint,
        };
        return point;
      });

      const labelsGeojson = {
        type: "FeatureCollection",
        features: centerPoints,
      };
      setLabels(labelsGeojson);
      console.log(labelsGeojson);
    }
  }, [results]);

  // update map color for different layers
  let layerColor = "orange";
  if (layerID === DATA_LAYERS.closuresSeasonalLayer) {
    layerColor = "#FFEB3B";
  }

  // Set default layer styles
  const layerClosures = {
    id: layerID,
    type: "fill",
    source: "closures-src",
    paint: {
      "fill-color": layerColor,
      "fill-opacity": 0.5,
      "fill-outline-color": "#fc4e2a",
    },
    layout: {
      visibility: "visible",
    },
  };
  /*
  const layerLabels = {
    id: 'closures-labels-layer',
    type: 'symbol',
    source: 'closures-labels-src',
    layout: {
      'visibility': 'visible',
      'text-field': ['get', 'count'],
      'text-font': ['DIN Offc Pro Medium', 'Arial Unicode MS Bold'],
      'text-size': 12
    }

  const layerLabelCircles = {
    id: 'closures-labels-circles-layer',
    type: 'circle',
    source: 'closures-labels-src',
    paint: {
      'circle-color': '#fed976',
      'circle-radius': 8,
      'circle-stroke-width': 0,
      'circle-stroke-color': '#feb24c'
    },
    layout: {
      'visibility': 'visible'
    }
  }
  */
  const layerClosuresIcons = {
    id: layerID + "-icons-layer",
    type: "symbol",
    source: layerID + "-labels-src",
    layout: {
      "icon-image": "icon-shellfish-closure",
      "icon-allow-overlap": false,
      visibility: "visible",
    },
  };

  return (
    <div>
      {!isLoaded && (
        <div className={classes.placeholder}>
          <CircularProgress />
        </div>
      )}

      <React.Fragment>
        {results && (
          <Source
            id={layerID + "-src"}
            type="geojson"
            data={results}
            buffer={10}
            maxzoom={12}
          >
            <Layer {...layerClosures} />
          </Source>
        )}

        {labels && (
          <Source id={layerID + "-labels-src"} type="geojson" data={labels}>
            <Layer {...layerClosuresIcons} key={layerID} />
          </Source>
        )}
      </React.Fragment>
    </div>
  );
}
