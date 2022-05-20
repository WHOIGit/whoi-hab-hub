import React, { useState } from "react";
import { makeStyles } from "@mui/styles";
import { styled } from '@mui/material/styles';
import { Box, Tabs, Tab } from "@mui/material";
import {
  Stars,
  Layers,
  List,
  Explore,
  Ballot,
  Bookmark,
} from "@mui/icons-material";
import DataLayersTab from "./DataLayersTab";
import HabSpeciesTab from "./HabSpeciesTab";
import LegendTab from "./LegendTab";
import LinksTab from "./LinksTab";
import PartnersTab from "./PartnersTab";
import BookmarkTab from "./BookmarkTab";

const IconTab = styled(Tab)({
  minWidth: "110px",
  color: "white",
  
});

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
          {children}
        </Box>
      )}
    </div>
  );
}

export default function Dashboard({ showControls, setShowControls, viewport }) {
  // Set const variables
  const classes = useStyles();
  // Set local state
  const [tabValue, setTabValue] = useState(0);

  function handleTabChange(event, newTabValue) {
    console.log(tabValue, newTabValue, showControls);
    if (tabValue === newTabValue && showControls) {
      setShowControls(false);
    } else {
      setShowControls(true);
    }
    setTabValue(newTabValue);
  }

  return (
    <Box sx={[
        {
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
        !showControls && {
          right: "-284px",
        },
      ]}
    >
      <div className={classes.dashboardContainer}>
        <>
          <div className={classes.iconsContainer}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              orientation="vertical"
              textColor="inherit"
              indicatorColor="secondary"
            >
              <IconTab
                icon={<Ballot />}
                label="Algal Species"
                
              />
              <IconTab
                icon={<Layers />}
                label="Data Layers"
                
              />
              <IconTab
                icon={<List />}
                label="Legend"
                
              />
              <IconTab
                icon={<Explore />}
                label="Links"
                
              />
              <IconTab
                icon={<Stars />}
                label="Partners"
                
              />
              <IconTab
                icon={<Bookmark />}
                label="Save Map"
                
              />
            </Tabs>
          </div>

          <TabPanel value={tabValue} index={0} className={classes.tabPanelRoot}>
            <HabSpeciesTab />
          </TabPanel>
          <TabPanel value={tabValue} index={1} className={classes.tabPanelRoot}>
            <DataLayersTab />
          </TabPanel>
          <TabPanel value={tabValue} index={2} className={classes.tabPanelRoot}>
            <LegendTab />
          </TabPanel>
          <TabPanel value={tabValue} index={3} className={classes.tabPanelRoot}>
            <LinksTab />
          </TabPanel>
          <TabPanel value={tabValue} index={4} className={classes.tabPanelRoot}>
            <PartnersTab />
          </TabPanel>
          <TabPanel value={tabValue} index={5} className={classes.tabPanelRoot}>
            <BookmarkTab viewport={viewport} />
          </TabPanel>
        </>
      </div>
    </Box>
  );
}
