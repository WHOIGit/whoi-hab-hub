import React, {useState, useEffect} from 'react'
import { makeStyles } from '@material-ui/styles'
import { Grid, Typography } from '@material-ui/core'

const expandWidth = window.outerWidth - 296;
const useStyles = makeStyles(theme => ({
  root: {
  },
}))

export default function LegendToxicity({habSpecies, renderColorChips}) {
  const classes = useStyles()
  const [visibleSpecies, setVisibleSpecies] = useState(habSpecies)

  useEffect(() => {
    const currentSpecies = habSpecies
      .filter(species => species.visibility)
      .filter(species => species.syndrome === "PSP");
    setVisibleSpecies(currentSpecies)
  }, [habSpecies]);

  return (
    <>
      <Grid
        container
        spacing={1}
      >
        <Grid item xs={3}>
          <Typography variant="body1">
             PST
          </Typography>
        </Grid>
        <Grid item xs={9}>
          {visibleSpecies.map(species => renderColorChips(species, 35, 20))}
        </Grid>
      </Grid>
      <Grid
        container
        spacing={1}
      >
        <Grid item xs={3}>
        </Grid>
        <Grid item xs={5}>
          <Typography variant="body2">
             0
          </Typography>
        </Grid>
        <Grid item xs={4}>
          <Typography variant="body2" align="right">
             > 2000
          </Typography>
        </Grid>

        <Grid item xs={3}>
        </Grid>
        <Grid item xs={9}>
          <Typography variant="body2" align="center" gutterBottom>
            &micro;g/100 g meat
          </Typography>
        </Grid>
      </Grid>
    </>
  )
}
