import React, { useState, useEffect } from "react";
import { makeStyles } from '@material-ui/styles';
import { Grid } from '@material-ui/core';
import DateRangePanel from "./dashboard/DateRangePanel";
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
    backgroundColor: 'white',
    alignItems: 'center',
    padding: theme.spacing(0),
    height: "400px",
    zIndex: 3000,
    transition: 'all 0.4s',
  },
  dateRangePanel: {
    width: "100%",
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

export default function DateControls({
  showDateControls,
  setShowDateControls,
  mapLayers,
  onDateRangeChange,
  dateFilter,
}) {
  console.log(dateFilter);
  const classes = useStyles();

  return (
    <div className={`${classes.root} ${showDateControls ? "active" : classes.collapse}`}>
      <Grid
        container
        spacing={0}
        >
        <Grid item xs={12}>
          <DateRangePanel
            onDateRangeChange={onDateRangeChange}
          />
        </Grid>
        <Grid item xs={12}>
          <DataTimeline
            mapLayers={mapLayers}
            dateFilter={dateFilter}
           />
        </Grid>
      </Grid>

    </div>
  );
}
