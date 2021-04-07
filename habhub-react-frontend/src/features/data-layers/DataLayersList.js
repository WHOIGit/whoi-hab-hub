import React from "react";
import { Grid, Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { useSelector } from "react-redux";

import DiamondMarker from "../../images/diamond.svg";
import CircleMarker from "../../images/circle.svg";
import SquareMarker from "../../images/square-orange.svg";
import ClosureIcon from "../../images/icon-shellfish-closure.png";

const useStyles = makeStyles(() => ({
  formControl: {
    width: "100%"
  },
  layerIcon: {
    width: "25px"
  }
}));

export default function DataLayersList() {
  const dataLayers = useSelector(state => state.dataLayers.layers);
  const classes = useStyles();

  const renderLayerGrid = dataLayer => {
    let imgSrc;
    if (dataLayer.id === "stations-layer") {
      imgSrc = DiamondMarker;
    } else if (dataLayer.id === "ifcb-layer") {
      imgSrc = CircleMarker;
    } else if (dataLayer.id === "closures-layer") {
      imgSrc = ClosureIcon;
    }
    return (
      <>
        <Grid item xs={2}>
          <div>
            <img
              src={imgSrc}
              alt={dataLayer.name}
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
      </>
    );
  };

  return (
    <Grid container spacing={0}>
      {dataLayers.map(layer => renderLayerGrid(layer))}
    </Grid>
  );
}
