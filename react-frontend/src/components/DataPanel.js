import React, { useState, useEffect, useCallback } from "react";
import { makeStyles } from '@material-ui/styles';
import { CircularProgress } from '@material-ui/core';
import { format } from 'date-fns';
import SidePane from './SidePane';

const API_URL = process.env.REACT_APP_API_URL

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    margin: theme.spacing(1),
    width: 600,
    height: 300,
    backgroundColor: 'white',
    alignItems: 'center',
    padding: theme.spacing(2),
  },
  placeholder: {
    margin: '0 auto',
  }
}));

const DataPanel = ({featureID, dataLayer, dateFilter, smoothingFactor, yAxisScale, onPaneClose}) => {
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();
  const classes = useStyles();

  useEffect(() => {
    const getFetchUrl = (featureID, dataLayer) => {
      let baseURL = ''
      if (dataLayer == 'stations-layer') {
        baseURL = `${API_URL}api/v1/stations/${featureID}/`;
      }
      else if (dataLayer == 'ifcb-layer') {
        baseURL = `${API_URL}api/v1/ifcb-datasets/${featureID}/`;
      }
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
      const url = getFetchUrl(featureID, dataLayer);
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
  }, [featureID, dataLayer, dateFilter])

  console.log(results);

  return (
    <div>
      {!isLoaded && (
        <div className={classes.root}>
          <div className={classes.placeholder}>
            <CircularProgress />
          </div>
        </div>
      )}

      {results && results.properties.max_mean_values.length && (
        <SidePane
          results={results}
          featureID={featureID}
          dataLayer={dataLayer}
          yAxisScale={yAxisScale}
          onPaneClose={onPaneClose}
        />
      )}
    </div>
  );
}

export default DataPanel;
