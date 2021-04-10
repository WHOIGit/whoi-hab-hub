import React from "react";
import { useSelector } from "react-redux";
import { Grid, Typography } from "@material-ui/core";
import HabSpeciesColorChip from "../hab-species/HabSpeciesColorChip";
import { selectSpeciesBySyndrome } from "../hab-species/habSpeciesSlice";

const LegendToxicity = () => {
  const habSpecies = useSelector(state =>
    selectSpeciesBySyndrome(state, "PSP")
  );

  if (!habSpecies) {
    return null;
  }
  return (
    <>
      <Grid container spacing={1}>
        <Grid item xs={3}>
          <Typography variant="body1">PST</Typography>
        </Grid>
        <Grid item xs={9}>
          {habSpecies.map(species => (
            <HabSpeciesColorChip
              species={species}
              chipWidth={35}
              chipHeight={20}
              key={species.id}
            />
          ))}
        </Grid>
      </Grid>
      <Grid container spacing={1}>
        <Grid item xs={3}></Grid>
        <Grid item xs={5}>
          <Typography variant="body2">0</Typography>
        </Grid>
        <Grid item xs={4}>
          <Typography variant="body2" align="right">
            &gt; 2000
          </Typography>
        </Grid>

        <Grid item xs={12}>
          <Typography variant="body2" align="center" gutterBottom>
            &micro;g/100 g meat
          </Typography>
        </Grid>
      </Grid>
    </>
  );
};

export default LegendToxicity;
