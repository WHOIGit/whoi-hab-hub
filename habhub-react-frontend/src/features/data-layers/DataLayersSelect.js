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
}));

export default function HabSpeciesForm() {
  const dataLayers = useSelector((state) => state.dataLayers);
  const dispatch = useDispatch();
  const classes = useStyles();

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
            onChange={(event) =>
              dispatch(
                changeLayerVisibility({
                  checked: event.target.checked,
                  layerID: dataLayer.id,
                })
              )
            }
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
                {dataLayer.id === "stations-layer" && (
                  <img
                    src={DiamondMarker}
                    alt="Station Toxicity Legend Icon"
                    className={classes.layerIcon}
                  />
                )}

                {dataLayer.id === "ifcb-layer" && (
                  <img
                    src={CircleMarker}
                    alt="IFCB Legend Icon"
                    className={classes.layerIcon}
                  />
                )}

                {dataLayer.id === "closures-layer" && (
                  <img
                    src="images/icon-shellfish-closure.png"
                    alt="Closures Legend Icon"
                    className={`${classes.layerIcon} ${classes.closureIcon}`}
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
