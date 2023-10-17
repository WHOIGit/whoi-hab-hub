/* eslint-disable no-unused-vars */
import React from "react";
import { makeStyles } from "@material-ui/styles";
import { Divider, List, ListItem } from "@material-ui/core";

import DataLayersSelect from "../data-layers/DataLayersSelect";
import MaxMeanSelect from "../data-layers/MaxMeanSelect";

const useStyles = makeStyles(theme => ({
  divider: {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1)
  },
  listItem: {
    paddingRight: 0
  }
}));

export default function DataLayersTab() {
  // Set const variables
  const classes = useStyles();

  return (
    <List>
      <ListItem>
        <DataLayersSelect />
      </ListItem>
      <Divider variant="middle" component="li" className={classes.divider} />
      <ListItem>
        <MaxMeanSelect />
      </ListItem>
    </List>
  );
}
