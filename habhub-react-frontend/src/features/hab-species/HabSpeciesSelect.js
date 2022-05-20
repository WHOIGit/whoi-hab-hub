/* eslint-disable no-unused-vars */
import React from "react";
import {
  Box,
  FormControl,
  Typography
} from "@mui/material";
import { makeStyles } from "@mui/styles";
import { useSelector, useDispatch } from "react-redux";
import HabSpeciesSelectByEnv from "./HabSpeciesSelectByEnv";

const useStyles = makeStyles(theme => ({
  formControl: {
    width: "100%",
    marginTop: theme.spacing(2)
  },
  colorPickerBtn: {
    display: "inline-block"
  },
  infoText: {
    width: "95%"
  }
}));

export default function HabSpeciesSelect() {
  const habSpecies = useSelector(state => state.habSpecies.species);
  const habEnvironments = useSelector(state => state.habSpecies.enviroments);
  const dispatch = useDispatch();
  const classes = useStyles();
  const error = habSpecies.filter(item => item.visibility).length > 6;
  const limitReached = habSpecies.filter(item => item.visibility).length >= 6;

  return (
    <div>
      <Typography variant="subtitle1" display="block" gutterBottom>
        Algal Species/Syndrome
      </Typography>

      <Typography
        variant="body2"
        display="block"
        gutterBottom
        className={classes.infoText}
      >
        Choose up to <strong>6 species</strong> to display on the map at one
        time. Click on the color box to change color palette.
      </Typography>
      <Box>
        <FormControl
          required
          error={error}
          component="fieldset"
          className={classes.formControl}
        >
          {habEnvironments.map(item => (
            <Box key={item}>
              <HabSpeciesSelectByEnv
                environment={item}
                limitReached={limitReached}
              />
            </Box>
          ))}
        </FormControl>
      </Box>
    </div>
  );
}
