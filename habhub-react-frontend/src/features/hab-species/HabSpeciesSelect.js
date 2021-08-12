/* eslint-disable no-unused-vars */
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
import {
  changeSpeciesVisibility,
  changeSpeciesColor,
  selectSpeciesByEnvironment
} from "./habSpeciesSlice";
import HabSpeciesSelectByEnv from "./HabSpeciesSelectByEnv";
import { palette } from "../../config.js";

const useStyles = makeStyles(() => ({
  formControl: {
    width: "100%"
  },
  colorPickerBtn: {
    display: "inline-block"
  }
}));

export default function HabSpeciesSelect() {
  const habSpecies = useSelector(state => state.habSpecies.species);
  const habEnvironments = useSelector(state => state.habSpecies.enviroments);
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
    <div>
      <Typography variant="subtitle1" display="block" gutterBottom>
        HAB Species/Syndrome
      </Typography>

      <FormControl
        required
        error={error}
        component="fieldset"
        className={classes.formControl}
      >
        {habEnvironments.map(item => (
          <>
            <HabSpeciesSelectByEnv
              environment={item}
              limitReached={limitReached}
            />
          </>
        ))}
      </FormControl>
    </div>
  );
}
