import React, { useState, useEffect } from "react";
import Highcharts from 'highcharts';
import Serieslabel from 'highcharts/modules/series-label';
import HighchartsReact from 'highcharts-react-official';
import { makeStyles } from '@material-ui/styles';
import { CircularProgress } from '@material-ui/core';
import { format } from 'date-fns';

Serieslabel(Highcharts);

const API_URL = process.env.REACT_APP_API_URL
const fullWidth = window.outerWidth - 380;

const useStyles = makeStyles((theme) => ({
  root: {
    position: 'fixed',
    bottom: 0,
    left: 0,
    display: 'flex',
    margin: theme.spacing(1),
    width: fullWidth,
    height: 300,
    backgroundColor: 'white',
    alignItems: 'center',
    padding: theme.spacing(2),
  },
  placeholder: {
    margin: '0 auto',
  }
}));

function DataPanel({mapLayers}) {
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();
  const [chartData, setChartData] = useState([]);
  const classes = useStyles();

  useEffect(() => {
    function fetchResults() {
      const url = `${API_URL}api/v1/data-density/`;
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
  }, [mapLayers])

  useEffect(() => {
    const newChartData = []
    if (results) {
      for (let [key, value] of Object.entries(results)) {
        const dataArray = value.map(item => [Date.parse(item.timestamp), item.count]).sort();

        const timeSeries = {
          name: key,
          data: dataArray,
        }

        newChartData.push(timeSeries)
      }
      setChartData(newChartData);
      console.log(newChartData);
    }

  }, [results]);

  const chartOptions = {
    chart: {
      type: 'column',
      zoomType: 'x',
      width: fullWidth,
      height: 280,
    },
    title: {
      text: null
    },
    subtitle: {
      text: document.ontouchstart === undefined ?
            'Click and drag in the plot area to zoom in' : 'Pinch the chart to zoom in'
    },
    xAxis: {
      type: 'datetime'
    },
    yAxis: {
      title: {
          text: 'Data Density'
      },
      min: 0,
    },
    series: chartData
  };

  return (
    <div className={classes.root}>
      {!isLoaded && (
        <div>
          <div className={classes.placeholder}>
            <CircularProgress />
          </div>
        </div>
      )}

      {results && (
        <HighchartsReact
          highcharts={Highcharts}
          options={chartOptions}
        />
      )}
    </div>
  );
}

export default DataPanel;
