import React, { useState, useEffect } from "react";
import { makeStyles } from '@material-ui/styles';
import DataTimeline from "./dashboard/DataTimeline";

const fullWidth = window.outerWidth - 400;

const useStyles = makeStyles((theme) => ({
  root: {
    position: 'fixed',
    bottom: 0,
    left: 0,
    display: 'flex',
    margin: theme.spacing(0),
    width: fullWidth,
    backgroundColor: 'none',
    alignItems: 'center',
    padding: theme.spacing(0),
    height: "500px",
    zIndex: 3000,
    transition: 'all 0.3s',
  },
  button: {
    margin: theme.spacing(0),
    position: "absolute",
    top: "-50px",
    left: 0,
  },
  collapse: {
    bottom: "-500px",
  },
}));

export default function BottomFullPanel({
  showDateControls,
  setShowDateControls,
  mapLayers,
}) {
  const classes = useStyles();

  return (
    <div className={`${classes.root} ${showDateControls ? "active" : classes.collapse}`}>
      <DataTimeline mapLayers={mapLayers} />

    </div>
  );
}
