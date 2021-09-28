import React, { useState, useEffect, useRef } from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/styles";
import { IconButton } from "@material-ui/core";
import { Close } from "@material-ui/icons";
import Highcharts from "highcharts";
import Exporting from "highcharts/modules/exporting";
import ExportData from "highcharts/modules/export-data";
import OfflineExporting from "highcharts/modules/offline-exporting";
import Serieslabel from "highcharts/modules/series-label";
import HighchartsReact from "highcharts-react-official";
// Local imports
import IfcbMetaData from "./IfcbMetaData";
import { selectVisibleSpecies } from "../../hab-species/habSpeciesSlice";

Exporting(Highcharts);
ExportData(Highcharts);
Serieslabel(Highcharts);
OfflineExporting(Highcharts);

// eslint-disable-next-line no-undef
const API_URL = process.env.REACT_APP_API_URL;
const expandWidth = window.outerWidth - 430;

const useStyles = makeStyles(() => ({
  chartContainer: {},
  chartContainerExpand: {
    width: expandWidth,
    height: "100%",
  },
  metaDataCloseBtn: {
    textAlign: "right",
  },
}));

// eslint-disable-next-line no-unused-vars
function IfcbGraph({ visibleResults, metricName, chartExpanded, yAxisScale }) {
  const habSpecies = useSelector(selectVisibleSpecies);
  const classes = useStyles();
  const chartRef = useRef();
  // Local state
  const [chartOptions, setChartOptions] = useState({});
  const [metaDataUrl, setMetaDataUrl] = useState(null);
  const [openMetaData, setOpenMetaData] = useState(false);

  useEffect(() => {
    const chartData = visibleResults.map(item =>
      handleChartDataFormat(item, metricName)
    );

    const newChartOptions = {
      chart: {
        type: "spline",
        zoomType: "x",
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
          text: "Cell concentration (cells/L)",
        },
        type: "linear",
        min: 0,
      },
      legend: {
        itemStyle: {
          fontStyle: "italic",
        },
      },
      tooltip: {
        formatter: function () {
          // eslint-disable-next-line no-unused-vars
          const [y_value, pointData] = highChartsGetMetaData(this);
          const sampleTime = new Date(this.x).toISOString().split("T")[0];
          const tooltip = `
                ${sampleTime}<br>
                <i>${this.series.name}</i>: ${y_value} cells/L<br>
                Click to see IFCB images<br>
            `;
          return tooltip;
        },
      },
      plotOptions: {
        series: {
          cursor: "pointer",
          point: {
            events: {
              click: function () {
                // eslint-disable-next-line no-unused-vars
                const [y_value, pointData] = highChartsGetMetaData(this);
                console.log(this.series.name, pointData);
                // build API URL to get BIN images
                const url =
                  `${API_URL}ifcb-datasets/maps/ajax/get-bin-images-species/?` +
                  new URLSearchParams({
                    species: this.series.name,
                    bin_pid: pointData.binPid,
                    format: "json",
                  });
                setMetaDataUrl(url);
                setOpenMetaData(true);
              },
            },
          },
        },
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
        sourceWidth: 600,
        sourceHeight: 400,
        scale: 2,
        fallbackToExportServer: false,
      },
      series: chartData,
    };
    setChartOptions(newChartOptions);
  }, [visibleResults, metricName]);

  useEffect(() => {
    if (chartExpanded) {
      chartRef.current.chart.setSize(expandWidth, null);
    } else {
      chartRef.current.chart.setSize(550, 300);
    }
  }, [chartExpanded]);
  /*
  useEffect(() => {
    if (yAxisScale==='linear') {
      console.log(chartRef.current.chart);
      chartRef.current.chart.yAxis[0].update({
        type: 'linear',
        min: 0,
      });
    } else {
      console.log(chartRef.current.chart);
      chartRef.current.chart.yAxis[0].update({
        type: 'logarithmic',
        minorTickInterval: 1,
        min: 100,
      });
    }
  }, [yAxisScale]);
  */
  function handleChartDataFormat(dataObj, metricName) {
    // set up data arrays for Highcharts format.
    // match the value displayed to the metricName
    console.log(dataObj);
    const dataArray = dataObj.data
<<<<<<< HEAD
      .map(item => {
        const sampleTime = Date.parse(item.sampleTime);
        const metricValue = item.metrics.find(
          metric => metric.metricName === metricName
        ).value;
        return [sampleTime, metricValue];
      })
=======
      .map((item) => [Date.parse(item.sampleTime), item.cellConcentration])
>>>>>>> main
      .sort();

    const seriesColor = habSpecies.find((item) => item.id === dataObj.species);

    const timeSeries = {
      color: seriesColor.primaryColor,
      name: dataObj.speciesDisplay,
      data: dataArray,
    };
    return timeSeries;
  }

  function highChartsGetMetaData(point) {
    // Get the original data structure with metadata for this point by matching timestamps
    const timeSeries = visibleResults.find(
      (series) => series.speciesDisplay === point.series.name
    );
    console.log(timeSeries);
    const pointData = timeSeries.data.find(
      (row) => Date.parse(row.sampleTime) === point.x
    );
    console.log(pointData);

    let y_value = point.y;
    if (point.y == 1) {
      y_value = 0;
    }
    return [y_value, pointData];
  }

  return (
    <React.Fragment>
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

      {openMetaData && (
        <div>
          <div className={classes.metaDataCloseBtn}>
            <IconButton
              onClick={() => setOpenMetaData(!openMetaData)}
              aria-label="close image panel"
            >
              <Close fontSize="small" />
            </IconButton>
          </div>
          <div>
            <IfcbMetaData
              metaDataUrl={metaDataUrl}
              chartExpanded={chartExpanded}
            />
          </div>
        </div>
      )}
    </React.Fragment>
  );
}

export default IfcbGraph;
