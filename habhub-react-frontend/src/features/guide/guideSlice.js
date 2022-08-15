import { createSlice } from "@reduxjs/toolkit";

const guideSteps = [
  {
    stepId: 0,
    label: "About",
    text: `<b>Welcome to the WHOI HABHub!</b><br /><br />
    The HABHub data portal integrates and visualizes multiple data sources related 
    to Harmful Algal Blooms (HABs) in New England.`,
    tabIndex: null,
    isActive: false,
  },
  {
    stepId: 1,
    label: "Select HAB Species",
    text: `Add up to 6 HAB Species/Syndromes of interest at a time. 
    You can change the color indicated by clicking the square      
    to use the color picker tool and create your own custom color palette.`,
    tabIndex: 0,
    isActive: false,
  },
  {
    stepId: 2,
    label: "Select Data Layers",
    text: `Select Data Layers associated with the selected HAB species/syndromes, 
    including: IFCB cell concentrations from fixed locations, seasonal shellfish closures, 
    event triggered shellfish closures, or shellfish toxicity data.<br /><br />
    Select the Data Type shown on the map to display Max or Mean values of the data 
    set during the time range.`,
    tabIndex: 1,
    isActive: false,
  },
  {
    stepId: 3,
    label: "Select Timeframe",
    text: `Click on Date Controls to select the date range and see a relative plot of data 
    density for the selected data sets. Select years and specific months by dragging the 
    control along the timeline to look at seasonal trends. To omit a time range, select "exclude selected month range."<br /><br />
    To display data from the past 30 days, click Current Data.<br /><br />
    Click on Save Map to create a unique link with your current map settings.`,
    tabIndex: null,
    highlightFeatures: [],
    isActive: false,
  },
  {
    stepId: 4,
    label: "View and Save Data",
    text: `Click on shapes or shaded features populated on your map to display more information 
    including: graphical data, closure notices, download options and links to data sources.<br /><br />
    On graphs, zoom in to selected time frames by clicking and dragging your mouse across the graph. 
    Click on species names below plots to remove data and adjust the scale. Hover over data points to view raw numbers. 
    Click on data points to view a subset of auto-classified images, and to access the IFCB dashboard.<br /><br />
    Click on graph dropdown menu to print or save a graph and export data to a CSV.`,
    tabIndex: null,
    isActive: false,
  },
  {
    stepId: 5,
    label: "Learn More!",
    text: `Learn more about this data portal <a href="https://northeasthab.whoi.edu/hab-hub/" target="_blank">here<a>.
    <br /><br />Click the orange dropdown icon in the upper left corner for links to companion websites with additional information and resources on HABs in New England.
    <br /><br />To open this guide at any time, click the <strong>Guide</strong> tab.`,
    tabIndex: null,
    isActive: false,
  },
];

const initialState = {
  guideSteps: guideSteps,
};

export const guideSlice = createSlice({
  name: "guide",
  initialState: initialState,
  reducers: {
    changeActiveGuideStep: (state, action) => {
      state.guideSteps.forEach((element) => {
        if (element.stepId == action.payload.stepId) {
          element.isActive = true;
        } else {
          element.isActive = false;
        }
      });
    },
    // eslint-disable-next-line no-unused-vars
    resetGuideSteps: (state, action) => {
      state.guideSteps.forEach((element) => {
        element.isActive = false;
      });
    },
  },
});

// Action creators are generated for each case reducer function
export const { changeActiveGuideStep, resetGuideSteps } = guideSlice.actions;

export default guideSlice.reducer;

// Selector functions
// return only the currently active Guide Step
export const selectActiveGuideStep = (state) =>
  state.guide.guideSteps.find((item) => item.isActive);
