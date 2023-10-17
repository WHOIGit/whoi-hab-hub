/* eslint-disable no-unused-vars */
import React from "react";
import {
  FormLabel,
  FormGroup,
  FormControlLabel,
  Checkbox,
  Typography,
} from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { useSelector, useDispatch } from "react-redux";
import {
  changeSpeciesVisibility,
  changeSpeciesColor,
  selectSpeciesByType,
} from "./habSpeciesSlice";
import { ColorPicker } from "material-ui-color";
import { PALETTE } from "../../Constants";
import HabSpeciesNameDisplay from "./HabSpeciesNameDisplay";

const useStyles = makeStyles((theme) => ({
  formGroup: {
    overflowY: "scroll",
    marginBottom: theme.spacing(2),
  },
  colorPickerBtn: {
    display: "inline-block",
  },
}));

export default function HabSpeciesSelectByType({ species_type, limitReached }) {
  const dispatch = useDispatch();
  const classes = useStyles();

  const speciesList = useSelector((state) =>
    selectSpeciesByType(state, species_type)
  );

  const handleSpeciesSelect = (event, species) => {
    dispatch(
      changeSpeciesVisibility({
        checked: event.target.checked,
        species: species,
      })
    );
  };

  if (!speciesList.length) {
    return null;
  }
  return (
    <>
      <FormLabel component="legend">{species_type}</FormLabel>
      <FormGroup className={classes.formGroup}>
        {speciesList.map((species) => {
          return (
            <FormControlLabel
              key={species.id}
              control={
                <Checkbox
                  color="primary"
                  checked={species.visibility}
                  onChange={(event) => handleSpeciesSelect(event, species)}
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
                      palette={PALETTE}
                      value={species.primaryColor}
                      hideTextfield
                      disableAlpha
                      onChange={(event) =>
                        dispatch(
                          changeSpeciesColor({
                            primaryColor: "#" + event.hex,
                            species: species,
                          })
                        )
                      }
                    />
                  </div>
                  <HabSpeciesNameDisplay species={species} />
                </Typography>
              }
            />
          );
        })}
      </FormGroup>
    </>
  );
}
