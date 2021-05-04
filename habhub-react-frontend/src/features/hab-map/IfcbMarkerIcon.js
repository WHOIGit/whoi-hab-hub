/* eslint-disable */
import React, { useState, useEffect } from "react";
import { makeStyles } from "@material-ui/core/styles";
import { Grid } from "@material-ui/core";
import { Marker } from "react-map-gl";

const useStyles = makeStyles(() => ({
  button: {
    background: "none",
    border: "none",
    cursor: "pointer"
  },
  squaresGrid: {
    display: "flex",
    flexWrap: "wrap",
    alignItems: "baseline"
  },
  gridBreak: {
    flexBasis: "100%",
    height: 0
  }
}));

const IfcbMarkerIcon = ({ feature, layerID, speciesValues, onMarkerClick }) => {
  const [offsetLeft, setOffsetLeft] = useState(-32);
  const [offsetTop, setOffsetTop] = useState(-25);
  const classes = useStyles();
  // set some constants for square sizes
  const maxSquareSize = 32;
  const minSquareSize = 8;
  // set default grid structure for different #s of species. Max squares across = 4
  let gridHorizontal = 3;
  let gridVertical = 2;
  if (speciesValues.length > 6) {
    gridHorizontal = 4;
  }
  if (speciesValues.length > 5) {
    gridVertical = Math.ceil(speciesValues.length / 4);
  }

  useEffect(() => {
    // Dynamically adjust the Marker offsets and Circle width depending on # of species
    // Set a base offset based on the first items X/Y position in the SVG
    const defaultOffsetCorrection = 0;
    // Sort array by max/mean value
    const sortedValues = speciesValues.sort(
      (a, b) => Number(a.value) - Number(b.value)
    );
    let maxHeight = 0;
    // Set the Y offset
    if (sortedValues.length > 3) {
      // if two rows of values, get the highest two values
      maxHeight =
        getSquareSize(sortedValues.slice(-1)[0], maxSquareSize) +
        getSquareSize(sortedValues.slice(-2)[0], maxSquareSize);
    } else {
      // else just get the highest
      maxHeight = getSquareSize(sortedValues.slice(-1)[0], maxSquareSize);
    }
    const offsetTop = (maxHeight / 2) * -1 - defaultOffsetCorrection;

    // Set the X offset
    // Max items across = gridHorizontal, so get that slice of highest values
    const maxWidthArr = sortedValues.slice(-Math.abs(gridHorizontal));
    // Sum values
    const maxWidth = maxWidthArr.reduce(function(a, b) {
      return a + getSquareSize(b, maxSquareSize);
    }, 0);
    const offsetLeft = (maxWidth / 2) * -1 - defaultOffsetCorrection;
    setOffsetLeft(offsetLeft);
    setOffsetTop(offsetTop);
  }, [speciesValues]);

  const getSquareSize = (speciesItem, maxSquareSize) => {
    const value = speciesItem.value;
    let squareSize = maxSquareSize;

    if (value < 100) {
      squareSize = minSquareSize;
    } else if (value < 10e4) {
      squareSize = (maxSquareSize / 5) * 2;
    } else if (value < 10e5) {
      squareSize = (maxSquareSize / 5) * 3;
    } else if (value < 10e6) {
      squareSize = (maxSquareSize / 5) * 4;
    }
    return squareSize;
  };

  const renderSquare = (item, index) => {
    const squareSize = getSquareSize(item, maxSquareSize);

    // Set fill opacity/stroke color based on Value scale
    let fillOpacity = 1;
    let stroke = "white";
    if (item.value < 100) {
      fillOpacity = 0;
    }

    let rowStart = false;
    let rowEnd = false;
    if (!index % 3) {
      rowStart = true;
    }
    if ((index + 1) % 3 === 0) {
      rowEnd = true;
    }

    return (
      <>
        <div className={classes.gridItem} style={{ height: squareSize }}>
          <svg width={squareSize} height={squareSize}>
            <rect
              width={squareSize}
              height={squareSize}
              fill={item.color}
              fillOpacity={fillOpacity}
              x={0}
              y={0}
              key={index}
              strokeWidth={1}
              stroke={stroke}
            ></rect>
          </svg>
        </div>
        {rowEnd && <div className={classes.gridBreak}></div>}
      </>
    );
    /*
    if (item.value < 100) {
      return (
        <>
        <line x1={xValue} y1={yValue} x2={xValue + squareSize} y2={yValue + squareSize} stroke={item.color} strokeWidth={2}></line>
        <line x1={xValue + squareSize} y1={yValue} x2={xValue} y2={yValue + squareSize} stroke={item.color} strokeWidth={2}></line>
        </>
      )
    } else {
      return (
        <rect
          width={squareSize}
          height={squareSize}
          fill={item.color}
          fillOpacity={fillOpacity}
          x={xValue}
          y={yValue}
          key={index}
          strokeWidth={1}
          stroke={stroke}>
        </rect>
      );
    }
    */
  };

  return (
    <Marker
      key={feature.id}
      latitude={feature.geometry.coordinates[1]}
      longitude={feature.geometry.coordinates[0]}
      offsetLeft={offsetLeft}
      offsetTop={offsetTop}
      captureClick={true}
    >
      <div
        className={classes.button}
        onClick={event => onMarkerClick(event, feature, layerID)}
      >
        <div className={classes.squaresGrid}>
          {speciesValues.map((item, index) => renderSquare(item, index))}
        </div>
      </div>
    </Marker>
  );
};

export default IfcbMarkerIcon;
