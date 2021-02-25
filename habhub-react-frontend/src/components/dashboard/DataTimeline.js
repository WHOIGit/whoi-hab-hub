import React, { useState, useEffect } from "react";
import Highcharts from 'highcharts';
import Serieslabel from 'highcharts/modules/series-label';
import HighchartsReact from 'highcharts-react-official';
import { makeStyles } from '@material-ui/styles';
import { CircularProgress, Button } from '@material-ui/core';
import BarChartIcon from '@material-ui/icons/BarChart';
import ExpandLessIcon from '@material-ui/icons/ExpandLess';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { format } from 'date-fns';

Serieslabel(Highcharts);

const API_URL = process.env.REACT_APP_API_URL
const fullWidth = window.outerWidth - 400;

const useStyles = makeStyles((theme) => ({
  root: {
    position: 'absolute',
    bottom: 0,
    left: 0,
    display: 'flex',
    margin: theme.spacing(0),
    alignItems: 'center',
    padding: theme.spacing(0),
    transition: 'all 0.3s',
  },
  placeholder: {
    margin: '0 auto',
  },
  button: {
    margin: theme.spacing(0),
    position: "absolute",
    top: 0,
    left: 0,
  },
  collapse: {
    bottom: "-320px",
  },
}));

function DataTimeline({mapLayers}) {
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();
  const [chartData, setChartData] = useState([]);
  const [showTimeline, setShowTimeline] = useState(false);
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
        const dataArray = value.map(item => [Date.parse(item.timestamp), item.count]);

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
      type: 'spline',
      zoomType: 'x',
      width: fullWidth,
      height: 220,
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

export default DataTimeline;
