import React from "react";
import { useDispatch } from "react-redux";
import { makeStyles } from "@material-ui/styles";
import { Card, CardHeader, CardContent, IconButton } from "@material-ui/core";
import { Close } from "@material-ui/icons";
import LegendCellConcentration from "./LegendCellConcentration";
import LegendToxicity from "./LegendToxicity";
import { changeLegendVisibility } from "../data-layers/dataLayersSlice";

const useStyles = makeStyles(theme => ({
  root: {
    margin: theme.spacing(1),
    width: 300,
    transition: "all 0.3s",
    zIndex: 2000
  },
  rootWider: {
    width: 300
  },
  rootHeader: {
    paddingBottom: 0
  },
  title: {
    color: theme.palette.primary.main,
    fontSize: "1.1rem"
  }
}));

export default function LegendPane({ dataLayer }) {
  const dispatch = useDispatch();
  const classes = useStyles();

  let title;

  if (dataLayer === "ifcb_layer") {
    title = "Cell Concentration";
  } else if (dataLayer === "stations_layer") {
    title = "Shellfish Toxicity";
  }

  return (
    <Card
      className={`${classes.root} ${
        dataLayer === "ifcb-layer" ? classes.rootWider : "standard"
      }`}
    >
      <CardHeader
        classes={{
          root: classes.rootHeader,
          title: classes.title
        }}
        action={
          <React.Fragment>
            <IconButton
              onClick={() =>
                dispatch(
                  changeLegendVisibility({
                    layerID: dataLayer,
                    legendVisibility: false
                  })
                )
              }
              aria-label="close"
            >
              <Close />
            </IconButton>
          </React.Fragment>
        }
        title={title}
      />

      <CardContent>
        {dataLayer === "ifcb_layer" && <LegendCellConcentration />}

        {dataLayer === "stations_layer" && <LegendToxicity />}
      </CardContent>
    </Card>
  );
}
