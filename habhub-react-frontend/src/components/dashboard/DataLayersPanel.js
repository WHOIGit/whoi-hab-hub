import React, {
  useState,
  useEffect
} from 'react';
import {
  makeStyles
} from '@material-ui/styles';
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
}))

export default function DataLayersPanel({
  mapLayers,
  habSpecies,
  onLayerVisibilityChange,
  onSpeciesVisibilityChange
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

function renderColorChips(color, index) {
  const xValue = index * 20;
  return (
    <rect width="20" height="20" fill={color} x={xValue} key={index}></rect>
  )
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
          <Typography variant="body2" color="textSecondary">{`${species.speciesName} / ${species.syndrome}`}</Typography>
        }
      />
      <Box>
        <svg width="100" height="20">
          {species.colorGradient.map((item, index) => renderColorChips(item, index))}
        </svg>
      </Box>
    </React.Fragment>

  );
}

return (
  <List>
    <ListItem>
      <FormControl component="fieldset" >
        <FormLabel component="legend">Data Layers</FormLabel>
        <FormGroup>
          {mapLayers.map(layer => renderLayerControl(layer))}
        </FormGroup>
      </FormControl>
    </ListItem>
    <Divider variant="middle" component="li" className={classes.divider} />
    <ListItem>
      <FormControl component="fieldset" >
        <FormLabel component="legend">HAB Species/Syndromes</FormLabel>
        <FormGroup>
          {habSpecies.map(species => renderSpeciesControl(species))}
        </FormGroup>
      </FormControl>
    </ListItem>

  </List>
);
}
