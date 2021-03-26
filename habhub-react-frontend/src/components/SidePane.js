import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/styles";
import { Card, CardHeader, CardContent, IconButton } from "@material-ui/core";
import { Close, OpenWith, Minimize } from "@material-ui/icons";

import StationsGraph from "./StationsGraph";
import IfcbGraph from "./IfcbGraph";
import ClosuresList from "./ClosuresList";

const expandWidth = window.outerWidth - 420;
const useStyles = makeStyles((theme) => ({
  root: {
    margin: theme.spacing(1),
    width: 600,
    transition: "all 0.3s",
  },
  media: {
    height: 140,
  },
  title: {
    color: theme.palette.primary.main,
    fontSize: "1.2rem",
  },
  header: {
    color: theme.palette.primary.main,
  },
  expand: {
    position: "fixed",
    top: 0,
    left: 10,
    width: expandWidth,
    height: "95vh",
    zIndex: 3000,
    overflowY: "scroll",
  },
  expandContent: {
    width: expandWidth,
    height: "80%",
  },
}));

export default function SidePane({
  results,
  featureID,
  dataLayer,
  yAxisScale,
  onPaneClose,
}) {
  const habSpecies = useSelector((state) => state.habSpecies);
  const classes = useStyles();
  const [expandPane, setExpandPane] = useState(false);
  const [visibleResults, setVisibleResults] = useState([]);

  useEffect(() => {
    // Filter the results to only visible species to pass to the Graph
    if (dataLayer === "ifcb-layer") {
      const data = results.properties.timeseries_data;
      const visibleSpecies = habSpecies
        .filter((species) => species.visibility)
        .map((species) => species.id);

      const filteredData = data.filter((item) =>
        visibleSpecies.includes(item.species)
      );
      setVisibleResults(filteredData);
    }
  }, [results, habSpecies]);

  function onExpandPanel() {
    setExpandPane(!expandPane);
  }

  let title = null;
  let subTitle = null;

  if (dataLayer === "stations-layer") {
    title = `Station Toxicity Data: ${results.properties.station_location}`;
    subTitle = `
      Station Name: ${results.properties.station_name} |
      Lat: ${results.geometry.coordinates[1]} Long: ${results.geometry.coordinates[0]}
    `;
  } else if (dataLayer === "ifcb-layer") {
    title = `IFCB Data: ${results.properties.name}`;
    subTitle = `
      ${results.properties.location} |
      Lat: ${results.geometry.coordinates[1]} Long: ${results.geometry.coordinates[0]}
    `;
  } else if (dataLayer === "closures-layer") {
    title = `Shellfish Closure: ${results.properties.name}`;
    subTitle = `
      State: ${results.properties.state} |
      ${results.properties.area_description}
    `;
  }

  return (
    <Card className={`${expandPane ? classes.expand : ""} ${classes.root}`}>
      <CardHeader
        classes={{
          title: classes.title, // class name, e.g. `classes-nesting-label-x`
        }}
        action={
          <React.Fragment>
            <IconButton onClick={() => onExpandPanel()} aria-label="expand">
              {expandPane ? <Minimize /> : <OpenWith />}
            </IconButton>
            <IconButton
              onClick={() => onPaneClose(featureID)}
              aria-label="close"
            >
              <Close />
            </IconButton>
          </React.Fragment>
        }
        title={title}
        subheader={subTitle}
      />

      <CardContent className={expandPane ? classes.expandContent : ""}>
        {dataLayer === "stations-layer" && (
          <StationsGraph
            results={results}
            chartExpanded={expandPane}
            yAxisScale={yAxisScale}
          />
        )}
        {dataLayer === "ifcb-layer" && visibleResults && (
          <IfcbGraph
            visibleResults={visibleResults}
            chartExpanded={expandPane}
            yAxisScale={yAxisScale}
          />
        )}
        {dataLayer === "closures-layer" && <ClosuresList results={results} />}
      </CardContent>
    </Card>
  );
}
