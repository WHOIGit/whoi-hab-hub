import React, { useState, useEffect, useRef } from "react"
import MapGL, {
  Source,
  Layer,
  Marker,
  Popup,
  NavigationControl,
  FullscreenControl,
  ScaleControl,
  GeolocateControl
} from 'react-map-gl'
import { DndProvider } from 'react-dnd'
import { HTML5Backend } from 'react-dnd-html5-backend'
import { differenceInDays } from 'date-fns'
// Material UI imports
import { makeStyles } from '@material-ui/styles'
import CssBaseline from '@material-ui/core/CssBaseline'
import { ThemeProvider } from '@material-ui/core/styles'
// Import our stuff
import SidePane from './SidePane'
import DashBoard from './dashboard/DashBoard'
import DateControls from './dashboard/DateControls'
import DataPanel from './DataPanel'
import StationsGraph from './StationsGraph'
import StationsMarkers from './StationsMarkers'
import IfcbMarkers from './IfcbMarkers'
import ClosuresLayer from './ClosuresLayer'
import LowerLeftPanel from "./LowerLeftPanel";
import { layers, species } from '../Constants'

const MAPBOX_TOKEN = 'pk.eyJ1IjoiZWFuZHJld3MiLCJhIjoiY2p6c2xxOWx4MDJudDNjbjIyNTdzNWxqaCJ9.Ayp0hdQGjUayka8dJFwSug';
const popupFromZoom = 6;
const defaultStartDate = new Date('2017-01-01T21:11:54');

const navStyle = {
  position: 'absolute',
  bottom: 72,
  left: 0,
  padding: '10px'
};

const scaleControlStyle = {
  position: 'absolute',
  bottom: 36,
  left: 0,
  padding: '10px'
};

const useStyles = makeStyles(theme => ({
  dataPanelContainer: {
    background: "none",
    position: "absolute",
    top: 0,
    left: 0,
    zIndex: 3000,
    maxHeight: "100vh",
    overflowY: "scroll",
  },
}))

