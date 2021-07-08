import React, { useState } from "react";
import { Container } from "@material-ui/core";
// Import our stuff
import Header from "./Header";
import HabMap from "../features/hab-map/HabMap";
import DashBoard from "../features/dashboard/DashBoard";
import DateControls from "../features/date-filter/DateControls";
import LowerLeftPanel from "../features/legends/LowerLeftPanel";

export default function AuthenticatedApp() {
  const [showControls, setShowControls] = useState(true);
  const [showDateControls, setShowDateControls] = useState(false);

  return (
    <Container maxWidth={false} disableGutters={true}>
      <Header />
      <main>
        <>
          <HabMap />

          <DashBoard
            showControls={showControls}
            setShowControls={setShowControls}
          />

          <DateControls
            showControls={showControls}
            showDateControls={showDateControls}
            setShowDateControls={setShowDateControls}
          />

          <LowerLeftPanel />
        </>
      </main>
    </Container>
  );
}
