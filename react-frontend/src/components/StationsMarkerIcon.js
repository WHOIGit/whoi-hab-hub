import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { species } from '../hab-species'

const useStyles = makeStyles((theme) => ({
  root: {
    width: 32,
    height: 32,
    fontFamily: 'Verdana',
    fontSize: '1.8rem',
    fontWeight: 'bold',

  },
  triangle: {
    stroke: '#de2d26',
    strokeWidth: 4,
  }
}));

// set colors to use for the gradient from Species
const activeSpecies = species.filter(item => item.id === 'Alexandrium_catenella');
const colors = activeSpecies[0].colorGradient;
//const colors = species[0].colorGradient;

const StationsMarkerIcon = ({maxValue, meanValue}) => {
  const classes = useStyles();
  const [valueType, setValueType] = useState('max');

  const setGradientColor = (maxValue) => {
    let gradient = colors[4];

    if (maxValue < 42) {
      gradient = colors[0];
    } else if (maxValue < 60) {
      gradient = colors[1];
    } else if (maxValue < 80) {
      gradient = colors[2];
    } else if (maxValue < 100) {
      gradient = colors[3];
    }

    return gradient;
  }

  return (
    <div>
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" className={classes.root} >
          <polygon points="50 0, 100 50, 50 100, 0 50" fill={setGradientColor(maxValue)} className={classes.triangle}/>
          <text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle">{maxValue}</text>
      </svg>
    </div>
  );
}

export default StationsMarkerIcon;
