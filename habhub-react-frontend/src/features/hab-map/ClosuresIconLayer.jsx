/* eslint-disable no-unused-vars */
import React, { useState, useEffect } from "react";
import { Source, Layer } from "react-map-gl";
import { useMap } from "react-map-gl";
import { DATA_LAYERS } from "../../Constants";

export default function ClosuresIconLayer({ layerID, results }) {
  const [labels, setLabels] = useState();
  const { current: map } = useMap();

  if (!map.hasImage("icon-shellfish-closure")) {
    map.loadImage("images/icon-shellfish-closure.png", (error, image) => {
      if (error) throw error;
      if (!map.hasImage("icon-shellfish-closure")) {
        console.log(layerID, "Load icon image closure");
        map.addImage("icon-shellfish-closure", image);
      }
    });
  }
  // Need to create a new data source/layer to put label on polygon centroid
  // update the Labels text layer when API results change
  useEffect(() => {
    if (results) {
      const centerPoints = results.features.map((item) => {
        const point = {
          type: "Feature",
          id: item.id,
          properties: {
            name: item.properties.name,
            layerID: layerID,
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

  return (
    <div>
      {labels && (
        <Source
          id={layerID + "-labels-src"}
          key={layerID + "-labels-src"}
          type="geojson"
          data={labels}
        >
          <Layer
            id={layerID + "_icons"}
            type="symbol"
            source={layerID + "-labels-src"}
            layout={{
              "icon-image": "icon-shellfish-closure",
              "icon-allow-overlap": false,
              //visibility: "visible",
            }}
            key={layerID}
          />
        </Source>
      )}
    </div>
  );
}
