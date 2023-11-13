import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { species } from '../hab-species'

const useStyles = makeStyles((theme) => ({
  root: {
    width: 36,
    height: 36,
    transform: 'rotate(-90deg)',
  },
  triangle: {
    stroke: '#de2d26',
    strokeWidth: 4,
  }
}));

const IfcbMarkerIcon = ({visibleSpecies, maxMeanData}) => {
  const classes = useStyles();

  // set the percentage for each slice by number of visible species
  const slicePercent = 1 / visibleSpecies.length;
  console.log(maxMeanData);

  const slices = visibleSpecies.map(item => {
    const maxMeanItem = maxMeanData.filter(data => item.id === data.species)
    const value = maxMeanItem[0].max_value;
    console.log(value);

    let gradient = item.colorGradient[4];

    if (value < 20000) {
      gradient = item.colorGradient[0];
    } else if (value < 40000) {
      gradient = item.colorGradient[1];
    } else if (value < 60000) {
      gradient = item.colorGradient[2];
    } else if (value < 80000) {
      gradient = item.colorGradient[3];
    }

    return {
      id: item.id,
      percent: slicePercent,
      color: gradient,
    };
  })

  let cumulativePercent = 0;

  function getCoordinatesForPercent(percent) {
    const x = Math.cos(2 * Math.PI * percent);
    const y = Math.sin(2 * Math.PI * percent);
    return [x, y];
  }

  const renderSlice = (slice) => {
    const [startX, startY] = getCoordinatesForPercent(cumulativePercent);

    // each slice starts where the last slice ended, so keep a cumulative percent
    cumulativePercent += slice.percent;

    const [endX, endY] = getCoordinatesForPercent(cumulativePercent);

    // if the slice is more than 50%, take the large arc (the long way around)
    const largeArcFlag = slice.percent > .5 ? 1 : 0;

  	// create an array and join it just for code readability
    const pathData = [
      `M ${startX} ${startY}`, // Move
      `A 1 1 0 ${largeArcFlag} 1 ${endX} ${endY}`, // Arc
      `L 0 0`, // Line
    ].join(' ');

    return (
      <path d={pathData} fill={slice.color} stroke="#000000" strokeWidth="0.04" strokeOpacity="1" key={slice.id}></path>
    );
  }

  return (
    <div>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="-1 -1 2 2" className={classes.root}>
          {slices.map(slice => renderSlice(slice))}
        </svg>
    </div>
  );
}

export default IfcbMarkerIcon;
