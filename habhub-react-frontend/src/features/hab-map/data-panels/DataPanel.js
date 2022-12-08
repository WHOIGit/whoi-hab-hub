import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/styles";
import { CircularProgress } from "@material-ui/core";
import { format, parseISO } from "date-fns";
// local
import SidePane from "./SidePane";
import axiosInstance from "../../../app/apiAxios";
import { DATA_LAYERS } from "../../../Constants";
import { selectDateFilter } from "../../date-filter/dateFilterSlice";

const useStyles = makeStyles((theme) => ({
  root: {
    display: "flex",
    margin: theme.spacing(1),
    width: 600,
    height: 300,
    backgroundColor: "white",
    alignItems: "center",
    padding: theme.spacing(2),
  },
  placeholder: {
    margin: "0 auto",
  },
}));

export default function DataPanel({
  featureID,
  dataLayer,
  yAxisScale,
  onPaneClose,
  metricID,
  gridLength,
}) {
  //const dateFilter = useSelector((state) => state.dateFilter);
  const dateFilter = useSelector(selectDateFilter);
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();
  const [hasData, setHasData] = useState(true);
  const classes = useStyles();

  useEffect(() => {
    // Need to check different properties to see whether the API result has data for time frame
    function hasData(result, dataLayer) {
      if (dataLayer !== DATA_LAYERS.closuresLayer) {
        result.properties.maxMeanValues.length
          ? setHasData(true)
          : setHasData(false);
      }
    }

    async function fetchResults() {
      try {
        let endpoint;
        let smoothingFactor = dateFilter.smoothingFactor;
        if (dataLayer === DATA_LAYERS.stationsLayer) {
          endpoint = `api/v1/stations/${featureID}/`;
          // Force smoothing_factor to be ignored for Station graphs
          smoothingFactor = 1;
        } else if (
          dataLayer === DATA_LAYERS.cellConcentrationLayer ||
          dataLayer === DATA_LAYERS.biovolumeLayer
        ) {
          endpoint = `api/v1/ifcb-datasets/${featureID}/`;
        } else if (
          dataLayer === DATA_LAYERS.cellConcentrationSpatialGridLayer ||
          dataLayer === DATA_LAYERS.biovolumeSpatialGridLayer
        ) {
          endpoint = `api/v1/ifcb-spatial-grid/${featureID}/`;
          // Match smoothing_factor for Spatial Grid graphs
          smoothingFactor = 4;
        } else if (
          dataLayer === DATA_LAYERS.closuresLayer ||
          dataLayer === DATA_LAYERS.closuresSeasonalLayer
        ) {
          endpoint = `api/v1/closures/${featureID}/`;
        }

        const params = new URLSearchParams({
          start_date: format(parseISO(dateFilter.startDate), "yyyy-MM-dd"),
          end_date: format(parseISO(dateFilter.endDate), "yyyy-MM-dd"),
          seasonal: dateFilter.seasonal,
          exclude_month_range: dateFilter.excludeMonthRange,
          smoothing_factor: smoothingFactor,
          grid_level: gridLength,
        });
        const res = await axiosInstance.get(endpoint, {
          params,
        });
        console.log(res.request.responseURL);
        setIsLoaded(true);
        setResults(res.data);
        hasData(res.data, dataLayer);
      } catch (error) {
        setIsLoaded(true);
        setError(error);
      }
    }
    fetchResults();
  }, [featureID, dataLayer, dateFilter, metricID]);

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
          metricID={metricID}
        />
      )}
    </div>
  );
}
