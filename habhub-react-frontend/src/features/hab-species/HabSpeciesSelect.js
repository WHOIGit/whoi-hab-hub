import React from "react";
import {
  FormLabel,
  FormControl,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Typography,
  Box
} from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { useSelector, useDispatch } from "react-redux";
import { changeSpeciesVisibility } from "./habSpeciesSlice";
import HabSpeciesColorChip from "./HabSpeciesColorChip";

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
                <Typography variant="body2" color="textSecondary">
                  <em>{species.displayName}</em> / {species.syndrome}
                  <Box component="span" m={1}>
                    <HabSpeciesColorChip
                      species={species}
                      chipWidth={12}
                      chipHeight={12}
                      chipType="primary"
                    />
                  </Box>
                </Typography>
              }
            />
          );
        })}
      </FormGroup>
    </FormControl>
  );
}
