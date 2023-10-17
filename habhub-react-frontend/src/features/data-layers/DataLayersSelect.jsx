import React from "react";
import {
  FormLabel,
  FormControl,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Typography,
  Grid,
} from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { useSelector, useDispatch } from "react-redux";
import { changeLayerVisibility } from "./dataLayersSlice";
import DiamondMarker from "../../images/diamond.svg";
import CircleMarker from "../../images/circle.svg";
import TriangleMarker from "../../images/triangle.svg";
// local
import { DATA_LAYERS } from "../../Constants";

const useStyles = makeStyles((theme) => ({
  formControl: {
    width: "100%",
  },
  checkBoxes: {
    ...theme.typography.body2,
  },
  label: {
    width: "100%",
  },
  labelText: {
    paddingTop: "5px",
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

export default function HabSpeciesForm() {
  const dataLayers = useSelector((state) => state.dataLayers.layers);
  const dispatch = useDispatch();
  const classes = useStyles();

  const handleCheckboxChange = (event, dataLayer) => {
    // only one of cell concentration-layer/biovolume-layer can be active at one time

    if (
      dataLayer.id === DATA_LAYERS.cellConcentrationLayer &&
      event.target.checked
    ) {
      dispatch(
        changeLayerVisibility({
          checked: false,
          layerID: DATA_LAYERS.biovolumeLayer,
        })
      );
    }

    if (
      dataLayer.id === DATA_LAYERS.cellConcentrationSpatialGridLayer &&
      event.target.checked
    ) {
      dispatch(
        changeLayerVisibility({
          checked: false,
          layerID: DATA_LAYERS.biovolumeSpatialGridLayer,
        })
      );
    }

    if (dataLayer.id === DATA_LAYERS.biovolumeLayer && event.target.checked) {
      dispatch(
        changeLayerVisibility({
          checked: false,
          layerID: DATA_LAYERS.cellConcentrationLayer,
        })
      );
    }

    if (
      dataLayer.id === DATA_LAYERS.biovolumeSpatialGridLayer &&
      event.target.checked
    ) {
      dispatch(
        changeLayerVisibility({
          checked: false,
          layerID: DATA_LAYERS.cellConcentrationSpatialGridLayer,
        })
      );
    }

    dispatch(
      changeLayerVisibility({
        checked: event.target.checked,
        layerID: dataLayer.id,
      })
    );
  };

  const renderLayerControl = (dataLayer) => {
    return (
      <FormControlLabel
        classes={{
          root: classes.checkBoxes, // class name, e.g. `classes-nesting-root-x`
          label: classes.label, // class name, e.g. `classes-nesting-label-x`
        }}
        key={dataLayer.id}
        control={
          <Checkbox
            color="primary"
            checked={dataLayer.visibility}
            onChange={(event) => handleCheckboxChange(event, dataLayer)}
            name={dataLayer.name}
          />
        }
        label={
          <Grid container spacing={0}>
            <Grid item xs={11}>
              <Typography
                variant="body2"
                color="textSecondary"
                className={classes.labelText}
              >
                {dataLayer.name}
              </Typography>
            </Grid>
            <Grid item xs={1}>
              <div>
                {dataLayer.id === DATA_LAYERS.stationsLayer && (
                  <img
                    src={DiamondMarker}
                    alt="Station Toxicity Legend Icon"
                    className={classes.layerIcon}
                  />
                )}

                {dataLayer.id === DATA_LAYERS.cellConcentrationLayer && (
                  <img
                    src={CircleMarker}
                    alt="Fixed Location Legend Icon"
                    className={classes.layerIcon}
                  />
                )}

                {dataLayer.id ===
                  DATA_LAYERS.cellConcentrationSpatialGridLayer && (
                  <img
                    src={TriangleMarker}
                    alt="Spatial Grid Legend Icon"
                    className={classes.layerIcon}
                  />
                )}

                {dataLayer.id === DATA_LAYERS.biovolumeLayer && (
                  <img
                    src={CircleMarker}
                    alt="Biovolume Legend Icon"
                    className={classes.layerIcon}
                  />
                )}

                {dataLayer.id === DATA_LAYERS.closuresLayer && (
                  <img
                    src="/images/icon-shellfish-closure.png"
                    alt="Closures Legend Icon"
                    className={`${classes.layerIcon} ${classes.closureIcon}`}
                  />
                )}

                {dataLayer.id === DATA_LAYERS.closuresSeasonalLayer && (
                  <img
                    src="/images/icon-shellfish-closure.png"
                    alt="Closures Legend Icon"
                    className={`${classes.layerIcon} ${classes.closureSeasonalIcon}`}
                  />
                )}
              </div>
            </Grid>
          </Grid>
        }
      />
    );
  };

  return (
    <FormControl component="fieldset" className={classes.formControl}>
      <FormLabel component="legend">Data Layers</FormLabel>
      <FormGroup>
        {dataLayers.map((layer) => renderLayerControl(layer))}
      </FormGroup>
    </FormControl>
  );
}
