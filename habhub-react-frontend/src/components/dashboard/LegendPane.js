import React, {
  useState,
  useEffect,
  useRef
} from 'react'
import { makeStyles } from '@material-ui/styles'
import {
  Card,
  CardHeader,
  CardActionArea,
  CardMedia,
  CardContent,
  Typography,
  CardActions,
  IconButton,
  Button,
} from '@material-ui/core'
import {
  Close,
  OpenWith,
  Minimize
} from '@material-ui/icons'
import LegendCellAbundance from "./LegendCellAbundance"
import LegendToxinConcentrations from "./LegendToxinConcentrations"

const expandWidth = window.outerWidth - 296;
const useStyles = makeStyles(theme => ({
  root: {
    margin: theme.spacing(1),
    width: 200,
    transition: 'all 0.3s',
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
    fontSize: '1.1rem'
  },
}))

export default function LegendPane({
  dataLayer,
  habSpecies,
  onLegendPaneClose,
  renderColorChips,
}) {
  const classes = useStyles()

  let title = null;

  if (dataLayer === 'ifcb-layer') {
    title = 'Cell Abundance';
  } else if (dataLayer === 'stations-layer') {
    title = "Toxin Concentrations";
  }

  return (
    <Card className={`${classes.root} ${dataLayer === 'ifcb-layer' ? classes.rootWider : "standard"}`}>
        <CardHeader
          classes={{
            root: classes.rootHeader,
            title: classes.title,
          }}
          action={
            <React.Fragment>
              <IconButton onClick={() => onLegendPaneClose(dataLayer)} aria-label="close">
                <Close />
              </IconButton>
            </React.Fragment>
          }
          title={title}
        />

        <CardContent>
          {dataLayer === 'ifcb-layer' && (
            <LegendCellAbundance />
          )}

          {dataLayer === 'stations-layer' && (
            <LegendToxinConcentrations
              habSpecies={habSpecies}
              renderColorChips={renderColorChips}
            />
          )}

        </CardContent>

    </Card>
  )
}
