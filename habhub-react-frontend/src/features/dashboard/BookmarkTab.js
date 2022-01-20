/* eslint-disable no-unused-vars */
import React, { useState } from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/core/styles";
import {
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Divider,
  Button,
  IconButton,
  Tooltip,
} from "@material-ui/core";
import { Link, FileCopy } from "@material-ui/icons";
import { parseISO, format } from "date-fns";
// local imports
import axiosInstance from "../../app/apiAxios";
import { selectVisibleSpecies } from "../hab-species/habSpeciesSlice";
import { selectVisibleLayers } from "../data-layers/dataLayersSlice";

const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(2),
  },
  listItem: {
    paddingLeft: 0,
  },
  blueText: {
    color: theme.palette.secondary.dark,
  },
  divider: {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
  },
  buttonDiv: {
    marginTop: theme.spacing(1),
    marginBottom: theme.spacing(1),
    textAlign: "center",
  },
  popper: {
    zIndex: 9999,
  },
}));

const defaultTooltipText = "Copy to Clipboard";

export default function BookmarkTab({ viewport }) {
  let classes = useStyles();
  let dateFilter = useSelector((state) => state.dateFilter);
  let visibleSpecies = useSelector(selectVisibleSpecies);
  let visibleLayers = useSelector(selectVisibleLayers);
  let [bookmarks, setBookmarks] = useState([]);
  let [tooltipText, setTooltipText] = useState(defaultTooltipText);
  // eslint-disable-next-line no-unused-vars
  let [error, setError] = useState(null);
  // eslint-disable-next-line no-unused-vars
  let [isLoaded, setIsLoaded] = useState(false);

  async function handleBookmarkCreate() {
    let params = {
      startDate: dateFilter.startDate,
      endDate: dateFilter.endDate,
      species: visibleSpecies.map((item) => item.id),
      dataLayers: visibleLayers.map((item) => item.id),
      latitude: Math.round(viewport.latitude * 10000) / 10000,
      longitude: Math.round(viewport.longitude * 10000) / 10000,
      zoom: Math.round(viewport.zoom * 1000) / 1000,
      seasonal: dateFilter.seasonal.toString(),
      excludeMonthRange: dateFilter.excludeMonthRange.toString(),
    };

    console.log(params);
    try {
      let res = await axiosInstance.post("api/v1/core/map-bookmarks/", {
        ...params,
      });
      console.log(res.request.responseURL);
      let data = JSON.parse(res.request.response);
      console.log(data);
      let url = `${window.location.protocol}//${window.location.hostname}/bookmark/${data.id}/`;
      setBookmarks([url, ...bookmarks]);
      setIsLoaded(true);
    } catch (error) {
      console.log(error.response);
      setIsLoaded(true);
      setError(error);
    }
  }

  function handleCopyUrl(text) {
    navigator.clipboard.writeText(text);
    setTooltipText("Copied!");
  }

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

        <div className={classes.buttonDiv}>
          {" "}
          <Button
            onClick={() => handleBookmarkCreate()}
            variant="contained"
            color="default"
            startIcon={<Link />}
          >
            Create Link
          </Button>
        </div>

        {bookmarks?.length > 0 && (
          <div>
            <Typography variant="subtitle1" display="block">
              Saved Bookmarks
            </Typography>

            <List dense={true}>
              {bookmarks.map((item, index) => (
                <ListItem className={classes.listItem} key={index}>
                  <ListItemText className={classes.blueText} primary={item} />
                  <ListItemSecondaryAction>
                    <Tooltip
                      title={tooltipText}
                      classes={{
                        popper: classes.popper,
                      }}
                      onClose={() => setTooltipText(defaultTooltipText)}
                    >
                      <IconButton
                        edge="end"
                        aria-label="copy link"
                        onClick={() => handleCopyUrl(item)}
                      >
                        <FileCopy />
                      </IconButton>
                    </Tooltip>
                  </ListItemSecondaryAction>
                </ListItem>
              ))}
            </List>
          </div>
        )}

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
              Start Date:{" "}
              {format(parseISO(dateFilter.startDate), "MMM dd, yyyy")}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              End Date: {format(parseISO(dateFilter.endDate), "MMM dd, yyyy")}
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
              Map Zoom: {Math.round(viewport.zoom * 1000) / 1000}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              Latitude: {Math.round(viewport.latitude * 10000) / 10000}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              Longitude: {Math.round(viewport.longitude * 10000) / 10000}
            </Typography>
          </ListItem>
        </List>
      </div>
    </>
  );
}
