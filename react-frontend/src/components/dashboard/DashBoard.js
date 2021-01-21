import React, { useState, useEffect } from 'react';
import { makeStyles } from '@material-ui/styles';
import {
  IconButton,
  Typography,
  Box,
  AppBar,
  Tabs,
  Tab
} from '@material-ui/core';
import { ArrowForward, ArrowBack, Restore, Phone } from '@material-ui/icons';
import DataLayersPanel from './DataLayersPanel'

const useStyles = makeStyles(theme => ({
  root: {
    //margin: theme.spacing(1),
    position: 'absolute',
    top: 0,
    right: 0,
    width: '380px',
    background: '#fff',
    boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
    color: '#6b6b76',
    outline: 'none',
    transition: 'all 0.3s',
    zIndex: 2000,
    height: '100vh',
    overflowY: 'scroll',

  },
  collapse: {
    right: '-284px',
  },
  toggleArrow: {
    color: theme.palette.primary.main,
    position: 'fixed',
    right: theme.spacing(1),
    zIndex: 3000,
  },
  resetBtn: {
    position: 'absolute',
    top: '-3px',
    right: '15px',
    zIndex: 100,
  },
  tabs: {
    borderLeft: `1px solid ${theme.palette.divider}`,
    backgroundColor: theme.palette.primary.main,
    position: 'absolute',
    top: 0,
    right: 0,
  },
  indicator: {
    left: '0px'
  },
  tabRoot: {
    minWidth: "110px",
    color: 'white',
  },
  tabPanelRoot: {
    maxWidth: "270px"
  }
}))

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

export default function Dashboard({mapLayers, habSpecies, yAxisScale, onLayerVisibilityChange, onSpeciesVisibilityChange, onDateRangeChange, onYAxisChange,}) {
  // Set const variables
  const classes = useStyles();
  // Set local state
  const [showControls, setShowControls] = useState(true);
  const [tabValue, setTabValue] = useState(0);

  function handleTabChange(event, newTabValue) {
    setTabValue(newTabValue);
  };
  return (
      <div className={`${classes.root} control-panel ${showControls ? "active" : classes.collapse}`}>
        <IconButton
          className={classes.toggleArrow}
          onClick={() => setShowControls(!showControls)}
          aria-label="Open/Close Filter Pane" >
          {showControls ? <ArrowForward /> :  <ArrowBack />}
        </IconButton>

        <React.Fragment>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          orientation="vertical"
          className={classes.tabs}
          classes={{
            indicator: classes.indicator
          }}
        >
          <Tab
            icon={<Phone />}
            label="Data Layers"
            classes={{
              root: classes.tabRoot
            }}
          />
          <Tab
            icon={<Phone />}
            label="Date Ranges"
            classes={{
              root: classes.tabRoot
            }}
          />
          <Tab
            icon={<Phone />}
            label="Legend"
            classes={{
              root: classes.tabRoot
            }}
          />
        </Tabs>

        <TabPanel
          value={tabValue}
          index={0}
          className={classes.tabPanelRoot}
        >
          <DataLayersPanel
            mapLayers={mapLayers}
            habSpecies={habSpecies}
            onLayerVisibilityChange={onLayerVisibilityChange}
            onSpeciesVisibilityChange={onSpeciesVisibilityChange}
          />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          Item Two
        </TabPanel>
        <TabPanel value={tabValue} index={2}>
          Item Three
        </TabPanel>
        </React.Fragment>
      </div>
  );
}