export default function HabMap() {
  const classes = useStyles()
  const [viewport, setViewport] = useState({
    latitude: 42.89,
    longitude: -69.75,
    width: "100%",
    height: "100vh",
    zoom: 6.7
  });
  const mapOptions = {
    "logoPosition": "top-left",
  }

  const [features, setFeatures] = useState([]);
  const [mapLayers, setMapLayers] = useState(layers);
  const [habSpecies, setHabSpecies] = useState(species);
  // dateFilter value for API: array [startDate:date, endDate:date, seasonal:boolean]
  // const [dateFilter, setDateFilter] = useState([defaultStartDate, new Date(), false]);
  const [dateFilter, setDateFilter] = useState({
    "startDate": defaultStartDate,
    "endDate": new Date(),
    "seasonal": false,
    "exclude_month_range": false
  });
  const [stateFilter, setStateFilter] = useState(null);
  const [showControls, setShowControls] = useState(true);
  const [showDateControls, setShowDateControls] = useState(false);
  const [smoothingFactor, setSmoothingFactor] = useState(4);
  const [showMaxMean, setShowMaxMean] = useState("max");
  const [yAxisScale, setYAxisScale] = useState("linear");

  const mapRef = useRef();

  const interactiveLayerIds = ['closures-layer'];

  function onMapLoad() {
    const mapObj = mapRef.current.getMap();
    // Load the custom icon image from the 'public' directory for the Closures Layer
    mapObj.loadImage("images/icon-shellfish-closure.png", function(error, image) {
      if (error) throw error;
      mapObj.addImage("icon-shellfish-closure", image);
    });
  }

  function onMapClick(event) {
    const mapObj = mapRef.current.getMap();
    const mapFeatures = mapRef.current.queryRenderedFeatures(event.point, {layers: interactiveLayerIds});
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
    const newFeatures = features.filter(feature => feature.id !== featureID)
    setFeatures(newFeatures);
  }

  function onLayerVisibilityChange(event, layerID) {
    // set the mapLayers state
    const newVisibility = mapLayers.map(item => {
      if (item.id === layerID) {
        item.visibility = event.target.checked;
      }
      return item;
    })
    setMapLayers(newVisibility);

    // set the features state
    const newFeatures = features.filter(feature => feature.layer.id !== layerID)
    setFeatures(newFeatures);
  }

  function onSpeciesVisibilityChange(event, speciesID) {
    const mapObj = mapRef.current.getMap();
    const newVisibility = habSpecies.map(item => {
      if (item.id == speciesID) {
        item.visibility = event.target.checked;
      }
      return item;
    })
    setHabSpecies(newVisibility);
  }

  function onDateRangeChange(startDate, endDate, seasonal=false, exclude_month_range=false) {
    //setDateFilter([startDate, endDate, seasonal, exclude_month_range]);
    const newDateFilter = {
      "startDate": startDate,
      "endDate": endDate,
      "seasonal": seasonal,
      "exclude_month_range": exclude_month_range
    }
    setDateFilter(newDateFilter);

    // calculate the date range length to determine a smoothing factor to pass API
    const dateRange = differenceInDays(endDate, startDate);
    let newFactor = 4;

    if (dateRange < 90) {
      newFactor = 1;
    }
    else if (dateRange < 180) {
      newFactor = 2;
    }
    else if (dateRange < 240) {
      newFactor = 3;
    }
    setSmoothingFactor(newFactor);
  }

  function onYAxisChange(event) {
    console.log(event.target.value);
    setYAxisScale(event.target.value);
  };

  function renderColorChips(species, chipWidth=20, chipHeight=20, chipType="gradient", ) {
    // default to show all colors in gradient list
    // if chipType is "primary", only show single chip for primary color
    let colors = species.colorGradient;
    if (chipType === "primary") {
      colors = [species.colorPrimary];
    }

    let svgWidth = chipWidth * colors.length;

    return (
      <svg width={svgWidth} height={chipHeight}>
        {colors.map((color, index) => (
          <rect width={chipWidth} height={chipHeight} fill={color} x={index * chipWidth} key={index}></rect>
        ))}
      </svg>
    )
  }

  function renderMarkerLayer(layer) {
    console.log(layer.id);
    if (layer.visibility && layer.id === 'stations-layer') {
      return (
        <StationsMarkers
          habSpecies={habSpecies}
          onMarkerClick={onMarkerClick}
          dateFilter={dateFilter}
          smoothingFactor={smoothingFactor}
          visibility={layer.visibility}
          showMaxMean={showMaxMean}
          key={layer.id}
        />
      );
    } else if (layer.id === 'closures-layer') {
      return (
        <ClosuresLayer
          mapRef={mapRef}
          habSpecies={habSpecies}
          dateFilter={dateFilter}
          stateFilter={stateFilter}
          visibility={layer.visibility}
          key={layer.id}
        />
      );
    } else if (layer.id === 'ifcb-layer') {
      return (
        <IfcbMarkers
          habSpecies={habSpecies}
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
            {features.map(feature => (
              <DataPanel
                key={feature.id}
                featureID={feature.id}
                dataLayer={feature.layer}
                dateFilter={dateFilter}
                smoothingFactor={smoothingFactor}
                yAxisScale={yAxisScale}
                onPaneClose={onPaneClose}
                habSpecies={habSpecies}
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
              setViewport(viewport)
            }}
            onClick={event => onMapClick(event)}
            onLoad={() => onMapLoad()}
            interactiveLayerIds={interactiveLayerIds}
            ref={mapRef}
          >

            <React.Fragment>
              {mapLayers.map(layer => renderMarkerLayer(layer))}
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
            habSpecies={habSpecies}
            yAxisScale={yAxisScale}
            onLayerVisibilityChange={onLayerVisibilityChange}
            onSpeciesVisibilityChange={onSpeciesVisibilityChange}
            onDateRangeChange={onDateRangeChange}
            onYAxisChange={onYAxisChange}
            renderColorChips={renderColorChips}
            showControls={showControls}
            setShowControls={setShowControls}
            showDateControls={showDateControls}
            setShowDateControls={setShowDateControls}
            showMaxMean={showMaxMean}
            setShowMaxMean={setShowMaxMean}
          />
        </div>

        <div>
          <DateControls
            showControls={showControls}
            setShowControls={setShowControls}
            showDateControls={showDateControls}
            setShowDateControls={setShowDateControls}
            mapLayers={mapLayers}
            onDateRangeChange={onDateRangeChange}
            dateFilter={dateFilter}
          />
        </div>

        <div>
          <LowerLeftPanel
            mapLayers={mapLayers}
            habSpecies={habSpecies}
            renderColorChips={renderColorChips}
          />
        </div>
      </div>
    </DndProvider>
  );
}
