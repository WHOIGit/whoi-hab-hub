import React, {
  useState,
  useEffect
} from 'react';
import { makeStyles } from '@material-ui/styles';
import {
  IconButton,
  Button,
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
  List,
  BarChart,
  Explore,
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
  iconsContainer: {
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
    flexDirection: 'column'
  },
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

export default function Dashboard({
  mapLayers,
  habSpecies,
  yAxisScale,
  onLayerVisibilityChange,
  onSpeciesVisibilityChange,
  onDateRangeChange,
  onYAxisChange,
  renderColorChips,
  showDateControls,
  setShowDateControls,
}) {
  // Set const variables
  const classes = useStyles();
  // Set local state
  const [showControls, setShowControls] = useState(true);
  const [tabValue, setTabValue] = useState(0);

  function handleTabChange(event, newTabValue) {
    console.log(newTabValue);
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
      <div className={classes.dashboardContainer}>
        <>
          <div className={classes.iconsContainer}>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              orientation="vertical"
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
                icon={<List />}
                label="Legend"
                classes={{
                  root: classes.tabRoot
                }}
              />
              <Tab
                icon={<Explore />}
                label="Links"
                classes={{
                  root: classes.tabRoot
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
            Legend
          </TabPanel>
          <TabPanel
            value={tabValue}
            index={2}
            className={classes.tabPanelRoot}
          >
            Links
          </TabPanel>
        </>
      </div>
    </div>
  );
}
