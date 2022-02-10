import React from "react";
import { Grid, Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { useSelector } from "react-redux";

import { DATA_LAYERS } from "../../Constants";
import DiamondMarker from "../../images/diamond.svg";
import CircleMarker from "../../images/circle.svg";
import SquareMarker from "../../images/square-orange.svg";
import ClosureIcon from "../../images/icon-shellfish-closure.png";
import { selectVisibleLayers } from "../data-layers/dataLayersSlice";

const useStyles = makeStyles(() => ({
  formControl: {
    width: "100%",
  },
  layerIcon: {
    width: "25px",
  },
}));

export default function DataLayersList() {
  const dataLayers = useSelector(selectVisibleLayers);
  const classes = useStyles();

  const renderLayerGrid = (dataLayer) => {
    let imgSrc;
    if (dataLayer.id === DATA_LAYERS.stationsLayer) {
      imgSrc = DiamondMarker;
    } else if (
      dataLayer.id === DATA_LAYERS.cellConcentrationLayer ||
      dataLayer.id === DATA_LAYERS.biovolumeLayer
    ) {
      imgSrc = CircleMarker;
    } else if (dataLayer.id === DATA_LAYERS.closuresLayer) {
      imgSrc = ClosureIcon;
    }
    return (
      <div key={dataLayer.id}>
        <Grid item xs={2}>
          {imgSrc && (
            <div>
              <img
                src={imgSrc}
                alt={dataLayer.name}
                className={classes.layerIcon}
              />
            </div>
          )}
        </Grid>
        <Grid item xs={10}>
          <Typography
            variant="body2"
            color="textSecondary"
            className={classes.labelText}
          >
            {dataLayer.name}
          </Typography>
        </Grid>
        {dataLayer.id === "closures-layer" && (
          <>
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
          </>
        )}
      </div>
    );
  };

  return (
    <Grid container spacing={0}>
      {dataLayers.map((layer) => renderLayerGrid(layer))}
    </Grid>
  );
}
