/* eslint-disable no-unused-vars */
import React, { useState, useRef, useEffect } from "react";
import { useSelector } from "react-redux";
import MapGL, { NavigationControl, ScaleControl } from "react-map-gl";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
// Material UI imports
import { makeStyles } from "@material-ui/styles";
// Import our stuff
import DataPanel from "./data-panels/DataPanel";
import StationsMarkers from "./StationsMarkers";
import IfcbMarkers from "./IfcbMarkers";
import ClosuresLayer from "./ClosuresLayer";
import DisclaimerBox from "./DisclaimerBox";
import CurrentDateChip from "../date-filter/CurrentDateChip";
import {
  selectInteractiveLayerIds,
  selectVisibleLayerIds
} from "../data-layers/dataLayersSlice";

const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN;
const MAP_LATITUDE = parseFloat(process.env.REACT_APP_MAP_LATITUDE);
const MAP_LONGITUDE = parseFloat(process.env.REACT_APP_MAP_LONGITUDE);
const MAP_ZOOM = parseFloat(process.env.REACT_APP_MAP_ZOOM);

const navStyle = {
  position: "absolute",
  bottom: 72,
  left: 0,
  padding: "10px"
};

const scaleControlStyle = {
  position: "absolute",
  bottom: 36,
  left: 0,
  padding: "10px"
};

// eslint-disable-next-line no-unused-vars
const useStyles = makeStyles(theme => ({
  dataPanelContainer: {
    background: "none",
    position: "absolute",
    top: 0,
    left: 0,
    zIndex: 3000,
    maxHeight: "100vh",
    overflowY: "scroll"
  }
}));

export default function HabMap() {
  const classes = useStyles();
  const [viewport, setViewport] = useState({
    latitude: MAP_LATITUDE,
    longitude: MAP_LONGITUDE,
    zoom: MAP_ZOOM,
    width: "100%",
    height: "100vh"
  });

  const visibleLayerIds = useSelector(selectVisibleLayerIds);
  // only refers to map layer that use the Mapbox Layer/Source properties
  const interactiveLayerIds = useSelector(selectInteractiveLayerIds);
  const [features, setFeatures] = useState([]);
  // eslint-disable-next-line no-unused-vars
  const [yAxisScale, setYAxisScale] = useState("linear");
  const mapRef = useRef();

  useEffect(() => {
    const newFeatures = features.filter(feature =>
      visibleLayerIds.includes(feature.layer)
    );
    setFeatures(newFeatures);

    /*
    if (!event.target.checked) {
      const newLegends = visibleLegends.filter((item) => item !== layerID);
      setVisibleLegends(newLegends);
    }
    */
  }, [visibleLayerIds]);

  const onMapLoad = () => {
    const mapObj = mapRef.current.getMap();
    // Load the custom icon image from the 'public' directory for the Closures Layer
    mapObj.loadImage("images/icon-shellfish-closure.png", function(
      error,
      image
    ) {
      if (error) throw error;
      mapObj.addImage("icon-shellfish-closure", image);
    });
  };

  const onMapClick = event => {
    const mapFeatures = mapRef.current.queryRenderedFeatures(event.point);
    const feature = mapFeatures[0];

    if (
      feature !== undefined &&
      interactiveLayerIds.includes(feature.layer.id)
    ) {
      feature.layer = feature.layer.id;
      setFeatures([feature, ...features]);
    }
  };

  const onMarkerClick = (event, feature, layerID) => {
    feature.layer = layerID;
    setFeatures([feature, ...features]);
  };

  const onPaneClose = featureID => {
    const newFeatures = features.filter(feature => feature.id !== featureID);
    setFeatures(newFeatures);
  };

  const renderMarkerLayer = layerID => {
    if (layerID === "stations-layer") {
      return <StationsMarkers onMarkerClick={onMarkerClick} key={layerID} />;
    } else if (layerID === "closures-layer") {
      return <ClosuresLayer key={layerID} />;
    } else if (layerID === "ifcb-layer") {
      return (
        <IfcbMarkers
          onMarkerClick={onMarkerClick}
          metricName="cell_concentration"
          key={layerID}
        />
      );
    } else {
      return;
    }
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div>
        <div>
          <CurrentDateChip />
        </div>
        {features && (
          <div className={classes.dataPanelContainer}>
            {features.map(feature => (
              <DataPanel
                key={feature.id}
                featureID={feature.id}
                dataLayer={feature.layer}
                yAxisScale={yAxisScale}
                onPaneClose={onPaneClose}
                metricName="cell_concentration"
              />
            ))}
          </div>
        )}
        <div>
          <MapGL
            {...viewport}
            mapboxApiAccessToken={MAPBOX_TOKEN}
            mapStyle="mapbox://styles/mapbox/light-v10"
            onViewportChange={viewport => {
              setViewport(viewport);
            }}
            onClick={event => onMapClick(event)}
            onLoad={() => onMapLoad()}
            interactiveLayerIds={interactiveLayerIds}
            preserveDrawingBuffer={true}
            ref={mapRef}
          >
            <React.Fragment>
              {visibleLayerIds.reverse().map(layer => renderMarkerLayer(layer))}
            </React.Fragment>

            <div style={navStyle}>
              <NavigationControl />
            </div>
            <div style={scaleControlStyle}>
              <ScaleControl />
            </div>
          </MapGL>
        </div>

        <div>
          <DisclaimerBox />
        </div>
      </div>
    </DndProvider>
  );
}
