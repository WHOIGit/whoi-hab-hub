import React from "react";
import { Grid, Typography } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { useSelector } from "react-redux";
import HabSpeciesColorChip from "./HabSpeciesColorChip";
import HabSpeciesNameDisplay from "./HabSpeciesNameDisplay";
const useStyles = makeStyles(() => ({
  formControl: {
    width: "100%",
  },
}));

export default function HabSpeciesList() {
  const habSpecies = useSelector((state) => state.habSpecies.species);
  const classes = useStyles();

  return (
    <Grid container spacing={0}>
      {habSpecies.map((species) => {
        return (
          <>
            <Grid item xs={2}>
              <div>
                <HabSpeciesColorChip
                  species={species}
                  chipWidth={20}
                  chipHeight={20}
                  chipType="primary"
                />
              </div>
            </Grid>
            <Grid item xs={10}>
              <Typography
                variant="body2"
                color="textSecondary"
                className={classes.labelText}
              >
                <HabSpeciesNameDisplay species={species} />
              </Typography>
            </Grid>
          </>
        );
      })}
    </Grid>
  );
}
