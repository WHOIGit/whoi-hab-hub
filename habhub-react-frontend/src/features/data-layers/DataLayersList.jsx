import React from "react";
import { Grid, Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { useSelector } from "react-redux";

import { DATA_LAYERS } from "../../Constants";
import DiamondMarker from "../../images/diamond.svg";
import CircleMarker from "../../images/circle.svg";
import TriangleMarker from "../../images/triangle.svg";
import ClosureIcon from "../../images/icon-shellfish-closure.png";
import { selectVisibleLayers } from "./dataLayersSlice";

const useStyles = makeStyles(() => ({
  formControl: {
    width: "100%",
  },
  layerIcon: {
    width: "25px",
  },
  closureIcon: {
    backgroundColor: "#f2b036",
  },
  closureSeasonalIcon: {
    backgroundColor: "#FFEB3B",
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
    } else if (
      dataLayer.id === DATA_LAYERS.cellConcentrationSpatialGridLayer ||
      dataLayer.id === DATA_LAYERS.biovolumeSpatialGridLayer
    ) {
      imgSrc = TriangleMarker;
    } else if (
      dataLayer.id === DATA_LAYERS.closuresLayer ||
      dataLayer.id === DATA_LAYERS.closuresSeasonalLayer
    ) {
      imgSrc = ClosureIcon;
    }

    return (
      <Grid container spacing={2} key={dataLayer.id}>
        <Grid item xs={2}>
          {imgSrc && (
            <div>
              <img
                src={imgSrc}
                alt={dataLayer.name}
                className={`${classes.layerIcon} ${
                  dataLayer.id === DATA_LAYERS.closuresLayer
                    ? classes.closureIcon
                    : ""
                }  ${
                  dataLayer.id === DATA_LAYERS.closuresSeasonalLayer
                    ? classes.closureSeasonalIcon
                    : ""
                }`}
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
      </Grid>
    );
  };

  return dataLayers.map((layer) => renderLayerGrid(layer));
}
