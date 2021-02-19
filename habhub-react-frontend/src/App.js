import React, { useState, useEffect, useCallback, useRef } from "react";
// Material UI imports
import CssBaseline from '@material-ui/core/CssBaseline';
import { ThemeProvider, makeStyles } from '@material-ui/core/styles';
import {
  Grid,
  Container
} from '@material-ui/core';
// Import our stuff
import Header from './components/Header';
import HabMap from './components/HabMap';
import theme from './theme';

export default function App() {

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth={false} disableGutters={true}>
        <Header />
        <main>
          <HabMap />
        </main>
      </Container>
    </ThemeProvider>
  );
}
