import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { Source, Marker } from 'react-map-gl';
import { format } from 'date-fns'
import IfcbMarkerIcon from './IfcbMarkerIcon'

const API_URL = process.env.REACT_APP_API_URL

const useStyles = makeStyles((theme) => ({
  button: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
  },
}));

const IfcbMarkers = ({habSpecies, onMarkerClick, dateFilter, smoothingFactor}) => {
  const classes = useStyles();
  console.log(habSpecies);
  const layerID = 'ifcb-layer';
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();

  useEffect(() => {
    const getFetchUrl = () => {
      let baseURL = API_URL + 'api/v1/ifcb-datasets/'
      // build API URL to get set Date Filter
      if (dateFilter.length) {
        const filterURL = baseURL + '?' + new URLSearchParams({
            start_date: format(dateFilter[0], 'MM/dd/yyyy'),
            end_date: format(dateFilter[1], 'MM/dd/yyyy'),
            smoothing_factor: smoothingFactor,
        })
        return filterURL;
      }
      return baseURL;
    }

    const fetchResults = () => {
      const url = getFetchUrl();
      console.log(url);
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
  }, [dateFilter])

  const renderMarker = (feature) => {
    const visibleSpecies = habSpecies.filter(species => species.visibility);
    console.log(feature.properties.max_mean_values);
    if (visibleSpecies.length && feature.properties.max_mean_values.length) {
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
            <IfcbMarkerIcon visibleSpecies={visibleSpecies} maxMeanData={feature.properties.max_mean_values} />
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

export default IfcbMarkers;
