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
import { layers } from './map-layers'
import { species } from './hab-species'
import theme from './theme'
import './App.css'

// Set up Font Awesome icons for global use
import { library } from '@fortawesome/fontawesome-svg-core'
import { faArrowLeft, faArrowRight, faAngleDoubleRight, faExpandAlt } from '@fortawesome/free-solid-svg-icons'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

library.add(faArrowLeft, faArrowRight, faAngleDoubleRight, faExpandAlt)

const MAPBOX_TOKEN = 'pk.eyJ1IjoiZWFuZHJld3MiLCJhIjoiY2p6c2xxOWx4MDJudDNjbjIyNTdzNWxqaCJ9.Ayp0hdQGjUayka8dJFwSug';

const popupFromZoom = 6;

const geolocateStyle = {
  position: 'absolute',
  bottom: 166,
  right: 0,
  padding: '10px'
};

const fullscreenControlStyle = {
  position: 'absolute',
  bottom: 130,
  right: 0,
  padding: '10px'
};

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

  const [feature, setFeature] = useState(null);
  const [mapLayers, setMapLayers] = useState(layers);
  const [habSpecies, setHabSpecies] = useState(species);

  const mapRef = useRef();
  const popupRef = useRef();

  const interactiveLayerIds = layers.map(item => item.id);

  const onMapClick = (event) => {
    const mapObj = mapRef.current.getMap();
    const features = mapRef.current.queryRenderedFeatures(event.point, {
      layers: interactiveLayerIds
    });
    //console.log(features);
    if (!features.length) {
      return;
    } else if (mapObj.getZoom() < popupFromZoom) {
       mapObj.easeTo({center: event.lngLat, zoom: mapObj.getZoom() + 2});
    } else {
      const selectedFeature = features[0];
      setFeature(selectedFeature);
    }
  }

  const onLayerVisibilityChange = (event, layerID) => {
    const mapObj = mapRef.current.getMap();
    console.log(popupRef);
    const newVisibility = mapLayers.map(item => {
      if (item.id == layerID) {
        item.visibility = event.target.checked;
      }
      return item;
    })
    setMapLayers(newVisibility);
    // Update the Mapbox Map object to change visibility
    // set array of all grouped layers
    let layerGroups = [layerID]
    if (layerID == 'stations-layer') {
      layerGroups = [...layerGroups, 'stations-max-label-layer']
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
    console.log(popupRef);
    const newVisibility = habSpecies.map(item => {
      if (item.id == speciesID) {
        item.visibility = event.target.checked;
      }
      return item;
    })
    setHabSpecies(newVisibility);
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      {feature && (
        <div className="side-panes-container">
          <SidePane key="1" />
          <SidePane key="2" />
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
          interactiveLayerIds={interactiveLayerIds}
          onClick={event => onMapClick(event)}
          ref={mapRef}
        >

          <ControlPanel
            mapRef={mapRef}
            mapLayers={mapLayers}
            habSpecies={habSpecies}
            onLayerVisibilityChange={onLayerVisibilityChange}
            onSpeciesVisibilityChange={onSpeciesVisibilityChange}
          />

          <React.Fragment>
            <StationsLayer />
            <IfcbLayer />
          </React.Fragment>

          <div style={geolocateStyle}>
            <GeolocateControl />
          </div>
          <div style={navStyle}>
            <NavigationControl />
          </div>
          <div style={scaleControlStyle}>
            <ScaleControl />
          </div>
          {feature && (
            <div>
              {mapLayers.map(item => (feature.layer.id == item.id && item.visibility) ? (
              <Popup
                className={`data-panel ${feature.layer.id}`}
                latitude={feature.geometry.coordinates[1]}
                longitude={feature.geometry.coordinates[0]}
                onClose={() => {
                  setFeature(null);
                }}
                closeOnClick={false}
                ref={popupRef}
                key={feature.id}
              >
                <div>
                  <FontAwesomeIcon
                    icon="expand-alt"
                    pull="right"
                  />
                </div>
                <DataPanel key={feature.id} featureID={feature.id} dataLayer={feature.layer.id} />
              </Popup>
            ) : '')}
            </div>
          )}
        </MapGL>
      </div>
    </ThemeProvider>
  );
}
