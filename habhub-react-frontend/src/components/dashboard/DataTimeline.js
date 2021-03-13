import React, { useState, useEffect } from "react";
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import { makeStyles } from '@material-ui/styles';
import { CircularProgress, Button } from '@material-ui/core';
import BarChartIcon from '@material-ui/icons/BarChart';
import ExpandLessIcon from '@material-ui/icons/ExpandLess';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { format } from 'date-fns';

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

function DataTimeline({
  mapLayers,
  dateFilter,
  onDateRangeChange,
  onDateRangeReset,
  setSelectedStartDate,
  setSelectedEndDate,
  setSliderValuesFromDates,
}) {
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
        const dataArray = value.map(item => [Date.parse(item.timestamp), parseFloat(item.density_percentage)]);
        console.log(dataArray);
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
      if (dateFilter.seasonal) {
        function range(start, end) {
          return Array.from({ length: end - start + 1 }, (_, i) => i + start);
        }

        const yearRange = range(dateFilter.startDate.getFullYear(), dateFilter.endDate.getFullYear());
        const newChartBands = yearRange.map(year => {
          let startDateFields = [year, dateFilter.startDate.getMonth(), dateFilter.startDate.getDate()];
          let endDateFields = [year, dateFilter.endDate.getMonth(), dateFilter.endDate.getDate()];

          if (dateFilter.exclude_month_range) {
             startDateFields = [year, dateFilter.endDate.getMonth(), dateFilter.endDate.getDate()];
             endDateFields = [year + 1, dateFilter.startDate.getMonth(), dateFilter.startDate.getDate()];
           }

          const startDate = new Date(...startDateFields);
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
          from: dateFilter.startDate,
          to: dateFilter.endDate
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
      // update dateFilter state on zoom selection, then set all date controls to match
      events: {
        selection: function(event) {
            if(event.xAxis != null) {
              let start = new Date(Math.ceil(event.xAxis[0].min));
              let end = new Date(Math.floor(event.xAxis[0].max));
              onDateRangeChange(start, end);
              setSelectedStartDate(start);
              setSelectedEndDate(end);
              setSliderValuesFromDates(start, end);
            } else {
              onDateRangeReset();
            }
        }
      },
    },
    title: {
      text: null
    },
    subtitle: {
      text: document.ontouchstart === undefined ?
            'Click and drag in the plot area to select date range' : 'Pinch the chart to select data range'
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
      max: 1,
    },
    plotOptions: {
      series: {
        label: {
          enabled: false
        },
      }
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
