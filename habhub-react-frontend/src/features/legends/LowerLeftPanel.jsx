import React from "react";
import { useSelector } from "react-redux";
import { makeStyles } from "@material-ui/styles";
//import { useDrop } from "react-dnd";
import LegendPane from "./LegendPane";
import { selectLayerLegendIds } from "../data-layers/dataLayersSlice";
//import { ItemTypes } from "../../Constants";

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

export default function LowerLeftPane() {
  const legendLayerIds = useSelector(selectLayerLegendIds);
  const classes = useStyles();

  if (!legendLayerIds) {
    return null;
  }

  return (
    <div className={classes.root}>
      {legendLayerIds.map((legend) => (
        <LegendPane dataLayer={legend} key={legend} />
      ))}
    </div>
  );
}
