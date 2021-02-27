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
    position: 'relative',
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

function DataTimeline({mapLayers, dateFilter}) {
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();
  const [chartData, setChartData] = useState([]);
  const [chartBands, setChartBands] = useState([]);
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
    }

  }, [results]);

  // update Chart Bands when Dates are changed
  useEffect(() => {
    if (dateFilter) {
      const bandColor = "#e1f5fe"
      // if seasonal filter, need to create array of date ranges
      if (dateFilter[2]) {
        function range(start, end) {
          return Array.from({ length: end - start + 1 }, (_, i) => i + start);
        }

        const yearRange = range(dateFilter[0].getFullYear(), dateFilter[1].getFullYear());
        const newChartBands = yearRange.map(year => {
          const startDateFields = [year, dateFilter[0].getMonth(), dateFilter[0].getDate()];
          const startDate = new Date(...startDateFields);

          const endDateFields = [year, dateFilter[1].getMonth(), dateFilter[1].getDate()];
          const endDate = new Date(...endDateFields);

          return {
            color: bandColor,
            from: startDate,
            to: endDate
          }
        })
        setChartBands(newChartBands);
      } else {
        const band = {
          color: bandColor,
          from: dateFilter[0],
          to: dateFilter[1]
        }
        setChartBands([band]);
      }
    }
  }, [dateFilter]);

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
      type: 'datetime',
      plotBands: chartBands,
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
