import React, { useState } from "react";
// Import our stuff
import HabMap from "../features/hab-map/HabMap";
import DashBoard from "../features/dashboard/DashBoard";
import DateControls from "../features/date-filter/DateControls";
import LowerLeftPanel from "../features/legends/LowerLeftPanel";

const MAP_LATITUDE = parseFloat(process.env.REACT_APP_MAP_LATITUDE);
const MAP_LONGITUDE = parseFloat(process.env.REACT_APP_MAP_LONGITUDE);
const MAP_ZOOM = parseFloat(process.env.REACT_APP_MAP_ZOOM);

export default function MapContainer() {
  const [showControls, setShowControls] = useState(true);
  const [showDateControls, setShowDateControls] = useState(false);
  const [viewport, setViewport] = useState({
    latitude: MAP_LATITUDE,
    longitude: MAP_LONGITUDE,
    zoom: MAP_ZOOM,
    width: "100%",
    height: "100vh",
  });

  return (
    <>
      <HabMap viewport={viewport} setViewport={setViewport} />

      <DashBoard
        showControls={showControls}
        setShowControls={setShowControls}
        viewport={viewport}
      />

      <DateControls
        showControls={showControls}
        showDateControls={showDateControls}
        setShowDateControls={setShowDateControls}
      />

      <LowerLeftPanel />
    </>
  );
}
