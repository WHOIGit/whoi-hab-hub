import React, { useState, useEffect, useCallback, useRef } from "react"
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
// Material UI imports
import CssBaseline from '@material-ui/core/CssBaseline'
import { ThemeProvider } from '@material-ui/core/styles'
// Import our stuff
import SidePane from './components/SidePane'
import ControlPanel from './components/ControlPanel'
import DataPanel from './components/DataPanel'
import StationsGraph from './components/StationsGraph'
import StationsLayer from './components/StationsLayer'
import IfcbLayer from './components/IfcbLayer'
import StationsMarkers from './components/StationsMarkers'
import IfcbMarkers from './components/IfcbMarkers'
import { layers } from './map-layers'
import { species } from './hab-species'
import theme from './theme'
import './App.css'

const MAPBOX_TOKEN = 'pk.eyJ1IjoiZWFuZHJld3MiLCJhIjoiY2p6c2xxOWx4MDJudDNjbjIyNTdzNWxqaCJ9.Ayp0hdQGjUayka8dJFwSug';

const popupFromZoom = 6;

const navStyle = {
  position: 'absolute',
  bottom: 36,
  right: 0,
  padding: '10px'
};

const scaleControlStyle = {
  position: 'absolute',
  bottom: 36,
  left: 0,
  padding: '10px'
};

export default function App() {
  const [viewport, setViewport] = useState({
    latitude: 42.89,
    longitude: -69.75,
    width: "100vw",
    height: "100vh",
    zoom: 6.7
  });

  const [features, setFeatures] = useState([]);
  const [mapLayers, setMapLayers] = useState(layers);
  const [habSpecies, setHabSpecies] = useState(species);
  const [dateFilter, setDateFilter] = useState([]);
  const [yAxisScale, setYAxisScale] = useState('linear');

  const mapRef = useRef();

  const interactiveLayerIds = layers.map(item => item.id);

  const renderMarkerLayer = (layer) => {
    console.log(layer);
    if (layer.visibility && layer.id === 'stations-layer') {
      return (
        <StationsMarkers habSpecies={habSpecies} onMarkerClick={onMarkerClick} dateFilter={dateFilter} key={layer.id} />
      );
    } else if (layer.visibility && layer.id === 'ifcb-layer') {
      return (
        <IfcbMarkers habSpecies={habSpecies} onMarkerClick={onMarkerClick} dateFilter={dateFilter} key={layer.id} />
      );
    } else {
      return;
    }
  }

  const onMapClick = (event) => {
    const mapObj = mapRef.current.getMap();

    if (mapObj.getZoom() < popupFromZoom) {
       mapObj.easeTo({center: event.lngLat, zoom: mapObj.getZoom() + 2});
    }
  }

  const onMarkerClick = (event, feature, layerID) => {
    const mapObj = mapRef.current.getMap();
    console.log(event);
    console.log(feature);
    feature.layer = layerID;
    setFeatures([feature, ...features]);
    console.log(features);
  }

  const onPaneClose = (featureID) => {
    const newFeatures = features.filter(feature => feature.id !== featureID)
    setFeatures(newFeatures);
  }

  const onLayerVisibilityChange = (event, layerID) => {
    const mapObj = mapRef.current.getMap();
    // set the mapLayers state
    const newVisibility = mapLayers.map(item => {
      if (item.id == layerID) {
        item.visibility = event.target.checked;
      }
      return item;
    })
    setMapLayers(newVisibility);
    // set the features state
    const newFeatures = features.filter(feature => feature.layer.id !== layerID)
    setFeatures(newFeatures);
  }

  const onSpeciesVisibilityChange = (event, speciesID) => {
    const mapObj = mapRef.current.getMap();
    const newVisibility = habSpecies.map(item => {
      if (item.id == speciesID) {
        item.visibility = event.target.checked;
      }
      return item;
    })
    setHabSpecies(newVisibility);
  }

  const onDateRangeChange = (startDate, endDate) => {
    setDateFilter([startDate, endDate]);
  }

  const onYAxisChange = (event) => {
    console.log(event.target.value);
    setYAxisScale(event.target.value);
  };

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {features && (
        <div className="side-panes-container">
          {features.map(feature => (
            <DataPanel
              key={feature.id}
              featureID={feature.id}
              dataLayer={feature.layer}
              dateFilter={dateFilter}
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
            setViewport(viewport)
          }}
          onClick={event => onMapClick(event)}
          ref={mapRef}
        >

          <ControlPanel
            mapLayers={mapLayers}
            habSpecies={habSpecies}
            yAxisScale={yAxisScale}
            onLayerVisibilityChange={onLayerVisibilityChange}
            onSpeciesVisibilityChange={onSpeciesVisibilityChange}
            onDateRangeChange={onDateRangeChange}
            onYAxisChange={onYAxisChange}
          />

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
    </ThemeProvider>
  );
}
