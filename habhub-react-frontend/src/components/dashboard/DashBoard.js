import React, {
  useState,
  useEffect
} from 'react';
import { makeStyles } from '@material-ui/styles';
import {
  IconButton,
  Typography,
  Box,
  AppBar,
  Tabs,
  Tab
} from '@material-ui/core';
import {
  ArrowForward,
  ArrowBack,
  Restore,
  Tune,
  Layers,
  List
} from '@material-ui/icons';
import DataLayersPanel from './DataLayersPanel';
import DateRangePanel from './DateRangePanel';

const useStyles = makeStyles(theme => ({
  root: {
    //margin: theme.spacing(1),
    position: 'absolute',
    top: 0,
    right: 0,
    width: '448px',
    background: 'none',
    zIndex: 2000,
    height: '100vh',
    overflowY: 'scroll',
    transition: 'all 0.3s',
  },
  dashboardContainer: {
    //margin: theme.spacing(1),
    position: 'absolute',
    top: 0,
    right: 0,
    width: '400px',
    background: '#fff',
    boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
    color: '#6b6b76',
    outline: 'none',
    height: '100vh',
    overflowY: 'scroll',
    overflowX: 'visible'

  },
  collapse: {
    right: '-280px',
  },
  toggleArrow: {
    position: 'absolute',
    top: 0,
    left: 0,
    zIndex: 3000,
    color: theme.palette.primary.contrastText,
    backgroundColor: theme.palette.primary.light,
    borderRadius: 0,
    '&:hover': {
      backgroundColor: theme.palette.primary.dark,
    },
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
    position: 'fixed',
    top: 0,
    right: 0,
    zIndex: 4000,
    height: '100vh',
  },
  indicator: {
    left: '0px'
  },
  tabRoot: {
    minWidth: "110px",
    color: 'white',
  },
  tabPanelRoot: {
    maxWidth: "300px"
  }
}))

function TabPanel(props) {
  const {children, value, index, ...other} = props;
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

function Dashboard({
  mapLayers,
  habSpecies,
  yAxisScale,
  onLayerVisibilityChange,
  onSpeciesVisibilityChange,
  onDateRangeChange,
  onYAxisChange,
}) {
  // Set const variables
  const classes = useStyles();
  // Set local state
  const [showControls, setShowControls] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const defaultStartDate = new Date('2017-01-01T21:11:54');
  const [selectedStartDate, setSelectedStartDate] = useState(defaultStartDate);
  const [selectedEndDate, setSelectedEndDate] = useState(new Date());

  function handleTabChange(event, newTabValue) {
    setTabValue(newTabValue);
  };

  function onStartDateChange(date) {
    setSelectedStartDate(date);
    if (date instanceof Date && !isNaN(date)) {
      onDateRangeChange(date, selectedEndDate);
    }
  };

  function onEndDateChange(date) {
    setSelectedEndDate(date);
    if (date instanceof Date && !isNaN(date)) {
      onDateRangeChange(selectedStartDate, date);
    }
  };

  function onDateRangeReset() {
    setSelectedStartDate(defaultStartDate);
    setSelectedEndDate(new Date());
    onDateRangeChange(defaultStartDate, new Date());
  };

  function renderColorChips(species, chipType="gradient", squareWidth=20) {
    // default to show all colors in gradient list
    // if chipType is "primary", only show single chip for primary color
    let colors = species.colorGradient;
    if (chipType === "primary") {
      colors = [species.colorPrimary];
    }

    let svgWidth = squareWidth * colors.length;

    return (
      <svg width={svgWidth} height={squareWidth}>
        {colors.map((color, index) => (
          <rect width={squareWidth} height={squareWidth} fill={color} x={index * 20} key={index}></rect>
        ))}
      </svg>
    )
  }

  return (
    <div className={`${classes.root} control-panel ${showControls ? "active" : classes.collapse}`}>
      <IconButton
        className={classes.toggleArrow}
        onClick={() => setShowControls(!showControls)}
        aria-label="Open/Close Filter Pane" >
        {showControls ? <ArrowForward /> :  <ArrowBack />}
      </IconButton>
      <div className={classes.dashboardContainer}>
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
            icon={<Layers />}
            label="Data Layers"
            classes={{
              root: classes.tabRoot
            }}
          />
          <Tab
            icon={<Tune />}
            label="Date Ranges"
            classes={{
              root: classes.tabRoot
            }}
          />
          <Tab
            icon={<List />}
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
            renderColorChips={renderColorChips}
          />
        </TabPanel>
        <TabPanel
          value={tabValue}
          index={1}
          className={classes.tabPanelRoot}
        >
          <DateRangePanel
            selectedStartDate={selectedStartDate}
            selectedEndDate={selectedEndDate}
            onDateRangeChange={onDateRangeChange}
            onStartDateChange={onStartDateChange}
            onEndDateChange={onEndDateChange}
            onDateRangeReset={onDateRangeReset}
          />
        </TabPanel>
        <TabPanel
          value={tabValue}
          index={2}
          className={classes.tabPanelRoot}
        >
          Item Three
        </TabPanel>
        </React.Fragment>
      </div>
      </div>
  );
}

export default Dashboard;
