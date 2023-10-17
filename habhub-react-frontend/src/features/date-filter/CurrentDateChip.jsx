import React from "react";
import { useSelector } from "react-redux";
import { Chip } from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { parseISO, format } from "date-fns";

const useStyles = makeStyles(theme => ({
  root: {
    width: "100%",
    position: "absolute",
    top: 0,
    padding: theme.spacing(1),
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    zIndex: 100
  },
  chip: {
    //backgroundColor: "rgba(255,255,255,0.4)"
  }
}));

export default function CurrentDateChip() {
  const startDate = format(
    parseISO(useSelector(state => state.dateFilter.startDate)),
    "MMM dd, yyyy"
  );
  const endDate = format(
    parseISO(useSelector(state => state.dateFilter.endDate)),
    "MMM dd, yyyy"
  );
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Chip
        color="primary"
        className={classes.chip}
        label={`Selected Date Range: ${startDate} - ${endDate}`}
      />
    </div>
  );
}
