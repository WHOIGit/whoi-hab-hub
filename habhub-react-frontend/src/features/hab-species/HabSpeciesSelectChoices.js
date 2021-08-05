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
import { changeSpeciesActiveOption } from "./habSpeciesSlice";

const useStyles = makeStyles(() => ({
  formControl: {
    width: "100%"
  }
}));

export default function HabSpeciesForm() {
  const habSpecies = useSelector(state => state.habSpecies.species);
  const dispatch = useDispatch();
  const classes = useStyles();

  return (
    <FormControl component="fieldset" className={classes.formControl}>
      <FormLabel component="legend">Pick Six</FormLabel>
      <FormGroup>
        {habSpecies.map(species => {
          return (
            <FormControlLabel
              key={species.id}
              control={
                <Checkbox
                  color="primary"
                  checked={species.isActive}
                  onChange={event =>
                    dispatch(
                      changeSpeciesActiveOption({
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
