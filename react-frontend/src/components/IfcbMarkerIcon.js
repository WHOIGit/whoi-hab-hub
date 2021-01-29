import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/core/styles';
import { species } from '../hab-species'

const useStyles = makeStyles((theme) => ({
  root: {
  },
}));

function IfcbMarkerIcon({speciesValues, setOffsetLeft, setOffsetTop}) {
  const classes = useStyles();
  const maxSquareSize = 25;

  useEffect(() => {
    // Dynamically adjust the Marker offsets and Circle width depending on # of species
    // Sort array by max/mean value
    const sortedValues = speciesValues.sort((a, b) => Number(a.value) - Number(b.value));
    const defaultOffsetCorrection = 5;
    let maxHeight = 0
    // Set the Y offset
    if (sortedValues.length > 3) {
      // if two rows of values, get the highest two values
      maxHeight = getSquareSize(sortedValues.slice(-1)[0], maxSquareSize) + getSquareSize(sortedValues.slice(-2)[0], maxSquareSize);
    } else {
      // else just get the highest
      maxHeight = getSquareSize(sortedValues.slice(-1)[0], maxSquareSize)
    }
    const offsetTop = (maxHeight / 2 * -1) - defaultOffsetCorrection;

    // Set the X offset
    const maxWidthArr = sortedValues.slice(-3);
    const maxWidth = maxWidthArr.reduce(function(a, b){
      return a + getSquareSize(b, maxSquareSize);
    }, 0);
    const offsetLeft = (maxWidth / 2 * -1 ) - defaultOffsetCorrection;
    setOffsetLeft(offsetLeft);
    setOffsetTop(offsetTop);

  }, [speciesValues])

  function getSquareSize(speciesItem, maxSquareSize) {
    const value = speciesItem.value
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
    const squareSize = getSquareSize(item, maxSquareSize)
    // Set 0 index X/Y values
    let xValue = maxSquareSize - squareSize;
    let yValue = maxSquareSize - squareSize;

    if (index === 1) {
      xValue = maxSquareSize;
    } else if (index === 2) {
      // get the last middle square width to calculate the last X value for the SVG Glyphs
      const lastItem = speciesValues[1]
      const middleSquareWidth = getSquareSize(lastItem, maxSquareSize)
      xValue = maxSquareSize + middleSquareWidth;
    } else if (index === 3) {
      yValue = maxSquareSize;
    } else if (index === 4) {
      xValue = maxSquareSize;
      yValue = maxSquareSize;
    } else if (index === 5) {
      // get the last middle square width to calculate the last X value for the SVG Glyphs
      const lastItem = speciesValues[4]
      const middleSquareWidth = getSquareSize(lastItem, maxSquareSize)
      xValue = maxSquareSize + middleSquareWidth;
      yValue = maxSquareSize;
    }

    return (
      <rect
        width={squareSize}
        height={squareSize}
        fill={item.color}
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
        {speciesValues.map((item, index) => renderSquare(item, index))}
      </svg>
    </div>
  );
}

export default IfcbMarkerIcon;
