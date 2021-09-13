import React, { useState, useEffect, useRef } from "react";
import { useSelector, useDispatch } from "react-redux";
import { parseISO } from "date-fns";
import _ from "lodash";
import Highcharts from "highcharts";
import HighchartsReact from "highcharts-react-official";
import { makeStyles } from "@material-ui/styles";
import { CircularProgress } from "@material-ui/core";
import { changeDateRange } from "./dateFilterSlice";

import axiosInstance from "../../app/apiAxios";

const widthWithDashboard = window.outerWidth - 400;
const widthFull = window.outerWidth - 116;
const bandColor = "#e1f5fe";

const useStyles = makeStyles(theme => ({
  root: {
    position: "relative",
    display: "flex",
    margin: theme.spacing(0),
    alignItems: "center",
    padding: theme.spacing(0),
    transition: "all 0.3s"
  },
  placeholder: {
    margin: "0 auto"
  },
  button: {
    margin: theme.spacing(0),
    position: "absolute",
    top: 0,
    left: 0
  },
  collapse: {
    bottom: "-320px"
  }
}));

function DataTimeline({
  onDateRangeReset,
  setSelectedStartDate,
  setSelectedEndDate,
  setSliderValuesFromDates,
  showControls,
  chartZoomReset,
  setChartZoomReset
}) {
  const dataLayers = useSelector(state => state.dataLayers.layers);
  const dateFilter = useSelector(state => state.dateFilter);
  const dispatch = useDispatch();
  const chartRef = useRef();

  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();
  const [chartData, setChartData] = useState([]);
  const [chartBands, setChartBands] = useState([]);
  const [chartWidth, setChartWidth] = useState(widthWithDashboard);
  const classes = useStyles();

  useEffect(() => {
    async function fetchResults() {
      try {
        const res = await axiosInstance.get("api/v1/core/data-density/");
        console.log(res.request.responseURL);
        setIsLoaded(true);
        setResults(res.data);
      } catch (error) {
        setIsLoaded(true);
        setError(error);
      }
    }
    fetchResults();
  }, [dataLayers]);

  useEffect(() => {
    const newChartData = [];
    if (results) {
      for (let [key, value] of Object.entries(results)) {
        const dataArray = value.map(item => [
          Date.parse(item.timestamp),
          parseFloat(item.densityPercentage)
        ]);

        const timeSeries = {
          name: key,
          data: dataArray
        };

        newChartData.push(timeSeries);
      }
      setChartData(newChartData);
    }
  }, [results]);

  // update Chart Bands when Dates are changed
  useEffect(() => {
    if (dateFilter) {
      const filterStartDate = parseISO(dateFilter.startDate);
      const filterEndDate = parseISO(dateFilter.endDate);
      // if seasonal filter, need to create array of date ranges
      if (dateFilter.seasonal) {
        const yearRange = _.range(
          filterStartDate.getFullYear(),
          filterEndDate.getFullYear()
        );
        const newChartBands = yearRange.map(year => {
          let startDateFields = [
            year,
            filterStartDate.getMonth(),
            filterStartDate.getDate()
          ];
          let endDateFields = [
            year,
            filterEndDate.getMonth(),
            filterEndDate.getDate()
          ];

          if (dateFilter.excludeMonthRange) {
            startDateFields = [
              year,
              filterEndDate.getMonth(),
              filterEndDate.getDate()
            ];
            endDateFields = [
              year + 1,
              filterStartDate.getMonth(),
              filterStartDate.getDate()
            ];
          }

          const startDate = new Date(...startDateFields);
          const endDate = new Date(...endDateFields);

          return {
            color: bandColor,
            from: startDate,
            to: endDate
          };
        });
        setChartBands(newChartBands);
      } else {
        const band = {
          color: bandColor,
          from: filterStartDate,
          to: filterEndDate
        };
        setChartBands([band]);
      }
    }
  }, [dateFilter]);

  useEffect(() => {
    if (showControls) {
      setChartWidth(widthWithDashboard);
    } else {
      setChartWidth(widthFull);
    }
  }, [showControls, dateFilter]);

  useEffect(() => {
    if (chartZoomReset === true) {
      chartRef.current.chart.zoom();
      // option to just resize zoom to match dates
      // chartRef.current.chart.zoomOut();
    }
  }, [chartZoomReset]);

  const chartOptions = {
    chart: {
      type: "spline",
      zoomType: "x",
      width: chartWidth,
      height: 220,
      // update dateFilter state on zoom selection, then set all date controls to match
      events: {
        selection: function(event) {
          if (event.xAxis != null) {
            let start = new Date(Math.ceil(event.xAxis[0].min));
            let end = new Date(Math.floor(event.xAxis[0].max));
            // trigger Redux dispatch function to fetch data
            const payload = {
              startDate: start.toISOString(),
              endDate: end.toISOString(),
              seasonal: dateFilter.seasonal,
              excludeMonthRange: dateFilter.excludeMonthRange
            };
            dispatch(changeDateRange(payload));

            setSelectedStartDate(start);
            setSelectedEndDate(end);
            setSliderValuesFromDates(start, end);
            setChartZoomReset(false);
          } else {
            onDateRangeReset();
          }
        }
      }
    },
    title: {
      text: null
    },
    subtitle: {
      text:
        document.ontouchstart === undefined
          ? "Click and drag in the plot area to select date range"
          : "Pinch the chart to select data range"
    },
    xAxis: {
      type: "datetime",
      plotBands: chartBands
    },
    yAxis: {
      title: {
        text: "Data Density"
      },
      min: 0,
      max: 1
    },
    plotOptions: {
      series: {
        label: {
          enabled: false
        }
        //enableMouseTracking : false,
      }
    },
    tooltip: { enabled: false },
    /*
    tooltip: {
      formatter: function () {
          const sampleTime = format(new Date(this.x), 'MMM yyyy');
          const tooltip = `
              ${sampleTime}<br>
              ${this.series.name}
          `
          return tooltip;
      }
    },
    */
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
          ref={chartRef}
        />
      )}
    </div>
  );
}

export default DataTimeline;
