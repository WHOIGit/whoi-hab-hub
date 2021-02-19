import React, {
  useState,
  useEffect
} from 'react';
import DateFnsUtils from '@date-io/date-fns';
import {
  makeStyles
} from '@material-ui/styles';
import {
  FormLabel,
  FormControl,
  FormGroup,
  List,
  ListItem,
  IconButton,
} from '@material-ui/core';
import {
  Restore
} from '@material-ui/icons';
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

  return (
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
  );
}
