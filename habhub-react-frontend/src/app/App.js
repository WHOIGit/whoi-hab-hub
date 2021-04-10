import React, { useState } from "react";
// Material UI imports
import CssBaseline from "@material-ui/core/CssBaseline";
import { ThemeProvider } from "@material-ui/core/styles";
import { Container } from "@material-ui/core";
// Import our stuff
import Header from "./Header";
import HabMap from "../features/hab-map/HabMap";
import DashBoard from "../features/dashboard/DashBoard";
import DateControls from "../features/date-filter/DateControls";
import LowerLeftPanel from "../features/legends/LowerLeftPanel";
import theme from "./theme";

export default function App() {
  const [showControls, setShowControls] = useState(true);
  const [showDateControls, setShowDateControls] = useState(false);

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth={false} disableGutters={true}>
        <Header />
        <main>
          <>
            <HabMap />

            <DashBoard
              showControls={showControls}
              setShowControls={setShowControls}
              showDateControls={showDateControls}
              setShowDateControls={setShowDateControls}
            />

            <DateControls
              showControls={showControls}
              showDateControls={showDateControls}
            />

            <LowerLeftPanel />
          </>
        </main>
      </Container>
    </ThemeProvider>
  );
}