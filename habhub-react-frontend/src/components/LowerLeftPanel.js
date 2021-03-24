import React from "react";
import { makeStyles } from "@material-ui/styles";
import LegendPane from "./dashboard/LegendPane";

// eslint-disable-next-line no-unused-vars
const useStyles = makeStyles((theme) => ({
  root: {
    width: 250,
    transition: "all 0.3s",
    position: "absolute",
    bottom: 0,
    left: 0,
    zIndex: 2000,
  },
}));

export default function LowerLeftPane({
  visibleLegends,
  setVisibleLegends,
  habSpecies,
  renderColorChips,
}) {
  const classes = useStyles();

  function onLegendPaneClose(layerID) {
    const newLegends = visibleLegends.filter((item) => item !== layerID);
    setVisibleLegends(newLegends);
  }

  console.log(visibleLegends);
  if (visibleLegends) {
    return (
      <div className={classes.root}>
        {visibleLegends.map((item) => (
          <LegendPane
            dataLayer={item}
            habSpecies={habSpecies}
            onLegendPaneClose={onLegendPaneClose}
            renderColorChips={renderColorChips}
            key={item}
          />
        ))}
      </div>
    );
  } else {
    return null;
  }
}
