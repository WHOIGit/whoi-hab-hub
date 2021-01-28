import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import Grid from '@material-ui/core/Grid';
import { species } from '../hab-species'

const useStyles = makeStyles((theme) => ({
  root: {
  },
}));

function IfcbMarkerIcon({visibleSpecies, maxMeanData}) {
  const classes = useStyles();
  const maxSquareSize = 25;
  // set the percentage for each slice by number of visible species
  const slicePercent = 1 / visibleSpecies.length;
  console.log(maxMeanData);

  function getSquareSize(value, maxSquareSize) {
    let squareSize = maxSquareSize;

    if (value < 100) {
      squareSize = maxSquareSize / 5;
    } else if (value < 1000) {
      squareSize = maxSquareSize / 5 * 2;
    } else if (value < 10000) {
      squareSize = maxSquareSize / 5 * 3;
    } else if (value < 100000) {
      squareSize = maxSquareSize / 5 * 4;
    }
    return squareSize;
  }

  function renderSquare(item, index) {
    const maxMeanItem = maxMeanData.filter(data => item.id === data.species)
    const value = maxMeanItem[0].max_value;
    console.log(value);
    console.log(index);

    const squareSize = getSquareSize(value, maxSquareSize)

    // Set 0 index X/Y values
    let xValue = maxSquareSize - squareSize;
    let yValue = maxSquareSize - squareSize;

    if (index === 1) {
      xValue = maxSquareSize;
    } else if (index === 2) {
      // get the last middle square width to calculate the last X value for the SVG Glyphs
      const lastItem = visibleSpecies[1]
      const middleMaxMeanItem = maxMeanData.filter(data => lastItem.id === data.species)
      const middleValue = middleMaxMeanItem[0].max_value;
      const middleSquareWidth = getSquareSize(middleValue, maxSquareSize)
      xValue = maxSquareSize + middleSquareWidth;
    } else if (index === 3) {
      yValue = maxSquareSize;
    } else if (index === 4) {
      xValue = maxSquareSize;
      yValue = maxSquareSize;
    } else if (index === 5) {
      // get the last middle square width to calculate the last X value for the SVG Glyphs
      const lastItem = visibleSpecies[4]
      const middleMaxMeanItem = maxMeanData.filter(data => lastItem.id === data.species)
      const middleValue = middleMaxMeanItem[0].max_value;
      const middleSquareWidth = getSquareSize(middleValue, maxSquareSize)
      xValue = maxSquareSize + middleSquareWidth;
      yValue = maxSquareSize;
    }

    console.log(xValue);
    console.log(yValue);

    return (
      <rect
        width={squareSize}
        height={squareSize}
        fill={item.colorGradient[4]}
        x={xValue}
        y={yValue}
        key={index}
        strokeWidth={1}
        stroke="white">
      </rect>
    );
  }

  return (
    <div>
      <svg width={maxSquareSize * 3} height={maxSquareSize * 2}>
        {visibleSpecies.map((item, index) => renderSquare(item, index))}
      </svg>
    </div>
  );
}

export default IfcbMarkerIcon;
