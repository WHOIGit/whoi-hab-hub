/* eslint-disable */
import React, { useState, useEffect } from "react";
import { makeStyles } from "@material-ui/core/styles";
import { Grid } from "@material-ui/core";
import { Marker } from "react-map-gl";

const useStyles = makeStyles(() => ({
  button: {
    background: "none",
    border: "none",
    cursor: "pointer",
  },
  squaresGrid: {
    display: "flex",
    flexWrap: "wrap",
    alignItems: "baseline",
  },
  gridBreak: {
    flexBasis: "100%",
    height: 0,
  },
}));

export default function IfcbMarkerSquaresGrid({
  feature,
  layerID,
  speciesValues,
  onMarkerClick,
  metricID,
}) {
  const [offsetLeft, setOffsetLeft] = useState(15);
  const [offsetTop, setOffsetTop] = useState(-10);
  const classes = useStyles();
  // set some constants for square sizes
  const maxSquareSize = 30;
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

    // Set fill opacity/stroke color based on Value scale
    let fillOpacity = 1;
    let stroke = "white";
    if (item.value < 100) {
      fillOpacity = 0;
    }

    let rowEnd = false;
    if ((index + 1) % 3 === 0) {
      rowEnd = true;
    }

    return (
      <React.Fragment key={index}>
        <div className={classes.gridItem} style={{ height: squareSize }}>
          <svg width={squareSize} height={squareSize}>
            <rect
              width={squareSize}
              height={squareSize}
              fill={item.color}
              fillOpacity={fillOpacity}
              x={0}
              y={0}
              strokeWidth={1}
              stroke={stroke}
            ></rect>
          </svg>
        </div>
        {rowEnd && <div className={classes.gridBreak}></div>}
      </React.Fragment>
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
        //onClick={(event) => onMarkerClick(event, feature, layerID, metricID)}
      >
        <div className={classes.squaresGrid}>
          {speciesValues.map((item, index) => renderSquare(item, index))}
        </div>
      </div>
    </Marker>
  );
}
