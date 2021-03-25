import React from "react";
import ReactDOM from "react-dom";
import App from "./App";
import ReactGA from "react-ga";
// Google Analytics setup
ReactGA.initialize("UA-156412996-2");
ReactGA.pageview(window.location.pathname + window.location.search);

ReactDOM.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
  document.getElementById("root")
);
