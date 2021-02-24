// array of HAB Species objects.
// id: matches species_id from HABhub Data Server API results
export const species = [
  {
    'id': 'Alexandrium_catenella',
    'speciesName': 'Alexandrium catenella',
    'syndrome': 'PSP',
    'visibility': true,
    'colorPrimary': '#e31a1c',
    'colorGradient': ['#fee5d9', '#fcae91', '#fb6a4a', '#e31a1c', '#a50f15'],
  },
  {
    'id': 'Dinophysis_acuminata',
    'speciesName': 'Dinophysis acuminata',
    'syndrome': 'DSP',
    'visibility': true,
    'colorPrimary': '#1f78b4',
    'colorGradient': ['#eff3ff', '#bdd7e7', '#6baed6', '#1f78b4', '#08519c'],
  },
  {
    'id': 'Dinophysis_norvegica',
    'speciesName': 'Dinophysis norvegica',
    'syndrome': 'DSP',
    'visibility': true,
    'colorPrimary': '#a6cee3',
    'colorGradient': ['#eff3ff', '#bdd7e7', '#6baed6', '#a6cee3', '#08519c'],
  },
  {
    'id': 'Karenia',
    'speciesName': 'Karenia',
    'syndrome': 'Fish Kills',
    'visibility': true,
    'colorPrimary': '#33a02c',
    'colorGradient': ['#edf8e9', '#bae4b3', '#74c476', '#33a02c', '#006d2c'],
  },
  {
    'id': 'Margalefidinium',
    'speciesName': 'Margalefidinium polykrikoides',
    'syndrome': 'Fish Kills',
    'visibility': true,
    'colorPrimary': '#b2df8a',
    'colorGradient': ['#edf8e9', '#bae4b3', '#74c476', '#b2df8a', '#006d2c'],
  },
  {
    'id': 'Pseudo-nitzschia',
    'speciesName': 'Pseudo nitzschia',
    'syndrome': 'ASP',
    'visibility': true,
    'colorPrimary': '#b15928',
    'colorGradient': ['#feedde', '#fdbe85', '#fd8d3c', '#b15928', '#a63603'],
  },
];

// array of Data Layers to display on the map
export const layers = [
  {'name': 'Station Shellfish Toxicity', 'id': 'stations-layer', 'visibility': true},
  {'name': 'IFCB Cell Concentration', 'id': 'ifcb-layer', 'visibility': true},
  {'name': 'Shellfish Closures', 'id': 'closures-layer', 'visibility': true},
];

// object of Component "types" to work with react-dnd drag and drop functionality
export const ItemTypes = {
  PANE: 'pane',
}
