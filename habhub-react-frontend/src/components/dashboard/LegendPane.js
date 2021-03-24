import React from "react";
import { makeStyles } from "@material-ui/styles";
import { Card, CardHeader, CardContent, IconButton } from "@material-ui/core";
import { Close } from "@material-ui/icons";
import LegendCellConcentration from "./LegendCellConcentration";
import LegendToxicity from "./LegendToxicity";

const useStyles = makeStyles((theme) => ({
  root: {
    margin: theme.spacing(1),
    width: 300,
    transition: "all 0.3s",
    zIndex: 2000,
  },
  rootWider: {
    width: 300,
  },
  rootHeader: {
    paddingBottom: 0,
  },
  title: {
    color: theme.palette.primary.main,
    fontSize: "1.1rem",
  },
}));

export default function LegendPane({
  dataLayer,
  habSpecies,
  onLegendPaneClose,
  renderColorChips,
}) {
  const classes = useStyles();

  let title = null;

  if (dataLayer === "ifcb-layer") {
    title = "Cell Concentration";
  } else if (dataLayer === "stations-layer") {
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
          title: classes.title,
        }}
        action={
          <React.Fragment>
            <IconButton
              onClick={() => onLegendPaneClose(dataLayer)}
              aria-label="close"
            >
              <Close />
            </IconButton>
          </React.Fragment>
        }
        title={title}
      />

      <CardContent>
        {dataLayer === "ifcb-layer" && <LegendCellConcentration />}

        {dataLayer === "stations-layer" && (
          <LegendToxicity
            habSpecies={habSpecies}
            renderColorChips={renderColorChips}
          />
        )}
      </CardContent>
    </Card>
  );
}
