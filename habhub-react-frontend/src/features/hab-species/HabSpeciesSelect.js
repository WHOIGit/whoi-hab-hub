import React from "react";
import {
  FormLabel,
  FormControl,
  FormGroup,
  FormControlLabel,
  FormHelperText,
  Checkbox,
  Typography
} from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { useSelector, useDispatch } from "react-redux";
import { changeSpeciesVisibility, changeSpeciesColor } from "./habSpeciesSlice";
import { ColorPicker } from "material-ui-color";
import { palette } from "../../config.js";

const useStyles = makeStyles(() => ({
  formControl: {
    width: "100%",
    maxHeight: "340px",
    overflowY: "scroll"
  },
  colorPickerBtn: {
    display: "inline-block"
  }
}));

export default function HabSpeciesForm() {
  const habSpecies = useSelector(state => state.habSpecies.species);
  const dispatch = useDispatch();
  const classes = useStyles();
  const error = habSpecies.filter(item => item.visibility).length > 6;
  const limitReached = habSpecies.filter(item => item.visibility).length >= 6;

  const handleSpeciesSelect = (event, species) => {
    dispatch(
      changeSpeciesVisibility({
        checked: event.target.checked,
        species: species
      })
    );
  };

  return (
    <FormControl
      required
      error={error}
      component="fieldset"
      className={classes.formControl}
    >
      <FormLabel component="legend">HAB Species/Syndrome</FormLabel>
      <FormHelperText>Pick up to six</FormHelperText>
      <FormGroup>
        {habSpecies.map(species => {
          return (
            <FormControlLabel
              key={species.id}
              control={
                <Checkbox
                  color="primary"
                  checked={species.visibility}
                  onChange={event => handleSpeciesSelect(event, species)}
                  name={species.speciesName}
                  disabled={limitReached && !species.visibility}
                />
              }
              label={
                <Typography
                  variant="body2"
                  color="textSecondary"
                  component="span"
                >
                  {" "}
                  <div className={classes.colorPickerBtn}>
                    <ColorPicker
                      palette={palette}
                      value={species.primaryColor}
                      hideTextfield
                      disableAlpha
                      onChange={event =>
                        dispatch(
                          changeSpeciesColor({
                            primaryColor: "#" + event.hex,
                            species: species
                          })
                        )
                      }
                    />
                  </div>
                  <em>{species.displayName}</em> / {species.syndrome}
                </Typography>
              }
            />
          );
        })}
      </FormGroup>
    </FormControl>
  );
}
