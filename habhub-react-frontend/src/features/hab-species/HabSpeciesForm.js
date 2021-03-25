import React from "react";
import {
  FormLabel,
  FormControl,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Typography,
  Box,
} from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { useSelector, useDispatch } from "react-redux";
import { changeSpeciesVisibility } from "./habSpeciesSlice";

const useStyles = makeStyles(() => ({
  formControl: {
    width: "100%",
  },
}));

function renderColorChips(
  species,
  chipWidth = 20,
  chipHeight = 20,
  chipType = "gradient"
) {
  // default to show all colors in gradient list
  // if chipType is "primary", only show single chip for primary color
  let colors = species.colorGradient;
  if (chipType === "primary") {
    colors = [species.colorPrimary];
  }

  let svgWidth = chipWidth * colors.length;

  return (
    <svg width={svgWidth} height={chipHeight}>
      {colors.map((color, index) => (
        <rect
          width={chipWidth}
          height={chipHeight}
          fill={color}
          x={index * chipWidth}
          key={index}
        ></rect>
      ))}
    </svg>
  );
}

export function HabSpeciesForm() {
  const habSpecies = useSelector((state) => state.habSpecies);
  const dispatch = useDispatch();
  const classes = useStyles();

  return (
    <FormControl component="fieldset" className={classes.formControl}>
      <FormLabel component="legend">HAB Species/Syndrome</FormLabel>
      <FormGroup>
        {habSpecies.map((species) => {
          return (
            <FormControlLabel
              key={species.id}
              control={
                <Checkbox
                  color="primary"
                  checked={species.visibility}
                  onChange={(event) =>
                    dispatch(
                      changeSpeciesVisibility({
                        checked: event.target.checked,
                        species: species,
                      })
                    )
                  }
                  name={species.speciesName}
                />
              }
              label={
                <Typography variant="body2" color="textSecondary">
                  <em>{species.speciesName}</em> / {species.syndrome}
                  <Box component="span" m={1}>
                    {renderColorChips(species, 12, 12, "primary")}
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
