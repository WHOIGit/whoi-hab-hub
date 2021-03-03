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
    'colorPrimary': '#9e9e9e',
    'colorGradient': ['#fafafa', '#eeeeee', '#bdbdbd', '#9e9e9e', '#616161'],
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
    'colorPrimary': '#ffeb3b',
    'colorGradient': ['#fffde7', '#fff59d', '#fff176', '#ffeb3b', '#fdd835'],
  },
  {
    'id': 'Pseudo-nitzschia',
    'speciesName': 'Pseudo nitzschia',
    'syndrome': 'ASP',
    'visibility': true,
    'colorPrimary': '#673ab7',
    'colorGradient': ['#ede7f6', '#d1c4e9', '#9575cd', '#673ab7', '#311b92'],
  },
];

// array of Data Layers to display on the map
export const layers = [
  {
    'name': 'Station Shellfish Toxicity',
    'id': 'stations-layer',
    'visibility': true,
    'isActive': true,
    'hasLegend': true,
  },
  {
    'name': 'IFCB Cell Concentration',
    'id': 'ifcb-layer',
    'visibility': true,
    'isActive': true,
    'hasLegend': true,
  },
  {
    'name': 'Shellfish Closures',
    'id': 'closures-layer',
    'visibility': true,
    'isActive': true,
    'hasLegend': false,
  },
];

// object of Component "types" to work with react-dnd drag and drop functionality
export const ItemTypes = {
  PANE: 'pane',
}
