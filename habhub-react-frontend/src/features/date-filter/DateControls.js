import React, { useState } from "react";
import { useSelector, useDispatch } from "react-redux";
import DateFnsUtils from "@date-io/date-fns";
import { parseISO } from "date-fns";
import { makeStyles } from "@material-ui/styles";
import {
  Grid,
  Box,
  List,
  ListItem,
  Slider,
  Typography,
  FormLabel,
  FormControl,
  FormControlLabel,
  FormGroup,
  IconButton,
  Checkbox,
  Tooltip,
} from "@material-ui/core";
import { Restore } from "@material-ui/icons";
import {
  MuiPickersUtilsProvider,
  KeyboardDatePicker,
} from "@material-ui/pickers";

import DataTimeline from "./DataTimeline";
import DateDashboardButtons from "./DateDashboardButtons";
import { changeDateRange } from "./dateFilterSlice";

const widthWithDashboard = window.outerWidth - 400;
const widthFull = window.outerWidth - 116;

const marksYearSlider = [
  {
    value: 1970,
    label: "1970",
  },
  {
    value: 1980,
    label: "1980",
  },
  {
    value: 1990,
    label: "1990",
  },
  {
    value: 2000,
    label: "2000",
  },
  {
    value: 2010,
    label: "2010",
  },
  {
    value: 2020,
    label: "2020",
  },
];

const marksMonthSlider = [
  {
    value: 0,
    label: "Jan",
  },
  {
    value: 1,
    label: "Feb",
  },
  {
    value: 2,
    label: "Mar",
  },
  {
    value: 3,
    label: "Apr",
  },
  {
    value: 4,
    label: "May",
  },
  {
    value: 5,
    label: "Jun",
  },
  {
    value: 6,
    label: "Jul",
  },
  {
    value: 7,
    label: "Aug",
  },
  {
    value: 8,
    label: "Sep",
  },
  {
    value: 9,
    label: "Oct",
  },
  {
    value: 10,
    label: "Nov",
  },
  {
    value: 11,
    label: "Dec",
  },
];

function valueMonthLabelFormat(value) {
  return value + 1;
}

