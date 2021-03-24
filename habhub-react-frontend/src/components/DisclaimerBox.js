import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import { Chip } from "@material-ui/core";

const useStyles = makeStyles((theme) => ({
  root: {
    width: "100%",
    position: "absolute",
    bottom: 0,
    padding: theme.spacing(1),
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
  },
  chip: {
    backgroundColor: "rgba(255,255,255,0.4)",
  },
}));

export default function DisclaimerBox() {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Chip
        variant="outlined"
        className={classes.chip}
        label="This resource does not provide up-to-date information of HAB-related shellfishing closures. Check with state and/or local authorities before harvesting"
      />
    </div>
  );
}
