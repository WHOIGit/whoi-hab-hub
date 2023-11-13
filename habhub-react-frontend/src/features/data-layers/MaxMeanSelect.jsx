import React from "react";
import {
  FormLabel,
  FormControl,
  RadioGroup,
  Radio,
  FormControlLabel,
  Typography,
} from "@material-ui/core";
import { makeStyles } from "@material-ui/styles";
import { useSelector, useDispatch } from "react-redux";
import { changeMaxMean, selectMaxMeanOption } from "./dataLayersSlice";

const useStyles = makeStyles(() => ({
  formControl: {
    width: "100%",
  },
}));

export default function MaxMeanSelect() {
  const showMaxMean = useSelector(selectMaxMeanOption);
  const dispatch = useDispatch();
  const classes = useStyles();

  return (
    <FormControl component="fieldset" className={classes.formControl}>
      <FormLabel component="legend">Data Type</FormLabel>
      <RadioGroup
        aria-label="Show Max or Mean"
        name="Show Max or Mean"
        value={showMaxMean}
        onChange={(event) =>
          dispatch(
            changeMaxMean({
              value: event.target.value,
            })
          )
        }
      >
        <FormControlLabel
          value="max"
          control={<Radio color="primary" />}
          label={<Typography variant="body2">Max</Typography>}
        />
        <FormControlLabel
          value="mean"
          control={<Radio color="primary" />}
          label={<Typography variant="body2">Mean</Typography>}
        />
      </RadioGroup>
    </FormControl>
  );
}
