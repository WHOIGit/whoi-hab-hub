import React from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/core/styles";

// eslint-disable-next-line no-unused-vars
const useStyles = makeStyles((theme) => ({
  root: {
    width: 20,
    height: 20,
    fontFamily: "Verdana",
    fontSize: "1.8rem",
    fontWeight: "bold",
  },
  triangle: {
    stroke: "#de2d26",
    strokeWidth: 2,
  },
}));

export default function StationsMarkerIcon({ maxMeanValue }) {
  const habSpecies = useSelector((state) => state.habSpecies.species);
  const classes = useStyles();

  // set colors to use for the gradient from Species
  const activeSpecies = habSpecies.filter(
    (item) => item.id === "Alexandrium_catenella"
  )[0];
  const colors = activeSpecies.colorGradient;

  // eslint-disable-next-line no-unused-vars
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

  function setFillOpacity(value) {
    let opacity = 1.0;

    if (value < 42) {
      opacity = 0.2;
    } else if (value < 60) {
      opacity = 0.4;
    } else if (value < 80) {
      opacity = 0.6;
    } else if (value < 100) {
      opacity = 0.8;
    }

    return opacity;
  }

  return (
    <div>
      <svg
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 100 100"
        className={classes.root}
      >
        <polygon
          points="50 0, 100 50, 50 100, 0 50"
          fill={activeSpecies.primaryColor}
          style={{
            stroke: activeSpecies.primaryColor,
            strokeWidth: 2,
            fillOpacity: setFillOpacity(maxMeanValue),
          }}
          //className={classes.triangle}
        />
        {/*<text x="50%" y="50%" textAnchor="middle" dominantBaseline="middle">{value}</text>*/}
      </svg>
    </div>
  );
}
