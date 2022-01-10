import React from "react";
// Material UI imports
import CssBaseline from "@material-ui/core/CssBaseline";
import { ThemeProvider } from "@material-ui/core/styles";
import { Container } from "@material-ui/core";
import { Outlet } from "react-router-dom";
// Import our stuff
import Header from "./Header";
import theme from "./theme";

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth={false} disableGutters={true}>
        <Header />
        <main>
          <Outlet />
        </main>
      </Container>
    </ThemeProvider>
  );
}
