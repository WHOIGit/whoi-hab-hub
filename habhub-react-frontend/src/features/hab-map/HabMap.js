/* eslint-disable no-unused-vars */
import React, { useState, useRef, useEffect } from "react";
import { useSelector } from "react-redux";
import MapGL, { NavigationControl, ScaleControl } from "react-map-gl";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
// Material UI imports
import { makeStyles } from "@material-ui/styles";
// Import our stuff
import DashBoard from "../dashboard/DashBoard";
import DataPanel from "./data-panels/DataPanel";
import StationsMarkers from "./StationsMarkers";
import IfcbMarkers from "./IfcbMarkers";
import ClosuresLayer from "./ClosuresLayer";
import LowerLeftPanel from "../../components/LowerLeftPanel";
import DisclaimerBox from "../../components/DisclaimerBox";
import {
  selectVisibleLayers,
  selectVisibleLayerIds
} from "../data-layers/dataLayersSlice";

// eslint-disable-next-line no-undef
const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN;
const interactiveLayerIds = ["closures-layer"];

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

export default function HabMap({
  showControls,
  setShowControls,
  showDateControls,
  setShowDateControls
}) {
  const classes = useStyles();
  const [viewport, setViewport] = useState({
    latitude: 42.89,
    longitude: -69.75,
    width: "100%",
    height: "100vh",
    zoom: 6.7
  });

  const visibleLayers = useSelector(selectVisibleLayers);
  const visibleLayerIds = useSelector(selectVisibleLayerIds);
  const [features, setFeatures] = useState([]);
  // eslint-disable-next-line no-unused-vars
  const [yAxisScale, setYAxisScale] = useState("linear");
  const [visibleLegends, setVisibleLegends] = useState([
    "stations-layer",
    "ifcb-layer"
  ]);
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
    const mapFeatures = mapRef.current.queryRenderedFeatures(event.point, {
      layers: interactiveLayerIds
    });
    const feature = mapFeatures[0];

    if (feature !== undefined) {
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

  const renderMarkerLayer = layer => {
    if (layer.id === "stations-layer") {
      return (
        <StationsMarkers
          onMarkerClick={onMarkerClick}
          visibility={layer.visibility}
          key={layer.id}
        />
      );
    } else if (layer.id === "closures-layer") {
      return <ClosuresLayer key={layer.id} />;
    } else if (layer.id === "ifcb-layer") {
      return <IfcbMarkers onMarkerClick={onMarkerClick} key={layer.id} />;
    } else {
      return;
    }
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <div>
        {features && (
          <div className={classes.dataPanelContainer}>
            {features.map(feature => (
              <DataPanel
                key={feature.id}
                featureID={feature.id}
                dataLayer={feature.layer}
                yAxisScale={yAxisScale}
                onPaneClose={onPaneClose}
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
              {visibleLayers.map(layer => renderMarkerLayer(layer))}
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
          <DashBoard
            showControls={showControls}
            setShowControls={setShowControls}
            showDateControls={showDateControls}
            setShowDateControls={setShowDateControls}
            visibleLegends={visibleLegends}
            setVisibleLegends={setVisibleLegends}
          />
        </div>

        <div>
          <LowerLeftPanel
            visibleLegends={visibleLegends}
            setVisibleLegends={setVisibleLegends}
          />
        </div>

        <div>
          <DisclaimerBox />
        </div>
      </div>
    </DndProvider>
  );
}
