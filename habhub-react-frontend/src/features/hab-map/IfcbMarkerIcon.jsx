import React, { useState, useEffect } from "react";
import { makeStyles } from "@material-ui/core/styles";
import { Marker } from "react-map-gl";

// eslint-disable-next-line no-unused-vars
const useStyles = makeStyles((theme) => ({
  button: {
    background: "none",
    border: "none",
    cursor: "pointer",
  },
}));

const IfcbMarkerIcon = ({
  feature,
  layerID,
  speciesValues,
  onMarkerClick,
  metricID,
}) => {
  const [offsetLeft, setOffsetLeft] = useState(-32);
  const [offsetTop, setOffsetTop] = useState(-25);
  const classes = useStyles();
  const maxSquareSize = 30;
  const minSquareSize = 8;

  useEffect(() => {
    // Dynamically adjust the Marker offsets and Circle width depending on # of species
    // Set a base offset based on the first items X/Y position in the SVG
    const defaultOffsetCorrection =
      maxSquareSize - getSquareSize(speciesValues[0], maxSquareSize);
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
    // Max 3 items across, so get the 3 highest values
    const maxWidthArr = sortedValues.slice(-3);
    // Sum values
    const maxWidth = maxWidthArr.reduce(function (a, b) {
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
    } else if (value < 1e4) {
      squareSize = (maxSquareSize / 5) * 2;
    } else if (value < 1e5) {
      squareSize = (maxSquareSize / 5) * 3;
    } else if (value < 1e6) {
      squareSize = (maxSquareSize / 5) * 4;
    }
    return squareSize;
  };

  const renderSquare = (item, index) => {
    const squareSize = getSquareSize(item, maxSquareSize);
    // Set 0 index X/Y values
    let xValue = maxSquareSize - squareSize;
    let yValue = maxSquareSize - squareSize;

    if (index === 1) {
      xValue = maxSquareSize;
    } else if (index === 2) {
      // get the last middle square width to calculate the last X value for the SVG Glyphs
      const lastItem = speciesValues[1];
      const middleSquareWidth = getSquareSize(lastItem, maxSquareSize);
      xValue = maxSquareSize + middleSquareWidth;
    } else if (index === 3) {
      yValue = maxSquareSize;
    } else if (index === 4) {
      xValue = maxSquareSize;
      yValue = maxSquareSize;
    } else if (index === 5) {
      // get the last middle square width to calculate the last X value for the SVG Glyphs
      const lastItem = speciesValues[4];
      const middleSquareWidth = getSquareSize(lastItem, maxSquareSize);
      xValue = maxSquareSize + middleSquareWidth;
      yValue = maxSquareSize;
    }

    // Set fill opacity/stroke color based on Value scale
    let fillOpacity = 1;
    let stroke = "white";
    if (item.value < 100) {
      fillOpacity = 0;
    }
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
        stroke={stroke}
      ></rect>
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
        onClick={(event) => onMarkerClick(event, feature, layerID, metricID)}
      >
        <div>
          <svg width={maxSquareSize * 3} height={maxSquareSize * 2}>
            {speciesValues.map((item, index) => renderSquare(item, index))}
          </svg>
        </div>
      </div>
    </Marker>
  );
};

export default IfcbMarkerIcon;
