import React, {
  useState,
  useEffect
} from 'react';
import DateFnsUtils from '@date-io/date-fns';
import { makeStyles } from '@material-ui/styles';
import {
  Grid,
  Slider,
  Typography,
  FormLabel,
  FormControl,
  FormGroup,
  List,
  ListItem,
  IconButton,
} from '@material-ui/core';
import { Restore } from '@material-ui/icons';
import {
  MuiPickersUtilsProvider,
  KeyboardDatePicker
} from '@material-ui/pickers';

const useStyles = makeStyles(theme => ({
  root: {},
  resetBtn: {
    position: 'absolute',
    top: '-3px',
    right: '15px',
    zIndex: 100,
  }
}))

const marksYearSlider = [
  {
    value: 1970,
    label: '1970',
  },
  {
    value: 1980,
    label: '1980',
  },
  {
    value: 1990,
    label: '1990',
  },
  {
    value: 2000,
    label: '2000',
  },
  {
    value: 2010,
    label: '2010',
  },
  {
    value: 2020,
    label: '2020',
  },
]

const marksMonthSlider = [
  {
    value: 0,
    label: 'Jan',
  },
  {
    value: 1,
    label: 'Feb',
  },
  {
    value: 2,
    label: 'Mar',
  },
  {
    value: 3,
    label: 'Apr',
  },
  {
    value: 4,
    label: 'May',
  },
  {
    value: 5,
    label: 'Jun',
  },
  {
    value: 6,
    label: 'Jul',
  },
  {
    value: 7,
    label: 'Aug',
  },
  {
    value: 8,
    label: 'Sep',
  },
  {
    value: 9,
    label: 'Oct',
  },
  {
    value: 10,
    label: 'Nov',
  },
  {
    value: 11,
    label: 'Dec',
  },
]


function valueMonthLabelFormat(value) {
  return value + 1;
}

export default function DateRangePanel({
  selectedStartDate,
  selectedEndDate,
  onDateRangeChange,
  onStartDateChange,
  onEndDateChange,
  onDateRangeReset
}) {
  // Set const variables
  const classes = useStyles();
  const [valueYearSlider, setValueYearSlider] = useState([2017, 2021]);
  const [valueMonthSlider, setValueMonthSlider] = useState([1, 12]);

  const handleYearSliderChange = (event, newValue) => {
    setValueYearSlider(newValue);
  };

  const handleYearSliderCommit = (event, newValue) => {
    setValueYearSlider(newValue);
    onSliderRangeChange(newValue, valueMonthSlider);
  };

  const handleMonthSliderChange = (event, newValue) => {
    setValueMonthSlider(newValue);
  };

  const handleMonthSliderCommit = (event, newValue) => {
    setValueMonthSlider(newValue);
    onSliderRangeChange(valueYearSlider, newValue);
  };

  const onSliderRangeChange = (valueYearSlider, valueMonthSlider) => {
    // Calculate new dates based on slider input
    const startDateFields = [valueYearSlider[0], valueMonthSlider[0], 1];  // 1 Jan 1970
    const newStartDate = new Date(...startDateFields);

    const endDateFields = [valueYearSlider[1], valueMonthSlider[1], 1];  // 1 Jan 1970
    const newEndDate = new Date(...endDateFields);
    console.log(newStartDate, newEndDate);
    // set "seasonal" filter to TRUE
    onDateRangeChange(newStartDate, newEndDate, true);
  }

  return (
    <Grid
      container
      spacing={1}
      >
      <Grid item xs={3}>
        <MuiPickersUtilsProvider utils={DateFnsUtils}>
            <List className={classes.root}>
              <ListItem>
                <IconButton onClick={() => onDateRangeReset()} aria-label="expand" className={classes.resetBtn}>
                   <Restore />
                </IconButton>
                <FormControl component="fieldset" >
                  <FormLabel component="legend">Date Range</FormLabel>
                  <FormGroup>
                    <KeyboardDatePicker
                      disableToolbar
                      variant="inline"
                      format="MM/dd/yyyy"
                      margin="normal"
                      id="start-date"
                      label="Start Date"
                      value={selectedStartDate}
                      onChange={onStartDateChange}
                      KeyboardButtonProps={{
                        'aria-label': 'change date',
                      }}
                    />
                  </FormGroup>
                  <FormGroup>
                    <KeyboardDatePicker
                      disableToolbar
                      variant="inline"
                      format="MM/dd/yyyy"
                      margin="normal"
                      id="end-date"
                      label="End Date"
                      value={selectedEndDate}
                      onChange={onEndDateChange}
                      KeyboardButtonProps={{
                        'aria-label': 'change date',
                      }}
                    />
                  </FormGroup>
                </FormControl>

              </ListItem>
            </List>
        </MuiPickersUtilsProvider>
      </Grid>
      <Grid item xs={9}>
        <Typography variant="body1" gutterBottom>
          Seasonal range selectors
        </Typography>
        <Slider
          value={valueYearSlider}
          onChange={handleYearSliderChange}
          onChangeCommitted={handleYearSliderCommit}
          min={1970}
          max={2021}
          marks={marksYearSlider}
          valueLabelDisplay="on"
          aria-labelledby="year-slider"
          key="year-slider"
        />

        <Slider
          value={valueMonthSlider}
          onChange={handleMonthSliderChange}
          onChangeCommitted={handleMonthSliderCommit}
          min={0}
          max={11}
          marks={marksMonthSlider}
          valueLabelDisplay="on"
          valueLabelFormat={valueMonthLabelFormat}
          aria-labelledby="month-slider"
          key="month-slider"
        />
      </Grid>
    </Grid>

  );
}
