/* eslint-disable no-unused-vars */
import React, { useState, useRef, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import Map, { NavigationControl, ScaleControl } from "react-map-gl";
import maplibregl from "maplibre-gl";
import { makeStyles } from "@material-ui/styles";
// local
import DataPanel from "./data-panels/DataPanel";
import StationsMarkers from "./StationsMarkers";
import IfcbMarkers from "./IfcbMarkers";
import SpatialGridMarkers from "./SpatialGridMarkers";
import ClosuresLayer from "./ClosuresLayer";
import DisclaimerBox from "./DisclaimerBox";
import CurrentDateChip from "../date-filter/CurrentDateChip";
import {
  selectInteractiveLayerIds,
  selectVisibleLayerIds,
} from "../data-layers/dataLayersSlice";
import { DATA_LAYERS, METRIC_IDS, INTERACTIVE_LAYERS } from "../../Constants";
import {
  changeMapData,
  selectActiveFeatues,
  addFeature,
  deleteFeature,
  setAllFeatures,
} from "./habMapDataSlice";
import "maplibre-gl/dist/maplibre-gl.css";

const navStyle = {
  position: "absolute",
  bottom: 72,
  left: 0,
  padding: "10px",
};

const scaleControlStyle = {
  position: "absolute",
  bottom: 36,
  left: 0,
  padding: "10px",
};

// eslint-disable-next-line no-unused-vars
const useStyles = makeStyles((theme) => ({
  dataPanelContainer: {
    background: "none",
    position: "absolute",
    top: 0,
    left: 0,
    zIndex: 3000,
    maxHeight: "100vh",
    overflowY: "scroll",
  },
}));

const initialGridZoomArray = [
  // gridLength refers to the PostGIS SnapToGrid function length arg
  { gridLength: 0.1, maxZoom: 100, minZoom: 8, isActive: false },
  { gridLength: 0.3, maxZoom: 8, minZoom: 7, isActive: false },
  { gridLength: 0.5, maxZoom: 7, minZoom: 6, isActive: true },
  { gridLength: 0.8, maxZoom: 6, minZoom: 5, isActive: false },
  { gridLength: 1.0, maxZoom: 5, minZoom: 0, isActive: false },
];

const MAP_LATITUDE = parseFloat(import.meta.env.VITE_MAP_LATITUDE);
const MAP_LONGITUDE = parseFloat(import.meta.env.VITE_MAP_LONGITUDE);
const MAP_ZOOM = parseFloat(import.meta.env.VITE_MAP_ZOOM);

const defaultViewport = {
  latitude: MAP_LATITUDE,
  longitude: MAP_LONGITUDE,
  zoom: MAP_ZOOM,
};

export default function HabMap({ bookmarkViewport }) {
  const classes = useStyles();

  const visibleLayerIds = useSelector(selectVisibleLayerIds);
  // only refers to map layer that use the Mapbox Layer/Source properties
  //const interactiveLayerIds = useSelector(selectInteractiveLayerIds);
  const features = useSelector(selectActiveFeatues);
  const [viewport, setViewport] = useState(defaultViewport);
  const [gridZoomRange, setGridZoomRange] = useState(initialGridZoomArray);
  // eslint-disable-next-line no-unused-vars
  const [yAxisScale, setYAxisScale] = useState("linear");
  const mapRef = useRef();
  const dispatch = useDispatch();

  useEffect(() => {
    if (bookmarkViewport) {
      setViewport(bookmarkViewport);
    }
  }, [bookmarkViewport]);

  useEffect(() => {
    const newFeatures = features.filter((feature) =>
      visibleLayerIds.includes(feature.layerID)
    );
    //setFeatures(newFeatures);
    dispatch(setAllFeatures(newFeatures));
  }, [visibleLayerIds]);

  /*
  useEffect(() => {
    // effect to set the active grid squares based on map Bounds
    console.log(mapBounds);
    //const zoomRange = gridZoomRange.filter(item => item.isActive);
    if (mapBounds !== null) {
      // trigger Redux dispatch function to fetch active grid squaresdata
      const payload = {
        mapBounds: mapBounds,
      };
      dispatch(changeActiveGridSquares(payload));
    }
  }, [mapBounds]);
 */
  const dispatchHabMapChanges = (viewport) => {
    // trigger Redux dispatch function to fetch active grid squaresdata
    const payload = {
      latitude: viewport.latitude,
      longitude: viewport.longitude,
      zoom: viewport.zoom,
    };
    dispatch(changeMapData(payload));
  };

  const getGridZoomLength = () => {
    const zoom = gridZoomRange.find((item) => item.isActive).gridLength;
    return zoom;
  };

  const handleZoomUpdates = () => {
    // set the zoom levels for Spatial Grid
    const currentZoomRange = gridZoomRange.find((item) => item.isActive);
    //console.log(currentZoomRange);
    if (
      viewport.zoom > currentZoomRange.maxZoom ||
      viewport.zoom < currentZoomRange.minZoom
    ) {
      console.log("UPDATE GRID");
      const newRange = gridZoomRange.map((item) => {
        if (viewport.zoom < item.maxZoom && viewport.zoom > item.minZoom) {
          item.isActive = true;
        } else {
          item.isActive = false;
        }
        return item;
      });
      console.log(newRange);
      setGridZoomRange(newRange);
      /*
      const zoomRange = newRange.filter(item => item.isActive)[0];
      // trigger Redux dispatch function to change grid zoom
      const payload = {
        zoomRange: zoomRange
      };*/
      //dispatch(changeGridZoom(payload));
    }
  };

  const onMapClick = (event) => {
    console.log("MAP CLICK");
    const mapFeatures = mapRef.current.queryRenderedFeatures(event.point);
    const feature = mapFeatures[0];
    if (
      feature !== undefined &&
      INTERACTIVE_LAYERS.includes(feature.layer.id)
    ) {
      console.log(feature);
      const payload = { id: feature.id, layerID: feature.properties.layerID };
      dispatch(addFeature(payload));
    }
  };

  const onMarkerClick = (event, feature, layerID, metricID) => {
    console.log("MARKER CLICK");
    feature.layerID = layerID;
    feature.metricID = metricID;
    const payload = { id: feature.id, layerID: layerID, metricID: metricID };
    dispatch(addFeature(payload));
  };

  const onPaneClose = (featureID) => {
    const payload = featureID;
    dispatch(deleteFeature(payload));
  };

  const renderMarkerLayer = (layerID) => {
    if (layerID === DATA_LAYERS.stationsLayer) {
      return (
        <StationsMarkers
          onMarkerClick={onMarkerClick}
          metricID={METRIC_IDS.shellfishToxicity}
          layerID={layerID}
          key={layerID}
        />
      );
    } else if (
      layerID === DATA_LAYERS.closuresLayer ||
      layerID === DATA_LAYERS.closuresSeasonalLayer
    ) {
      return <ClosuresLayer layerID={layerID} key={layerID} />;
    } else if (layerID === DATA_LAYERS.cellConcentrationSpatialGridLayer) {
      return (
        <SpatialGridMarkers
          onMarkerClick={onMarkerClick}
          gridLength={getGridZoomLength()}
          metricID={METRIC_IDS.cellConcentration}
          layerID={layerID}
          key={layerID}
        />
      );
    } else if (layerID === DATA_LAYERS.cellConcentrationLayer) {
      return (
        <IfcbMarkers
          onMarkerClick={onMarkerClick}
          metricID={METRIC_IDS.cellConcentration}
          layerID={layerID}
          onPaneClose={onPaneClose}
          key={layerID}
        />
      );
    } else if (layerID === DATA_LAYERS.biovolumeLayer) {
      return (
        <IfcbMarkers
          onMarkerClick={onMarkerClick}
          metricID={METRIC_IDS.biovolume}
          layerID={layerID}
          key={layerID}
        />
      );
    } else {
      return;
    }
  };

  return (
    <div>
      <div>
        <CurrentDateChip />
      </div>
      {features && (
        <div className={classes.dataPanelContainer}>
          {features.map((feature) => (
            <DataPanel
              key={feature.id}
              featureID={feature.id}
              dataLayer={feature.layerID}
              yAxisScale={yAxisScale}
              onPaneClose={onPaneClose}
              metricID={feature.metricID}
              gridLength={getGridZoomLength()}
            />
          ))}
        </div>
      )}
      <div>
        <Map
          {...viewport}
          mapLib={maplibregl}
          mapStyle="/positron-map-style.json"
          onMove={(evt) => {
            setViewport(evt.viewState);
            dispatchHabMapChanges(evt.viewState);
          }}
          reuseMaps={true}
          style={{ height: "100vh", width: "100%" }}
          onClick={(event) => onMapClick(event)}
          //interactiveLayerIds={interactiveLayerIds}
          //preserveDrawingBuffer={true}
          onZoomEnd={handleZoomUpdates}
          ref={mapRef}
        >
          <React.Fragment>
            {visibleLayerIds.reverse().map((layer) => renderMarkerLayer(layer))}
          </React.Fragment>

          <div style={navStyle}>
            <NavigationControl />
          </div>
          <div style={scaleControlStyle}>
            <ScaleControl />
          </div>
        </Map>
      </div>

      <div>
        <DisclaimerBox />
      </div>
    </div>
  );
}
