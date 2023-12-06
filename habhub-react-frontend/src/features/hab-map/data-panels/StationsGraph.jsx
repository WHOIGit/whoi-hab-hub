import React, { useState, useEffect, useRef } from "react";
import { makeStyles } from "@material-ui/styles";
import Highcharts from "highcharts";
import Exporting from "highcharts/modules/exporting";
import ExportData from "highcharts/modules/export-data";
import Serieslabel from "highcharts/modules/series-label";
import HighchartsReact from "highcharts-react-official";
// need to add this extra window variable declaration
// Highcharts has internal references that rely on it being defined on the window
window.Highcharts = Highcharts;

Exporting(Highcharts);
ExportData(Highcharts);
Serieslabel(Highcharts);

const expandWidth = window.outerWidth - 430;

// eslint-disable-next-line no-unused-vars
const useStyles = makeStyles((theme) => ({
  chartContainer: {},
  chartContainerExpand: {
    width: expandWidth,
    height: "100%",
  },
}));

// eslint-disable-next-line no-unused-vars
function StationsGraph({ results, chartExpanded, yAxisScale }) {
  const chartRef = useRef();
  const classes = useStyles();
  const [chartOptions, setChartOptions] = useState({});

  useEffect(() => {
    const data = results.properties.timeseriesData;
    const chartData = data
      .map((item) => [Date.parse(item.date), item.measurement])
      .sort();

    const chartOptions = {
      chart: {
        type: "spline",
        zooming: {
          type: "x",
        },
      },
      title: {
        text: null,
      },
      subtitle: {
        text:
          document.ontouchstart === undefined
            ? "Click and drag in the plot area to zoom in"
            : "Pinch the chart to zoom in",
      },
      xAxis: {
        type: "datetime",
      },
      yAxis: {
        title: {
          text: "Shellfish meat toxicity",
        },
        min: 0,
        softMax: 150,
        plotLines: [
          {
            value: 80,
            color: "red",
            dashStyle: "shortdash",
            width: 2,
            label: {
              text: "Closure threshold",
            },
          },
        ],
      },
      plotOptions: {
        series: { threshold: 100 },
      },
      exporting: {
        buttons: {
          contextButton: {
            menuItems: [
              "printChart",
              "separator",
              "downloadPNG",
              "downloadJPEG",
              "downloadPDF",
              "downloadSVG",
              "separator",
              "downloadCSV",
            ],
          },
        },
      },
      series: [
        {
          name: "Shellfish meat toxicity",
          data: chartData,
        },
      ],
    };
    setChartOptions(chartOptions);
  }, [results]);

  useEffect(() => {
    if (chartExpanded) {
      console.log(window.outerWidth, window.outerHeight);
      chartRef.current.chart.setSize(expandWidth, null);
    } else {
      chartRef.current.chart.setSize(550, 300);
    }
  }, [chartExpanded]);
  /*
  useEffect(() => {
    console.log(yAxisScale);
    if (yAxisScale==='linear') {
      console.log(chartRef.current.chart);
      chartRef.current.chart.yAxis[0].update({
        type: 'linear',
        min: 0,
      });
    }
    else if (yAxisScale==='logarithmic') {
      console.log(chartRef.current.chart);
      chartRef.current.chart.yAxis[0].update({
        type: 'logarithmic',
        //minorTickInterval: 1,
        min: 100,
      });
    }
  }, [yAxisScale]);
  */

  return (
    <HighchartsReact
      highcharts={Highcharts}
      options={chartOptions}
      containerProps={
        chartExpanded
          ? { className: classes.chartContainerExpand }
          : { className: classes.chartContainer }
      }
      ref={chartRef}
    />
  );
}

export default StationsGraph;
