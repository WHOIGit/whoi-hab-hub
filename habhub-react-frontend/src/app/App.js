import React, { useState } from "react";
// Material UI imports
import CssBaseline from "@material-ui/core/CssBaseline";
import { ThemeProvider } from "@material-ui/core/styles";
import { Container } from "@material-ui/core";
// Import our stuff
import Header from "./Header";
import HabMap from "../features/hab-map/HabMap";
import DateControls from "../features/date-filter/DateControls";
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
            <HabMap
              showControls={showControls}
              setShowControls={setShowControls}
              setShowDateControls={setShowDateControls}
              showDateControls={showDateControls}
            />

            <DateControls
              showControls={showControls}
              showDateControls={showDateControls}
            />
          </>
        </main>
      </Container>
    </ThemeProvider>
  );
}
