import React from 'react';
import { makeStyles } from '@material-ui/core/styles';
import {Marker} from 'react-map-gl';
import iconShellfishClosure from '../images/icon-shellfish-closure.png';

const useStyles = makeStyles((theme) => ({
  button: {
    background: 'none',
    border: 'none',
    cursor: 'pointer',
  },
  icon: {
    width: "24px",
    height: "24px",
  }
}));

export default function ClosuresMarkers({labels}) {
  const classes = useStyles();
  const layerID = 'closures-layer';

  function renderMarker(feature) {
    return (
      <Marker
        key={feature.id}
        latitude={feature.geometry.coordinates[1]}
        longitude={feature.geometry.coordinates[0]}
        captureClick={false}
        offsetLeft={-16}
        offsetTop={-16}
      >
        <div className={classes.button} >
          <img src={iconShellfishClosure} className={classes.icon} />
        </div>
      </Marker>
    );
  }

  return (
    <div>
      {labels && labels.features.map(feature => renderMarker(feature))}
    </div>
  )
}
