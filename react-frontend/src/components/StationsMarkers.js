import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import {Source, Marker} from 'react-map-gl';
import StationsMarkerIcon from './StationsMarkerIcon'
import diamondIcon from '../map-icons/diamond.svg'

const useStyles = makeStyles((theme) => ({
  button: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
  },
}));

const StationsMarkers = ({habSpecies, onMarkerClick}) => {
  const classes = useStyles();
  console.log(habSpecies);
  const layerID = 'stations-layer';
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();

  useEffect(() => {
    const fetchResults = () => {
      const url = 'https://habhub.whoi.edu/services/api/v1/stations/';
      fetch(url)
        .then(res => res.json())
        .then(
          (result) => {
            console.log(result);
            setIsLoaded(true);
            setResults(result);
          },
          // Note: it's important to handle errors here
          // instead of a catch() block so that we don't swallow
          // exceptions from actual bugs in components.
          (error) => {
            setIsLoaded(true);
            setError(error);
          }
        )
    }
    fetchResults();
  }, [])

  const renderMarker = (feature) => {

    const visibleSpecies = habSpecies
      .filter(species => species.visibility && feature.properties.hab_species.includes(species.id));

    console.log(visibleSpecies);
    if (visibleSpecies.length) {
      return (
        <Marker
          key={feature.id}
          latitude={feature.geometry.coordinates[1]}
          longitude={feature.geometry.coordinates[0]}
          captureClick={true}
        >
          <div
            className={classes.button}
            onClick={(event) => onMarkerClick(event, feature, layerID)}
          >
            <StationsMarkerIcon
              maxValue={feature.properties.station_max}
              meanValue={feature.properties.station_mean}
            />
          </div>
        </Marker>
      );
    } else {
      return;
    }
  }

  console.log(results);
  return (
    <div>
      {results && results.features.map(feature => renderMarker(feature))}
    </div>
  )
}

export default StationsMarkers;
