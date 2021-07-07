import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/styles";
import { CircularProgress } from "@material-ui/core";
import { format, parseISO } from "date-fns";
import SidePane from "./SidePane";
import axiosInstance from "../../../app/apiAxios";

const useStyles = makeStyles(theme => ({
  root: {
    display: "flex",
    margin: theme.spacing(1),
    width: 600,
    height: 300,
    backgroundColor: "white",
    alignItems: "center",
    padding: theme.spacing(2)
  },
  placeholder: {
    margin: "0 auto"
  }
}));

export default function DataPanel({
  featureID,
  dataLayer,
  yAxisScale,
  onPaneClose
}) {
  const dateFilter = useSelector(state => state.dateFilter);
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  const [isLoaded, setIsLoaded] = useState(false);
  const [results, setResults] = useState();
  const [hasData, setHasData] = useState(true);
  const classes = useStyles();

  useEffect(() => {
    // Need to check different properties to see whether the API result has data for time frame
    function hasData(result, dataLayer) {
      console.log(result);
      if (dataLayer === "stations-layer" || dataLayer === "ifcb-layer") {
        result.properties.maxMeanValues.length
          ? setHasData(true)
          : setHasData(false);
      }
    }

    async function fetchResults() {
      try {
        let endpoint;
        let smoothingFactor = dateFilter.smoothingFactor;
        if (dataLayer === "stations-layer") {
          endpoint = `api/v1/stations/${featureID}/`;
          // Force smoothing_factor to be ignored for Station graphs
          smoothingFactor = 1;
        } else if (dataLayer === "ifcb-layer") {
          endpoint = `api/v1/ifcb-datasets/${featureID}/`;
        } else if (dataLayer === "closures-layer") {
          endpoint = `api/v1/closures/${featureID}/`;
        }

        const params = new URLSearchParams({
          start_date: format(parseISO(dateFilter.startDate), "MM/dd/yyyy"),
          end_date: format(parseISO(dateFilter.endDate), "MM/dd/yyyy"),
          seasonal: dateFilter.seasonal,
          exclude_month_range: dateFilter.excludeMonthRange,
          smoothing_factor: smoothingFactor
        });
        const res = await axiosInstance.get(endpoint, {
          params
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
  }, [featureID, dataLayer, dateFilter]);

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
        />
      )}
    </div>
  );
}
