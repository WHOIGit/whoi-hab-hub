import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import {
  Typography,
  Link,
  Divider,
} from '@material-ui/core';
import LegendCellConcentration from "./LegendCellConcentration"
import LegendToxicity from "./LegendToxicity"

const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(2)
  },
  legendBox: {
    marginTop: theme.spacing(3),
    marginBottom: theme.spacing(3)
  },
  legendDivider: {
    maring: theme.spacing(2)
  }
}));

export default function LegendTab({ habSpecies, renderColorChips }) {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Typography variant="subtitle1" display="block" gutterBottom>
        Legend
      </Typography>

      <div className={classes.legendBox}>
        <Typography variant="body1" display="block" gutterBottom>
          Cell Concentration
        </Typography>
        <LegendCellConcentration />
      </div>
      <Divider />
      <div className={classes.legendBox}>
        <Typography variant="body1" display="block" gutterBottom>
          Shellfish Toxicity
        </Typography>
        <LegendToxicity
          habSpecies={habSpecies}
          renderColorChips={renderColorChips}
        />
      </div>
    </div>
  );
}
