import React, { lazy, Suspense } from "react";
// Material UI imports
import CssBaseline from "@material-ui/core/CssBaseline";
import { ThemeProvider } from "@material-ui/core/styles";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";

import theme from "./theme";
import Login from "../features/user/Login";
import { PrivateRoute } from "./helpers/PrivateRoute";
//import AuthenticatedApp from "./AuthenticatedApp";
const AuthenticatedApp = lazy(() => import("./AuthenticatedApp"));

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Switch>
          <Route exact component={Login} path="/login" />
          <Suspense fallback={<div>Loading...</div>}>
            <PrivateRoute exact component={AuthenticatedApp} path="/" />
          </Suspense>
        </Switch>
      </Router>
    </ThemeProvider>
  );
}
