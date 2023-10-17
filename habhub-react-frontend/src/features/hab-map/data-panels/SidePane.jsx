import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/styles";
import { Card, CardHeader, CardContent, IconButton } from "@material-ui/core";
import { Close, OpenWith, Minimize } from "@material-ui/icons";
// local
import StationsGraph from "./StationsGraph";
import IfcbGraph from "./IfcbGraph";
import ClosuresList from "./ClosuresList";
import { selectVisibleSpecies } from "../../hab-species/habSpeciesSlice";
import { DATA_LAYERS, METRIC_IDS } from "../../../Constants";

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
  metricID,
}) {
  const habSpecies = useSelector(selectVisibleSpecies);
  const classes = useStyles();
  const [expandPane, setExpandPane] = useState(false);
  const [visibleResults, setVisibleResults] = useState([]);

  useEffect(() => {
    // Filter the results to only visible species to pass to the Graph

    if (metricID && metricID !== METRIC_IDS.shellfishToxicity) {
      const data = results.properties.timeseriesData;
      const visibleSpecies = habSpecies
        .filter((species) => species.visibility)
        .map((species) => species.id);

      const filteredData = data.filter((item) =>
        visibleSpecies.includes(item.species)
      );
      setVisibleResults(filteredData);
    }
  }, [results, habSpecies, metricID]);

  function onExpandPanel() {
    setExpandPane(!expandPane);
  }

  let title;
  let subTitle;

  if (dataLayer === DATA_LAYERS.stationsLayer) {
    title = `Station Toxicity Data: ${results.properties?.stationLocation}`;
    subTitle = `
      Station Name: ${results.properties?.station_name} |
      Lat: ${results.geometry.coordinates[1]} Long: ${results.geometry.coordinates[0]}
    `;
  } else if (
    dataLayer === DATA_LAYERS.closuresLayer ||
    dataLayer === DATA_LAYERS.closuresSeasonalLayer
  ) {
    title = `Shellfish Closure: ${results.properties?.name}`;
    subTitle = `
      State: ${results.properties?.state} |
      ${results.properties?.areaDescription}
    `;
  } else if (
    dataLayer === DATA_LAYERS.cellConcentrationSpatialGridLayer ||
    dataLayer === DATA_LAYERS.biovolumeSpatialGridLayer
  ) {
    // calculate approx grid area. 1 degicmal degree = 111 km
    // let gridArea = Math.pow(gridLength * 111, 2);
    title = `Grid Center Point | Lat: ${results.geometry.coordinates[1]}, Long: ${results.geometry.coordinates[0]}`;
    //subTitle = `Grid Area (km<sup>2</sup): ${gridArea}`;
  } else {
    title = `IFCB Data: ${results.properties?.name}`;
    subTitle = `
      ${results.properties?.location} |
      Lat: ${results.geometry.coordinates[1]} Long: ${results.geometry.coordinates[0]}
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
        {dataLayer === DATA_LAYERS.stationsLayer && (
          <StationsGraph
            results={results}
            chartExpanded={expandPane}
            yAxisScale={yAxisScale}
          />
        )}
        {metricID &&
          metricID !== METRIC_IDS.shellfishToxicity &&
          visibleResults && (
            <IfcbGraph
              visibleResults={visibleResults}
              metricID={metricID}
              chartExpanded={expandPane}
              yAxisScale={yAxisScale}
              dataLayer={dataLayer}
            />
          )}
        {(dataLayer === DATA_LAYERS.closuresLayer ||
          dataLayer === DATA_LAYERS.closuresSeasonalLayer) && (
          <ClosuresList results={results} />
        )}
      </CardContent>
    </Card>
  );
}
