import React from "react";
import ReactDOM from "react-dom";
import App from "./app/App";
import ReactGA from "react-ga";
// Redux
import store from "./app/store";
import { Provider } from "react-redux";
import { fetchHabSpecies } from "./features/hab-species/habSpeciesSlice";
import { fetchLayers } from "./features/data-layers/dataLayersSlice";

store.dispatch(fetchLayers());
store.dispatch(fetchHabSpecies());

// Google Analytics setup
const GA_UID = process.env.REACT_APP_GA_UID;
ReactGA.initialize(GA_UID);
ReactGA.pageview(window.location.pathname + window.location.search);

ReactDOM.render(
  <Provider store={store}>
    <React.StrictMode>
      <App />
    </React.StrictMode>
  </Provider>,
  document.getElementById("root")
);
