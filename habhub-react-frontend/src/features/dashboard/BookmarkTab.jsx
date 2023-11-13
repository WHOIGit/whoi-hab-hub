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
  Checkbox,
  FormControlLabel,
} from "@material-ui/core";
import { Link, FileCopy } from "@material-ui/icons";
import { parseISO, format, differenceInDays } from "date-fns";
// local imports
import axiosInstance from "../../app/apiAxios";
import { selectVisibleSpecies } from "../hab-species/habSpeciesSlice";
import {
  selectVisibleLayers,
  selectMaxMeanOption,
} from "../data-layers/dataLayersSlice";
import { selectActiveFeatues } from "../hab-map/habMapDataSlice";

const useStyles = makeStyles((theme) => ({
  root: {
    padding: theme.spacing(2),
  },
  listItem: {
    paddingLeft: 0,
  },
  blueText: {
    color: theme.palette.primary.main,
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
  label: {
    ...theme.typography.body2,
  },
}));

const defaultTooltipText = "Copy to Clipboard";

export default function BookmarkTab() {
  const classes = useStyles();
  const dateFilter = useSelector((state) => state.dateFilter);
  const visibleSpecies = useSelector(selectVisibleSpecies);
  const visibleLayers = useSelector(selectVisibleLayers);
  const showMaxMean = useSelector(selectMaxMeanOption);
  const activeFeatures = useSelector(selectActiveFeatues);
  const habMapData = useSelector((state) => state.habMapData);
  const [bookmarks, setBookmarks] = useState([]);
  const [tooltipText, setTooltipText] = useState(defaultTooltipText);
  // eslint-disable-next-line no-unused-vars
  const [error, setError] = useState(null);
  // eslint-disable-next-line no-unused-vars
  const [isLoaded, setIsLoaded] = useState(false);
  const [useRelativeDateRange, setUseRelativeDateRange] = useState(false);

  const showDatacharts = activeFeatures.length ? "Yes" : "No";

  async function handleBookmarkCreate() {
    let relativeDateRange = null;

    if (useRelativeDateRange) {
      console.log("Using relative date range");
      relativeDateRange = differenceInDays(
        parseISO(dateFilter.endDate),
        parseISO(dateFilter.startDate)
      );
      console.log(relativeDateRange);
    }

    let params = {
      startDate: dateFilter.startDate,
      endDate: dateFilter.endDate,
      species: visibleSpecies.map((item) => item.id),
      dataLayers: visibleLayers.map((item) => item.id),
      latitude: Math.round(habMapData.latitude * 10000) / 10000,
      longitude: Math.round(habMapData.longitude * 10000) / 10000,
      zoom: Math.round(habMapData.zoom * 1000) / 1000,
      seasonal: dateFilter.seasonal.toString(),
      excludeMonthRange: dateFilter.excludeMonthRange.toString(),
      maxMean: showMaxMean,
      activeFeatures: activeFeatures,
      relativeDateRange: relativeDateRange,
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
                <ListItem
                  className={classes.listItem}
                  key={index}
                  component="a"
                  href={item}
                  target="_blank"
                >
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

        <FormControlLabel
          classes={{
            //root: classes.checkBoxes, // class name, e.g. `classes-nesting-root-x`
            label: classes.label,
          }}
          control={
            <Checkbox
              checked={useRelativeDateRange}
              onChange={(event) =>
                setUseRelativeDateRange(event.target.checked)
              }
              name="relativeDateRange"
              color="primary"
            />
          }
          label="Use date range relative to current day (ex: always show the most recent 30 days of data)"
        />
        <Typography variant="body2" display="block"></Typography>

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
              {useRelativeDateRange
                ? "Today"
                : format(parseISO(dateFilter.startDate), "yyyy-MM-dd")}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              End Date:{" "}
              {useRelativeDateRange
                ? differenceInDays(
                    parseISO(dateFilter.endDate),
                    parseISO(dateFilter.startDate)
                  ) + " days"
                : format(parseISO(dateFilter.endDate), "yyyy-MM-dd")}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              Use Relative Date Range: {useRelativeDateRange.toString()}
            </Typography>
          </ListItem>

          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              Data Type:{" "}
              {showMaxMean.charAt(0).toUpperCase() + showMaxMean.slice(1)}
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
              Map Zoom: {Math.round(habMapData.zoom * 1000) / 1000}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              Latitude: {Math.round(habMapData.latitude * 10000) / 10000}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              Longitude: {Math.round(habMapData.longitude * 10000) / 10000}
            </Typography>
          </ListItem>
          <ListItem className={classes.listItem}>
            <Typography variant="body2" display="block">
              Show Data Charts: {showDatacharts}
            </Typography>
          </ListItem>
        </List>
      </div>
    </>
  );
}
