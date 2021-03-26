import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import {
  Typography,
  Divider,
  Grid,
  IconButton,
  Tooltip,
} from "@material-ui/core";
import { Launch } from "@material-ui/icons";

import LegendCellConcentration from "./LegendCellConcentration";
import LegendToxicity from "./LegendToxicity";
import DiamondMarker from "../../images/diamond.svg";
import CircleMarker from "../../images/circle.svg";
import SquareMarker from "../../images/square-orange.svg";
import HabSpeciesList from "../../features/hab-species/HabSpeciesList";

const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(2),
  },
  legendBox: {
    marginTop: theme.spacing(2),
    marginBottom: theme.spacing(2),
  },
  legendBoxTop: {
    marginTop: theme.spacing(0),
  },
  legendDivider: {
    maring: theme.spacing(2),
  },
  layerIcon: {
    width: "25px",
  },
  popper: {
    zIndex: 9999,
  },
}));

export default function LegendTab({ visibleLegends, setVisibleLegends }) {
  const classes = useStyles();

  function handleLegendOpen(layerID) {
    if (visibleLegends.indexOf(layerID) === -1) {
      setVisibleLegends([layerID, ...visibleLegends]);
    }
  }

  return (
    <div className={classes.root}>
      <div className={`${classes.legendBox} ${classes.legendBoxTop}`}>
        <Typography variant="subtitle1" display="block" gutterBottom>
          Data Sources
        </Typography>

        <Grid container spacing={0}>
          <Grid item xs={2}>
            <div>
              <img
                src={DiamondMarker}
                alt="Station Toxicity Legend Icon"
                className={classes.layerIcon}
              />
            </div>
          </Grid>
          <Grid item xs={10}>
            <Typography
              variant="body2"
              color="textSecondary"
              className={classes.labelText}
            >
              Shellfish Toxicity (state data)
            </Typography>
          </Grid>
          <Grid item xs={2}>
            <div>
              <img
                src={CircleMarker}
                alt="IFCB Legend Icon"
                className={classes.layerIcon}
              />
            </div>
          </Grid>
          <Grid item xs={10}>
            <Typography
              variant="body2"
              color="textSecondary"
              className={classes.labelText}
            >
              IFCB
            </Typography>
          </Grid>
          <Grid item xs={2}>
            <div>
              <img
                src="images/icon-shellfish-closure.png"
                alt="Closures Legend Icon"
                className={classes.layerIcon}
              />
            </div>
          </Grid>
          <Grid item xs={10}>
            <Typography
              variant="body2"
              color="textSecondary"
              className={classes.labelText}
            >
              Shellfish Bed Closure
            </Typography>
          </Grid>
          <Grid item xs={2}>
            <div>
              <img
                src={SquareMarker}
                alt="Closures Area Color"
                className={classes.layerIcon}
              />
            </div>
          </Grid>
          <Grid item xs={10}>
            <Typography
              variant="body2"
              color="textSecondary"
              className={classes.labelText}
            >
              Closure Area
            </Typography>
          </Grid>
        </Grid>
      </div>
      <Divider />

      <div className={classes.legendBox}>
        <Typography variant="subtitle1" display="block" gutterBottom>
          HAB Species/Syndrome
        </Typography>

        <HabSpeciesList />
      </div>
      <Divider />

      <div className={classes.legendBox}>
        <Typography variant="subtitle1" display="block" gutterBottom>
          Cell Concentration
          <Tooltip
            title="Open window"
            classes={{
              popper: classes.popper,
            }}
          >
            <IconButton
              onClick={() => handleLegendOpen("ifcb-layer")}
              aria-label="open Cell Concentration legend on map"
            >
              <Launch />
            </IconButton>
          </Tooltip>
        </Typography>
        <LegendCellConcentration />
      </div>
      <Divider />

      <div className={classes.legendBox}>
        <Typography variant="subtitle1" display="block" gutterBottom>
          Shellfish Toxicity
          <Tooltip
            title="Open window"
            classes={{
              popper: classes.popper,
            }}
          >
            <IconButton
              onClick={() => handleLegendOpen("stations-layer")}
              aria-label="open Shellfish Toxicity legend on map"
            >
              <Launch />
            </IconButton>
          </Tooltip>
        </Typography>
        <LegendToxicity />
      </div>
    </div>
  );
}
