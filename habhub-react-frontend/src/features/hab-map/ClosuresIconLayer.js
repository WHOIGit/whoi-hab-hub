import React, { useState, useEffect } from "react";
import { Source, Layer } from "react-map-gl";

export default function ClosuresIconLayer({ layerID, results }) {
  const [labels, setLabels] = useState();

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
    }
  }, [results]);

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
      {labels && (
        <Source
          id={layerID + "-labels-src"}
          key={layerID + "-labels-src"}
          type="geojson"
          data={labels}
        >
          <Layer {...layerClosuresIcons} key={layerID} />
        </Source>
      )}
    </div>
  );
}
