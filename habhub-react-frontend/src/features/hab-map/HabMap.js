/* eslint-disable no-unused-vars */
import React, { useState, useRef, useEffect } from "react";
import { useSelector } from "react-redux";
import MapGL, {
  NavigationControl,
  ScaleControl,
  Source,
  Layer
} from "react-map-gl";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
// Material UI imports
import { makeStyles } from "@material-ui/styles";
// Import our stuff
import DataPanel from "./data-panels/DataPanel";
import StationsMarkers from "./StationsMarkers";
import IfcbMarkers from "./IfcbMarkers";
import IfcbSpatialMarkers from "./IfcbSpatialMarkers";
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
  const gridJson = useSelector(state => state.spatialGrid.gridJson);
  const gridSquares = useSelector(state => state.spatialGrid.gridSquares);
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
  const [mapBounds, setMapBounds] = useState(null);
  const [gridZoomRange, setGridZoomRange] = useState([
    { gridLength: 15, maxZoom: 100, minZoom: 8, isActive: false },
    { gridLength: 30, maxZoom: 8, minZoom: 7, isActive: false },
    { gridLength: 60, maxZoom: 7, minZoom: 6, isActive: true },
    { gridLength: 120, maxZoom: 6, minZoom: 5, isActive: false },
    { gridLength: 240, maxZoom: 5, minZoom: 0, isActive: false }
  ]);
  // eslint-disable-next-line no-unused-vars
  const [yAxisScale, setYAxisScale] = useState("linear");
  const mapRef = useRef();

  const getGridZoomRange = () => {
    const zoom = gridZoomRange.filter(item => item.isActive)[0];
    return zoom;
  };

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

  useEffect(() => {
    console.log(gridZoomRange);
    if (gridSquares !== null) {
      /*
      const mapObj = mapRef.current.getMap();
      console.log(viewport.zoom);
      // Get the initial map bounds, set state to load spatial data
      const bounds = mapObj.getBounds();
      setMapBounds(bounds);
      */
    }
  }, [gridZoomRange]);

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
    // Get the initial map bounds, set state to load spatial data
    const bounds = mapObj.getBounds();
    setMapBounds(bounds);
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
        <div>
          {gridSquares.map((item, index) => (
            <IfcbSpatialMarkers
              onMarkerClick={onMarkerClick}
              mapBounds={mapBounds}
              gridSquare={item}
              key={index}
            />
          ))}
        </div>
      );
      //return <IfcbMarkers onMarkerClick={onMarkerClick} key={layerID} />;
    } else {
      return;
    }
  };

  const layerGrid = {
    id: "grid-layer",
    type: "fill",
    source: "grid-src",
    paint: {
      "fill-color": "orange",
      "fill-opacity": 0.5,
      "fill-outline-color": "#fc4e2a"
    },
    layout: {
      visibility: "visible"
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
              console.log(viewport.zoom);
              const currentZoomRange = getGridZoomRange();
              console.log(currentZoomRange);
              if (
                viewport.zoom > currentZoomRange.maxZoom ||
                viewport.zoom < currentZoomRange.minZoom
              ) {
                console.log("UPDATE GRID");
                const newRange = gridZoomRange.map(item => {
                  if (
                    viewport.zoom < item.maxZoom &&
                    viewport.zoom > item.minZoom
                  ) {
                    item.isActive = true;
                  } else {
                    item.isActive = false;
                  }
                  return item;
                });
                console.log(newRange);
                setGridZoomRange(newRange);
              }
            }}
            onClick={event => onMapClick(event)}
            onLoad={() => onMapLoad()}
            interactiveLayerIds={interactiveLayerIds}
            preserveDrawingBuffer={true}
            ref={mapRef}
          >
            <React.Fragment>
              {visibleLayerIds.reverse().map(layer => renderMarkerLayer(layer))}
              <Source id="grid-src" type="geojson" data={gridJson}>
                <Layer {...layerGrid} key="grid-layer" />
              </Source>
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
