import React from "react";
import ReactDOM from "react-dom";
import GA4React from "ga-4-react";
import App from "./app/App";

// Redux
import store from "./app/store";
import { Provider } from "react-redux";
import { fetchHabSpecies } from "./features/hab-species/habSpeciesSlice";
import { fetchLayers } from "./features/data-layers/dataLayersSlice";
import { fetchBoundingBox } from "./features/hab-map/spatialGridSlice";

store.dispatch(fetchLayers());
store.dispatch(fetchHabSpecies());
store.dispatch(fetchBoundingBox());

// Google Analytics setup
let GA_UID = null;
if (process.env.REACT_APP_GA_UID) {
  //GA_UID = process.env.REACT_APP_GA_UID;
}
const ga4react = new GA4React(GA_UID);

(async () => {
  await ga4react.initialize();

  ReactDOM.render(
    <Provider store={store}>
      <React.StrictMode>
        <App />
      </React.StrictMode>
    </Provider>,
    document.getElementById("root")
  );
})();
