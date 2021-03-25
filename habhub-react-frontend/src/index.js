import React from "react";
import ReactDOM from "react-dom";
import App from "./App";
import ReactGA from "react-ga";
// Google Analytics setup
const GA_UID = process.env.REACT_APP_GA_UID;
ReactGA.initialize(GA_UID);
ReactGA.pageview(window.location.pathname + window.location.search);

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById("root")
);
