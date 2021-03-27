import React, { useState, useRef } from "react";
import MapGL, { NavigationControl, ScaleControl } from "react-map-gl";
import { DndProvider } from "react-dnd";
import { HTML5Backend } from "react-dnd-html5-backend";
import { differenceInDays } from "date-fns";
// Material UI imports
import { makeStyles } from "@material-ui/styles";
// Import our stuff
import DashBoard from "./dashboard/DashBoard";
//import DateControls from "./dashboard/DateControls";
import DateControls from "../features/date-filter/DateControls";
import DataPanel from "./DataPanel";
import StationsMarkers from "./StationsMarkers";
import IfcbMarkers from "./IfcbMarkers";
import ClosuresLayer from "./ClosuresLayer";
import LowerLeftPanel from "./LowerLeftPanel";
import DisclaimerBox from "./DisclaimerBox";
import { layers } from "../Constants";

// eslint-disable-next-line no-undef
const MAPBOX_TOKEN = process.env.REACT_APP_MAPBOX_TOKEN;
const defaultStartDate = new Date("2017-01-01T21:11:54");

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

export default function HabMap() {
  const classes = useStyles();
  const [viewport, setViewport] = useState({
    latitude: 42.89,
    longitude: -69.75,
    width: "100%",
    height: "100vh",
    zoom: 6.7,
  });

  const [features, setFeatures] = useState([]);
  const [mapLayers, setMapLayers] = useState(layers);
  // dateFilter value for API: array [startDate:date, endDate:date, seasonal:boolean]
  // const [dateFilter, setDateFilter] = useState([defaultStartDate, new Date(), false]);
  const [dateFilter, setDateFilter] = useState({
    startDate: defaultStartDate,
    endDate: new Date(),
    seasonal: false,
    exclude_month_range: false,
  });
  const [showControls, setShowControls] = useState(true);
  const [showDateControls, setShowDateControls] = useState(false);
  const [smoothingFactor, setSmoothingFactor] = useState(4);
  const [showMaxMean, setShowMaxMean] = useState("max");
  // eslint-disable-next-line no-unused-vars
  const [yAxisScale, setYAxisScale] = useState("linear");
  const [visibleLegends, setVisibleLegends] = useState([
    "stations-layer",
    "ifcb-layer",
  ]);

  const mapRef = useRef();

  const interactiveLayerIds = ["closures-layer"];

  function onMapLoad() {
    const mapObj = mapRef.current.getMap();
    // Load the custom icon image from the 'public' directory for the Closures Layer
    mapObj.loadImage(
      "images/icon-shellfish-closure.png",
      function (error, image) {
        if (error) throw error;
        mapObj.addImage("icon-shellfish-closure", image);
      }
    );
  }

  function onMapClick(event) {
    const mapFeatures = mapRef.current.queryRenderedFeatures(event.point, {
      layers: interactiveLayerIds,
    });
    console.log(mapFeatures[0]);
    const feature = mapFeatures[0];

    if (feature !== undefined) {
      feature.layer = feature.layer.id;
      setFeatures([feature, ...features]);
    }
  }

  function onMarkerClick(event, feature, layerID) {
    feature.layer = layerID;
    setFeatures([feature, ...features]);
  }

  function onPaneClose(featureID) {
    const newFeatures = features.filter((feature) => feature.id !== featureID);
    setFeatures(newFeatures);
  }

  function onLayerVisibilityChange(event, layerID) {
    // set the mapLayers state
    const newVisibility = mapLayers.map((item) => {
      if (item.id === layerID) {
        item.visibility = event.target.checked;
      }
      return item;
    });
    setMapLayers(newVisibility);

    // set the features state
    const newFeatures = features.filter(
      (feature) => feature.layer.id !== layerID
    );
    setFeatures(newFeatures);

    // remove any legned panes if they're active, no action on activating
    if (!event.target.checked) {
      const newLegends = visibleLegends.filter((item) => item !== layerID);
      setVisibleLegends(newLegends);
    }
  }

  // eslint-disable-next-line no-unused-vars
  function onDateRangeChange(
    startDate,
    endDate,
    seasonal = false,
    exclude_month_range = false
  ) {
    const newDateFilter = {
      startDate: startDate,
      endDate: endDate,
      seasonal: seasonal,
      exclude_month_range: exclude_month_range,
    };
    setDateFilter(newDateFilter);

    // calculate the date range length to determine a smoothing factor to pass API
    const dateRange = differenceInDays(endDate, startDate);
    let newFactor = 4;

    if (dateRange < 90) {
      newFactor = 1;
    } else if (dateRange < 180) {
      newFactor = 2;
    } else if (dateRange < 240) {
      newFactor = 3;
    }
    setSmoothingFactor(newFactor);
  }

  function renderMarkerLayer(layer) {
    console.log(layer.id);
    if (layer.visibility && layer.id === "stations-layer") {
      return (
        <StationsMarkers
          onMarkerClick={onMarkerClick}
          dateFilter={dateFilter}
          smoothingFactor={smoothingFactor}
          visibility={layer.visibility}
          showMaxMean={showMaxMean}
          key={layer.id}
        />
      );
    } else if (layer.id === "closures-layer") {
      return (
        <ClosuresLayer
          dateFilter={dateFilter}
          visibility={layer.visibility}
          key={layer.id}
        />
      );
    } else if (layer.id === "ifcb-layer") {
      return (
        <IfcbMarkers
          onMarkerClick={onMarkerClick}
          dateFilter={dateFilter}
          smoothingFactor={smoothingFactor}
          visibility={layer.visibility}
          showMaxMean={showMaxMean}
          key={layer.id}
        />
      );
    } else {
      return;
    }
  }

  return (
    <DndProvider backend={HTML5Backend}>
      <div>
        {features && (
          <div className={classes.dataPanelContainer}>
            {features.map((feature) => (
              <DataPanel
                key={feature.id}
                featureID={feature.id}
                dataLayer={feature.layer}
                dateFilter={dateFilter}
                smoothingFactor={smoothingFactor}
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
            onViewportChange={(viewport) => {
              setViewport(viewport);
            }}
            onClick={(event) => onMapClick(event)}
            onLoad={() => onMapLoad()}
            interactiveLayerIds={interactiveLayerIds}
            preserveDrawingBuffer={true}
            ref={mapRef}
          >
            <React.Fragment>
              {mapLayers.map((layer) => renderMarkerLayer(layer))}
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
            mapLayers={mapLayers}
            onLayerVisibilityChange={onLayerVisibilityChange}
            showControls={showControls}
            setShowControls={setShowControls}
            showDateControls={showDateControls}
            setShowDateControls={setShowDateControls}
            showMaxMean={showMaxMean}
            setShowMaxMean={setShowMaxMean}
            visibleLegends={visibleLegends}
            setVisibleLegends={setVisibleLegends}
            mapRef={mapRef}
          />
        </div>

        <div>
          <DateControls
            showControls={showControls}
            showDateControls={showDateControls}
            mapLayers={mapLayers}
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
