import React, { useState } from "react";
import { makeStyles } from "@material-ui/styles";
import { Button, Typography, Box, Tabs, Tab } from "@material-ui/core";
import { Stars, Tune, Layers, List, Explore } from "@material-ui/icons";
import DataLayersTab from "./DataLayersTab";
import LegendTab from "./LegendTab";
import LinksTab from "./LinksTab";
import PartnersTab from "./PartnersTab";

const useStyles = makeStyles((theme) => ({
  root: {
    //margin: theme.spacing(1),
    position: "absolute",
    top: 0,
    right: 0,
    width: "448px",
    background: "none",
    zIndex: 2000,
    height: "100vh",
    overflowY: "scroll",
    transition: "all 0.3s",
  },
  dashboardContainer: {
    //margin: theme.spacing(1),
    position: "absolute",
    top: 0,
    right: 0,
    width: "400px",
    background: "#fff",
    boxShadow: "0 2px 4px rgba(0,0,0,0.3)",
    color: "#6b6b76",
    outline: "none",
    height: "100vh",
    overflowY: "scroll",
    overflowX: "visible",
  },
  collapse: {
    right: "-284px",
  },
  resetBtn: {
    position: "absolute",
    top: "-3px",
    right: "15px",
    zIndex: 100,
  },
  iconsContainer: {
    borderLeft: `1px solid ${theme.palette.divider}`,
    backgroundColor: theme.palette.primary.main,
    position: "fixed",
    top: 0,
    right: 0,
    zIndex: 4000,
    height: "100vh",
  },
  indicator: {
    left: "0px",
  },
  tabRoot: {
    minWidth: "110px",
    color: "white",
  },
  tabPanelRoot: {
    maxWidth: "284px",
  },
  dashboardButtonBox: {
    position: "absolute",
    bottom: 0,
  },
  dashboardButton: {
    color: "white",
    width: "100%",
    marginBottom: theme.spacing(1),
  },
  dashboardButtonLabel: {
    // Aligns the content of the button vertically.
    flexDirection: "column",
  },
}));

function TabPanel(props) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`vertical-tabpanel-${index}`}
      aria-labelledby={`vertical-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box>
          <Typography>{children}</Typography>
        </Box>
      )}
    </div>
  );
}

export default function Dashboard({
  mapLayers,
  habSpecies,
  onLayerVisibilityChange,
  onSpeciesVisibilityChange,
  renderColorChips,
  showControls,
  setShowControls,
  showDateControls,
  setShowDateControls,
  showMaxMean,
  setShowMaxMean,
  visibleLegends,
  setVisibleLegends,
  mapRef,
}) {
  // Set const variables
  const classes = useStyles();
  // Set local state
  const [tabValue, setTabValue] = useState(0);

  function handleTabChange(event, newTabValue) {
    console.log(event);
    console.log(tabValue);
    console.log(newTabValue);
    if (tabValue === newTabValue && showControls) {
      setShowControls(false);
    } else {
      setShowControls(true);
    }
    setTabValue(newTabValue);
  }

  return (
    <div
      className={`${classes.root} control-panel ${
        showControls ? "active" : classes.collapse
      }`}
    >
      <div className={classes.dashboardContainer}>
        <>
          <div className={classes.iconsContainer}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              orientation="vertical"
              classes={{
                indicator: classes.indicator,
              }}
            >
              <Tab
                icon={<Layers />}
                label="Data Layers"
                classes={{
                  root: classes.tabRoot,
                }}
              />
              <Tab
                icon={<List />}
                label="Legend"
                classes={{
                  root: classes.tabRoot,
                }}
              />
              <Tab
                icon={<Explore />}
                label="Links"
                classes={{
                  root: classes.tabRoot,
                }}
              />
              <Tab
                icon={<Stars />}
                label="Partners"
                classes={{
                  root: classes.tabRoot,
                }}
              />
            </Tabs>

            <div className={classes.dashboardButtonBox}>
              <Button
                classes={{
                  root: classes.dashboardButton,
                  label: classes.dashboardButtonLabel,
                }}
                onClick={() => setShowDateControls(!showDateControls)}
              >
                <Tune />
                Date Controls
              </Button>
            </div>
          </div>

          <TabPanel value={tabValue} index={0} className={classes.tabPanelRoot}>
            <DataLayersTab
              mapLayers={mapLayers}
              habSpecies={habSpecies}
              onLayerVisibilityChange={onLayerVisibilityChange}
              onSpeciesVisibilityChange={onSpeciesVisibilityChange}
              renderColorChips={renderColorChips}
              showMaxMean={showMaxMean}
              setShowMaxMean={setShowMaxMean}
              mapRef={mapRef}
            />
          </TabPanel>
          <TabPanel value={tabValue} index={1} className={classes.tabPanelRoot}>
            <LegendTab
              habSpecies={habSpecies}
              renderColorChips={renderColorChips}
              visibleLegends={visibleLegends}
              setVisibleLegends={setVisibleLegends}
            />
          </TabPanel>
          <TabPanel value={tabValue} index={2} className={classes.tabPanelRoot}>
            <LinksTab />
          </TabPanel>
          <TabPanel value={tabValue} index={3} className={classes.tabPanelRoot}>
            <PartnersTab />
          </TabPanel>
        </>
      </div>
    </div>
  );
}
