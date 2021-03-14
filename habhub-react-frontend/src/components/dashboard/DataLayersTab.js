import React, {
  useState,
  useEffect
} from 'react';
import { makeStyles } from '@material-ui/styles';
import {
  FormLabel,
  FormControl,
  FormGroup,
  FormControlLabel,
  RadioGroup,
  Radio,
  Checkbox,
  Divider,
  List,
  ListItem,
  Typography,
  Box,
  Grid,
} from '@material-ui/core';
import DiamondMarker from '../../images/diamond.svg';
import CircleMarker from '../../images/circle.svg';
import SquareMarker from '../../images/square-orange.svg';

const useStyles = makeStyles(theme => ({
  divider: {
    marginBottom: theme.spacing(1),
  },
  formControl: {
    width: "100%",
  },
  checkBoxes: {
    ...theme.typography.body2,
  },
  label: {
    width: "100%",
  },
  labelText: {
    paddingTop: "5px",
  },
  body2: {
    ...theme.typography.body2,
  },
  listItem: {
    paddingRight: 0,
  },
  layerIcon: {
    width: "25px",
  },
  closureIcon: {
    backgroundColor: "#f2b036",
  }
}))

export default function DataLayersTab({
  mapLayers,
  habSpecies,
  onLayerVisibilityChange,
  onSpeciesVisibilityChange,
  renderColorChips,
  showMaxMean,
  setShowMaxMean,
}) {
  // Set const variables

  const classes = useStyles();

  const handleChange = (event) => {
    setShowMaxMean(event.target.value);
  };

  function renderLayerControl(mapLayer) {
    return (
      <FormControlLabel
        classes={{
          root: classes.checkBoxes, // class name, e.g. `classes-nesting-root-x`
          label: classes.label, // class name, e.g. `classes-nesting-label-x`
        }}
        key={mapLayer.id}
        control={
          <Checkbox
            color="primary"
            checked={mapLayer.visibility}
            onChange={(event) => onLayerVisibilityChange(event, mapLayer.id)}
            name={mapLayer.name} />
        }
        label = {
          <Grid container spacing={0}>
            <Grid item xs={11}>
              <Typography variant="body2" color="textSecondary" className={classes.labelText}>
                {mapLayer.name}
              </Typography>
            </Grid>
            <Grid item xs={1}>
              <div>
                {mapLayer.id === "stations-layer" && (
                  <img src={DiamondMarker} alt="Station Toxicity Legend Icon" className={classes.layerIcon} />
                )}

                {mapLayer.id === "ifcb-layer" && (
                  <img src={CircleMarker} alt="IFCB Legend Icon" className={classes.layerIcon} />
                )}

                {mapLayer.id === "closures-layer" && (
                  <img src="images/icon-shellfish-closure.png" alt="Closures Legend Icon" className={`${classes.layerIcon} ${classes.closureIcon}`} />
                )}
              </div>
            </Grid>
          </Grid>
        }
      />
    );
  }

  function renderSpeciesControl(species) {
    return (
        <FormControlLabel
          key={species.id}
          control={
            <Checkbox
              color="primary"
              checked={species.visibility}
              onChange={(event) => onSpeciesVisibilityChange(event, species.id)}
              name={species.speciesName} />
          }
          label={
            <Typography
              variant="body2"
              color="textSecondary"
              >
                <em>{species.speciesName}</em> / {species.syndrome}
                <Box component="span" m={1}>
                  {renderColorChips(species, 12, 12, "primary")}
                </Box>
              </Typography>
          }
        />

    );
  }

  return (
    <List>
      <ListItem className={classes.listItem}>
        <FormControl component="fieldset" className={classes.formControl}>
          <FormLabel component="legend">HAB Species/Syndrome</FormLabel>
          <FormGroup>
            {habSpecies.map(species => renderSpeciesControl(species))}
          </FormGroup>
        </FormControl>
      </ListItem>
      <Divider variant="middle" component="li" className={classes.divider} />
      <ListItem>
        <FormControl component="fieldset" className={classes.formControl}>
          <FormLabel component="legend">Data Layers</FormLabel>
          <FormGroup>
            {mapLayers.map(layer => renderLayerControl(layer))}
          </FormGroup>
        </FormControl>
      </ListItem>
      <Divider variant="middle" component="li" className={classes.divider} />
      <ListItem>
        <FormControl component="fieldset" className={classes.formControl}>
          <FormLabel component="legend">Data Type</FormLabel>
          <RadioGroup aria-label="gender" name="gender1" value={showMaxMean} onChange={handleChange}>
            <FormControlLabel value="max" control={<Radio color="primary" />} label="Max" />
            <FormControlLabel value="mean" control={<Radio color="primary" />} label="Mean" />
          </RadioGroup>
        </FormControl>
      </ListItem>
    </List>

  );
}
