import React from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/core/styles";
import { Typography, List, ListItem, Divider } from "@material-ui/core";
import { parseISO, format } from "date-fns";
// local imports
import { selectVisibleSpecies } from "../hab-species/habSpeciesSlice";
import { selectVisibleLayers } from "../data-layers/dataLayersSlice";

const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(2),
  },
  listItem: {
    paddingLeft: 0,
  },
  divider: {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
  },
}));

export default function BookmarkTab({ viewport }) {
  let classes = useStyles();
  let dateFilter = useSelector((state) => state.dateFilter);
  let visibleSpecies = useSelector(selectVisibleSpecies);
  let visibleLayers = useSelector(selectVisibleLayers);
  console.log(viewport);
  return (
    <>
      <div className={classes.root}>
        <Typography variant="subtitle1" display="block" gutterBottom>
          Bookmark Your Map
        </Typography>

        <Typography variant="body2" display="block" gutterBottom>
          If you want to save your current map settings, you can use this
          feature to create a unique bookmarkable link.
        </Typography>
        <Divider className={classes.divider} />
        <Typography variant="subtitle1" display="block">
          Current Map Settings
        </Typography>

        <List>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              HAB Species:{" "}
              {visibleSpecies.map((item) => item.displayName).join(", ")}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              Data Layers: {visibleLayers.map((item) => item.name).join(", ")}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              Start Date: {format(parseISO(dateFilter.startDate), "yyyy-mm-dd")}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              End Date: {format(parseISO(dateFilter.endDate), "yyyy-mm-dd")}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              Seasonal: {dateFilter.seasonal.toString()}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              Exclude Months: {dateFilter.excludeMonthRange.toString()}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              Map Zoom: {viewport.zoom}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              Latitude: {viewport.latitude}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              Longitude: {viewport.longitude}
            </Typography>
          </ListItem>
        </List>
      </div>
    </>
  );
}
