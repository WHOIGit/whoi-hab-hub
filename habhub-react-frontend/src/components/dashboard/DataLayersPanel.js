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
} from '@material-ui/core';

const useStyles = makeStyles(theme => ({
  divider: {
    marginBottom: theme.spacing(1),
  },
  checkBoxes: {
    ...theme.typography.body2,
  },
  body2: {
    ...theme.typography.body2,
  },
  listItem: {
    paddingRight: 0,
  }
}))

export default function DataLayersPanel({
  mapLayers,
  habSpecies,
  onLayerVisibilityChange,
  onSpeciesVisibilityChange,
  renderColorChips,
}) {
  // Set const variables

  const classes = useStyles();

  function renderLayerControl(mapLayer) {
    return (
      <FormControlLabel
        className={classes.checkBoxes}
        key={mapLayer.id}
        control={
          <Checkbox
            color="primary"
            checked={mapLayer.visibility}
            onChange={(event) => onLayerVisibilityChange(event, mapLayer.id)}
            name={mapLayer.name} />
        }
        label = {
          <Typography variant="body2" color="textSecondary">{mapLayer.name}</Typography>
        }
      />
    );
  }

  function renderSpeciesControl(species) {
    return (
      <React.Fragment>
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

      </React.Fragment>

    );
  }

  return (
    <List>
      <ListItem className={classes.listItem}>
        <FormControl component="fieldset" >
          <FormLabel component="legend">HAB Species/Syndrome</FormLabel>
          <FormGroup>
            {habSpecies.map(species => renderSpeciesControl(species))}
          </FormGroup>
        </FormControl>
      </ListItem>
      <Divider variant="middle" component="li" className={classes.divider} />
      <ListItem>
        <FormControl component="fieldset" >
          <FormLabel component="legend">Data Layers</FormLabel>
          <FormGroup>
            {mapLayers.map(layer => renderLayerControl(layer))}
          </FormGroup>
        </FormControl>
      </ListItem>
    </List>

  );
}
