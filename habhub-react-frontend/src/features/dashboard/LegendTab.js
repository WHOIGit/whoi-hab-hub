import React from "react";
import { useSelector, useDispatch } from "react-redux";
import { makeStyles } from "@material-ui/core/styles";
import { Typography, Divider, IconButton, Tooltip } from "@material-ui/core";
import { Launch } from "@material-ui/icons";

import LegendToxicity from "../legends/LegendToxicity";
import LegendCellConcentration from "../legends/LegendCellConcentration";
import HabSpeciesList from "../hab-species/HabSpeciesList";
import DataLayersList from "../data-layers/DataLayersList";
import {
  changeLegendVisibility,
  selectVisibleLayerIds,
} from "../data-layers/dataLayersSlice";
import { DATA_LAYERS } from "../../Constants";

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
  popper: {
    zIndex: 9999,
  },
}));

export default function LegendTab() {
  const classes = useStyles();
  const dispatch = useDispatch();
  const dataLayers = useSelector(selectVisibleLayerIds);

  const handleLegendOpen = (layerID) => {
    dispatch(
      changeLegendVisibility({
        layerID: layerID,
        legendVisibility: true,
      })
    );
  };

  return (
    <div className={classes.root}>
      <div className={`${classes.legendBox} ${classes.legendBoxTop}`}>
        <Typography variant="subtitle1" display="block" gutterBottom>
          Data Sources
        </Typography>

        <DataLayersList />
      </div>
      <Divider />

      <div className={classes.legendBox}>
        <Typography variant="subtitle1" display="block" gutterBottom>
          HAB Species/Syndrome
        </Typography>

        <HabSpeciesList />
      </div>
      <Divider />

      {(dataLayers.includes(DATA_LAYERS.cellConcentrationLayer) ||
        dataLayers.includes(DATA_LAYERS.cellConcentrationSpatialGridLayer)) && (
        <>
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
                  onClick={() =>
                    handleLegendOpen(DATA_LAYERS.cellConcentrationLayer)
                  }
                  aria-label="open Cell Concentration legend on map"
                >
                  <Launch />
                </IconButton>
              </Tooltip>
            </Typography>
            <LegendCellConcentration />
          </div>
          <Divider />
        </>
      )}

      {dataLayers.includes(DATA_LAYERS.stationsLayer) && (
        <>
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
                  onClick={() => handleLegendOpen(DATA_LAYERS.stationsLayer)}
                  aria-label="open Shellfish Toxicity legend on map"
                >
                  <Launch />
                </IconButton>
              </Tooltip>
            </Typography>
            <LegendToxicity />
          </div>
          <Divider />
        </>
      )}
    </div>
  );
}
