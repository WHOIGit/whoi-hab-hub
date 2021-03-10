import React from 'react'
import { makeStyles } from '@material-ui/styles'
import { Grid, Typography, Box } from '@material-ui/core'

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
  legendGrid: {
    fontSize: ".8em",
  },
  legendText: {

  }
}))

export default function LegendCellAbundance() {
  const classes = useStyles()

  const maxSquareSize = 32;
  const minSquareSize = 8;
  const strokeColor = "black";
  const strokeWidth = 4;
  const fillColor = "white";

  return (
    <>
      <Grid
        container
        spacing={3}
        justify="center"
        alignItems="center"
        className={classes.legendGrid}
        >
        <Grid item >
          <Typography variant="caption" display="block" align="center">
            <svg width={minSquareSize} height={minSquareSize}>
              <line x1={0} y1={0} x2={minSquareSize} y2={minSquareSize} stroke={strokeColor} strokeWidth={2}></line>
              <line x1={0} y1={minSquareSize} x2={minSquareSize} y2={0} stroke={strokeColor} strokeWidth={2}></line>
            </svg>
          </Typography>
        </Grid>
        <Grid item >
          <Typography variant="caption" display="block" align="center">
            <svg width={minSquareSize} height={minSquareSize}>
              <rect
                width={minSquareSize}
                height={minSquareSize}
                fill={fillColor}
                strokeWidth={strokeWidth}
                stroke={strokeColor}>
              </rect>
            </svg>
          </Typography>
        </Grid>
        <Grid item >
          <Typography variant="caption" display="block" align="center">
            <svg width={maxSquareSize / 5 * 2} height={maxSquareSize / 5 * 2}>
              <rect
                width={maxSquareSize / 5 * 2}
                height={maxSquareSize / 5 * 2}
                fill={fillColor}
                strokeWidth={strokeWidth}
                stroke={strokeColor}>
              </rect>
            </svg>
          </Typography>
        </Grid>
        <Grid item >
          <Typography variant="caption" display="block" align="center">
            <svg width={maxSquareSize / 5 * 3} height={maxSquareSize / 5 * 3}>
              <rect
                width={maxSquareSize / 5 * 3}
                height={maxSquareSize / 5 * 3}
                fill={fillColor}
                strokeWidth={strokeWidth}
                stroke={strokeColor}>
              </rect>
            </svg>
          </Typography>
        </Grid>
        <Grid item >
          <Typography variant="caption" display="block" align="center">
            <svg width={maxSquareSize / 5 * 4} height={maxSquareSize / 5 * 4}>
              <rect
                width={maxSquareSize / 5 * 4}
                height={maxSquareSize / 5 * 4}
                fill={fillColor}
                strokeWidth={strokeWidth}
                stroke={strokeColor}>
              </rect>
            </svg>
          </Typography>
        </Grid>
        <Grid item >
          <Typography variant="caption" display="block" align="center">
            <svg width={maxSquareSize} height={maxSquareSize}>
              <rect
                width={maxSquareSize}
                height={maxSquareSize}
                fill={fillColor}
                strokeWidth={strokeWidth}
                stroke={strokeColor}>
              </rect>
            </svg>
          </Typography>
        </Grid>
      </Grid>

      <Grid
        container
        spacing={1}
        justify="center"
        alignItems="center"
        className={classes.legendGrid}
        >
        <Grid item >
          <Typography variant="caption" display="block" align="center" className={classes.legendText}>
            ND
          </Typography>
        </Grid>
        <Grid item >
          <Typography variant="caption" display="block" align="center" className={classes.legendText}>
            >100
          </Typography>
        </Grid>
        <Grid item >
          <Typography variant="caption" display="block" align="center" className={classes.legendText}>
            >1000
          </Typography>
        </Grid>
        <Grid item >
          <Typography variant="caption" display="block" align="center" className={classes.legendText}>
            >1x10<sup>4</sup>
          </Typography>
        </Grid>
        <Grid item>
          <Typography variant="caption" display="block" align="center" className={classes.legendText}>
            >1x10<sup>5</sup>
          </Typography>
        </Grid>
        <Grid item >
          <Typography variant="caption" display="block" align="center" className={classes.legendText}>
            >1x10<sup>6</sup>
          </Typography>
        </Grid>
      </Grid>

      <Typography variant="body2" align="center" gutterBottom>
         Cells L <sup>-1</sup>
      </Typography>

    </>
  )
}
