import React, { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import { Grid, Typography } from "@material-ui/core";

export default function LegendToxicity({ renderColorChips }) {
  const habSpecies = useSelector((state) => state.habSpecies);
  const [visibleSpecies, setVisibleSpecies] = useState();

  useEffect(() => {
    if (habSpecies) {
      const currentSpecies = habSpecies
        .filter((species) => species.visibility)
        .filter((species) => species.syndrome === "PSP");
      setVisibleSpecies(currentSpecies);
    }
  }, [habSpecies]);

  if (visibleSpecies) {
    return (
      <>
        <Grid container spacing={1}>
          <Grid item xs={3}>
            <Typography variant="body1">PST</Typography>
          </Grid>
          <Grid item xs={9}>
            {visibleSpecies.map((species) => renderColorChips(species, 35, 20))}
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
  }

  return null;
}
