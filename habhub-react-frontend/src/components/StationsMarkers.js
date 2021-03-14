import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import {Source, Marker} from 'react-map-gl';
import { format } from 'date-fns';
import StationsMarkerIcon from './StationsMarkerIcon'

const API_URL = process.env.REACT_APP_API_URL

const useStyles = makeStyles((theme) => ({
  button: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
  },
}));

export default function StationsMarkers({
  habSpecies,
  onMarkerClick,
  dateFilter,
  smoothingFactor,
  showMaxMean,
}) {
  const classes = useStyles();
  const layerID = 'stations-layer';
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();

  useEffect(() => {
    function getFetchUrl() {
      const baseURL = API_URL + 'api/v1/stations/'
    // build API URL to get set Date Filter
      const filterURL = baseURL + '?' + new URLSearchParams({
          start_date: format(dateFilter.startDate, 'MM/dd/yyyy'),
          end_date: format(dateFilter.endDate, 'MM/dd/yyyy'),
          seasonal: dateFilter.seasonal,
          exclude_month_range: dateFilter.exclude_month_range,
          smoothing_factor: smoothingFactor,
      })
      return filterURL;
    }

    function fetchResults() {
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
  }, [dateFilter, smoothingFactor])

  function renderMarker(feature) {

    const visibleSpecies = habSpecies
      .filter(species => species.visibility && feature.properties.hab_species.includes(species.id));

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
            <StationsMarkerIcon
              maxMeanData={feature.properties.max_mean_values}
              showMaxMean={showMaxMean}
             />
          </div>
        </Marker>
      );
    } else {
      return;
    }
  }

  return (
    <div>
      {results && results.features.map(feature => renderMarker(feature))}
    </div>
  )
}
