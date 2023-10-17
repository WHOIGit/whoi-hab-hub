import React from "react";
import ReactDOM from "react-dom";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import GA4React from "ga-4-react";
import App from "./app/App";
import Home from "./routes/home";
import Bookmark from "./routes/bookmark";
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
if (import.meta.env.VITE_GA_UID) {
  //GA_UID = process.env.REACT_APP_GA_UID;
}
const ga4react = new GA4React(GA_UID);

(async () => {
  // eslint-disable-next-line no-unused-vars
  await ga4react.initialize().catch((err) => {});

  ReactDOM.render(
    <Provider store={store}>
      <React.StrictMode>
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<App />}>
              <Route index element={<Home />} />
              <Route path="bookmark" element={<Bookmark />}>
                <Route path=":bookmarkId" element={<Bookmark />} />
              </Route>
            </Route>
          </Routes>
        </BrowserRouter>
        <App />
      </React.StrictMode>
    </Provider>,
    document.getElementById("root")
  );
})();
