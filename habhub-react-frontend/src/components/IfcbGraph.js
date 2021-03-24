import React, { useState, useEffect, useRef } from "react";
import { makeStyles } from "@material-ui/styles";
import { IconButton } from "@material-ui/core";
import { Close } from "@material-ui/icons";
import Highcharts from "highcharts";
import Exporting from "highcharts/modules/exporting";
import ExportData from "highcharts/modules/export-data";
import Serieslabel from "highcharts/modules/series-label";
import HighchartsReact from "highcharts-react-official";
// Local imports
import IfcbMetaData from "./IfcbMetaData";
import { species } from "../Constants";

Exporting(Highcharts);
ExportData(Highcharts);
Serieslabel(Highcharts);

const API_URL = process.env.REACT_APP_API_URL;
const expandWidth = window.outerWidth - 430;

// eslint-disable-next-line no-unused-vars
const useStyles = makeStyles((theme) => ({
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
function IfcbGraph({ visibleResults, chartExpanded, yAxisScale }) {
  const classes = useStyles();
  const chartRef = useRef();
  // Local state
  const [chartOptions, setChartOptions] = useState({});
  const [metaDataUrl, setMetaDataUrl] = useState(null);
  const [openMetaData, setOpenMetaData] = useState(false);
  console.log(visibleResults);

  useEffect(() => {
    const chartData = visibleResults.map((item) => handleChartDataFormat(item));

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
                    bin_pid: pointData.bin_pid,
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
      },
      series: chartData,
    };
    setChartOptions(newChartOptions);
  }, [visibleResults]);

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
  function handleChartDataFormat(dataObj) {
    const dataArray = dataObj.data
      .map((item) => [Date.parse(item.sample_time), item.cell_concentration])
      .sort();

    const seriesColor = species
      .filter((item) => item.id === dataObj.species)
      .map((item) => item.colorPrimary)
      .toString();

    const timeSeries = {
      color: seriesColor,
      name: dataObj.species_display,
      data: dataArray,
    };
    return timeSeries;
  }

  function highChartsGetMetaData(point) {
    // Get the original data structure with metadata for this point by matching timestamps
    const timeSeries = visibleResults.find(
      (series) => series.species_display === point.series.name
    );
    console.log(timeSeries);
    const pointData = timeSeries.data.find(
      (row) => Date.parse(row.sample_time) === point.x
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
