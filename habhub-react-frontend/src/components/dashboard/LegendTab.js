import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import {
  Typography,
  Link,
  Divider,
  Grid,
} from '@material-ui/core';
import LegendCellConcentration from "./LegendCellConcentration"
import LegendToxicity from "./LegendToxicity"
import DiamondMarker from '../../images/diamond.svg';
import CircleMarker from '../../images/circle.svg';
import SquareMarker from '../../images/square-orange.svg';

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
  },
  layerIcon: {
    width: "25px",
  },
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
          Data Sources
        </Typography>

        <Grid container spacing={0}>
          <Grid item xs={2}>
            <div>
              <img src={DiamondMarker} alt="Station Toxicity Legend Icon" className={classes.layerIcon} />
            </div>
          </Grid>
          <Grid item xs={10}>
            <Typography variant="body2" color="textSecondary" className={classes.labelText}>
              Shellfish Toxicity (state data)
            </Typography>
          </Grid>
          <Grid item xs={2}>
            <div>
              <img src={CircleMarker} alt="IFCB Legend Icon" className={classes.layerIcon} />
            </div>
          </Grid>
          <Grid item xs={10}>
            <Typography variant="body2" color="textSecondary" className={classes.labelText}>
              IFCB
            </Typography>
          </Grid>
          <Grid item xs={2}>
            <div>
              <img src="images/icon-shellfish-closure.png" alt="Closures Legend Icon" className={classes.layerIcon} />
            </div>
          </Grid>
          <Grid item xs={10}>
            <Typography variant="body2" color="textSecondary" className={classes.labelText}>
              Shellfish Bed Closure
            </Typography>
          </Grid>
          <Grid item xs={2}>
            <div>
              <img src={SquareMarker} alt="Closures Area Color" className={classes.layerIcon} />
            </div>
          </Grid>
          <Grid item xs={10}>
            <Typography variant="body2" color="textSecondary" className={classes.labelText}>
              Closure Area
            </Typography>
          </Grid>
        </Grid>

      </div>
      <Divider />

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
