import React, { useState, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
// Material UI imports
import CssBaseline from "@material-ui/core/CssBaseline";
import { ThemeProvider } from "@material-ui/core/styles";
import { Container } from "@material-ui/core";
// Import our stuff
import Header from "./Header";
import HabMap from "../features/hab-map/HabMap";
import DateControls from "../features/date-filter/DateControls";
import { fetchLayers } from "../features/data-layers/dataLayersSlice";
import theme from "./theme";

export default function App() {
  const dispatch = useDispatch();
  const dataLayerStatus = useSelector(state => state.dataLayers.status);
  console.log(dataLayerStatus);
  const error = useSelector(state => state.dataLayers.error);
  const [showControls, setShowControls] = useState(true);
  const [showDateControls, setShowDateControls] = useState(false);

  useEffect(() => {
    if (dataLayerStatus === "idle") {
      dispatch(fetchLayers());
    }
  }, [dataLayerStatus, dispatch]);

  let content;

  if (dataLayerStatus === "loading") {
    content = <div className="loader">Loading...</div>;
  } else if (dataLayerStatus === "succeeded") {
    content = (
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
    );
  } else if (dataLayerStatus === "failed") {
    content = <div>{error}</div>;
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth={false} disableGutters={true}>
        <Header />
        <main>{content}</main>
      </Container>
    </ThemeProvider>
  );
}
