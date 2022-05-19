import React from "react";
// Material UI imports
import CssBaseline from "@mui/material/CssBaseline";
import { ThemeProvider, StyledEngineProvider } from "@mui/material/styles";
import { Container } from "@mui/material";
import { Outlet } from "react-router-dom";
// Import our stuff
import Header from "./Header";
import theme from "./theme";

export default function App() {
  return (
    <StyledEngineProvider injectFirst>
      <ThemeProvider theme={theme}>
        <CssBaseline />
        <Container maxWidth={false} disableGutters={true}>
          <Header />
          <main>
            <Outlet />
          </main>
        </Container>
      </ThemeProvider>
    </StyledEngineProvider>
  );
}
