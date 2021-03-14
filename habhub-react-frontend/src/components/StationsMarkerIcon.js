import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { species } from '../Constants'

const useStyles = makeStyles((theme) => ({
  root: {
    width: 20,
    height: 20,
    fontFamily: 'Verdana',
    fontSize: '1.8rem',
    fontWeight: 'bold',

  },
  triangle: {
    stroke: '#de2d26',
    strokeWidth: 2,
  }
}));

// set colors to use for the gradient from Species
const activeSpecies = species.filter(item => item.id === 'Alexandrium_catenella');
const colors = activeSpecies[0].colorGradient;
//const colors = species[0].colorGradient;

export default function StationsMarkerIcon({ maxMeanData, showMaxMean }) {
  const classes = useStyles();
  const [value, setValue] = useState();

  useEffect(() => {
    if (showMaxMean === 'mean') {
      setValue(maxMeanData[0].mean_value);
    } else {
      setValue(maxMeanData[0].max_value);
    }
  }, [maxMeanData, showMaxMean]);

  function setGradientColor(value) {
    let gradient = colors[4];

    if (value < 42) {
      gradient = colors[0];
    } else if (value < 60) {
      gradient = colors[1];
    } else if (value < 80) {
      gradient = colors[2];
    } else if (value < 100) {
      gradient = colors[3];
    }

    return gradient;
  }

  return (
    <div>
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" className={classes.root} >
          <polygon points="50 0, 100 50, 50 100, 0 50" fill={setGradientColor(value)} className={classes.triangle}/>
          {/*<text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle">{value}</text>*/}

      </svg>
    </div>
  );
}
