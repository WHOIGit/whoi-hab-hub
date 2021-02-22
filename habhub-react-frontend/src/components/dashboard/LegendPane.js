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
  Button
} from '@material-ui/core'
import {
  Close,
  OpenWith,
  Minimize
} from '@material-ui/icons'

const expandWidth = window.outerWidth - 296;
const useStyles = makeStyles(theme => ({
  root: {
    margin: theme.spacing(1),
    width: 400,
    transition: 'all 0.3s',
    position: 'absolute',
    bottom: 0,
    left: 0,
    zIndex: 2000,
  },
  media: {
    height: 140,
  },
  title: {
    color: theme.palette.primary.main,
    fontSize: '1.2rem'
  },
  header: {
    color: theme.palette.primary.main,
  },
  expand: {
    position: 'fixed',
    top: 0,
    left: 10,
    width: expandWidth,
    height: '95vh',
    zIndex: 3000,
    overflowY: 'scroll',
  },
  expandContent: {
    width: expandWidth,
    height: '80%',
  }
}))

function LegendPane({
  mapLayers,
  setShowLegendPane,
  renderColorChips,
}) {
  const classes = useStyles()
  const [visibleResults, setVisibleResults] = useState([])

  return (
    <Card className={classes.root}>
        <CardHeader
          classes={{
            title: classes.title, // class name, e.g. `classes-nesting-label-x`
          }}
          action={
            <React.Fragment>
              <IconButton onClick={() => setShowLegendPane(false)} aria-label="close">
                <Close />
              </IconButton>
            </React.Fragment>
          }
          title="Legend"
          subheader="Sub Title"
        />

        <CardContent>
          <h3>Cell Abundance</h3>
        </CardContent>

    </Card>
  )
}

export default LegendPane;
