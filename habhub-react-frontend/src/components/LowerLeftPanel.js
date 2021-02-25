import React, {
  useState,
  useEffect,
  useRef
} from 'react'
import { makeStyles } from '@material-ui/styles'
import {
  Card,
  CardHeader,
  CardActionArea,
  CardMedia,
  CardContent,
  Typography,
  CardActions,
  IconButton,
  Button,
} from '@material-ui/core'
import LegendPane from "./dashboard/LegendPane"

const useStyles = makeStyles(theme => ({
  root: {
    width: 250,
    transition: 'all 0.3s',
    position: 'absolute',
    bottom: 0,
    left: 0,
    zIndex: 2000,
  },
}))

export default function LowerLeftPane({
  mapLayers,
  habSpecies,
  renderColorChips,
}) {
  const classes = useStyles();
  const [visibleLayers, setVisibleLayers] = useState();

  useEffect(() => {
    const currentLayers = mapLayers.filter(layer => layer.visibility && layer.hasLegend);
    setVisibleLayers(currentLayers);
  }, [mapLayers]);

  function onLegendPaneClose(layerID) {
    const newLayers = visibleLayers.filter(layer => layer.id !== layerID)
    setVisibleLayers(newLayers);
  }

  console.log(visibleLayers);
  if (visibleLayers) {
    return (
      <div className={classes.root}>
        {visibleLayers.map(layer => (
          <LegendPane
            dataLayer={layer.id}
            habSpecies={habSpecies}
            onLegendPaneClose={onLegendPaneClose}
            renderColorChips={renderColorChips}
            key={layer.id}
          />
        ))}
      </div>
    )
  } else {
      return null;
  }
}
