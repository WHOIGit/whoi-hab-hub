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
import { selectActiveGuideStep } from "../guide/guideSlice";
import { DATA_LAYERS, METRIC_IDS } from "../../Constants";
import { changeMapData } from "./habMapDataSlice";
import "maplibre-gl/dist/maplibre-gl.css";

//const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN;

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

const MAP_LATITUDE = parseFloat(process.env.REACT_APP_MAP_LATITUDE);
const MAP_LONGITUDE = parseFloat(process.env.REACT_APP_MAP_LONGITUDE);
const MAP_ZOOM = parseFloat(process.env.REACT_APP_MAP_ZOOM);

const defaultViewport = {
  latitude: MAP_LATITUDE,
  longitude: MAP_LONGITUDE,
  zoom: MAP_ZOOM,
};

export default function HabMap({ bookmarkViewport }) {
  const classes = useStyles();

  const visibleLayerIds = useSelector(selectVisibleLayerIds);
  // only refers to map layer that use the Mapbox Layer/Source properties
  const interactiveLayerIds = useSelector(selectInteractiveLayerIds);
  const activeGuideStep = useSelector(selectActiveGuideStep);
  const [viewport, setViewport] = useState(defaultViewport);
  const [features, setFeatures] = useState([]);
  const [mapBounds, setMapBounds] = useState(null);
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
    setFeatures(newFeatures);
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

  const handleMapBoundsUpdates = (viewport) => {
    // Get the map viewport bounds, set state to load spatial data
    if (mapRef.current !== undefined) {
      const mapObj = mapRef.current.getMap();
      const bounds = mapObj.getBounds();
      const bbox = [
        bounds._sw.lng,
        bounds._sw.lat,
        bounds._ne.lng,
        bounds._ne.lat,
      ];
      setMapBounds(bbox);
    }
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

  const onMapLoad = () => {
    // set the initial bbox/zoom levels for Spatial Grid
    handleMapBoundsUpdates(viewport);
  };

  const onMapClick = (event) => {
    console.log("MAP CLICK");
    const mapFeatures = mapRef.current.queryRenderedFeatures(event.point);
    const feature = mapFeatures[0];
    console.log(feature);
    if (
      feature !== undefined &&
      interactiveLayerIds.includes(feature.layer.id)
    ) {
      feature.layerID = feature.layer.id;
      setFeatures([feature, ...features]);
    }
  };

  const onMarkerClick = (event, feature, layerID, metricID) => {
    console.log("MARKER CLICK");
    feature.layerID = layerID;
    feature.metricID = metricID;
    setFeatures([feature, ...features]);
  };

  const onPaneClose = (featureID) => {
    const newFeatures = features.filter((feature) => feature.id !== featureID);
    setFeatures(newFeatures);
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
          mapStyle="positron-map-style.json"
          onMove={(evt) => {
            setViewport(evt.viewState);
            dispatchHabMapChanges(evt.viewState);
          }}
          reuseMaps={true}
          style={{ height: "100vh", width: "100%" }}
          onClick={(event) => onMapClick(event)}
          //onLoad={onMapLoad}
          interactiveLayerIds={interactiveLayerIds}
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