const useStyles = makeStyles((theme) => ({
  root: {
    position: "fixed",
    bottom: 0,
    left: 0,
    display: "flex",
    margin: theme.spacing(0),
    backgroundColor: "white",
    alignItems: "center",
    padding: theme.spacing(0),
    height: "400px",
    zIndex: 3000,
    transition: "all 0.4s",
  },
  dashBoardWidthPanel: {
    width: widthWithDashboard,
  },
  fullWidthPanel: {
    width: widthFull,
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
  resetBtn: {
    position: "absolute",
    top: "-3px",
    right: "15px",
    zIndex: 100,
  },
  collapse: {
    bottom: "-500px",
  },
  sliderContainer: {
    padding: "12px 16px",
    color: theme.palette.text.secondary,
  },
  popper: {
    zIndex: 9999,
  },
}));

export default function DateControls({
  showControls,
  showDateControls,
  setShowDateControls,
}) {
  const dateFilter = useSelector((state) => state.dateFilter);

  const dispatch = useDispatch();
  const classes = useStyles();

  const [valueYearSlider, setValueYearSlider] = useState([
    2017,
    new Date().getFullYear(),
  ]);
  const [valueMonthSlider, setValueMonthSlider] = useState([0, 11]);
  const [selectedStartDate, setSelectedStartDate] = useState(
    parseISO(dateFilter.startDate)
  );
  const [selectedEndDate, setSelectedEndDate] = useState(
    parseISO(dateFilter.endDate)
  );
  const [excludeChecked, setExcludeChecked] = useState(false);
  const [chartZoomReset, setChartZoomReset] = useState();

  const onStartDateChange = (date) => {
    setSelectedStartDate(date);
    if (date instanceof Date && !isNaN(date)) {
      // trigger Redux dispatch function to fetch data
      const payload = {
        startDate: date.toISOString(),
        endDate: selectedEndDate.toISOString(),
        seasonal: false,
        excludeMonthRange: false,
      };
      dispatch(changeDateRange(payload));
      // update the slider values to match new date
      setSliderValuesFromDates(date, selectedEndDate);
      // reset timeline chart zoom if necesssary
      setChartZoomReset(true);
    }
  };

  const onEndDateChange = (date) => {
    setSelectedEndDate(date);
    if (date instanceof Date && !isNaN(date)) {
      // trigger parent function to fetch data
      const payload = {
        startDate: dateFilter.startDate,
        endDate: date.toISOString(),
        seasonal: false,
        excludeMonthRange: false,
      };
      dispatch(changeDateRange(payload));
      // update the slider values to match new date
      setSliderValuesFromDates(selectedStartDate, date);
      // reset timeline chart zoom if necesssary
      setChartZoomReset(true);
    }
  };

  const onDateRangeReset = () => {
    setSelectedStartDate(parseISO(dateFilter.defaultStartDate));
    setSelectedEndDate(new Date());

    // trigger parent function to fetch data
    const payload = {
      startDate: dateFilter.defaultStartDate,
      endDate: new Date().toISOString(),
      seasonal: false,
      excludeMonthRange: false,
    };
    dispatch(changeDateRange(payload));

    // update the slider values to match new date, set months to full year range
    const newSliderYear = [
      parseISO(dateFilter.defaultStartDate).getFullYear(),
      new Date().getFullYear(),
    ];
    setValueYearSlider(newSliderYear);
    const newSliderMonth = [0, 11];
    setValueMonthSlider(newSliderMonth);
    // reset timeline chart zoom if necesssary
    setChartZoomReset(true);
  };

  const setSliderValuesFromDates = (startDate, endDate) => {
    // updates the Slider state values from two Date objects
    const newSliderYear = [startDate.getFullYear(), endDate.getFullYear()];
    setValueYearSlider(newSliderYear);
    const newSliderMonth = [startDate.getMonth(), endDate.getMonth()];
    setValueMonthSlider(newSliderMonth);
  };

  const onYearSliderCommit = (event, newValue) => {
    setValueYearSlider(newValue);
    onSliderRangeChange(newValue, valueMonthSlider);
  };

  const onMonthSliderCommit = (event, newValue) => {
    setValueMonthSlider(newValue);
    onSliderRangeChange(valueYearSlider, newValue);
  };

  const onSliderRangeChange = (valueYearSlider, valueMonthSlider) => {
    // Calculate new dates based on slider input
    const startDateFields = [valueYearSlider[0], valueMonthSlider[0], 1];
    const newStartDate = new Date(...startDateFields);
    setSelectedStartDate(newStartDate);

    const endDateFields = [valueYearSlider[1], valueMonthSlider[1] + 1, 0];
    const newEndDate = new Date(...endDateFields);
    setSelectedEndDate(newEndDate);
    // set "seasonal" filter to TRUE
    // trigger parent function to fetch data
    const payload = {
      startDate: newStartDate.toISOString(),
      endDate: newEndDate.toISOString(),
      seasonal: true,
      excludeMonthRange: excludeChecked,
    };
    dispatch(changeDateRange(payload));
    // reset timeline chart zoom if necesssary
    setChartZoomReset(true);
  };

  const onExcludeChange = (event) => {
    setExcludeChecked(event.target.checked);
    const payload = {
      startDate: selectedStartDate.toISOString(),
      endDate: selectedEndDate.toISOString(),
      seasonal: true,
      excludeMonthRange: event.target.checked,
    };
    dispatch(changeDateRange(payload));
  };

  return (
    <>
      <DateDashboardButtons
        showDateControls={showDateControls}
        setShowDateControls={setShowDateControls}
        setSelectedStartDate={setSelectedStartDate}
        setSelectedEndDate={setSelectedEndDate}
        setSliderValuesFromDates={setSliderValuesFromDates}
        setChartZoomReset={setChartZoomReset}
      />
      <div
        className={`${classes.root} ${
          showDateControls ? "active" : classes.collapse
        } ${
          showControls ? classes.dashBoardWidthPanel : classes.fullWidthPanel
        }`}
      >
        <Grid container spacing={0}>
          <Grid item xs={12}>
            <Grid container spacing={1}>
              <Grid item xs={3}>
                <MuiPickersUtilsProvider utils={DateFnsUtils}>
                  <List>
                    <ListItem>
                      <Tooltip
                        title="Reset Dates"
                        classes={{
                          popper: classes.popper,
                        }}
                      >
                        <IconButton
                          onClick={() => onDateRangeReset()}
                          aria-label="expand"
                          className={classes.resetBtn}
                        >
                          <Restore />
                        </IconButton>
                      </Tooltip>
                      <FormControl component="fieldset">
                        <FormLabel component="legend">Date Range</FormLabel>
                        <FormGroup>
                          <KeyboardDatePicker
                            disableToolbar
                            variant="inline"
                            format="yyyy-MM-dd"
                            margin="normal"
                            id="start-date"
                            label="Start Date"
                            value={dateFilter.startDate}
                            onChange={onStartDateChange}
                            KeyboardButtonProps={{
                              "aria-label": "start date",
                            }}
                          />
                        </FormGroup>
                        <FormGroup>
                          <KeyboardDatePicker
                            disableToolbar
                            variant="inline"
                            format="yyyy-MM-dd"
                            margin="normal"
                            id="end-date"
                            label="End Date"
                            value={selectedEndDate}
                            onChange={onEndDateChange}
                            KeyboardButtonProps={{
                              "aria-label": "end date",
                            }}
                          />
                        </FormGroup>
                      </FormControl>
                    </ListItem>
                  </List>
                </MuiPickersUtilsProvider>
              </Grid>
              <Grid item xs={9}>
                <div className={classes.sliderContainer}>
                  <Typography variant="body1" gutterBottom>
                    Seasonal range selectors
                  </Typography>
                  <Slider
                    value={valueYearSlider}
                    onChange={(event, newValue) => setValueYearSlider(newValue)}
                    onChangeCommitted={onYearSliderCommit}
                    min={1970}
                    max={new Date().getFullYear()}
                    marks={marksYearSlider}
                    valueLabelDisplay="on"
                    aria-labelledby="year-slider"
                    key="year-slider"
                  />

                  <Slider
                    value={valueMonthSlider}
                    onChange={(event, newValue) =>
                      setValueMonthSlider(newValue)
                    }
                    onChangeCommitted={onMonthSliderCommit}
                    min={0}
                    max={11}
                    marks={marksMonthSlider}
                    valueLabelDisplay="on"
                    valueLabelFormat={valueMonthLabelFormat}
                    aria-labelledby="month-slider"
                    key="month-slider"
                  />
                  <Box color="text.secondary">
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={excludeChecked}
                          onChange={onExcludeChange}
                          color="primary"
                          inputProps={{
                            "aria-label": "exclude selected month range",
                          }}
                        />
                      }
                      label="Exclude selected month range"
                    />
                  </Box>
                </div>
              </Grid>
            </Grid>
          </Grid>
          <Grid item xs={12}>
            <DataTimeline
              onDateRangeReset={onDateRangeReset}
              setSelectedStartDate={setSelectedStartDate}
              setSelectedEndDate={setSelectedEndDate}
              setSliderValuesFromDates={setSliderValuesFromDates}
              showControls={showControls}
              chartZoomReset={chartZoomReset}
              setChartZoomReset={setChartZoomReset}
            />
          </Grid>
        </Grid>
      </div>
    </>
  );
}
