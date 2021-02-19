import React, {useState, useEffect, useCallback, useRef} from "react";
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
import {ThemeProvider} from '@material-ui/core/styles'
// Import our stuff
import SidePane from './components/SidePane'
import ControlPanel from './components/ControlPanel'
import DataPanel from './components/DataPanel'
import StationsGraph from './components/StationsGraph'
import StationsLayer from './components/StationsLayer'
import IfcbLayer from './components/IfcbLayer'
import StationsMarkers from './components/StationsMarkers'
import {layers} from './map-layers'
import {species} from './hab-species'
import theme from './theme'
import './App.css'

// Set up Font Awesome icons for global use
import {library} from '@fortawesome/fontawesome-svg-core'
import {faArrowLeft, faArrowRight, faAngleDoubleRight, faExpandAlt} from '@fortawesome/free-solid-svg-icons'
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'

library.add(faArrowLeft, faArrowRight, faAngleDoubleRight, faExpandAlt)

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
  const [viewport, setViewport] = useState({latitude: 42.89, longitude: -69.75, width: "100vw", height: "100vh", zoom: 6.7});

  const [features, setFeatures] = useState([]);
  const [mapLayers, setMapLayers] = useState(layers);
  const [habSpecies, setHabSpecies] = useState(species);
  const [dateFilter, setDateFilter] = useState([]);
  const [yAxisScale, setYAxisScale] = useState('linear');

  const mapRef = useRef();

  const interactiveLayerIds = layers.map(item => item.id);

  const onMapClick = (event) => {
    const mapObj = mapRef.current.getMap();
    const mapFeatures = mapRef.current.queryRenderedFeatures(event.point, {layers: interactiveLayerIds});
    //console.log(features);
    if (!mapFeatures.length) {
      return;
    } else if (mapObj.getZoom() < popupFromZoom) {
      mapObj.easeTo({
        center: event.lngLat,
        zoom: mapObj.getZoom() + 2
      });
    } else {
      const selectedFeature = mapFeatures[0];
      setFeatures([
        selectedFeature, ...features
      ]);
    }
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
    // Update the Mapbox Map object to change visibility
    // set array of all grouped layers
    let layerGroups = [layerID]
    if (layerID == 'stations-layer') {
      layerGroups = [
        ...layerGroups,
        'stations-max-label-layer'
      ]
    }

    const currentVisProp = mapObj.getLayoutProperty(layerID, 'visibility');
    if (currentVisProp == 'visible') {
      layerGroups.map(item => mapObj.setLayoutProperty(item, 'visibility', 'none'));
    } else {
      layerGroups.map(item => mapObj.setLayoutProperty(item, 'visibility', 'visible'));
    }
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

  return (<ThemeProvider theme={theme}>
    <CssBaseline/> {
      features && (<div className="side-panes-container">
        {features.map(feature => (<DataPanel key={feature.id} featureID={feature.id} dataLayer={feature.layer.id} dateFilter={dateFilter} yAxisScale={yAxisScale} onPaneClose={onPaneClose}/>))}
      </div>)
    }
    <div>
      <MapGL {...viewport} mapboxApiAccessToken={MAPBOX_TOKEN} mapStyle="mapbox://styles/mapbox/light-v10" onViewportChange={viewport => {
          setViewport(viewport)
        }} interactiveLayerIds={interactiveLayerIds} onClick={event => onMapClick(event)} ref={mapRef}>

        <ControlPanel mapLayers={mapLayers} habSpecies={habSpecies} yAxisScale={yAxisScale} onLayerVisibilityChange={onLayerVisibilityChange} onSpeciesVisibilityChange={onSpeciesVisibilityChange} onDateRangeChange={onDateRangeChange} onYAxisChange={onYAxisChange}/>

        <React.Fragment>
          <StationsMarkers mapRef={mapRef} setFeatures={setFeatures}/>
          <IfcbLayer mapRef={mapRef}/>
        </React.Fragment>

        <div style={navStyle}>
          <NavigationControl/>
        </div>
        <div style={scaleControlStyle}>
          <ScaleControl/>
        </div>
      </MapGL>
    </div>
  </ThemeProvider>);
}
