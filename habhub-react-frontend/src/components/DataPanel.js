import React, { useState, useEffect} from "react";
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

function DataPanel({
  featureID,
  dataLayer,
  dateFilter,
  smoothingFactor,
  yAxisScale,
  onPaneClose,
  habSpecies
}) {
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();
  const [hasData, setHasData] = useState(true);
  const classes = useStyles();

  useEffect(() => {
    function getFetchUrl(featureID, dataLayer) {
      let baseURL = ''
      if (dataLayer === 'stations-layer') {
        baseURL = `${API_URL}api/v1/stations/${featureID}/`;
        // Force smoothing_factor to be ignored for Station graphs
        smoothingFactor = 1;
      } else if (dataLayer === 'ifcb-layer') {
        baseURL = `${API_URL}api/v1/ifcb-datasets/${featureID}/`;
      } else if (dataLayer === 'closures-layer') {
        baseURL = `${API_URL}api/v1/closures/${featureID}/`;
      }

      const filterURL = baseURL + '?' + new URLSearchParams({
        start_date: format(dateFilter.startDate, 'MM/dd/yyyy'),
        end_date: format(dateFilter.endDate, 'MM/dd/yyyy'),
        seasonal: dateFilter.seasonal,
        exclude_month_range: dateFilter.exclude_month_range,
        smoothing_factor: smoothingFactor,
      })
      return filterURL;
    }

    // Need to check different properties to see whether the API result has data for time frame
    function hasData(result, dataLayer) {
      console.log(result);
      if (dataLayer === 'stations-layer' || dataLayer === 'ifcb-layer') {
        result.properties.max_mean_values.length ? setHasData(true) : setHasData(false);
      } else if (dataLayer === 'closures-layer') {
        result.properties.closures.length ? setHasData(true) : setHasData(false);
      }
    }

    function fetchResults() {
      const url = getFetchUrl(featureID, dataLayer);
      console.log(url);
      fetch(url)
        .then(res => res.json())
        .then(
          (result) => {
            console.log(result);
            setIsLoaded(true);
            setResults(result);
            hasData(result, dataLayer);
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
  }, [featureID, dataLayer, dateFilter, smoothingFactor])

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

      {results && hasData && (
        <SidePane
          results={results}
          featureID={featureID}
          dataLayer={dataLayer}
          yAxisScale={yAxisScale}
          onPaneClose={onPaneClose}
          habSpecies={habSpecies}
        />
      )}
    </div>
  );
}

export default DataPanel;
