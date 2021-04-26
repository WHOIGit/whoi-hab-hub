import React from "react";
import { useDispatch } from "react-redux";
import { Button } from "@material-ui/core";
//import ScheduleIcon from "@material-ui/icons/Schedule";
import MyLocationIcon from "@material-ui/icons/MyLocation";
import TuneIcon from "@material-ui/icons/Tune";
import { makeStyles } from "@material-ui/styles";
import { sub } from "date-fns";
import { changeDateRange } from "./dateFilterSlice";

const useStyles = makeStyles(theme => ({
  root: {
    position: "absolute",
    right: 0,
    bottom: theme.spacing(1),
    zIndex: 2000,
    width: "116px"
  },
  dashboardButton: {
    color: "white",
    width: "100%",
    marginBottom: theme.spacing(1)
  },
  dashboardButtonLabel: {
    // Aligns the content of the button vertically.
    flexDirection: "column"
  }
}));

export default function DateDashboardButtons({
  showDateControls,
  setShowDateControls,
  setSelectedStartDate,
  setSelectedEndDate,
  setSliderValuesFromDates,
  setChartZoomReset
}) {
  const dispatch = useDispatch();
  const classes = useStyles();

  const onCurrentDataClick = () => {
    let end = new Date();
    let start = sub(end, { months: 1 });
    // trigger Redux dispatch function to send data
    const payload = {
      startDate: start.toISOString(),
      endDate: end.toISOString(),
      seasonal: false,
      excludeMonthRange: false
    };
    dispatch(changeDateRange(payload));

    setSelectedStartDate(start);
    setSelectedEndDate(end);
    setSliderValuesFromDates(start, end);
    setChartZoomReset(true);
  };

  return (
    <div className={classes.root}>
      <Button
        classes={{
          root: classes.dashboardButton,
          label: classes.dashboardButtonLabel
        }}
        onClick={onCurrentDataClick}
      >
        <MyLocationIcon />
        Current Data
      </Button>

      <Button
        classes={{
          root: classes.dashboardButton,
          label: classes.dashboardButtonLabel
        }}
        onClick={() => setShowDateControls(!showDateControls)}
      >
        <TuneIcon />
        Date Controls
      </Button>
    </div>
  );
}
