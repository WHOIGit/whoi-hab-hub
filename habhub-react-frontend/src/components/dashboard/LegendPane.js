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
  Grid,
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
    width: 300,
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

export default function LegendPane({
  mapLayers,
  setShowLegendPane,
  renderColorChips,
}) {
  const classes = useStyles()
  const [visibleResults, setVisibleResults] = useState([])

  const maxSquareSize = 32;
  const minSquareSize = 8;
  const strokeColor = "black";
  const strokeWidth = 4;
  const fillColor = "white";

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
        />

        <CardContent>
          <Grid
            container
            spacing={0}
            justify="center"
            alignItems="center"
            >
            <Grid item xs={2}>
              <svg width={minSquareSize} height={minSquareSize}>
                <line x1={0} y1={0} x2={minSquareSize} y2={minSquareSize} stroke={strokeColor} strokeWidth={2}></line>
                <line x1={0} y1={minSquareSize} x2={minSquareSize} y2={0} stroke={strokeColor} strokeWidth={2}></line>
              </svg>
            </Grid>
            <Grid item xs={2}>
              <svg width={minSquareSize} height={minSquareSize}>
                <rect
                  width={minSquareSize}
                  height={minSquareSize}
                  fill={fillColor}
                  strokeWidth={strokeWidth}
                  stroke={strokeColor}>
                </rect>
              </svg>
            </Grid>
            <Grid item xs={2}>
              <svg width={maxSquareSize / 5 * 2} height={maxSquareSize / 5 * 2}>
                <rect
                  width={maxSquareSize / 5 * 2}
                  height={maxSquareSize / 5 * 2}
                  fill={fillColor}
                  strokeWidth={strokeWidth}
                  stroke={strokeColor}>
                </rect>
              </svg>
            </Grid>
            <Grid item xs={2}>
              <svg width={maxSquareSize / 5 * 3} height={maxSquareSize / 5 * 3}>
                <rect
                  width={maxSquareSize / 5 * 3}
                  height={maxSquareSize / 5 * 3}
                  fill={fillColor}
                  strokeWidth={strokeWidth}
                  stroke={strokeColor}>
                </rect>
              </svg>
            </Grid>
            <Grid item xs={2}>
              <svg width={maxSquareSize / 5 * 4} height={maxSquareSize / 5 * 4}>
                <rect
                  width={maxSquareSize / 5 * 4}
                  height={maxSquareSize / 5 * 4}
                  fill={fillColor}
                  strokeWidth={strokeWidth}
                  stroke={strokeColor}>
                </rect>
              </svg>
            </Grid>
            <Grid item xs={2}>
              <svg width={maxSquareSize} height={maxSquareSize}>
                <rect
                  width={maxSquareSize}
                  height={maxSquareSize}
                  fill={fillColor}
                  strokeWidth={strokeWidth}
                  stroke={strokeColor}>
                </rect>
              </svg>
            </Grid>

            <Grid item xs={2}>
              box
            </Grid>
            <Grid item xs={2}>
              box
            </Grid>
            <Grid item xs={2}>
              box
            </Grid>
            <Grid item xs={2}>
              box
            </Grid>
            <Grid item xs={2}>
              box
            </Grid>
            <Grid item xs={2}>
              box
            </Grid>
          </Grid>
        </CardContent>

    </Card>
  )
}
