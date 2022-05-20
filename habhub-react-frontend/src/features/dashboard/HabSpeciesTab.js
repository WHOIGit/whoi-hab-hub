/* eslint-disable no-unused-vars */
import React from "react";
import { makeStyles } from "@mui/styles";
import { List, ListItem } from "@mui/material";

import HabSpeciesSelect from "../hab-species/HabSpeciesSelect";

const useStyles = makeStyles(theme => ({
  divider: {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1)
  },
  listItem: {
    paddingRight: 0
  }
}));

export default function HabSpeciesTab() {
  // Set const variables
  const classes = useStyles();

  return (
    <List>
      <ListItem className={classes.listItem}>
        <HabSpeciesSelect />
      </ListItem>
    </List>
  );
}
