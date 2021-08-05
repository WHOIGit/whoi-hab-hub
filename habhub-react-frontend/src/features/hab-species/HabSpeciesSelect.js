import React from "react";
import {
  FormLabel,
  FormControl,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Typography
} from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { useSelector, useDispatch } from "react-redux";
import { changeSpeciesVisibility, changeSpeciesColor } from "./habSpeciesSlice";
import { ColorPicker } from "material-ui-color";

const useStyles = makeStyles(() => ({
  formControl: {
    width: "100%"
  },
  colorPickerBtn: {
    display: "inline-block"
  }
}));

export default function HabSpeciesForm() {
  const habSpecies = useSelector(state => state.habSpecies.species);
  const dispatch = useDispatch();
  const classes = useStyles();

  return (
    <FormControl component="fieldset" className={classes.formControl}>
      <FormLabel component="legend">HAB Species/Syndrome</FormLabel>
      <FormGroup>
        {habSpecies.map(species => {
          return (
            <FormControlLabel
              key={species.id}
              control={
                <Checkbox
                  color="primary"
                  checked={species.visibility}
                  onChange={event =>
                    dispatch(
                      changeSpeciesVisibility({
                        checked: event.target.checked,
                        species: species
                      })
                    )
                  }
                  name={species.speciesName}
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
                      value={species.primaryColor}
                      hideTextfield
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
