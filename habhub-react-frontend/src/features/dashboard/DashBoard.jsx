import React, { useEffect, useState } from "react";
import { makeStyles } from "@material-ui/styles";
import { Box, Tabs, Tab } from "@material-ui/core";
import {
  Stars,
  Layers,
  List,
  Explore,
  Ballot,
  Bookmark,
  Help,
} from "@material-ui/icons";
import { useSelector } from "react-redux";
// local imports
import DataLayersTab from "./DataLayersTab";
import HabSpeciesTab from "./HabSpeciesTab";
import LegendTab from "./LegendTab";
import LinksTab from "./LinksTab";
import PartnersTab from "./PartnersTab";
import BookmarkTab from "./BookmarkTab";
import { selectActiveGuideStep } from "../guide/guideSlice";
import styles from "../guide/styles.module.css";

const useStyles = makeStyles((theme) => ({
  root: {
    //margin: theme.spacing(1),
    position: "absolute",
    top: 0,
    right: 0,
    width: "448px",
    background: "none",
    zIndex: 1200,
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
    //boxShadow: "0px 0px 1px 1px #0000001a",
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
      {value === index && <Box>{children}</Box>}
    </div>
  );
}

export default function Dashboard({
  showControls,
  setShowControls,
  setOpenGuide,
}) {
  // Set const variables
  console.log("DASHBOARD");
  const classes = useStyles();
  // Set local state
  const [tabValue, setTabValue] = useState(0);
  const activeGuideStep = useSelector(selectActiveGuideStep);

  const handleTabChange = (event, newTabValue) => {
    // handle the Help button with Dialog modal instead of tabs
    if (newTabValue === 6) {
      setOpenGuide(true);
      return null;
    }

    if (tabValue === newTabValue && showControls) {
      setShowControls(false);
    } else {
      setShowControls(true);
    }
    setTabValue(newTabValue);
  };

  useEffect(() => {
    if (activeGuideStep && activeGuideStep?.tabIndex !== null) {
      setTabValue(activeGuideStep?.tabIndex);
    }
  }, [activeGuideStep]);

  return (
    <>
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
                  icon={<Ballot />}
                  label="Algal Species"
                  className={activeGuideStep?.tabIndex === 0 && styles.pulse}
                  classes={{
                    root: classes.tabRoot,
                  }}
                />
                <Tab
                  icon={<Layers />}
                  label="Data Layers"
                  className={activeGuideStep?.tabIndex === 1 && styles.pulse}
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
                  icon={<Bookmark />}
                  label="Save Map"
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
                <Tab
                  icon={<Help />}
                  label="Guide"
                  classes={{
                    root: classes.tabRoot,
                  }}
                />
              </Tabs>
            </div>

            <TabPanel
              value={tabValue}
              index={0}
              className={classes.tabPanelRoot}
            >
              <HabSpeciesTab />
            </TabPanel>
            <TabPanel
              value={tabValue}
              index={1}
              className={classes.tabPanelRoot}
            >
              <DataLayersTab />
            </TabPanel>
            <TabPanel
              value={tabValue}
              index={2}
              className={classes.tabPanelRoot}
            >
              <LegendTab />
            </TabPanel>
            <TabPanel
              value={tabValue}
              index={3}
              className={classes.tabPanelRoot}
            >
              <BookmarkTab />
            </TabPanel>
            <TabPanel
              value={tabValue}
              index={4}
              className={classes.tabPanelRoot}
            >
              <LinksTab />
            </TabPanel>
            <TabPanel
              value={tabValue}
              index={5}
              className={classes.tabPanelRoot}
            >
              <PartnersTab />
            </TabPanel>
          </>
        </div>
      </div>
    </>
  );
}
